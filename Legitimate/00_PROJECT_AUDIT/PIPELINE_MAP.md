# Pipeline Map: End-to-End Execution Flow

```text
+-------------------------------------------------------------+
|             PRE-LAUNCH PRODUCT SPECIFICATIONS               |
|  (Title, Category, Brand, Price, Raw Feature Descriptions)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               LLM SEMANTIC EXTRACTION STAGE                 |
|  - Ingests pre-launch text & category priors                |
|  - Original: Outputs 9 scalar aspect scores + confidence    |
|  - Bottleneck: Compresses raw specs into scalar summaries   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               STRUCTURED FEATURE COMPOSITION                |
|  - Launch price                                             |
|  - Brand Tier (from frozen pre-cutoff catalog footprint)    |
|  - Category identifier (categorical dtype)                  |
|  - Aspect scores (9) + Mention rates (9)                    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                  XGBOOST REGRESSOR STAGE                    |
|  - 112 trees, depth 5, lr 0.05, monotone priors             |
|  - Fitted exclusively on 507 pre-cutoff products            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|          PREDICTED MARKET-SUCCESS PROXY [0, 100]            |
|  Target = 100 * (0.40 * vol_norm + 0.35 * rat_norm          |
|                  + 0.25 * vel_norm)                         |
+-------------------------------------------------------------+
```
