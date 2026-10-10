# TARGET COMPONENT ALIGNMENT AUDIT
**Date**: October 2026  
**Scope**: Bounded Model Rescue Feasibility Test — Target Mismatch Hypothesis (Section 8)  
**Dataset**: Frozen Temporal Test Set ($N=124$), Evaluated Against Temporal Cutoff (October 31, 2021)

---

## 1. Executive Summary

A central hypothesis tested in this model rescue investigation is the **Target-Mismatch Hypothesis**:
> *Does the LLM specification-derived aspect representation fail to predict the composite market success score because the composite target combines commercial marketplace dynamics (volume, sales velocity) that specifications cannot physically encode, while successfully predicting customer satisfaction (ratings)?*

**Empirical Conclusion**: **The Target-Mismatch Hypothesis is FALSIFIED.**
1. The LLM aspect representation fails to predict **all three individual target components** within categories.
2. The within-category macro-average Spearman correlation with customer rating (`rating_norm`) is **$\bar{\rho} = -0.145$**, with sales volume (`volume_norm`) is **$\bar{\rho} = -0.138$**, and with sales velocity (`velocity_norm`) is **$\bar{\rho} = -0.071$**.
3. In pooled test evaluation, the large negative correlations with volume (e.g., `durability` $\rho = -0.649$, `build_quality` $\rho = -0.604$) reflect category confounding (smartwatches have high technical aspect scores but lower review volume than commodity ice makers/webcams).
4. Raw specification text (TF-IDF tokens) captures genuine product attributes that explain residual target variance ($\rho = +0.336$), whereas LLM aspect scores explain **zero incremental variance** ($\rho = -0.119$).
5. Thus, the model failure is not a benign mismatch between technical specs and commercial volume; rather, the LLM aspect bridge strips predictive technical distinctions and replaces them with redundant, category-correlated hallucinations.

---

## 2. Target Formulation and Component Decomposition

The composite ground-truth target is defined as:
$$\text{Composite Success Score} = 0.40 \times \text{Volume}_{\text{norm}} + 0.35 \times \text{Rating}_{\text{norm}} + 0.25 \times \text{Velocity}_{\text{norm}}$$

Each component captures a distinct post-launch marketplace construct:

| Component | Weight | Underlying Metric | Theoretical Determinants | Inferable from Pre-Launch Specs? |
| :--- | :---: | :--- | :--- | :--- |
| **Volume ($\text{Volume}_{\text{norm}}$)** | 40% | Total verified consumer review count | Brand reach, distribution channel, marketing budget, retail prominence, price tier. | **No.** Technical specifications do not determine commercial sales scale. |
| **Rating ($\text{Rating}_{\text{norm}}$)** | 35% | Bayesian-damped average review rating | Product quality, defect rates, customer expectation vs. reality, usability, reliability. | **Partially.** High build quality and ergonomics should theoretically mitigate negative ratings. |
| **Velocity ($\text{Velocity}_{\text{norm}}$)** | 25% | Review arrival rate in initial post-launch window | Launch momentum, PR buzz, initial channel velocity, pre-order conversion. | **No.** Primarily commercial and marketing execution. |

---

## 3. Empirical Component Correlations (Frozen Test Set, $N=124$)

### 3.1 Pooled Target vs. Aspect Correlations

The table below presents the Pearson $r$ and Spearman $\rho$ between each of the 9 LLM-derived aspects and the three target components across the entire test set ($N=124$):

| Aspect | Success Score ($\rho$) | Volume Norm ($\rho$) | Rating Norm ($\rho$) | Velocity Norm ($\rho$) |
| :--- | :---: | :---: | :---: | :---: |
| `value_for_money` | -0.219 | -0.209 | -0.145 | -0.122 |
| `utility` | -0.094 | -0.177 | +0.067 | -0.008 |
| `ease_of_use` | +0.209 | +0.111 | +0.147 | +0.364 |
| `reliability` | -0.480 | -0.538 | -0.194 | -0.364 |
| `design_appeal` | -0.151 | -0.168 | +0.045 | -0.197 |
| `after_sales` | -0.385 | -0.419 | -0.138 | -0.325 |
| `build_quality` | -0.550 | -0.604 | -0.233 | -0.433 |
| `durability` | -0.593 | -0.649 | -0.255 | -0.492 |
| `repairability` | -0.508 | -0.536 | -0.266 | -0.388 |

#### Key Observations:
1. **Pervasive Negative Direction**: For 8 out of 9 aspects, higher LLM ratings correlate **negatively** with commercial success, sales volume, and customer rating.
2. **Monotonic Constraint Invalidation**: The original architecture imposed a strict $+1$ monotonic constraint on all 9 aspects in XGBoost (`monotone_constraints=(1, 1, 1, 1, 1, 1, 1, 1, 1)`). Imposing a positive monotonicity constraint on features whose true pooled correlations with the target are $-0.48$ to $-0.59$ severely degraded performance ($\rho = 0.562$).
3. **Rating Component is Not Rescued**: The expectation that LLM aspects would at least correlate positively with `rating_norm` is contradicted: 6 of 9 aspects are negatively correlated with ratings, and the remaining 3 (`utility`, `ease_of_use`, `design_appeal`) exhibit negligible correlation ($\rho \le +0.147$).

---

## 4. Within-Category Component Alignment

To eliminate between-category distribution shifts and determine if aspects predict product quality *within* competitive cohorts, we compute macro-averaged Spearman correlations within each of the 5 test categories:

| Target Component | Macro Within-Category Mean $\bar{\rho}$ | Positive Aspects ($>0$) | Negative Aspects ($<0$) | Range of Within-Category $\bar{\rho}$ |
| :--- | :---: | :---: | :---: | :---: |
| **Composite Success** | **-0.149** | 0 / 9 | 9 / 9 | -0.198 to -0.117 |
| **Volume Norm** | **-0.138** | 0 / 9 | 9 / 9 | -0.163 to -0.094 |
| **Rating Norm** | **-0.145** | 0 / 9 | 9 / 9 | -0.243 to -0.106 |
| **Velocity Norm** | **-0.071** | 0 / 9 | 9 / 9 | -0.090 to -0.038 |

### Breakdown by Individual Aspect (Within-Category $\bar{\rho}$):

| Aspect | Within-Cat Success ($\bar{\rho}$) | Within-Cat Volume ($\bar{\rho}$) | Within-Cat Rating ($\bar{\rho}$) | Within-Cat Velocity ($\bar{\rho}$) |
| :--- | :---: | :---: | :---: | :---: |
| `value_for_money` | -0.198 | -0.163 | -0.243 | -0.068 |
| `utility` | -0.117 | -0.138 | -0.106 | -0.056 |
| `ease_of_use` | -0.123 | -0.096 | -0.155 | -0.038 |
| `reliability` | -0.154 | -0.152 | -0.144 | -0.090 |
| `design_appeal` | -0.118 | -0.094 | -0.108 | -0.059 |
| `after_sales` | -0.151 | -0.147 | -0.147 | -0.082 |
| `build_quality` | -0.151 | -0.149 | -0.137 | -0.077 |
| `durability` | -0.149 | -0.145 | -0.155 | -0.085 |
| `repairability` | -0.151 | -0.146 | -0.153 | -0.088 |

### Root Cause of the Negative Within-Category Signal:
1. **The Price–Expectation Penalty**: The LLM assigns higher aspect scores to more expensive, feature-packed flagship models ($r = +0.65$ to $+0.84$ with price). However, consumers purchasing premium products hold substantially higher performance expectations, leading to more critical review ratings.
2. **Mass-Market Sales Skew**: Entry-level and mid-tier products sell far higher volumes on e-commerce platforms than expensive flagship devices with exhaustive spec sheets. Because the LLM rewards technical complexity, its scores systematically correlate inversely with sales volume.
3. **Absence of Defect Information**: Pre-launch specifications only describe design intent and claimed features; they cannot anticipate manufacturing flaws, firmware instability, or thermal throttling. Post-launch ratings are dominated by defects and unmet expectations, which are absent from pre-launch specifications.

---

## 5. Residual Target Prediction Test

To definitively test whether the LLM aspects contain any signal for the composite target or its components after controlling for price, brand, and category, we fit a baseline Ridge model on `[Price, Category, Brand]` and correlated the test residuals ($y - \hat{y}_{\text{baseline}}$) against:
1. The 9 LLM Aspect scores
2. Raw specification text TF-IDF features

### Residual Prediction Results:

| Feature Source | Correlation with Residual ($\rho$) | Interpretation |
| :--- | :---: | :--- |
| **LLM Aspects** | **-0.119** | **Negative / Zero Signal.** Adding LLM aspects introduces noise and distorts predictions. |
| **Raw TF-IDF Tokens** | **+0.336** | **Strong Positive Signal.** Specific factual tokens (e.g., specific sensor models, battery mAh, wireless protocols) explain meaningful variance. |

---

## 6. Scientific Conclusion for the Rescue Decision

The Target-Mismatch Hypothesis cannot justify rescuing the LLM aspect bridge:
- If the problem were merely that specifications cannot predict volume, LLM aspects would still predict within-category ratings. They do not ($\bar{\rho} = -0.145$).
- If the target were fundamentally unsuited for textual specification input, raw text representations would also fail. However, raw TF-IDF features capture residual signal ($\rho = +0.336$), whereas LLM aspect ratings fail ($\rho = -0.119$).
- Therefore, the failure stems directly from **the LLM aspect transformation itself**: it projects rich technical tokens into 9 coarse, subjective, category-confounded ratings that destroy the predictive information originally present in the technical text.
