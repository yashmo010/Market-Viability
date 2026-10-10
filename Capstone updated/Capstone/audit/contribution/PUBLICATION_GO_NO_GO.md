# Publication Go / No-Go Assessment

**Document**: `audit/contribution/PUBLICATION_GO_NO_GO.md`  
**Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher and Hostile Peer Reviewer  

---

## 1. Assessment Classification

$$\mathbf{B\ —\ Publishable\ After\ Reframing}$$

> *"The original hypothesis of superior predictive accuracy over all baselines fails, but a scientifically meaningful, rigorous, and highly citable paper can be built from the existing evidence by reframing it as an empirical boundary and epistemic limits investigation."*

---

## 2. Why Not A, C, D, or E?

- **Why Not A (Strong publishable contribution as currently written)?**  
  The current manuscript draft claims that the proposed model "outperforms baselines", that monotonic constraints "significantly boost AUC from 0.826 to 0.903", and that the LLM bridge provides four-fifths of review information. These claims are empirically contradicted by the baseline and ablation audits. Submitting the paper in its current framing would result in immediate desk rejection or scathing reviewer critiques.
- **Why Not C (Publishable only after additional experiments)?**  
  The project does not lack data or experiments. We have 631 products, 43,000+ extracted reviews, a strictly sealed forward-in-time temporal holdout ($N=124$), 14 baselines, 11 ablations, 2,000 paired bootstrap resamples, multi-seed distributions, and an oracle ceiling. Running more experiments (e.g. tuning more tree depths or prompt variations) would not alter the fundamental finding that category and brand priors dominate pooled prediction. The evidence needed to support a strong paper is already complete.
- **Why Not D (Major redesign required)?**  
  The experimental design, data hygiene, and validation infrastructure are already at state-of-the-art standards. Issues 1 through 6 solved temporal leakage, target scaling, statistical paired testing, LLM prompt engineering, and external categorization. The pipeline does not need to be rebuilt.
- **Why Not E (Abandon current study)?**  
  Abandoning the project would be a grave scientific mistake. A negative result—demonstrating that pooled pre-launch product success prediction is heavily confounded by category-level shifts, that LLMs inject estimation noise into mature brand signals, and that specifications only carry signal in spec-expressive electronics—is a **valuable scientific discovery**. The literature is saturated with unreplicable papers claiming miraculous LLM accuracy. A paper that proves where the limits lie and provides an honest decision-support architecture is a major contribution.

---

## 3. The Path to Publication: The Reframing Blueprint

To achieve publication in a reputable venue (e.g. IEEE Transactions, ACM SIGKDD, Decision Support Systems, or Management Science tracks):

1. **Adopt Option 1 (The Boundary & Epistemic Limits Paper)**:
   - Frame the paper around: *"When Can Product Specifications Predict Market Success? Empirical Limits of Launch-Blind Forecasting and the Dominance of Category and Brand Priors."*
2. **Present the Negative Result as a Primary Finding**:
   - Openly show the baseline table in the main text. Explain why Category + Brand Ridge ($\rho = 0.712$) and GBDT ($\rho = 0.698$) beat the proposed model ($\rho = 0.562$).
   - Demonstrate through within-category analysis that pooled metrics are confounded by between-category shifts.
3. **Highlight the Genuine Positive Contributions**:
   - Asymmetric aspect recoverability ($r \approx 0.50$ for physical vs. $r \approx 0.07$ for service).
   - Category dissociation: why specifications work in smartwatches ($\rho = 0.415$) but fail in capacity-only ice makers (fidelity $r \approx 0.04$).
   - Brand dominance: how commoditization decouples sales from specifications in headphones and power banks.
   - Interpretable, monotonic design levers and calibrated abstention for pre-production decision-makers.

---

## 4. Final Recommendation
**PROCEED WITH REFRAMING PLAN**. Complete the final assessment report and await user direction on manuscript text alignment.
