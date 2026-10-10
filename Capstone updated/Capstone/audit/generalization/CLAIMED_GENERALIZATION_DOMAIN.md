# Claimed Generalization Domain vs Empirical Evidence Audit

**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher, Experimental Scientist, and Hostile Peer Reviewer  
**Scope**: Complete inventory of every claim in the manuscript, repository, and design briefs implying generalization across products, categories, brands, time horizons, and deployment environments.

---

## 1. Domain Claims Inventory

| Claim Statement | Text Location | Population Implied | Empirical Evidence Available | Supported by Evidence? | Required Manuscript Qualification |
|---|---|---|---|---|---|
| "Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging" | Title & Abstract | All commercial products launched across global e-commerce | 631 Amazon US consumer hardware/tech products across 5 categories | **PARTIALLY SUPPORTED (QUALIFIED)** | Restrict scope explicitly to *consumer electronic hardware and small appliances with experiential feature specifications on Amazon US*. |
| "Estimates the aspect profile of an unseen product before launch" | Abstract (L18) | Unseen products across arbitrary categories | 124 temporal test products across 5 pre-specified categories | **SUPPORTED (WITHIN KNOWN CATEGORIES)** | Qualify that "unseen product" applies to products within categories that have established training reference profiles; unseen *categories* fail. |
| "The lesson generalizes. Where a category's specifications describe experiential attributes... aspect bridging works." | Main Text Section VI (L203) | All categories with experiential vs functional specs | 5 categories: 2 high-spec (smartwatches, speakers), 1 mixed (headphones), 2 low/functional (ice makers, power banks) | **SUPPORTED WITH BOUNDARIES** | Clearly delineate the boundary condition: experiential spec expressiveness is a required precondition; purely functional or capacity-only categories fail. |
| "Enables pre-launch product viability prediction across e-commerce" | System Architecture & Intro | General e-commerce catalog (apparel, groceries, software, industrial) | Zero non-hardware, non-appliance data | **UNSUPPORTED** | Remove broad e-commerce claims; state that non-hardware and non-experiential categories have not been validated. |
| "Generalization to unseen brands via Tier 0 fallback" | Methodology (Brand Model) | New market entrants and startup brands with zero catalog history | 82 test products from 70 unseen brands evaluated with Tier 0 fallback | **WELL SUPPORTED** | Maintain Tier 0 fallback; report empirical performance ($\rho = 0.585, \text{AUC} = 0.929$ on unseen brands). |
| "Cross-category transfer to novel product domains without retraining" | System Architecture (App) | Zero-shot transfer to previously unseen product verticals | 5 Leave-One-Category-Out (LOCO) folds ($n=7, 36, 19, 39, 23$) | **UNSUPPORTED / FALSIFIED** | LOCO mean $\rho = -0.106$. Cross-category transfer without in-domain category grounding completely collapses. Manuscript must explicitly disclaim zero-shot category transfer. |
| "Predicts long-term market success for future product launches" | Abstract & Marketing Explainer | Future product lifecycle out to multi-year horizons | Temporal test set covers launches Nov 2021 to Feb 2023 (up to 16 months post-cutoff) | **SUPPORTED UP TO 12 MONTHS** | Qualify temporal horizon: performance is robust through 12 months ($\rho = 0.562$ near, $\rho = 0.624$ mid), but decays at 16+ months ($\rho = 0.364, n=11$). |
| "Specification expressiveness determines prediction fidelity" | Discussion & Spec Coach | Expressiveness across all consumer specifications | Specification completeness score terciles (High: $\rho=0.631$; Med: $\rho=0.508$; Low: $\rho=-0.284$) | **STRONGLY SUPPORTED** | Retain as a core scientific discovery with explicit completeness score thresholding ($S_{\text{comp}} \ge 0.90$). |
| "Predictor does not rely on brand memorization" | Discussion & Robustness | Predictions driven by specs rather than brand identity | Brand-ablated model ($\rho = 0.513$ vs Full $\rho = 0.562$); unseen brand performance ($\rho = 0.585$) | **WELL SUPPORTED** | Document that 91.3% of ranking power is retained when brand information is completely eliminated. |
| "Deployment-ready for external e-commerce platforms" | Operating Manual & App | Platforms outside Amazon US (Shopify, Kickstarter, Walmart) | 100% Amazon US platform data | **UNVERIFIED (EXTERNAL DATASET UNAVAILABLE)** | State explicitly as a limitation that external validation across other e-commerce platforms was not conducted due to lack of pre-launch spec and outcome proxy datasets. |

---

## 2. Summary of Claim Boundary Governance

1. **Category Boundaries**:
   - Supported: Pre-profiled physical consumer tech and small appliances with rich experiential specifications.
   - Unsupported: Zero-shot unobserved categories (LOCO $\rho \le 0$); non-hardware verticals (apparel, groceries, commodities).

2. **Brand Boundaries**:
   - Supported: Both established brands (Tiers 1–3, $\rho = 0.346$) and new market entrants with zero footprint (Tier 0 fallback, $\rho = 0.585$).

3. **Temporal Boundaries**:
   - Supported: Forward-in-time deployment up to 12 months post-cutoff.
   - Uncertain / Decaying: Horizons beyond 12 months subject to technological paradigm shifts (e.g., GaN transition in power banks).

4. **Information Input Boundaries**:
   - Supported: Pre-launch specifications containing at least 5 bullet points, $\ge 200$ words, and numeric engineering specifications ($S_{\text{comp}} \ge 0.90$).
   - Unsupported: Sparse, generic, or marketing-only copy ($S_{\text{comp}} < 0.90$, where $\rho = -0.284$).
