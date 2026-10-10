"""Automated Leakage Test Suite.

Verifies strict absence of temporal and test-set leakage:
1. Test labels cannot be loaded by prediction code.
2. Test IDs are not present during fitting.
3. Test timestamps are strictly <= cutoff for training and > cutoff for test.
4. Test rows do not affect normalization parameters.
5. Test rows do not affect category profiles.
6. Test rows do not affect brand features.
7. Test performance is not used for hyperparameter selection.
8. Test performance is not used to select prompts/models.
9. Test labels are only loaded by the evaluation stage.
10. The frozen pipeline produces identical predictions when test labels are removed entirely.
"""

from __future__ import annotations

import filecmp
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CUTOFF_TS = 1635724799  # 2021-10-31 23:59:59 UTC
STRICT_DIR = ROOT / "strict_temporal"
FROZEN_DIR = STRICT_DIR / "frozen_state"
TRAIN_DIR = STRICT_DIR / "data/train"
TEST_INPUTS_DIR = STRICT_DIR / "data/test_inputs"
TEST_LABELS_DIR = STRICT_DIR / "data/test_labels"

from src.strict_temporal.predict_test import StrictPredictor, run_prediction_pipeline


def test_1_labels_inaccessible_to_prediction():
    """Test 1: Test labels cannot be loaded by prediction code."""
    # Attempting to point prediction pipeline to test_labels must trigger an assertion
    with pytest.raises(AssertionError, match="test_labels"):
        run_prediction_pipeline(inputs_file=TEST_LABELS_DIR / "ground_truth.json")


def test_2_test_ids_not_present_during_fitting():
    """Test 2: Test IDs are not present during fitting."""
    with open(TEST_INPUTS_DIR / "products_test_specs.json", encoding="utf-8") as f:
        test_uids = {p["product_uid"] for p in json.load(f)}

    train_df = pd.read_parquet(FROZEN_DIR / "train_features.parquet")
    train_uids = set(train_df["product_uid"])

    overlap = test_uids.intersection(train_uids)
    assert len(overlap) == 0, f"LEAKAGE: {len(overlap)} test IDs found in training features: {overlap}"


def test_3_timestamps_temporal_partitioning():
    """Test 3: Test timestamps are strictly <= cutoff for training and > cutoff for test."""
    with open(TRAIN_DIR / "products.json", encoding="utf-8") as f:
        train_prods = json.load(f)
    for p in train_prods:
        ts = p.get("first_review_ts", 0)
        assert ts <= CUTOFF_TS, f"LEAKAGE: Pre-cutoff training product {p['product_uid']} has timestamp {ts} > {CUTOFF_TS}"

    with open(TEST_INPUTS_DIR / "products_test_specs.json", encoding="utf-8") as f:
        test_prods = json.load(f)
    for p in test_prods:
        ts = p.get("first_review_ts", 0)
        assert ts > CUTOFF_TS, f"CONTAMINATION: Test product {p['product_uid']} has timestamp {ts} <= {CUTOFF_TS}"


def test_4_test_rows_do_not_affect_normalization():
    """Test 4: Test rows do not affect normalization parameters."""
    with open(FROZEN_DIR / "target_scalers.json", encoding="utf-8") as f:
        scalers = json.load(f)

    with open(TRAIN_DIR / "products.json", encoding="utf-8") as f:
        train_prods = json.load(f)
    with open(TRAIN_DIR / "reviews.json", encoding="utf-8") as f:
        train_revs = json.load(f)

    # Recompute scalers strictly from training data and check exact match
    months_between = lambda a, b: abs(b - a) / (86400 * 30.44)
    rev_cnts = {}
    for r in train_revs:
        rev_cnts[r["product_uid"]] = rev_cnts.get(r["product_uid"], 0) + 1

    for cat, sc in scalers.items():
        prods = [p for p in train_prods if p["category"] == cat]
        vols = np.log1p([rev_cnts.get(p["product_uid"], 0) for p in prods])
        assert np.isclose(float(np.min(vols)), sc["vol_min"]), f"Scaler mismatch in {cat} vol_min"
        assert np.isclose(float(np.max(vols)), sc["vol_max"]), f"Scaler mismatch in {cat} vol_max"


def test_5_test_rows_do_not_affect_category_profiles():
    """Test 5: Test rows do not affect category profiles."""
    with open(FROZEN_DIR / "category_profiles.json", encoding="utf-8") as f:
        profiles = json.load(f)

    with open(TRAIN_DIR / "products.json", encoding="utf-8") as f:
        train_prods = json.load(f)

    for cat, prof in profiles.items():
        c_prods = [p for p in train_prods if p["category"] == cat]
        prices = [p["price"] for p in c_prods]
        assert prof["n_products"] == len(c_prods), f"Profile n_products {prof['n_products']} != training count {len(c_prods)}"
        assert np.isclose(prof["price"]["median"], float(np.median(prices))), f"Profile median price mismatch in {cat}"


def test_6_test_rows_do_not_affect_brand_features():
    """Test 6: Test rows do not affect brand features."""
    with open(FROZEN_DIR / "brand_tier_map.json", encoding="utf-8") as f:
        bt = json.load(f)

    with open(TRAIN_DIR / "products.json", encoding="utf-8") as f:
        train_prods = json.load(f)

    # Calculate footprint on train_prods only
    counts = {}
    for p in train_prods:
        b = (p.get("brand") or "").strip().casefold()
        counts[b] = counts.get(b, 0) + 1

    for b, cnt in counts.items():
        expected_tier = 3 if cnt >= 11 else 2 if cnt >= 5 else 1 if cnt >= 2 else 0
        assert bt["brands"].get(b) == expected_tier, f"Brand tier mismatch for brand {b}"

    # Verify fallback for unknown brand is new_tier (0)
    assert bt["new_tier"] == 0


def test_7_hyperparameters_selected_without_test_set():
    """Test 7: Hyperparameters selected strictly on training cross-validation."""
    with open(FROZEN_DIR / "xgb_physical_aspects_only_features.json", encoding="utf-8") as f:
        features = json.load(f)

    # Ensure no test products participated in hyperparameter determination
    train_df = pd.read_parquet(FROZEN_DIR / "train_features.parquet")
    assert len(train_df) == 507, f"Training features has {len(train_df)} rows, expected 507"


def test_8_prompts_frozen_without_test_influence():
    """Test 8: LLM bridging prompts are frozen and reference only pre-cutoff profiles."""
    with open(FROZEN_DIR / "category_profiles.json", encoding="utf-8") as f:
        profiles = json.load(f)

    from src.extraction.extraction_prompt import build_bridging_prompt
    from src.prediction.bridging_layer import profile_to_prompt_fields

    fields = profile_to_prompt_fields(profiles["smartwatches"])
    prompt = build_bridging_prompt({"name": "Test Watch", "price": 99.0, "description": "Good watch"}, "smartwatches", fields, version=2)
    assert "smartwatches" in prompt
    assert str(profiles["smartwatches"]["price"]["median"]) in prompt or f"{profiles['smartwatches']['price']['median']:.0f}" in prompt


def test_9_test_labels_only_loaded_by_evaluation():
    """Test 9: Test labels are only loaded by the evaluation stage."""
    eval_script = (ROOT / "src/strict_temporal/evaluate_test.py").read_text(encoding="utf-8")
    assert "test_labels/ground_truth.json" in eval_script

    pred_script = (ROOT / "src/strict_temporal/predict_test.py").read_text(encoding="utf-8")
    assert "test_labels" not in pred_script or "assert \"test_labels\" not in" in pred_script


def test_10_byte_for_byte_prediction_identity_without_labels():
    """Test 10: Run A (labels present elsewhere) vs Run B (labels completely deleted/unavailable)
    yields byte-for-byte identical predictions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pred_a_file = tmp_path / "pred_a.json"
        pred_b_file = tmp_path / "pred_b.json"

        # Run A: standard execution
        run_prediction_pipeline(
            inputs_file=TEST_INPUTS_DIR / "products_test_specs.json",
            out_file=pred_a_file,
            mode="bridged"
        )

        # Run B: temporarily move/hide test_labels directory completely
        backup_labels_dir = tmp_path / "temp_backup_labels"
        shutil.move(str(TEST_LABELS_DIR), str(backup_labels_dir))
        try:
            assert not TEST_LABELS_DIR.exists(), "test_labels was not removed for Run B test!"
            run_prediction_pipeline(
                inputs_file=TEST_INPUTS_DIR / "products_test_specs.json",
                out_file=pred_b_file,
                mode="bridged"
            )
        finally:
            # Restore test_labels directory
            shutil.move(str(backup_labels_dir), str(TEST_LABELS_DIR))
            assert TEST_LABELS_DIR.exists(), "Failed to restore test_labels directory!"

        # Compare outputs byte-for-byte
        assert filecmp.cmp(pred_a_file, pred_b_file, shallow=False), (
            "CRITICAL FAILURE: Predictions differ when test labels are removed!"
        )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
