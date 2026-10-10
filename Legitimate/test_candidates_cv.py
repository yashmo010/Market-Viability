"""Pre-registered candidate evaluation on training data (5-fold CV).
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy import stats
import xgboost as xgb

ROOT_PROJECT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Capstone updated\Capstone")
TRAIN_PARQUET = ROOT_PROJECT / "strict_temporal/frozen_state/train_features.parquet"
TRAIN_PRODUCTS = ROOT_PROJECT / "strict_temporal/data/train/products.json"

import sys
sys.path.insert(0, str(Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)").resolve()))
from Legitimate.test_extraction_logic import parse_technical_specs

SEED = 42

def load_data():
    df_train = pd.read_parquet(TRAIN_PARQUET)
    train_products = json.load(open(TRAIN_PRODUCTS, encoding="utf-8"))
    prod_map = {p["product_uid"]: p for p in train_products}

    # Extract technical specs for all train products
    spec_rows = []
    for uid in df_train["product_uid"]:
        p = prod_map[uid]
        specs = p.get("specs", {}).get("features", [])
        parsed = parse_technical_specs(p.get("name", ""), specs)
        parsed["product_uid"] = uid
        spec_rows.append(parsed)

    df_specs = pd.DataFrame(spec_rows)
    df_merged = pd.merge(df_train, df_specs, on="product_uid")
    return df_merged

def run_cv_candidate(df: pd.DataFrame, feature_cols: list[str], monotone_dict: dict = None):
    X = df[feature_cols].copy()
    y = df["success_score"].to_numpy(dtype=float)

    params = dict(
        objective="reg:squarederror",
        n_estimators=112,
        learning_rate=0.05,
        max_depth=5,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        enable_categorical=True,
        tree_method="hist",
        random_state=SEED,
    )
    if monotone_dict:
        # Filter monotone_dict to features present in feature_cols
        active_monotone = {k: v for k, v in monotone_dict.items() if k in feature_cols}
        if active_monotone:
            params["monotone_constraints"] = active_monotone

    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    r2_list, rmse_list, mae_list, rho_list = [], [], [], []
    oof_preds = np.zeros(len(df))

    for tr_idx, va_idx in kf.split(X):
        m = xgb.XGBRegressor(**params)
        m.fit(X.iloc[tr_idx], y[tr_idx], verbose=False)
        p_val = m.predict(X.iloc[va_idx])
        oof_preds[va_idx] = p_val

        r2_list.append(r2_score(y[va_idx], p_val))
        rmse_list.append(np.sqrt(mean_squared_error(y[va_idx], p_val)))
        mae_list.append(mean_absolute_error(y[va_idx], p_val))
        r, _ = stats.spearmanr(p_val, y[va_idx])
        rho_list.append(r)

    overall_rho, p_val = stats.spearmanr(oof_preds, y)
    return {
        "cv_r2": float(np.mean(r2_list)),
        "cv_rmse": float(np.mean(rmse_list)),
        "cv_mae": float(np.mean(mae_list)),
        "cv_spearman_rho": float(overall_rho),
        "cv_spearman_p": float(p_val),
    }

def main():
    df = load_data()
    print(f"Loaded {len(df)} merged training rows.")

    aspect_cols = [
        "value_for_money", "utility", "ease_of_use", "reliability",
        "design_appeal", "after_sales", "build_quality", "durability", "repairability"
    ]
    mention_cols = [f"{a}_mention_rate" for a in aspect_cols]
    base_features = ["price"] + aspect_cols + mention_cols + ["brand_tier", "category"]

    tech_attrs = [
        "attr_battery_hrs", "attr_battery_mah", "attr_ip_level", "attr_bluetooth_ver",
        "attr_watts", "attr_ice_lbs", "attr_ice_mins", "attr_has_anc", "attr_has_mic",
        "attr_has_warranty", "attr_has_display", "attr_has_fast_charge"
    ]
    meta_attrs = ["attr_spec_bullets", "attr_word_count", "attr_number_density"]

    monotone_priors = {
        "price": -1,
        "brand_tier": 1,
        "value_for_money": 1, "utility": 1, "ease_of_use": 1, "reliability": 1,
        "design_appeal": 1, "after_sales": 1, "build_quality": 1, "durability": 1,
        "repairability": 1,
        "attr_battery_hrs": 1, "attr_battery_mah": 1, "attr_ip_level": 1, "attr_bluetooth_ver": 1,
        "attr_watts": 1, "attr_ice_lbs": 1, "attr_has_anc": 1, "attr_has_mic": 1,
        "attr_has_warranty": 1, "attr_has_display": 1, "attr_has_fast_charge": 1,
    }

    candidates = {
        "Candidate A (Baseline Model_O)": base_features,
        "Candidate B (Aspects + Spec Density)": base_features + meta_attrs,
        "Candidate C (Aspects + Tech Attributes)": base_features + tech_attrs,
        "Candidate D (Aspects + Tech + Density)": base_features + tech_attrs + meta_attrs,
        "Candidate E (Tech Attributes + Meta Alone)": ["price", "brand_tier", "category"] + tech_attrs + meta_attrs,
        "Candidate F (Aspects + Tech Attrs without Mentions)": ["price"] + aspect_cols + tech_attrs + ["brand_tier", "category"],
        "Candidate G (Full Hybrid Cold-Start Rich)": base_features + tech_attrs + meta_attrs,
    }

    results = {}
    for name, feats in candidates.items():
        res = run_cv_candidate(df, feats, monotone_priors)
        results[name] = res
        print(f"{name}: CV R^2 = {res['cv_r2']:.4f}, CV RMSE = {res['cv_rmse']:.2f}, CV Spearman rho = {res['cv_spearman_rho']:.4f}")

if __name__ == "__main__":
    main()
