"""Strict Temporal Prediction Pipeline.

Enforces strict launch-blind prediction:
- Input: test_inputs/products_test_specs.json ONLY.
- Access to test_labels/ is physically blocked and audited.
- Uses FROZEN category profiles, FROZEN brand tiers, and FROZEN XGBoost model.
- Operates in two audited modes:
    1. 'bridged': Deployed launch-blind pipeline (cached LLM bridging + frozen category priors)
    2. 'oracle': True review-aspect ceiling (frozen model + frozen brand tiers)
"""

from __future__ import annotations

import collections
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[2]
FROZEN_DIR = ROOT / "strict_temporal/frozen_state"
INPUTS_PATH = ROOT / "strict_temporal/data/test_inputs/products_test_specs.json"
PRED_DIR = ROOT / "strict_temporal/predictions"
PRED_DIR.mkdir(parents=True, exist_ok=True)

PHYSICAL_ASPECT_KEYS = [
    "value_for_money", "utility", "ease_of_use", "reliability",
    "design_appeal", "after_sales", "build_quality", "durability", "repairability"
]


class StrictPredictor:
    def __init__(self, frozen_dir: Path = FROZEN_DIR):
        self.frozen_dir = frozen_dir
        with open(frozen_dir / "category_profiles.json", encoding="utf-8") as f:
            self.profiles = json.load(f)
        with open(frozen_dir / "brand_tier_map.json", encoding="utf-8") as f:
            self.brand_tiers = json.load(f)
        with open(frozen_dir / "xgb_physical_aspects_only_features.json", encoding="utf-8") as f:
            self.manifest = json.load(f)

        self.model = xgb.XGBRegressor(enable_categorical=True)
        self.model.load_model(frozen_dir / "xgb_physical_aspects_only.json")

        # Load training category dtype to match categorical encoding exactly
        train_df = pd.read_parquet(frozen_dir / "train_features.parquet", columns=["category"])
        self.cat_dtype = train_df["category"].dtype

        # Load cached benchmark bridging logs if available
        self.cached_aspects = {}
        bench_dir = ROOT / "models/benchmarks"
        for p in sorted(bench_dir.glob("*.jsonl")):
            for line in open(p, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    uid = r.get("product_uid")
                    if uid and "bridged" in r:
                        self.cached_aspects[uid] = r["bridged"]

    def _brand_tier(self, brand: str) -> int:
        b_key = (brand or "").strip().casefold()
        if b_key in self.brand_tiers.get("brands", {}):
            return int(self.brand_tiers["brands"][b_key])
        return int(self.brand_tiers.get("new_tier", 0))

    def _mock_bridge(self, spec: dict, category: str) -> dict[str, float]:
        prof = self.profiles[category]
        median_price = prof["price"]["median"] or 1.0
        price = float(spec.get("price", median_price))
        nudge = max(-1.5, min(1.5, (median_price - price) / max(median_price, 1.0) * 2.0))
        scores = {}
        for a in PHYSICAL_ASPECT_KEYS:
            base = prof["avg_aspect_scores"].get(a, 5.0)
            val = max(0.0, min(10.0, base + (nudge if a == "value_for_money" else nudge * 0.3)))
            scores[a] = round(float(val), 2)
        return scores

    def _deterministic_value_for_money(self, bridged: dict, price: float, category: str) -> dict:
        prof = self.profiles[category]
        pstats = prof.get("price", {})
        med = pstats.get("median") or float(price) or 1.0
        p25 = pstats.get("p25") or med * 0.7
        p75 = pstats.get("p75") or med * 1.3
        spread = max(p75 - p25, med * 0.3, 1.0)
        dev = (float(price) - med) / spread
        adj = -2.5 * max(-1.5, min(3.0, dev))
        out = dict(bridged)
        if "value_for_money" in out:
            out["value_for_money"] = float(np.clip(float(out["value_for_money"]) + adj, 0.0, 10.0))
        return out

    def predict_one(self, item: dict, mode: str = "bridged") -> dict[str, Any]:
        uid = item["product_uid"]
        cat = item["category"]
        price = float(item.get("price", 0.0))
        brand = item.get("brand", "")
        prof = self.profiles[cat]

        if mode == "bridged":
            if uid in self.cached_aspects:
                aspects = dict(self.cached_aspects[uid])
                bridge_source = "cached_prompt_v2"
            else:
                aspects = self._mock_bridge(item, cat)
                bridge_source = "frozen_category_grounded_mock"
            aspects = self._deterministic_value_for_money(aspects, price, cat)
        elif mode == "oracle":
            # True review aspects from extracted reviews (oracle ceiling)
            aspects = {}
            for a in PHYSICAL_ASPECT_KEYS:
                aspects[a] = item.get(a, np.nan)
            bridge_source = "oracle_true_reviews"
        else:
            raise ValueError(f"Unknown mode: {mode}")

        row_dict = {}
        for col in self.manifest:
            if col == "category":
                row_dict[col] = cat
            elif col == "price":
                row_dict[col] = price
            elif col == "brand_tier":
                row_dict[col] = self._brand_tier(brand)
            elif col in aspects:
                row_dict[col] = aspects[col]
            elif col.endswith("_mention_rate"):
                a_name = col[:-len("_mention_rate")]
                row_dict[col] = prof["avg_mention_rates"].get(a_name, np.nan)
            else:
                row_dict[col] = np.nan

        df_row = pd.DataFrame([row_dict], columns=self.manifest)
        df_row["category"] = df_row["category"].astype(self.cat_dtype)
        viab = float(self.model.predict(df_row)[0])

        return {
            "product_uid": uid,
            "category": cat,
            "predicted_viability": round(viab, 2),
            "bridge_source": bridge_source,
            "price": price,
            "brand_tier": self._brand_tier(brand),
            "aspects": {a: round(float(aspects.get(a, 0.0)), 2) for a in PHYSICAL_ASPECT_KEYS if a in aspects}
        }


def run_prediction_pipeline(
    inputs_file: Path = INPUTS_PATH,
    out_file: Path = PRED_DIR / "predictions.json",
    mode: str = "bridged"
) -> list[dict]:
    # BARRIER AUDIT: ensure inputs_file does not contain labels
    assert "test_labels" not in str(inputs_file.resolve()), "CRITICAL: Attempted to load test_labels in prediction code!"
    
    with open(inputs_file, encoding="utf-8") as f:
        items = json.load(f)

    # Verify no labels exist in loaded input records
    for it in items:
        assert "success_score" not in it, "CRITICAL: success_score found in test input record!"

    predictor = StrictPredictor()
    predictions = [predictor.predict_one(it, mode=mode) for it in items]

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2)

    print(f"Generated {len(predictions)} predictions -> {out_file} (mode={mode})")
    return predictions


if __name__ == "__main__":
    run_prediction_pipeline()
