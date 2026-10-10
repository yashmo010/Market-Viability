# Target Reconciliation & Formulation Audit

## 1. Mathematical Formulation
Per `Capstone updated/Capstone/audit/target/TARGET_DEFINITION.md` and executable source code in `Capstone updated/Capstone/src/features/target_builder.py`, the target variable `SuccessScore` is computed as:

$$\text{SuccessScore} = 100 \times \left(0.40 \cdot V_{\text{norm}} + 0.35 \cdot R_{\text{norm}} + 0.25 \cdot \text{Vel}_{\text{norm}}\right)$$

Where:
- $V_{\text{norm}}$: Log-transformed review volume normalized across the training population: $\frac{\log(1 + \text{n\_reviews}) - \mu_V}{\sigma_V}$, clipped to $[0, 1]$.
- $R_{\text{norm}}$: Average star rating normalized from $[1.0, 5.0]$ to $[0, 1]$: $\frac{\text{rating} - 1.0}{4.0}$.
- $\text{Vel}_{\text{norm}}$: Review velocity (reviews per active month) log-normalized: $\frac{\log(1 + \text{velocity}) - \mu_{\text{Vel}}}{\sigma_{\text{Vel}}}$, clipped to $[0, 1]$.

## 2. Theoretical & Practical Purpose
- `SuccessScore` serves as a **review-derived market-success proxy**.
- It captures consumer reception, product satisfaction, and sustained engagement.
- It is **strictly prohibited** to describe this target as:
  - "Direct retail sales"
  - "Gross commercial revenue"
  - "Total units sold"
  - "Commercial profitability"

## 3. Leakage Quarantine
- The target values for the 124 temporal test items are physically segregated in `strict_temporal/data/test_labels/ground_truth.json`.
- The normalization parameters ($\mu_V, \sigma_V, \mu_{\text{Vel}}, \sigma_{\text{Vel}}$) were fitted strictly on the 507 pre-cutoff training items.
- At no point during feature extraction, scaling, imputation, or model training are test labels exposed.
