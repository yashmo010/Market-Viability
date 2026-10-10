# Paper Story Options: Strategic Reframing Assessment

**Document**: `audit/contribution/PAPER_STORY_OPTIONS.md`  
**Purpose**: Formulate, evaluate, and rank three distinct scientific paper narratives based strictly on the verified empirical evidence.

---

## Option 1 (STRONGEST): The Boundary & Epistemic Limits Paper (Candidate D)

### 1. Title Concept
> *"When Can Product Specifications Predict Market Success? Empirical Limits of Launch-Blind Forecasting and the Dominance of Category and Brand Priors"*

### 2. Central Research Question
Under what market and product conditions can pre-launch technical specifications forecast subsequent consumer adoption, and where do historical category and brand priors fundamentally dominate?

### 3. Main Hypothesis
Technical specifications carry verifiable signals of functional and experiential quality that predict market outcomes in spec-expressive personal electronics, but this signal is strictly bounded: it collapses in capacity-only appliances and is completely overshadowed by brand equity in mature, commoditized product categories.

### 4. Key Evidence
- **Asymmetric Aspect Recoverability**: Specifications encode utility ($r = 0.53$), build quality ($r = 0.51$), and durability ($r = 0.53$), but fail completely on after-sales service ($r = 0.07$) and subjective design appeal ($r = 0.21$).
- **Category Dissociation**: Smartwatches achieve strong within-category specification ranking ($\rho = 0.415$), whereas ice makers collapse (bridging fidelity $r \approx 0.04$) because capacity numbers ("26 lb/day") encode zero experiential reliability.
- **Brand Dominance in Commoditized Markets**: In headphones and power banks, specifications are commoditized; removing brand tier causes within-category correlation to collapse from positive to strongly negative ($\rho = -0.316$ and $-0.274$).
- **Autonomous Semantic Signal**: LLM aspects alone without metadata achieve $\rho = 0.526$ ($\text{AUC} = 0.886$) across 124 forward-in-time products.
- **Oracle Diagnostic**: The operational specification model captures $74.5\%$ of the rank correlation ceiling ($\rho = 0.562$ vs. $0.754$) and $55.6\%$ of the squared correlation achieved by an oracle model trained on true post-launch reviews.

### 5. Main Negative Result
- **Baselines Beat Proposed Model on Pooled Metrics**: Category + Brand Ridge ($\rho = 0.712$) and GBDT ($\rho = 0.698$) outperform the proposed LLM-bridged model ($\rho = 0.562$).
- **Between-Category Confound**: Simple Category Median achieves $\rho = 0.691$ pooled because of large between-category target shifts.
- **LLM Estimation Noise**: Adding LLM bridged aspects to clean metadata reduces performance from $\rho = 0.726$ to $0.562$.

### 6. Core Scientific Contribution
An honest, definitive empirical map establishing the epistemic boundaries of pre-launch product forecasting. Demonstrates that while LLMs can autonomously extract physical quality dimensions from text, pooled pre-launch forecasting is primarily governed by category and brand priors, with specification signals operating within narrow, identifiable category boundaries.

### 7. Why It Is Novel
Virtually all prior literature on e-WOM and product success relies on post-launch reviews (Chevalier & Mayzlin, Archak et al., Luca). This is the first study to test launch-blind forecasting under strict temporal isolation and systematically map where pre-launch design signals exist vs. where they fail.

### 8. Why a Reviewer Might Care
Reviewers in top-tier computer science, management science, and e-commerce venues are fatigued by papers claiming "our new LLM beats everything" on synthetic or leaky benchmarks. A rigorous, methodologically airtight study that exposes why simpler baselines win, identifies between-category confounds, and proves where text actually adds value is refreshing, highly credible, and immediately citable.

### 9. Biggest Reviewer Objection
> *"If simple metadata baselines achieve $\rho = 0.712$, why bother with the complex LLM bridging pipeline at all?"*
- **Rebuttal**: Metadata models are black-box lookup tables on historical brands and category intercepts; they cannot evaluate a new product design, suggest specification changes, or provide explanatory feedback. The LLM pipeline provides actionable, interpretable quality dimensions (utility, durability) that enable design-level screening for new entrants where brand lookups are useless.

### 10. Required Experiments
**NONE**. All necessary within-category, cold-start, ablation, and baseline comparisons are already computed and validated (`14/14 passed`).

### 11. Required Manuscript Changes
- Rewrite Abstract and Introduction to frame the paper around the investigation of boundaries rather than a horse-race claim of superior accuracy.
- Elevate Section V ("Scope and Boundary Conditions") to be the central empirical finding of the paper.
- Present the baseline comparisons honestly in Section IV/V, explaining the role of between-category shifts.

### 12. Publication Risk
**LOW TO MODERATE**. High scientific integrity; immune to hostile peer review because all limitations and baseline superiorities are openly stated and explained.

---

## Option 2 (SECOND-BEST): The Methodological Framework & Calibrated Decision Support Paper (Candidate E)

### 1. Title Concept
> *"Launch-Blind Product Viability Estimation: A Calibrated Decision-Support Framework with Reliability Weighting and Measured Abstention"*

### 2. Central Research Question
How can a machine learning system estimate pre-production product viability from unstructured specifications while explicitly measuring, calibrating, and exposing its own epistemic uncertainties to decision-makers?

### 3. Main Hypothesis
A pre-launch decision-support pipeline combining skeptic-prompted aspect bridging, monotonic shape constraints, and empirical fidelity weighting can provide interpretable, economically consistent design feedback while reliably abstaining when specifications lack predictive grounding.

### 4. Key Evidence
- **Monotonic Economic Constraints**: Guaranteed non-increasing price effects and non-decreasing quality attributions in SHAP explanations without statistical loss in ranking performance ($\Delta \rho = +0.020, p=0.453$).
- **Calibrated Honesty Layer**: Reliability-weighted confidence matches measured per-aspect empirical fidelity ($r \approx 0.50$ vs. $0.07$).
- **Abstention Mechanism**: The system successfully detects flat, non-grounded capacity specifications (e.g. ice makers) and withholds false-precision predictions.
- **End-to-End Operational Pipeline**: Demonstrated across 43,000+ reviews, 5 categories, and deployed interactive decision dashboard.

### 5. Main Negative Result
- The framework does not achieve state-of-the-art predictive accuracy on pooled metrics compared to unconstrained trees or metadata models.

### 6. Core Scientific Contribution
A complete, open-source architectural and methodological framework for pre-launch product analytics that treats model limitations and calibration as primary system components rather than post-hoc disclosures.

### 7. Why It Is Novel
Existing decision-support systems in product design treat predictions as uncalibrated point estimates. This paper introduces the first system with measured trust tiers, skeptic prompt filters (adjective blindness), and structural monotonicity for pre-launch e-commerce.

### 8. Why a Reviewer Might Care
Appeals strongly to applied AI, software engineering, and human-AI interaction tracks (e.g. IEEE Transactions on Engineering Management, ACM IUI).

### 9. Biggest Reviewer Objection
> *"This is primarily an engineering system paper rather than an empirical discovery."*

### 10. Required Experiments
**NONE**. Functional, architectural, and evaluation pipelines already complete.

### 11. Required Manuscript Changes
- Reframe paper around the software engineering, decision-support, and calibration architecture.
- Downplay competitive ML benchmark claims; emphasize human-in-the-loop interpretability and the "spec coach" design.

### 12. Publication Risk
**MODERATE**. Strong for engineering management or applied system venues; slightly less suited for pure ML science tracks.

---

## Option 3 (WEAKEST): The Cold-Start Semantic Forecasting Paper (Candidate B)

### 1. Title Concept
> *"Pre-Launch Product Success Forecasting for Unknown Brands: Semantic Quality Extraction from Technical Specifications"*

### 2. Central Research Question
Can an LLM semantic extractor forecast post-launch market adoption for greenfield products and unknown brands where historical sales records and brand reputation do not exist?

### 3. Main Hypothesis
By bypassing brand equity and focusing exclusively on intrinsic specification attributes, LLM aspect bridging enables cold-start success prediction for new market entrants.

### 4. Key Evidence
- On 82 test products from brands completely absent from the training catalog, the proposed model achieves $\rho = 0.585$, while a brand lookup baseline fails completely (variance = 0).
- Within Smartwatches on unseen brands ($n=28$), the proposed model achieves $\rho = 0.253$, while TF-IDF fails ($\rho = -0.406$).

### 5. Main Negative Result
- **Category Mean Beating Model on Cold-Start**: On the exact same 82 unseen-brand products, Category Mean alone achieves $\rho = \mathbf{0.686}$ and Category Median achieves $\rho = \mathbf{0.663}$, beating the proposed model ($\rho = 0.585$).
- In headphones and power banks, cold-start specification prediction produces negative rank correlations.

### 6. Core Scientific Contribution
Demonstrating that specifications contain semantic signal in specific cold-start electronics categories.

### 7. Why It Is Novel
Direct focus on the "unknown brand" cold-start problem in physical product manufacturing.

### 8. Why a Reviewer Might Care
Relevant to small business innovation and entrepreneurship.

### 9. Biggest Reviewer Objection (FATAL FLAW)
> *"You claim the model enables cold-start prediction for unseen brands, but simply predicting the category mean on those exact 82 products achieves $\rho = 0.686$, which is higher than your model's $\rho = 0.585$. Your cold-start correlation is driven by category priors, not specification intelligence."*
- **Rebuttal Difficulty**: Extremely difficult to defend without retreating to within-category sub-analyses.

### 10. Required Experiments
Would require expanding the unseen-brand dataset to dozens of categories to test whether the cold-start signal survives cross-category pooling.

### 11. Required Manuscript Changes
Extensive restructuring around brand cold-start.

### 12. Publication Risk
**HIGH**. A competent reviewer running or requesting the Category Mean baseline on the unseen-brand subset will immediately reject the central thesis.

---

## Summary Ranking of Paper Options

1. **Rank 1 (STRONGEST)**: **Option 1 — The Boundary & Epistemic Limits Paper (Candidate D)**  
   *Completely bulletproof against reviewer scrutiny. Converts potential weaknesses into the central scientific discovery.*
2. **Rank 2 (SECOND-BEST)**: **Option 2 — The Methodological Framework & Honesty Layer Paper (Candidate E)**  
   *Strong applied systems paper emphasizing decision support, monotonicity, and calibration.*
3. **Rank 3 (WEAKEST)**: **Option 3 — The Cold-Start Semantic Forecasting Paper (Candidate B)**  
   *Fragile; vulnerable to the fact that Category Mean achieves $\rho = 0.686$ on unseen brands.*
