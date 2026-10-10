# External Auditor Package — Strict Temporal Evaluation & Leakage Elimination

This package contains the complete audit trail, machine-readable manifests, frozen pipeline configurations, automated test suites, and empirical evaluation results resolving **Issue 1: Temporal / Test-Set Leakage** for the LaunchSight research project.

---

## 1. Executive Summary

| Audit Item | Original Pipeline (Legacy) | Corrected Pipeline (Strict Temporal) | Verdict |
|---|---|---|---|
| **Temporal Cutoff** | Stated as 2021-10-31, but mixed with 80% quantile split (2021-10-20) | Formally frozen calendar cutoff: **2021-10-31 23:59:59 UTC** | **RESOLVED & FROZEN** |
| **Information Barrier** | None: shared dataframe (`features_physical.parquet`) with test labels accessible | Physical filesystem separation (`train/`, `test_inputs/`, `test_labels/`) | **STRICT BARRIER IMPLEMENTED** |
| **Target Normalization** | Category MinMax volume/rating/velocity fitted over all 640 products | MinMax scalers fitted **strictly on 507 pre-cutoff products** | **LEAKAGE REMOVED** |
| **Brand Tier Feature** | Catalog footprint counted all products including future post-cutoff releases | Footprint counted **strictly on pre-cutoff products**; fallback tier 0 | **LEAKAGE REMOVED** |
| **Category Profiles** | Means, price percentiles, and review quotes pooled across all 631 products | Profiles fitted **strictly on pre-cutoff products and reviews** | **LEAKAGE REMOVED** |
| **Model Fitting** | Model fitted on full dataset; test products participated in training | Fitted strictly on 507 training products; 5-fold CV early stopping | **LEAKAGE REMOVED** |
| **Automated Tests** | None | 10 automated leakage tests in `tests/test_temporal_leakage.py` | **10/10 TESTS PASSED** |
| **Primary Metric (n=124)** | Claimed rho = 0.590, AUC = 0.942 | **Spearman rho = 0.562 [0.414, 0.681], AUC = 0.890 [0.795, 0.968]** | **SCIENTIFICALLY VALID** |
| **Mature Cohort (n=51)** | Claimed n=66, rho = 0.545, AUC = 0.901 | **n = 51, Spearman rho = 0.631 [0.413, 0.778], AUC = 0.955** | **RECONCILED & VALID** |

---

## 2. Directory Contents

```text
audit/
  README.md                          <-- You are here: comprehensive audit package guide
  EXPERIMENT_MANIFEST.json           <-- Machine-readable frozen manifest (IDs, commit, parameters)
  DATA_SPLIT_MANIFEST.csv            <-- Complete product-level split manifest (631 rows, train/test)
  FEATURE_LEAKAGE_AUDIT.csv          <-- Exhaustive feature provenance audit table
  PREPROCESSING_AUDIT.csv            <-- Preprocessing transformation audit table
  MODEL_CONFIG.json                  <-- Frozen XGBoost hyperparameters and monotone priors
  LLM_CONFIG.json                    <-- Frozen LLM bridging configuration and schema
  PROMPT_VERSION.txt                 <-- Prompt specification (Skeptic Prompt v2)
  RANDOM_SEEDS.json                  <-- Exact random seeds used across all operations
  ENVIRONMENT.txt                    <-- Operating system, Python version, and dependency manifests
  CODE_COMMIT.txt                    <-- Git commit hash at audit freeze
  PIPELINE_DATA_FLOW.md              <-- Detailed data-flow map and 3-class information architecture
  LEAKAGE_TEST_RESULTS.md            <-- Pytest log of 10 automated leakage tests (all PASSED)
  STRICT_TEST_RESULTS.json           <-- Primary machine-readable evaluation metrics
  CATEGORY_RESULTS.csv               <-- Per-category sample sizes, correlations, and AUCs
  REPRODUCIBILITY_INSTRUCTIONS.md    <-- Terminal commands to independently reproduce the experiment
  before_fix/
    original_summary.json            <-- Legacy benchmark figures and documented leakage flaws
  after_fix/
    strict_summary.json              <-- Verified strict temporal figures
    delta_comparison.csv             <-- Metric-by-metric comparison table with delta commentary
```

---

## 3. Quick-Start Verification

An external auditor can verify all claims in under 2 minutes:

```bash
# 1. Run the automated 10-point leakage test suite:
python scripts/run_leakage_tests.py

# 2. Re-run strict predictions from specs alone:
python src/strict_temporal/predict_test.py

# 3. Evaluate against ground truth test labels:
python src/strict_temporal/evaluate_test.py
```
