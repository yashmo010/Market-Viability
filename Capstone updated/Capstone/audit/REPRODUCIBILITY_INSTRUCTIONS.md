# External Auditor Reproducibility Instructions

This document provides exact, terminal-executable commands for an independent researcher or auditor to reproduce and verify the strict launch-blind temporal evaluation pipeline from scratch.

---

## 1. Prerequisites and Environment

Ensure Python 3.10+ (tested on Python 3.13.12) is installed with standard scientific packages:

```bash
pip install numpy pandas scipy scikit-learn xgboost pytest
```

Verify your environment matches `audit/ENVIRONMENT.txt`.

---

## 2. Step-by-Step Verification Protocol

### Step 1: Verify the Temporal Partitioning and Information Barrier
Run the data splitter to partition raw products and reviews at the October 31, 2021 cutoff (`1635724799`):

```bash
python src/strict_temporal/split_temporal.py
```

**Verification Checks:**
- Confirms 507 pre-cutoff training products in `strict_temporal/data/train/products.json`.
- Confirms 124 post-cutoff test products in `strict_temporal/data/test_inputs/products_test_specs.json`.
- Confirms `test_inputs/products_test_specs.json` contains ONLY product specifications (`name`, `brand`, `category`, `price`, `specs`) and NO target fields (`success_score`, `avg_rating`, `review_velocity`).
- Confirms 124 ground truth labels isolated in `strict_temporal/data/test_labels/ground_truth.json`.
- Generates `audit/DATA_SPLIT_MANIFEST.csv`.

---

### Step 2: Fit and Freeze Preprocessing & Model on Training Data Only
Execute the fit-and-freeze pipeline:

```bash
python src/strict_temporal/fit_freeze.py
```

**Verification Checks:**
- Target scalers (`vol_min`, `vol_max`, etc.) fitted strictly on 507 training products (`strict_temporal/frozen_state/target_scalers.json`).
- Brand tier catalog footprint fitted strictly on 507 training products (`strict_temporal/frozen_state/brand_tier_map.json`).
- Category profiles (aspect means, price quantiles) fitted strictly on 507 training products (`strict_temporal/frozen_state/category_profiles.json`).
- Optimal tree depth and estimators selected via 5-fold cross-validation strictly on pre-cutoff data (`best_iteration = 112`, mean CV R² = 0.574).
- Final model saved to `strict_temporal/frozen_state/xgb_physical_aspects_only.json`.

---

### Step 3: Run the Automated Leakage Test Suite (10/10 Verification)
Execute the complete automated leakage verification test suite:

```bash
python -m pytest tests/test_temporal_leakage.py -v
```

or via the reporting script:

```bash
python scripts/run_leakage_tests.py
```

**Verification Checks:**
- All 10 tests must pass (10/10).
- Confirms test labels are inaccessible to prediction code.
- Confirms zero test ID overlap in training features.
- Confirms byte-for-byte identical predictions whether test labels are physically present or deleted from disk (Run A vs Run B).

---

### Step 4: Generate Strict Launch-Blind Predictions
Run prediction on test specifications using the frozen artifacts:

```bash
python src/strict_temporal/predict_test.py
```

**Verification Checks:**
- Loads strictly from `strict_temporal/data/test_inputs/products_test_specs.json`.
- Throws an assertion error if any attempt is made to read from `test_labels/`.
- Generates 124 predictions saved to `strict_temporal/predictions/predictions.json`.

---

### Step 5: Evaluate Against Ground Truth Labels
Execute the final evaluation stage:

```bash
python src/strict_temporal/evaluate_test.py
```

**Expected Metrics Output:**
- Sample Size: `n = 124`
- Overall Spearman rho: `0.562` (95% CI: `[0.414, 0.681]`, `p = 1.09e-11`)
- Top-vs-Bottom Quintile AUC: `0.890` (95% CI: `[0.795, 0.968]`)
- RMSE: `21.12`, MAE: `17.84`
- Mean Within-Category rho: `0.207`
- Mature Cohort (review count >= 30, `n = 51`): Spearman rho = `0.631` (95% CI `[0.413, 0.778]`), AUC = `0.955`
- Output saved to `audit/STRICT_TEST_RESULTS.json` and `audit/CATEGORY_RESULTS.csv`.
