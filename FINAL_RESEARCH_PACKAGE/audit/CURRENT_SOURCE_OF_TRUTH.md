# CURRENT SOURCE OF TRUTH (SOT) SPECIFICATION
**Autonomous Publication Engineering System — Current Modified Project Only**  
**Date of Audit & Freeze**: October 2026  
**Status**: ACTIVE / FROZEN EMPIRICAL TRUTH  

---

## 1. Zero Backward Contamination Mandate

This document establishes the sole empirical source of truth for the project:
**"Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging"**

Under no circumstances are historical benchmark numbers, obsolete classification matrices, discarded feature counts, or old project artifacts imported into the current study. The historical codebase (`Capstone updated/Capstone`) remains strictly preserved and byte-for-byte quarantined as a known-issue reference only.

---

## 2. Source-of-Truth Hierarchy

When evaluating claims, figures, tables, or documentation, the following hierarchy strictly governs:

```
Level 1: CURRENT RAW DATA
         - 507 Training Products (strict_temporal/data/train/products.json)
         - 124 Strictly Post-Cutoff Products (strict_temporal/data/test_inputs/products_test_specs.json)
         - Ground Truth Proxy Labels (strict_temporal/data/test_labels/ground_truth.json)
         - External Real-World Cohort (155 Amazon 2022-2024 Products)

Level 2: CURRENT EXECUTABLE CODE
         - Feature Extraction & Bridging (Legitimate/test_extraction_logic.py)
         - Execution & Verification (Legitimate/save_promoted_model.py, run_statistical_tests.py)
         - Application Inference Engine (Legitimate/application_sync/backend/inference.py)

Level 3: CURRENT FINAL MODEL + CONFIG
         - Promoted Checkpoint: Legitimate/08_FINAL_MODEL/xgb_coldstart_rich_promoted.json
         - Feature Manifest (24 features): Legitimate/08_FINAL_MODEL/feature_manifest.json

Level 4: CURRENT FINAL PREDICTIONS
         - Frozen Test Predictions (n=124): Legitimate/08_FINAL_MODEL/test_predictions.csv
         - External Test Predictions (n=155): Legitimate/application_evaluation/external_evaluation_dataset.json

Level 5: CURRENT FINAL STATISTICAL OUTPUTS
         - Master Numerical Ground Truth: FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json

Level 6: CURRENT EXPERIMENT LEDGER
         - Controlled Ablation & Candidates: Legitimate/EXPERIMENT_LEDGER.csv

Level 7: CURRENT APPLICATION
         - Interactive Dashboard: Legitimate/application_sync/

Level 8: CURRENT MANUSCRIPT / FIGURES / TABLES
         - IEEE Paper: Legitimate/09_MANUSCRIPT/FINAL_MANUSCRIPT.docx / .pdf / .md
         - Publication Figures: Legitimate/figures/ (Figs 1–7)
         - Publication Tables: Legitimate/tables/ (Tables I–IX)
```

---

## 3. Canonical Scientific Facts & Parameters

| Parameter | Current Verified Value | Empirical Source |
|---|---|---|
| **Title** | *Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging* | Manuscript & Code |
| **Temporal Cutoff** | October 31, 2021, 23:59:59 UTC | `strict_temporal/frozen_state` |
| **Training Products ($n$)** | 507 products | `train_features.parquet` |
| **Temporal Holdout ($n$)** | 124 strictly post-cutoff launch-blind products | `products_test_specs.json` |
| **Total Core Products ($N$)** | 631 unique products | Train + Test |
| **External Evaluation ($n$)** | 155 real-world launch products (2022–2024) | `external_evaluation_dataset.json` |
| **Canonical Categories** | 5 (Bluetooth speakers, Ice makers, Power banks, Smartwatches, Wireless headphones) | Taxonomy Manifest |
| **Air Fryer Occurrence** | **0** (Permanently purged from core taxonomy) | Full codebase audit |
| **Target Variable** | Review-derived Market-Success Proxy (0–100 continuous score) | Ground truth labels |
| **Promoted Architecture** | LLM Aspect Bridging + Specification Density $\to$ Monotonic Constrained XGBoost | `xgb_coldstart_rich_promoted.json` |
| **Feature Count** | **24 features** (1 price + 9 aspect scores + 9 mention rates + 1 tier + 1 category + 3 density) | `feature_manifest.json` |

---

## 4. Frozen Core Metrics (Holdout $n=124$)

| Model Configuration | Spearman $\rho$ | 95% Bootstrap CI | Spearman $p$ (Asymptotic) | Extreme-Group AUC | RMSE | MAE |
|---|---|---|---|---|---|---|
| **Controlled Baseline** | 0.5623 | [0.4140, 0.6812] | $1.08 \times 10^{-11}$ | 0.8904 | 21.12 | 17.83 |
| **Promoted (Model_New)** | **0.6722** | **[0.5495, 0.7620]** | **$1.25 \times 10^{-17}$** | **0.9712** | **19.75** | **16.66** |
| **Paired Improvement ($\Delta$)** | **+0.1099** | **[+0.0485, +0.1833]** | **$p = 0.0004$ (Permutation)** | **+0.0808** | **-1.37** | **-1.17** |

*Note on $p$-values*: The asymptotic Spearman rank correlation test yields $p = 1.25 \times 10^{-17}$ ($H_0: \rho = 0$). The paired model-comparison non-parametric permutation test yields $p = 0.0004$ ($H_0: \Delta\rho \le 0$, 10,000 paired sign-flips). Both tests are mathematically distinct and never conflated.

---

## 5. Frozen Subgroup Metrics

- **Unseen Brands / Cold-Start ($n=90$, Tier 0)**:
  - Baseline $\rho = 0.5155$, AUC = 0.8843
  - Promoted $\rho = 0.6328$, AUC = 0.9815 ($\Delta\rho = +0.1173$)
- **External Real-World Application Cohort ($n=155$, 2022–2024 launches)**:
  - Spearman $\rho = 0.6120$ (95% CI: [0.5042, 0.7021], $p = 1.84 \times 10^{-17}$)
  - Directional Discrimination AUC = 0.8840
  - Mean Absolute Error = 14.82 pts
