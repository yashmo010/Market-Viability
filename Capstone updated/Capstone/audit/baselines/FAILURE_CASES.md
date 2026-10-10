# Failure Cases & Scientific Pathology Audit

**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher, Experimental Scientist, and Hostile Peer Reviewer  
**Scope**: Rigorous examination of all scenarios where simpler baselines or ablations outperform the proposed method, where predictions collapse, or where performance exhibits instability.

---

## 1. Primary Failure Mode 1: Simple Baselines Outperform the Proposed Model on Pooled Ranking

### The Empirical Evidence:
Under the identical forward-in-time temporal holdout ($N=124$, cutoff October 31, 2021), multiple simple and conventional baselines achieve higher pooled Spearman rank correlation than the proposed LLM-bridged XGBoost model ($\rho = 0.562$):

| Model | Evaluated Features | Spearman $\rho$ | AUC | RMSE | $\Delta \rho$ vs Proposed |
|---|---|:---:|:---:|:---:|:---:|
| **Baseline F: Category + Brand** | One-hot Category + Brand Tier | **0.712** | **0.994** | 17.79 | **+0.150** ($p = 0.003$) |
| **Baseline H2: Gradient Boosting** | Full Features (Aspects + Brand + Cat) | **0.698** | **0.970** | 20.27 | **+0.136** ($p = 0.014$) |
| **Baseline H1: Random Forest** | Full Features (Aspects + Brand + Cat) | **0.694** | **0.993** | 19.46 | **+0.132** ($p = 0.034$) |
| **Baseline D: Category Median** | Category Grouping Only | **0.691** | **0.980** | **15.82** | **+0.129** ($p = 0.006$) |
| **Baseline I2: Spec TF-IDF + Price + Cat** | TF-IDF Text + Price + Category | **0.688** | **0.979** | 16.92 | **+0.126** ($p = 0.026$) |
| **Baseline I1: Spec TF-IDF + Ridge** | 300 TF-IDF Technical Tokens Only | **0.683** | **0.979** | 17.00 | **+0.120** ($p = 0.035$) |
| **Baseline C: Category Mean** | Category Grouping Only | **0.671** | **0.980** | 17.18 | **+0.109** ($p = 0.014$) |
| **Proposed Model (XGBoost Monotone)** | Full LLM Bridged Aspects + Brand + Cat | **0.562** | **0.890** | 21.12 | Reference |

### Root-Cause Diagnosis:
- **Type**: **Target Limitation & Methodological Confound**.
- **Explanation**:
  1. **Between-Category Target Shift**: The target `SuccessScore` has substantial between-category mean differences across the test set (e.g., smartwatches average 62.4, ice makers average 48.1, power banks average 44.2). Simply predicting the category mean or median cleanly separates these clusters across the pooled 124 products, generating an automatic pooled $\rho = 0.671$ with zero within-category ranking skill.
  2. **Estimation Variance Induced by LLM Bridging**: The proposed model attempts to predict granular within-category variations. Because bridged aspects are estimated from noisy marketing copy, they introduce estimation error ($\sigma_{\epsilon}^2$). When combined across categories, this estimation variance scrambles the clean category boundaries, pulling the pooled $\rho$ down from $0.671$ to $0.562$.
- **Scientific Implication**:
  The paper **MUST NOT** claim that the proposed model outperforms simple category priors or TF-IDF models on pooled rank correlation. Even on the unseen-brand cold-start subset ($N=82$), Category Mean alone achieves $\rho = 0.686$, beating the proposed model's $\rho = 0.585$. This demonstrates that pooled correlation on unseen brands is also substantially driven by between-category intercept shifts. Any claimed design intelligence must be strictly bounded to domain-specific within-category product differentiation where semantic signals provide positive alignment.

---

## 2. Failure Mode 2: Ablating LLM Aspects Improves Pooled Performance

### The Empirical Evidence:
- **Ablation A (Remove LLM Aspects)**: An XGBoost model trained on only `price`, `brand_tier`, and `category` achieves:
  $$\rho = \mathbf{0.726}, \quad \text{AUC} = \mathbf{0.994}, \quad \text{RMSE} = \mathbf{17.12}, \quad \text{MAE} = \mathbf{13.92}$$
  outperforming the full model ($\rho = 0.562$) by **$\Delta \rho = +0.164$ ($p < 0.001$)**!
- Within-category ranking also improves: from mean $\bar{\rho}_{\text{within}} = 0.207$ to $\bar{\rho}_{\text{within}} = 0.307$!

### Root-Cause Diagnosis:
- **Type**: **Data Limitation & Noise Injection**.
- **Explanation**:
  In physical e-commerce marketplaces, brand footprint and price positioning explain the vast majority of consumer adoption. Established brands (Sony, Apple, Bose) with premium pricing reliably generate massive sales volumes. When the model relies strictly on brand and price, it makes clean, confident predictions. Introducing 9 subjective LLM-bridged aspect scores introduces noise that dilutes the high-confidence brand/price signal.
- **Scientific Implication**:
  The LLM bridging layer does not act as an additive booster to established brand predictions; its true purpose is a **cold-start substitute** when brand reputation is absent.

---

## 3. Failure Mode 3: Complete Ranking Collapse When Brand Tier is Removed

### The Empirical Evidence:
- **Ablation B (Brand Tier Zeroed)**:
  - Pooled $\rho$ drops from $0.562$ to $0.458$ ($\Delta \rho = -0.104$).
  - Mean within-category $\rho$ collapses from **$+0.207$ to $-0.180$**!
  - Within Bluetooth Speakers: $\rho = -0.393$!
  - Within Wireless Headphones: $\rho = -0.316$!
  - Within Power Banks: $\rho = -0.274$!

### Root-Cause Diagnosis:
- **Type**: **Distribution Shift & Brand Monopoly Dynamic**.
- **Explanation**:
  Within mature categories like headphones and speakers, product specifications are largely commoditized (nearly all products list "Bluetooth 5.0", "IPX5 waterproof", "long battery life"). Two products with identical specification bullets can have a 100-fold difference in sales because one is manufactured by Bose and the other by an unbranded white-label vendor. Without brand tier, the model cannot distinguish between premium flagships and low-tier clones from specifications alone.

---

## 4. Failure Mode 4: Category-Specific Instability (Ice Makers & Power Banks)

### The Empirical Evidence:
Within-category performance varies wildly across the 5 evaluated categories:

| Category | Test Sample $N$ | Proposed Model $\rho$ | Baseline E (Brand) $\rho$ | Baseline H2 (GBDT) $\rho$ | Diagnosis |
|---|:---:|:---:|:---:|:---:|---|
| **Bluetooth Speakers** | 7 | **0.536** | 0.578 | **0.643** | Brand-dominated; small test sample |
| **Smartwatches** | 39 | **0.415** | 0.549 | 0.370 | High specification fidelity; stable |
| **Ice Makers** | 36 | **0.179** | -0.160 | **0.272** | Highly commoditized; brand misleading; spec noise |
| **Power Banks** | 19 | **-0.042** | **0.368** | 0.255 | **TOTAL FAILURE**: Specs fail to predict adoption |
| **Wireless Headphones** | 23 | **-0.055** | **0.428** | **0.531** | **TOTAL FAILURE**: Dominated entirely by brand; specs decorrelated |

### Root-Cause Diagnosis:
- **Type**: **Domain Heterogeneity & Market Dynamics Shift**.
- **Explanation**:
  - In **Smartwatches**, hardware specifications (AMOLED, GPS, battery capacity, sensors) directly correlate with product utility and market success ($\rho = 0.415$).
  - In **Power Banks** and **Wireless Headphones**, specifications are saturated and non-differentiating (almost all claim 10,000mAh or 20-hour battery life). Real commercial outcomes depend on distribution deals, marketing spend, and brand prestige. As a result, specification-derived predictions fail completely ($\rho < 0$), while Brand Tier succeeds ($\rho = 0.368$ and $0.428$).
- **Scientific Implication**:
  The paper must state clearly that pre-launch specification bridging is effective in **feature-differentiated categories** (smartwatches, speakers), but fails in **heavily commoditized categories** where brand equity is the sole determinant of market success.

---

## 5. Summary Table of Pathologies & Recommended Fixes

| Failure Case | Root Cause | Paper Threat Level | Required Manuscript Remedy |
|---|---|:---:|---|
| Category Mean / Median beats Proposed Model on pooled $\rho$ | Target between-category shift | **CRITICAL** | Retract claim of general pooled superiority; disclose Category Mean $\rho = 0.671$. |
| Removing LLM aspects improves fit ($\rho = 0.726$) | LLM bridging noise vs. clean metadata | **CRITICAL** | Frame LLM bridge as cold-start tool for unseen brands, not an additive booster. |
| Negative within-category ranking without Brand ($\rho = -0.180$) | Specification commoditization | **HIGH** | Transparently document that brand drives established within-category sorting. |
| Negative ranking in Power Banks & Headphones | Commodity distribution dynamics | **MEDIUM** | Bound claimed scope to feature-rich consumer electronics. |
