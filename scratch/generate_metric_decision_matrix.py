"""Generate FINAL_AUDIT/METRIC_DECISION_MATRIX.csv.
Evaluates candidate metrics and analyses under Section 27 decision logic.
"""

import csv
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
OUT_CSV = ROOT_DIR / "FINAL_AUDIT" / "METRIC_DECISION_MATRIX.csv"

candidates = [
    {
        "candidate_analysis": "Primary Spearman Rank Correlation (rho)",
        "task_family": "Continuous Ranking / Viability",
        "current_data_availability": "Yes (n=124 temporal, n=507 train)",
        "scientific_relevance_score": "+8 (Directly captures viability monotonicity without assuming linearity)",
        "leakage_status": "Clean (Zero leakage)",
        "redundancy_status": "Non-redundant (Primary metric)",
        "decision": "Main Paper (Core)",
        "justification": "Primary benchmark metric aligned with product viability ranking under launch-blind conditions."
    },
    {
        "candidate_analysis": "RMSE and MAE Regression Loss",
        "task_family": "Continuous Regression",
        "current_data_availability": "Yes (n=124 temporal, n=507 train)",
        "scientific_relevance_score": "+6 (Measures calibration on 0-100 proxy scale)",
        "leakage_status": "Clean (Zero leakage)",
        "redundancy_status": "Non-redundant (Supplements rank correlation with point-error magnitude)",
        "decision": "Main Paper (Core)",
        "justification": "Required to report magnitude error in proxy units alongside rank-order alignment."
    },
    {
        "candidate_analysis": "Extreme-Group ROC-AUC (Top 20% vs Bottom 20%)",
        "task_family": "Derived Binary Discrimination",
        "current_data_availability": "Yes (n=124 holdout, top=25, bot=25)",
        "scientific_relevance_score": "+5 (Threshold-independent separation of market successes vs failures)",
        "leakage_status": "Clean (Defined strictly on test label percentiles)",
        "redundancy_status": "Non-redundant (Validates high-stakes launch decisions)",
        "decision": "Main Paper (Table III, VII)",
        "justification": "Demonstrates whether investors/brands can distinguish definitive blockbusters from market flops."
    },
    {
        "candidate_analysis": "Operating-Point Classification Metrics (Accuracy, Precision, Recall, F1, MCC)",
        "task_family": "Arbitrary Threshold Classification",
        "current_data_availability": "Possible from predictions",
        "scientific_relevance_score": "-1 (Arbitrary 0.5 threshold on continuous proxy confuses regression/ranking)",
        "leakage_status": "Risk of post-hoc threshold tuning",
        "redundancy_status": "Redundant with ROC-AUC",
        "decision": "Omit from Main Paper",
        "justification": "Operating-point metrics depend on arbitrary decision thresholds; AUC provides rigorous threshold-free discrimination without misleading readers."
    },
    {
        "candidate_analysis": "Confusion Matrix for Extreme Groups",
        "task_family": "Derived Binary Decision Task",
        "current_data_availability": "Yes (n=50 extreme holdout items)",
        "scientific_relevance_score": "+1 (Visual contingency count for top/bottom)",
        "leakage_status": "Clean retrospectively",
        "redundancy_status": "Redundant with ROC-AUC and subgroup tables",
        "decision": "Supplementary Material",
        "justification": "Adds qualitative count visualization for extreme groups but redundant for main text space constraints."
    },
    {
        "candidate_analysis": "Standardized 6-Learner Benchmark (XGBoost, GBDT, RF, Ridge, SVR, MLP)",
        "task_family": "Model Family Comparison",
        "current_data_availability": "Yes (n=507 training products, 5-fold CV)",
        "scientific_relevance_score": "+5 (Confirms tree ensemble superiority over linear and neural alternatives)",
        "leakage_status": "Clean (Fold-contained CV, zero holdout leakage)",
        "redundancy_status": "Non-redundant supporting evidence",
        "decision": "Supplementary Material & Audit (Table IX summary in paper)",
        "justification": "Validates why XGBoost was promoted over SVR, RF, GBDT, Ridge, and MLP under current representation."
    },
    {
        "candidate_analysis": "Top-K Ranking Metrics (NDCG@K, Precision@K)",
        "task_family": "Information Retrieval / Recommender Ranking",
        "current_data_availability": "Yes (Available per category)",
        "scientific_relevance_score": "+2 (Valid for ranking shortlists)",
        "leakage_status": "Clean",
        "redundancy_status": "Partially redundant with Spearman rho",
        "decision": "Supplementary Material / Contextual Method Note",
        "justification": "Spearman rank correlation already captures full-slate monotonic order; NDCG@5 is noted methodologically for cold-start item literature."
    },
    {
        "candidate_analysis": "Computational Efficiency (Training & Inference Latency)",
        "task_family": "Engineering & Operational Feasibility",
        "current_data_availability": "Yes (Benchmarked on local runtime)",
        "scientific_relevance_score": "+3 (Proves millisecond real-time capability for web dashboard)",
        "leakage_status": "Clean",
        "redundancy_status": "Non-redundant operational evidence",
        "decision": "Main Paper (Section V & Dashboard Parity)",
        "justification": "Demonstrates production feasibility (<0.04 ms/item XGBoost inference vs LLM batch extraction)."
    },
    {
        "candidate_analysis": "Interpretability & Feature Importance (Gain & Monotonic Regularization)",
        "task_family": "Model Transparency / Explainability",
        "current_data_availability": "Yes (XGBoost feature importances & priors)",
        "scientific_relevance_score": "+5 (Explains which spec aspects drive viability)",
        "leakage_status": "Clean (From training fit)",
        "redundancy_status": "Non-redundant (Deepens domain insight)",
        "decision": "Main Paper (Integrated in Discussion & Application)",
        "justification": "Confirms that specification density and semantic build quality drive prediction rather than superficial noise."
    },
    {
        "candidate_analysis": "Unseen-Brand Cold-Start Evaluation (Tier-0, n=90)",
        "task_family": "Out-of-Distribution Generalization",
        "current_data_availability": "Yes (n=90 strictly post-cutoff)",
        "scientific_relevance_score": "+8 (Critical reviewer hurdle: does model work without established brand bias?)",
        "leakage_status": "Clean",
        "redundancy_status": "Non-redundant (Core finding)",
        "decision": "Main Paper (Core Figure 4, Table VI)",
        "justification": "Proves the semantic bridging extracts true product utility rather than leaning on brand equity."
    },
    {
        "candidate_analysis": "Within-Category Disaggregated Evaluation (5 Categories)",
        "task_family": "Category-Specific Viability",
        "current_data_availability": "Yes (All 5 canonical categories evaluated)",
        "scientific_relevance_score": "+7 (Reveals category-level variation and challenges)",
        "leakage_status": "Clean",
        "redundancy_status": "Non-redundant (Core finding)",
        "decision": "Main Paper (Core Figure 5, Table V)",
        "justification": "Transparently shows positive deltas across high-volume categories while detailing small-sample limitations."
    }
]

def main():
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        fields = [
            "candidate_analysis",
            "task_family",
            "current_data_availability",
            "scientific_relevance_score",
            "leakage_status",
            "redundancy_status",
            "decision",
            "justification"
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(candidates)
    print(f"Generated {OUT_CSV} with {len(candidates)} candidate evaluations.")

if __name__ == "__main__":
    main()
