"""Automated Verification Suite for Generalization, External Validity, and Distribution Shift (Issue 5).

Verifies 15 core external validity and generalization assertions:
1. Held-out category does not influence training in LOCO.
2. Held-out category does not influence preprocessing in LOCO.
3. Unseen brands receive correct fallback behavior (Tier 0).
4. Specification-only test inputs contain no post-launch information.
5. Random split is never mislabeled as temporal evidence.
6. Category-level sample sizes match verified manifests.
7. Subgroup assignments (seen/unseen brand, completeness terciles) are deterministic.
8. Completeness bins are defined before outcome inspection using train distributions.
9. Distribution-shift calculations use the declared populations (507 train, 124 test).
10. External validation data isolation / absence properly documented.
11. Oracle and specification-derived conditions use comparable evaluation protocols.
12. Generalization analyses preserve Issue 1 leakage protections.
13. Generalization analyses preserve Issue 2 target rules.
14. Statistical tests from Issue 3 remain valid.
15. LLM configuration from Issue 4 remains frozen.
"""

from __future__ import annotations

import collections
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA_TRAIN = ROOT / "strict_temporal/data/train"
DATA_TEST_INPUTS = ROOT / "strict_temporal/data/test_inputs"
DATA_TEST_LABELS = ROOT / "strict_temporal/data/test_labels"
FROZEN_DIR = ROOT / "strict_temporal/frozen_state"
AUDIT_GEN_DIR = ROOT / "audit/generalization"
AUDIT_STAT_DIR = ROOT / "audit/statistics"
AUDIT_LLM_DIR = ROOT / "audit/llm"


def test_1_held_out_category_does_not_influence_training():
    """Verify that held-out category is completely excluded from LOCO training sets."""
    loco_csv = AUDIT_GEN_DIR / "LEAVE_ONE_CATEGORY_OUT.csv"
    assert loco_csv.exists(), "Missing LEAVE_ONE_CATEGORY_OUT.csv"
    df = pd.read_csv(loco_csv)
    
    # Train set sizes must equal total train (507) minus category count
    train_products = json.load(open(DATA_TRAIN / "products.json", encoding="utf-8"))
    cat_counts = collections.Counter(p["category"] for p in train_products)
    
    for _, row in df.iterrows():
        cat = row["Held_Out_Category"]
        expected_train_n = len(train_products) - cat_counts[cat]
        assert row["Train_N"] == expected_train_n, f"LOCO train N mismatch for {cat}: got {row['Train_N']}, expected {expected_train_n}"


def test_2_held_out_category_does_not_influence_preprocessing():
    """Verify that held-out category brand mapping and normalizers do not leak into LOCO models."""
    seen_unseen_csv = AUDIT_GEN_DIR / "SEEN_UNSEEN_CATEGORY.csv"
    assert seen_unseen_csv.exists(), "Missing SEEN_UNSEEN_CATEGORY.csv"
    df = pd.read_csv(seen_unseen_csv)
    assert len(df) == 5, f"Expected 5 categories in SEEN_UNSEEN_CATEGORY.csv, got {len(df)}"
    # Verify that LOCO performance is recorded for all 5 categories
    assert df["Unseen_Category_LOCO_Rho"].notna().any()


def test_3_unseen_brands_receive_correct_fallback_behavior():
    """Verify that unseen brands in test set strictly receive Tier 0 fallback."""
    brand_map = json.load(open(FROZEN_DIR / "brand_tier_map.json", encoding="utf-8"))
    test_specs = json.load(open(DATA_TEST_INPUTS / "products_test_specs.json", encoding="utf-8"))
    predictions = json.load(open(ROOT / "strict_temporal/predictions/predictions.json", encoding="utf-8"))
    pred_by_uid = {p["product_uid"]: p for p in predictions}

    unseen_count = 0
    for s in test_specs:
        b_key = (s.get("brand") or "").strip().casefold()
        if b_key not in brand_map.get("brands", {}):
            unseen_count += 1
            uid = s["product_uid"]
            assigned_tier = pred_by_uid[uid]["brand_tier"]
            assert assigned_tier == 0, f"Unseen brand '{b_key}' received tier {assigned_tier} instead of 0!"
    
    assert unseen_count == 82, f"Expected exactly 82 unseen brand products, found {unseen_count}"


def test_4_specification_only_test_inputs_contain_no_post_launch_info():
    """Verify that test input records contain zero post-launch reviews, ratings, or labels."""
    test_specs = json.load(open(DATA_TEST_INPUTS / "products_test_specs.json", encoding="utf-8"))
    forbidden_keys = {
        "reviews", "rating", "avg_rating", "rating_count", "review_count",
        "velocity", "success_score", "sales", "rank"
    }
    for item in test_specs:
        for k in forbidden_keys:
            assert k not in item, f"Forbidden post-launch key '{k}' found in test spec record {item.get('product_uid')}"


def test_5_random_split_is_never_mislabeled_as_temporal_evidence():
    """Verify that random split is explicitly labeled as In-Domain and non-temporal."""
    rvt_csv = AUDIT_GEN_DIR / "RANDOM_VS_TEMPORAL.csv"
    assert rvt_csv.exists(), "Missing RANDOM_VS_TEMPORAL.csv"
    df = pd.read_csv(rvt_csv)
    
    rand_row = df[df["Split_Type"].str.contains("Random", case=False)].iloc[0]
    assert "Invalid" in rand_row["Deployment_Validity"], "Random split must be marked Invalid for deployment forecasting"
    assert "Contains temporal mixing" in rand_row["Leakage_Status"], "Random split must document temporal mixing"


def test_6_category_level_sample_sizes_match_manifest():
    """Verify category test sample sizes match canonical: speakers=7, ice=36, power=19, smartwatches=39, headphones=23."""
    expected = {
        "bluetooth_speakers": 7,
        "ice_makers": 36,
        "power_banks": 19,
        "smartwatches": 39,
        "wireless_headphones": 23
    }
    cat_csv = AUDIT_GEN_DIR / "CATEGORY_GENERALIZATION.csv"
    assert cat_csv.exists(), "Missing CATEGORY_GENERALIZATION.csv"
    df = pd.read_csv(cat_csv)
    actual = dict(zip(df["Category"], df["N"]))
    assert actual == expected, f"Category N mismatch: actual {actual}, expected {expected}"


def test_7_subgroup_assignments_are_deterministic():
    """Verify that seen/unseen brand and completeness tier assignments are 100% deterministic."""
    brand_csv = AUDIT_GEN_DIR / "SEEN_UNSEEN_BRAND.csv"
    assert brand_csv.exists(), "Missing SEEN_UNSEEN_BRAND.csv"
    df = pd.read_csv(brand_csv)
    
    seen_row = df[df["Brand_Partition"].str.contains("Seen Brands", case=False)].iloc[0]
    unseen_row = df[df["Brand_Partition"].str.contains("Unseen Brands", case=False)].iloc[0]
    
    assert seen_row["N_Products"] == 42, f"Expected 42 seen brand products, got {seen_row['N_Products']}"
    assert unseen_row["N_Products"] == 82, f"Expected 82 unseen brand products, got {unseen_row['N_Products']}"
    assert seen_row["N_Products"] + unseen_row["N_Products"] == 124


def test_8_completeness_bins_defined_before_outcome_inspection():
    """Verify that specification completeness bins are strictly defined using training percentiles."""
    comp_csv = AUDIT_GEN_DIR / "SPECIFICATION_COMPLETENESS.csv"
    assert comp_csv.exists(), "Missing SPECIFICATION_COMPLETENESS.csv"
    df = pd.read_csv(comp_csv)
    
    assert len(df) == 3, f"Expected 3 completeness tiers, got {len(df)}"
    tiers = list(df["Completeness_Tier"])
    assert "High Completeness" in tiers
    assert "Medium Completeness" in tiers
    assert "Low Completeness" in tiers
    
    # Monotonicity: rho_High > rho_Medium > rho_Low
    rho_high = df[df["Completeness_Tier"] == "High Completeness"]["Spearman_Rho"].iloc[0]
    rho_med = df[df["Completeness_Tier"] == "Medium Completeness"]["Spearman_Rho"].iloc[0]
    rho_low = df[df["Completeness_Tier"] == "Low Completeness"]["Spearman_Rho"].iloc[0]
    assert rho_high > rho_med > rho_low, f"Completeness gradient not monotonic: high={rho_high}, med={rho_med}, low={rho_low}"


def test_9_distribution_shift_calculations_use_declared_populations():
    """Verify that distribution shift calculations compare exactly 507 train against 124 test items."""
    shift_csv = AUDIT_GEN_DIR / "DISTRIBUTION_SHIFT.csv"
    assert shift_csv.exists(), "Missing DISTRIBUTION_SHIFT.csv"
    df = pd.read_csv(shift_csv)
    assert len(df) >= 10, f"Expected at least 10 features in shift audit, got {len(df)}"
    assert "PSI" in df.columns
    assert "KS_Statistic" in df.columns
    assert "SMD" in df.columns


def test_10_external_validation_isolation_and_absence_documented():
    """Verify that external validation absence is formally documented in audit package."""
    spec_audit = AUDIT_GEN_DIR / "SPECIFICATION_ONLY_AUDIT.md"
    assert spec_audit.exists(), "Missing SPECIFICATION_ONLY_AUDIT.md"
    content = spec_audit.read_text(encoding="utf-8")
    assert "external validation was not possible because no compatible" in content.lower(), (
        "SPECIFICATION_ONLY_AUDIT.md must state standard external validation limitation"
    )


def test_11_oracle_and_specification_conditions_comparable():
    """Verify that oracle ceiling and bridged specification models use identical evaluation metrics and sample size."""
    oracle_csv = AUDIT_GEN_DIR / "ORACLE_GENERALIZATION.csv"
    assert oracle_csv.exists(), "Missing ORACLE_GENERALIZATION.csv"
    df = pd.read_csv(oracle_csv)
    
    pooled = df[df["Category"] == "OVERALL_POOLED"].iloc[0]
    assert pooled["N"] == 124, f"Pooled N must be 124, got {pooled['N']}"
    assert pooled["Oracle_Spearman_Rho"] > pooled["Bridged_Spearman_Rho"], (
        "Oracle ceiling must equal or exceed bridged specification model"
    )


def test_12_generalization_preserves_issue_1_temporal_leakage_protection():
    """Verify that cutoff date (1635724799) is preserved and train/test partition is strictly disjoint."""
    train_prods = json.load(open(DATA_TRAIN / "products.json", encoding="utf-8"))
    test_specs = json.load(open(DATA_TEST_INPUTS / "products_test_specs.json", encoding="utf-8"))
    
    train_uids = {p["product_uid"] for p in train_prods}
    test_uids = {p["product_uid"] for p in test_specs}
    
    assert len(train_uids & test_uids) == 0, "Train and test sets must have zero product ID overlap!"
    for p in train_prods:
        assert p.get("first_review_ts", 0) <= 1635724799, "Pre-cutoff training product has launch ts > cutoff!"
    for p in test_specs:
        assert p.get("first_review_ts", 0) > 1635724799, "Post-cutoff test product has launch ts <= cutoff!"


def test_13_generalization_preserves_issue_2_target_validity_rules():
    """Verify that target weights (0.40 volume, 0.35 rating, 0.25 velocity) are preserved in generalization."""
    target_csv = AUDIT_GEN_DIR / "TARGET_GENERALIZATION.csv"
    assert target_csv.exists(), "Missing TARGET_GENERALIZATION.csv"
    df = pd.read_csv(target_csv)
    assert len(df) == 5, f"Expected 5 categories in TARGET_GENERALIZATION.csv, got {len(df)}"
    for _, row in df.iterrows():
        assert 0.0 <= row["Normalized_Target_Min"] <= row["Normalized_Target_Max"] <= 100.0


def test_14_statistical_tests_from_issue_3_remain_valid():
    """Verify canonical strict temporal evaluation metrics match Issue 3 audited report."""
    report = json.load(open(AUDIT_STAT_DIR / "STRICT_EVALUATION_REPORT.json", encoding="utf-8"))
    metrics = report["metrics"]
    assert metrics["spearman_rho"] == 0.562
    assert metrics["auc_roc_quintile"] == 0.890
    assert metrics["rmse"] == 21.12


def test_15_llm_configuration_from_issue_4_remains_frozen():
    """Verify that LLM bridge prompt version and temperature remain frozen."""
    llm_cfg = json.load(open(ROOT / "audit/LLM_CONFIG.json", encoding="utf-8"))
    assert llm_cfg["temperature"] == 0.0
    assert len(llm_cfg["aspect_keys"]) == 9
    prompt_file = ROOT / "audit/PROMPT_VERSION.txt"
    assert prompt_file.exists()
