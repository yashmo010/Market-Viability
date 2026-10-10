# Pooled vs. Within-Category Statistical Decomposition

**Auditor:** Senior Statistician and ML Evaluation Auditor  
**Date:** 2026-10-05  
**Evaluation Scope:** Strict Launch-Blind Temporal Holdout ($n = 124$)  

---

## 1. The Statistical Discrepancy

A central finding of this evaluation audit is the contrast between pooled and within-category performance:

$$\text{Pooled Spearman } \rho = \mathbf{0.562} \quad (p = 1.09 \times 10^{-11})$$
$$\text{Arithmetic Mean Within-Category } \rho = \mathbf{0.207}$$
$$\text{Fisher-Weighted Within-Category } \rho = \mathbf{0.189}$$

A hostile peer-reviewer would immediately challenge this result:
> *"Does the high pooled correlation ($\rho = 0.562$) merely reflect the model predicting broad category averages rather than genuine product-level discrimination?"*

---

## 2. Empirical Variance & Correlation Decomposition

To answer this challenge rigorously, we decomposed both model predictions $\hat{y}_i$ and actual outcomes $y_i$ into their **between-category component** (category group mean $\bar{y}_c$) and **within-category residual** ($y_{i,c}^* = y_{i,c} - \bar{y}_c$):

$$\text{Var}(\hat{y}) = \text{Var}(\bar{\hat{y}}_c) + \text{Var}(\hat{y} - \bar{\hat{y}}_c)$$
$$\text{Var}(y) = \text{Var}(\bar{y}_c) + \text{Var}(y - \bar{y}_c)$$

### Variance Shares
- **Predicted Viability Variance:**  
  $$\text{Between Categories} = \mathbf{74.3\%}, \quad \text{Within Categories} = \mathbf{25.7\%}$$
- **Actual Success Score Variance:**  
  $$\text{Between Categories} = \mathbf{63.0\%}, \quad \text{Within Categories} = \mathbf{37.0\%}$$

### Correlation Decomposition
1. **Category Mean Alignment (Macro Signal):**  
   The Pearson correlation between predicted category mean and actual category mean across the 5 categories is:
   $$r_{\text{between}} = \mathbf{0.8549}$$
   The model accurately identifies which categories enjoy higher overall post-launch review traction (e.g. smartwatches and ice makers vs. power banks).
2. **Demeaned Within-Category Ranking (Micro Signal):**  
   After completely subtracting category means from both predictions and actual labels, the residual correlation across all 124 products is:
   $$\rho_{\text{within-demeaned}} = \mathbf{0.1770} \quad (p = 0.0492)$$
   $$r_{\text{within-demeaned}} = \mathbf{0.1135} \quad (p = 0.2094)$$

---

## 3. Category-by-Category Granular Audit

Recorded in [`audit/statistics/WITHIN_CATEGORY_RESULTS.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/statistics/WITHIN_CATEGORY_RESULTS.csv):

| Category | Sample $n$ | Spearman $\rho$ | 95% Fisher CI | $p$-value | Quintile AUC | RMSE | Statistical Reliability |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Smartwatches** | 39 | **0.415** | [0.095, 0.657] | **0.0086** | **0.844** | 16.10 | **Statistically Robust** ($n \ge 30, p < 0.01$) |
| **Ice Makers** | 36 | 0.179 | [-0.179, 0.495] | 0.2959 | 0.688 | 20.50 | Moderate ($n \ge 30$, low spec expressiveness) |
| **Wireless Headphones** | 23 | -0.055 | [-0.478, 0.388] | 0.8017 | 0.540 | 22.93 | Underpowered ($n < 30$, wide CI) |
| **Power Banks** | 19 | -0.042 | [-0.509, 0.444] | 0.8638 | 0.438 | 27.95 | Underpowered ($n < 30$, technological drift) |
| **Bluetooth Speakers** | 7 | 0.536 | [-0.414, 0.927] | 0.2152 | N/A | 21.17 | **Severely Underpowered** ($n = 7$, uninterpretable) |

---

## 4. Auditor Conclusion & Scientific Synthesis

1. **Dual-Scale Predictive Power:** The model functions simultaneously at two distinct scales:
   - **Cross-Category Sorting ($r = 0.855$):** Successfully captures category-level base rates and market expansion.
   - **Intra-Category Discrimination ($\rho = 0.177$ to $0.415$):** Operates effectively in spec-rich, highly articulated categories (Smartwatches: $\rho = 0.415, p = 0.0086$), but struggles in categories with flat, non-experiential spec sheets (Ice Makers: $\rho = 0.179$) or rapid hardware protocol drift (Power Banks: $\rho = -0.042$).
2. **Manuscript Language Requirement:** The manuscript is commendable for already stating that *"within-category $\rho$ is the stricter measure."* However, the paper must explicitly caution readers against drawing conclusions from the $n = 7$ Bluetooth speaker cohort and clearly report that the demeaned within-category rank correlation across all items is $\rho \approx 0.18$ ($p \approx 0.049$).
