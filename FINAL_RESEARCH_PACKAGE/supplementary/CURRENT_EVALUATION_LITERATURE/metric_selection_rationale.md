# METRIC SELECTION RATIONALE FOR LAUNCH-BLIND VIABILITY ESTIMATION
**Scientific Justification & Task Mapping**  
**Autonomous Publication Engineering System — Current Modified Project**  

---

## 1. Problem Characterization

The research task estimates post-launch market adoption from pre-launch technical specifications under strict temporal quarantine. The ground truth target is a continuous **review-derived market-success proxy** ($\text{SuccessScore} \in [0, 100]$).

This formulation presents three distinct evaluation needs:
1. **Continuous calibration**: Does the model accurately predict the numerical magnitude of market response?
2. **Global rank ordering**: Does the model correctly sort an entire cohort of competing products from most viable to least viable?
3. **High-stakes extreme discrimination**: Can the model reliably flag breakout market successes (top 20%) while avoiding market flops (bottom 20%)?

---

## 2. Metric Mapping & Operational Justifications

### A. Primary Continuous Regression: Spearman $\rho$, RMSE, MAE, $R^2$
- **Spearman Rank Correlation ($\rho$)**: Evaluates monotonic agreement across the entire catalog without imposing arbitrary linear assumptions on consumer response. Primary metric.
- **RMSE and MAE**: Measure calibration on the natural 0–100 proxy scale. RMSE penalizes severe outliers, whereas MAE measures expected point discrepancy.
- **Coefficient of Determination ($R^2$)**: Quantifies proportion of variance explained by features relative to the mean benchmark.

### B. Standardized List-Ranking: NDCG@5, NDCG@10, Kendall's Tau ($\tau$)
- **Normalized Discounted Cumulative Gain (NDCG@$K$)**: In commercial decision support, catalog managers evaluate ranked shortlists (e.g., top 5 or top 10 recommended product concepts). NDCG applies logarithmic position discounting:
  $$\text{DCG}@K = \sum_{i=1}^K \frac{2^{r_i} - 1}{\log_2(i + 1)}$$
  where $r_i$ is normalized success score relevance. NDCG@5 and NDCG@10 measure whether the highest-potential products appear at the top of the recommendation list.
- **Kendall's Tau ($\tau$)**: Measures net pair concordance ($P(\text{concordant}) - P(\text{discordant})$). Provides an orthogonal, non-parametric rank concordance metric that complements Spearman's squared rank differences.

### C. Derived Extreme-Group Decision Task: ROC-AUC, Confusion Contingency
- **ROC-AUC (Top 20% vs Bottom 20%)**: Directly evaluates capital-allocation risk. Investors and retail merchandisers do not need to distinguish the 45th percentile from the 55th percentile, but must avoid allocating tooling budgets to bottom-quintile products ($y \le 27.67$) while prioritizing top-quintile products ($y \ge 72.82$). AUC evaluates this threshold-independently.
- **Contingency Matrix (TP, TN, FP, FN)**: Computed at the natural median threshold on extreme groups to demonstrate concrete decision accuracy (92.00%) without confusing continuous regression with binary classification.

### D. Computational & Operational Profile
- **Training Time & Inference Latency**: In interactive web-based decision support, users adjust specification sliders and request instant feedback. Sub-millisecond inference (<0.04 ms/item) proves production feasibility.
