# Baseline, Model Comparison & Ablation Validity Audit Report

**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher, Experimental Scientist, and Hostile Peer Reviewer  
**Audit Protocol**: Frozen Strict Forward-in-Time Temporal Holdout ($N=507$ pre-cutoff train, $N=124$ post-cutoff test, Cutoff October 31, 2021)  
**Governing Artifacts**:
- [`audit/baselines/BASELINE_RESULTS.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/BASELINE_RESULTS.csv)
- [`audit/baselines/PAIRED_MODEL_COMPARISONS.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/PAIRED_MODEL_COMPARISONS.csv)
- [`audit/baselines/ABLATION_RESULTS.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/ABLATION_RESULTS.csv)
- [`audit/baselines/FEATURE_ACCESS_MATRIX.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/FEATURE_ACCESS_MATRIX.csv)
- [`audit/baselines/TUNING_FAIRNESS_AUDIT.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/TUNING_FAIRNESS_AUDIT.csv)
- [`audit/baselines/SEED_STABILITY.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/SEED_STABILITY.csv)
- [`audit/baselines/MANUSCRIPT_CLAIM_EVIDENCE_MATRIX.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/MANUSCRIPT_CLAIM_EVIDENCE_MATRIX.csv)
- [`tests/test_baseline_validity.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/tests/test_baseline_validity.py)

---

## 1. Executive Conclusion

### Classification:
$$\mathbf{PARTIALLY\ SEALED\ —\ MANUSCRIPT\ CLAIMS\ REQUIRE\ REVISION}$$

### Summary of Audit Findings:
1. **The Experimental Comparison is Complete and Methodologically Fair**:
   All 14 baseline and ablation variants, spanning simple empirical priors, brand/category heuristics, regularized linear models, standard non-LLM tree ensembles, and raw specification TF-IDF representations, have been evaluated under the identical sealed forward-in-time temporal holdout ($N=124$).
2. **Simpler Baselines Outperform Proposed Model on Pooled Test Correlation**:
   The skeptical reviewer's objection is **empirically confirmed**: Category + Brand Ridge ($\rho = \mathbf{0.712}$), Gradient Boosting ($\rho = \mathbf{0.698}$), Random Forest ($\rho = \mathbf{0.694}$), Category Median ($\rho = \mathbf{0.691}$), and Spec TF-IDF + Ridge ($\rho = \mathbf{0.683}$) all achieve higher pooled rank correlation than the proposed LLM-bridged model ($\rho = \mathbf{0.562}$).
3. **Within-Category Ranking Head-to-Head**:
   Once broad between-category target shifts are removed, the proposed model ($\bar{\rho}_{\text{macro}} = \mathbf{0.207}, \bar{\rho}_{\text{weighted}} = \mathbf{0.196}$) does NOT outperform GBDT ($\bar{\rho}_{\text{macro}} = \mathbf{0.414}, \bar{\rho}_{\text{weighted}} = \mathbf{0.369}$) or Category + Brand Ridge ($\bar{\rho}_{\text{macro}} = \mathbf{0.352}, \bar{\rho}_{\text{weighted}} = \mathbf{0.294}$).
4. **Cold-Start Unseen-Brand Decomposition ($N=82$)**:
   The proposed model's pooled correlation of $\rho = 0.585$ on unseen brands is lower than Category Mean alone ($\rho = \mathbf{0.686}$) and Category Median ($\rho = \mathbf{0.663}$). The pooled correlation on unseen brands is thus heavily driven by between-category intercept shifts rather than specification-driven rank ordering.
5. **Monotonic Constraints and LLM Bridge**:
   Monotonic constraints enforce specified directional modeling assumptions but do not produce a statistically significant empirical gain ($\Delta \rho = +0.020, p=0.453$). The LLM semantic bridge provides structured, interpretable aspect ratings from text alone, but introduces estimation noise that degrades ranking performance relative to pure metadata or text models.
6. **Mandatory Manuscript Revisions**:
   All manuscript claims asserting general superiority or outperforming baselines must be retracted and replaced with transparent, scientifically bounded statements.

---

## 2. Existing Model Inventory

The project evaluated seven algorithm architectures across eight distinct feature configurations:
- **Algorithms**: XGBoost (Monotone), XGBoost (Unconstrained), Gradient Boosting (GBDT), Random Forest, Ridge Regression, Elastic Net, Multi-Layer Perceptron (MLP), and Support Vector Regression (SVR).
- **Historical vs. Temporal Evaluator**:
  - Historical evaluations (Table 1) benchmarked algorithms on 5-fold CV across 631 products with post-launch extracted review aspects.
  - The audited temporal benchmark evaluates forward-in-time predictions on 124 untouched post-cutoff products using launch-blind technical specifications.
- Complete mapping documented in [`EXISTING_MODEL_COMPARISON_INVENTORY.md`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/EXISTING_MODEL_COMPARISON_INVENTORY.md).

---

## 3. Baseline Justification

To ensure a skeptical reviewer cannot claim that competitors were artificially weakened, 10 competitive baselines were constructed:
1. **Baselines A & B (Global Priors)**: Empirical scalar mean ($53.07$) and median ($52.88$) from pre-cutoff training pool.
2. **Baselines C & D (Category Priors)**: Training-set category mean and median, testing whether category identity alone explains the outcome.
3. **Baseline E (Brand-Only)**: Regressor on catalog brand footprint ($0..3$), testing whether brand equity dominates.
4. **Baseline F (Category + Brand)**: Joint linear model on category and brand indicators.
5. **Baselines G1 & G2 (Regularized Linear)**: Ridge and Elastic Net with cross-validated penalty parameter on proposed features.
6. **Baselines H1 & H2 (Conventional Tree Models)**: 112-tree Random Forest and Gradient Boosting Regressors matched to proposed tree budget.
7. **Baselines I1, I2, I3 (Specification-Only Non-LLM)**: 300-token TF-IDF unigram/bigram models fit directly on technical spec text and product titles, representing standard text-mining alternatives without LLMs.

---

## 4. Feature-Access Fairness Audit

Audited via [`FEATURE_ACCESS_MATRIX.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/FEATURE_ACCESS_MATRIX.csv):
- **Temporal Isolation**: Zero post-cutoff reviews, ratings, velocity, or sales ranks were accessible to any baseline.
- **Brand Footprint Isolation**: Brand tiers were computed strictly from the 507 pre-cutoff training products. Test products from new brands correctly mapped to tier 0.
- **Verification**: Byte-for-byte prediction reproducibility verified via `tests/test_baseline_validity.py`.

---

## 5. Hyperparameter and Tuning Fairness Audit

Audited via [`TUNING_FAIRNESS_AUDIT.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/TUNING_FAIRNESS_AUDIT.csv):
- **Proposed Model**: 112 estimators selected via 5-fold CV early stopping on pre-cutoff training folds.
- **Ridge Regression**: $\alpha$ grid search ($[0.01..100.0]$) evaluated across identical 5-fold CV folds ($\alpha=10.0$ selected).
- **Tree Baselines**: Matched tree count (112) and depth (5) to ensure computational equity.
- **Test Set Protection**: Zero test-set loss was used to tune any parameter.

---

## 6. Canonical Proposed Model Re-Run

Re-running the primary proposed model under the frozen protocol reproduces the sealed baseline metrics exactly:
- **Spearman $\rho$**: **$0.562$** ($95\%$ CI $[0.412, 0.682]$, $p = 1.09 \times 10^{-11}$)
- **Top vs. Bottom Quintile AUC**: **$0.890$** ($95\%$ CI $[0.791, 0.966]$)
- **RMSE**: **$21.12$**
- **MAE**: **$17.84$**
- **Mean Within-Category $\rho$**: **$0.207$**
- **Prediction File Hash**: `20ac4b1e670fe3f45fb79d3e3abe1ece191466b5a09a63d94ed413d871f627c2` (Exact match).

---

## 7. Baseline Results Summary Table

| Model | Feature Set | Spearman $\rho$ | $95\%$ CI | $p$-value | AUC | RMSE | MAE |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Baseline F: Category + Brand** | Category + Brand Tier | **0.712** | $[0.626, 0.778]$ | $1.90 \times 10^{-20}$ | **0.994** | 17.79 | 14.33 |
| **Baseline H2: Gradient Boosting** | Full Features | **0.698** | $[0.597, 0.778]$ | $2.12 \times 10^{-19}$ | **0.970** | 20.27 | 17.25 |
| **Baseline H1: Random Forest** | Full Features | **0.694** | $[0.579, 0.779]$ | $3.98 \times 10^{-19}$ | **0.993** | 19.46 | 16.62 |
| **Baseline D: Category Median** | Category Grouping | **0.691** | $[0.575, 0.781]$ | $6.84 \times 10^{-19}$ | **0.980** | **15.82** | **12.94** |
| **Baseline I2: Spec TF-IDF + Price + Cat** | TF-IDF + Metadata | **0.688** | $[0.577, 0.772]$ | $1.09 \times 10^{-18}$ | **0.979** | 16.92 | 14.03 |
| **Baseline I1: Spec TF-IDF + Ridge** | 300 TF-IDF Tokens | **0.683** | $[0.572, 0.764]$ | $2.53 \times 10^{-18}$ | **0.979** | 17.00 | 14.15 |
| **Baseline C: Category Mean** | Category Grouping | **0.671** | $[0.548, 0.762]$ | $1.41 \times 10^{-17}$ | **0.980** | 17.18 | 14.15 |
| **Baseline G2: Elastic Net** | Full Features | **0.652** | $[0.534, 0.737]$ | $2.29 \times 10^{-16}$ | **0.977** | 19.14 | 15.32 |
| **Baseline G1: Ridge Regression** | Full Features | **0.651** | $[0.528, 0.738]$ | $2.84 \times 10^{-16}$ | **0.977** | 18.31 | 14.60 |
| **Proposed Model (XGBoost Monotone)** | Full Features | **0.562** | $[0.412, 0.682]$ | $1.09 \times 10^{-11}$ | **0.890** | 21.12 | 17.84 |
| **Baseline E: Brand-Only** | Brand Tier (0..3) | **0.227** | $[0.088, 0.370]$ | $0.011$ | **0.640** | 24.51 | 19.76 |
| **Baseline A: Global Mean** | Constant Prior | **0.000** | $[0.000, 0.000]$ | $1.000$ | **0.500** | 24.08 | 20.27 |
| **Baseline B: Global Median** | Constant Prior | **0.000** | $[0.000, 0.000]$ | $1.000$ | **0.500** | 24.12 | 19.99 |

---

## 8. Paired Statistical Comparisons

Evaluating paired predictions on the identical 124 test products via 2,000-replicate paired bootstrap and paired $t$-tests:

1. **Proposed Model vs. Category Mean**:
   - $\Delta \rho = -0.109$ ($95\%$ CI $[-0.213, -0.018]$, bootstrap $p = 0.014$).
   - $\Delta \text{AUC} = -0.090$ ($95\%$ CI $[-0.183, -0.022]$, $p = 0.005$).
   - Category Mean achieves significantly higher pooled rank correlation and discrimination.
2. **Proposed Model vs. Category + Brand**:
   - $\Delta \rho = -0.150$ ($95\%$ CI $[-0.260, -0.047]$, bootstrap $p = 0.003$).
   - $\Delta \text{AUC} = -0.103$ ($95\%$ CI $[-0.203, -0.031]$, $p < 0.001$).
3. **Proposed Model vs. Spec TF-IDF + Ridge**:
   - $\Delta \rho = -0.120$ ($95\%$ CI $[-0.246, -0.010]$, bootstrap $p = 0.035$).
   - Raw specification text n-grams statistically significantly outperform the LLM-bridged model on pooled ranking.
4. **Proposed Model vs. Gradient Boosting (GBDT)**:
   - $\Delta \rho = -0.136$ ($95\%$ CI $[-0.258, -0.022]$, bootstrap $p = 0.014$).
   - GBDT significantly outperforms monotonic XGBoost on the identical feature matrix.
5. **Proposed Model vs. Brand-Only Baseline**:
   - $\Delta \rho = +0.335$ ($95\%$ CI $[+0.109, +0.520]$, bootstrap $p = 0.002$).
   - The proposed model is significantly superior to using brand tier alone.

---

## 9. Component Ablation Results

| Ablation Condition | Spearman $\rho$ | AUC | RMSE | MAE | $\Delta \rho$ vs Full | Interpretation |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Ablation A: Remove LLM Aspects** | **0.726** | **0.994** | **17.12** | **13.92** | **+0.164** | **Ablation improves pooled fit**: Bridged aspects add noise to metadata |
| **Ablation H: Text-Only (TF-IDF XGB)** | **0.708** | **0.984** | **17.01** | **14.05** | **+0.146** | High-dimensional hardware tokens outperform coarse 0-10 aspect scores |
| **Ablation F3: Remove Commercial Aspects** | **0.667** | **0.964** | **20.21** | **17.27** | **+0.105** | Subjective after-sales & design appeal aspects degrade prediction |
| **Ablation I: Minimal Proposed Model** | **0.620** | **0.970** | **17.65** | **14.51** | **+0.058** | Pruning noisy aspects improves accuracy |
| **Ablation F1: Remove Physical Build Aspects** | **0.573** | **0.886** | **19.24** | **15.89** | **+0.011** | Build quality aspects have marginal impact |
| **Ablation C: Remove Category** | **0.571** | **0.916** | **21.37** | **17.95** | **+0.009** | Category is redundant given price and technical aspects |
| **Full Proposed Model** | **0.562** | **0.890** | **21.12** | **17.84** | Reference | Canonical baseline |
| **Ablation D: Remove Monotonic Constraints** | **0.542** | **0.879** | **21.52** | **18.05** | **-0.020** | Monotonic constraints induce negligible empirical shift ($p = 0.453$) |
| **Model 2: LLM Aspects Alone** | **0.526** | **0.886** | **22.58** | **18.98** | **-0.036** | Autonomous semantic quality signal without metadata |
| **Ablation G: Numeric-Only (Price + Brand)** | **0.512** | **0.953** | **23.47** | **18.78** | **-0.050** | Removing all text/aspects degrades performance |
| **Ablation F2: Remove Experiential Aspects** | **0.494** | **0.842** | **21.08** | **17.71** | **-0.068** | Utility, ease of use, and reliability are the most informative aspects |
| **Ablation B: Remove Brand** | **0.458** | **0.842** | **22.47** | **18.91** | **-0.104** | Critical drop; within-category ranking collapses to $-0.180$ |
| **Ablation E: Raw Target (Unnormalized)** | **0.404** | **0.830** | **10.44** | **8.21** | **-0.158** | Target normalization is mathematically vital |
| **Oracle Diagnostic (Review Aspects)** | **0.754** | **0.992** | **15.42** | **12.45** | **+0.191** | Empirical ceiling if true review aspects were known at launch |

---

## 10. LLM Bridge Incremental-Value Analysis

We directly evaluated the incremental contribution of the LLM semantic bridge against non-LLM baselines:
- **Model 1 (Non-LLM Spec Baseline: TF-IDF + Ridge)**: $\rho = 0.683, \text{AUC} = 0.979, \text{RMSE} = 18.23, \text{MAE} = 14.61$.
- **Model 2 (LLM Aspects Alone, No Metadata)**: $\rho = 0.526, \text{AUC} = 0.886, \text{RMSE} = 22.58, \text{MAE} = 18.98$.
- **Model 3 (Full Proposed Model: Aspects + Brand + Price + Cat)**: $\rho = 0.562, \text{AUC} = 0.890, \text{RMSE} = 21.12, \text{MAE} = 17.84$.
- **Ablation A (Remove LLM Aspects: Metadata Only)**: $\rho = \mathbf{0.726}, \text{AUC} = \mathbf{0.994}, \text{RMSE} = \mathbf{17.12}, \text{MAE} = \mathbf{13.92}$.
- **Cold-Start Subset (Unseen Brands $N=82$)**:
  - Category Mean: $\rho = \mathbf{0.686}$
  - Spec TF-IDF + Ridge: $\rho = \mathbf{0.623}$
  - LLM Aspects Alone: $\rho = \mathbf{0.621}$
  - Proposed Full Model: $\rho = \mathbf{0.585}$

### Critical Scientific Verdict:
Does the LLM bridge add incremental value over non-LLM baselines?
- On **overall pooled predictive accuracy**: **NO**. Non-LLM TF-IDF models ($\rho = 0.683$) and simple metadata models ($\rho = 0.726$) achieve higher pooled rank correlations than the proposed LLM-bridged model ($\rho = 0.562$).
- The scientifically defensible finding is:
  > *"LLM semantic extraction provides an interpretable structured aspect representation from text alone without historical review footprints, but introduces estimation noise that degrades pooled and within-category ranking performance relative to pure metadata or direct text models."*

---

## 11. Brand Memorization Analysis

Evaluating performance across Seen Brands ($N=42$) vs. Unseen Brands ($N=82$):
- **Brand-Only Baseline**:
  - Seen Brands: $\rho = -0.045$.
  - Unseen Brands: $\rho = \text{Undefined}$ (all receive fallback tier 0; zero variance).
  - Pooled ($N=124$): $\rho = 0.472$.
  - Macro-average within-category: $\bar{\rho}_{\text{macro}} = \mathbf{0.352}$.
- **Impact of Removing Brand Tier (Ablation B)**:
  - Pooled $\rho$ drops from $0.562$ to $0.458$ ($\Delta \rho = -0.104$).
  - Mean within-category $\bar{\rho}$ collapses from $+0.207$ to **$-0.180$**.
- **Cold-Start Performance on Unseen Brands ($N=82$)**:
  - Proposed model achieves $\rho = 0.585$.
  - However, Category Mean alone achieves $\rho = \mathbf{0.686}$ on the same 82 unseen-brand products.
- **Empirical Conclusion**:
  Brand footprint is the primary driver of positive within-category ranking for established brands. On unseen brands, between-category priors dominate the pooled correlation. Specification information differentiates products within specific spec-expressive categories (e.g. smartwatches unseen $\rho = 0.253$), but does not provide an overall pooled boost beyond category priors.

---

## 12. Category Memorization Analysis

Comparing Category-Only priors against the proposed model:
- **Category Mean Baseline**: Pooled $\rho = 0.671, \text{AUC} = 0.980, \text{RMSE} = 17.88$.
- **Category Median Baseline**: Pooled $\rho = 0.691, \text{AUC} = 0.980, \text{RMSE} = 18.06$.
- **Mathematical Clarification on Within-Category Performance**:
  - Category Mean and Median assign every product in a category the identical prediction ($\operatorname{Var}(\hat{y}_{\cdot, c}) = 0$).
  - Consequently, within-category Pearson and Spearman correlations are **mathematically undefined (division by zero / NaN)** for every category.
  - In ranking terms, every product pair in the category is tied, yielding an intra-category pairwise concordance index of exactly $C_{\text{within}} = \mathbf{0.500}$ (equivalent to random guessing).
- **Conclusion**:
  Category priors achieve high pooled correlation solely through between-category intercept shifts across the 5 categories, with zero intra-category discriminative ranking power.

---

## 13. Oracle Benchmark Analysis

- **Operational Model (Bridged Specs)**: $\rho = 0.562, \text{AUC} = 0.890, \text{RMSE} = 21.12, \text{MAE} = 17.84$.
- **Oracle Diagnostic (True Post-Launch Reviews)**: $\rho = 0.754, \text{AUC} = 0.992, \text{RMSE} = 15.42, \text{MAE} = 12.45$.
- **Ratio of Spearman Rank Correlations**:
  $$\frac{\rho_{\text{bridge}}}{\rho_{\text{oracle}}} = \frac{0.562}{0.7536} = \mathbf{74.5\%}$$
- **Ratio of Squared Spearman Correlations**:
  $$\frac{\rho^2_{\text{bridge}}}{\rho^2_{\text{oracle}}} = \frac{0.562^2}{0.7536^2} = \frac{0.3158}{0.5679} = \mathbf{55.6\%}$$
- **Inter-Prediction Rank Agreement**: $\rho(\hat{y}_{\text{bridge}}, \hat{y}_{\text{oracle}}) = \mathbf{0.628}$ ($p = 3.58 \times 10^{-15}$).
- **Audit Rule**:
  Do NOT describe $\rho^2$ automatically as "explained rank variance" without qualification, nor describe $74.5\%$ as "percentage of information recovered." The exact approved phrasing is:
  > *"The squared Spearman correlation is 0.316 for the operational model versus 0.568 for the oracle, giving a ratio of 55.6%, while the ratio of Spearman rank correlations is 74.5%."*

---

## 14. Monotonic Constraints and Seed Stability

### Monotonic Constraints Analysis:
- Unconstrained XGBoost (Ablation D): $\rho = 0.542, \text{AUC} = 0.879$.
- Monotonic XGBoost (Proposed): $\rho = 0.562, \text{AUC} = 0.890$.
- Paired difference: $\Delta \rho = +0.020$ ($95\%$ CI $[-0.037, +0.074], p = 0.453$); $\Delta \text{AUC} = +0.011$ ($p = 0.753$).
- Approved phrasing:
  > *"The monotonic constraints enforce the specified directional relationships and prevent predictions that violate those modeling assumptions; in this experiment they did not produce a statistically significant change in ranking performance."*

### Seed Stability (8 predefined seeds $\{10, 42, 123, 456, 789, 999, 1337, 2026\}$):
- **Proposed Model (XGBoost Monotone)**: Mean $\rho = 0.562 \pm 0.000$ (deterministic on frozen features/split).
- **Random Forest**: Mean $\rho = 0.693 \pm 0.002$, range $[0.691, 0.695]$.
- **Gradient Boosting**: Mean $\rho = 0.698 \pm 0.000$.

---

## 15. Within-Category Head-to-Head Comparison

Using the identical temporal test set ($N=124$), we evaluate performance within each category and report macro-averages, sample-weighted averages, mean-centered pooled correlation, and intra-category concordance:

| Category | $n$ | Proposed XGBoost | Cat + Brand Ridge | GBDT | Random Forest | TF-IDF + Ridge | Brand-Only | Category Mean/Median |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Bluetooth Speakers** | 7 | 0.536 | 0.578 | **0.643** | -0.143 | -0.286 | 0.578 | Undefined (NaN) |
| **Smartwatches** | 39 | 0.415 | **0.549** | 0.370 | 0.208 | 0.140 | **0.549** | Undefined (NaN) |
| **Ice Makers** | 36 | 0.179 | -0.160 | **0.272** | 0.141 | 0.106 | -0.160 | Undefined (NaN) |
| **Power Banks** | 19 | -0.042 | **0.368** | 0.255 | -0.175 | 0.068 | **0.368** | Undefined (NaN) |
| **Wireless Headphones** | 23 | -0.055 | 0.428 | **0.531** | 0.518 | 0.166 | 0.428 | Undefined (NaN) |
| **Macro-Average $\bar{\rho}$** | — | **0.207** | **0.352** | **0.414** | **0.110** | **0.039** | **0.352** | **Undefined (NaN)** |
| **Weighted-Average $\bar{\rho}_{\text{weighted}}$** | — | **0.196** | **0.294** | **0.369** | **0.168** | **0.100** | **0.294** | **Undefined (NaN)** |
| **Centered Pooled $\rho_{\text{centered}}$** | — | **0.177** | **0.321** | **0.264** | **0.144** | **0.095** | **0.321** | **Undefined (NaN)** |
| **Intra-Category C-Index ($C_{\text{within}}$)** | — | **0.575** | **0.568** | **0.609** | **0.557** | **0.531** | **0.568** | **0.500** |

### Paired Within-Category Differences (Proposed vs. Baselines):
- **Smartwatches ($n=39$)**:
  - vs. Category + Brand Ridge: $\Delta \rho = -0.134$ ($95\%$ CI $[-0.441, +0.139], p = 0.363$)
  - vs. GBDT: $\Delta \rho = +0.045$ ($95\%$ CI $[-0.344, +0.421], p = 0.787$)
  - vs. Random Forest: $\Delta \rho = +0.208$ ($95\%$ CI $[-0.110, +0.552], p = 0.220$)
  - vs. TF-IDF + Ridge: $\Delta \rho = +0.276$ ($95\%$ CI $[-0.168, +0.709], p = 0.236$)
- **Ice Makers ($n=36$)**:
  - vs. Category + Brand Ridge: $\Delta \rho = +0.340$ ($95\%$ CI $[-0.026, +0.708], p = 0.082$)
  - vs. GBDT: $\Delta \rho = -0.093$ ($95\%$ CI $[-0.368, +0.146], p = 0.480$)
- **Wireless Headphones ($n=23$)**:
  - vs. GBDT: $\Delta \rho = \mathbf{-0.586}$ ($95\%$ CI $[-1.102, -0.032], p = \mathbf{0.040}$) — *Statistically significant inferiority*
  - vs. Random Forest: $\Delta \rho = \mathbf{-0.573}$ ($95\%$ CI $[-1.070, -0.049], p = \mathbf{0.030}$) — *Statistically significant inferiority*
  - vs. Category + Brand Ridge: $\Delta \rho = -0.483$ ($95\%$ CI $[-0.950, +0.005], p = 0.055$)
- **Power Banks ($n=19$)**:
  - vs. Category + Brand Ridge: $\Delta \rho = -0.411$ ($95\%$ CI $[-0.940, +0.187], p = 0.173$)
  - vs. GBDT: $\Delta \rho = -0.297$ ($95\%$ CI $[-0.761, +0.147], p = 0.202$)

### Critical Scientific Answer:
> Once broad between-category target shifts are removed, does the proposed model outperform or materially compete with the strong baselines?

**NO**. GBDT ($\bar{\rho}_{\text{macro}} = 0.414$) and Category + Brand Ridge ($\bar{\rho}_{\text{macro}} = 0.352$) substantially outperform the proposed XGBoost model ($\bar{\rho}_{\text{macro}} = 0.207$). The proposed model suffers from negative correlations in mature commoditized categories (Wireless Headphones $\rho = -0.055$, Power Banks $\rho = -0.042$) where brand dominance decouples market success from specifications.

---

## 16. Failure Cases and Root Causes

Detailed in [`FAILURE_CASES.md`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/FAILURE_CASES.md):
1. **Pooled Superiority of Category Priors**: Category Mean achieves $\rho = 0.671$ on the full test set and $\rho = 0.686$ on unseen brands due to between-category target shifts.
2. **Superiority of Non-LLM Metadata Model ($\rho = 0.726$)**: Bridged aspects inject estimation noise that dilutes high-confidence brand/price signals.
3. **Negative Correlation in Power Banks & Headphones**: Extreme market commoditization renders specifications non-discriminative.

---

## 17. Researcher Degrees of Freedom

Documented in [`EXPERIMENT_SEARCH_SPACE.md`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/EXPERIMENT_SEARCH_SPACE.md):
- 8 algorithms, 14 baselines, and 11 ablations were tracked.
- All non-significant or negative results are fully reported.

---

## 18. Remaining Limitations

1. **Marketplace Specificity**: Amazon US consumer dynamics.
2. **Commoditized Category Failure**: Inability to differentiate commoditized white-label hardware.
3. **Noise in Bridged Estimates**: LLM aspect scoring introduces estimation variance.

---

## 19. Exact Manuscript Changes Required

Detailed in [`MANUSCRIPT_CLAIM_EVIDENCE_MATRIX.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/baselines/MANUSCRIPT_CLAIM_EVIDENCE_MATRIX.csv):
1. **Abstract & Section I**:
   - Retract claims that the proposed model outperforms baselines on pooled rank correlation.
   - Report that Category Median ($\rho = 0.691$), Category + Brand Ridge ($\rho = 0.712$), and Spec TF-IDF ($\rho = 0.683$) achieve higher pooled correlations.
   - Clarify that within categories, GBDT achieves $\bar{\rho}_{\text{macro}} = 0.414$ vs. the proposed model's $0.207$.
2. **Section IV-B Model Selection**:
   - Unify CV reporting: Gradient Boosting led in CV fit ($R^2 = 0.558$ vs. $0.550$); XGBoost was chosen for native missing-value and categorical support.
3. **Section V-A Monotonic Constraints**:
   - State: *"The monotonic constraints enforce the specified directional relationships and prevent predictions that violate those modeling assumptions; in this experiment they did not produce a statistically significant change in ranking performance."*
4. **Section V-B Oracle Comparison**:
   - State: *"The squared Spearman correlation is 0.316 for the operational model versus 0.568 for the oracle, giving a ratio of 55.6%, while the ratio of Spearman rank correlations is 74.5%."* Delete all references to "information recovered" or "explained rank variance."

---

## 20. Final Verdict

$$\mathbf{PARTIALLY\ SEALED\ —\ MANUSCRIPT\ CLAIMS\ REQUIRE\ REVISION}$$

The computational and experimental audit is complete, leak-free, reproducible, and supported by automated validation tests (`14/14 passed`). However, because the empirical evidence clearly establishes that simpler and conventional ML baselines outperform the proposed model on pooled test correlation and within-category macro-average ranking, the manuscript's claims must be formally revised to align with these empirical realities before Issue 6 can be considered permanently sealed.
