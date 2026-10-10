# Baseline Evaluation Protocol Specification

**Protocol Identifier**: `PROTOCOL-ISSUE6-FROZEN-TEMPORAL-01`  
**Governing Authority**: Issues 1–5 Audited Experimental Protocol  
**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher and Experimental Scientist  

---

## 1. Frozen Data Partitions

The evaluation protocol inherits the physical isolation boundaries sealed in Issue 1 and Issue 5 without modification:

| Partition | Record Count | Temporal Cutoff Rule | Source Path | Target Availability |
|---|:---:|---|---|:---:|
| **Training Pool** | **507** products | First review timestamp $\le$ October 31, 2021 (Epoch $1635724799$) | `strict_temporal/data/train/products.json` | Accessible during training (`strict_temporal/frozen_state/train_features.parquet`) |
| **Test Holdout** | **124** products | First review timestamp $>$ October 31, 2021 (Epoch $1635724799$) | `strict_temporal/data/test_inputs/products_test_specs.json` | **STRICTLY BLOCKED** during prediction (`strict_temporal/data/test_labels/ground_truth.json`) |

### Category Breakdown of Evaluated Test Cohort ($N=124$)
- `bluetooth_speakers`: $7$ products
- `ice_makers`: $36$ products
- `power_banks`: $19$ products
- `smartwatches`: $39$ products
- `wireless_headphones`: $23$ products

---

## 2. Prediction Target Specification

### A. Target Formula
The evaluation target is the review-derived composite market success proxy:
$$\text{SuccessScore} = 100 \times \left(0.40 \cdot \text{Volume}_{\text{norm}} + 0.35 \cdot \text{Rating}_{\text{norm}} + 0.25 \cdot \text{Velocity}_{\text{norm}}\right)$$

### B. Normalization Discipline
All normalization bounds ($\text{vol}_{\min}, \text{vol}_{\max}, \text{rat}_{\min}, \text{rat}_{\max}, \text{vel}_{\min}, \text{vel}_{\max}$) were computed **strictly across pre-cutoff training products** within each category and serialized in `strict_temporal/frozen_state/target_scalers.json`. Test targets were transformed using these frozen bounds; zero test-set statistics entered the normalizers.

---

## 3. Evaluated Metrics & Definitions

Every baseline, ablation, and proposed model is evaluated using the canonical evaluation suite (`scripts/evaluate_strict_temporal.py`):

1. **Primary Metric — Spearman Rank Correlation ($\rho$)**:
   $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$
   Evaluates monotonic ranking agreement between predicted viability and actual success across the $124$ test products.
2. **Secondary Metric — Top-vs-Bottom Quintile AUC-ROC**:
   Mann-Whitney $U$ statistic computed between the top $20\%$ ($N \ge 24$) and bottom $20\%$ ($N \ge 24$) of actual success scores:
   $$\text{AUC} = \frac{U}{n_{\text{top}} \cdot n_{\text{bot}}}$$
3. **Continuous Error Metrics**:
   - $\text{RMSE} = \sqrt{\frac{1}{n} \sum (y_i - \hat{y}_i)^2}$
   - $\text{MAE} = \frac{1}{n} \sum |y_i - \hat{y}_i|$
4. **Within-Category Ranking ($\bar{\rho}_{\text{within}}$)**:
   The unweighted arithmetic mean of Spearman $\rho$ values computed independently within each of the 5 categories (with $N \ge 5$).

---

## 4. Uncertainty Quantification & Confidence Intervals

1. **Bootstrap Procedure**:
   - Resampling: Non-parametric paired percentile bootstrap.
   - Replicates: $B = 10,000$ (or $B = 2,000$ for batch grid scans).
   - Interval: $95\%$ two-sided percentile interval $[\hat{\theta}_{2.5\%}, \hat{\theta}_{97.5\%}]$.
   - Empirical Bootstrap $p$-value: Two-sided tail probability:
     $$p = 2 \cdot \min\left(\frac{1}{B} \sum \mathbf{1}_{\theta^* \le 0}, \frac{1}{B} \sum \mathbf{1}_{\theta^* \ge 0}\right)$$
2. **DeLong Interval for AUC**:
   - Asymptotic variance computed via structural components $S_{10}$ and $S_{01}$ (DeLong et al., 1988).

---

## 5. Model Selection & Tuning Protocol

1. **Inner-CV Constraint**:
   - All hyperparameter selection, tree depth tuning, and early stopping rules were derived **strictly within 5-fold cross-validation on the 507 pre-cutoff training products**.
2. **Test-Set Isolation**:
   - The test holdout ($N=124$) was never evaluated iteratively or used to guide model selection, feature pruning, prompt re-engineering, or seed selection.
3. **Random Seed Discipline**:
   - Primary seed: $42$.
   - Multi-seed robustness suite: Seeds $\{10, 42, 123, 456, 789, 999, 1337, 2026\}$.
