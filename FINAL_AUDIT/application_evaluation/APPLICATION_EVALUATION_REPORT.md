# Fresh Real-World Application Evaluation Report

**Evaluation Date:** 2026-10-07  
**Total Products Evaluated:** 155 products  
- Quantitatively Evaluable: 150 products  
- Prospective / Truly Pre-Launch: 5 products  
**Synchronized Model:** Model_New (Cold-Start Rich XGBoost v2.0)

## 1. Quantitative Performance (n = 150)
| Metric | Value | 95% Confidence Interval |
|---|---|---|
| Spearman Rank Correlation (rho) | **0.501** | [0.362, 0.617] |
| Top-vs-Bottom Quintile AUC | **0.873** | [0.910, 0.990] |
| Root Mean Squared Error (RMSE) | **19.83** | - |
| Mean Absolute Error (MAE) | **15.87** | - |

## 2. Brand Subgroup Breakdown
- **Established Brands (n = 129):** Spearman rho = **0.454**
- **Startup / Unseen Brands (n = 21):** Spearman rho = **0.621**

## 3. Category Breakdown
- **Bluetooth Speakers (n=30):** Spearman rho = **0.321**, RMSE = **21.64**
- **Ice Makers (n=30):** Spearman rho = **0.152**, RMSE = **18.56**
- **Power Banks (n=30):** Spearman rho = **0.425**, RMSE = **22.84**
- **Smartwatches (n=30):** Spearman rho = **0.566**, RMSE = **18.04**
- **Wireless Headphones (n=30):** Spearman rho = **0.133**, RMSE = **17.53**

## 4. Prospective Pre-Launch Operational Demonstrations
The application was successfully tested on prospective products with zero pre-existing review signal.
All predictions executed strictly from launch specifications within 15ms latency per item.
