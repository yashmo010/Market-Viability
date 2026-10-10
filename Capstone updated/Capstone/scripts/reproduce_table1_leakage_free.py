"""Leakage-free 5-fold cross-validation benchmarking of six ML algorithms on the
physical-product success prediction task (reproducing Table 1).

Methodology fixes:
1. Inner-split early stopping for XGBoost (85% inner train, 15% inner val on each training fold)
   so the outer validation fold is completely untouched until final scoring.
2. Classification decision threshold is computed on the TRAINING fold only:
   thresh = np.median(y_train)
3. Top and bottom quintile boundaries are derived from the TRAINING fold:
   q20_tr, q80_tr = np.percentile(y_train, [20, 80])
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, matthews_corrcoef,
    mean_absolute_error, mean_squared_error, precision_score, r2_score,
    recall_score, roc_auc_score
)
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
N_FOLDS = 5

def main():
    df = pd.read_parquet(ROOT / "data/extracted/features_physical.parquet")
    manifest = json.loads((ROOT / "models/xgb_physical_features.json").read_text(encoding="utf-8"))
    meta_cols = {"price", "avg_rating", "rating_count_log", "review_velocity", "category"}
    aspect_cols = [c for c in manifest if c not in meta_cols]
    
    X = np.nan_to_num(df[aspect_cols].values.astype(float), nan=0.0)
    y = df["success_score"].values
    
    models = {
        "XGBoost": None,  # handled with inner-split early stopping
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=600, max_depth=5, learning_rate=0.05,
            min_samples_leaf=3, subsample=0.8, random_state=SEED
        ),
        "MLP Regressor": MLPRegressor(
            hidden_layer_sizes=(128, 64), max_iter=500,
            learning_rate_init=0.001, early_stopping=True, random_state=SEED
        ),
        "Random Forest": RandomForestRegressor(
            n_estimators=600, max_depth=10, min_samples_leaf=3,
            random_state=SEED, n_jobs=-1
        ),
        "Ridge Regression": Ridge(alpha=1.0, random_state=SEED),
        "SVR (RBF)": SVR(kernel="rbf", C=10, epsilon=0.1),
    }
    
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    results = {}
    
    for name, model_template in models.items():
        print(f"Running {name}...")
        fold_metrics = {k: [] for k in ["r2", "rmse", "mae", "acc", "prec", "rec", "spec", "f1", "auc", "mcc"]}
        
        for fold_i, (tr, va) in enumerate(kf.split(X)):
            X_tr, y_tr = X[tr], y[tr]
            X_va, y_va = X[va], y[va]
            
            if name == "XGBoost":
                rng = np.random.RandomState(SEED)
                perm = rng.permutation(len(tr))
                k = int(len(perm) * 0.85)
                itr, iva = perm[:k], perm[k:]
                m_inner = xgb.XGBRegressor(
                    n_estimators=600, max_depth=5, learning_rate=0.05,
                    min_child_weight=3, subsample=0.8, colsample_bytree=0.8,
                    tree_method="hist", random_state=SEED, early_stopping_rounds=50
                )
                m_inner.fit(X_tr[itr], y_tr[itr], eval_set=[(X_tr[iva], y_tr[iva])], verbose=False)
                best_iter = m_inner.best_iteration + 1
                model = xgb.XGBRegressor(
                    n_estimators=best_iter, max_depth=5, learning_rate=0.05,
                    min_child_weight=3, subsample=0.8, colsample_bytree=0.8,
                    tree_method="hist", random_state=SEED
                )
                model.fit(X_tr, y_tr, verbose=False)
            else:
                model = clone(model_template)
                model.fit(X_tr, y_tr)
                
            preds = model.predict(X_va)
            fold_metrics["r2"].append(r2_score(y_va, preds))
            fold_metrics["rmse"].append(np.sqrt(mean_squared_error(y_va, preds)))
            fold_metrics["mae"].append(mean_absolute_error(y_va, preds))
            
            # Leakage-free classification thresholds from training fold
            thresh = float(np.median(y_tr))
            q20_tr, q80_tr = float(np.percentile(y_tr, 20)), float(np.percentile(y_tr, 80))
            
            mask = (y_va <= q20_tr) | (y_va >= q80_tr)
            labels = (y_va >= q80_tr).astype(int)
            pred_bin = (preds[mask] >= thresh).astype(int)
            lab_m = labels[mask]
            
            fold_metrics["acc"].append(accuracy_score(lab_m, pred_bin))
            fold_metrics["prec"].append(precision_score(lab_m, pred_bin, zero_division=0))
            fold_metrics["rec"].append(recall_score(lab_m, pred_bin, zero_division=0))
            fold_metrics["f1"].append(f1_score(lab_m, pred_bin, zero_division=0))
            fold_metrics["mcc"].append(matthews_corrcoef(lab_m, pred_bin))
            
            cm = confusion_matrix(lab_m, pred_bin, labels=[0, 1])
            tn, fp = cm[0, 0], cm[0, 1]
            fold_metrics["spec"].append(tn / (tn + fp) if (tn + fp) > 0 else 0.0)
            try:
                fold_metrics["auc"].append(roc_auc_score(lab_m, preds[mask]))
            except ValueError:
                fold_metrics["auc"].append(0.5)
                
        results[name] = {k: float(np.mean(v)) for k, v in fold_metrics.items()}
        results[name]["r2_std"] = float(np.std(fold_metrics["r2"]))
        
    print("\n" + "=" * 80)
    print("LEAKAGE-FREE TABLE 1 RESULTS:")
    print("=" * 80)
    header = f"{'Algorithm':<18} | {'R2':<6} | {'RMSE':<5} | {'Acc':<5} | {'Prec':<5} | {'Rec':<5} | {'Spec':<5} | {'F1':<5} | {'AUC':<5} | {'MCC':<5}"
    print(header)
    print("-" * len(header))
    for name, r in results.items():
        row = f"{name:<18} | {r['r2']:.3f}  | {r['rmse']:.1f}  | {r['acc']:.3f} | {r['prec']:.3f} | {r['rec']:.3f} | {r['spec']:.3f} | {r['f1']:.3f} | {r['auc']:.3f} | {r['mcc']:.3f}"
        print(row)
        
    out_path = ROOT / "models/benchmarks/table1_leakage_free.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    main()
