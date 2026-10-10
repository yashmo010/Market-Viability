# Temporal Protocol Reconciliation

## 1. Frozen Temporal Cutoff
- **Cutoff Timestamp**: October 31, 2021 23:59:59 UTC
- **Rationale**: Reflects realistic pre-launch deployment where historical review interactions are available only up to the cutoff date.

## 2. Sample Cohort Verification
- **Training Cohort ($N = 507$)**: Products with first review timestamp $\le$ October 31, 2021.
- **Temporal Test Cohort ($N = 124$)**: Products with launch/first review timestamp strictly $>$ October 31, 2021.
- **Total Evaluated Products**: $507 + 124 = 631$ products.
- **Zero Temporal Leakage**:
  - No post-cutoff products exist in the training feature matrix.
  - No pre-cutoff test products exist in the test evaluation pool.
  - No future review tokens or metadata enter the feature vector.
