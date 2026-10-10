# REVIEWER QUESTION MAPPING MATRIX
**Comprehensive Reviewer Defense Architecture — Current Modified Project**  
**Autonomous Publication Engineering System**  

---

## 1. Overview

To guarantee that every included analysis directly defends a core scientific assertion without introducing redundant fluff, each evaluation is mapped to the fundamental questions anticipated from peer reviewers.

---

## 2. Reviewer Question Defense Mapping

| Reviewer Attack / Question | Core Scientific Defense | Evidence Artifact | Empirical Values |
|---|---|---|---|
| **Q1: Why XGBoost instead of alternative tabular models?** | XGBoost achieves the top cross-validated rank correlation ($\rho=0.7565$) and $R^2=0.5715$ while natively enforcing domain-informed monotonic constraints (e.g., negative price elasticity, positive build quality priors). | **Table IX, Fig. 8** (Six-Learner OOF Benchmark) | XGBoost $\rho=0.757 \pm 0.043$ vs SVR $0.751$, GBDT $0.741$, RF $0.729$, Ridge $0.650$, MLP $0.541$. |
| **Q2: Is the model effective at continuous prediction?** | Continuous point error is bounded on the 0–100 review-derived proxy scale, outperforming baseline models across RMSE and MAE. | **Table III, Table IV, Fig. 7** | Holdout RMSE = 19.75, MAE = 16.66 (vs Baseline RMSE = 21.12, MAE = 17.83). |
| **Q3: Is the model effective at global product ranking?** | Model significantly elevates full-catalog rank monotonicity and list concordance under strictly launch-blind conditions. | **Table III, Table X, Fig. 9(a)** | Spearman $\rho = 0.6722$ (vs 0.5623, $\Delta = +0.1099$, $p=0.0004$); Kendall's $\tau = 0.4772$ (vs 0.3946); NDCG@5 = 0.8933 (vs 0.8600). |
| **Q4: Can the model reliably identify breakout winners vs market failures?** | In the derived extreme-group decision task (top 20% vs bottom 20%), the model demonstrates near-perfect discrimination without operating-point threshold leakage. | **Table III, Table X, Fig. 9(b), `CONFUSION_MATRIX_DECISION.md`** | Extreme-group ROC-AUC = 0.9712 (vs 0.8904); Contingency accuracy = 92.00% (46/50 correct: 23 TP, 23 TN, 2 FP, 2 FN). |
| **Q5: Is performance robust across alternative learner families?** | Non-linear tree and kernel models (XGBoost, SVR, GBDT, RF) consistently achieve $\rho > 0.72$ on the enriched representation, proving representation quality is algorithm-agnostic. | **Table IX, Fig. 8** | GBDT $\rho=0.7396$, SVR $\rho=0.7495$, RF $\rho=0.7267$. |
| **Q6: Is the system operationally feasible for interactive web deployment?** | Tabular inference executes in sub-millisecond real time, imposing zero runtime bottleneck in interactive decision support dashboards. | **Table XI, `EFFICIENCY_DECISION.md`** | Inference latency = 0.0395 ms / item (>25,000 items/sec throughput); Model artifact size = 297 KB. |
| **Q7: Which launch-time features contribute to viability?** | Controlled component ablation proves that LLM semantic aspect bridging is the single most critical contributor, supplemented by specification density and brand tier. | **Table IV, Fig. 6, `INTERPRETABILITY_DECISION.md`** | Dropping LLM aspects collapses $\rho$ by $-0.0880$; dropping spec density drops $\rho$ by $-0.0321$; metadata-only collapses $\rho$ by $-0.2304$. |
| **Q8: Does performance hold under true cold-start conditions for unseen brands?** | On brands with zero pre-cutoff training presence (Tier 0), the model preserves superior viability ranking and discrimination. | **Table VI, Fig. 4** | Unseen brand holdout ($n=90$): Promoted $\rho = 0.6328$, AUC = 0.9815 (vs Baseline $\rho = 0.5155$, AUC = 0.8843). |
| **Q9: Does the deployed application execute the exact evaluated model?** | End-to-end numerical parity tests between the research model and the production inference engine show bit-for-bit mathematical agreement. | **`APPLICATION_AUDIT.md`, `test_application_parity.py`** | Maximum absolute prediction discrepancy across all 124 temporal products = **0.000000** (Error = 0.0). |
