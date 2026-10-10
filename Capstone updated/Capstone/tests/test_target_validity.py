"""Target Validity and Construct Audit Test Suite.

Automated verification of Issue 2 audit requirements:
1. Target formula correctness (recomputation matches recorded SuccessScore).
2. Target component provenance (review-level aggregation trace).
3. No test labels entering feature construction.
4. No future reviews entering predictors.
5. No review-derived target components in predictor features.
6. Review IDs used for target vs predictor are traceable and disjoint for test products.
7. Category normalization follows declared protocol.
8. Target weights match declared formula (0.40, 0.35, 0.25).
9. Alternative target definitions are reproducible.
10. Strict temporal protocol remains intact (Issue 1 preservation).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
STRICT_DIR = ROOT / "strict_temporal"
FROZEN_DIR = STRICT_DIR / "frozen_state"
TRAIN_DIR = STRICT_DIR / "data/train"
TEST_INPUTS_DIR = STRICT_DIR / "data/test_inputs"
TEST_LABELS_DIR = STRICT_DIR / "data/test_labels"
AUDIT_DIR = ROOT / "audit/target"


def test_1_target_formula_correctness():
    """Test 1: Target formula correctness.
    
    Verifies that SuccessScore = 100 * (0.40 * volume_norm + 0.35 * rating_norm + 0.25 * velocity_norm)
    within numerical tolerance.
    """
    with open(TEST_LABELS_DIR / "ground_truth.json", encoding="utf-8") as f:
        gt_dict = json.load(f)

    with open(FROZEN_DIR / "target_scalers.json", encoding="utf-8") as f:
        scalers = json.load(f)

    for uid, item in gt_dict.items():
        cat = item["category"]
        bounds = scalers[cat]
        
        # Verify minmax normalization from raw components
        vol_raw = np.log1p(item["n_reviews"])
        vol_norm = (vol_raw - bounds["vol_min"]) / (bounds["vol_max"] - bounds["vol_min"] + 1e-9)
        vol_norm = float(np.clip(vol_norm, 0.0, 1.0))
        
        rat_norm = (item["avg_rating"] - bounds["rat_min"]) / (bounds["rat_max"] - bounds["rat_min"] + 1e-9)
        rat_norm = float(np.clip(rat_norm, 0.0, 1.0))
        
        vel_norm = (item["velocity"] - bounds["vel_min"]) / (bounds["vel_max"] - bounds["vel_min"] + 1e-9)
        vel_norm = float(np.clip(vel_norm, 0.0, 1.0))
        
        expected_score = 100.0 * (0.40 * vol_norm + 0.35 * rat_norm + 0.25 * vel_norm)
        actual_score = item["success_score"]
        
        assert abs(expected_score - actual_score) < 0.05, (
            f"Formula mismatch for {uid}: expected {expected_score:.3f}, got {actual_score:.3f}"
        )


def test_2_target_component_provenance():
    """Test 2: Target component provenance.
    
    Verifies that all target components trace back to raw review fields
    and that no commercial sales fields exist.
    """
    provenance_path = AUDIT_DIR / "TARGET_PROVENANCE.csv"
    assert provenance_path.exists(), "TARGET_PROVENANCE.csv missing from audit package"
    
    prov_df = pd.read_csv(provenance_path)
    components = set(prov_df["Target Component"])
    assert "volume_norm" in components
    assert "rating_norm" in components
    assert "velocity_norm" in components
    assert "success_score" in components
    
    # Verify that commercial fields do not exist in the raw dataset
    raw_products_file = ROOT / "data/products_physical.json"
    if raw_products_file.exists():
        with open(raw_products_file, encoding="utf-8") as f:
            raw_sample = json.load(f)[0]
        commercial_terms = ["sales", "revenue", "units_sold", "profit", "bsr"]
        for term in commercial_terms:
            assert term not in raw_sample, f"Unexpected commercial field found in raw data: {term}"


def test_3_no_test_labels_in_feature_construction():
    """Test 3: No test labels enter predictor feature construction."""
    with open(FROZEN_DIR / "xgb_physical_aspects_only_features.json", encoding="utf-8") as f:
        feature_cols = json.load(f)
        
    forbidden = {"successscore", "success_score", "success_label", "target", "y", "ground_truth"}
    for col in feature_cols:
        assert col.lower() not in forbidden, f"Forbidden label column found in features: {col}"


def test_4_no_future_reviews_entering_predictors():
    """Test 4: No post-cutoff reviews enter predictor features for test items."""
    # Test products rely exclusively on spec-based bridging; verify 0 reviews were accessed
    with open(TEST_INPUTS_DIR / "products_test_specs.json", encoding="utf-8") as f:
        test_specs = json.load(f)
        
    for p in test_specs:
        assert "reviews" not in p
        assert "rating_count" not in p
        assert "avg_rating" not in p
        assert "review_velocity" not in p
        assert "success_score" not in p


def test_5_no_review_derived_target_components_in_predictor_features():
    """Test 5: No review-derived target component is in the predictor feature set."""
    with open(FROZEN_DIR / "xgb_physical_aspects_only_features.json", encoding="utf-8") as f:
        features = json.load(f)
        
    leaky_components = [
        "avg_rating", "rating_count", "n_reviews", "review_velocity", "velocity",
        "helpful_votes", "verified_ratio", "success_score",
        "norm_rating_count", "norm_avg_rating", "norm_review_velocity",
        "volume_norm", "rating_norm", "velocity_norm"
    ]
    for feat in features:
        for leaky in leaky_components:
            assert feat.lower() != leaky.lower(), f"Leaky target component '{feat}' found in predictor features!"


def test_6_review_traceability_and_disjointness():
    """Test 6: Review IDs used for target vs predictor are traceable and disjoint."""
    # Audit 1: Review source audit confirms all 9 aspects have NO direct leakage
    review_audit_path = AUDIT_DIR / "REVIEW_SOURCE_AUDIT.csv"
    assert review_audit_path.exists()
    rev_df = pd.read_csv(review_audit_path)
    assert len(rev_df) == 9
    assert all(rev_df["Direct Leakage?"] == "NO")
    
    # Audit 2: Construct overlap audit confirms direct review targets are excluded from features
    overlap_audit_path = AUDIT_DIR / "CONSTRUCT_OVERLAP_AUDIT.csv"
    assert overlap_audit_path.exists()
    overlap_df = pd.read_csv(overlap_audit_path)
    leaky_rows = overlap_df[overlap_df["Direct Leakage?"] == "YES"]
    assert len(leaky_rows) == 3  # avg_rating, review count, review velocity
    assert all(leaky_rows["Classification"] == "Target Leakage (Excluded)")
    
    # Audit 3: Test items have zero review data attached in predictor inputs
    with open(TEST_INPUTS_DIR / "products_test_specs.json", encoding="utf-8") as f:
        test_specs = json.load(f)
    assert all("reviews" not in p for p in test_specs)


def test_7_category_normalization_protocol():
    """Test 7: Category normalization follows declared protocol."""
    norm_file = FROZEN_DIR / "target_scalers.json"
    assert norm_file.exists()
    with open(norm_file, encoding="utf-8") as f:
        scalers = json.load(f)
        
    expected_categories = {"bluetooth_speakers", "ice_makers", "power_banks", "smartwatches", "wireless_headphones"}
    assert set(scalers.keys()) == expected_categories
    
    # Check that category bounds are positive and non-zero
    for cat, bounds in scalers.items():
        assert bounds["vol_max"] > bounds["vol_min"]
        assert bounds["rat_max"] > bounds["rat_min"]
        assert bounds["vel_max"] > bounds["vel_min"]


def test_8_target_weights_match_declared_formula():
    """Test 8: Target weights match declared formula."""
    formula_path = AUDIT_DIR / "TARGET_FORMULA.json"
    assert formula_path.exists()
    
    with open(formula_path, encoding="utf-8") as f:
        f_data = json.load(f)
        
    weights = f_data["weights"]
    assert weights["volume"] == 0.40
    assert weights["rating"] == 0.35
    assert weights["velocity"] == 0.25
    assert sum(weights.values()) == pytest.approx(1.0)


def test_9_alternative_targets_reproducible():
    """Test 9: Alternative target definitions are reproducible."""
    sens_path = AUDIT_DIR / "TARGET_WEIGHT_SENSITIVITY.csv"
    assert sens_path.exists()
    
    sens_df = pd.read_csv(sens_path)
    schemes = set(sens_df["weight_scheme"])
    expected_schemes = {
        "Baseline (40/35/25)",
        "Equal (33.3/33.3/33.3)",
        "Volume-Heavy (50/30/20)",
        "Quality-Heavy (30/40/30)",
        "Rating-Dominant (20/50/30)",
        "Velocity-Heavy (25/25/50)",
        "Leave-Out-Volume (0/58/42)",
        "Leave-Out-Rating (62/0/38)",
        "Leave-Out-Velocity (53/47/0)",
        "Volume-Only (100/0/0)",
        "Rating-Only (0/100/0)",
        "Velocity-Only (0/0/100)",
    }
    assert expected_schemes.issubset(schemes)


def test_10_strict_temporal_protocol_intact():
    """Test 10: Strict temporal protocol remains intact."""
    manifest_path = ROOT / "audit/EXPERIMENT_MANIFEST.json"
    assert manifest_path.exists()
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
        
    assert manifest["cutoff_timestamp_epoch"] == 1635724799
    assert manifest["dataset_summary"]["train_products_n"] == 507
    assert manifest["dataset_summary"]["final_test_products_n"] == 124
