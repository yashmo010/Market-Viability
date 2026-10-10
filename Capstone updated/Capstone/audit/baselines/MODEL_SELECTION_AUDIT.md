# Model Selection vs. Final Inference Audit

**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher, Experimental Scientist, and Hostile Peer Reviewer  
**Scope**: Verification of the separation between training-time model selection and untouched test inference.

---

## 1. Audit Inquest: Was the Test Set Ever Used for Model Selection?

We audited every stage of the pipeline to verify whether test set performance guided any modeling decision:

| Development Decision | Selected On | Was Test Set Evaluated? | Evidence / Code Trace | Audit Verdict |
|---|---|:---:|---|:---:|
| **Tree Count ($n=112$)** | 5-Fold CV on pre-cutoff pool ($N=507$) | **NO** | `fit_freeze.py:L298-315` | **CLEAN** |
| **Learning Rate ($\eta=0.05$)** | Fixed architecture prior | **NO** | Hardcoded in `XGB_PARAMS` | **CLEAN** |
| **Max Depth ($5$)** | Fixed architecture prior | **NO** | Hardcoded in `XGB_PARAMS` | **CLEAN** |
| **Monotone Constraints** | Domain economic theory | **NO** | Fixed in `MONOTONE_BY_FEATURE` | **CLEAN** |
| **Feature Manifest (21 features)** | Domain schema definition | **NO** | Serialized in `frozen_state/` | **CLEAN** |
| **Target Scalers (Min/Max)** | 507 training products only | **NO** | `fit_freeze.py:L95-131` | **CLEAN** |
| **Brand Tier Mapping** | Pre-cutoff catalog footprint | **NO** | `fit_freeze.py:L133-151` | **CLEAN** |
| **Category Profiles** | Pre-cutoff reviews & extractions | **NO** | `fit_freeze.py:L230-283` | **CLEAN** |
| **Ridge Alpha ($\alpha=10.0$)** | 5-Fold CV on training pool | **NO** | `audit_baselines_and_ablations.py` | **CLEAN** |
| **Seed Selection ($42$)** | Arbitrary default convention | **NO** | Tested across 8 seeds in audit | **CLEAN** |

---

## 2. Verification of Physical Code Barriers

1. **Prediction Script Isolation**:
   In `src/strict_temporal/predict_test.py`:
   - Line 156: Explicit assert statement blocks loading any file containing `"test_labels"` in the path.
   - Line 163: Asserts that input records do not contain the key `"success_score"`.
   - The test labels file (`strict_temporal/data/test_labels/ground_truth.json`) is never imported, read, or parsed during feature construction or inference.
2. **Byte-for-Byte Output Determinism**:
   When `predict_test.py` is executed with `ground_truth.json` deleted or moved to an isolated directory, the generated predictions file (`predictions.json`) produces the **exact same SHA-256 hash** (`20ac4b1e670fe3f4...`).
3. **Automated Assertion Test**:
   In `tests/test_temporal_leakage.py` (Test 1) and `tests/test_statistical_validity.py` (Test 10), automated test suites verify that prediction code cannot access ground truth labels.

---

## 3. Forensic Identification of Past Vulnerabilities (Pre-Audit)

During our historical code audit, two pre-audit vulnerabilities were identified and resolved:
1. **Vulnerability 1 (Historical Table 1 Script `ml_algorithm_comparison.py`)**:
   - In early capstone drafts, 5-fold CV was executed across all 631 products with early stopping evaluated on the outer validation fold.
   - **Resolution**: Fixed in `scripts/reproduce_table1_leakage_free.py` via inner 85/15 nested splits, and superseded by the strict forward-in-time temporal holdout in Issue 1.
2. **Vulnerability 2 (Prompt Tuning on 90 Retro Products)**:
   - Prompt v2 (skeptic prompt) was iteratively refined on an initial sample of 90 products, introducing potential overfitting to that development sample.
   - **Resolution**: Pre-registered a separate confirmatory holdout ($N=59$), and subsequently sealed the strict forward-in-time temporal holdout ($N=124$) with zero prompt re-tuning.

---

## 4. Final Verdict

**MODEL SELECTION PROTOCOL IS STRICTLY VERIFIED AND CLEAN**.  
The test set ($N=124$) functions exclusively as a sealed out-of-sample forward-in-time evaluation target, with zero feedback into feature engineering, hyperparameter selection, or model checkpoints.
