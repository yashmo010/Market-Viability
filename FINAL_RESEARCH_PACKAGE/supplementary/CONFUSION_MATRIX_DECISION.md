# CONFUSION MATRIX DECISION MEMORANDUM
**Decision & Methodological Justification — Current Modified Project**  
**Status**: APPROVED FOR SUPPLEMENTARY AUDIT / OMITTED FROM MAIN TEXT  

---

## 1. Problem Formulation & Task Definition

In product viability prediction, the ground-truth target is inherently continuous: a **review-derived market-success proxy** scaled from 0 to 100. Evaluating continuous regression using binary classification metrics (e.g., accuracy, precision, recall, F1, MCC, and confusion matrices) poses significant methodological hazards:
1. It requires defining arbitrary threshold cutoffs on a continuous scale, which risks post-hoc threshold tuning and data snooping.
2. It discards fine-grained ranking information among intermediate products (the middle 60% of the market).
3. If presented indiscriminately, it leads reviewers to confuse regression error with classification error.

However, a secondary derived decision task is practically valuable for venture capital and retail inventory allocation:
> **Extreme-Group Discrimination**: Can the model decisively separate the **top 20% highest-performing products** from the **bottom 20% lowest-performing products**, excluding the ambiguous middle 60%?

---

## 2. Empirical Confusion Matrix (Current Temporal Holdout, $n=124$)

Under the strictly frozen temporal holdout ($n = 124$), selecting products below the 20th percentile ($y \le 27.67$, $n = 25$) and above the 80th percentile ($y \ge 72.82$, $n = 25$) yields $n = 50$ extreme items.

Evaluating predictions from `xgb_coldstart_rich_promoted.json` against this derived task yields:

| Actual Category | Predicted Top 20% | Predicted Bottom 20% | Total |
|---|---|---|---|
| **Actual Top 20% (Market Winners)** | **23 (TP)** | 2 (FN) | 25 |
| **Actual Bottom 20% (Market Flops)** | 2 (FP) | **23 (TN)** | 25 |
| **Total Predicted** | 25 | 25 | 50 |

### Associated Derived Metrics:
- **ROC-AUC**: **0.9712** (Threshold-independent separation, 95% CI: [0.9328, 1.0000])
- **Accuracy**: **92.00%** (46 / 50 correctly categorized)
- **Precision (Top 20%)**: **92.00%** (23 / 25)
- **Recall (Top 20%)**: **92.00%** (23 / 25)
- **Specificity**: **92.00%** (23 / 25)
- **Matthews Correlation Coefficient (MCC)**: **+0.8400**

---

## 3. Decision & Placement Rationale

Per Section 17 & Section 27 of the master protocol:
1. **Omit from Main Manuscript**:  
   The primary paper already communicates discrimination power concisely and without threshold bias via **ROC-AUC = 0.9712** in Table III and Table VII. Adding a confusion matrix to the main paper would consume limited IEEE column space while duplicating evidence already captured by AUC and the residual scatter plot (Fig. 7).
2. **Include in Supplementary Audit**:  
   This memorandum and the contingency counts are preserved in the **Supplementary Audit Package** (`FINAL_AUDIT/CONFUSION_MATRIX_DECISION.md`) to provide immediate, transparent answers should a reviewer request explicit contingency tables.
