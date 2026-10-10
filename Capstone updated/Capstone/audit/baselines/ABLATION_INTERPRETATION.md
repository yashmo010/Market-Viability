# Component Ablation Interpretation & Root-Cause Evidence Analysis

**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher, Experimental Scientist, and Hostile Peer Reviewer  
**Reference Artifact**: [`audit/baselines/ABLATION_RESULTS.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/ABLATION_RESULTS.csv)  
**Evaluation Protocol**: Strict Temporal Holdout ($N=124$, cutoff October 31, 2021)

---

## 1. Executive Summary of Component Contributions

To determine whether the paper's reported performance reflects genuine architectural synergy or hidden confounds, we systematically ablated every component of the proposed system under identical test conditions:

| Component Under Audit | Ablation Condition | Spearman $\rho$ | $\Delta \rho$ vs Full ($0.562$) | Paired $p$-value | Empirical Verdict |
|---|---|:---:|:---:|:---:|---|
| **Brand Information** | Ablation B (Brand Tier Zeroed) | **0.458** | **-0.104** | **$p < 0.001$** | **CRITICAL DRIVER**: Primary contributor to within-category ranking |
| **Experiential Aspects** | Ablation F2 (Omit Utility, Ease, Reliability) | **0.494** | **-0.068** | **$p < 0.001$** | **MEANINGFUL CONTRIBUTOR**: Most informative aspect family |
| **Category Normalization** | Ablation E (Evaluate on Raw Target) | **0.404** | **-0.158** | **$p < 0.001$** | **CRITICAL METHODOLOGY**: Category scaling is mathematically essential |
| **Monotonic Constraints** | Ablation D (Unconstrained XGBoost) | **0.542** | **-0.020** | $p = 0.453$ | **MARGINAL / REDUNDANT**: Economic prior; no empirical boost |
| **Category Indicators** | Ablation C (Omit Category Feature) | **0.571** | **+0.009** | $p = 0.734$ | **REDUNDANT**: Price and aspects encode category implicitly |
| **Physical Build Aspects** | Ablation F1 (Omit Build, Durability, Repair) | **0.573** | **+0.011** | $p = 0.612$ | **NEUTRAL**: Negligible incremental contribution |
| **Commercial/Aesthetic Aspects** | Ablation F3 (Omit Value, Design, Service) | **0.667** | **+0.105** | **$p < 0.001$** | **HARMFUL / NOISY**: Subjective aspects degrade prediction |
| **LLM Aspect Extractions (All)** | Ablation A (Metadata Only: Price + Brand + Cat) | **0.726** | **+0.164** | **$p < 0.001$** | **HARMFUL ON POOLED FIT**: Introducing bridged aspects penalizes pooled fit |
| **Raw Specs Text (Non-LLM)** | Ablation H (TF-IDF XGBoost) | **0.708** | **+0.146** | **$p < 0.001$** | **STRONG NON-LLM BASELINE**: Simple n-grams beat LLM bridge |

---

## 2. Component-by-Component Scientific Inquest

### Question 1: What evidence demonstrates that LLM-derived aspects contribute meaningful information?
- **Finding**: **Qualified / Mixed Evidence; Degrades Overall Accuracy Relative to Simpler Models**.
- **Empirical Facts**:
  1. When evaluated in complete isolation (Model 2: LLM Aspects Alone, no metadata), the bridged aspects achieve Spearman $\rho = 0.526$ and $\text{AUC} = 0.886$. This indicates that LLM aspect extractions capture genuine semantic signal from product specifications.
  2. However, when added to strong metadata features (Price + Brand Tier + Category, which alone achieve $\rho = 0.726$), the full proposed model's pooled performance **drops to $\rho = 0.562$** ($\Delta \rho = -0.164, p < 0.001$).
  3. Furthermore, on non-LLM technical specifications, a simple TF-IDF + Ridge model achieves $\rho = 0.683$.
  4. Even on the unseen-brand cold-start subset ($N=82$), Category Mean alone achieves $\rho = 0.686$ and TF-IDF achieves $\rho = 0.623$, whereas the full proposed model achieves $\rho = 0.585$.
- **Scientific Verdict**:
  The paper **CANNOT** claim that adding LLM aspects improves overall predictive accuracy over simpler metadata or text baselines. The scientifically defensible characterization is:
  > *"LLM semantic extraction provides an interpretable structured aspect representation from text alone without historical review footprints, but introduces estimation noise when combined with strong historical metadata priors and does not improve overall predictive accuracy relative to category priors or direct text models."*

---

### Question 2: Is the model driven primarily by brand memorization?
- **Finding**: **Substantially Brand-Driven for Within-Category Ranking on Established Brands; Category-Driven on Unseen Brands**.
- **Empirical Facts**:
  1. Removing brand tier (Ablation B) causes pooled $\rho$ to drop from $0.562$ to $0.458$ ($\Delta \rho = -0.104$).
  2. Within categories, removing brand tier causes mean within-category $\rho$ to collapse from **$+0.207$ to $-0.180$**.
  3. Brand-Only baseline achieves a within-category macro-average $\bar{\rho}$ of $+0.353$, exceeding the proposed model's $+0.207$.
  4. On the $82$ test products from brands completely unseen in the training catalog, the Brand-Only baseline has zero variance (constant fallback tier 0) and yields undefined correlation.
  5. The proposed model achieves $\rho = 0.585$ on unseen brands. However, Category Mean alone achieves $\rho = 0.686$ on the same unseen-brand subset. This demonstrates that the high pooled correlation on unseen brands is primarily driven by between-category intercept differences rather than specification-driven rank ordering.
- **Scientific Verdict**:
  Brand footprint explains most of the model's within-category ranking skill for established brands. On unseen brands, between-category priors dominate the pooled correlation. Within specific categories like smartwatches ($n=28$ unseen), the proposed model achieves $\rho = 0.253$ (where TF-IDF yields $\rho = -0.406$), which supports specification-based differentiation in specific spec-expressive domains, but this does not generalize across all categories.

---

### Question 3: What is the empirical value of monotonic constraints?
- **Finding**: **Enforces Modeling Assumptions with No Statistically Significant Performance Shift**.
- **Empirical Facts**:
  - Unconstrained XGBoost (Ablation D): $\rho = 0.542, \text{AUC} = 0.879, \text{RMSE} = 21.52$.
  - Monotonic XGBoost (Proposed): $\rho = 0.562, \text{AUC} = 0.890, \text{RMSE} = 21.12$.
  - Paired difference: $\Delta \rho = +0.020$ ($95\%$ CI $[-0.037, +0.074], p = 0.453$); $\Delta \text{AUC} = +0.011$ ($p = 0.753$).
- **Scientific Verdict**:
  The monotonic constraints enforce the specified directional relationships and prevent predictions that violate those modeling assumptions; in this experiment they did not produce a statistically significant change in ranking performance. Monotonic constraints must not be claimed as an empirical forecasting accuracy improvement.

---

### Question 4: Which specific aspect families matter?
- **Finding**: **Experiential aspects dominate; commercial and subjective aspects degrade performance**.
- **Empirical Facts**:
  1. **Experiential Aspects** (`utility`, `ease_of_use`, `reliability`): Removing them (Ablation F2) drops performance to $\rho = 0.494$ ($\Delta \rho = -0.068, p < 0.001$). These are the most verifiable and predictive aspects in technical specifications.
  2. **Physical Build Aspects** (`build_quality`, `durability`, `repairability`): Removing them (Ablation F1) yields $\rho = 0.573$ ($\Delta \rho = +0.011$, neutral). Durability claims in specs are often marketing exaggerations that fail to translate into post-launch reliability.
  3. **Commercial / Aesthetic Aspects** (`value_for_money`, `design_appeal`, `after_sales`): Removing them (Ablation F3) **substantially improves performance** to $\rho = 0.667$ ($\Delta \rho = +0.105, p < 0.001$). Aesthetics are subjective, after-sales service is unmentioned in specs, and value-for-money is heavily collinear with price.
- **Scientific Recommendation**:
  The proposed model could be simplified and made more performant by pruning commercial and aesthetic aspects entirely, focusing exclusively on experiential engineering utility.

---

### Question 5: Why does raw TF-IDF text outperform the proposed LLM bridge?
- **Finding**: **High-dimensional n-grams directly capture specific technical specifications that the LLM summary compresses away**.
- **Empirical Facts**:
  - Baseline I1 (Spec TF-IDF + Ridge): $\rho = 0.683, \text{AUC} = 0.979, \text{RMSE} = 17.00$.
  - Ablation H (Spec TF-IDF + XGBoost): $\rho = 0.708, \text{AUC} = 0.984, \text{RMSE} = 17.01$.
  - Proposed Model (LLM Bridge + XGBoost): $\rho = 0.562, \text{AUC} = 0.890, \text{RMSE} = 21.12$.
- **Root Cause**:
  Raw specifications contain exact numeric hardware tokens (e.g., "5000mAh", "IP67", "Bluetooth 5.2", "AMOLED", "ANC", "24-bit") that a linear or tree model can directly map to product categories and quality tiers. The LLM aspect bridging layer compresses these rich multidimensional technical tokens down into 9 coarse scalar scores (0–10), discarding fine-grained component signals.
- **Scientific Verdict**:
  A skeptical reviewer who states: *"A much simpler model (TF-IDF + Ridge) achieves essentially the same or better result"* is **factually correct regarding pooled test correlation**. The authors must transparently disclose that TF-IDF achieves $\rho = 0.683$ and defend the LLM bridging layer based on **interpretability, conversational feedback, and actionable product development insights**, NOT superior raw predictive accuracy.
