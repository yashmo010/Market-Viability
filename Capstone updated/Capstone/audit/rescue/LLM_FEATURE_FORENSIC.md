# Forensic Audit of LLM-Derived Aspect Features

**Document**: `audit/rescue/LLM_FEATURE_FORENSIC.md`  
**Data Reference**: [`audit/rescue/LLM_FEATURE_FORENSIC.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/rescue/LLM_FEATURE_FORENSIC.csv)  
**Sample**: Strict Temporal Holdout ($N=124$, Cutoff October 31, 2021)  

---

## 1. Executive Summary of Forensic Findings

A rigorous inspection of the 9 LLM-derived aspect features reveals that their failure to improve pre-launch forecasting is driven by three fundamental statistical defects:

1. **Massive Category Collinearity (Category Proxies)**:
   Aspect scores are heavily determined by product category ($F = 68 \text{ to } 188, p < 10^{-25}$). Instead of measuring within-category design variation, aspect distributions reflect category-level baseline shifts.
2. **Artificial Inverted Price Coupling**:
   Physical aspects (`durability`, `build_quality`, `reliability`) exhibit strong negative correlations with the composite success score ($\rho = -0.48 \text{ to } -0.59$) across the pooled dataset and modest negative correlations within categories ($\bar{\rho} = -0.12 \text{ to } -0.15$). This directly contradicts the model's monotonic assumption ($+1$).
3. **Zero Incremental Residual Signal**:
   When regressing target residuals from a simple metadata baseline (Price + Category + Brand) against LLM aspects, the aspects achieve a **negative rank correlation of $\rho = -0.119$**. By contrast, raw TF-IDF specification tokens achieve **$\rho = +0.336$**. The LLM aspects contain **zero unique predictive information** beyond metadata.

---

## 2. Statistical Profiles Across the 9 Aspects

| Aspect | Mean $\pm$ SD | Median (IQR) | Pooled $\rho$ (Target) | Within-Cat $\bar{\rho}$ | Price $\rho$ | Category ANOVA $F$ ($p$-value) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **value_for_money** | $6.36 \pm 2.83$ | $7.54$ ($2.92$) | $-0.219$ | $-0.198$ | $-0.796$ | $F = 1.98$ ($p = 0.102$) |
| **utility** | $7.02 \pm 0.59$ | $6.96$ ($0.95$) | $-0.094$ | $-0.117$ | $-0.476$ | $F = 28.59$ ($p = 1.19 \times 10^{-16}$) |
| **ease_of_use** | $7.02 \pm 0.69$ | $7.03$ ($1.06$) | $+0.209$ | $-0.123$ | $-0.187$ | $F = 75.77$ ($p = 8.42 \times 10^{-32}$) |
| **reliability** | $4.27 \pm 0.95$ | $4.33$ ($1.37$) | $-0.480$ | $-0.154$ | $-0.682$ | $F = 82.06$ ($p = 2.75 \times 10^{-33}$) |
| **design_appeal** | $7.73 \pm 0.42$ | $7.79$ ($0.57$) | $-0.151$ | $-0.118$ | $-0.234$ | $F = 6.67$ ($p = 7.04 \times 10^{-5}$) |
| **after_sales** | $4.20 \pm 0.85$ | $4.14$ ($1.23$) | $-0.385$ | $-0.151$ | $-0.661$ | $F = 50.69$ ($p = 7.65 \times 10^{-25}$) |
| **build_quality** | $5.87 \pm 1.14$ | $6.30$ ($1.98$) | $-0.550$ | $-0.151$ | $-0.661$ | $F = 131.05$ ($p = 1.24 \times 10^{-42}$) |
| **durability** | $4.23 \pm 1.47$ | $4.84$ ($2.82$) | $-0.593$ | $-0.149$ | $-0.583$ | $F = 187.81$ ($p = 2.02 \times 10^{-50}$) |
| **repairability** | $3.77 \pm 1.10$ | $3.77$ ($1.31$) | $-0.508$ | $-0.151$ | $-0.719$ | $F = 68.61$ ($p = 5.33 \times 10^{-30}$) |

---

## 3. The Eight Diagnostic Dimensions

### 1. Are they Informative?
**Only in isolated semantic evaluation**. When evaluated completely alone (Model D: aspects only), they achieve $\rho = 0.541$ ($\text{AUC} = 0.886$). However, in the presence of metadata, they provide zero incremental predictive information.

### 2. Are they Redundant?
**YES, Highly Redundant with Price and Category**. `value_for_money`, `repairability`, `reliability`, and `build_quality` correlate at $r = -0.66 \text{ to } -0.80$ with price. They act as noisy, non-linear inverse price transforms.

### 3. Are they Noisy?
**YES, Substantial Estimation Variance**. Estimating aspect numbers from marketing copy injects variance ($\sigma_{\epsilon}^2$). When added to clean metadata features (Price, Brand, Category), this estimation noise degrades pooled rank correlation from $\rho = 0.726$ down to $\rho = 0.562$ (a $-0.164$ performance penalty).

### 4. Are they Category Proxies?
**EXTREMELY SO**. Category ANOVA F-statistics reach $187.81$ for `durability` and $131.05$ for `build_quality`. Ice makers receive mean durability scores of $2.17$, while bluetooth speakers receive $6.04$. The features primarily sort categories rather than products within categories.

### 5. Are they Brand Proxies?
**NO**. Aspect correlations with brand tier are modest ($r = -0.01 \text{ to } -0.33$). They do not capture historical brand reputation.

### 6. Are they Highly Collinear?
**YES**. The inter-aspect Spearman correlation matrix shows extreme collinearity between physical aspects: `durability` correlates with `build_quality` at $r = 0.89$ and with `reliability` at $r = 0.84$.

### 7. Are they Poorly Calibrated?
**YES**. The LLM compresses values into a narrow range for subjective aspects (`design_appeal` std $= 0.42$, IQR $= 0.57$) while producing category-dependent shifts that distort pooled ranking.

### 8. Are they Dominated by Subjective Attributes?
**YES**. In marketing copy, claims about "exceptional design" or "revolutionary sound" lack verifiable anchors, resulting in uncalibrated scores that fail to predict post-launch customer sentiment.

---

## 4. Semantic Validity vs. Predictive Validity

A central contribution of this forensic audit is disentangling **Semantic Validity** from **Predictive Validity**:

- **Semantic Validity**:
  *Definition*: Does the LLM aspect score accurately describe what the product specification says?
  *Audit Result*: **HIGH**. Human validation audits confirm that when a spec describes a lithium-ion battery or IP67 rating, the LLM reliably rates utility and durability higher ($r \approx 0.50$ fidelity against review ground truth). The model is semantically competent.
- **Predictive Validity**:
  *Definition*: Does that specification quality predict whether the product will succeed in the market?
  *Audit Result*: **LOW TO ZERO INCREMENTAL VALUE**. Market success in e-commerce physical goods is driven by pricing tier, category momentum, distribution partnerships, and brand trust. Two Bluetooth speakers with identical IP67 specifications have vastly different market outcomes depending on whether they carry a Bose logo or an unbranded white-label name.

**Conclusion**: The LLM aspect features possess genuine **semantic validity**, but lack **incremental predictive validity** for market success.
