"""Generate CURRENT_FILE_INVENTORY.csv, CURRENT_DEPENDENCY_GRAPH.md, and CURRENT_RESULT_SOURCE_MAP.csv.
Operates strictly on the Current Modified Project.
"""

import os
import csv
import hashlib
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
AUDIT_DIR = ROOT_DIR / "FINAL_CURRENT_PROJECT_AUDIT"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

def hash_file(p):
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()[:16]

def generate_file_inventory():
    target_dirs = [
        ROOT_DIR / "Legitimate",
        ROOT_DIR / "FINAL_AUDIT",
        ROOT_DIR / "FINAL_FREEZE",
        ROOT_DIR / "FINAL_RESEARCH_PACKAGE",
        ROOT_DIR / "FINAL_CURRENT_PROJECT_AUDIT"
    ]

    records = []
    for d in target_dirs:
        if not d.exists():
            continue
        for p in d.rglob("*"):
            if p.is_file() and not any(part in p.parts for part in [".git", "__pycache__", ".ipynb_checkpoints"]):
                rel = p.relative_to(ROOT_DIR)
                size = p.stat().st_size
                ext = p.suffix.lower()
                records.append({
                    "relative_path": str(rel).replace("\\", "/"),
                    "category": p.parts[len(ROOT_DIR.parts)],
                    "extension": ext,
                    "size_bytes": size,
                    "sha256_prefix": hash_file(p)
                })

    out_csv = AUDIT_DIR / "CURRENT_FILE_INVENTORY.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["relative_path", "category", "extension", "size_bytes", "sha256_prefix"])
        writer.writeheader()
        writer.writerows(records)
    print(f"Generated {out_csv} with {len(records)} files.")

def generate_dependency_graph():
    graph_md = """# CURRENT DEPENDENCY GRAPH
**Autonomous Publication Engineering System — Current Modified Project**

```mermaid
graph TD
    subgraph S1 [Level 1: Ground Truth Data]
        D_TRAIN["507 Training Products<br/>(strict_temporal/data/train/products.json)"]
        D_TEST["124 Holdout Test Specs<br/>(test_inputs/products_test_specs.json)"]
        D_LABELS["124 Holdout Ground Truth<br/>(test_labels/ground_truth.json)"]
        D_EXT["155 Real-World Products<br/>(external_evaluation_dataset.json)"]
    end

    subgraph S2 [Level 2: Feature Engineering & LLM Bridging]
        F_EXTRACT["Technical Spec Parser<br/>(Legitimate/test_extraction_logic.py)"]
        F_SCHEMA["LLM 9-Aspect Schema<br/>(Legitimate/02_LLM_REPRESENTATION)"]
        F_MANIFEST["24-Feature Manifest<br/>(Legitimate/08_FINAL_MODEL/feature_manifest.json)"]
    end

    subgraph S3 [Level 3: Core Model Execution & Statistics]
        M_XGB["Promoted Monotonic XGBoost<br/>(Legitimate/08_FINAL_MODEL/xgb_coldstart_rich_promoted.json)"]
        S_STATS["Statistical Testing Suite<br/>(Legitimate/run_statistical_tests.py)"]
        S_LEDGER["Experiment Ledger & Ablations<br/>(Legitimate/EXPERIMENT_LEDGER.csv)"]
        S_OOF["6-Learner OOF Benchmark<br/>(FINAL_AUDIT/CURRENT_OOF_RESULTS.json)"]
        S_JSON["Master Numerical Source<br/>(FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json)"]
    end

    subgraph S4 [Level 4: Application System]
        APP_ENG["Inference Engine<br/>(Legitimate/application_sync/backend/inference.py)"]
        APP_UI["Interactive Dashboard<br/>(Legitimate/application_sync/frontend/index.html)"]
        APP_PARITY["Application Parity Test (Error=0.0)<br/>(Legitimate/test_application_parity.py)"]
    end

    subgraph S5 [Level 5: Publication Artifacts]
        PUB_FIGS["Publication Figures 1-7 (300 DPI)<br/>(Legitimate/figures/)"]
        PUB_TABS["Publication Tables I-IX<br/>(Legitimate/tables/)"]
        PUB_MANU["IEEE Double-Column Manuscript<br/>(Legitimate/09_MANUSCRIPT/FINAL_MANUSCRIPT.pdf)"]
    end

    D_TRAIN --> F_EXTRACT
    D_TEST --> F_EXTRACT
    F_SCHEMA --> F_MANIFEST
    F_EXTRACT --> F_MANIFEST
    F_MANIFEST --> M_XGB

    M_XGB --> S_STATS
    D_LABELS --> S_STATS
    S_STATS --> S_JSON
    S_STATS --> S_LEDGER
    D_TRAIN --> S_OOF

    M_XGB --> APP_ENG
    F_MANIFEST --> APP_ENG
    APP_ENG --> APP_UI
    APP_ENG --> APP_PARITY

    S_JSON --> PUB_FIGS
    S_JSON --> PUB_TABS
    PUB_FIGS --> PUB_MANU
    PUB_TABS --> PUB_MANU
```
"""
    out_md = AUDIT_DIR / "CURRENT_DEPENDENCY_GRAPH.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(graph_md)
    print(f"Generated {out_md}")

def generate_result_source_map():
    source_map = [
        {"metric_claim": "Promoted Spearman rho = 0.6722", "evaluation_split": "Temporal Holdout (n=124)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "model_promoted.spearman_rho", "verification_script": "Legitimate/run_statistical_tests.py"},
        {"metric_claim": "Promoted 95% Bootstrap CI = [0.5495, 0.7620]", "evaluation_split": "Temporal Holdout (n=124)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "model_promoted.ci_low, ci_high", "verification_script": "Legitimate/run_statistical_tests.py"},
        {"metric_claim": "Promoted Asymptotic p = 1.25e-17", "evaluation_split": "Temporal Holdout (n=124)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "model_promoted.p_value", "verification_script": "Legitimate/run_statistical_tests.py"},
        {"metric_claim": "Promoted Top/Bottom AUC = 0.9712", "evaluation_split": "Temporal Holdout (n=124, Top20 vs Bot20)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "model_promoted.auc", "verification_script": "Legitimate/run_candidate_experiments.py"},
        {"metric_claim": "Promoted RMSE = 19.75, MAE = 16.66", "evaluation_split": "Temporal Holdout (n=124)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "model_promoted.rmse, mae", "verification_script": "Legitimate/save_promoted_model.py"},
        {"metric_claim": "Controlled Baseline rho = 0.5623", "evaluation_split": "Temporal Holdout (n=124)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "baseline_controlled.spearman_rho", "verification_script": "Legitimate/run_candidate_experiments.py"},
        {"metric_claim": "Controlled Baseline 95% CI = [0.4140, 0.6812]", "evaluation_split": "Temporal Holdout (n=124)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "baseline_controlled.ci_low, ci_high", "verification_script": "Legitimate/run_candidate_experiments.py"},
        {"metric_claim": "Controlled Baseline AUC = 0.8904", "evaluation_split": "Temporal Holdout (n=124)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "baseline_controlled.auc", "verification_script": "Legitimate/run_candidate_experiments.py"},
        {"metric_claim": "Delta rho = +0.1099, 95% CI = [+0.0485, +0.1833]", "evaluation_split": "Temporal Holdout (n=124 paired)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "paired_comparisons_vs_controlled.bootstrap_ci_95", "verification_script": "Legitimate/run_statistical_tests.py"},
        {"metric_claim": "Paired Permutation p = 0.0004", "evaluation_split": "Temporal Holdout (n=124 paired, 10k flips)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "paired_comparisons_vs_controlled.permutation_p_value", "verification_script": "Legitimate/run_statistical_tests.py"},
        {"metric_claim": "Cold-Start Unseen Brands rho = 0.6328 (vs 0.5155)", "evaluation_split": "Temporal Holdout Tier-0 (n=90)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "cold_start_unseen_brands.model_promoted_rho", "verification_script": "Legitimate/run_candidate_experiments.py"},
        {"metric_claim": "Cold-Start Unseen Brands AUC = 0.9815 (vs 0.8843)", "evaluation_split": "Temporal Holdout Tier-0 (n=90)", "source_file": "FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json", "variable_path": "cold_start_unseen_brands.model_promoted_auc", "verification_script": "Legitimate/run_candidate_experiments.py"},
        {"metric_claim": "External Real-World Cohort rho = 0.6120", "evaluation_split": "External Amazon 2022-2024 (n=155)", "source_file": "Legitimate/application_evaluation/EXTERNAL_EVALUATION_REPORT.md", "variable_path": "spearman_rho", "verification_script": "Legitimate/build_application_evaluation.py"},
        {"metric_claim": "External Cohort AUC = 0.8840, MAE = 14.82", "evaluation_split": "External Amazon 2022-2024 (n=155)", "source_file": "Legitimate/application_evaluation/EXTERNAL_EVALUATION_REPORT.md", "variable_path": "auc, mae", "verification_script": "Legitimate/build_application_evaluation.py"},
        {"metric_claim": "5-Fold OOF XGBoost rho = 0.7565, R2 = 0.5715", "evaluation_split": "Training Cross-Validation (n=507 OOF)", "source_file": "FINAL_AUDIT/CURRENT_OOF_RESULTS.json", "variable_path": "XGBoost.pooled_oof_spearman_rho", "verification_script": "scratch/run_clean_six_learner_benchmark.py"}
    ]

    out_csv = AUDIT_DIR / "CURRENT_RESULT_SOURCE_MAP.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric_claim", "evaluation_split", "source_file", "variable_path", "verification_script"])
        writer.writeheader()
        writer.writerows(source_map)
    print(f"Generated {out_csv}")

if __name__ == "__main__":
    generate_file_inventory()
    generate_dependency_graph()
    generate_result_source_map()
