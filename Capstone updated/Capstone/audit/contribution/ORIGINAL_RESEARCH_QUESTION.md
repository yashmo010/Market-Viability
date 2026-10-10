# Reconstructing the Original Research Questions and Hypotheses

**Document**: `audit/contribution/ORIGINAL_RESEARCH_QUESTION.md`  
**Purpose**: Rigorous forensic audit of what the project originally intended to answer, what was hypothesized, and which hypotheses survived vs. were falsified.

---

## 1. What Was the Original Research Question?

The original overarching research question stated in the manuscript (`main.tex`, lines 26–33) is:

> *"Can a physical product's eventual market success be predicted launch-blind from its pre-production technical specification alone, before any customer has reviewed, rated, or purchased it?"*

This was broken down into three operational sub-questions:
- **RQ1 (Semantic Feasibility)**: Can a large language model extract meaningful, grounded product-quality aspect ratings from technical specifications using a skeptic-prompting regime?
- **RQ2 (Predictive Validity)**: Does an aspect-bridged model outperform conventional baselines in forecasting post-launch market adoption on unseen, forward-in-time product launches?
- **RQ3 (Econ-Monotonic Interpretability)**: Can machine learning models enforce structural economic constraints (e.g. non-increasing in price, non-decreasing in quality) to prevent non-physical inversions while improving or maintaining empirical accuracy?

---

## 2. What Specific Hypotheses Were Being Tested?

The manuscript and code repository were built around five core hypotheses ($H_1$ through $H_5$):

- **$H_1$ (Superior Predictive Accuracy)**:  
  *A monotonic gradient-boosted architecture combining LLM-bridged aspects, price, and category priors outperforms standard machine learning baselines (Random Forest, Linear Models, Category Priors, Price Baselines) in predicting post-launch success.*
- **$H_2$ (LLM Bridging Value-Add)**:  
  *Estimating latent aspect quality from text via an LLM semantic bridge provides incremental predictive information beyond simple raw text representations (e.g., TF-IDF) and metadata.*
- **$H_3$ (Monotonic Constraints Empirical Lift)**:  
  *Enforcing monotonic shape constraints prevents overfitting to noisy target signals and significantly improves out-of-sample ranking accuracy and quintile separation (claimed AUC lift from 0.826 to 0.903).*
- **$H_4$ (Cold-Start Generalization on Unseen Brands)**:  
  *Because the LLM analyzes intrinsic physical specifications rather than historical sales, the model generalizes effectively to new market entrants and unbranded/unknown manufacturers where historical brand lookups fail.*
- **$H_5$ (Asymmetric Aspect Recoverability / Boundary Conditions)**:  
  *Specifications encode verifiable experiential and functional quality (utility, durability, build quality) but cannot encode non-spec properties (after-sales service, aesthetic appeal); consequently, predictive power is bounded by the spec-expressiveness of the product category.*

---

## 3. What Was the Proposed Methodological Contribution?

The paper proposed a multi-stage methodology consisting of:
1. **Null-Forcing Review Extraction**: Scoring 43,000+ customer reviews along 9 aspects, requiring verbatim quote grounding and output validation.
2. **Skeptic-Prompted Aspect Bridging**: An LLM inference pipeline with "adjective blindness", "absence penalties", and "anchor discipline" to convert marketing copy and spec bullets into latent aspect profiles.
3. **Monotonic XGBoost Forecaster**: A tree-based regressor constrained to respect economic signs (price $\le 0$, quality aspects $\ge 0$).
4. **Honesty Layer & Calibrated Abstention**: Weighting confidence by measured aspect fidelity ($r \approx 0.50$ vs. $0.07$), assigning trust badges, and abstaining when specifications contain flat capacity numbers without experiential depth.

---

## 4. What Outcomes Were Expected?

1. The proposed model was expected to be the top-performing model on all primary metrics (highest $R^2$, lowest RMSE, highest Spearman $\rho$, highest quintile AUC).
2. The LLM aspect bridging layer was expected to be the critical engine of predictive accuracy, with ablations showing that removing LLM aspects would collapse performance.
3. Monotonic constraints were expected to demonstrate clear, statistically significant empirical superiority over unconstrained trees.
4. The model was expected to dramatically outperform simple category and brand priors across all evaluation regimes.

---

## 5. Which Original Hypotheses Survived?

### ✅ $H_4$ (Cold-Start Semantic Generalization on Unseen Brands) — *PARTIALLY SURVIVED (WITH BOUNDARIES)*
- **Evidence**: On products from brands completely unseen in training ($N=82$), the Brand-Only baseline has zero variance and fails completely. LLM aspects alone achieve $\rho = 0.621$ ($\text{AUC} = 0.886$), proving that specifications convey genuine quality signals without brand metadata. In spec-expressive categories like Smartwatches ($n=28$ unseen), the proposed model achieves $\rho = 0.253$ while TF-IDF collapses to $\rho = -0.406$.
- **Qualification**: While the semantic signal exists, pooled correlation on unseen brands is still dominated by between-category shifts (Category Mean achieves $\rho = 0.686$).

### ✅ $H_5$ (Asymmetric Aspect Recoverability & Category Boundary) — *STRONGLY SURVIVED*
- **Evidence**: The empirical fidelity measurements confirmed that physical and experiential aspects bridge with moderate fidelity ($r = 0.50 \text{ to } 0.53$ for utility, ease of use, durability, build quality), whereas commercial and subjective aspects fail ($r = 0.07$ for after-sales, $0.21$ for design appeal).
- **Evidence**: The category dissociation between spec-expressive personal electronics (Smartwatches within $\rho = 0.415$) and capacity-only appliances (Ice Makers bridging fidelity $r \approx 0.04$) is strongly supported and forms a major empirical finding.

---

## 6. Which Original Hypotheses Were Falsified?

### ❌ $H_1$ (Superior Predictive Accuracy) — *FALSIFIED*
- **Evidence**: The proposed model ($\rho = \mathbf{0.562}$) is **outperformed** on pooled test rank correlation by:
  - Category + Brand Ridge ($\rho = \mathbf{0.712}$, $p = 1.90 \times 10^{-20}$)
  - Gradient Boosting ($\rho = \mathbf{0.698}$)
  - Random Forest ($\rho = \mathbf{0.694}$)
  - Category Median ($\rho = \mathbf{0.691}$)
  - Spec TF-IDF + Ridge ($\rho = \mathbf{0.683}$)
  - Category Mean ($\rho = \mathbf{0.671}$)
- **Evidence**: Within categories, GBDT ($\bar{\rho}_{\text{macro}} = \mathbf{0.414}$) and Category + Brand Ridge ($\bar{\rho}_{\text{macro}} = \mathbf{0.352}$) also outperform the proposed model ($\bar{\rho}_{\text{macro}} = \mathbf{0.207}$).
- **Verdict**: The claim that the proposed architecture achieves superior forecasting accuracy is definitively falsified.

### ❌ $H_2$ (LLM Bridging Improves Overall Accuracy) — *FALSIFIED*
- **Evidence**: Ablating LLM aspects entirely (**Ablation A: Price + Brand + Category**) causes pooled performance to **increase** from $\rho = 0.562$ to $\rho = \mathbf{0.726}$ ($\Delta \rho = +0.164, p < 0.001$).
- **Evidence**: A simple 300-token bag-of-words TF-IDF model achieves $\rho = 0.683$, beating the LLM-bridged model.
- **Verdict**: Estimating latent aspects via LLM injects estimation variance ($\sigma_{\epsilon}^2$) into the prediction pipeline. It does NOT improve overall predictive accuracy relative to pure metadata or direct text baselines.

### ❌ $H_3$ (Monotonic Constraints Improve Empirical Accuracy) — *FALSIFIED*
- **Evidence**: On the frozen temporal holdout, removing monotonic constraints (Ablation D) yields $\rho = 0.542$ vs. $0.562$ ($\Delta \rho = +0.020$, $95\%$ CI $[-0.037, +0.074], p = 0.453$) and AUC $= 0.879$ vs. $0.890$ ($\Delta \text{AUC} = +0.011, p = 0.753$).
- **Verdict**: The constraints do not produce a statistically significant empirical gain. Their contribution is strictly inductive bias (preventing illogical sign inversions), not accuracy enhancement.

---

## 7. Which Hypotheses Remain Inconclusive?

### ❓ Cross-Platform / Market-Wide Generalization
- The study evaluated Amazon US. While external survey evidence in Issue 5 showed that consumer priorities align with review aspect importance, direct cross-platform outcome validation (e.g. Best Buy, Target, Shopify) could not be executed due to the absence of public pre-launch multi-platform sales datasets. This hypothesis remains inconclusive and bounded to Amazon.
