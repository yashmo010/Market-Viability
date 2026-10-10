# Existing Model Comparison & Baseline Inventory

**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher, Experimental Scientist, and Hostile Peer Reviewer  
**Scope**: Complete forensic mapping of all models, baselines, feature sets, configurations, and manuscript claims across the codebase.

---

## 1. Inventory of All Evaluated Models & Algorithms

Across the codebase (`scripts/ml_algorithm_comparison.py`, `scripts/reproduce_table1_leakage_free.py`, `src/strict_temporal/`, and `scratch/`), seven primary algorithm families have been implemented and benchmarked:

| Algorithm | Implementation / Library | Hyperparameter Specification | Objective / Loss | Native Missing Handling? | Role in Project |
|---|---|---|---|:---:|---|
| **XGBoost (Monotone)** | `xgboost.XGBRegressor` | `n_estimators=112` (CV-selected), `max_depth=5`, `lr=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `min_child_weight=3`, `tree_method='hist'`, `monotone_constraints` active | `reg:squarederror` | Yes | **Primary Proposed Production Model** |
| **XGBoost (Unconstrained)** | `xgboost.XGBRegressor` | Identical to above, with `monotone_constraints=None` | `reg:squarederror` | Yes | Ablation comparator (monotonicity impact) |
| **Gradient Boosting (GBDT)** | `sklearn.ensemble.GradientBoostingRegressor` | `n_estimators=112` (or 600 in Table 1), `max_depth=5`, `learning_rate=0.05`, `min_samples_leaf=3`, `subsample=0.8`, `random_state=42` | Squared error | No (imputation required) | Primary Non-XGB Tree Baseline |
| **Random Forest** | `sklearn.ensemble.RandomForestRegressor` | `n_estimators=112` (or 600 in Table 1), `max_depth=5` (or 10 in Table 1), `min_samples_leaf=3`, `random_state=42` | Squared error | No (imputation required) | Classic Bagging Baseline |
| **Ridge Regression** | `sklearn.linear_model.Ridge` | `alpha=10.0` (CV-tuned from `[0.01..100.0]`), `random_state=42` | L2-penalized OLS | No (imputation required) | Regularized Linear Baseline |
| **Elastic Net** | `sklearn.linear_model.ElasticNet` | `alpha=0.1`, `l1_ratio=0.5`, `random_state=42` | L1 + L2 penalized OLS | No (imputation required) | Sparsity-Inducing Linear Baseline |
| **Multi-Layer Perceptron (MLP)** | `sklearn.neural_network.MLPRegressor` | `hidden_layer_sizes=(128, 64)`, `max_iter=500`, `early_stopping=True`, `lr_init=0.001` | Squared error | No (imputation required) | Deep/Neural Tabular Baseline |
| **Support Vector Regression (SVR)** | `sklearn.svm.SVR` | `kernel='rbf'`, `C=10.0`, `epsilon=0.1` | Epsilon-insensitive loss | No (imputation required) | Kernel Non-Linear Baseline |

---

## 2. Inventory of Evaluated Baselines

Historically and currently, the project has explored the following baselines across various development scripts:

### A. Trivial & Empirical Priors
1. **Global Mean**: Predicts $\bar{y}_{\text{train}} = 53.07$ for all test instances.
2. **Global Median**: Predicts $\text{median}(y_{\text{train}}) = 52.88$ for all test instances.
3. **Category Mean**: Predicts the training-set mean of the product's category.
4. **Category Median**: Predicts the training-set median of the product's category.

### B. Brand & Category Structural Baselines
5. **Brand-Only**: Predicts using only the pre-cutoff brand footprint tier ($0, 1, 2, 3$).
6. **Category + Brand**: Ridge regression combining one-hot category indicators with brand tier.

### C. Heuristic Pre-Launch Baselines (Historical)
7. **Price-Distance to Category Median**: Evaluated in `scripts/baseline_check.py` on 90 retro products: $-|p - \text{median}_{\text{cat}}|$, yielding $\rho = -0.178$.
8. **Within-Category Price Percentile**: Evaluated in `scripts/baseline_check.py` ($\rho = 0.250$) and Section V-C ($\rho = 0.147$).
9. **Marketing Copy Character Length**: Evaluated in `scripts/baseline_check.py`: string length of feature bullet points, yielding $\rho = -0.259$.

### D. Specification-Only Non-LLM Baselines
10. **Spec TF-IDF + Ridge**: 300 unigram/bigram TF-IDF features extracted from product title and technical feature bullets, regressed with Ridge ($\alpha = 1.0$).
11. **Spec TF-IDF + Price + Category (Ridge)**: Multimodal non-LLM baseline combining TF-IDF spec text, launch price, and category indicators.
12. **Spec TF-IDF + Gradient Boosting**: GBDT applied directly to TF-IDF text features.

---

## 3. Inventory of Feature Sets

Across experiments, five distinct feature representations have been evaluated:

1. **Full Operational Specification Matrix (21 Features)**:
   - Metadata: `price`, `brand_tier`, `category` (categorical/one-hot).
   - Bridged Aspect Sentiment Means (9): `value_for_money`, `utility`, `ease_of_use`, `reliability`, `design_appeal`, `after_sales`, `build_quality`, `durability`, `repairability`.
   - Category Aspect Mention Rates (9): `{aspect}_mention_rate`.
2. **Aspects-Only Matrix (18 Features)**:
   - 9 aspect means + 9 aspect mention rates. Metadata (`price`, `brand_tier`, `category`) excluded.
3. **Metadata-Only Matrix (3 Features)**:
   - `price`, `brand_tier`, `category`. (Evaluated in Ablation A).
4. **Numeric-Only Matrix (2 Features)**:
   - `price`, `brand_tier`. (Evaluated in Ablation G).
5. **Raw Spec Text TF-IDF Matrix (300 Features)**:
   - N-gram term frequencies from raw pre-launch engineering specifications.
6. **Leaky Feature Set (Excluded by Audit)**:
   - `avg_rating`, `rating_count_log`, `review_velocity`, `install_count_log`, `days_since_update`.

---

## 4. Target Definitions & Splits

### A. Target Construct
- **Canonical Composite Target**:
  $$\text{SuccessScore} = 100 \times (0.40 \times \text{Volume}_{\text{norm}} + 0.35 \times \text{Rating}_{\text{norm}} + 0.25 \times \text{Velocity}_{\text{norm}})$$
  where normalization is performed using category-specific min/max bounds established strictly on the training pool.
- **Alternative Ablation Targets**:
  - Volume Only ($100/0/0$)
  - Rating Only ($0/100/0$)
  - Velocity Only ($0/0/100$)
  - Raw Global Composite (Unnormalized across categories)

### B. Partitioning Schemes
1. **Historical 5-Fold Cross-Validation (`features_physical.parquet`, $N=631$)**:
   - Random partitioning across all physical products. Pre-cutoff and post-cutoff products mixed. Evaluated in Table 1.
2. **First-Generation Holdout ($N=59$)**:
   - Stratified random holdout sampled disjointly before prompt v2 tuning.
3. **Extended Retrained Holdout ($N=118$)**:
   - Extended sample from older pipeline.
4. **Strict Forward-in-Time Temporal Holdout ($N=124$, Cutoff Oct 31, 2021)**:
   - The sealed, canonical, leakage-free benchmark established in Issues 1–5:
     - Pre-cutoff training pool: $N=507$ products.
     - Post-cutoff test pool: $N=124$ products ($N=51$ mature $\ge 30$ reviews).

---

## 5. Evaluation Metrics & Tuning Procedures

- **Primary Metric**: Spearman rank correlation coefficient ($\rho$) on test predictions.
- **Secondary Metrics**:
  - Top-vs-Bottom quintile AUC-ROC (Mann-Whitney U rank discrimination).
  - Root Mean Squared Error (RMSE).
  - Mean Absolute Error (MAE).
  - Pearson correlation coefficient ($r$).
  - Mean within-category Spearman correlation ($\bar{\rho}_{\text{within}}$).
- **Uncertainty Quantification**:
  - 10,000-replicate non-parametric percentile bootstrap for Spearman $\rho$ and AUC.
  - DeLong asymptotic standard errors for AUC.
- **Model Selection & Tuning**:
  - Primary model: XGBoost hyperparameters frozen with 5-fold CV early stopping (round 112) strictly within pre-cutoff training folds.
  - Ridge baseline: $\alpha \in [0.01, 0.1, 1.0, 10.0, 100.0]$ tuned via 5-fold CV on training pool.
  - Test set was never used for model selection, feature selection, or early stopping.

---

## 6. Manuscript Claims Mapping

Every claim in `Research_Paper_IEEE_Final.docx` depending on model comparisons has been inventoried and mapped to its supporting code:

1. **Table 1 Algorithm Comparison**: Claims XGBoost and Gradient Boosting lead 5-fold CV with $R^2 = 0.550$ and $0.558$. (Traceable to `scripts/reproduce_table1_leakage_free.py`).
2. **Table 2 Cohort Summary**: Claims extended temporal model achieves $\rho = 0.590$ [0.464, 0.692], and oracle ceiling reaches $\rho = 0.738$.
3. **Section V-C Price-Free Ablation**: Claims removing price yields $\rho = 0.476$ on $n=118$.
4. **Section V-C Reddit A/B Trial**: Claims lift of $+0.049$ in $\rho$ is not statistically significant ($95\%$ CI $[-0.024, 0.127]$).
5. **Section IV-B Monotonic Constraints**: Claims monotonic constraints improve out-of-sample AUC from $0.826$ to $0.903$.

---

## 7. Forensic Audit Summary

The existing experimental record reveals an important scientific dichotomy:
1. **Pre-Audit Historical Experiments** (Table 1, Table 2 cohorts $n=59, 118, 125$) evaluated various algorithm variants under random splits or mixed temporal cutoffs.
2. **Audited Strict Temporal Holdout** ($N=124$, cutoff October 31, 2021) established the definitive, leakage-free evaluation protocol.
3. Prior to this Issue 6 audit, standard simple baselines (Global Mean, Category Mean, Brand-Only, Ridge, Random Forest, TF-IDF) had **never been systematically executed under the identical strict temporal holdout protocol**. Executing them now is required to establish whether the proposed model's performance represents genuine incremental scientific value.
