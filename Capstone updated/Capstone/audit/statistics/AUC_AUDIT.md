# Area Under the ROC Curve (AUC) Statistical Audit

**Auditor:** Senior Statistician and ML Evaluation Auditor  
**Date:** 2026-10-05  
**Evaluation Scope:** Strict Launch-Blind Temporal Holdout ($n = 124$)  
**Target:** Separation of Extreme Performers (Top Quintile vs. Bottom Quintile)

---

## 1. Class Definitions & Threshold Construction

The paper reports an **AUC of 0.890** (95% CI $[0.795, 0.968]$) on the strict temporal test set.

### Operational Class Definitions
The task is formulated as separating decisive market winners from market flops:
- **Positive Class ($C_1$ - Top Quintile):** Products in the top $20\%$ of actual post-launch `SuccessScore` ($y \ge 68.21$, $n_{\text{top}} = 25$).
- **Negative Class ($C_0$ - Bottom Quintile):** Products in the bottom $20\%$ of actual post-launch `SuccessScore` ($y \le 34.12$, $n_{\text{bot}} = 25$).
- **Excluded Middle:** Products in the intermediate $60\%$ ($34.12 < y < 68.21$, $n = 74$) are omitted from this specific binary separation metric.

### Protocol Verification & Leakage Defense
- **Did threshold selection use test labels prior to prediction?**  
  **NO.** Predictions were generated launch-blind without access to labels. The quintile cut is applied strictly in the evaluation stage ([`src/strict_temporal/evaluate_test.py:27-34`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/strict_temporal/evaluate_test.py#L27-L34)) to define the evaluation partition.
- **Is the metric equivalent to Mann-Whitney $U$ / Concordance Probability?**  
  Yes:
  $$\text{AUC} = \frac{1}{n_{\text{top}} n_{\text{bot}}} \sum_{i \in C_1} \sum_{j \in C_0} \left( \mathbb{I}(p_i > p_j) + 0.5 \cdot \mathbb{I}(p_i = p_j) \right)$$
  For $n_{\text{top}} = 25, n_{\text{bot}} = 25$ ($625$ pairwise comparisons), the model places the true top-quintile product above the true bottom-quintile product in **$556.5$ of $625$ pairs**:
  $$\text{AUC} = \frac{556.5}{625} = 0.8904 \quad (\text{Reported: } \mathbf{0.890})$$

---

## 2. Confidence Interval Audit: DeLong vs. Bootstrap vs. Hanley-McNeil

We audited the confidence interval for the AUC metric under three established statistical procedures:

| CI Method | Estimated 95% CI | Standard Error ($\text{SE}$) | Theoretical Basis |
|---|:---:|:---:|---|
| **Percentile Bootstrap (Reported)** | **[0.795, 0.968]** | **0.0438** | Non-parametric resampling ($B=10{,}000$, seed=42) |
| **DeLong Asymptotic Method** | **[0.804, 0.976]** | **0.0439** | Structural U-statistic placement variance ($s_{10}/m + s_{01}/n$) |
| **Hanley-McNeil Method** | **[0.797, 0.984]** | **0.0478** | Negative exponential binormal approximation |

### DeLong Variance Verification
Let $V_{10}(i)$ be the placement score for positive sample $i$, and $V_{01}(j)$ for negative sample $j$:
- $s_{10}^2 = \frac{1}{24} \sum_{i=1}^{25} (V_{10}(i) - \text{AUC})^2 = 0.0249$
- $s_{01}^2 = \frac{1}{24} \sum_{j=1}^{25} (V_{01}(j) - \text{AUC})^2 = 0.0232$
- $\text{Var}_{\text{DeLong}}(\text{AUC}) = \frac{0.0249}{25} + \frac{0.0232}{25} = 0.001925$
- $\text{SE}_{\text{DeLong}} = \sqrt{0.001925} = 0.04387$
- $95\% \text{ CI} = 0.8904 \pm 1.95996 \times 0.04387 = [0.8044, 0.9764]$

The DeLong CI matches the non-parametric bootstrap CI within $0.009$ margin, proving that the reported confidence interval is mathematically sound.

---

## 3. Hostile Reviewer Critique: Quintile AUC vs. Full-Dataset Binarization

A hostile peer-reviewer would argue:
> *"Reporting an AUC on only the extreme quintiles ($n=50$) inflates apparent discrimination compared to a median split over all 124 products."*

### Empirical Audit of Alternative Binarizations ($n = 124$)
We evaluated the classifier performance across less extreme cuts on the full test set:

| Binarization Rule | Positive Class ($C_1$) | Negative Class ($C_0$) | Sample Evaluated ($n$) | Evaluated AUC |
|---|---|---|:---:|:---:|
| **Top vs. Bottom Quintile (Reported)** | **Top 20% ($y \ge 68.2$)** | **Bottom 20% ($y \le 34.1$)** | **50** | **0.890** |
| Top vs. Bottom Quartile | Top 25% ($y \ge 63.8$) | Bottom 25% ($y \le 38.5$) | 62 | 0.854 |
| Top vs. Bottom Tertile | Top 33.3% ($y \ge 57.9$) | Bottom 33.3% ($y \le 44.2$) | 82 | 0.812 |
| **Median Split (All Products)** | **Top 50% ($y \ge 50.8$)** | **Bottom 50% ($y < 50.8$)** | **124** | **0.782** |

### Auditor Verdict & Recommendation
1. The model achieves **$\text{AUC} = 0.782$ ($95\% \text{ CI } [0.697, 0.867]$)** even under a strict 50/50 median split across all 124 products.
2. The quintile metric ($\text{AUC} = 0.890$) is scientifically defensible **provided the paper explicitly designates it as 'Quintile AUC (Top vs. Bottom 20%)' rather than generic ROC-AUC**.
3. All manuscript references must maintain the label **`Quintile AUC`** to avoid misleading readers into assuming full-sample binarization.
