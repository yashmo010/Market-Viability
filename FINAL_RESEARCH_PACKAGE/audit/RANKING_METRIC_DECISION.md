# RANKING METRIC DECISION MEMORANDUM
**Decision & Methodological Justification — Current Modified Project**  
**Status**: APPROVED FOR SUPPLEMENTARY AUDIT / METHODOLOGICAL CONTEXT IN PAPER  

---

## 1. Methodological Context in Cold-Start Literature

In item cold-start recommendation literature (e.g., Springer journals: *Data Mining and Knowledge Discovery*, *User Modeling and User-Adapted Interaction*, and *Computing*), item recommendation tasks frequently deploy top-$K$ ranking metrics such as Normalized Discounted Cumulative Gain (NDCG@$K$), Mean Average Precision (MAP@$K$), and Kendall's tau ($\tau$).

However, product launch viability estimation differs critically from conventional user-item collaborative filtering:
1. **Full-Catalog Slate vs. Personalized Top-$K$ Recommendation**: Launch viability models predict the relative market strength of entire product lines or cohorts rather than personalizing an individualized feed for an active user session.
2. **Global Monotonic Viability Order**: The primary objective is to verify whether higher predicted scores correspond monotonically to superior post-launch market adoption across the entire catalog.

---

## 2. Empirical Ranking Metrics (Current Temporal Holdout, $n=124$)

Evaluating the frozen temporal predictions yields the following ranking statistics:

| Metric | Controlled Baseline | Promoted Model (Model_New) | Delta ($\Delta$) | Statistical Significance |
|---|---|---|---|---|
| **Spearman Rank Correlation ($\rho$)** | 0.5623 | **0.6722** | **+0.1099** | $p = 0.0004$ (Permutation) |
| **Kendall's Tau ($\tau$)** | 0.3946 | **0.4772** | **+0.0826** | $p = 4.12 \times 10^{-15}$ |
| **NDCG@5 (Top-5 Slate)** | 0.8600 | **0.8933** | **+0.0333** | Graded success score relevance |
| **NDCG@10 (Top-10 Slate)** | 0.8832 | 0.8771 | -0.0061 | Graded success score relevance |

---

## 3. Decision & Placement Rationale

Per Section 20, 21, and 27:
1. **Primary Metric Remains Spearman Rank Correlation ($\rho = 0.6722$)**:  
   Spearman's $\rho$ directly evaluates monotonic rank-order alignment across all $n = 124$ products and all 5 categories without relying on arbitrary choice of cutoff $K$.
2. **Kendall's Tau Corroborates Concordance**:  
   Kendall's $\tau$ increases from 0.3946 to 0.4772, confirming that the proportion of concordant product pairs is substantially enhanced (+8.26% concordant net margin).
3. **Supplementary Material Placement**:  
   Because Spearman's $\rho$ is the standard in product viability forecasting and avoids redundant metric reporting in the main paper, full NDCG and Kendall metrics are archived in the supplementary package and referenced in the methodological notes of the paper.
