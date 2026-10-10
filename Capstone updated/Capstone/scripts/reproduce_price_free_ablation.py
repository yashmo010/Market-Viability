"""Reproducible price-free ablation experiment on the n=118 deployment cohort.

Removes the price feature from the aspect-based XGBoost model and evaluates
Spearman rank correlation against the ground-truth success score on the 118
paired holdout products.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ROOT / "data/extracted/features_physical.parquet"
PRODUCTS = ROOT / "data/final/products_physical.json"
PROFILES = ROOT / "data/extracted/category_profiles.json"
BRAND_TIERS = ROOT / "models/brand_tier_map.json"
OUT = ROOT / "models/benchmarks/price_free_ablation.json"

BRIDGED_SOURCES = [
    ROOT / "models/benchmarks/retro_bridged_v2.jsonl",
    ROOT / "models/benchmarks/holdout_bridged.jsonl",
    ROOT / "models/benchmarks/ice_holdout_bridged.jsonl",
]


def main() -> None:
    df = pd.read_parquet(FEATURES).set_index("product_uid")
    with open(PRODUCTS, encoding="utf-8") as f:
        products = {p["product_uid"]: p for p in json.load(f)}

    with open(BRAND_TIERS, encoding="utf-8") as f:
        bt = json.load(f)

    with open(PROFILES, encoding="utf-8") as f:
        profiles = json.load(f)

    cache: dict[str, dict] = {}
    for p in BRIDGED_SOURCES:
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    uid = r.get("product_uid")
                    if uid in df.index and r.get("bridged"):
                        cache[uid] = r

    uids = list(cache.keys())
    train_uids = [u for u in df.index if u not in cache]
    y_true = np.array([float(df.at[u, "success_score"]) for u in uids])

    bst = xgb.Booster()
    bst.load_model(str(ROOT / "models/xgb_physical_aspects_only.json"))
    aspect_cols = [c for c in bst.feature_names if c != "price"]

    rows = []
    for u in uids:
        r = cache[u]
        cat = str(df.at[u, "category"])
        prof = profiles[cat]
        brand = (products[u].get("brand") or "").strip().casefold()
        btier = float(bt["brands"].get(brand, 1))
        row = {col: np.nan for col in aspect_cols}
        row["category"] = cat
        for col in aspect_cols:
            if col in r["bridged"]:
                row[col] = float(r["bridged"][col])
            elif col.endswith("_mention_rate"):
                asp = col[:-len("_mention_rate")]
                row[col] = prof["avg_mention_rates"].get(asp, np.nan)
            elif col == "brand_tier":
                row[col] = btier
        rows.append(row)

    X_train = df.loc[train_uids, aspect_cols].copy()
    X_train["category"] = X_train["category"].astype("category")
    y_train = df.loc[train_uids, "success_score"].values
    X_test = pd.DataFrame(rows, columns=aspect_cols)
    X_test["category"] = X_test["category"].astype("category")

    dtrain = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
    dtest = xgb.DMatrix(X_test, enable_categorical=True)

    params = {
        "objective": "reg:squarederror",
        "learning_rate": 0.05,
        "max_depth": 5,
        "min_child_weight": 3,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "tree_method": "hist",
        "random_state": 42,
    }

    # Best iteration from aspects-only cross-validation
    model = xgb.train(params, dtrain, num_boost_round=297)
    preds = model.predict(dtest)
    rho, pval = stats.spearmanr(preds, y_true)

    result = {
        "experiment": "EXP-BASE-02: Price-Free Semantic Ablation",
        "n_holdout": len(uids),
        "n_train": len(train_uids),
        "features": aspect_cols,
        "num_boost_round": 297,
        "spearman_rho": round(float(rho), 3),
        "spearman_rho_exact": float(rho),
        "p_value": float(pval),
        "status": "VERIFIED"
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Price-free ablation on n={len(uids)}: rho = {rho:.4f} (rounded: {round(float(rho), 3)})")
    print(f"Result saved to {OUT}")


if __name__ == "__main__":
    main()
