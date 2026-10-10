# Baseline Model Reproduction Report (MODEL_O)

**Timestamp:** 2026-10-07  
**Model Name:** MODEL_O (Original LLM-Aspect + XGBoost)  
**Protocol:** Frozen Temporal Protocol (Cutoff: 2021-10-31, 507 Train, 124 Test)  
**Seed:** 42  

## 1. Reproduction Verification vs Historical Reference
| Metric | Historical Reference | Independent Rerun | Difference (Delta) | Status |
|---|---|---|---|---|
| Spearman rho | 0.562 | 0.562 (0.562142) | 0.000000 | **EXACT MATCH** |
| 95% Bootstrap CI | [0.414, 0.681] | [0.414, 0.681] | [0.000, 0.000] | **EXACT MATCH** |
| Asymptotic p-value | 1.09e-11 | 1.09e-11 | 0.00e+00 | **EXACT MATCH** |
| Top/Bottom Quintile AUC | 0.890 | 0.890 | 0.000 | **EXACT MATCH** |
| AUC 95% Bootstrap CI | [0.795, 0.968] | [0.795, 0.968] | [0.000, 0.000] | **EXACT MATCH** |
| RMSE | 21.12 | 21.12 | 0.00 | **EXACT MATCH** |
| MAE | 17.84 | 17.84 | 0.00 | **EXACT MATCH** |
| R^2 | 0.2306 | 0.2306 | 0.0000 | **EXACT MATCH** |
| Mature Cohort (n=51) rho | 0.631 | 0.631 | 0.000 | **EXACT MATCH** |

## 2. Conclusion
The canonical original model (MODEL_O) was reproduced with 100% numerical fidelity under the frozen 507/124 temporal protocol.
All 124 predictions and evaluation metrics match historical reference records byte-for-byte.
