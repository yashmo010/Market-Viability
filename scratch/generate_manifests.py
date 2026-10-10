"""Generate complete audit manifests for Figures and Tables including new evaluations.
"""

import csv
import shutil
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
AUDIT_DIR = ROOT_DIR / "FINAL_AUDIT"
CURRENT_AUDIT_DIR = ROOT_DIR / "FINAL_CURRENT_PROJECT_AUDIT"

def make_figure_manifest():
    figs = [
        {
            "artifact": "Figure 1 (fig1_pipeline.png)",
            "source_dataset": "Architecture Specification",
            "source_result_file": "Legitimate/02_LLM_REPRESENTATION/LLM_SCHEMA.json",
            "model_version": "xgb_coldstart_rich_promoted",
            "evaluation_split": "End-to-End System Diagram",
            "n": "Full Pipeline",
            "metric": "Architecture Flow (Date-Free, 24 Features, 5 Categories)",
            "generation_script": "Legitimate/generate_publication_figures.py (make_fig1)",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Figure 2 (fig2_temporal_protocol.png)",
            "source_dataset": "Strict Temporal Holdout Protocol",
            "source_result_file": "strict_temporal/frozen_state",
            "model_version": "Temporal Quarantine",
            "evaluation_split": "Train (507) vs Test (124)",
            "n": "631 Total Products",
            "metric": "Strict Label Quarantine & Forward-in-Time Split",
            "generation_script": "Legitimate/generate_publication_figures.py (make_fig2)",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Figure 3 (fig3_performance_comparison.png)",
            "source_dataset": "Temporal Holdout (124 products)",
            "source_result_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json",
            "model_version": "Controlled Baseline vs Promoted (Model_New)",
            "evaluation_split": "Post-Cutoff Holdout",
            "n": "124",
            "metric": "Spearman rho (0.672 vs 0.562) & Extreme-Group AUC (0.971 vs 0.890)",
            "generation_script": "Legitimate/generate_publication_figures.py (make_fig3)",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Figure 4 (fig4_cold_start.png)",
            "source_dataset": "Unseen Brand Holdout (Tier 0)",
            "source_result_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json",
            "model_version": "Controlled Baseline vs Promoted",
            "evaluation_split": "Tier-0 Unseen Brands",
            "n": "90",
            "metric": "Spearman rho (0.633 vs 0.516) & AUC (0.982 vs 0.884)",
            "generation_script": "Legitimate/generate_publication_figures.py (make_fig4)",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Figure 5 (fig5_within_category.png)",
            "source_dataset": "Category-Specific Temporal Holdout",
            "source_result_file": "Legitimate/04_EXPERIMENTS/WITHIN_CATEGORY_ANALYSIS.csv",
            "model_version": "Controlled Baseline vs Promoted",
            "evaluation_split": "5 Canonical Categories",
            "n": "124 (7, 18, 30, 31, 38)",
            "metric": "Disaggregated Spearman rho across 5 Categories",
            "generation_script": "Legitimate/generate_publication_figures.py (make_fig5)",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Figure 6 (fig6_ablation.png)",
            "source_dataset": "Controlled Component Feature Ablation",
            "source_result_file": "Legitimate/04_EXPERIMENTS/ABLATION_STUDY.csv",
            "model_version": "Ablated XGBoost Variants (A0-A7)",
            "evaluation_split": "Post-Cutoff Holdout",
            "n": "124",
            "metric": "Spearman rho & RMSE across Feature Drop Configurations",
            "generation_script": "Legitimate/generate_publication_figures.py (make_fig6)",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Figure 7 (fig7_scatter.png)",
            "source_dataset": "Test Predictions vs Ground Truth",
            "source_result_file": "Legitimate/08_FINAL_MODEL/test_predictions.csv",
            "model_version": "Promoted Model (xgb_coldstart_rich_promoted)",
            "evaluation_split": "Post-Cutoff Holdout",
            "n": "124",
            "metric": "Predicted Viability vs Observed Market Proxy Residual Fit",
            "generation_script": "Legitimate/generate_publication_figures.py (make_fig7)",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Figure 8 (fig8_six_learner_benchmark.png)",
            "source_dataset": "Training Cohort 5-Fold OOF (n=507)",
            "source_result_file": "FINAL_AUDIT/CURRENT_OOF_BENCHMARK/oof_metrics_summary.json",
            "model_version": "6 Learner Families (XGBoost, SVR, GBDT, RF, Ridge, MLP)",
            "evaluation_split": "5-Fold Out-of-Fold CV",
            "n": "507",
            "metric": "Spearman rho with fold SD, R2, and RMSE calibration",
            "generation_script": "scratch/build_comprehensive_evaluations.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Figure 9 (fig9_ranking_decision_quality.png)",
            "source_dataset": "Temporal Holdout Predictions (n=124)",
            "source_result_file": "FINAL_AUDIT/CURRENT_RANKING_METRICS/ranking_metrics.json, CURRENT_DECISION_METRICS/extreme_group_metrics.json",
            "model_version": "Controlled Baseline vs Promoted (Model_New)",
            "evaluation_split": "Post-Cutoff Holdout & Extreme Quintiles (n=50)",
            "n": "124 (extreme n=50)",
            "metric": "NDCG@5, NDCG@10, Kendall tau, ROC Curve (AUC=0.9712 vs 0.8904)",
            "generation_script": "scratch/build_comprehensive_evaluations.py",
            "status": "FROZEN_VERIFIED"
        }
    ]

    for p in [CURRENT_AUDIT_DIR / "FIGURE_SOURCE_MANIFEST.csv", AUDIT_DIR / "FIGURE_SOURCE_MANIFEST.csv", AUDIT_DIR / "FIGURE_AUDIT.csv"]:
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(figs[0].keys()))
            writer.writeheader()
            writer.writerows(figs)
    print("Wrote FIGURE_SOURCE_MANIFEST.csv and FIGURE_AUDIT.csv (Figs 1-9)")

def make_table_manifest():
    tabs = [
        {
            "artifact": "Table I",
            "source_dataset": "Product Corpus (strict_temporal)",
            "source_result_file": "train/products.json, test_inputs/products_test_specs.json",
            "model_version": "N/A (Corpus Specification)",
            "evaluation_split": "Training (507) vs Holdout (124)",
            "n": "631 Total",
            "metric": "Category Distribution & Brand Tier Breakdown",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table II",
            "source_dataset": "Engineered Representation Manifest",
            "source_result_file": "Legitimate/08_FINAL_MODEL/feature_manifest.json",
            "model_version": "Promoted Feature Set",
            "evaluation_split": "N/A (Feature Taxonomy)",
            "n": "24 Features",
            "metric": "Feature Definitions, Constraints, and Extractions",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table III",
            "source_dataset": "Temporal Holdout (124 products)",
            "source_result_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json",
            "model_version": "Controlled Baseline vs Promoted",
            "evaluation_split": "Post-Cutoff Holdout",
            "n": "124",
            "metric": "Spearman rho, 95% CI, p-value, AUC, RMSE, MAE",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table IV",
            "source_dataset": "Controlled Component Ablation",
            "source_result_file": "Legitimate/04_EXPERIMENTS/ABLATION_STUDY.csv",
            "model_version": "Ablated XGBoost Models",
            "evaluation_split": "Post-Cutoff Holdout",
            "n": "124",
            "metric": "Spearman rho, Delta rho, RMSE, MAE",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table V",
            "source_dataset": "Category Holdout",
            "source_result_file": "Legitimate/04_EXPERIMENTS/WITHIN_CATEGORY_ANALYSIS.csv",
            "model_version": "Controlled Baseline vs Promoted",
            "evaluation_split": "5 Canonical Categories",
            "n": "124 (7, 18, 30, 31, 38)",
            "metric": "Category-Specific rho, Delta rho, RMSE",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table VI",
            "source_dataset": "Tier-0 Cold-Start Holdout",
            "source_result_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json",
            "model_version": "Controlled Baseline vs Promoted",
            "evaluation_split": "Unseen Brands (Tier 0)",
            "n": "90",
            "metric": "Spearman rho, AUC, Delta vs Baseline",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table VII",
            "source_dataset": "Paired Statistical Evaluation",
            "source_result_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json",
            "model_version": "Promoted vs Controlled Baseline",
            "evaluation_split": "Post-Cutoff Holdout (Paired)",
            "n": "124 paired",
            "metric": "Delta rho, Bootstrap 95% CI, Permutation p-value",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table VIII",
            "source_dataset": "External Amazon Cohort (2022-2024)",
            "source_result_file": "Legitimate/application_evaluation/EXTERNAL_EVALUATION_REPORT.md",
            "model_version": "Promoted Model (xgb_coldstart_rich_promoted)",
            "evaluation_split": "External Real-World Cohort",
            "n": "155",
            "metric": "Spearman rho, 95% CI, p-value, AUC, MAE",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table IX",
            "source_dataset": "Training Cohort 5-Fold OOF",
            "source_result_file": "FINAL_AUDIT/CURRENT_OOF_BENCHMARK/oof_metrics_summary.json",
            "model_version": "6 Learner Families (XGB, SVR, GBDT, RF, Ridge, MLP)",
            "evaluation_split": "5-Fold Out-of-Fold CV",
            "n": "507",
            "metric": "OOF rho, Pearson r, RMSE, MAE, R2, Latency",
            "generation_script": "scratch/run_clean_six_learner_benchmark.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table X",
            "source_dataset": "Temporal Holdout Predictions (n=124)",
            "source_result_file": "FINAL_AUDIT/CURRENT_RANKING_METRICS/ranking_metrics.json, CURRENT_DECISION_METRICS/extreme_group_metrics.json",
            "model_version": "Controlled Baseline vs Promoted (Model_New)",
            "evaluation_split": "Post-Cutoff Holdout & Extreme Quintiles (n=50)",
            "n": "124",
            "metric": "Spearman rho, Kendall tau, NDCG@5, NDCG@10, ROC-AUC, Accuracy, Precision",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        },
        {
            "artifact": "Table XI",
            "source_dataset": "Production Inference Profiler",
            "source_result_file": "FINAL_AUDIT/CURRENT_EFFICIENCY/computational_profile.json",
            "model_version": "Promoted Model (xgb_coldstart_rich_promoted)",
            "evaluation_split": "Runtime Profiling",
            "n": "Inference Latency & Throughput",
            "metric": "Latency (ms/item), Throughput (items/sec), Disk Size",
            "generation_script": "Legitimate/generate_tables.py",
            "status": "FROZEN_VERIFIED"
        }
    ]

    for p in [CURRENT_AUDIT_DIR / "TABLE_SOURCE_MANIFEST.csv", AUDIT_DIR / "TABLE_SOURCE_MANIFEST.csv", AUDIT_DIR / "TABLE_AUDIT.csv"]:
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(tabs[0].keys()))
            writer.writeheader()
            writer.writerows(tabs)
    print("Wrote TABLE_SOURCE_MANIFEST.csv and TABLE_AUDIT.csv (Tables I-XI)")

if __name__ == "__main__":
    make_figure_manifest()
    make_table_manifest()
