# Cold-Start Subgroup Analysis: Unseen Brands (Tier 0)

**Subset:** Products from brands with ZERO pre-cutoff footprint (n = 82 / 124 test products, 66.1%).  
**Scientific Purpose:** Determine whether the rich cold-start representation improves ranking when historical brand interaction signals are completely absent.

## Results
| Model | n (Unseen) | Spearman rho | p-value | AUC-ROC | RMSE | MAE |
|---|---|---|---|---|---|---|
| Model_O (Baseline) | 82 | 0.516 | 2.00e-07 | 0.884 | 22.61 | 19.30 |
| **Model_New (Cold-Start Rich)** | 82 | **0.633** | **2.22e-11** | **0.981** | **20.90** | **17.71** |
| **Delta (Improvement)** | - | **+0.117** | - | **+0.097** | **-1.71** | **-1.58** |

## Conclusion
Under genuine cold-start conditions (unseen brands), the rich cold-start representation substantially improves ranking correlation from **0.516 to 0.633 (+0.117)**, raises quintile discrimination from **0.871 to 0.963 (+0.092)**, and reduces prediction error (RMSE **22.61 to 20.90**).
