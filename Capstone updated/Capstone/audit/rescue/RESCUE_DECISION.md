# FORMAL MODEL RESCUE DECISION MEMORANDUM

**Date**: October 2026  
**Evaluation Scope**: Bounded Model Rescue Feasibility Test  
**Evaluation Protocol**: Strictly Frozen Temporal Baseline ($N_{\text{train}}=507, N_{\text{test}}=124$, Cutoff October 31, 2021)  
**Deliverable**: Final Decision on Project Methodology and Model Architecture

---

## 1. RESCUE DECISION

$$\mathbf{RESCUE\ NOT\ JUSTIFIED}$$

The empirical investigation definitively demonstrates that the failure of the LLM aspect + monotonic XGBoost model is not an integration artifact that can be resolved through re-tuning or model tweaking. Adding the 9 LLM-derived aspects to standard metadata baselines consistently and statistically degrades predictive performance across all model families, fails the residualized target test ($\rho = -0.119$), and offers zero incremental value beyond raw specification text and category priors. Continued engineering effort directed at "rescuing" this specific predictive formulation is scientifically unpromising.

---

## 2. ROOT CAUSE

**Primary Diagnosis**: **Combination of Factors**

The failure of the proposed model is driven by four interacting structural mechanisms:

1. **Target-Specification Semantic Mismatch**:
   - The market success target is composed of review volume (40%), customer rating (35%), and sales velocity (25%). Commercial volume and launch velocity are heavily dictated by brand retail distribution, advertising budgets, and channel placement.
   - Pre-launch specifications describe design intentions and feature lists. They cannot forecast post-launch hardware failures, software bugs, thermal issues, or customer service execution.
   - Within categories, products with higher aspect scores receive lower consumer review ratings ($\bar{\rho} = -0.145$) due to inflated expectations for premium, complex hardware.

2. **LLM Representation Quality and Text Contamination**:
   - 75.5% of pre-launch product bullet points consist of promotional marketing claims, subjective adjectives, and brand boilerplate.
   - The LLM bridge maps this rhetoric into 9 highly collinear ($r > 0.85$), compressed aspect ratings. Rather than extracting true physical capabilities, the LLM acts as a category proxy ($F = 187.81$).
   - Granular, genuinely predictive engineering tokens (e.g., specific sensor part numbers, switch types, battery capacities) are destroyed by the coarse 9-aspect summarization, which explains why raw TF-IDF tokens achieve residual $\rho = +0.336$ while LLM aspects achieve $\rho = -0.119$.

3. **Category and Brand Dominance**:
   - Between-category variance accounts for the vast majority of target spread (e.g., Ice Makers mean success = 81.08; Smartwatches mean success = 37.20).
   - Once broad category shifts and brand tiers are captured ($\rho = 0.720$), little unexplained variance remains for generic aspect scores.

4. **Flawed Monotonic Architecture**:
   - Enforcing a positive $+1$ monotonic constraint on features that exhibit empirical negative correlations with the pooled target ($-0.48$ to $-0.59$) artificially crippled the XGBoost model, reducing performance from $\rho = 0.726$ (without aspects) down to $\rho = 0.562$.

---

## 3. BEST REVISED RESULT

The best scientifically validated model discovered during the rescue investigation is **Model C (Price + Category + Brand + Raw Specification Text Ridge)**:

| Metric | Proposed Original Model | Best Metadata Baseline (Model A) | Best Revised Model (Model C) |
| :--- | :---: | :---: | :---: |
| **Model Family** | Monotonic XGBoost | Ridge Regression | Ridge Regression |
| **Feature Set** | Price + Cat + Brand + 9 LLM Aspects | Price + Category + Brand | Price + Cat + Brand + Raw TF-IDF Text |
| **Test Spearman $\rho$** | 0.562 | 0.720 | **0.738** |
| **95% Bootstrap CI** | [0.435, 0.668] | [0.622, 0.795] | **[0.646, 0.810]** |
| **Binary Success AUC** | 0.812 | 0.892 | **0.908** |
| **RMSE** | 20.12 | 17.76 | **16.63** |
| **MAE** | 16.45 | 14.26 | **13.41** |
| **Within-Category Macro $\bar{\rho}$** | 0.112 | 0.310 | **0.342** |
| **Unseen-Brand Test $\rho$** | 0.514 | 0.680 | **0.704** |

*Note: In all cases, including the 9 LLM aspect features degrades the corresponding baseline.*

---

## 4. INCREMENTAL LLM VALUE

| Baseline Comparison | Incremental $\Delta \rho$ of LLM Aspects | Statistical Significance | Substantive Verdict |
| :--- | :---: | :---: | :--- |
| **Beyond Category + Brand + Price** | **-0.087** ($0.720 \to 0.633$) | $p < 0.001$ (Negative) | **Actively Harmful** |
| **Beyond Raw Specification Text** | **-0.050** ($0.683 \to 0.633$) | $p < 0.01$ (Negative) | **Inferior to Raw Text** |
| **Residualized Target Prediction** | **$\rho = -0.119$** | $p = 0.187$ | **Zero Orthogonal Signal** |
| **Within-Category Discrimination** | **-0.154** ($0.310 \to 0.156$) | $p < 0.001$ (Negative) | **Destroys Within-Cohort Signal** |

**Conclusion**: The LLM aspect features provide **no positive incremental information** beyond simple metadata and raw specification text.

---

## 5. REPRODUCIBILITY

- **Seed Stability**: Model evaluations across 5 distinct random seed initializations demonstrate negligible variance ($\sigma_{\rho} < 0.004$ across seeds).
- **CV Stability**: 5-fold cross-validation on the training set ($N=507$) replicates the test set ranking:
  - Model A (Metadata Ridge): Mean CV $\rho = 0.704 \pm 0.021$
  - Model B (Metadata + LLM Ridge): Mean CV $\rho = 0.628 \pm 0.026$
  - Model C (Metadata + Raw Text Ridge): Mean CV $\rho = 0.722 \pm 0.019$
- The degradation caused by LLM aspects is completely reproducible and deterministic.

---

## 6. TIME AND COST ASSESSMENT

- **Additional Work Required if GO**: Re-extracting aspects with custom fine-tuned models, collecting external teardown datasets, and engineering manual feature rubrics would require an estimated 3–4 weeks of engineering without guaranteed success.
- **Feasibility Verdict**: A 2–3 day rebuild searching for alternative XGBoost configurations is **NOT justified**, as empirical tests confirm the representation itself carries negative residual correlation ($\rho = -0.119$).
- **Reframing Timeline**: Reframing the manuscript to rigorously report these negative results, category priors, and LLM text distortions requires **1–2 working days** and produces a methodologically unassailable scientific contribution.

---

## 7. FINAL RECOMMENDATION

$$\mathbf{STOP\ MODEL\ RESCUE\ AND\ REFRAME}$$

### Scientific Rationale:
The evidence indicates that the current methodological idea (claiming predictive superiority for LLM-extracted aspect ratings in market forecasting) is fundamentally contradicted by the data. Continuing to tune the model in pursuit of an artificial win is scientifically unsound.

However, the findings gathered across Issues 1 through 6 and this Feasibility Test represent a **compelling, high-impact scientific contribution** when reframed as:
1. A rigorous empirical demonstration of the **Category Dominance and Proxy Effect** in e-commerce forecasting.
2. An essential cautionary case study demonstrating that **LLM zero-shot aspect extraction acts as a lossy, collinear distortion** when applied to promotional pre-launch text, underperforming raw n-gram representations.
3. An audit methodology illustrating how **imposing theoretical monotonic constraints on proxy features degrades performance** when macro-category distributions shift.

The paper should be reframed around these rigorous negative findings and methodological lessons.
