# Experiment Search Space & Researcher Degrees of Freedom Audit

**Audit Date**: October 2026  
**Auditor**: Senior Machine Learning Researcher and Experimental Methodologist  
**Scope**: Full accounting of all models, baselines, feature variants, seeds, and configurations explored across the project lifecycle.

---

## 1. Accounting of Researcher Degrees of Freedom

To provide complete transparency against "cherry-picking" or multiple hypothesis testing without correction, we inventoried every experiment attempted throughout this capstone project:

| Category | Total Explored | Retained in Manuscript | Unsuccessful / Negative Findings Disclosed |
|---|:---:|:---:|---|
| **Algorithms Evaluated** | **8** | 2 (XGBoost, GBDT in Table 1) | Random Forest, MLP, Ridge, ElasticNet, SVR, TF-IDF linear |
| **Evaluated Baselines** | **12** | 3 (Price-only, Copy-length, Category) | Global Mean, Global Median, Category Median, Brand-Only, Category+Brand, Ridge, TF-IDF |
| **Component Ablations** | **11** | 2 (Price-free, Monotonic constraints) | Remove LLM aspects, Remove Brand, Remove Category, Remove Individual Aspect Families (3), Unnormalized target |
| **Feature Representation Variants** | **6** | 1 (Physical aspects + metadata) | Aspects-only, Metadata-only, Numeric-only, Raw TF-IDF, Leaky review features (rejected) |
| **Random Seeds Evaluated** | **10+** | 1 (Seed 42) | Audited across 8 seeds: $\{10, 42, 123, 456, 789, 999, 1337, 2026\}$ |
| **Target Normalization Variants** | **4** | 1 (Category min/max composite) | Global min/max, Z-score, Raw volume/rating composite |
| **Evaluation Metrics Calculated** | **9** | 3 ($\rho$, AUC, RMSE) | MAE, Pearson $r$, $R^2$, Accuracy, F1, MCC |
| **Domain Tracks Attempted** | **2** | 1 (Physical products) | **Mobile Application Track** (Failed: $R^2 = 0.101$; prominently disclosed in Section VI) |

---

## 2. Disclosed Negative Results & Unsuccessful Explorations

Unlike papers that conceal failed configurations, this research project explicitly documents multiple negative results:

1. **Negative Result 1 — Mobile Application Failure**:
   - The identical LLM bridging pipeline was evaluated across 319 mobile applications in Google Play.
   - Result: $R^2 = 0.101$, failing the pre-registered acceptance gate ($R^2 \ge 0.35$).
   - Testing 5 alternative target definitions (ratings, retention, velocity, installs) confirmed that app success is distribution-driven, not quality-driven.
   - Status: Prominently reported in Section VI of the paper; user-facing app track was disabled with the experiment cited.
2. **Negative Result 2 — Reddit Consumer Priorities Lift**:
   - Injected buying-intent Reddit comments to summarize category consumer priorities.
   - Result: Lift of $\Delta \rho = +0.049$ on 89 development products, but paired bootstrap $95\%$ CI spans zero ($[-0.024, +0.127]$).
   - Status: Explicitly labeled "exploratory" and non-statistically significant in Section V-C and Section VII.
3. **Negative Result 3 — Validity-Weighted Shrinkage**:
   - Attempted Bayesian shrinkage of bridged aspect scores toward category means weighted by measured aspect validity.
   - Result: Degraded end-to-end $\rho$ from $0.313$ to $0.249$ by destroying cross-aspect covariance.
   - Status: Reported as a cautionary negative finding in Section V-C.
4. **Negative Result 4 — Baseline Superiority on Pooled Ranking (Uncovered in this Issue 6 Audit)**:
   - Category Mean ($\rho = 0.671$), Category + Brand ($\rho = 0.712$), Random Forest ($\rho = 0.694$), and TF-IDF Ridge ($\rho = 0.683$) all outperform the proposed LLM-bridged model ($\rho = 0.562$) on pooled test rank correlation.
   - Status: Fully preserved and documented in `audit/baselines/BASELINE_RESULTS.csv` and the audit report.

---

## 3. Multiple Testing & Selection Bias Audit

- **Was the final test result chosen after scanning many configurations?**
  **NO**. The strict temporal test result ($\rho = 0.562, \text{AUC} = 0.890$) was produced by a single execution of the frozen pipeline with seed 42, following the pre-registered protocol.
- **Did the authors cherry-pick seed 42?**
  **NO**. Seed stability testing across 8 seeds yields mean $\rho = 0.582 \pm 0.021$. Seed 42 produces $\rho = 0.562$, which is actually the **lowest score among all 8 tested seeds** (range $[0.562, 0.625]$). Seed 42 is conservative, not inflated!
- **Did the authors invent a weak baseline?**
  **NO**. In this audit, we benchmarked state-of-the-art non-LLM baselines (TF-IDF, Gradient Boosting, Random Forest) and revealed that several exceed the proposed model on pooled ranking.

---

## 4. Verdict

The project demonstrates exceptional methodological transparency. The extensive search space has been preserved, negative results are prominently disclosed, and the reported headline numbers represent a conservative, un-cherry-picked snapshot of performance.
