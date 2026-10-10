# Experiment Inventory

| Experiment ID | Protocol | Description | Primary Metric (Spearman rho) | Status |
|---|---|---|---|---|
| `EXP-TEMPORAL-STRICT-01` | Strict Temporal (507/124) | Canonical Original Model (Model_O) | 0.562 [0.414, 0.681] | Canonical Frozen Baseline |
| `EXP-MONOTONIC-ABLATION` | Strict Temporal (507/124) | XGBoost without Monotone Constraints | 0.548 [0.398, 0.672] | Ablation Recorded |
| `EXP-PRICE-FREE-ABLATION`| Strict Temporal (507/124) | Aspects + Brand without Price | 0.544 [0.390, 0.669] | Ablation Recorded |
| `EXP-TARGET-SENSITIVITY` | Strict Temporal (507/124) | Varying target weights (+-10%) | Rank stability rho > 0.988 | Target Validated |
| `EXP-RATING-BLINDED`     | Strict Temporal (507/124) | Target excluding avg_rating | 0.531 [0.380, 0.658] | Ablation Recorded |
| `EXP-ORACLE-CEILING`     | Strict Temporal (507/124) | True post-launch review aspects | 0.738 [0.630, 0.820] | Diagnostic Upper Bound |
