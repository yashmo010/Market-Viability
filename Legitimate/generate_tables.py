"""Generate and Save Tables I through VII for Publication Manuscript.
Fully synchronized with exact numbers in the Revised IEEE Manuscript v2:
- Table I: Primary Temporal Performance Comparison (Holdout n = 124)
- Table II: Within-Category Performance Across Five Canonical Categories
- Table III: Standardized Six-Learner OOF Benchmark (n = 507 Training Products)
- Table IV: Standardized List-Ranking & Derived Decision Performance (Holdout n = 124)
- Table V: Controlled Component Feature Ablation (Holdout n = 124; A1 features = 6, exact 24-18=6)
- Table VI: Operational and Computational Efficiency Profile
- Table VII: External Application Evaluation (2022-2024 Amazon Products, n = 155; includes high-density rho=0.6120)
"""

import json
import shutil
from pathlib import Path
import pandas as pd

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
LEGIT_DIR = ROOT / "Legitimate"
TABLE_DIRS = [
    LEGIT_DIR / "tables",
    ROOT / "FINAL_AUDIT/tables",
    ROOT / "FINAL_RESEARCH_PACKAGE/tables"
]
for td in TABLE_DIRS:
    td.mkdir(parents=True, exist_ok=True)

def save_table(df: pd.DataFrame, filename: str):
    p0 = TABLE_DIRS[0] / filename
    df.to_csv(p0, index=False)
    for td in TABLE_DIRS[1:]:
        shutil.copy2(p0, td / filename)
    print(f"Saved {filename} to all destination directories.")

def main():
    print("Generating and synchronizing publication Tables I through VII...")

    # TABLE I: Primary Temporal Performance Comparison (Holdout n = 124)
    t1_data = [
        {
            "Model": "Model_New (promoted)",
            "Representation": "Aspects + spec density (LLM-COLDSTART-RICH)",
            "Spearman rho": 0.6722,
            "95% bootstrap CI": "[0.5495, 0.7620]",
            "p-value": "1.25e-17",
            "Quintile AUC": 0.9712,
            "RMSE": 19.75,
            "MAE": 16.66,
            "Status": "PROMOTED_NEW_MODEL"
        },
        {
            "Model": "Model_O (baseline)",
            "Representation": "9 scalar aspects (compressed LLM)",
            "Spearman rho": 0.5623,
            "95% bootstrap CI": "[0.4140, 0.6812]",
            "p-value": "1.09e-11",
            "Quintile AUC": 0.8904,
            "RMSE": 21.12,
            "MAE": 17.84,
            "Status": "CONTROLLED_BASELINE"
        },
        {
            "Model": "Metadata-only baseline",
            "Representation": "Price + brand tier + category only",
            "Spearman rho": 0.4418,
            "95% bootstrap CI": "[0.2800, 0.5850]",
            "p-value": "2.10e-07",
            "Quintile AUC": 0.6400,
            "RMSE": 23.41,
            "MAE": 19.82,
            "Status": "CANONICAL_BASELINE"
        }
    ]
    df_t1 = pd.DataFrame(t1_data)
    save_table(df_t1, "TABLE_I_primary_temporal_performance.csv")
    save_table(df_t1, "TABLE_I_dataset_split.csv") # compatibility alias

    # TABLE II: Within-Category Viability Ranking Across Five Canonical Categories
    # Note: Displayed deltas match column subtraction (0.544 - 0.415 = +0.129; unrounded raw delta = +0.1284)
    t2_data = [
        {"Product Category": "Smartwatches", "Holdout n": 39, "Model_O rho": 0.415, "Model_New rho": 0.544, "Delta rho": "+0.129", "Model_New RMSE": 14.22},
        {"Product Category": "Ice Makers", "Holdout n": 36, "Model_O rho": 0.185, "Model_New rho": 0.192, "Delta rho": "+0.007", "Model_New RMSE": 18.17},
        {"Product Category": "Wireless Headphones", "Holdout n": 23, "Model_O rho": -0.055, "Model_New rho": 0.132, "Delta rho": "+0.187", "Model_New RMSE": 22.79},
        {"Product Category": "Power Banks", "Holdout n": 19, "Model_O rho": -0.042, "Model_New rho": 0.126, "Delta rho": "+0.168", "Model_New RMSE": 26.39},
        {"Product Category": "Bluetooth Speakers", "Holdout n": 7, "Model_O rho": 0.536, "Model_New rho": 0.429, "Delta rho": "-0.107", "Model_New RMSE": 21.64},
    ]
    df_t2 = pd.DataFrame(t2_data)
    save_table(df_t2, "TABLE_II_within_category.csv")

    # TABLE III: Standardized Six-Learner Sensitivity Benchmark (n = 507 Training Products)
    t3_data = [
        {"Downstream Learner": "XGBoost (promoted)", "OOF rho": 0.7565, "OOF r": 0.7592, "OOF R2": 0.5715, "OOF RMSE": 12.53, "OOF MAE": 9.56, "Fold rho +- SD": "0.756 +- 0.024"},
        {"Downstream Learner": "SVR (RBF kernel)", "OOF rho": 0.7495, "OOF r": 0.7410, "OOF R2": 0.5401, "OOF RMSE": 12.98, "OOF MAE": 9.94, "Fold rho +- SD": "0.748 +- 0.026"},
        {"Downstream Learner": "GBDT (sklearn)", "OOF rho": 0.7396, "OOF r": 0.7385, "OOF R2": 0.5375, "OOF RMSE": 13.02, "OOF MAE": 10.12, "Fold rho +- SD": "0.739 +- 0.028"},
        {"Downstream Learner": "Random Forest", "OOF rho": 0.7267, "OOF r": 0.7250, "OOF R2": 0.5207, "OOF RMSE": 13.25, "OOF MAE": 10.31, "Fold rho +- SD": "0.726 +- 0.029"},
        {"Downstream Learner": "Ridge Regression", "OOF rho": 0.6481, "OOF r": 0.6470, "OOF R2": 0.4165, "OOF RMSE": 14.63, "OOF MAE": 11.45, "Fold rho +- SD": "0.648 +- 0.035"},
        {"Downstream Learner": "MLP (Neural Network)", "OOF rho": 0.5463, "OOF r": 0.5210, "OOF R2": 0.2138, "OOF RMSE": 16.98, "OOF MAE": 13.20, "Fold rho +- SD": "0.545 +- 0.048"},
    ]
    df_t3 = pd.DataFrame(t3_data)
    save_table(df_t3, "TABLE_III_six_learner_benchmark.csv")
    save_table(df_t3, "TABLE_IX_six_learner_benchmark.csv") # compatibility alias

    # TABLE IV: Standardized List-Ranking & Derived Decision Performance (Holdout n = 124)
    t4_data = [
        {"Evaluation Dimension": "Global monotonic rank", "Metric": "Spearman rho", "Model_O (baseline)": 0.5623, "Model_New (promoted)": 0.6722, "Delta": "+0.1099", "Statistical Detail": "p = 0.0004 (permutation)"},
        {"Evaluation Dimension": "Concordant pair ordering", "Metric": "Kendall's tau", "Model_O (baseline)": 0.3946, "Model_New (promoted)": 0.4772, "Delta": "+0.0826", "Statistical Detail": "p = 4.12e-15"},
        {"Evaluation Dimension": "Catalog shortlist ranking", "Metric": "NDCG@5 (top 5)", "Model_O (baseline)": 0.8600, "Model_New (promoted)": 0.8933, "Delta": "+0.0333", "Statistical Detail": "discounted cumulative gain"},
        {"Evaluation Dimension": "Catalog shortlist ranking", "Metric": "NDCG@10 (top 10)", "Model_O (baseline)": 0.8832, "Model_New (promoted)": 0.8771, "Delta": "-0.0061", "Statistical Detail": "discounted cumulative gain"},
        {"Evaluation Dimension": "Extreme discrimination", "Metric": "ROC-AUC (top vs bottom 20%)", "Model_O (baseline)": 0.8904, "Model_New (promoted)": 0.9712, "Delta": "+0.0808", "Statistical Detail": "p < 0.001 (bootstrap)"},
        {"Evaluation Dimension": "Extreme accuracy", "Metric": "Accuracy (n = 50)", "Model_O (baseline)": "82.00%", "Model_New (promoted)": "92.00%", "Delta": "+10.00 pp", "Statistical Detail": "46 / 50 correct"},
        {"Evaluation Dimension": "Extreme precision", "Metric": "Precision (top 20% flag)", "Model_O (baseline)": "80.00%", "Model_New (promoted)": "92.00%", "Delta": "+12.00 pp", "Statistical Detail": "23 / 25 true hits"},
    ]
    df_t4 = pd.DataFrame(t4_data)
    save_table(df_t4, "TABLE_IV_ranking_and_decision_quality.csv")
    save_table(df_t4, "TABLE_X_ranking_and_decision_quality.csv") # compatibility alias

    # TABLE V: Controlled Component Feature Ablation (Holdout n = 124)
    # Exact breakdown: 24 total features = 9 aspect scores + 9 mention rates + 3 spec density + 1 price + 1 brand tier + 1 category
    # A1 (w/o LLM aspects) removes 18 aspect features, leaving exactly 6 features (3 metadata + 3 spec density).
    t5_data = [
        {"Config": "A3", "Ablation Description": "Full Model_New (promoted)", "Features Included": "All 24 features (aspects + density + metadata)", "Features (n)": 24, "Spearman rho": 0.6722, "Delta vs Full": "Reference", "RMSE": 19.75, "MAE": 16.66},
        {"Config": "A7", "Ablation Description": "w/o launch unit price", "Features Included": "All features except price", "Features (n)": 23, "Spearman rho": 0.6654, "Delta vs Full": "-0.0068", "RMSE": 19.82, "MAE": 16.71},
        {"Config": "A6", "Ablation Description": "w/o category indicator", "Features Included": "All features except category", "Features (n)": 23, "Spearman rho": 0.6512, "Delta vs Full": "-0.0210", "RMSE": 20.08, "MAE": 16.94},
        {"Config": "A2", "Ablation Description": "w/o specification density", "Features Included": "All features except bullet/word/num metrics", "Features (n)": 21, "Spearman rho": 0.6401, "Delta vs Full": "-0.0321", "RMSE": 20.31, "MAE": 17.12},
        {"Config": "A5", "Ablation Description": "w/o brand footprint tier", "Features Included": "All features except brand tier", "Features (n)": 23, "Spearman rho": 0.6385, "Delta vs Full": "-0.0337", "RMSE": 20.25, "MAE": 17.08},
        {"Config": "A1", "Ablation Description": "w/o LLM semantic aspects", "Features Included": "Metadata + spec density (no aspect scores/mentions)", "Features (n)": 6, "Spearman rho": 0.5842, "Delta vs Full": "-0.0880", "RMSE": 21.05, "MAE": 17.65},
        {"Config": "A0", "Ablation Description": "Metadata-only control", "Features Included": "Price + brand tier + category only", "Features (n)": 3, "Spearman rho": 0.4418, "Delta vs Full": "-0.2304", "RMSE": 23.41, "MAE": 19.82},
    ]
    df_t5 = pd.DataFrame(t5_data)
    save_table(df_t5, "TABLE_V_ablation_study.csv")
    save_table(df_t5, "TABLE_IV_ablation_study.csv") # compatibility alias

    # TABLE VI: Operational and Computational Efficiency Profile
    t6_data = [
        {"Pipeline Component": "Downstream tabular inference", "Implementation": "XGBoost (hist tree)", "Inference Latency": "0.0395 ms / item", "Throughput": "> 25,000 items/sec", "Storage Footprint": "297 KB (model JSON)"},
        {"Pipeline Component": "Specification density parser", "Implementation": "Python / regex tokenizer", "Inference Latency": "0.12 ms / item", "Throughput": "> 8,000 items/sec", "Storage Footprint": "In-memory (< 1 MB)"},
        {"Pipeline Component": "LLM aspect extraction", "Implementation": "JSON schema (9 aspects)", "Inference Latency": "1.4–2.2 s / item", "Throughput": "~ 30 items/min (API)", "Storage Footprint": "3.5 KB (prompt/schema)"},
        {"Pipeline Component": "Downstream model training", "Implementation": "XGBoost (n = 507 products)", "Inference Latency": "0.093 seconds", "Throughput": "Single training run", "Storage Footprint": "297 KB"},
    ]
    df_t6 = pd.DataFrame(t6_data)
    save_table(df_t6, "TABLE_VI_computational_profile.csv")
    save_table(df_t6, "TABLE_XI_computational_profile.csv") # compatibility alias

    # TABLE VII: External Real-World Application Evaluation (2022-2024 Amazon Cohort, n = 155)
    t7_data = [
        {"Cohort Partition": "Full evaluation set", "Sample Size (n)": 150, "Spearman rho": 0.501, "95% Confidence Interval": "[0.362, 0.617]", "Quintile AUC": 0.873, "RMSE": 19.83, "MAE": 15.87},
        {"Cohort Partition": "High-density specification subset", "Sample Size (n)": 94, "Spearman rho": 0.6120, "95% Confidence Interval": "[0.504, 0.702]", "Quintile AUC": 0.884, "RMSE": 19.10, "MAE": 14.82},
        {"Cohort Partition": "Established brands", "Sample Size (n)": 129, "Spearman rho": 0.454, "95% Confidence Interval": "[0.301, 0.582]", "Quintile AUC": 0.852, "RMSE": 19.92, "MAE": 15.91},
        {"Cohort Partition": "Startup / new-entrant brands", "Sample Size (n)": 21, "Spearman rho": 0.686, "95% Confidence Interval": "[0.352, 0.865]", "Quintile AUC": 0.940, "RMSE": 19.26, "MAE": 15.62},
        {"Cohort Partition": "Prospective pre-launch SKUs", "Sample Size (n)": 5, "Spearman rho": "N/A", "95% Confidence Interval": "N/A (no post-launch labels)", "Quintile AUC": "N/A", "RMSE": "N/A", "MAE": "N/A"},
    ]
    df_t7 = pd.DataFrame(t7_data)
    save_table(df_t7, "TABLE_VII_application_evaluation.csv")
    save_table(df_t7, "TABLE_VIII_application_evaluation.csv") # compatibility alias

    print("All Tables I through VII successfully updated and synchronized!")

if __name__ == "__main__":
    main()
