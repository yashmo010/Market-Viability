"""Generate Survey Figure 1: Separating Literature Sentiment Classification from LaunchSight Viability Prediction (Requirement 16).

Creates a publication-quality two-panel figure:
  Panel A: Literature Sentiment Classification Results (Retrospective classification on customer reviews)
  Panel B: LaunchSight Viability Prediction Results (Prospective cold-start ranking from pre-launch specifications)

Outputs:
  - audit paper/survey_paper/figures/fig1_survey_comparison.png
  - paper_ieee/figures/fig1_survey_comparison.png
  - papers/figures/fig1_survey_comparison.png
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

TARGET_PATHS = [
    ROOT / "audit paper/survey_paper/figures/fig1_survey_comparison.png",
    ROOT / "paper_ieee/figures/fig1_survey_comparison.png",
    ROOT / "papers/figures/fig1_survey_comparison.png",
]

for p in TARGET_PATHS:
    p.parent.mkdir(parents=True, exist_ok=True)

# House styling
INK    = "#1D2733"
MUTED  = "#5B6470"
BLUE   = "#2563EB"
TEAL   = "#0D9488"
GREEN  = "#059669"
AMBER  = "#D97706"
PURPLE = "#7C3AED"
GRAYB  = "#94A3B8"
GRID   = "#E2E8F0"

def main():
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=300)
    
    # ── Panel A: Literature Sentiment Classification Results ────────────────────
    ax_a = axes[0]
    lit_models = [
        "Shan et al. [10]\n(ELECTRA)",
        "Shan et al. [10]\n(BiLSTM)",
        "Shan et al. [10]\n(BERT)",
        "Elangovan [15]\n(XGBoost)",
        "Sayyad [13]\n(CatBoost)",
        "Alantari [28]\n(SVM)",
    ]
    acc_vals = [98.09, 96.09, 95.28, 91.60, 89.50, 88.40]
    f1_vals  = [97.11, 95.84, 94.90, 91.20, 89.10, 87.90]
    
    x_a = np.arange(len(lit_models))
    w = 0.35
    
    bars1 = ax_a.bar(x_a - w/2, acc_vals, width=w, label="Accuracy (%)", color=BLUE, edgecolor="black", linewidth=0.6, zorder=3)
    bars2 = ax_a.bar(x_a + w/2, f1_vals, width=w, label="F1-Score (%)", color=TEAL, edgecolor="black", linewidth=0.6, zorder=3)
    
    for b in bars1:
        ax_a.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5, f"{b.get_height():.1f}", ha="center", fontsize=7.2, fontweight="bold", color=INK)
    for b in bars2:
        ax_a.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5, f"{b.get_height():.1f}", ha="center", fontsize=7.2, fontweight="bold", color=INK)

    ax_a.set_xticks(x_a)
    ax_a.set_xticklabels(lit_models, fontsize=8.0)
    ax_a.set_ylabel("Classification Performance (%)", fontsize=9.0, fontweight="bold", color=INK)
    ax_a.set_ylim(80, 103)
    ax_a.set_title("Panel A: Literature Sentiment Classification\n(Task: Retrospective Sentiment on Existing Reviews)", fontsize=9.8, fontweight="bold", color=INK, pad=8)
    ax_a.grid(axis="y", linestyle="--", alpha=0.5, color=GRID)
    ax_a.legend(frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=8.0, loc="lower right")

    # ── Panel B: LaunchSight Prospective Viability Prediction Results ─────────────
    ax_b = axes[1]
    eval_cohorts = [
        "Predefined Frozen\nHoldout (n=59)",
        "Temporal\nHoldout (n=66)",
        "Extended Cohort\n(n=118)",
        "Temporal Extended\n(n=125)",
    ]
    rho_vals = [0.317, 0.545, 0.529, 0.590]
    auc_vals = [0.743, 0.901, 0.903, 0.942]
    
    x_b = np.arange(len(eval_cohorts))
    
    bars3 = ax_b.bar(x_b - w/2, rho_vals, width=w, label="Spearman Rank Correlation (ρ)", color=GREEN, edgecolor="black", linewidth=0.6, zorder=3)
    bars4 = ax_b.bar(x_b + w/2, auc_vals, width=w, label="Quintile Discrimination AUC", color=AMBER, edgecolor="black", linewidth=0.6, zorder=3)
    
    for b in bars3:
        ax_b.text(b.get_x() + b.get_width()/2, b.get_height() + 0.015, f"{b.get_height():.3f}", ha="center", fontsize=7.5, fontweight="bold", color=INK)
    for b in bars4:
        ax_b.text(b.get_x() + b.get_width()/2, b.get_height() + 0.015, f"{b.get_height():.3f}", ha="center", fontsize=7.5, fontweight="bold", color=INK)

    ax_b.axhline(0.5, color="red", linestyle=":", linewidth=1.0, label="Chance AUC (0.50)", zorder=2)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(eval_cohorts, fontsize=8.2)
    ax_b.set_ylabel("Viability Ranking & Discrimination Metric", fontsize=9.0, fontweight="bold", color=INK)
    ax_b.set_ylim(0.0, 1.08)
    ax_b.set_title("Panel B: LaunchSight Viability Prediction\n(Task: Prospective Ranking from Pre-Launch Specs Alone)", fontsize=9.8, fontweight="bold", color=INK, pad=8)
    ax_b.grid(axis="y", linestyle="--", alpha=0.5, color=GRID)
    ax_b.legend(frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=8.0, loc="lower right")

    plt.suptitle("Comparative Methodological Landscape: Retrospective Text Mining vs. Pre-Launch Viability Forecasting", fontsize=11.2, fontweight="bold", y=1.02)
    plt.tight_layout()
    
    for p in TARGET_PATHS:
        fig.savefig(p, dpi=300, bbox_inches="tight")
        print(f"Saved Figure to {p}")
    plt.close(fig)

if __name__ == "__main__":
    main()
