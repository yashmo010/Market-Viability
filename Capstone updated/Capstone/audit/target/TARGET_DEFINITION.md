# LaunchSight Target Definition: Mathematical & Operational Specification

## 1. Executive Summary

This document formalizes the target variable **`SuccessScore`** used in the LaunchSight e-commerce product prediction pipeline. 

Based on an exhaustive statistical and data provenance audit across 631 physical hardware products ($n_{\text{train}} = 507$, $n_{\text{test}} = 124$), `SuccessScore` is classified as:

$$\mathbf{TARGET\ VALID\ AS\ EXPLICIT\ PROXY}$$

It operates as an empirical **review-derived market-success proxy** combining post-launch customer adoption volume, customer satisfaction, and velocity of adoption. It **does not** measure gross sales, dollar revenue, profit margin, units sold, or retail conversion rate directly, as zero transactional or sales rank data exists in the Amazon physical products dataset.

---

## 2. Mathematical Definition

The target variable is continuous, bounded within $[0.0, 100.0]$, and constructed as a category-normalized weighted linear composite of three log-transformed or normalized review-based metrics:

$$\text{SuccessScore}_i = 100.0 \times \Big( 0.40 \cdot \widetilde{V}_{i,c} + 0.35 \cdot \widetilde{R}_{i,c} + 0.25 \cdot \widetilde{\omega}_{i,c} \Big)$$

Where:
- $i$ denotes product $i$ belonging to category $c \in \{\text{bluetooth\_speakers}, \text{ice\_makers}, \text{power\_banks}, \text{smartwatches}, \text{wireless\_headphones}\}$.
- $\widetilde{V}_{i,c} \in [0, 1]$ is the within-category normalized review volume.
- $\widetilde{R}_{i,c} \in [0, 1]$ is the within-category normalized average star rating.
- $\widetilde{\omega}_{i,c} \in [0, 1]$ is the within-category normalized review velocity.

---

## 3. Component Formulations & Transformations

### 3.1. Review Volume Component ($\widetilde{V}_{i,c}$)
- **Raw Variable:** $N_i$, total count of verified consumer reviews accumulated over the product's observation period.
- **Transformation:** Natural log-plus-one transformation to compress heavy-tailed power-law distribution:
  $$V_i = \ln(1 + N_i)$$
- **Normalization:** Per-category MinMax scaling using parameter bounds fitted **strictly on the pre-cutoff training pool** ($n=507$):
  $$\widetilde{V}_{i,c} = \text{clip}\left( \frac{V_i - V_{\min, c}^{\text{train}}}{V_{\max, c}^{\text{train}} - V_{\min, c}^{\text{train}} + \epsilon}, 0.0, 1.0 \right)$$
  where $\epsilon = 10^{-9}$.

### 3.2. Rating Component ($\widetilde{R}_{i,c}$)
- **Raw Variable:** $\bar{R}_i$, arithmetic mean star rating across all reviews for product $i$, bounded in $[1.0, 5.0]$.
- **Transformation:** Identity (linear).
- **Normalization:** Per-category MinMax scaling using pre-cutoff training bounds:
  $$\widetilde{R}_{i,c} = \text{clip}\left( \frac{\bar{R}_i - R_{\min, c}^{\text{train}}}{R_{\max, c}^{\text{train}} - R_{\min, c}^{\text{train}} + \epsilon}, 0.0, 1.0 \right)$$

### 3.3. Review Velocity Component ($\widetilde{\omega}_{i,c}$)
- **Raw Variable:** $\omega_i$, average monthly review accumulation rate over the product's active lifespan.
  $$\Delta t_i = \max\left( \frac{t_{\text{latest}, i} - t_{\text{first}, i}}{30.4375 \times 86400}, 1.0 \right) \quad [\text{months}]$$
  $$\omega_i = \frac{N_i}{\Delta t_i} \quad [\text{reviews / month}]$$
- **Transformation:** Linear monthly rate with a 1-month floor denominator to prevent division-by-zero on bursty or single-day launches.
- **Normalization:** Per-category MinMax scaling using pre-cutoff training bounds:
  $$\widetilde{\omega}_{i,c} = \text{clip}\left( \frac{\omega_i - \omega_{\min, c}^{\text{train}}}{\omega_{\max, c}^{\text{train}} - \omega_{\min, c}^{\text{train}} + \epsilon}, 0.0, 1.0 \right)$$

---

## 4. Frozen Training Category Bounds

All normalization parameters are computed exclusively from the 507 pre-cutoff products ($\le \text{2021-10-31}$) and frozen in `strict_temporal/frozen_state/target_scalers.json`:

| Category | $V_{\min}$ ($\ln$) | $V_{\max}$ ($\ln$) | $R_{\min}$ ($\star$) | $R_{\max}$ ($\star$) | $\omega_{\min}$ (rev/mo) | $\omega_{\max}$ (rev/mo) |
|---|---:|---:|---:|---:|---:|---:|
| `bluetooth_speakers` | 1.7918 | 5.7071 | 3.80 | 4.80 | 0.1177 | 6.5799 |
| `power_banks` | 2.0794 | 5.7071 | 3.90 | 4.70 | 0.1889 | 5.0237 |
| `smartwatches` | 1.7918 | 5.6937 | 3.30 | 4.70 | 0.1682 | 11.0366 |
| `wireless_headphones` | 2.3979 | 5.7071 | 3.70 | 4.80 | 0.2976 | 16.3567 |
| `ice_makers` | 2.0794 | 4.1109 | 3.30 | 4.50 | 0.2433 | 3.8019 |

---

## 5. Survivorship and Filtering Protocol

1. **Review Count Threshold:** Products with $N_i < 5$ reviews are excluded during dataset compilation. This introduces an explicit survivorship constraint: the model predicts success conditional on achieving minimal market entry ($N \ge 5$).
2. **Fraud / Astroturfing Exclusion:** 9 products exhibiting synthetic review velocity anomalies ($\omega_i > 50$ reviews/month with $<5\%$ verified purchase ratio) were purged in data preprocessing.
3. **Missing Value Policy:** Any product missing star rating or timestamp is dropped prior to feature extraction; no imputation is performed on target fields.

---

## 6. Information Boundary & Leakage Defense

Under the Issue 1 strict temporal protocol, target variables are generated exclusively in `strict_temporal/data/test_labels/ground_truth.json`.
- The predictor (`StrictPredictor`) loads **only** `products_test_specs.json` which contains: `product_uid`, `name`, `brand`, `price`, `specs`, and `first_review_ts`.
- All target columns (`success_score`, `n_reviews`, `avg_rating`, `velocity`, `volume_norm`, `rating_norm`, `velocity_norm`) are strictly sealed in the test labels directory and accessed exclusively by `evaluate_test.py`.
