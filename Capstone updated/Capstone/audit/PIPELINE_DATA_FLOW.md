# Strict Launch-Blind Pipeline Data Flow and Information Architecture

This document maps the complete information flow of the LaunchSight research evaluation pipeline under the strict temporal evaluation protocol.

---

## 1. End-to-End Data Flow Map

```text
                                RAW DATA
                 +------------------------------------+
                 | products_physical.json (n=640)     |
                 | reviews_physical.json (n=43,599)   |
                 | reddit_context.json                |
                 +-----------------+------------------+
                                   |
                         PREPROCESSING / CLEANING
                 +-----------------+------------------+
                 | Fake-Review Quality Filters        |
                 | (Burst, Extreme J, Near-Duplicates)|
                 | Excluded: 9 suspect products       |
                 | Retained: 631 clean products       |
                 +-----------------+------------------+
                                   |
                     TEMPORAL CUTOFF PARTITIONING
                     Cutoff: 2021-10-31 23:59:59 UTC
                                   |
                  +----------------+----------------+
                  |                                 |
           PRE-CUTOFF DATA                   POST-CUTOFF DATA
         (Launch <= 2021-10-31)            (Launch > 2021-10-31)
              n = 507                           n = 124
                  |                                 |
                  |                                 +-----------------------+
                  |                                 |                       |
                  v                                 v                       v
         +-----------------+              +-------------------+    +-----------------+
         |  TRAINING SET   |              | FINAL TEST INPUTS |    |   TEST LABELS   |
         |  (507 products, |              | (Specs, Brand,    |    | (Post-launch    |
         |  39,138 reviews)|              |  Category, Price) |    |  Success Score) |
         +--------+--------+              +---------+---------+    +--------+--------+
                  |                                 |                       |
                  v                                 |              PHYSICALLY ISOLATED
         +-----------------+                        |              IN test_labels/
         | FIT OPERATIONS  |                        |              (Inaccessible to
         | - Target MinMax |                        |               prediction code)
         | - Brand Footpr. |                        |                       |
         | - Cat. Profiles |                        |                       |
         | - XGBoost Model |                        |                       |
         +--------+--------+                        |                       |
                  |                                 |                       |
                  v                                 |                       |
         +-----------------+                        |                       |
         |  FREEZE STATE   |                        |                       |
         | - target_scalers|                        |                       |
         | - brand_tier_map|                        |                       |
         | - cat_profiles  |                        |                       |
         | - xgb_model.json|                        |                       |
         +--------+--------+                        |                       |
                  |                                 |                       |
                  +----------------+----------------+                       |
                                   |                                        |
                                   v                                        |
                        +----------------------+                            |
                        | PREDICTION PIPELINE  |                            |
                        | Spec Bridging + Model|                            |
                        | (Strictly test specs |                            |
                        |  + frozen artifacts) |                            |
                        +----------+-----------+                            |
                                   |                                        |
                                   v                                        |
                        +----------------------+                            |
                        |  FROZEN PREDICTIONS  |                            |
                        |  predictions.json    |                            |
                        +----------+-----------+                            |
                                   |                                        |
                                   +--------------------+-------------------+
                                                        |
                                                        v
                                             +--------------------+
                                             |  EVALUATION STAGE  |
                                             |  Reveal labels &   |
                                             |  compute Spearman  |
                                             |  rho, AUC, RMSE    |
                                             +--------------------+
```

---

## 2. Information Classification Framework

Every variable and process in the project is strictly partitioned into three classes:

### CLASS A — Allowed at Prediction Time
Information genuinely available to a manufacturer before product launch:
1. Product Title / Model Name
2. Product Category (one of 5 hardware categories)
3. Product Target Launch Price (USD)
4. Launch Specifications and feature bullet points
5. Historical category norms prior to cutoff (frozen category price quartiles, historical aspect averages)
6. Historical brand catalog footprint prior to cutoff (SKU count launched on or before 2021-10-31)

### CLASS B — Allowed Only for Fitting Training / Validation Procedures
Information accessible during the training and hyperparameter selection phase, but strictly forbidden from entering test prediction rows:
1. Historical review volume, rating distributions, and review text of pre-cutoff products
2. Historical extracted aspect scores from reviews of pre-cutoff products
3. Target success scores of pre-cutoff products
4. 5-fold cross-validation out-of-fold validation splits on pre-cutoff products

### CLASS C — Forbidden Before Final Prediction
Information that must never touch any feature, scaler, reference distribution, model parameter, or prompt prior to evaluation:
1. Final test product post-launch reviews
2. Final test product post-launch star ratings
3. Final test product post-launch sales/volume/velocity
4. Final test product target labels (`success_score`)
5. Catalog releases occurring after 2021-10-31
6. Post-cutoff category distributions or shifts
7. Final test performance metrics (cannot be used to tune models or prompts)

---

## 3. Physical Information Barrier Architecture

To prevent accidental leakage through shared memory, joins, or dataframe filtering, the pipeline implements code-level and filesystem-level barriers:

```text
strict_temporal/
  data/
    train/
      products.json           <-- 507 pre-cutoff products
      reviews.json            <-- 39,138 pre-cutoff reviews
    test_inputs/
      products_test_specs.json<-- 124 test products (SPECS ONLY, NO TARGETS)
    test_labels/
      ground_truth.json       <-- 124 target scores (ISOLATED)
  frozen_state/
    target_scalers.json       <-- Fitted on train only
    brand_tier_map.json       <-- Fitted on train only
    category_profiles.json    <-- Fitted on train only
    xgb_physical_aspects_only.json <-- Trained on train only
  predictions/
    predictions.json          <-- Generated strictly from test_inputs + frozen_state
```

The prediction entry point (`src/strict_temporal/predict_test.py`) asserts that `test_labels` is not in the input filepath and verifies that `success_score` does not exist in any input record. Only `src/strict_temporal/evaluate_test.py` loads `ground_truth.json`.
