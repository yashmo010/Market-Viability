"""Stage D: feature matrix assembly — defines the model's feature space.

Outputs:
  data/extracted/features_physical.parquet, features_app.parquet
  models/xgb_physical_features.json, xgb_app_features.json  (the ordered column manifest —
  prediction builds input vectors by iterating this file; NEVER hardcode order elsewhere)

Rules (the pipeline spec §5):
  - per aspect: mean of non-null scores + mention_rate = n_mentioned / n_reviews_extracted
  - zero mentions -> NaN (XGBoost native missing; never impute)
  - drop extraction rows with confidence < 0.3
  - drop suspect_reviews products
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.extraction.extraction_prompt import APP_ASPECT_KEYS, PHYSICAL_ASPECT_KEYS
from src.loading.load_final import ContractData, load_contract
from src.training.label_engineering import months_between

SCORES_PATH = Path("data/extracted/aspect_scores.jsonl")
LABELS_PATH = Path("data/extracted/labels.json")
OUT_DIR = Path("data/extracted")
MODELS_DIR = Path("models")
MIN_CONFIDENCE = 0.3

PHYSICAL_META = ["price", "avg_rating", "rating_count_log", "review_velocity"]
APP_META = ["price", "avg_rating", "rating_count_log", "install_count_log",
            "days_since_update", "review_velocity"]


def feature_columns(product_type: str) -> list[str]:
    aspects = PHYSICAL_ASPECT_KEYS if product_type == "physical" else APP_ASPECT_KEYS
    meta = PHYSICAL_META if product_type == "physical" else APP_META
    return (meta + aspects + [f"{a}_mention_rate" for a in aspects]
            + ["brand_tier", "category"])


# --- brand-tier feature ------------------------------------------------------
# Ordinal brand-recognition proxy from catalog footprint (how many distinct
# products the brand has in the collected pool). NOT derived from any label
# component (review volume / rating), so it is a legitimate recognition signal
# rather than leakage. Lets the model LEARN the brand-maturity effect (an
# established brand's after-sales / reliability transfers to a new unit; an
# unknown brand's does not) instead of relying on a hand-tuned penalty.
#   tier 0 = single-product / unknown brand   (greenfield)
#   tier 1 = minor brand (2-4 products)
#   tier 2 = mid brand (5-10)
#   tier 3 = major brand (11+)
BRAND_TIER_MAP_PATH = MODELS_DIR / "brand_tier_map.json"


def _brand_key(brand: str | None) -> str:
    return (brand or "").strip().casefold()


def _bucket(footprint: int) -> int:
    if footprint >= 11:
        return 3
    if footprint >= 5:
        return 2
    if footprint >= 2:
        return 1
    return 0


def compute_brand_tiers(products) -> dict[str, int]:
    """casefolded brand -> ordinal tier, from distinct-product footprint."""
    footprint: dict[str, int] = defaultdict(int)
    for p in products:
        footprint[_brand_key(p.brand)] += 1
    return {b: _bucket(n) for b, n in footprint.items()}


def load_aspect_aggregates(product_type: str) -> dict[str, dict]:
    """product_uid -> {aspect: mean, aspect_mention_rate: rate} from aspect_scores.jsonl."""
    aspects = PHYSICAL_ASPECT_KEYS if product_type == "physical" else APP_ASPECT_KEYS
    per_product: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    n_extracted: dict[str, int] = defaultdict(int)
    if not SCORES_PATH.exists():
        raise FileNotFoundError(f"{SCORES_PATH} not found — run Stage B extraction first.")
    with open(SCORES_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row["product_type"] != product_type:
                continue
            if row.get("confidence", 0) < MIN_CONFIDENCE:
                continue
            uid = row["product_uid"]
            n_extracted[uid] += 1
            for aspect, val in row["scores"].items():
                if val is not None:
                    per_product[uid][aspect].append(val["score"])

    out: dict[str, dict] = {}
    for uid, n in n_extracted.items():
        feats: dict[str, float] = {}
        for a in aspects:
            vals = per_product[uid].get(a, [])
            feats[a] = float(np.mean(vals)) if vals else np.nan
            feats[f"{a}_mention_rate"] = len(vals) / n if n else np.nan
        out[uid] = feats
    return out


def build_features(data: ContractData, labels: dict[str, dict],
                   product_type: str, now_ts: int | None = None) -> pd.DataFrame:
    now_ts = now_ts or int(time.time())
    products = data.products_physical if product_type == "physical" else data.products_app
    reviews = data.reviews_physical if product_type == "physical" else data.reviews_app
    review_counts: dict[str, int] = defaultdict(int)
    for r in reviews:
        review_counts[r.product_uid] += 1

    aggregates = load_aspect_aggregates(product_type)
    brand_tiers = compute_brand_tiers(products)
    cols = feature_columns(product_type)
    rows, skipped_no_extraction, skipped_suspect = [], 0, 0
    for p in products:
        label = labels.get(p.product_uid)
        if label is None:
            continue
        if label["suspect_reviews"]:
            skipped_suspect += 1
            continue
        agg = aggregates.get(p.product_uid)
        if agg is None:
            skipped_no_extraction += 1
            continue
        row = {
            "product_uid": p.product_uid,
            "price": float(p.price),
            "avg_rating": float(p.avg_rating),
            "rating_count_log": float(np.log1p(p.rating_count)),
            "review_velocity": review_counts[p.product_uid]
            / max(months_between(p.first_review_ts, p.latest_review_ts), 1.0),
            "category": p.category,
            "brand_tier": brand_tiers.get(_brand_key(p.brand), 0),
            "success_score": label["success_score"],
        }
        if product_type == "app":
            row["install_count_log"] = float(np.log1p(p.install_count))
            row["days_since_update"] = (now_ts - p.last_updated_ts) / 86400.0
        row.update(agg)
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError(
            f"No {product_type} feature rows produced. "
            f"(skipped: {skipped_suspect} suspect, {skipped_no_extraction} without extractions)"
        )
    df["category"] = df["category"].astype("category")
    df = df[["product_uid"] + cols + ["success_score"]]
    if product_type == "physical":
        _save_brand_tiers(brand_tiers, df)
    print(f"{product_type}: {len(df)} rows "
          f"({skipped_suspect} suspect excluded, {skipped_no_extraction} without extractions)")
    return df


def _save_brand_tiers(brand_tiers: dict[str, int], df: pd.DataFrame) -> None:
    """Persist the brand->tier lookup + fallback priors for prediction time.

    established_prior: the tier a NAMED-but-unlisted established brand gets (median
    tier among the training products that belong to a multi-product brand). A new /
    unknown brand gets new_tier = 0.
    """
    est = df.loc[df["brand_tier"] >= 1, "brand_tier"]
    established_prior = int(round(float(est.median()))) if len(est) else 1
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(BRAND_TIER_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump({"brands": brand_tiers, "established_prior": established_prior,
                   "new_tier": 0}, f, indent=2)
    print(f"Wrote {BRAND_TIER_MAP_PATH} "
          f"({len(brand_tiers)} brands, established_prior={established_prior})")


def write_outputs(df: pd.DataFrame, product_type: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    parquet_path = OUT_DIR / f"features_{product_type}.parquet"
    df.to_parquet(parquet_path, index=False)
    manifest_path = MODELS_DIR / f"xgb_{product_type}_features.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(feature_columns(product_type), f, indent=2)
    print(f"Wrote {parquet_path} and {manifest_path}")


def run(data_dir: str = "data/final", force: bool = False) -> None:
    outputs = [OUT_DIR / "features_physical.parquet", OUT_DIR / "features_app.parquet"]
    if all(p.exists() for p in outputs) and not force:
        print("Feature parquets exist — skipping (use --force to rebuild).")
        return
    if not LABELS_PATH.exists():
        raise FileNotFoundError(f"{LABELS_PATH} not found — run Stage C first.")
    with open(LABELS_PATH, encoding="utf-8") as f:
        labels = json.load(f)
    data = load_contract(data_dir)
    # apps removed from the system — build app features only if any apps exist
    types = ["physical"] + (["app"] if data.products_app else [])
    for product_type in types:
        df = build_features(data, labels, product_type)
        write_outputs(df, product_type)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Stage D feature matrix assembly")
    ap.add_argument("--data-dir", default="data/final")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    run(args.data_dir, args.force)
