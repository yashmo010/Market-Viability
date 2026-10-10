# Final System Architecture Specification (Machine-Audited)

This specification defines the complete, verified, and audited system architecture for the final publication diagram (Figure 1).

## 1. Information Boundary & Stages
- **Boundary**: Strict launch-blind information boundary. Only pre-launch inputs are admitted.
- **Stage 1 (Pre-Launch Inputs)**:
  - Technical bullet specifications (e.g., mAh, hours, Bluetooth version, IP rating, dimensions).
  - Launch price (USD).
  - Product category (Exactly 5 categories: Bluetooth speakers, Ice makers, Power banks, Smartwatches, Wireless headphones).
  - Brand name (mapped to pre-cutoff historical brand tier: 0 = unseen/startup, 1 = emerging, 2 = established).
- **Stage 2 (Semantic Extraction & Cold-Start Enrichment)**:
  - **LLM Aspect Extraction**: Null-forcing, evidence-grounded extraction producing 9 scalar aspect scores:
    `value_for_money`, `utility`, `ease_of_use`, `reliability`, `design_appeal`, `after_sales`, `build_quality`, `durability`, `repairability`.
  - **Specification Density Metrics**: Objective item-side richness measures:
    - `spec_bullet_count` (number of technical specifications provided).
    - `spec_word_count` (total technical word length).
    - `spec_num_density` (ratio of numeric technical tokens to words).
- **Stage 3 (Structured Feature Vector - 24 Features)**:
  - 9 LLM Aspect Scores
  - 9 Category Aspect Mention Rates
  - 3 Specification Density Metrics
  - 3 Launch Metadata Features (`price`, `brand_tier`, `category`)
- **Stage 4 (Downstream Gradient-Boosted Decision Tree - XGBoost)**:
  - Monotonic priors enforcing directional consistency (e.g., higher build quality $\ge 0$, higher price $\le 0$).
  - Hist tree method, $L_2$ regularization, learning rate = 0.05, max depth = 5.
- **Stage 5 (Inference Output)**:
  - Predicted `SuccessScore` $[0, 100]$: A review-derived market-success proxy representing post-launch consumer viability.
- **Stage 6 (Temporal Holdout & Evaluation Barrier)**:
  - Strictly quarantined post-cutoff ground truth labels (October 31, 2021).
  - 0% leakage into model fitting or feature scaling.

## 2. Forbidden Elements in Visual Diagrams
- NO "Air Fryers" (only the 5 canonical categories).
- NO "Sales / Revenue Prediction" labels (strictly review-derived viability proxy).
- NO backward flow from post-launch review labels into the feature path.
