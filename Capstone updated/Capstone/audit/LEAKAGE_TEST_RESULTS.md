# Automated Leakage Test Results

**Date / Timestamp:** 2026-10-05  
**Verdict:** **PASSED (10/10)**  
**Runner:** pytest on `tests/test_temporal_leakage.py`  

---

## Summary of Evaluated Tests

| Test ID | Test Description | Required Behavior | Status |
|---|---|---|---|
| **TEST-01** | Label Inaccessibility to Prediction | Prediction pipeline throws assertion error if passed test labels | **PASS** |
| **TEST-02** | Test ID Absence in Fitting | 0% overlap between test product IDs and training features | **PASS** |
| **TEST-03** | Temporal Timestamp Partitioning | All train products have first review <= cutoff; all test products > cutoff | **PASS** |
| **TEST-04** | Normalization Invariance | Normalization scalers strictly fitted on training products only | **PASS** |
| **TEST-05** | Category Profile Invariance | Category price quantiles and aspect means derived only from train set | **PASS** |
| **TEST-06** | Brand Feature Invariance | Brand footprint counts only pre-cutoff SKUs; unknown brands get tier 0 | **PASS** |
| **TEST-07** | Hyperparameter Independence | Model hyperparameters selected strictly via 5-fold CV on train set | **PASS** |
| **TEST-08** | Prompt / Schema Freezing | Bridging prompts reference frozen pre-cutoff profiles only | **PASS** |
| **TEST-09** | Evaluation Isolation | Ground truth test labels are loaded solely at evaluation stage | **PASS** |
| **TEST-10** | Byte-for-Byte Identity | Run A (labels present elsewhere) vs Run B (labels deleted) identical | **PASS** |

---

## Detailed Execution Output

```text
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- C:\Program Files\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Capstone updated\Capstone
plugins: anyio-4.12.1, langsmith-0.10.5
collecting ... collected 10 items

tests/test_temporal_leakage.py::test_1_labels_inaccessible_to_prediction PASSED [ 10%]
tests/test_temporal_leakage.py::test_2_test_ids_not_present_during_fitting PASSED [ 20%]
tests/test_temporal_leakage.py::test_3_timestamps_temporal_partitioning PASSED [ 30%]
tests/test_temporal_leakage.py::test_4_test_rows_do_not_affect_normalization PASSED [ 40%]
tests/test_temporal_leakage.py::test_5_test_rows_do_not_affect_category_profiles PASSED [ 50%]
tests/test_temporal_leakage.py::test_6_test_rows_do_not_affect_brand_features PASSED [ 60%]
tests/test_temporal_leakage.py::test_7_hyperparameters_selected_without_test_set PASSED [ 70%]
tests/test_temporal_leakage.py::test_8_prompts_frozen_without_test_influence PASSED [ 80%]
tests/test_temporal_leakage.py::test_9_test_labels_only_loaded_by_evaluation PASSED [ 90%]
tests/test_temporal_leakage.py::test_10_byte_for_byte_prediction_identity_without_labels PASSED [100%]

============================= 10 passed in 4.14s ==============================

```
