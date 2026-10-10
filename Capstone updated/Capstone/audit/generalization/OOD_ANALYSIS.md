# Out-Of-Domain (OOD) Detection and Reliability Gating Audit

**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher, Experimental Scientist, and Hostile Peer Reviewer  
**Focus**: Investigating whether the current pipeline supports a legitimate Out-Of-Domain (OOD) warning or reliability gating mechanism.

---

## 1. The Core Scientific Question

> *Can the existing pre-launch prediction pipeline detect when an incoming product specification falls outside the operational domain where its viability estimates are statistically reliable?*

A hostile reviewer objection:
> *"The model produces a point estimate $\hat{y} \in [0, 100]$ for any arbitrary input specification string, even if the category is unobserved, the specifications are gibberish, or the product represents a novel technological paradigm. Without an audited OOD detection mechanism, the model invites silent catastrophic failure in production deployment."*

---

## 2. Evaluation of Candidate OOD Signals in Current Pipeline

We investigated seven potential signals available within the codebase:

| Candidate Signal | Data Source in Repo | Feasibility | Empirical Correlation with Reliability | Legitimate OOD Signal? |
|---|---|---|---|---|
| **1. Category Familiarity** | `strict_temporal/frozen_state/category_profiles.json` | **Fully Feasible** | Binary gating: unobserved categories have LOCO $\rho = -0.106$. If category $\notin \mathcal{C}_{\text{train}}$, model is guaranteed OOD. | **YES (HARD GATING)**: Pipeline must abort or flag any product from an unprofiled category. |
| **2. Specification Completeness Index ($S_{\text{comp}}$)** | Bullet count, word count, price, numeric specs regex | **Fully Feasible** | Direct monotonic relationship: High ($S_{\text{comp}} \ge 0.90, \rho = 0.631$) vs Low ($S_{\text{comp}} < 0.90, \rho = -0.284$). | **YES (RELIABILITY WARNING)**: Products with $S_{\text{comp}} < 0.90$ should trigger a "Low Specification Expressiveness" warning. |
| **3. Distance from Training Feature Distribution (Mahalanobis / GMM)** | `train_features.parquet` (Price, aspect distributions) | **Partially Feasible** | Extreme price outliers ($>\$500$) or extreme aspect combinations exhibit higher prediction residual variance. | **YES (SOFT WARNING)**: Normalized Euclidean or Mahalanobis distance $> 3.0\sigma$ from category centroid indicates OOD pricing/aspects. |
| **4. Brand Familiarity / Tier** | `brand_tier_map.json` | **Not an OOD Gating Signal** | Unseen brands with Tier 0 fallback achieve $\rho = 0.585$ (higher than seen brands $\rho = 0.346$). | **NO**: Being an unseen brand does NOT mean the product is OOD; specification ranking works well for new entrants. |
| **5. LLM Aspect Extraction Confidence** | `aspect_scores.jsonl` confidence scores | **Limited Feasibility** | Extraction prompt outputs confidence, but bridging prompt outputs deterministic aspect estimates without calibrated Bayesian uncertainty. | **NO (CURRENTLY UNCALIBRATED)**: Bridge prompt does not produce valid epistemic uncertainty. |
| **6. Tree Ensemble Disagreement** | XGBoost tree leaf variance | **Feasible via Subsampling** | Variance across individual tree predictions in hist gradient boosting can be extracted, but is not currently surfaced in `predict_test.py`. | **NO (NOT SURFACED)**: Not currently exposed in deployment interface. |
| **7. Cross-Prompt LLM Disagreement** | Multiple prompt variants (Skeptic vs Optimist) | **Demonstrated in Issue 4** | Mean spread across prompts was $\pm 0.32$ aspect points. | **EXPERIMENTAL**: Requires multi-pass LLM invocation, increasing latency and cost. |

---

## 3. Audited OOD Warning Rules Supported by Empirical Evidence

Based on our empirical findings in Issues 1–5, the current system legitimately supports a **Two-Tier OOD & Reliability Gating Rule**:

```
                       INCOMING SPECIFICATION
                                 │
                     [Category in Profile?]
                                 │
                   NO ───────────┴─────────── YES
                   │                           │
          [ABORT / REJECT]             [S_comp >= 0.90?]
       "Fatal: Category Unseen"                │
       (LOCO Rho = -0.106)       NO ───────────┴─────────── YES
                                 │                           │
                        [FLAG WARNING]               [PROCEED CLEAN]
                      "Low Expressiveness"         "Valid In-Domain"
                       (Rho = -0.284)               (Rho = 0.631)
```

### Rule 1: Category Membership Gate (Strict Precondition)
- If `category` is not in the frozen set of 5 calibrated categories (`bluetooth_speakers`, `ice_makers`, `power_banks`, `smartwatches`, `wireless_headphones`):
  - **Action**: Reject inference. Return `OOD_CATEGORY_ERROR`.
  - **Rationale**: LOCO experiments prove that cross-category zero-shot transfer fails ($\rho = -0.106$). The model cannot reliably predict viability in uncalibrated verticals.

### Rule 2: Specification Expressiveness Gate (Quality Warning)
- Compute reproducible completeness index $S_{\text{comp}}$:
  $$S_{\text{comp}} = 0.35 \min\left(\frac{W}{200}, 1\right) + 0.35 \min\left(\frac{B}{5}, 1\right) + 0.15 \mathbb{I}(\text{Price} > 0) + 0.15 \min\left(\frac{N_{\text{num}}}{5}, 1\right)$$
- If $S_{\text{comp}} < 0.90$:
  - **Action**: Output prediction accompanied by a prominent disclaimer: `LOW_SPECIFICATION_CONFIDENCE_WARNING: Specification lacks sufficient engineering depth or numeric disclosures for reliable viability estimation.`
  - **Rationale**: In products with $S_{\text{comp}} < 0.90$, empirical rank correlation drops to $\rho = -0.284$.

---

## 4. Current Limitations and Manuscript Requirements

1. **No Calibrated Probabilistic Error Bounds**:
   - The model produces a deterministic point estimate without Bayesian posterior intervals. Prediction intervals currently displayed in UI mockups represent heuristic heuristic spans rather than calibrated conformal prediction intervals.
2. **Manuscript Transparency Requirement**:
   - The paper must explicitly disclose:
     > *"The current implementation does not incorporate automated out-of-distribution (OOD) epistemic uncertainty estimation. Predictions are validated only for specifications within pre-profiled categories with completeness scores $S_{\text{comp}} \ge 0.90$. Deployment to novel verticals or uncurated marketing copy requires prior category profiling and explicit specification expressiveness checks."*
