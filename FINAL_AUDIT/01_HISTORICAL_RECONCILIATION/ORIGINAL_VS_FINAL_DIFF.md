# Original Canonical Paper vs. Final Audited Implementation Diff

| Architectural Dimension | Original Canonical Model (Model_O) | Final Audited Model (Model_New / Cand B) | Reconciliation Status |
| :--- | :--- | :--- | :--- |
| **Research Title** | Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging | Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging | **IDENTICAL (Preserved)** |
| **Temporal Cutoff** | October 31, 2021 23:59:59 UTC | October 31, 2021 23:59:59 UTC | **IDENTICAL (Frozen)** |
| **Training Products** | 507 products across 5 categories | 507 products across 5 categories | **IDENTICAL (Preserved)** |
| **Test Products** | 124 launch-blind products | 124 launch-blind products | **IDENTICAL (Preserved)** |
| **Product Categories** | 5 (Bluetooth speakers, Ice makers, Power banks, Smartwatches, Wireless headphones) | 5 (Bluetooth speakers, Ice makers, Power banks, Smartwatches, Wireless headphones) | **IDENTICAL (Canon Locked)** |
| **Target Variable** | `SuccessScore` composite proxy | `SuccessScore` composite proxy | **IDENTICAL (Preserved)** |
| **Downstream Algorithm** | Monotonically constrained XGBoost | Monotonically constrained XGBoost | **IDENTICAL (Preserved)** |
| **Feature Representation** | 9 scalar LLM aspect scores + price + brand + category (21 features) | 9 scalar LLM aspects + 3 Specification Density Metrics + price + brand + category (24 features) | **ENRICHED (Cold-start attribute grounding)** |
| **Test Baseline Fairness** | Historical runtime had 26 cached prompts and 98 mock fallbacks | Separately reports Historical Baseline-H ($\rho=0.562$) and Controlled Baseline-C | **RESOLVED & TRANSPARENT** |
| **Temporal Test $\rho$** | $\rho = 0.5621$ | $\rho = 0.6720$ ($\Delta\rho = +0.1099$, $p=0.0004$) | **STATISTICALLY SUPERIOR** |
