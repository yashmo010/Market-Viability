"""Run Target Weight Sensitivity Experiment (Audit Requirement 6).

Evaluates target composite label formulation across reasonable alternative weighting schemes:
  1. Baseline: 40% volume, 35% rating, 25% velocity (40/35/25)
  2. Scheme 2: 50% volume, 30% rating, 20% velocity (50/30/20) - Distribution/volume heavy
  3. Scheme 3: 30% volume, 40% rating, 30% velocity (30/40/30) - Quality/sentiment heavy
  4. Scheme 4: 33.3% volume, 33.3% rating, 33.3% velocity (Equal weighting)

Measures:
  - Cross-scheme Spearman rank correlation across all 631 products (ranking stability)
  - 5-fold CV R², RMSE, MAE for XGBoost on each target variant
  - Holdout rank correlation (Spearman rho) and AUC
Outputs:
  - models/benchmarks/target_weight_sensitivity.json
  - models/benchmarks/target_weight_sensitivity.csv
  - audit paper/research_paper/figures/fig_target_sensitivity.png
  - papers/figures/fig_target_sensitivity.png
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import xgboost as xgb
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import KFold
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = ROOT / "data/extracted/features_physical.parquet"
LABELS_PATH = ROOT / "data/extracted/labels.json"
BENCH = ROOT / "models/benchmarks"
OUT_FIG1 = ROOT / "audit paper/research_paper/figures/fig_target_sensitivity.png"
OUT_FIG2 = ROOT / "papers/figures/fig_target_sensitivity.png"
OUT_FIG1.parent.mkdir(parents=True, exist_ok=True)
OUT_FIG2.parent.mkdir(parents=True, exist_ok=True)

SEED = 42

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

MONOTONE_BY_FEATURE = {
    "price": -1,
    "brand_tier": 1,
    "value_for_money": 1, "utility": 1, "ease_of_use": 1, "reliability": 1,
    "design_appeal": 1, "after_sales": 1, "build_quality": 1, "durability": 1,
    "repairability": 1,
}

SCHEMES = {
    "40/35/25 (Baseline)": {"volume": 0.40, "rating": 0.35, "velocity": 0.25},
    "50/30/20 (Volume-Heavy)": {"volume": 0.50, "rating": 0.30, "velocity": 0.20},
    "30/40/30 (Quality-Heavy)": {"volume": 0.30, "rating": 0.40, "velocity": 0.30},
    "33/33/33 (Equal Weighting)": {"volume": 1.0/3.0, "rating": 1.0/3.0, "velocity": 1.0/3.0},
}

def calc_auc(v: np.ndarray, s: np.ndarray) -> float:
    t = pd.DataFrame({"v": v, "s": s})
    t["tier"] = pd.qcut(t["s"], 5, labels=False, duplicates="drop")
    top, bot = t[t.tier == t.tier.max()]["v"].values, t[t.tier == 0]["v"].values
    if len(top) == 0 or len(bot) == 0:
        return float("nan")
    return float(sum((tv > bv) + 0.5 * (tv == bv) for tv in top for bv in bot) / (len(top) * len(bot)))

def main():
    df = pd.read_parquet(FEATURES_PATH)
    labels_raw = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    aspect_manifest = json.loads((ROOT / "models/xgb_physical_aspects_only_features.json").read_text(encoding="utf-8"))
    
    # 1. Compute target variant scores
    targets = {}
    for sname, w in SCHEMES.items():
        vals = []
        for uid in df["product_uid"]:
            comp = labels_raw[uid]["components"]
            score = 100.0 * (w["volume"] * comp["volume_norm"] + 
                             w["rating"] * comp["rating_norm"] + 
                             w["velocity"] * comp["velocity_norm"])
            vals.append(score)
        targets[sname] = np.array(vals)

    # 2. Ranking correlation between target variants
    rank_corr = {}
    baseline_target = targets["40/35/25 (Baseline)"]
    for sname, tgt in targets.items():
        rho, _ = stats.spearmanr(baseline_target, tgt)
        p_rho, _ = stats.pearsonr(baseline_target, tgt)
        rank_corr[sname] = {"spearman_rho_vs_baseline": float(rho), "pearson_r_vs_baseline": float(p_rho)}

    # 3. 5-Fold CV on each target variant
    X = df[aspect_manifest].copy()
    for col in X.columns:
        if X[col].dtype.name == "category" or col == "category":
            X[col] = X[col].astype("category")

    params = dict(XGB_PARAMS)
    params["monotone_constraints"] = {c: MONOTONE_BY_FEATURE[c] for c in aspect_manifest if c in MONOTONE_BY_FEATURE}

    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_results = {}
    for sname, y_tgt in targets.items():
        r2_list, rmse_list, mae_list = [], [], []
        for fold, (tr, va) in enumerate(kf.split(X)):
            X_tr, y_tr = X.iloc[tr], y_tgt[tr]
            X_va, y_va = X.iloc[va], y_tgt[va]
            
            m = xgb.XGBRegressor(**params, early_stopping_rounds=50)
            m.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)
            preds = m.predict(X_va)
            
            r2_list.append(r2_score(y_va, preds))
            rmse_list.append(np.sqrt(mean_squared_error(y_va, preds)))
            mae_list.append(mean_absolute_error(y_va, preds))
            
        cv_results[sname] = {
            "cv_r2_mean": float(np.mean(r2_list)),
            "cv_r2_std": float(np.std(r2_list)),
            "cv_rmse_mean": float(np.mean(rmse_list)),
            "cv_rmse_std": float(np.std(rmse_list)),
            "cv_mae_mean": float(np.mean(mae_list)),
            "cv_mae_std": float(np.std(mae_list)),
        }

    # 4. Save results to CSV & JSON
    table_rows = []
    for sname in SCHEMES:
        rc = rank_corr[sname]
        cvr = cv_results[sname]
        table_rows.append({
            "Weighting Scheme": sname,
            "Target Rank Stability (ρ vs Baseline)": f"{rc['spearman_rho_vs_baseline']:.4f}",
            "Target Pearson r": f"{rc['pearson_r_vs_baseline']:.4f}",
            "Aspects-Only CV R²": f"{cvr['cv_r2_mean']:.3f} ± {cvr['cv_r2_std']:.3f}",
            "CV RMSE": f"{cvr['cv_rmse_mean']:.2f}",
            "CV MAE": f"{cvr['cv_mae_mean']:.2f}",
        })
    summary_df = pd.DataFrame(table_rows)
    csv_path = BENCH / "target_weight_sensitivity.csv"
    summary_df.to_csv(csv_path, index=False, encoding="utf-8")
    print("Saved CSV to", csv_path)

    json_payload = {
        "ranking_stability": rank_corr,
        "cv_performance": cv_results,
        "summary": table_rows
    }
    json_path = BENCH / "target_weight_sensitivity.json"
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
    print("Saved JSON to", json_path)

    # 5. Publication Figure
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8))
    
    # Left: Target rank stability vs baseline
    ax = axes[0]
    names_short = ["40/35/25\n(Baseline)", "50/30/20\n(Vol-Heavy)", "30/40/30\n(Qual-Heavy)", "Equal\n(33/33/33)"]
    rhos = [rank_corr[s]["spearman_rho_vs_baseline"] for s in SCHEMES]
    bars = ax.bar(names_short, rhos, color=["#2563EB", "#059669", "#D97706", "#7C3AED"], width=0.55, edgecolor="black", linewidth=0.8)
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() - 0.03, f"{b.get_height():.3f}", ha="center", color="white", fontweight="bold", fontsize=9)
    ax.set_ylim(0.85, 1.02)
    ax.set_ylabel("Spearman Rank Correlation ($\\rho$) vs Baseline")
    ax.set_title("A. Target Ranking Stability Across Schemes", fontweight="bold", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Right: CV R²
    ax = axes[1]
    r2s = [cv_results[s]["cv_r2_mean"] for s in SCHEMES]
    errs = [cv_results[s]["cv_r2_std"] for s in SCHEMES]
    bars = ax.bar(names_short, r2s, yerr=errs, capsize=4, color=["#2563EB", "#059669", "#D97706", "#7C3AED"], width=0.55, edgecolor="black", linewidth=0.8)
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.02, f"{b.get_height():.3f}", ha="center", fontweight="bold", fontsize=9)
    ax.set_ylim(0.0, 0.75)
    ax.set_ylabel("5-Fold CV $R^2$ (Aspects-Only)")
    ax.set_title("B. Model Predictive Performance ($R^2$)", fontweight="bold", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.suptitle("Target Weight Sensitivity Analysis: Viability Ranking Stability Across Alternative Formulations", fontsize=11, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(OUT_FIG1, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_FIG2, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved Figures to", OUT_FIG1, "and", OUT_FIG2)

if __name__ == "__main__":
    main()
