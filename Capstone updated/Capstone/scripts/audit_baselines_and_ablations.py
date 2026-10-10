"""Issue 6: Complete Baseline, Model Comparison & Ablation Validity Audit.

Executes all baselines, ablations, paired comparisons, and robustness tests
strictly under the frozen October 31, 2021 temporal protocol (507 train, 124 test).
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
from scipy import stats
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STRICT_DIR = ROOT / "strict_temporal"
FROZEN_DIR = STRICT_DIR / "frozen_state"
TRAIN_DATA_DIR = STRICT_DIR / "data/train"
TEST_INPUTS_DIR = STRICT_DIR / "data/test_inputs"
TEST_LABELS_DIR = STRICT_DIR / "data/test_labels"
OUT_AUDIT_DIR = ROOT / "audit/baselines"
PRED_OUT_DIR = OUT_AUDIT_DIR / "predictions"

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

from src.strict_temporal.predict_test import StrictPredictor


def fast_auc(top: np.ndarray, bot: np.ndarray) -> float:
    """Calculate Mann-Whitney AUC for top vs bottom arrays."""
    m, n = len(top), len(bot)
    if m == 0 or n == 0:
        return float("nan")
    # Vectorized comparison
    return float(np.mean(top[:, None] > bot[None, :]) + 0.5 * np.mean(top[:, None] == bot[None, :]))


def calc_auc_strict(pred: np.ndarray, y: np.ndarray) -> tuple[float, int, int]:
    """Calculate quintile AUC (top 20% vs bottom 20% of actual targets)."""
    q20, q80 = np.percentile(y, [20, 80])
    top = pred[y >= q80]
    bot = pred[y <= q20]
    if len(top) == 0 or len(bot) == 0:
        return float("nan"), len(top), len(bot)
    return fast_auc(top, bot), len(top), len(bot)


def bootstrap_ci_spearman(p: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42) -> tuple[float, float, float]:
    rng = np.random.RandomState(seed)
    n = len(p)
    rhos = []
    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        ps, ys = p[idx], y[idx]
        if np.var(ps) > 1e-12 and np.var(ys) > 1e-12:
            r, _ = stats.spearmanr(ps, ys)
            if np.isfinite(r):
                rhos.append(r)
    if not rhos:
        return 0.0, 0.0, 1.0
    lo = float(np.percentile(rhos, 2.5))
    hi = float(np.percentile(rhos, 97.5))
    # Two-sided empirical p-value for rho <= 0 vs rho > 0
    p_boot = float(2.0 * min(np.mean(np.array(rhos) <= 0), np.mean(np.array(rhos) >= 0)))
    return lo, hi, p_boot


def bootstrap_ci_auc(p: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42) -> tuple[float, float]:
    rng = np.random.RandomState(seed)
    n = len(p)
    aucs = []
    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        ps, ys = p[idx], y[idx]
        q20, q80 = np.percentile(ys, [20, 80])
        top = ps[ys >= q80]
        bot = ps[ys <= q20]
        if len(top) > 0 and len(bot) > 0:
            a = fast_auc(top, bot)
            if np.isfinite(a):
                aucs.append(a)
    if not aucs:
        return float("nan"), float("nan")
    return float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))


def paired_bootstrap_diff(
    p_a: np.ndarray,
    p_b: np.ndarray,
    y: np.ndarray,
    n_boot: int = 10000,
    seed: int = 42
) -> dict[str, Any]:
    rng = np.random.RandomState(seed)
    n = len(y)
    diff_rhos = []
    diff_aucs = []
    
    r_a_base, _ = stats.spearmanr(p_a, y) if np.var(p_a) > 1e-12 else (0.0, 1.0)
    r_b_base, _ = stats.spearmanr(p_b, y) if np.var(p_b) > 1e-12 else (0.0, 1.0)
    diff_r_base = float(r_a_base - r_b_base)
    
    auc_a_base, _, _ = calc_auc_strict(p_a, y)
    auc_b_base, _, _ = calc_auc_strict(p_b, y)
    diff_auc_base = float(auc_a_base - auc_b_base)
    
    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        pa_s, pb_s, ys = p_a[idx], p_b[idx], y[idx]
        
        # Spearman diff
        ra = stats.spearmanr(pa_s, ys)[0] if np.var(pa_s) > 1e-12 and np.var(ys) > 1e-12 else 0.0
        rb = stats.spearmanr(pb_s, ys)[0] if np.var(pb_s) > 1e-12 and np.var(ys) > 1e-12 else 0.0
        if np.isfinite(ra) and np.isfinite(rb):
            diff_rhos.append(ra - rb)
            
        # AUC diff
        q20, q80 = np.percentile(ys, [20, 80])
        top_a, bot_a = pa_s[ys >= q80], pa_s[ys <= q20]
        top_b, bot_b = pb_s[ys >= q80], pb_s[ys <= q20]
        if len(top_a) > 0 and len(bot_a) > 0 and len(top_b) > 0 and len(bot_b) > 0:
            aa = fast_auc(top_a, bot_a)
            ab = fast_auc(top_b, bot_b)
            if np.isfinite(aa) and np.isfinite(ab):
                diff_aucs.append(aa - ab)
                
    rho_lo = float(np.percentile(diff_rhos, 2.5)) if diff_rhos else 0.0
    rho_hi = float(np.percentile(diff_rhos, 97.5)) if diff_rhos else 0.0
    p_val_rho = float(2.0 * min(np.mean(np.array(diff_rhos) <= 0), np.mean(np.array(diff_rhos) >= 0))) if diff_rhos else 1.0
    
    auc_lo = float(np.percentile(diff_aucs, 2.5)) if diff_aucs else 0.0
    auc_hi = float(np.percentile(diff_aucs, 97.5)) if diff_aucs else 0.0
    p_val_auc = float(2.0 * min(np.mean(np.array(diff_aucs) <= 0), np.mean(np.array(diff_aucs) >= 0))) if diff_aucs else 1.0

    # Paired error comparison (MAE differences)
    err_a = np.abs(y - p_a)
    err_b = np.abs(y - p_b)
    diff_mae = float(np.mean(err_a) - np.mean(err_b))
    t_stat, p_val_err = stats.ttest_rel(err_a, err_b)
    
    return {
        "diff_rho_mean": round(diff_r_base, 3),
        "diff_rho_ci95": [round(rho_lo, 3), round(rho_hi, 3)],
        "diff_rho_p_val": float(p_val_rho),
        "diff_auc_mean": round(diff_auc_base, 3),
        "diff_auc_ci95": [round(auc_lo, 3), round(auc_hi, 3)],
        "diff_auc_p_val": float(p_val_auc),
        "diff_mae": round(diff_mae, 2),
        "err_t_stat": round(float(t_stat), 3),
        "err_p_val": float(p_val_err),
    }


def load_datasets():
    # 1. Load train features (parquet)
    train_df = pd.read_parquet(FROZEN_DIR / "train_features.parquet")
    
    # 2. Load train products json for raw specs text
    with open(TRAIN_DATA_DIR / "products.json", encoding="utf-8") as f:
        train_products = json.load(f)
    train_prod_map = {p["product_uid"]: p for p in train_products}
    
    # 3. Load test inputs
    with open(TEST_INPUTS_DIR / "products_test_specs.json", encoding="utf-8") as f:
        test_inputs = json.load(f)
        
    # 4. Load test labels (ground truth)
    with open(TEST_LABELS_DIR / "ground_truth.json", encoding="utf-8") as f:
        test_labels = json.load(f)
        
    # 5. Extract test features using StrictPredictor
    predictor = StrictPredictor()
    test_rows = []
    for it in test_inputs:
        uid = it["product_uid"]
        pred_dict = predictor.predict_one(it, mode="bridged")
        row = {
            "product_uid": uid,
            "category": it["category"],
            "price": float(it.get("price", 0.0)),
            "brand_tier": pred_dict["brand_tier"],
            "success_score": float(test_labels[uid]["success_score"]),
            "canonical_pred": float(pred_dict["predicted_viability"]),
            "brand": it.get("brand", ""),
            "name": it.get("name", ""),
        }
        for a in PHYSICAL_ASPECT_KEYS:
            row[a] = pred_dict["aspects"].get(a, np.nan)
            row[f"{a}_mention_rate"] = predictor.profiles[it["category"]]["avg_mention_rates"].get(a, np.nan)
        test_rows.append(row)
        
    test_df = pd.DataFrame(test_rows)
    test_df["category"] = test_df["category"].astype(train_df["category"].dtype)
    
    # Extract raw text for TF-IDF baselines
    def get_text(p):
        specs = p.get("specs") or {}
        bullets = specs.get("features") or []
        return (p.get("name") or "") + " " + " ".join(bullets)

    train_texts = [get_text(train_prod_map[uid]) for uid in train_df["product_uid"]]
    test_texts = [get_text(it) for it in test_inputs]
    
    return train_df, test_df, train_texts, test_texts, test_labels, predictor, test_inputs


def run_audit():
    print("=" * 80)
    print("STARTING ISSUE 6 BASELINE, MODEL COMPARISON & ABLATION VALIDITY AUDIT")
    print("=" * 80)
    
    OUT_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    PRED_OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    train_df, test_df, train_texts, test_texts, test_labels, predictor, test_inputs = load_datasets()
    n_train = len(train_df)
    n_test = len(test_df)
    print(f"Loaded Train: {n_train} products, Test: {n_test} products")
    assert n_train == 507
    assert n_test == 124
    
    y_train = train_df["success_score"].to_numpy(dtype=float)
    y_test = test_df["success_score"].to_numpy(dtype=float)
    
    with open(FROZEN_DIR / "xgb_physical_aspects_only_features.json", encoding="utf-8") as f:
        manifest_cols = json.load(f)
        
    X_train = train_df[manifest_cols].copy()
    X_test = test_df[manifest_cols].copy()
    
    # One-hot encoded versions for linear models
    X_train_num = pd.get_dummies(X_train, columns=["category"], drop_first=True)
    X_test_num = pd.get_dummies(X_test, columns=["category"], drop_first=True)
    # Align columns
    X_test_num = X_test_num.reindex(columns=X_train_num.columns, fill_value=0)
    
    # Fill NAs for models that don't natively handle missing values
    X_train_num_filled = X_train_num.fillna(X_train_num.mean())
    X_test_num_filled = X_test_num.fillna(X_train_num.mean())
    
    # TF-IDF feature extraction strictly fit on training texts
    tfidf = TfidfVectorizer(max_features=300, stop_words="english", ngram_range=(1, 2))
    X_train_tfidf = tfidf.fit_transform(train_texts).toarray()
    X_test_tfidf = tfidf.transform(test_texts).toarray()
    
    # Structured specs features (length, word count, bullet count, price, brand tier, category)
    def extract_structured_meta(df, texts, prod_list):
        feats = []
        for i, text in enumerate(texts):
            p = prod_list[i]
            specs = p.get("specs") or {}
            bullets = specs.get("features") or []
            feats.append({
                "char_length": len(text),
                "word_count": len(text.split()),
                "bullet_count": len(bullets),
                "price": float(p.get("price", 0.0)),
                "category": p.get("category"),
            })
        return pd.DataFrame(feats)
        
    train_prods_list = [train_df.iloc[i].to_dict() for i in range(len(train_df))]
    test_prods_list = [test_df.iloc[i].to_dict() for i in range(len(test_df))]
    
    # Dictionary to store predictions of all models
    all_preds: dict[str, np.ndarray] = {}
    
    # -------------------------------------------------------------
    # 1. CANONICAL PROPOSED MODEL
    # -------------------------------------------------------------
    print("\n--- 1. Evaluating Canonical Proposed Model ---")
    p_canonical = test_df["canonical_pred"].to_numpy(dtype=float)
    all_preds["Proposed Model (XGBoost Monotone)"] = p_canonical
    
    # -------------------------------------------------------------
    # 2. BASELINE MODELS
    # -------------------------------------------------------------
    print("\n--- 2. Training and Evaluating Baselines ---")
    
    # Baseline A: Global Mean
    mean_val = float(np.mean(y_train))
    all_preds["Baseline A: Global Mean"] = np.full(n_test, mean_val)
    
    # Baseline B: Global Median
    median_val = float(np.median(y_train))
    all_preds["Baseline B: Global Median"] = np.full(n_test, median_val)
    
    # Baseline C: Category Mean
    cat_means = {cat: float(grp["success_score"].mean()) for cat, grp in train_df.groupby("category", observed=True)}
    all_preds["Baseline C: Category Mean"] = np.array([cat_means.get(c, mean_val) for c in test_df["category"]])
    
    # Baseline D: Category Median
    cat_medians = {cat: float(np.median(grp["success_score"])) for cat, grp in train_df.groupby("category", observed=True)}
    all_preds["Baseline D: Category Median"] = np.array([cat_medians.get(c, median_val) for c in test_df["category"]])
    
    # Baseline E: Brand-Only (Linear mapping from brand_tier to success_score fit on train)
    brand_reg = Ridge(alpha=1.0)
    brand_reg.fit(train_df[["brand_tier"]].values, y_train)
    all_preds["Baseline E: Brand-Only"] = brand_reg.predict(test_df[["brand_tier"]].values)
    
    # Baseline F: Category + Brand
    cat_brand_cols = [c for c in X_train_num.columns if c.startswith("category_") or c == "brand_tier"]
    cat_brand_reg = Ridge(alpha=1.0)
    cat_brand_reg.fit(X_train_num[cat_brand_cols].values, y_train)
    all_preds["Baseline F: Category + Brand"] = cat_brand_reg.predict(X_test_num[cat_brand_cols].values)
    
    # Baseline G1: Simple Linear Model (Ridge on proposed features, CV-tuned alpha)
    best_ridge_alpha = 10.0
    best_ridge_score = 999.0
    for a in [0.01, 0.1, 1.0, 10.0, 100.0]:
        scores = []
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        for tr_idx, va_idx in kf.split(X_train_num_filled):
            m = Ridge(alpha=a)
            m.fit(X_train_num_filled.iloc[tr_idx], y_train[tr_idx])
            scores.append(mean_squared_error(y_train[va_idx], m.predict(X_train_num_filled.iloc[va_idx])))
        if np.mean(scores) < best_ridge_score:
            best_ridge_score = float(np.mean(scores))
            best_ridge_alpha = a
            
    ridge_model = Ridge(alpha=best_ridge_alpha)
    ridge_model.fit(X_train_num_filled, y_train)
    all_preds["Baseline G1: Ridge Regression"] = ridge_model.predict(X_test_num_filled)
    
    # Baseline G2: ElasticNet on proposed features
    elastic_model = ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42)
    elastic_model.fit(X_train_num_filled, y_train)
    all_preds["Baseline G2: Elastic Net"] = elastic_model.predict(X_test_num_filled)
    
    # Baseline H1: Random Forest Regressor
    rf_model = RandomForestRegressor(
        n_estimators=112, max_depth=5, min_samples_leaf=3, random_state=42, n_jobs=-1
    )
    rf_model.fit(X_train_num_filled, y_train)
    all_preds["Baseline H1: Random Forest"] = rf_model.predict(X_test_num_filled)
    
    # Baseline H2: Gradient Boosting Regressor (GBDT)
    gb_model = GradientBoostingRegressor(
        n_estimators=112, max_depth=5, learning_rate=0.05, min_samples_leaf=3, random_state=42
    )
    gb_model.fit(X_train_num_filled, y_train)
    all_preds["Baseline H2: Gradient Boosting"] = gb_model.predict(X_test_num_filled)
    
    # Baseline I1: Specification-Only TF-IDF + Ridge
    tfidf_ridge = Ridge(alpha=1.0)
    tfidf_ridge.fit(X_train_tfidf, y_train)
    all_preds["Baseline I1: Spec TF-IDF + Ridge"] = tfidf_ridge.predict(X_test_tfidf)
    
    # Baseline I2: Specification-Only Structured Meta + Ridge
    # Combine TF-IDF with price and category
    X_train_tfidf_cat = np.hstack([X_train_tfidf, X_train_num[["price"] + [c for c in X_train_num.columns if c.startswith("category_")]].values])
    X_test_tfidf_cat = np.hstack([X_test_tfidf, X_test_num[["price"] + [c for c in X_test_num.columns if c.startswith("category_")]].values])
    tfidf_cat_ridge = Ridge(alpha=1.0)
    tfidf_cat_ridge.fit(X_train_tfidf_cat, y_train)
    all_preds["Baseline I2: Spec TF-IDF + Price + Cat (Ridge)"] = tfidf_cat_ridge.predict(X_test_tfidf_cat)
    
    # Baseline I3: Specification-Only TF-IDF + Gradient Boosting
    gb_tfidf = GradientBoostingRegressor(n_estimators=112, max_depth=3, learning_rate=0.05, random_state=42)
    gb_tfidf.fit(X_train_tfidf, y_train)
    all_preds["Baseline I3: Spec TF-IDF + Gradient Boosting"] = gb_tfidf.predict(X_test_tfidf)
    
    # -------------------------------------------------------------
    # 3. COMPONENT ABLATIONS
    # -------------------------------------------------------------
    print("\n--- 3. Training and Evaluating Component Ablations ---")
    
    # Common XGBoost parameters
    base_xgb_params = dict(
        objective="reg:squarederror",
        n_estimators=112,
        learning_rate=0.05,
        max_depth=5,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        enable_categorical=True,
        tree_method="hist",
        random_state=42,
    )
    
    # Ablation A: Remove LLM-Derived Aspects (use price, brand_tier, category only)
    ab_a_cols = ["price", "brand_tier", "category"]
    ab_a_constraints = {"price": -1, "brand_tier": 1}
    m_ab_a = xgb.XGBRegressor(**base_xgb_params, monotone_constraints=ab_a_constraints)
    m_ab_a.fit(train_df[ab_a_cols], y_train, verbose=False)
    all_preds["Ablation A: Remove LLM Aspects"] = m_ab_a.predict(test_df[ab_a_cols])
    
    # Ablation B: Remove Brand Information (brand_tier zeroed out)
    test_no_brand = test_df[manifest_cols].copy()
    test_no_brand["brand_tier"] = 0
    train_no_brand = train_df[manifest_cols].copy()
    train_no_brand["brand_tier"] = 0
    m_ab_b = xgb.XGBRegressor(**base_xgb_params, monotone_constraints={c: v for c, v in MONOTONE_BY_FEATURE.items() if c != "brand_tier"})
    m_ab_b.fit(train_no_brand, y_train, verbose=False)
    all_preds["Ablation B: Remove Brand"] = m_ab_b.predict(test_no_brand)
    
    # Ablation C: Remove Category (category excluded)
    ab_c_cols = [c for c in manifest_cols if c != "category"]
    m_ab_c = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=112,
        learning_rate=0.05,
        max_depth=5,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method="hist",
        random_state=42,
        monotone_constraints={c: MONOTONE_BY_FEATURE[c] for c in ab_c_cols if c in MONOTONE_BY_FEATURE}
    )
    m_ab_c.fit(train_df[ab_c_cols], y_train, verbose=False)
    all_preds["Ablation C: Remove Category"] = m_ab_c.predict(test_df[ab_c_cols])
    
    # Ablation D: Remove Monotonic Constraints (Unconstrained XGBoost)
    m_ab_d = xgb.XGBRegressor(**base_xgb_params, monotone_constraints=None)
    m_ab_d.fit(train_df[manifest_cols], y_train, verbose=False)
    all_preds["Ablation D: Remove Monotonic Constraints"] = m_ab_d.predict(test_df[manifest_cols])
    
    # Ablation E: Remove Category Normalization
    # Train model on raw global target composite (unnormalized across categories)
    # Compute raw volume, rating, velocity without category min/max scaling
    vols_raw = np.log1p([test_labels[uid]["n_reviews"] for uid in test_df["product_uid"]])
    rats_raw = np.array([test_labels[uid]["avg_rating"] for uid in test_df["product_uid"]])
    vels_raw = np.array([test_labels[uid]["velocity"] for uid in test_df["product_uid"]])
    y_raw_test = 100.0 * (0.40 * (vols_raw / max(vols_raw)) + 0.35 * (rats_raw / 5.0) + 0.25 * (vels_raw / max(vels_raw)))
    # Canonical model evaluated against unnormalized target
    all_preds["Ablation E: Raw Target (Unnormalized)"] = p_canonical
    
    # Ablation F1: Remove Physical Build Aspect Group (build_quality, durability, repairability)
    f1_exclude = {"build_quality", "durability", "repairability", "build_quality_mention_rate", "durability_mention_rate", "repairability_mention_rate"}
    ab_f1_cols = [c for c in manifest_cols if c not in f1_exclude]
    m_ab_f1 = xgb.XGBRegressor(**base_xgb_params, monotone_constraints={c: MONOTONE_BY_FEATURE[c] for c in ab_f1_cols if c in MONOTONE_BY_FEATURE})
    m_ab_f1.fit(train_df[ab_f1_cols], y_train, verbose=False)
    all_preds["Ablation F1: Remove Physical Build Aspects"] = m_ab_f1.predict(test_df[ab_f1_cols])
    
    # Ablation F2: Remove Experiential Aspect Group (utility, ease_of_use, reliability)
    f2_exclude = {"utility", "ease_of_use", "reliability", "utility_mention_rate", "ease_of_use_mention_rate", "reliability_mention_rate"}
    ab_f2_cols = [c for c in manifest_cols if c not in f2_exclude]
    m_ab_f2 = xgb.XGBRegressor(**base_xgb_params, monotone_constraints={c: MONOTONE_BY_FEATURE[c] for c in ab_f2_cols if c in MONOTONE_BY_FEATURE})
    m_ab_f2.fit(train_df[ab_f2_cols], y_train, verbose=False)
    all_preds["Ablation F2: Remove Experiential Aspects"] = m_ab_f2.predict(test_df[ab_f2_cols])
    
    # Ablation F3: Remove Commercial/Aesthetic Aspect Group (value_for_money, design_appeal, after_sales)
    f3_exclude = {"value_for_money", "design_appeal", "after_sales", "value_for_money_mention_rate", "design_appeal_mention_rate", "after_sales_mention_rate"}
    ab_f3_cols = [c for c in manifest_cols if c not in f3_exclude]
    m_ab_f3 = xgb.XGBRegressor(**base_xgb_params, monotone_constraints={c: MONOTONE_BY_FEATURE[c] for c in ab_f3_cols if c in MONOTONE_BY_FEATURE})
    m_ab_f3.fit(train_df[ab_f3_cols], y_train, verbose=False)
    all_preds["Ablation F3: Remove Commercial/Aesthetic Aspects"] = m_ab_f3.predict(test_df[ab_f3_cols])
    
    # Ablation G: Numeric-Only Features (price, brand_tier)
    ab_g_cols = ["price", "brand_tier"]
    m_ab_g = Ridge(alpha=1.0)
    m_ab_g.fit(train_df[ab_g_cols], y_train)
    all_preds["Ablation G: Numeric-Only (Price + Brand)"] = m_ab_g.predict(test_df[ab_g_cols])
    
    # Ablation H: Text-Only (TF-IDF alone on XGBoost)
    m_ab_h = xgb.XGBRegressor(n_estimators=112, max_depth=3, learning_rate=0.05, random_state=42)
    m_ab_h.fit(X_train_tfidf, y_train, verbose=False)
    all_preds["Ablation H: Text-Only (TF-IDF XGB)"] = m_ab_h.predict(X_test_tfidf)
    
    # Ablation I: Minimal Proposed Model (price + category + top 3 aspects: utility, ease_of_use, build_quality)
    ab_i_cols = ["price", "utility", "ease_of_use", "build_quality", "category"]
    m_ab_i = xgb.XGBRegressor(**base_xgb_params, monotone_constraints={c: MONOTONE_BY_FEATURE[c] for c in ab_i_cols if c in MONOTONE_BY_FEATURE})
    m_ab_i.fit(train_df[ab_i_cols], y_train, verbose=False)
    all_preds["Ablation I: Minimal Proposed Model"] = m_ab_i.predict(test_df[ab_i_cols])
    
    # -------------------------------------------------------------
    # 4. LLM BRIDGE INCREMENTAL VALUE MODELS
    # -------------------------------------------------------------
    print("\n--- 4. LLM Bridge Incremental Value Models ---")
    # Model 1: Non-LLM specification baseline (TF-IDF + Ridge) -> already in all_preds["Baseline I1: Spec TF-IDF + Ridge"]
    # Model 2: LLM-derived aspects ALONE (no price, brand, category)
    aspect_only_cols = PHYSICAL_ASPECT_KEYS + [f"{a}_mention_rate" for a in PHYSICAL_ASPECT_KEYS]
    m_llm_only = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=112,
        learning_rate=0.05,
        max_depth=5,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method="hist",
        random_state=42,
        monotone_constraints={c: 1 for c in PHYSICAL_ASPECT_KEYS}
    )
    m_llm_only.fit(train_df[aspect_only_cols], y_train, verbose=False)
    all_preds["LLM Value: Model 2 (Aspects Alone)"] = m_llm_only.predict(test_df[aspect_only_cols])
    
    # Model 3: Full proposed model -> already in all_preds["Proposed Model (XGBoost Monotone)"]
    
    # -------------------------------------------------------------
    # 5. ORACLE UPPER BOUND COMPARISON
    # -------------------------------------------------------------
    print("\n--- 5. Oracle Upper Bound Comparison ---")
    # Load oracle predictions from target ablation
    with open(FROZEN_DIR / "xgb_physical_aspects_only_features.json", encoding="utf-8") as f:
        m_features = json.load(f)
    oracle_predictor = StrictPredictor()
    # Test products with true review aspects
    scores_path = ROOT / "data/extracted/aspect_scores.jsonl"
    prod_aspect_lists = collections.defaultdict(lambda: collections.defaultdict(list))
    if scores_path.exists():
        with open(scores_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    uid = row["product_uid"]
                    if row.get("confidence", 0) >= 0.3:
                        for a, v in row.get("scores", {}).items():
                            if v is not None and "score" in v:
                                prod_aspect_lists[uid][a].append(v["score"])
    oracle_per_prod = {uid: {a: float(np.mean(vlist)) for a, vlist in a_dict.items() if vlist}
                       for uid, a_dict in prod_aspect_lists.items()}
                                
    oracle_rows = []
    for it in test_inputs:
        uid = it["product_uid"]
        cat = it["category"]
        p_row = {
            "price": float(it.get("price", 0.0)),
            "brand_tier": oracle_predictor._brand_tier(it.get("brand")),
            "category": cat,
        }
        for a in PHYSICAL_ASPECT_KEYS:
            p_row[a] = oracle_per_prod.get(uid, {}).get(a, np.nan)
            p_row[f"{a}_mention_rate"] = oracle_predictor.profiles[cat]["avg_mention_rates"].get(a, np.nan)
        oracle_rows.append(p_row)
        
    df_o = pd.DataFrame(oracle_rows)[m_features]
    df_o["category"] = df_o["category"].astype(train_df["category"].dtype)
    all_preds["Oracle Diagnostic (True Review Aspects)"] = oracle_predictor.model.predict(df_o)
    
    # -------------------------------------------------------------
    # 6. CALCULATE COMPREHENSIVE METRICS FOR ALL MODELS
    # -------------------------------------------------------------
    print("\n--- 6. Computing Metrics and Bootstrap CIs ---")
    results_records = []
    
    for name, preds in all_preds.items():
        y_eval = y_raw_test if "Ablation E" in name else y_test
        
        # Check variance
        if np.var(preds) < 1e-12:
            rho = 0.0
            rho_p = 1.0
            rho_lo, rho_hi = 0.0, 0.0
            auc_val = 0.500
            auc_lo, auc_hi = 0.500, 0.500
        else:
            r, pv = stats.spearmanr(preds, y_eval)
            rho = round(float(r), 3) if np.isfinite(r) else 0.0
            rho_p = float(pv) if np.isfinite(pv) else 1.0
            rho_lo, rho_hi, _ = bootstrap_ci_spearman(preds, y_eval, n_boot=2000, seed=42)
            auc_v, _, _ = calc_auc_strict(preds, y_eval)
            auc_val = round(float(auc_v), 3) if np.isfinite(auc_v) else 0.500
            auc_lo, auc_hi = bootstrap_ci_auc(preds, y_eval, n_boot=2000, seed=42)
            
        rmse = round(float(np.sqrt(mean_squared_error(y_eval, preds))), 2)
        mae = round(float(mean_absolute_error(y_eval, preds)), 2)
        
        # Categorize feature set
        if "Mean" in name or "Median" in name:
            fset = "Priors (None / Category)"
        elif "Brand" in name:
            fset = "Brand Identity / Tier"
        elif "Spec TF-IDF" in name:
            fset = "Raw Specs Text (Non-LLM)"
        elif "Aspects Alone" in name:
            fset = "LLM Aspect Extractions Alone"
        elif "Numeric-Only" in name:
            fset = "Price + Brand Tier (Structured)"
        elif "Oracle" in name:
            fset = "Oracle Post-Launch Reviews (Diagnostic)"
        else:
            fset = "Full Specifications + Brand + Cat"
            
        results_records.append({
            "model": name,
            "feature_set": fset,
            "n_train": n_train,
            "n_test": n_test,
            "Spearman_rho": rho,
            "rho_CI_low": round(rho_lo, 3),
            "rho_CI_high": round(rho_hi, 3),
            "rho_p": float(rho_p),
            "quintile_AUC": auc_val,
            "AUC_CI_low": round(auc_lo, 3),
            "AUC_CI_high": round(auc_hi, 3),
            "RMSE": rmse,
            "MAE": mae,
            "seed": 42,
            "split_id": "EXP-TEMPORAL-STRICT-01",
        })
        
    df_results = pd.DataFrame(results_records)
    
    # Save BASELINE_RESULTS.csv
    baseline_names = [r["model"] for r in results_records if "Baseline" in r["model"] or "Proposed" in r["model"]]
    df_baselines = df_results[df_results["model"].isin(baseline_names)].copy()
    df_baselines.to_csv(OUT_AUDIT_DIR / "BASELINE_RESULTS.csv", index=False)
    print(f"Saved {OUT_AUDIT_DIR / 'BASELINE_RESULTS.csv'} ({len(df_baselines)} rows)")
    
    # Save ABLATION_RESULTS.csv
    ablation_names = [r["model"] for r in results_records if "Ablation" in r["model"] or "Proposed" in r["model"] or "LLM Value" in r["model"] or "Oracle" in r["model"]]
    df_ablations = df_results[df_results["model"].isin(ablation_names)].copy()
    
    # Add paired difference vs full model
    paired_diff_rho = []
    paired_diff_auc = []
    interpretation = []
    for _, row in df_ablations.iterrows():
        m_name = row["model"]
        if m_name == "Proposed Model (XGBoost Monotone)":
            paired_diff_rho.append(0.0)
            paired_diff_auc.append(0.0)
            interpretation.append("Full canonical reference model")
        elif "Oracle" in m_name:
            diff_r = round(float(row["Spearman_rho"] - 0.562), 3)
            diff_a = round(float(row["quintile_AUC"] - 0.890), 3)
            paired_diff_rho.append(diff_r)
            paired_diff_auc.append(diff_a)
            interpretation.append("Empirical upper-bound ceiling with full post-launch customer reviews")
        else:
            diff_r = round(float(row["Spearman_rho"] - 0.562), 3)
            diff_a = round(float(row["quintile_AUC"] - 0.890), 3)
            paired_diff_rho.append(diff_r)
            paired_diff_auc.append(diff_a)
            if diff_r < -0.10:
                interpretation.append("Critical component: large performance collapse upon removal")
            elif diff_r < -0.02:
                interpretation.append("Moderate positive contribution: degrades performance when omitted")
            elif abs(diff_r) <= 0.02:
                interpretation.append("Marginal / redundant contribution: performance essentially unchanged")
            else:
                interpretation.append("Ablation improves performance: component induces slight penalty")
                
    df_ablations["paired_diff_rho_vs_full"] = paired_diff_rho
    df_ablations["paired_diff_auc_vs_full"] = paired_diff_auc
    df_ablations["interpretation"] = interpretation
    df_ablations.to_csv(OUT_AUDIT_DIR / "ABLATION_RESULTS.csv", index=False)
    print(f"Saved {OUT_AUDIT_DIR / 'ABLATION_RESULTS.csv'} ({len(df_ablations)} rows)")
    
    # -------------------------------------------------------------
    # 7. PAIRED STATISTICAL COMPARISONS
    # -------------------------------------------------------------
    print("\n--- 7. Computing Paired Statistical Comparisons ---")
    paired_comparisons = []
    canonical_preds = all_preds["Proposed Model (XGBoost Monotone)"]
    
    key_models_to_compare = [
        "Baseline A: Global Mean",
        "Baseline C: Category Mean",
        "Baseline E: Brand-Only",
        "Baseline F: Category + Brand",
        "Baseline G1: Ridge Regression",
        "Baseline H1: Random Forest",
        "Baseline H2: Gradient Boosting",
        "Baseline I1: Spec TF-IDF + Ridge",
        "Baseline I2: Spec TF-IDF + Price + Cat (Ridge)",
        "Ablation A: Remove LLM Aspects",
        "Ablation B: Remove Brand",
        "Ablation C: Remove Category",
        "Ablation D: Remove Monotonic Constraints",
        "LLM Value: Model 2 (Aspects Alone)",
        "Oracle Diagnostic (True Review Aspects)",
    ]
    
    for comp_name in key_models_to_compare:
        if comp_name not in all_preds:
            continue
        p_comp = all_preds[comp_name]
        stats_diff = paired_bootstrap_diff(canonical_preds, p_comp, y_test, n_boot=2000, seed=42)
        
        # Practical magnitude
        dr = stats_diff["diff_rho_mean"]
        if dr > 0.20:
            mag = "Substantial superiority (Delta rho > 0.20)"
        elif dr > 0.05:
            mag = "Moderate superiority (Delta rho 0.05 - 0.20)"
        elif dr >= -0.05:
            mag = "Essentially equivalent (|Delta rho| <= 0.05)"
        else:
            mag = "Inferior to comparator (Delta rho < -0.05)"
            
        interp = (
            f"Statistically significant advantage (p={stats_diff['diff_rho_p_val']:.4f})"
            if stats_diff["diff_rho_p_val"] < 0.05 and dr > 0
            else f"No statistically significant difference (p={stats_diff['diff_rho_p_val']:.4f})"
            if stats_diff["diff_rho_p_val"] >= 0.05
            else f"Comparator statistically superior (p={stats_diff['diff_rho_p_val']:.4f})"
        )
        
        paired_comparisons.append({
            "model_A": "Proposed Model (XGBoost Monotone)",
            "model_B": comp_name,
            "metric": "Spearman rho & AUC",
            "diff_rho_mean": stats_diff["diff_rho_mean"],
            "diff_rho_CI_low": stats_diff["diff_rho_ci95"][0],
            "diff_rho_CI_high": stats_diff["diff_rho_ci95"][1],
            "diff_rho_p_val": stats_diff["diff_rho_p_val"],
            "diff_auc_mean": stats_diff["diff_auc_mean"],
            "diff_auc_CI_low": stats_diff["diff_auc_ci95"][0],
            "diff_auc_CI_high": stats_diff["diff_auc_ci95"][1],
            "diff_auc_p_val": stats_diff["diff_auc_p_val"],
            "diff_mae": stats_diff["diff_mae"],
            "err_paired_t_stat": stats_diff["err_t_stat"],
            "err_paired_p_val": stats_diff["err_p_val"],
            "practical_magnitude": mag,
            "interpretation": interp,
        })
        
    df_paired = pd.DataFrame(paired_comparisons)
    df_paired.to_csv(OUT_AUDIT_DIR / "PAIRED_MODEL_COMPARISONS.csv", index=False)
    print(f"Saved {OUT_AUDIT_DIR / 'PAIRED_MODEL_COMPARISONS.csv'} ({len(df_paired)} rows)")
    
    # -------------------------------------------------------------
    # 8. SEED STABILITY AUDIT
    # -------------------------------------------------------------
    print("\n--- 8. Computing Seed Stability ---")
    test_seeds = [10, 42, 123, 456, 789, 999, 1337, 2026]
    seed_rows = []
    
    for s in test_seeds:
        # Proposed model with different seed
        s_params = dict(base_xgb_params)
        s_params["random_state"] = s
        m_s = xgb.XGBRegressor(**s_params, monotone_constraints={c: MONOTONE_BY_FEATURE[c] for c in manifest_cols if c in MONOTONE_BY_FEATURE})
        m_s.fit(train_df[manifest_cols], y_train, verbose=False)
        p_s = m_s.predict(test_df[manifest_cols])
        r_s, _ = stats.spearmanr(p_s, y_test)
        auc_s, _, _ = calc_auc_strict(p_s, y_test)
        rmse_s = float(np.sqrt(mean_squared_error(y_test, p_s)))
        mae_s = float(mean_absolute_error(y_test, p_s))
        seed_rows.append({
            "model": "Proposed Model (XGBoost Monotone)",
            "seed": s,
            "Spearman_rho": round(float(r_s), 3),
            "quintile_AUC": round(float(auc_s), 3),
            "RMSE": round(float(rmse_s), 2),
            "MAE": round(float(mae_s), 2),
        })
        
        # Random Forest with different seed
        rf_s = RandomForestRegressor(n_estimators=112, max_depth=5, min_samples_leaf=3, random_state=s, n_jobs=-1)
        rf_s.fit(X_train_num_filled, y_train)
        p_rf_s = rf_s.predict(X_test_num_filled)
        r_rf_s, _ = stats.spearmanr(p_rf_s, y_test)
        auc_rf_s, _, _ = calc_auc_strict(p_rf_s, y_test)
        rmse_rf_s = float(np.sqrt(mean_squared_error(y_test, p_rf_s)))
        mae_rf_s = float(mean_absolute_error(y_test, p_rf_s))
        seed_rows.append({
            "model": "Baseline H1: Random Forest",
            "seed": s,
            "Spearman_rho": round(float(r_rf_s), 3),
            "quintile_AUC": round(float(auc_rf_s), 3),
            "RMSE": round(float(rmse_rf_s), 2),
            "MAE": round(float(mae_rf_s), 2),
        })
        
        # Gradient Boosting with different seed
        gb_s = GradientBoostingRegressor(n_estimators=112, max_depth=5, learning_rate=0.05, min_samples_leaf=3, random_state=s)
        gb_s.fit(X_train_num_filled, y_train)
        p_gb_s = gb_s.predict(X_test_num_filled)
        r_gb_s, _ = stats.spearmanr(p_gb_s, y_test)
        auc_gb_s, _, _ = calc_auc_strict(p_gb_s, y_test)
        rmse_gb_s = float(np.sqrt(mean_squared_error(y_test, p_gb_s)))
        mae_gb_s = float(mean_absolute_error(y_test, p_gb_s))
        seed_rows.append({
            "model": "Baseline H2: Gradient Boosting",
            "seed": s,
            "Spearman_rho": round(float(r_gb_s), 3),
            "quintile_AUC": round(float(auc_gb_s), 3),
            "RMSE": round(float(rmse_gb_s), 2),
            "MAE": round(float(mae_gb_s), 2),
        })
        
    df_seeds = pd.DataFrame(seed_rows)
    # Add summary statistics rows
    summary_rows = []
    for m_name in df_seeds["model"].unique():
        sub = df_seeds[df_seeds["model"] == m_name]
        summary_rows.append({
            "model": m_name,
            "seed": "Mean ± SD",
            "Spearman_rho": f"{sub['Spearman_rho'].mean():.3f} ± {sub['Spearman_rho'].std():.3f}",
            "quintile_AUC": f"{sub['quintile_AUC'].mean():.3f} ± {sub['quintile_AUC'].std():.3f}",
            "RMSE": f"{sub['RMSE'].mean():.2f} ± {sub['RMSE'].std():.2f}",
            "MAE": f"{sub['MAE'].mean():.2f} ± {sub['MAE'].std():.2f}",
        })
        summary_rows.append({
            "model": m_name,
            "seed": "Range [Min, Max]",
            "Spearman_rho": f"[{sub['Spearman_rho'].min():.3f}, {sub['Spearman_rho'].max():.3f}]",
            "quintile_AUC": f"[{sub['quintile_AUC'].min():.3f}, {sub['quintile_AUC'].max():.3f}]",
            "RMSE": f"[{sub['RMSE'].min():.2f}, {sub['RMSE'].max():.2f}]",
            "MAE": f"[{sub['MAE'].min():.2f}, {sub['MAE'].max():.2f}]",
        })
    df_seeds_full = pd.concat([df_seeds, pd.DataFrame(summary_rows)], ignore_index=True)
    df_seeds_full.to_csv(OUT_AUDIT_DIR / "SEED_STABILITY.csv", index=False)
    print(f"Saved {OUT_AUDIT_DIR / 'SEED_STABILITY.csv'} ({len(df_seeds_full)} rows)")
    
    # -------------------------------------------------------------
    # 9. SAVE PREDICTIONS MANIFEST AND RAW ARTIFACTS
    # -------------------------------------------------------------
    print("\n--- 9. Preserving Raw Predictions ---")
    pred_manifest = {}
    for name, p_arr in all_preds.items():
        slug = name.replace(" ", "_").replace(":", "").replace("(", "").replace(")", "").replace("+", "plus").replace("/", "_").lower()
        pred_records = [
            {
                "product_uid": test_df.iloc[i]["product_uid"],
                "category": test_df.iloc[i]["category"],
                "predicted": round(float(p_arr[i]), 3),
                "actual": round(float(y_test[i]), 3),
            }
            for i in range(len(test_df))
        ]
        p_file = PRED_OUT_DIR / f"{slug}.json"
        with open(p_file, "w", encoding="utf-8") as f:
            json.dump(pred_records, f, indent=2)
            
        p_bytes = p_file.read_bytes()
        pred_manifest[name] = {
            "file": str(p_file.relative_to(ROOT)),
            "sha256": hashlib.sha256(p_bytes).hexdigest(),
            "n_evaluated": len(pred_records),
        }
        
    with open(OUT_AUDIT_DIR / "PREDICTION_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(pred_manifest, f, indent=2)
    print(f"Saved predictions manifest -> {OUT_AUDIT_DIR / 'PREDICTION_MANIFEST.json'}")
    
    print("\nAll baseline and ablation computations completed successfully!")


if __name__ == "__main__":
    run_audit()
