"""Clean 5-Fold Out-Of-Fold (OOF) Benchmark of Six Downstream Learners.
Strictly on the 507 Training Products under the Current Feature Representation.
ZERO Temporal Test Leakage.
"""

import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor

ROOT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
import sys
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "Capstone updated" / "Capstone"))
from Legitimate.run_candidate_experiments import prepare_datasets

def main():
    print("Loading current training dataset (n=507)...")
    df_train, _ = prepare_datasets()
    assert len(df_train) == 507, f"Expected 507 training items, got {len(df_train)}"

    with open(ROOT_DIR / "Legitimate" / "08_FINAL_MODEL" / "feature_manifest.json", "r", encoding="utf-8") as f:
        feature_cols = json.load(f)

    y = df_train["success_score"].to_numpy(dtype=float)
    X = df_train[feature_cols].copy()

    # Preprocessing pipelines for tabular learners
    cat_cols = ["category"]
    num_cols = [c for c in feature_cols if c != "category"]

    # K-Fold split
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    learners = {
        "XGBoost": {
            "type": "xgb",
        },
        "Gradient Boosting": {
            "type": "sklearn",
            "model": GradientBoostingRegressor(
                n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42
            )
        },
        "Random Forest": {
            "type": "sklearn",
            "model": RandomForestRegressor(
                n_estimators=100, max_depth=6, random_state=42, n_jobs=-1
            )
        },
        "Ridge Regression": {
            "type": "sklearn",
            "model": Ridge(alpha=10.0, random_state=42)
        },
        "Support Vector Regressor (SVR)": {
            "type": "sklearn",
            "model": SVR(C=10.0, epsilon=1.0)
        },
        "Multi-Layer Perceptron (MLP)": {
            "type": "sklearn",
            "model": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
        }
    }

    results = {}

    for name, config in learners.items():
        print(f"Evaluating {name}...")
        oof_preds = np.zeros(len(df_train))
        fold_metrics = []
        train_times = []
        infer_times = []

        for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
            X_tr, y_tr = X.iloc[train_idx], y[train_idx]
            X_val, y_val = X.iloc[val_idx], y[val_idx]

            t0 = time.perf_counter()
            if config["type"] == "xgb":
                # XGBoost handles categorical natively
                monotone_priors = {
                    "price": -1, "brand_tier": 1,
                    "value_for_money": 1, "utility": 1, "ease_of_use": 1, "reliability": 1,
                    "design_appeal": 1, "after_sales": 1, "build_quality": 1, "durability": 1,
                    "repairability": 1,
                }
                model = xgb.XGBRegressor(
                    objective="reg:squarederror",
                    n_estimators=112,
                    learning_rate=0.05,
                    max_depth=5,
                    min_child_weight=3,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    enable_categorical=True,
                    tree_method="hist",
                    random_state=42 + fold,
                    monotone_constraints=monotone_priors,
                )
                model.fit(X_tr, y_tr)
                t1 = time.perf_counter()
                val_pred = model.predict(X_val)
                t2 = time.perf_counter()
            else:
                preprocessor = ColumnTransformer(
                    transformers=[
                        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), num_cols),
                        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
                    ]
                )
                pipeline = Pipeline([
                    ("pre", preprocessor),
                    ("reg", config["model"])
                ])
                pipeline.fit(X_tr, y_tr)
                t1 = time.perf_counter()
                val_pred = pipeline.predict(X_val)
                t2 = time.perf_counter()

            train_times.append(t1 - t0)
            infer_times.append((t2 - t1) / len(val_idx) * 1000) # ms per sample
            oof_preds[val_idx] = val_pred

            f_rho, _ = stats.spearmanr(val_pred, y_val)
            f_rmse = float(np.sqrt(mean_squared_error(y_val, val_pred)))
            f_mae = float(mean_absolute_error(y_val, val_pred))
            f_r2 = float(r2_score(y_val, val_pred))
            fold_metrics.append({
                "fold": fold + 1,
                "spearman_rho": float(f_rho),
                "rmse": float(f_rmse),
                "mae": float(f_mae),
                "r2": float(f_r2)
            })

        # Overall pooled OOF metrics
        pooled_rho, pooled_p = stats.spearmanr(oof_preds, y)
        pooled_r, _ = stats.pearsonr(oof_preds, y)
        pooled_rmse = float(np.sqrt(mean_squared_error(y, oof_preds)))
        pooled_mae = float(mean_absolute_error(y, oof_preds))
        pooled_r2 = float(r2_score(y, oof_preds))

        results[name] = {
            "pooled_oof_spearman_rho": round(float(pooled_rho), 4),
            "pooled_oof_spearman_p": float(pooled_p),
            "pooled_oof_pearson_r": round(float(pooled_r), 4),
            "pooled_oof_rmse": round(float(pooled_rmse), 2),
            "pooled_oof_mae": round(float(pooled_mae), 2),
            "pooled_oof_r2": round(float(pooled_r2), 4),
            "mean_fold_rho": round(float(np.mean([m["spearman_rho"] for m in fold_metrics])), 4),
            "std_fold_rho": round(float(np.std([m["spearman_rho"] for m in fold_metrics])), 4),
            "mean_train_time_sec": round(float(np.mean(train_times)), 4),
            "mean_infer_latency_ms_per_item": round(float(np.mean(infer_times)), 4),
            "fold_metrics": fold_metrics
        }
        print(f" -> {name}: OOF rho={pooled_rho:.4f}, RMSE={pooled_rmse:.2f}, MAE={pooled_mae:.2f}, R2={pooled_r2:.4f}")

    # Save to JSON
    out_json = ROOT_DIR / "FINAL_AUDIT" / "CURRENT_OOF_RESULTS.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved OOF benchmark results to {out_json}")

if __name__ == "__main__":
    main()
