# Statistical Validity Automated Test Results

**Date of Execution:** 2026-10-05  
**Test Suite:** `tests/test_statistical_validity.py`  
**Environment:** Python 3.13.12, pytest 9.1.1, scikit-learn 1.8.0, xgboost 3.3.0, scipy 1.17.1  
**Overall Result:** **15 / 15 PASSED (100%)**

---

## Summary Table

| Test ID | Test Function | Property Verified | Result | Execution Time |
|---|---|---|:---:|---:|
| **STAT-01** | `test_1_spearman_rho_recomputation` | Recomputed Spearman $\rho = 0.562$ matches stored | **PASS** | 0.04s |
| **STAT-02** | `test_2_rmse_recomputation` | Recomputed $\text{RMSE} = 21.12$ matches stored | **PASS** | 0.02s |
| **STAT-03** | `test_3_auc_recomputation` | Recomputed Quintile $\text{AUC} = 0.890$ matches stored | **PASS** | 0.03s |
| **STAT-04** | `test_4_confidence_intervals_method` | 10k percentile bootstrap yields $[0.414, 0.681]$ | **PASS** | 0.21s |
| **STAT-05** | `test_5_sample_sizes_match` | Evaluated $n=124$ total, $n=51$ mature | **PASS** | 0.01s |
| **STAT-06** | `test_6_positive_negative_auc_classes` | Positive ($n=25$) and Negative ($n=25$) quintiles | **PASS** | 0.02s |
| **STAT-07** | `test_7_quintile_thresholds_rule` | Verified quintile cutoff distribution | **PASS** | 0.01s |
| **STAT-08** | `test_8_cv_folds_observations` | 5 folds on pre-cutoff training ($n=507$) | **PASS** | 0.03s |
| **STAT-09** | `test_9_preprocessing_isolated_to_training` | Preprocessing scalers fitted strictly on $n=507$ | **PASS** | 0.02s |
| **STAT-10** | `test_10_final_test_not_used_for_selection` | Test labels inaccessible to predictor code | **PASS** | 0.01s |
| **STAT-11** | `test_11_best_iteration_from_cv` | Mean best iteration $= 112$ from 5-fold CV | **PASS** | 0.01s |
| **STAT-12** | `test_12_oracle_comparison_paired_observations` | Experiment A vs B paired on same 124 test items | **PASS** | 0.02s |
| **STAT-13** | `test_13_percentage_ratio_calculations` | Correlation ratio $71.4\%$, variance ratio $50.9\%$ | **PASS** | 0.01s |
| **STAT-14** | `test_14_random_seeds_recorded` | All random seeds declared and evaluated | **PASS** | 0.01s |
| **STAT-15** | `test_15_canonical_evaluation_reproduces_metrics` | `evaluate_strict_temporal.py` reproduces stored results | **PASS** | 0.25s |

---

## Detailed Test Logs

### Test 1: Spearman Rho Recomputation
- Evaluated $n = 124$ predictions and ground-truth values.
- Recomputed: $\rho = 0.56214$. Stored: $0.562$. Difference: $< 0.0002$.
- **Verdict: PASS**

### Test 2: RMSE Recomputation
- Recomputed: $\text{RMSE} = 21.1194$. Stored: $21.12$. Difference: $< 0.001$.
- **Verdict: PASS**

### Test 3: AUC Recomputation
- Computed Mann-Whitney $U$ on actual top quintile ($n=25$) vs bottom quintile ($n=25$).
- Recomputed: $\text{AUC} = 0.8904$. Stored: $0.890$. Difference: $< 0.0005$.
- **Verdict: PASS**

### Test 4: Confidence Interval Mechanics
- Verified 10,000 non-parametric bootstrap resamples with seed 42.
- 2.5th percentile $= 0.414$, 97.5th percentile $= 0.681$.
- Matches stored bounds exactly.
- **Verdict: PASS**

### Test 5: Sample Sizes
- Total test items $= 124$. Mature cohort ($\ge 30$ reviews) $= 51$.
- **Verdict: PASS**

### Test 6: Class Definitions
- Verified that top quintile has 25 products, bottom quintile has 25 products.
- **Verdict: PASS**

### Test 7: Threshold Construction
- Cutoff points derived using `pd.qcut(y, 5)` strictly on label evaluation phase.
- **Verdict: PASS**

### Test 8: Cross-Validation Isolation
- Verified `train_features.parquet` has 507 products.
- Each CV fold has $\approx 405$ train and $\approx 102$ validation items.
- **Verdict: PASS**

### Test 9: Preprocessing Scope
- Category scalers and brand tiers verified to have been fit strictly on pre-cutoff training items.
- **Verdict: PASS**

### Test 10: Model Selection Independence
- Checked `predict_test.py` and feature manifests: zero references to ground truth or labels.
- **Verdict: PASS**

### Test 11: Early Stopping Derivation
- Cross-validation fold iterations: $[108, 124, 115, 98, 117]$.
- Mean iteration $= 112.4 \to 112$.
- **Verdict: PASS**

### Test 12: Paired Observations
- Both Experiment A (specs) and Experiment B (oracle reviews) evaluated on identical 124 test items.
- **Verdict: PASS**

### Test 13: Metric Math
- Ratio of correlations: $0.538 / 0.754 = 71.35\% \to 71.4\%$.
- Ratio of variance: $0.538^2 / 0.754^2 = 50.91\% \to 50.9\%$.
- **Verdict: PASS**

### Test 14: Seed Stability
- Evaluated seeds $42, 100, 2024, 777, 999$.
- Recorded in `SEED_STABILITY.csv`.
- **Verdict: PASS**

### Test 15: Canonical Script Verification
- `evaluate_strict_temporal.py` executed and produced identical primary metrics and cryptographic hashes.
- **Verdict: PASS**
