# Statistical Precision, Effect Size, and Calibration Audit

**Auditor:** Senior Statistician and ML Evaluation Auditor  
**Date:** 2026-10-05  
**Evaluation Scope:** Strict Launch-Blind Temporal Holdout ($n = 124$)  

---

## 1. Precision & Sample-Size Analysis

Rather than conducting uninformative post-hoc statistical power calculations, we directly analyze the **confidence interval precision** across evaluated sample cohorts:

| Cohort Evaluated | Sample $n$ | Spearman $\rho$ | 95% Confidence Interval | CI Width ($\Delta$) | Precision Assessment |
|---|:---:|:---:|:---:|:---:|---|
| **Pooled Strict Test** | **124** | **0.562** | **[0.414, 0.681]** | **0.267** | **High Precision**: Lower bound ($0.414$) clears moderate effect floor ($0.30$) with high certainty. |
| **Mature Cohort ($N \ge 30$)** | **51** | **0.631** | **[0.413, 0.778]** | **0.365** | **Adequate Precision**: Lower bound ($0.413$) demonstrates strong signal on stable products. |
| Smartwatches | 39 | 0.415 | [0.095, 0.657] | 0.562 | Moderate Precision: Confirms positive effect, but wide bounds. |
| Ice Makers | 36 | 0.179 | [-0.179, 0.495] | 0.674 | Indeterminate: CI spans zero; consistent with boundary condition. |
| Wireless Headphones | 23 | -0.055 | [-0.478, 0.388] | 0.866 | **Low Precision**: Sample size insufficient to resolve small effects. |
| Power Banks | 19 | -0.042 | [-0.509, 0.444] | 0.953 | **Low Precision**: Wide CI spanning $\pm 0.50$. |
| Bluetooth Speakers | 7 | 0.536 | [-0.414, 0.927] | 1.341 | **Statistically Uninterpretable**: $n=7$ yields essentially unconstrained CI. |

### Key Precision Finding:
The pooled sample ($n = 124$) and mature cohort ($n = 51$) possess sufficient sample size to establish that the lower bound of performance is $> 0.41$. However, individual category splits below $n = 30$ suffer from wide confidence intervals and must not be presented as definitive individual category conclusions.

---

## 2. Effect Size vs. Statistical Significance

The paper reports an extremely small $p$-value:
$$p = 1.09 \times 10^{-11}$$

### Hostile Reviewer Caveat:
> *"A p-value of $10^{-11}$ merely rejects the null hypothesis that true ranking concordance is exactly zero; it does not imply that the model is highly accurate in an absolute sense."*

### Auditor Evaluation:
1. **Rank Variance Explained:**  
   $$\rho = 0.562 \implies \rho^2 = 0.316 \quad (\mathbf{31.6\%}\text{ of rank variance explained})$$
   Roughly one-third of the rank variance in post-launch success is explained by pre-launch specifications alone. The remaining two-thirds are governed by post-launch factors outside the spec sheet (marketing expenditure, advertising bids, influencer campaigns, packaging, customer service execution, firmware updates, and competitive launches).
2. **Practical Interpretation:**  
   The model is an effective **pre-production screening filter** across candidate concepts or SKUs, but not a deterministic oracle for single-product sales forecasts. The paper's text must avoid equating small $p$-values with perfect prediction.

---

## 3. Calibration and Absolute Prediction Error

The model outputs a continuous `predicted_viability` score bounded in $[0.0, 100.0]$.

### Metric Audit on Strict Temporal Test Set ($n = 124$):
- **Root Mean Squared Error (RMSE):** $21.12$ points
- **Mean Absolute Error (MAE):** $17.84$ points
- **Out-of-Sample $R^2$:** $0.2306$
- **Target Distribution Standard Deviation:** $\sigma_y = 24.08$ points

### Interpretation:
1. An RMSE of $21.12$ against a label standard deviation of $24.08$ corresponds to a modest error reduction ($\approx 12.3\%$ over predicting the mean).
2. The out-of-sample $R^2 = 0.231$ is substantially lower than the training cross-validation $R^2 \approx 0.550$, reflecting the natural difficulty of forward-in-time generalization across distinct product cohorts.
3. **Core Conclusion:** The system functions primarily as a **rank-ordering and tier-separation engine** ($\rho = 0.562$, Quintile $\text{AUC} = 0.890$), rather than an absolute point-forecast regressor. The manuscript should explicitly guide practitioners to interpret predictions via **relative percentile ranks and quintiles** rather than raw point scores.
