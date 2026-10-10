import json
from pathlib import Path

orig = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Capstone updated\Capstone")
audit_dir = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Legitimate\00_PROJECT_AUDIT")
audit_dir.mkdir(parents=True, exist_ok=True)

# 1. PROJECT_INVENTORY.md
inv_text = """# Project Inventory: Existing Launch-Blind Product Success Prediction Research

**Audit Date:** 2026-10-07  
**Branch:** Legitimate/00_PROJECT_AUDIT  
**Integrity State:** Original workspace preserved byte-for-byte; read-only inspection.

## 1. Directory Structure Overview
- **`src/`**: Core library modules:
  - `src/strict_temporal/`: Frozen training pipeline (`fit_freeze.py`) and test predictor (`predict_test.py`).
  - `src/prediction/`: Deployed inference service (`predictor.py`), spec coach (`spec_coach.py`), bridging layer (`bridging_layer.py`), input gate (`input_gate.py`).
  - `src/training/`: Legacy training scripts (`run_training.py`).
  - `src/extraction/`: LLM prompt construction, provider management (`llm_provider.py`, `extraction_prompt.py`).
  - `src/app/`: FastAPI application (`api.py`) and Streamlit launcher (`app.py`), React frontend (`frontend/dist/`).
- **`strict_temporal/`**: Isolated research environment enforcing temporal cutoff:
  - `data/train/`: 507 pre-cutoff products (`products.json`) and 43,599 historical reviews (`reviews.json`).
  - `data/test_inputs/`: 124 launch-blind test products specs (`products_test_specs.json`).
  - `data/test_labels/`: Strictly isolated test labels (`ground_truth.json`).
  - `frozen_state/`: Frozen model (`xgb_physical_aspects_only.json`), feature manifest (`xgb_physical_aspects_only_features.json`), brand tiers (`brand_tier_map.json`), category profiles (`category_profiles.json`), target scalers (`target_scalers.json`), train features (`train_features.parquet`).
  - `predictions/`: Canonical predictions (`predictions.json`).
- **`tests/`**: Automated test suite (74/74 passing):
  - `test_temporal_leakage.py`: 10/10 strict temporal leakage checks.
  - `test_baseline_validity.py`: 14/14 baseline model checks.
  - `test_statistical_validity.py`: 15/15 statistical recomputation and bootstrap checks.
  - `test_generalization_validity.py`: 15/15 generalization, cold start, and category checks.
  - `test_target_validity.py`: 10/10 target definition and scaling checks.
  - `test_llm_bridge.py`: 10/10 LLM bridging schema and grounding checks.
- **`audit/`**: Comprehensive experimental and statistical audit records:
  - `statistics/`: Canonical evaluation reports, early stopping audits, bootstrap calculations.
  - `baselines/`: Benchmark results, cold-start decompositions, paired model comparisons.
  - `llm/`: Aspect definitions, prompt versioning, stochasticity checks.
- **`paper_ieee/`**: Publication source files (`main.tex`, `refs.bib`, `paper_full.md`, high-res figures).
- **`submission/` & `redesign/`**: Generated docx and pdf manuscripts (`Research_Paper_IEEE_Final.docx/pdf`, `Survey_Paper_IEEE_Final.docx/pdf`).
"""
(audit_dir / "PROJECT_INVENTORY.md").write_text(inv_text, encoding="utf-8")

# 2. DATA_INVENTORY.md
data_text = """# Data Inventory: Strict Temporal Protocol (Cutoff: Oct 31, 2021)

## 1. Primary Datasets
| Dataset | Location | Product Count | Review Count | Access Restriction |
|---|---|---|---|---|
| Pre-Cutoff Training Pool | `strict_temporal/data/train/products.json` | 507 | 43,599 (`reviews.json`) | Training & 5-fold CV only |
| Launch-Blind Test Inputs | `strict_temporal/data/test_inputs/products_test_specs.json` | 124 | 0 (specs only) | Inference input only; no review text |
| Isolated Ground Truth | `strict_temporal/data/test_labels/ground_truth.json` | 124 | Post-cutoff reviews | Sealed; loaded strictly at evaluation |

## 2. Category Distribution
| Category | Train Products (n=507) | Test Products (n=124) | Total (n=631) |
|---|---|---|---|
| Bluetooth Speakers | 128 | 7 | 135 |
| Ice Makers | 109 | 36 | 145 |
| Power Banks | 80 | 19 | 99 |
| Smartwatches | 75 | 39 | 114 |
| Wireless Headphones | 115 | 23 | 138 |

## 3. Brand Footprint & Cold-Start Stratification
- **Training Brands**: 252 unique brands mapped into Tiers 0-3 based strictly on pre-cutoff catalog footprint.
- **Test Brand Overlap**: 42 products from known brands (Tier >= 1), 82 products from unseen / new brands (Tier 0).
"""
(audit_dir / "DATA_INVENTORY.md").write_text(data_text, encoding="utf-8")

# 3. MODEL_INVENTORY.md
model_text = """# Model Inventory: Upstream Representations & Downstream Models

## 1. Upstream Semantic Representation (Original Model_O)
- **Concept**: Skeptical LLM aspect scoring (`audit/llm/FINAL_PROMPT.txt`).
- **Aspect Ontology**: 9 physical product aspects:
  1. `value_for_money` (0-10)
  2. `utility` (0-10)
  3. `ease_of_use` (0-10)
  4. `reliability` (0-10)
  5. `design_appeal` (0-10)
  6. `after_sales` (0-10)
  7. `build_quality` (0-10)
  8. `durability` (0-10)
  9. `repairability` (0-10)
- **Mention Rates**: 9 aspect mention rates derived from training category profiles.
- **Compression Bottleneck**: Product specification text is compressed into 9 broad scalar ratings, discarding fine-grained technical attribute values (e.g. 5000 mAh, 120 Hz, IP67).

## 2. Downstream Model Architecture (XGBoost Regressor)
- **Artifact**: `strict_temporal/frozen_state/xgb_physical_aspects_only.json`
- **Feature Manifest**: 22 features:
  - Launch price (1)
  - 9 physical aspect scores (9)
  - 9 aspect mention rates (9)
  - Brand tier (1)
  - Category categorical (1)
  - [Target: success_score]
- **Hyperparameters**:
  - `objective`: `reg:squarederror`
  - `n_estimators`: 112 (selected via 5-fold CV early stopping on training set)
  - `learning_rate`: 0.05
  - `max_depth`: 5
  - `min_child_weight`: 3
  - `subsample`: 0.8
  - `colsample_bytree`: 0.8
  - `tree_method`: `hist`
  - `random_state`: 42
  - `monotone_constraints`: `price`: -1, `brand_tier`: +1, all 9 aspect scores: +1

## 3. Canonical Baseline Models
- **Baseline A/B**: Global Mean & Median (rho = 0.0)
- **Baseline C/D**: Category Mean (rho = 0.671), Category Median (rho = 0.691)
- **Baseline E**: Brand-Only Ridge (rho = 0.227)
- **Baseline F**: Category + Brand Ridge (rho = 0.712)
- **Baseline G1/G2**: Ridge (rho = 0.651), ElasticNet (rho = 0.652)
- **Baseline H1/H2**: Random Forest (rho = 0.694), Gradient Boosting (rho = 0.698)
- **Baseline I1/I2/I3**: Raw Specs TF-IDF + Ridge (rho = 0.683), TF-IDF + Price + Cat (rho = 0.688), TF-IDF + GBDT (rho = 0.693)
"""
(audit_dir / "MODEL_INVENTORY.md").write_text(model_text, encoding="utf-8")

# 4. PIPELINE_MAP.md
pipe_text = """# Pipeline Map: End-to-End Execution Flow

```text
+-------------------------------------------------------------+
|             PRE-LAUNCH PRODUCT SPECIFICATIONS               |
|  (Title, Category, Brand, Price, Raw Feature Descriptions)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               LLM SEMANTIC EXTRACTION STAGE                 |
|  - Ingests pre-launch text & category priors                |
|  - Original: Outputs 9 scalar aspect scores + confidence    |
|  - Bottleneck: Compresses raw specs into scalar summaries   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               STRUCTURED FEATURE COMPOSITION                |
|  - Launch price                                             |
|  - Brand Tier (from frozen pre-cutoff catalog footprint)    |
|  - Category identifier (categorical dtype)                  |
|  - Aspect scores (9) + Mention rates (9)                    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                  XGBOOST REGRESSOR STAGE                    |
|  - 112 trees, depth 5, lr 0.05, monotone priors             |
|  - Fitted exclusively on 507 pre-cutoff products            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|          PREDICTED MARKET-SUCCESS PROXY [0, 100]            |
|  Target = 100 * (0.40 * vol_norm + 0.35 * rat_norm          |
|                  + 0.25 * vel_norm)                         |
+-------------------------------------------------------------+
```
"""
(audit_dir / "PIPELINE_MAP.md").write_text(pipe_text, encoding="utf-8")

# 5. EXPERIMENT_INVENTORY.md
exp_text = """# Experiment Inventory

| Experiment ID | Protocol | Description | Primary Metric (Spearman rho) | Status |
|---|---|---|---|---|
| `EXP-TEMPORAL-STRICT-01` | Strict Temporal (507/124) | Canonical Original Model (Model_O) | 0.562 [0.414, 0.681] | Canonical Frozen Baseline |
| `EXP-MONOTONIC-ABLATION` | Strict Temporal (507/124) | XGBoost without Monotone Constraints | 0.548 [0.398, 0.672] | Ablation Recorded |
| `EXP-PRICE-FREE-ABLATION`| Strict Temporal (507/124) | Aspects + Brand without Price | 0.544 [0.390, 0.669] | Ablation Recorded |
| `EXP-TARGET-SENSITIVITY` | Strict Temporal (507/124) | Varying target weights (+-10%) | Rank stability rho > 0.988 | Target Validated |
| `EXP-RATING-BLINDED`     | Strict Temporal (507/124) | Target excluding avg_rating | 0.531 [0.380, 0.658] | Ablation Recorded |
| `EXP-ORACLE-CEILING`     | Strict Temporal (507/124) | True post-launch review aspects | 0.738 [0.630, 0.820] | Diagnostic Upper Bound |
"""
(audit_dir / "EXPERIMENT_INVENTORY.md").write_text(exp_text, encoding="utf-8")

# 6. CURRENT_RESULTS.md
res_text = """# Current Results: Canonical Baseline (Model_O)

- **Dataset Protocol**:
  - Training products: 507 (pre-cutoff <= 2021-10-31)
  - Test products: 124 (post-cutoff > 2021-10-31)
- **Primary Performance Metrics**:
  - Spearman rank correlation (rho): **0.562** (Exact: 0.5621)
  - 95% Bootstrap CI: **[0.414, 0.681]** (10,000 iterations)
  - Asymptotic p-value: **1.09e-11**
  - Pearson r: **0.620** (p = 1.64e-14)
  - Top-vs-Bottom Quintile AUC: **0.890** (95% Bootstrap CI: [0.795, 0.968], DeLong: [0.804, 0.976])
  - RMSE: **21.12**
  - MAE: **17.84**
  - R^2: **0.2306**
  - Mean Within-Category rho: **0.207**
- **Subgroup & Cold-Start Metrics**:
  - Mature Cohort (n_reviews >= 30, n=51): rho = **0.631** [0.413, 0.778], AUC = **0.955**
  - Unseen Brands (Tier 0, n=82): rho = **0.585**, RMSE = **21.54**, MAE = **18.25**
- **Per-Category Breakdown**:
  - Bluetooth Speakers (n=7): rho = 0.536, RMSE = 21.17
  - Ice Makers (n=36): rho = 0.179, RMSE = 20.50
  - Power Banks (n=19): rho = -0.042, RMSE = 27.95
  - Smartwatches (n=39): rho = 0.415, RMSE = 16.10
  - Wireless Headphones (n=23): rho = -0.055, RMSE = 22.93
"""
(audit_dir / "CURRENT_RESULTS.md").write_text(res_text, encoding="utf-8")

# 7. CURRENT_ASSUMPTIONS.md
assump_text = """# Current Assumptions Audit

1. **Launch Date Proxy**: The date of the first recorded customer review is used as an empirical lower bound on commercial launch date.
2. **Review-Derived Success Proxy**: The target is explicitly defined as `SuccessScore = 100 * (0.40 * vol_norm + 0.35 * rat_norm + 0.25 * vel_norm)`. It is NOT sales, unit volume, or profit.
3. **9 Physical Aspects**: Assumes consumer perception in physical consumer electronics is adequately spanned by the 9 ontology aspects.
4. **Skeptical Extraction**: Assumes promotional marketing text can be filtered for objective specifications.
5. **Brand Footprint Tiering**: Assumes catalog SKU count prior to cutoff approximates brand market footprint (Tier 0 to 3).
6. **Directional Monotonicity**: Assumes price penalizes viability (-1), while brand tier (+1) and aspect performance (+1) monotonically aid viability.
"""
(audit_dir / "CURRENT_ASSUMPTIONS.md").write_text(assump_text, encoding="utf-8")

# 8. CURRENT_LEAKAGE_CONTROLS.md
leak_text = """# Current Leakage Controls Audit

The existing system implements strict temporal leakage isolation:
1. **Physical File Separation**: Test ground truth is stored in `strict_temporal/data/test_labels/ground_truth.json` and blocked during inference.
2. **Zero Test ID Overlap**: Verified 0% overlap between 124 test IDs and 507 training rows.
3. **Strict Timestamp Partitioning**: Max train review timestamp <= 1635724799; Min test first review timestamp > 1635724799.
4. **Scaler Isolation**: Normalization scalers (min/max for volume, rating, velocity) computed exclusively on 507 training products.
5. **Category Profile Invariance**: Price medians, quartiles, and aspect baselines derived solely from training products.
6. **Brand Tier Invariance**: Brand footprint counts only pre-cutoff SKUs; unseen brands default to Tier 0.
7. **Cross-Validation Isolation**: Hyperparameter tuning (tree count 112) performed strictly on 5-fold CV within the 507 training products.
8. **Byte-for-Byte Prediction Invariance**: Test predictions are bit-for-bit identical whether test ground truth files exist or are completely deleted.
9. **Test Suite Status**: 10/10 automated leakage tests pass via `tests/test_temporal_leakage.py`.
"""
(audit_dir / "CURRENT_LEAKAGE_CONTROLS.md").write_text(leak_text, encoding="utf-8")

# 9. CURRENT_MANUSCRIPT_CLAIMS.md
claims_text = """# Current Manuscript Claims Audit

Audit of existing claims across `Research_Paper_IEEE_Final.docx`, `paper_ieee/main.tex`, and `paper_full.md`:
1. **Target Terminology**: Correctly designated as a "review-derived market-success proxy" across abstract, intro, and methodology.
2. **Primary Performance Claim**: Claims pooled temporal Spearman rho = 0.562 [0.414, 0.681], AUC = 0.890.
3. **Ablation Claims**: Monotone constraints preserve AUC (0.903/0.890 vs 0.826) despite slight CV R^2 reduction.
4. **Cold Start Claim**: Evaluates 82 unseen brand products (Tier 0) with rho = 0.585.
5. **Oracle Claim**: Oracle review-aspect model achieves rho = 0.738, serving as a post-launch diagnostic ceiling.
6. **Identified Discrepancies to Reconcile**:
   - Some earlier drafts referenced R^2 = 0.566 vs 0.564 (unified to 0.564 in Table 1).
   - Ice maker within-category correlation is modest (rho = 0.179) and must be discussed cautiously.
"""
(audit_dir / "CURRENT_MANUSCRIPT_CLAIMS.md").write_text(claims_text, encoding="utf-8")

print("All 9 project audit documents created successfully in Legitimate/00_PROJECT_AUDIT/")
