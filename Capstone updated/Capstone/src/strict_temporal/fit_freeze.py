"""Strict Fit & Freeze Pipeline.

Performs all fitting operations EXCLUSIVELY on pre-cutoff training data.
Freezes every parameter and model artifact before any test prediction occurs.
"""

from __future__ import annotations

import collections
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[2]
TRAIN_DATA_DIR = ROOT / "strict_temporal/data/train"
FROZEN_DIR = ROOT / "strict_temporal/frozen_state"
FROZEN_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42

PHYSICAL_ASPECT_KEYS = [
    "value_for_money", "utility", "ease_of_use", "reliability",
    "design_appeal", "after_sales", "build_quality", "durability", "repairability"
]

MONOTONE_BY_FEATURE = {
    "price": -1,
    "brand_tier": 1,
    "value_for_money": 1, "utility": 1, "ease_of_use": 1, "reliability": 1,
    "design_appeal": 1, "after_sales": 1, "build_quality": 1, "durability": 1,
    "repairability": 1,
}

XGB_PARAMS = dict(
    objective="reg:squarederror",
    n_estimators=600,
    learning_rate=0.05,
    max_depth=5,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    enable_categorical=True,
    tree_method="hist",
    random_state=SEED,
)


def _brand_key(brand: str | None) -> str:
    return (brand or "").strip().casefold()


def _tier_from_footprint(n: int) -> int:
    if n >= 11:
        return 3
    if n >= 5:
        return 2
    if n >= 2:
        return 1
    return 0


def months_between(ts_a: int, ts_b: int) -> float:
    return abs(ts_b - ts_a) / (86400 * 30.44)


def fit_and_freeze_pipeline() -> dict[str, Any]:
    print("=" * 70)
    print("STEP 6: FIT & FREEZE ON PRE-CUTOFF DATA ONLY")
    print("=" * 70)

    # 1. Load Pre-Cutoff Training Data
    with open(TRAIN_DATA_DIR / "products.json", encoding="utf-8") as f:
        train_products: list[dict] = json.load(f)
    with open(TRAIN_DATA_DIR / "reviews.json", encoding="utf-8") as f:
        train_reviews: list[dict] = json.load(f)

    train_uids = {p["product_uid"] for p in train_products}
    print(f"Loaded {len(train_products)} training products, {len(train_reviews)} training reviews.")

    # 2. Fit Target Normalizer (min/max strictly on training products)
    rev_counts = collections.Counter(r["product_uid"] for r in train_reviews)
    cat_prods = {}
    for p in train_products:
        cat_prods.setdefault(p["category"], []).append(p)

    target_scalers = {}
    train_labels = {}
    for cat, prods in cat_prods.items():
        vols = np.log1p([rev_counts[p["product_uid"]] for p in prods])
        rats = np.array([p["avg_rating"] for p in prods], dtype=float)
        vels = np.array([
            rev_counts[p["product_uid"]] / max(months_between(p["first_review_ts"], p["latest_review_ts"]), 1.0)
            for p in prods
        ])
        v_min, v_max = float(np.min(vols)), float(np.max(vols))
        r_min, r_max = float(np.min(rats)), float(np.max(rats))
        vl_min, vl_max = float(np.min(vels)), float(np.max(vels))

        target_scalers[cat] = {
            "vol_min": v_min, "vol_max": v_max,
            "rat_min": r_min, "rat_max": r_max,
            "vel_min": vl_min, "vel_max": vl_max,
        }

        scale = lambda x, mn, mx: (x - mn) / (mx - mn) if (mx - mn) > 1e-12 else 0.5
        for i, p in enumerate(prods):
            vn = scale(vols[i], v_min, v_max)
            rn = scale(rats[i], r_min, r_max)
            veln = scale(vels[i], vl_min, vl_max)
            score = 100.0 * (0.40 * vn + 0.35 * rn + 0.25 * veln)
            train_labels[p["product_uid"]] = {
                "product_uid": p["product_uid"],
                "category": cat,
                "success_score": round(float(score), 3),
                "volume_norm": round(float(vn), 4),
                "rating_norm": round(float(rn), 4),
                "velocity_norm": round(float(veln), 4),
            }

    with open(FROZEN_DIR / "target_scalers.json", "w", encoding="utf-8") as f:
        json.dump(target_scalers, f, indent=2)
    print(f"Frozen target scalers to {FROZEN_DIR / 'target_scalers.json'}")

    # 3. Fit Brand Tiers strictly from training products
    brand_footprint = collections.defaultdict(int)
    for p in train_products:
        brand_footprint[_brand_key(p.get("brand"))] += 1

    brand_tier_map = {b: _tier_from_footprint(cnt) for b, cnt in brand_footprint.items()}
    established = [t for t in brand_tier_map.values() if t >= 1]
    established_prior = int(round(float(np.median(established)))) if established else 1

    brand_state = {
        "brands": brand_tier_map,
        "established_prior": established_prior,
        "new_tier": 0,
        "fitted_on_n_products": len(train_products),
        "fitted_on_n_brands": len(brand_tier_map),
    }
    with open(FROZEN_DIR / "brand_tier_map.json", "w", encoding="utf-8") as f:
        json.dump(brand_state, f, indent=2)
    print(f"Frozen brand tier map to {FROZEN_DIR / 'brand_tier_map.json'} ({len(brand_tier_map)} brands)")

    # 4. Load aspect extractions (filter to training products only)
    scores_path = ROOT / "data/extracted/aspect_scores.jsonl"
    per_product = collections.defaultdict(lambda: collections.defaultdict(list))
    n_extracted = collections.defaultdict(int)
    if scores_path.exists():
        with open(scores_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                uid = row["product_uid"]
                if uid not in train_uids:
                    continue  # STRICT ISOLATION: ignore any post-cutoff extractions
                if row.get("confidence", 0) < 0.3:
                    continue
                n_extracted[uid] += 1
                for aspect, val in row["scores"].items():
                    if val is not None:
                        per_product[uid][aspect].append(val["score"])

    # 5. Build Training Feature Matrix
    train_rows = []
    aspect_cols = PHYSICAL_ASPECT_KEYS
    mention_cols = [f"{a}_mention_rate" for a in aspect_cols]
    manifest_cols = ["price"] + aspect_cols + mention_cols + ["brand_tier", "category"]

    for p in train_products:
        uid = p["product_uid"]
        cat = p["category"]
        brand_t = brand_tier_map.get(_brand_key(p.get("brand")), 0)
        n_ext = n_extracted.get(uid, 0)

        row = {
            "product_uid": uid,
            "category": cat,
            "price": float(p.get("price", 0.0)),
            "brand_tier": brand_t,
            "success_score": train_labels[uid]["success_score"],
        }
        for a in aspect_cols:
            vals = per_product[uid].get(a, [])
            row[a] = float(np.mean(vals)) if vals else np.nan
            row[f"{a}_mention_rate"] = len(vals) / n_ext if n_ext > 0 else np.nan
        train_rows.append(row)

    train_df = pd.DataFrame(train_rows)
    train_df["category"] = train_df["category"].astype("category")
    train_df.to_parquet(FROZEN_DIR / "train_features.parquet", index=False)
    print(f"Built training feature matrix: {len(train_df)} rows")

    # 6. Fit Category Profiles strictly from training data
    # Collect evidence phrases from pre-cutoff extractions only
    cat_evidence = collections.defaultdict(lambda: collections.defaultdict(list))
    if scores_path.exists():
        with open(scores_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                uid = row["product_uid"]
                if uid not in train_uids:
                    continue
                cat = next((p["category"] for p in train_products if p["product_uid"] == uid), None)
                if not cat:
                    continue
                for aspect, val in row.get("scores", {}).items():
                    if val is not None and "evidence" in val and "score" in val:
                        cat_evidence[cat][aspect].append((val["score"], val["evidence"]))

    reddit_context = {}
    reddit_path = ROOT / "data/final/reddit_context.json"
    if reddit_path.exists():
        try:
            reddit_context = json.load(open(reddit_path, encoding="utf-8")) or {}
        except Exception:
            pass

    cat_profiles = {}
    for cat, group in train_df.groupby("category", observed=True):
        cat_str = str(cat)
        prices = group["price"].values
        avg_scores = {
            a: (round(float(group[a].mean()), 2) if group[a].notna().any() else 5.0)
            for a in aspect_cols
        }
        mention_rates = {
            a: (round(float(group[f"{a}_mention_rate"].mean()), 3) if group[f"{a}_mention_rate"].notna().any() else 0.1)
            for a in aspect_cols
        }

        # Rank worst and best aspects for pain points and strengths
        scored = {a: s for a, s in avg_scores.items() if s is not None}
        worst = sorted(scored, key=scored.get)[:3]
        best = sorted(scored, key=scored.get, reverse=True)[:3]

        def _phrases(aspect_list: list[str], low: bool) -> dict[str, list[str]]:
            out = {}
            for a in aspect_list:
                ranked = sorted(cat_evidence[cat_str].get(a, []), key=lambda t: t[0], reverse=not low)
                out[a] = [e for _, e in ranked[:15]]
            return out

        cat_profiles[cat_str] = {
            "n_products": int(len(group)),
            "price": {
                "mean": round(float(np.mean(prices)), 2),
                "median": round(float(np.median(prices)), 2),
                "p25": round(float(np.percentile(prices, 25)), 2),
                "p75": round(float(np.percentile(prices, 75)), 2),
                "min": round(float(np.min(prices)), 2),
                "max": round(float(np.max(prices)), 2),
            },
            "avg_aspect_scores": avg_scores,
            "avg_mention_rates": mention_rates,
            "pain_points": {"aspects": worst, "evidence": _phrases(worst, low=True)},
            "strengths": {"aspects": best, "evidence": _phrases(best, low=False)},
            "consumer_priorities": str(reddit_context.get(cat_str, ""))[:1000] if reddit_context.get(cat_str) else None,
            "success_score": {
                "mean": round(float(group["success_score"].mean()), 2),
                "median": round(float(np.median(group["success_score"])), 2),
                "min": round(float(np.min(group["success_score"])), 2),
                "max": round(float(np.max(group["success_score"])), 2),
            },
            "median_avg_rating": 4.2,
            "median_rating_count_log": 5.0,
            "median_review_velocity": 10.0,
        }

    with open(FROZEN_DIR / "category_profiles.json", "w", encoding="utf-8") as f:
        json.dump(cat_profiles, f, indent=2)
    print(f"Frozen category profiles to {FROZEN_DIR / 'category_profiles.json'}")

    # 7. Model Fitting with Pre-Cutoff Cross-Validation
    X = train_df[manifest_cols].copy()
    y = train_df["success_score"].to_numpy(dtype=float)

    # Monotonic constraints
    constraints = {c: MONOTONE_BY_FEATURE[c] for c in manifest_cols if c in MONOTONE_BY_FEATURE}
    params = dict(XGB_PARAMS)
    params["monotone_constraints"] = constraints

    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    best_iters = []
    cv_metrics = {"r2": [], "rmse": [], "mae": []}

    for fold, (tr_idx, va_idx) in enumerate(kf.split(X), 1):
        m = xgb.XGBRegressor(**params, early_stopping_rounds=50)
        m.fit(X.iloc[tr_idx], y[tr_idx], eval_set=[(X.iloc[va_idx], y[va_idx])], verbose=False)
        p_val = m.predict(X.iloc[va_idx])
        best_iters.append(int(m.best_iteration + 1) if m.best_iteration is not None else 600)
        cv_metrics["r2"].append(r2_score(y[va_idx], p_val))
        cv_metrics["rmse"].append(np.sqrt(mean_squared_error(y[va_idx], p_val)))
        cv_metrics["mae"].append(mean_absolute_error(y[va_idx], p_val))

    mean_iter = int(np.mean(best_iters))
    print(f"5-Fold CV on Training Set: mean R2={np.mean(cv_metrics['r2']):.3f}, "
          f"RMSE={np.mean(cv_metrics['rmse']):.2f}, best_iteration={mean_iter}")

    # Train final model on ALL pre-cutoff training products with best_iteration
    final_params = dict(params)
    final_params["n_estimators"] = mean_iter
    final_model = xgb.XGBRegressor(**final_params)
    final_model.fit(X, y, verbose=False)

    final_model.save_model(FROZEN_DIR / "xgb_physical_aspects_only.json")
    with open(FROZEN_DIR / "xgb_physical_aspects_only_features.json", "w", encoding="utf-8") as f:
        json.dump(manifest_cols, f, indent=2)

    print(f"Saved frozen model to {FROZEN_DIR / 'xgb_physical_aspects_only.json'}")

    return {
        "status": "FROZEN",
        "train_n": len(train_df),
        "cv_r2": float(np.mean(cv_metrics["r2"])),
        "cv_rmse": float(np.mean(cv_metrics["rmse"])),
        "cv_mae": float(np.mean(cv_metrics["mae"])),
        "best_iteration": mean_iter,
        "features": manifest_cols,
    }


if __name__ == "__main__":
    fit_and_freeze_pipeline()
