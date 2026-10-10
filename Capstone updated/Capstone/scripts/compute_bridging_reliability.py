"""Measure per-aspect bridging reliability and persist it as confidence weights.

For each physical aspect, correlate the LLM's spec-bridged score against the product's
REAL review-extracted score (across every product for which we have cached bridged specs).
The resulting Pearson r is how much the specs->aspect step can be trusted for that aspect.

These weights replace the uniform "grounded count" in the prediction confidence: an aspect
now contributes to confidence in proportion to how reliably it actually bridges (measured),
instead of every aspect counting equally. after_sales (specs say nothing about service) earns
~0 weight; utility/reliability/durability earn full weight.

Output: models/bridging_reliability.json  {"physical": {aspect: weight in [0,1]}, "meta": {...}}
Run:    python scripts/compute_bridging_reliability.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.extraction.extraction_prompt import PHYSICAL_ASPECT_KEYS

FEATURES = Path("data/extracted/features_physical.parquet")
OUT = Path("models/bridging_reliability.json")
# every source of frozen-pipeline bridged specs for real products
BRIDGED_SOURCES = [
    Path("models/benchmarks/retro_bridged_v2.jsonl"),
    Path("models/benchmarks/holdout_bridged.jsonl"),
    Path("models/benchmarks/ice_holdout_bridged.jsonl"),  # optional
]
MIN_N = 15  # need enough paired points for a stable r


def load_cached_bridged(uids: set[str]) -> dict[str, dict]:
    cache: dict[str, dict] = {}
    for p in BRIDGED_SOURCES:
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("product_uid") in uids and r.get("bridged"):
                cache[r["product_uid"]] = r["bridged"]  # later source wins (all frozen v2)
    return cache


def main() -> None:
    df = pd.read_parquet(FEATURES).set_index("product_uid")
    cache = load_cached_bridged(set(df.index))
    print(f"paired products (bridged specs matched to real extracted aspects): {len(cache)}")

    weights: dict[str, float] = {}
    detail: dict[str, dict] = {}
    for a in PHYSICAL_ASPECT_KEYS:
        B, R = [], []
        for uid, br in cache.items():
            b, real = br.get(a), df.at[uid, a]
            if b is not None and pd.notna(real):
                B.append(float(b))
                R.append(float(real))
        if len(B) >= MIN_N:
            r = float(np.corrcoef(B, R)[0, 1])
        else:
            r = float("nan")
        # weight = reliability, negatives/NaN clipped to 0 (an aspect that anti-correlates or
        # is unmeasurable earns no confidence). Kept on the raw-r scale (max ~0.53 here) so the
        # weighted fraction spans a meaningful range.
        w = 0.0 if (np.isnan(r) or r < 0) else round(r, 3)
        weights[a] = w
        detail[a] = {"r": None if np.isnan(r) else round(r, 3), "n": len(B), "weight": w}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"physical": weights,
         "meta": {"n_products": len(cache), "detail": detail,
                  "note": "per-aspect Pearson r of bridged-vs-real extracted score; "
                          "used as confidence weights in predictor._adj_confidence"}},
        indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    for a, d in sorted(detail.items(), key=lambda kv: kv[1]["weight"]):
        print(f"  {a:16s} r={str(d['r']):>6}  n={d['n']:>3}  weight={d['weight']}")


if __name__ == "__main__":
    main()
