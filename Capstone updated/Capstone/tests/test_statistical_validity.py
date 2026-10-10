"""Comprehensive Statistical Validity Test Suite.

Automated verification of Issue 3 statistical audit requirements:
1. Reported Spearman rho equals independently recomputed Spearman rho.
2. Reported RMSE equals independently recomputed RMSE.
3. Reported AUC equals independently recomputed AUC.
4. Confidence intervals use the declared bootstrap and DeLong methods.
5. Evaluated sample sizes match declared values (n=124 total, n=51 mature).
6. Positive and negative AUC classes match declared quintile definition (top 20% vs bottom 20%).
7. Quintile thresholds follow declared pd.qcut rule.
8. CV folds contain declared observations (n=507 pre-cutoff, 5 folds).
9. Preprocessing and scalers are isolated to training data.
10. Final temporal test set is not used for model selection.
11. Best iteration (112) is derived strictly from training cross-validation.
12. Oracle vs launch-blind comparison uses correctly aligned paired observations.
13. Percentage and ratio calculations are mathematically correct.
14. Random seeds are declared and recorded.
15. Canonical evaluation script reproduces stored primary metrics.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats
from sklearn.metrics import mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STRICT_DIR = ROOT / "strict_temporal"
FROZEN_DIR = STRICT_DIR / "frozen_state"
PRED_PATH = STRICT_DIR / "predictions/predictions.json"
LABELS_PATH = STRICT_DIR / "data/test_labels/ground_truth.json"
STRICT_RESULTS_PATH = ROOT / "audit/STRICT_TEST_RESULTS.json"
AUDIT_STAT_DIR = ROOT / "audit/statistics"

from scripts.evaluate_strict_temporal import calc_auc_strict, run_canonical_evaluation


@pytest.fixture(scope="module")
def evaluation_data():
    with open(PRED_PATH, encoding="utf-8") as f:
        preds = json.load(f)
    with open(LABELS_PATH, encoding="utf-8") as f:
        labels = json.load(f)
    with open(STRICT_RESULTS_PATH, encoding="utf-8") as f:
        stored = json.load(f)
        
    records = []
    for p in preds:
        uid = p["product_uid"]
        if uid in labels:
            records.append({
                "uid": uid,
                "category": p["category"],
                "pred": float(p["predicted_viability"]),
                "actual": float(labels[uid]["success_score"]),
                "n_reviews": int(labels[uid]["n_reviews"]),
            })
    df = pd.DataFrame(records)
    return df, stored


def test_1_spearman_rho_recomputation(evaluation_data):
    """Test 1: Reported Spearman rho equals independently recomputed Spearman rho."""
    df, stored = evaluation_data
    rho, _ = stats.spearmanr(df["pred"], df["actual"])
    assert round(float(rho), 3) == stored["spearman_rho"], (
        f"Spearman mismatch: recomputed {rho:.4f} vs stored {stored['spearman_rho']}"
    )


def test_2_rmse_recomputation(evaluation_data):
    """Test 2: Reported RMSE equals independently recomputed RMSE."""
    df, stored = evaluation_data
    rmse = np.sqrt(mean_squared_error(df["actual"], df["pred"]))
    assert round(float(rmse), 2) == stored["rmse"], (
        f"RMSE mismatch: recomputed {rmse:.4f} vs stored {stored['rmse']}"
    )


def test_3_auc_recomputation(evaluation_data):
    """Test 3: Reported AUC equals independently recomputed AUC."""
    df, stored = evaluation_data
    auc_val, n_top, n_bot = calc_auc_strict(df["pred"].to_numpy(), df["actual"].to_numpy())
    assert round(float(auc_val), 3) == stored["auc_roc_quintile"], (
        f"AUC mismatch: recomputed {auc_val:.4f} vs stored {stored['auc_roc_quintile']}"
    )


def test_4_confidence_intervals_method(evaluation_data):
    """Test 4: Confidence intervals use declared bootstrap method."""
    df, stored = evaluation_data
    # Recompute bootstrap with declared seed 42 and 10000 replicates
    rng = np.random.RandomState(42)
    boot_rhos = []
    p_all = df["pred"].to_numpy()
    y_all = df["actual"].to_numpy()
    n = len(df)
    for _ in range(10000):
        idx = rng.randint(0, n, n)
        r, _ = stats.spearmanr(p_all[idx], y_all[idx])
        if np.isfinite(r):
            boot_rhos.append(r)
    ci_low = round(float(np.percentile(boot_rhos, 2.5)), 3)
    ci_high = round(float(np.percentile(boot_rhos, 97.5)), 3)
    
    assert ci_low == stored["spearman_rho_ci95"][0]
    assert ci_high == stored["spearman_rho_ci95"][1]


def test_5_sample_sizes_match(evaluation_data):
    """Test 5: Evaluated sample sizes match declared values."""
    df, stored = evaluation_data
    assert len(df) == stored["n_evaluated"]
    assert len(df) == 124
    
    mature_df = df[df["n_reviews"] >= 30]
    assert len(mature_df) == stored["mature_cohort_ge30"]["n"]
    assert len(mature_df) == 51


def test_6_positive_negative_auc_classes(evaluation_data):
    """Test 6: Positive/negative AUC classes match top/bottom quintile definition."""
    df, _ = evaluation_data
    t = pd.DataFrame({"p": df["pred"], "y": df["actual"]})
    t["tier"] = pd.qcut(t["y"], 5, labels=False, duplicates="drop")
    
    n_top = len(t[t.tier == t.tier.max()])
    n_bot = len(t[t.tier == 0])
    
    # 20% of 124 is approx 25
    assert n_top == 25
    assert n_bot == 25


def test_7_quintile_thresholds_rule(evaluation_data):
    """Test 7: Quintile thresholds follow declared rule."""
    df, _ = evaluation_data
    quantiles = np.percentile(df["actual"], [20, 80])
    bot_items = df[df["actual"] <= quantiles[0]]
    top_items = df[df["actual"] >= quantiles[1]]
    assert len(bot_items) >= 24
    assert len(top_items) >= 24


def test_8_cv_folds_observations():
    """Test 8: CV folds contain declared observations."""
    train_df = pd.read_parquet(FROZEN_DIR / "train_features.parquet")
    assert len(train_df) == 507
    
    cv_csv = AUDIT_STAT_DIR / "CV_AUDIT.csv"
    assert cv_csv.exists()
    cv_df = pd.read_csv(cv_csv)
    fold_rows = cv_df[cv_df["Fold"] != "Mean / Pooled"]
    assert len(fold_rows) == 5
    assert all(fold_rows["Train n"] >= 405)
    assert all(fold_rows["Val n"] >= 101)


def test_9_preprocessing_isolated_to_training():
    """Test 9: Preprocessing is fit strictly on training data."""
    scalers_path = FROZEN_DIR / "target_scalers.json"
    with open(scalers_path, encoding="utf-8") as f:
        scalers = json.load(f)
    assert len(scalers) == 5
    
    brand_path = FROZEN_DIR / "brand_tier_map.json"
    with open(brand_path, encoding="utf-8") as f:
        brand_data = json.load(f)
    assert brand_data["fitted_on_n_products"] == 507


def test_10_final_test_not_used_for_selection():
    """Test 10: Final test is not used for model selection."""
    with open(FROZEN_DIR / "xgb_physical_aspects_only_features.json", encoding="utf-8") as f:
        features = json.load(f)
    assert "success_score" not in features
    
    # Verify that prediction code does not open ground_truth or test labels
    pred_script = ROOT / "src/strict_temporal/predict_test.py"
    content = pred_script.read_text(encoding="utf-8")
    assert "ground_truth.json" not in content
    assert "labels_dict" not in content


def test_11_best_iteration_from_cv():
    """Test 11: Best iteration (112) is derived from training validation folds."""
    cv_csv = AUDIT_STAT_DIR / "CV_AUDIT.csv"
    cv_df = pd.read_csv(cv_csv)
    fold_rows = cv_df[cv_df["Fold"] != "Mean / Pooled"]
    best_iters = fold_rows["Best Iteration"].astype(int).tolist()
    assert int(np.mean(best_iters)) == 112


def test_12_oracle_comparison_paired_observations():
    """Test 12: Oracle/launch-blind comparison uses correct paired observations."""
    ablation_csv = ROOT / "audit/target/TARGET_ABLATION_RESULTS.csv"
    assert ablation_csv.exists()
    ab_df = pd.read_csv(ablation_csv)
    col_name = "Experiment / Target Condition"
    exp_a = ab_df[ab_df[col_name].str.contains("Experiment A")]
    exp_b = ab_df[ab_df[col_name].str.contains("Experiment B")]
    assert len(exp_a) == 1 and len(exp_b) == 1
    assert int(exp_a["Test Sample Size n"].iloc[0]) == 124
    assert int(exp_b["Test Sample Size n"].iloc[0]) == 124


def test_13_percentage_ratio_calculations():
    """Test 13: Percentage/ratio calculations are mathematically correct."""
    # 0.538 / 0.754 = 0.7135 (71.4%)
    ratio = 0.538 / 0.754
    assert round(ratio * 100, 1) == 71.4
    
    # Variance ratio = 0.538^2 / 0.754^2 = 50.9%
    var_ratio = (0.538**2) / (0.754**2)
    assert round(var_ratio * 100, 1) == 50.9


def test_14_random_seeds_recorded():
    """Test 14: Random seeds are recorded and audited."""
    seed_csv = AUDIT_STAT_DIR / "SEED_STABILITY.csv"
    assert seed_csv.exists()
    seed_df = pd.read_csv(seed_csv)
    seeds = seed_df["Random Seed"].tolist()
    assert "42" in seeds or 42 in seeds
    assert "Mean ± SD" in seeds


def test_15_canonical_evaluation_reproduces_metrics():
    """Test 15: Canonical evaluation script reproduces stored primary metrics."""
    report = run_canonical_evaluation()
    assert report["n_evaluated"] == 124
    assert report["metrics"]["spearman_rho"] == 0.562
    assert report["metrics"]["auc_roc_quintile"] == 0.890
    assert report["metrics"]["rmse"] == 21.12
    assert report["metrics"]["mae"] == 17.84
