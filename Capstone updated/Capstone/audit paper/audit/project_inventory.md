# Project Inventory — Phase 1 Inspection Report

**Generated:** 2026-10-01  
**Auditor:** Automated Audit System  
**Status:** INSPECTION COMPLETE — DO NOT MODIFY ORIGINALS YET

---

## 1. Dataset Files

### Raw Data (`data/raw/`)
| File | Size | Description |
|---|---|---|
| amazon_candidates_Appliances.jsonl | 1.0 MB | Raw candidate products for Appliances |
| amazon_candidates_Cell_Phones_and_Accessories.jsonl | 3.8 MB | Raw candidates CPA |
| amazon_candidates_Electronics.jsonl | 8.9 MB | Raw candidates Electronics |
| amazon_reviews_raw.jsonl | 52.3 MB | Raw Amazon reviews |
| amazon_selected.json | 1.7 MB | Selected Amazon products |
| play_apps.jsonl | 128 KB | Google Play apps (NOT used in final) |
| play_reviews_raw.jsonl | 45.4 MB | Google Play reviews (NOT used in final) |
| reddit_context_raw.json | 2 B | Empty Reddit context |

### Final Data (`data/final/`)
| File | Size | Description |
|---|---|---|
| products_physical.json | 1.2 MB | **640 products** across 5 categories |
| reviews_physical.json | 26.9 MB | **43,599 reviews** |
| products_app.json | 2 B | Empty (apps removed) |
| reviews_app.json | 2 B | Empty (apps removed) |
| manifest.json | 795 B | Dataset manifest |
| reddit_context.json | 305 KB | Reddit context data |
| validation_report.txt | 1 KB | Data validation report |

### Extracted Data (`data/extracted/`)
| File | Size | Description |
|---|---|---|
| aspect_scores.jsonl | 44.9 MB | **78,394 extraction records** |
| aspect_scores_backup_pre_gemma_purge.jsonl | 29.3 MB | Pre-Gemma purge backup |
| aspect_scores_gemma_archive.jsonl | 4.8 MB | Archived Gemma extractions |
| category_profiles.json | 47.8 KB | Category statistical profiles |
| failed_reviews.jsonl | 116 KB | **470 failed extraction records** |
| features_physical.parquet | 88.9 KB | **631-row feature matrix** |
| labels.json | 214 KB | **640 product labels** |

---

## 2. Dataset Versions and Counts

### Final Dataset
- **Initial products:** 640
- **Categories:** 5 (bluetooth_speakers, ice_makers, power_banks, smartwatches, wireless_headphones)
- **Reviews:** 43,599
- **Fraud-filtered (suspect):** 9 products removed
- **Training-eligible:** 631 products

### Per-Category Breakdown
| Category | Products (raw) | Products (clean) | Reviews |
|---|---|---|---|
| bluetooth_speakers | 136 | 135 | 12,225 |
| ice_makers | 147 | 145 | 6,988 |
| power_banks | 103 | 99 | 3,932 |
| smartwatches | 116 | 114 | 3,981 |
| wireless_headphones | 138 | 138 | 16,473 |

### Suspect Products (9 total)
| UID | Category | Reason |
|---|---|---|
| amzp_B0C3B516G9 | bluetooth_speakers | burst |
| amzp_B09MTD2MQ6 | power_banks | burst |
| amzp_B0B7RGDLW3 | power_banks | extreme_j |
| amzp_B0CG5H76RD | power_banks | extreme_j |
| amzp_B0C8XZ8JYK | power_banks | burst |
| amzp_B0BWVD7KZG | smartwatches | burst |
| amzp_B0BLLRSZXM | smartwatches | extreme_j |
| amzp_B0CCJ8JHY6 | ice_makers | burst |
| amzp_B0BYZ8SB84 | ice_makers | burst |

---

## 3. Target Construction

**Formula:** `success = 100 * (0.40 * volume_norm + 0.35 * rating_norm + 0.25 * velocity_norm)`

- **volume:** log1p(review_count), min-max within category
- **rating:** avg_rating, min-max within category
- **velocity:** review_count / max(months_between(first_review, latest_review), 1), min-max within category
- **Weights:** 0.40 / 0.35 / 0.25 (DESIGN CHOICE, not empirically derived)

---

## 4. Features (26 columns in feature matrix)

### Metadata Features
| Feature | Description | Pre-launch available? |
|---|---|---|
| price | Product price | YES |
| avg_rating | Average star rating | NO (post-launch) |
| rating_count_log | log1p(rating_count) | NO (post-launch) |
| review_velocity | reviews/month | NO (post-launch) |
| brand_tier | Ordinal brand recognition (0-3) | NEEDS AUDIT |
| category | Product category | YES |

### Aspect Score Features (9 aspects x 2 = 18 features)
- Mean aspect score per product (from extraction)
- Mention rate per aspect
- Aspects: value_for_money, utility, ease_of_use, reliability, design_appeal, after_sales, build_quality, durability, repairability

### Leaky Columns (removed for headline model)
- avg_rating, rating_count_log, review_velocity, install_count_log, days_since_update

---

## 5. Train/Test Splits

### Random Holdout
- **Holdout UIDs file:** 60 UIDs
- **Actually bridged/evaluated:** 59 products (1 failed bridging)
- **Training set:** 631 - 59 = 572 (approximately)

### Temporal Split (cutoff: 2021-10-31 based on first_review_ts)
- **Train (first_review <= cutoff):** 510 products
- **Test (first_review > cutoff):** 130 products
- **After fraud filtering:** train ~505, test ~125 (approximate)
- **Actually evaluated:** 66 temporal holdout products

---

## 6. LLM Extraction Configuration

### Providers (from config/llm_providers.yaml)
| Provider | Keys | Status |
|---|---|---|
| Cerebras | 8 keys | Active |
| Gemini | 8 keys | Active |
| Groq | 8 keys | Active |
| Mistral | 8 keys | Active |
| SambaNova | 7 keys | Active |
| Ollama (gemma3:4b) | Local | Evaluated but excluded |
| GitHub | 0 keys | Not used |
| NVIDIA | 0 keys | Not used |

### Extraction Stats
- **Total extraction records:** 78,394
- **Failed reviews:** 470
- **Extraction success rate:** ~99.4%
- **Minimum confidence threshold:** 0.3

---

## 7. Models

### Trained Models (models/)
| Model | Description |
|---|---|
| xgb_physical.json | Full-feature XGBoost (leaky) |
| xgb_physical_aspects_only.json | Headline model (aspects + price + brand + category) |
| brand_tier_map.json | Brand to tier mapping |

### Hyperparameters
- n_estimators: 600, learning_rate: 0.05, max_depth: 5
- min_child_weight: 3, subsample: 0.8, colsample_bytree: 0.8
- tree_method: hist, enable_categorical: true, seed: 42

### Monotonic Constraints
- price: -1 (non-increasing)
- All aspects + brand_tier: +1 (non-decreasing)

---

## 8. Evaluation Results (ACTUAL from data files)

### CRITICAL: ACTUAL vs PAPER CLAIMS

### Cross-Validation (n=631, 5-fold, seed 42)
| Model | R2 | RMSE | MAE |
|---|---|---|---|
| Full | 0.892 | 5.76 | 4.34 |
| Aspects-only (headline) | 0.595 | 11.17 | 8.65 |

### Random Holdout (ACTUAL vs PAPER)
| Metric | ACTUAL Value | Paper Claims | MATCH? |
|---|---|---|---|
| n | **59** | 118 | NO |
| Spearman rho | **0.317** | 0.529 | NO |
| AUC (top/bottom quintile) | **0.743** | 0.903 | NO |
| rho 95% CI | **[0.059, 0.543]** | [0.377, 0.654] | NO |
| AUC 95% CI | **[0.507, 0.931]** | not reported | N/A |

### Temporal Holdout (ACTUAL vs PAPER)
| Metric | ACTUAL Value | Paper Claims | MATCH? |
|---|---|---|---|
| n | **66** | 125 | NO |
| Spearman rho | **0.545** | 0.590 | NO |
| AUC | **0.901** | 0.942 | NO |
| rho 95% CI | **[0.352, 0.694]** | [0.486, 0.696] | NO |

### Algorithm Comparison (5-fold CV, aspects-only, n=631)
| Algorithm | R2 | RMSE | AUC |
|---|---|---|---|
| XGBoost | 0.564 | 11.39 | 0.983 |
| Gradient Boosting | 0.550 | 11.59 | 0.983 |
| Random Forest | 0.532 | 11.81 | 0.979 |
| MLP Regressor | 0.490 | 12.30 | 0.966 |
| SVR (RBF) | 0.421 | 13.12 | 0.942 |
| Ridge Regression | 0.368 | 13.72 | 0.921 |

---

## 9. CRITICAL DISCREPANCY ANALYSIS

The paper reports results that do not match any existing data file:

1. **Holdout n=118 vs actual n=59:** Paper claims 118, data has 59-60.
2. **Holdout rho=0.529 vs actual rho=0.317:** Paper inflated by 67%.
3. **Holdout AUC=0.903 vs actual AUC=0.743:** Paper inflated by 22%.
4. **Temporal n=125 vs actual n=66:** Paper claims 125, data has 66.
5. **Temporal rho=0.590 vs actual rho=0.545:** Paper inflated.
6. **Temporal AUC=0.942 vs actual AUC=0.901:** Paper inflated.
7. **CI conflict:** Abstract [0.31,0.61] vs validation [0.377,0.654] vs actual [0.059,0.543].

The verified result wins (Rule 4). All paper claims must use actual data.

---

## 10. Scripts and Their Purposes
| Script | Purpose |
|---|---|
| holdout_validation.py | Holdout evaluation |
| retro_validation.py | Retrospective bridging validation |
| ml_algorithm_comparison.py | Algorithm benchmarking |
| make_paper_figures.py | Generate paper figures |
| make_algo_figures.py | Generate algorithm figures |
| headline_cis.py | Bootstrap confidence intervals |
| baseline_check.py | Price baseline |

---

## 11. Summary

The project has a sound architecture but the paper contains significant numerical inflation.
All results must be recomputed from actual data files and the paper rewritten around verified numbers.
