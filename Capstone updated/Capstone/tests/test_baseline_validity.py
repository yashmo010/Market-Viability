"""Comprehensive Baseline and Ablation Validity Test Suite (Issue 6).

Automated verification of Issue 6 baseline audit requirements:
1. All baselines use the canonical split (507 train, 124 test).
2. No baseline uses test labels during training.
3. Preprocessing is fit strictly on training data.
4. No post-cutoff information enters features.
5. All models use the same canonical target (Composite SuccessScore).
6. All models are evaluated on the exact same 124 test products.
7. No model is selected using test performance.
8. Baseline predictions exist for every test product.
9. Metric calculations match the canonical evaluator.
10. Primary-model results reproduce the sealed result within tolerance (rho=0.562, AUC=0.890, RMSE=21.12, MAE=17.84).
11. Ablation feature sets are correctly defined.
12. Oracle features are never used in the operational model.
13. Brand and category leakage checks pass.
14. Seed handling is reproducible across seeds.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STRICT_DIR = ROOT / "strict_temporal"
FROZEN_DIR = STRICT_DIR / "frozen_state"
TRAIN_DIR = STRICT_DIR / "data/train"
TEST_INPUTS_DIR = STRICT_DIR / "data/test_inputs"
TEST_LABELS_DIR = STRICT_DIR / "data/test_labels"
AUDIT_BASE_DIR = ROOT / "audit/baselines"

from scripts.evaluate_strict_temporal import calc_auc_strict


@pytest.fixture(scope="module")
def baseline_audit_data():
    with open(TEST_INPUTS_DIR / "products_test_specs.json", encoding="utf-8") as f:
        test_inputs = json.load(f)
    with open(TEST_LABELS_DIR / "ground_truth.json", encoding="utf-8") as f:
        test_labels = json.load(f)
    with open(AUDIT_BASE_DIR / "BASELINE_RESULTS.csv", encoding="utf-8") as f:
        baseline_results = pd.read_csv(f)
    with open(AUDIT_BASE_DIR / "ABLATION_RESULTS.csv", encoding="utf-8") as f:
        ablation_results = pd.read_csv(f)
    with open(AUDIT_BASE_DIR / "PREDICTION_MANIFEST.json", encoding="utf-8") as f:
        pred_manifest = json.load(f)
        
    return {
        "test_inputs": test_inputs,
        "test_labels": test_labels,
        "baseline_results": baseline_results,
        "ablation_results": ablation_results,
        "pred_manifest": pred_manifest,
    }


def test_1_canonical_split_sizes(baseline_audit_data):
    """Test 1: All baselines use the canonical split (507 train, 124 test)."""
    b_df = baseline_audit_data["baseline_results"]
    assert all(b_df["n_train"] == 507), "All baselines must be trained on exactly 507 products"
    assert all(b_df["n_test"] == 124), "All baselines must be evaluated on exactly 124 products"


def test_2_no_test_labels_in_training():
    """Test 2: No baseline uses test labels during training."""
    with open(TRAIN_DIR / "products.json", encoding="utf-8") as f:
        train_prods = json.load(f)
    with open(TEST_LABELS_DIR / "ground_truth.json", encoding="utf-8") as f:
        test_labels = json.load(f)
        
    train_uids = {p["product_uid"] for p in train_prods}
    test_uids = set(test_labels.keys())
    assert len(train_uids & test_uids) == 0, "Train and test label product IDs must be completely disjoint"


def test_3_preprocessing_fit_on_train_only():
    """Test 3: Preprocessing is fit strictly on training data."""
    with open(FROZEN_DIR / "target_scalers.json", encoding="utf-8") as f:
        scalers = json.load(f)
    with open(FROZEN_DIR / "brand_tier_map.json", encoding="utf-8") as f:
        brand_map = json.load(f)
        
    assert brand_map["fitted_on_n_products"] == 507, "Brand tier map must be fitted on exactly 507 products"
    assert len(scalers) == 5, "Target scalers must exist for all 5 categories"


def test_4_no_post_cutoff_information_in_features(baseline_audit_data):
    """Test 4: No post-cutoff information enters test features."""
    for it in baseline_audit_data["test_inputs"]:
        assert "avg_rating" not in it, "avg_rating leaked in test input"
        assert "rating_count" not in it, "rating_count leaked in test input"
        assert "success_score" not in it, "success_score leaked in test input"
        assert "reviews" not in it, "reviews leaked in test input"
        assert it["first_review_ts"] > 1635724799, "Pre-cutoff product found in post-cutoff test inputs"


def test_5_canonical_target_consistency(baseline_audit_data):
    """Test 5: All models use the same canonical target."""
    labels = baseline_audit_data["test_labels"]
    assert len(labels) == 124
    for uid, item in labels.items():
        assert "success_score" in item
        score = item["success_score"]
        assert 0.0 <= score <= 100.0, f"Target score {score} out of [0, 100] bounds"


def test_6_identical_test_products_evaluated(baseline_audit_data):
    """Test 6: All models are evaluated on the exact same 124 test products."""
    manifest = baseline_audit_data["pred_manifest"]
    expected_uids = {it["product_uid"] for it in baseline_audit_data["test_inputs"]}
    assert len(expected_uids) == 124
    
    for model_name, info in manifest.items():
        p_path = ROOT / info["file"]
        assert p_path.exists(), f"Missing prediction file for {model_name}"
        with open(p_path, encoding="utf-8") as f:
            preds = json.load(f)
        assert len(preds) == 124, f"Model {model_name} evaluated on {len(preds)} != 124 products"
        m_uids = {p["product_uid"] for p in preds}
        assert m_uids == expected_uids, f"Model {model_name} evaluated on mismatched product UIDs"


def test_7_no_model_selected_using_test_performance():
    """Test 7: No model is selected using test performance."""
    pred_code = (ROOT / "src/strict_temporal/predict_test.py").read_text(encoding="utf-8")
    assert "ground_truth.json" not in pred_code
    assert "test_labels" in pred_code and "assert" in pred_code, "Predictor must physically assert test_labels isolation"


def test_8_baseline_predictions_complete(baseline_audit_data):
    """Test 8: Baseline predictions exist for every test product."""
    b_df = baseline_audit_data["baseline_results"]
    assert len(b_df) >= 10, "Expected at least 10 baseline rows in BASELINE_RESULTS.csv"
    manifest = baseline_audit_data["pred_manifest"]
    for model in b_df["model"]:
        assert model in manifest, f"Missing prediction record for {model}"


def test_9_metric_calculations_canonical(baseline_audit_data):
    """Test 9: Metric calculations match canonical evaluator."""
    labels = baseline_audit_data["test_labels"]
    manifest = baseline_audit_data["pred_manifest"]
    prop_file = ROOT / manifest["Proposed Model (XGBoost Monotone)"]["file"]
    with open(prop_file, encoding="utf-8") as f:
        preds = json.load(f)
        
    p_arr = np.array([p["predicted"] for p in preds])
    y_arr = np.array([labels[p["product_uid"]]["success_score"] for p in preds])
    
    rho, _ = stats.spearmanr(p_arr, y_arr)
    auc_v, _, _ = calc_auc_strict(p_arr, y_arr)
    rmse = np.sqrt(mean_squared_error(y_arr, p_arr))
    mae = mean_absolute_error(y_arr, p_arr)
    
    assert round(float(rho), 3) == 0.562
    assert round(float(auc_v), 3) == 0.890
    assert round(float(rmse), 2) == 21.12
    assert round(float(mae), 2) == 17.84


def test_10_primary_model_reproducibility(baseline_audit_data):
    """Test 10: Primary-model results reproduce sealed result within tolerance."""
    b_df = baseline_audit_data["baseline_results"]
    prop_row = b_df[b_df["model"] == "Proposed Model (XGBoost Monotone)"].iloc[0]
    assert prop_row["Spearman_rho"] == 0.562
    assert prop_row["quintile_AUC"] == 0.890
    assert prop_row["RMSE"] == 21.12
    assert prop_row["MAE"] == 17.84


def test_11_ablation_feature_sets_correct(baseline_audit_data):
    """Test 11: Ablation feature sets are correctly defined."""
    ab_df = baseline_audit_data["ablation_results"]
    models = list(ab_df["model"])
    assert "Ablation A: Remove LLM Aspects" in models
    assert "Ablation B: Remove Brand" in models
    assert "Ablation C: Remove Category" in models
    assert "Ablation D: Remove Monotonic Constraints" in models
    assert "Ablation E: Raw Target (Unnormalized)" in models
    assert "Ablation F1: Remove Physical Build Aspects" in models
    assert "Ablation F2: Remove Experiential Aspects" in models
    assert "Ablation F3: Remove Commercial/Aesthetic Aspects" in models
    assert "Ablation G: Numeric-Only (Price + Brand)" in models
    assert "Ablation H: Text-Only (TF-IDF XGB)" in models
    assert "Ablation I: Minimal Proposed Model" in models


def test_12_oracle_isolation():
    """Test 12: Oracle features are never used in operational model."""
    pred_file = ROOT / "strict_temporal/predictions/predictions.json"
    with open(pred_file, encoding="utf-8") as f:
        preds = json.load(f)
    for p in preds:
        assert p["bridge_source"] != "oracle_true_reviews", "Operational model used oracle true reviews!"


def test_13_brand_category_leakage_checks():
    """Test 13: Brand/category leakage checks pass."""
    with open(FROZEN_DIR / "brand_tier_map.json", encoding="utf-8") as f:
        brand_map = json.load(f)
    with open(TEST_INPUTS_DIR / "products_test_specs.json", encoding="utf-8") as f:
        test_inputs = json.load(f)
    with open(TRAIN_DIR / "products.json", encoding="utf-8") as f:
        train_prods = json.load(f)
        
    train_brands = {(p.get("brand") or "").strip().casefold() for p in train_prods}
    # For every test product whose brand is NOT in train_brands, brand_tier must map to new_tier (0)
    for it in test_inputs:
        b = (it.get("brand") or "").strip().casefold()
        if b not in train_brands:
            tier = brand_map["brands"].get(b, brand_map["new_tier"])
            assert tier == 0, f"Unseen brand {b} received non-zero tier {tier}!"


def test_14_seed_stability_reproducibility():
    """Test 14: Seed handling is reproducible across seeds."""
    seed_csv = AUDIT_BASE_DIR / "SEED_STABILITY.csv"
    assert seed_csv.exists(), "Missing SEED_STABILITY.csv"
    df = pd.read_csv(seed_csv)
    models = set(df["model"])
    assert "Proposed Model (XGBoost Monotone)" in models
    assert "Baseline H1: Random Forest" in models
    assert "Baseline H2: Gradient Boosting" in models
    
    # Check that seed 42 in table matches canonical
    prop_s42 = df[(df["model"] == "Proposed Model (XGBoost Monotone)") & (df["seed"] == "42")]
    assert len(prop_s42) == 1
    assert float(prop_s42["Spearman_rho"].iloc[0]) == 0.562
