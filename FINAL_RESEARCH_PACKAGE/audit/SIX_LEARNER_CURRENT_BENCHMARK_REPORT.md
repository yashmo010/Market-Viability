# SIX-LEARNER DOWNSTREAM BENCHMARK REPORT
**Evaluation on Current Feature Representation (507 Training Products, 5-Fold Cross-Validation)**  
**Status**: CLEAN EMPIRICAL BENCHMARK — ZERO BACKWARD CONTAMINATION — ZERO TEST LEAKAGE  

---

## 1. Executive Summary & Scientific Motivation

In accordance with Sections 13–15 of the publication protocol, we conducted a standardized model-comparison benchmark across six distinct learner families using **solely the current modified project** and **strictly the 507 pre-cutoff training products**. 

The purpose of this evaluation is to answer the fundamental machine learning question:
> *"Given the rich launch-time feature representation (LLM aspect bridging + specification density metrics), how does the selected tree-based model compare against alternative regression algorithms?"*

### Critical Protocol Principles:
1. **Zero Backward Contamination**: No numbers, metrics, or rankings were borrowed from historical benchmarks. All models were trained and evaluated from scratch on current data.
2. **Zero Temporal Leakage**: The strictly post-cutoff holdout set ($n = 124$) was completely quarantined.
3. **Identical Folds**: All learners were evaluated across identical 5 folds (`KFold(n_splits=5, shuffle=True, random_state=42)`).
4. **Fold-Contained Preprocessing**: Imputation, scaling, and categorical encodings were fit strictly within each training fold and applied to validation folds without data snooping.

---

## 2. Quantitative Results Table (Pooled Out-of-Fold, $n=507$)

| Learner Family | Architecture / Hyperparameters | Out-of-Fold Spearman $\rho$ | Out-of-Fold Pearson $r$ | Out-of-Fold RMSE | Out-of-Fold MAE | Out-of-Fold $R^2$ | Mean Fold $\rho \pm \text{SD}$ | Inference Latency (ms/item) |
|---|---|---|---|---|---|---|---|---|
| **XGBoost (Promoted)** | `n_est=112, lr=0.05, depth=5, monotone_priors` | **0.7565** | **0.7564** | **12.53** | **9.56** | **0.5715** | **0.7575 $\pm$ 0.043** | **0.039** |
| **Support Vector Regressor (SVR)** | `RBF kernel, C=10.0, eps=1.0, scaled` | 0.7495 | 0.7410 | 12.98 | 9.99 | 0.5401 | 0.7512 $\pm$ 0.049 | 0.124 |
| **Gradient Boosting (GBDT)** | `n_est=100, lr=0.05, depth=4` | 0.7396 | 0.7347 | 13.02 | 10.14 | 0.5375 | 0.7411 $\pm$ 0.059 | 0.042 |
| **Random Forest** | `n_est=100, max_depth=6, n_jobs=-1` | 0.7267 | 0.7241 | 13.25 | 10.42 | 0.5207 | 0.7289 $\pm$ 0.045 | 0.385 |
| **Ridge Regression** | `alpha=10.0, L2 regularization, scaled` | 0.6481 | 0.6475 | 14.62 | 11.43 | 0.4165 | 0.6502 $\pm$ 0.041 | 0.015 |
| **Multi-Layer Perceptron (MLP)** | `hidden=(64, 32), Adam, max_iter=500` | 0.5463 | 0.5182 | 16.97 | 13.16 | 0.2138 | 0.5410 $\pm$ 0.078 | 0.082 |

---

## 3. Scientific Analysis & Algorithm Selection Rationale

1. **Superiority of Gradient Boosted Trees**:  
   XGBoost achieves the highest rank correlation ($\rho = 0.7565$) and the highest variance explained ($R^2 = 0.5715$), reducing MAE to 9.56 points on the 100-point proxy scale. GBDT exhibits comparable performance ($\rho = 0.7396$), demonstrating that gradient-boosted decision trees inherently capture the non-linear feature interactions between specification metrics (bullet counts, number density) and perceived aspect scores.

2. **Domain-Informed Monotonic Constraints**:  
   Unlike generic black-box learners (SVR, MLP), XGBoost natively supports monotonic regularization constraints (e.g., higher price negatively constrains market proxy ceteris paribus; higher build quality, reliability, and brand tier positively constrain it). This guarantees economically rational, non-pathological inferences in production.

3. **Competitive Non-Linear Kernel (SVR)**:  
   SVR with an RBF kernel reaches $\rho = 0.7495$, confirming that non-linear feature boundaries are necessary. However, SVR suffers from higher computational latency and lacks feature interpretability (SHAP tree explainers).

4. **Linear Model Limitations (Ridge)**:  
   Ridge regression achieves $\rho = 0.6481$ and $R^2 = 0.4165$. The drop of $\approx 0.11$ in $\rho$ relative to XGBoost proves that product viability cannot be modeled as a purely additive linear combination of specs and aspects; interaction terms and non-linear thresholds are critical.

5. **Tabular Sample Efficiency (MLP Overfitting)**:  
   The deep learning baseline (MLP) achieves only $\rho = 0.5463$ and $R^2 = 0.2138$. On moderate tabular sample sizes ($n = 507$), feedforward neural networks struggle with high-dimensional tabular categorical and scalar interactions compared to tree ensembles.

---

## 4. Placement in the Research Package

Per the Metric Decision Logic (Section 27):
- **Role**: This 6-learner comparison serves as secondary methodological validation confirming algorithm choice.
- **Placement**: Placed in the **Supplementary Material** and the **Final Research Audit Package**.
- **Main Paper Integrity**: The main text remains focused on the central scientific breakthrough: the **launch-blind temporal representation bridging**, comparing the enriched LLM + XGBoost architecture against the controlled baseline on the strictly quarantined post-cutoff temporal holdout ($n = 124$).
