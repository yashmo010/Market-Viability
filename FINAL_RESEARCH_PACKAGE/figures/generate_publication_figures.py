"""Generate All Publication Figures for IEEE Submission.

Outputs 300 DPI publication-grade figures in Legitimate/figures/.
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

LEGIT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Legitimate")
FIG_DIR = LEGIT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

FINAL_RESULTS_JSON = LEGIT_DIR / "08_FINAL_MODEL/FINAL_RESULTS.json"
PRED_CSV = LEGIT_DIR / "08_FINAL_MODEL/test_predictions.csv"
COMPARISON_CSV = LEGIT_DIR / "FINAL_MODEL_COMPARISON.csv"
ABLATION_CSV = LEGIT_DIR / "04_EXPERIMENTS/ABLATION_STUDY.csv"
WITHIN_CAT_CSV = LEGIT_DIR / "04_EXPERIMENTS/WITHIN_CATEGORY_ANALYSIS.csv"

# Style constants
INK = "#1A2530"
MUTED = "#556070"
PRIMARY = "#1F77B4"
SECONDARY = "#2CA02C"
ACCENT = "#FF7F0E"
RED = "#D62728"
GRID_COLOR = "#EAEAEA"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "axes.labelsize": 9.5,
    "axes.labelcolor": INK,
    "axes.edgecolor": "#707A8A",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "axes.grid": True,
    "grid.color": GRID_COLOR,
    "grid.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.dpi": 300,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "tight",
})

# FIGURE 1: Research System Overview
def make_fig1():
    fig, ax = plt.subplots(figsize=(8.5, 3.2), dpi=300)
    ax.axis("off")

    boxes = [
        ("PRE-LAUNCH INPUTS\n- Title & Category\n- Launch Price\n- Brand Name\n- Raw Specifications", 0.02, 0.20, 0.20, 0.60, "#E8F0FE", "#1967D2"),
        ("LLM COLD-START RICH\nEXTRACTION\n- Verifiable Specs\n- 9 Aspect Summaries\n- Grounding Verification\n- Specification Density", 0.26, 0.20, 0.22, 0.60, "#E6F4EA", "#137333"),
        ("STRUCTURED FEATURE\nCOMPOSITION\n- 24 Frozen Features\n- Pre-Cutoff Scalers\n- Category Profiles\n- Monotone Priors", 0.52, 0.20, 0.22, 0.60, "#FEF7E0", "#B06000"),
        ("XGBOOST REGRESSOR\n- 112 Trees, Depth 5\n- Monotone Priors\n\nPREDICTED PROXY\nSuccessScore [0, 100]", 0.78, 0.20, 0.20, 0.60, "#FCE8E6", "#C5221F"),
    ]

    for title, x, y, w, h, bg, border in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, title, ha="center", va="center", fontsize=8.5, color=INK, weight="bold")

    arrows = [(0.22, 0.50, 0.26, 0.50), (0.48, 0.50, 0.52, 0.50), (0.74, 0.50, 0.78, 0.50)]
    for x1, y1, x2, y2 in arrows:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=MUTED, lw=2.0))

    ax.set_title("Figure 1. End-to-End Launch-Blind Product Success Prediction Architecture", pad=12)
    fig.savefig(FIG_DIR / "fig1_pipeline.png")
    plt.close(fig)
    print("Saved fig1_pipeline.png")

# FIGURE 2: Temporal Protocol
def make_fig2():
    fig, ax = plt.subplots(figsize=(8.0, 2.8), dpi=300)
    ax.axis("off")

    rect1 = patches.FancyBboxPatch((0.05, 0.25), 0.40, 0.50, boxstyle="round,pad=0.02",
                                   facecolor="#EBF3FB", edgecolor="#2B7DE9", linewidth=1.5)
    ax.add_patch(rect1)
    ax.text(0.25, 0.50, "PRE-CUTOFF TRAINING POOL\n(n = 507 Products, 43,599 Reviews)\nLaunch <= Oct 31, 2021\nUsed for 5-Fold CV & Scalers",
            ha="center", va="center", fontsize=8.5, color=INK, weight="bold")

    rect2 = patches.FancyBboxPatch((0.55, 0.25), 0.40, 0.50, boxstyle="round,pad=0.02",
                                   facecolor="#FDE8E8", edgecolor="#E02424", linewidth=1.5)
    ax.add_patch(rect2)
    ax.text(0.75, 0.50, "LAUNCH-BLIND TEMPORAL TEST\n(n = 124 Products, Launch > Oct 31, 2021)\nInputs: Pre-Launch Specs Only\nLabels: Isolated in ground_truth.json",
            ha="center", va="center", fontsize=8.5, color=INK, weight="bold")

    # Divider
    ax.axvline(0.50, 0.15, 0.85, color="#D9381E", linestyle="--", linewidth=2.5)
    ax.text(0.50, 0.90, "TEMPORAL CUTOFF\n2021-10-31 23:59:59 UTC", ha="center", va="center",
            fontsize=8.5, color="#D9381E", weight="bold")

    ax.set_title("Figure 2. Strict Forward-in-Time Temporal Holdout Evaluation Protocol", pad=12)
    fig.savefig(FIG_DIR / "fig2_temporal_protocol.png")
    plt.close(fig)
    print("Saved fig2_temporal_protocol.png")

# FIGURE 3: Performance Comparison vs Baselines
def make_fig3():
    df_comp = pd.read_csv(COMPARISON_CSV)
    models_to_plot = [
        ("Model_New (Promoted Cold-Start Rich)", PRIMARY, "Proposed Model_New"),
        ("Model_O (Original Canonical Baseline)", "#7F7F7F", "Model_O (Baseline)"),
        ("Baseline H2: Gradient Boosting", "#AEC7E8", "GBDT (Aspects)"),
        ("Baseline H1: Random Forest", "#C7C7C7", "Random Forest"),
        ("Baseline I1: Spec TF-IDF + Ridge", "#FFBB78", "TF-IDF + Ridge"),
        ("Baseline F: Category + Brand", "#98DF8A", "Category + Brand"),
        ("Baseline C: Category Mean", "#BCBD22", "Category Mean"),
    ]

    names, rhos, aucs, colors = [], [], [], []
    for m_key, col, label in models_to_plot:
        match = df_comp[df_comp["Model"] == m_key]
        if not match.empty:
            names.append(label)
            rhos.append(float(match["Spearman_rho"].values[0]))
            aucs.append(float(match["AUC"].values[0]))
            colors.append(col)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.8), dpi=300)

    y_pos = np.arange(len(names))
    ax1.barh(y_pos, rhos, color=colors, height=0.6, edgecolor="#444", linewidth=0.6)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(names, fontsize=8.5)
    ax1.invert_yaxis()
    ax1.set_xlabel("Spearman Rank Correlation (rho)", fontsize=9)
    ax1.set_xlim(0.40, 0.75)
    ax1.set_title("A. Primary Temporal Correlation (n=124)", fontsize=9.5)
    for i, v in enumerate(rhos):
        ax1.text(v + 0.008, i, f"{v:.3f}", va="center", fontsize=8, weight="bold")

    ax2.barh(y_pos, aucs, color=colors, height=0.6, edgecolor="#444", linewidth=0.6)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])
    ax2.invert_yaxis()
    ax2.set_xlabel("Top vs Bottom Quintile AUC", fontsize=9)
    ax2.set_xlim(0.80, 1.02)
    ax2.set_title("B. Market Quintile Discrimination", fontsize=9.5)
    for i, v in enumerate(aucs):
        ax2.text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=8, weight="bold")

    fig.suptitle("Figure 3. Proposed Cold-Start Model vs. Canonical Baselines on Temporal Holdout", fontsize=11, weight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_performance_comparison.png")
    plt.close(fig)
    print("Saved fig3_performance_comparison.png")

# FIGURE 4: Cold-Start / Unseen Brand Analysis
def make_fig4():
    fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=300)

    categories = ["Proposed Model_New\n(Cold-Start Rich)", "Model_O\n(Original Baseline)", "Category Mean\nBaseline", "TF-IDF + Ridge\n(Text Control)"]
    unseen_rhos = [0.633, 0.516, 0.686, 0.623]
    colors = [PRIMARY, "#7F7F7F", "#BCBD22", "#FFBB78"]

    bars = ax.bar(categories, unseen_rhos, color=colors, width=0.55, edgecolor="#333", linewidth=0.7)
    ax.set_ylabel("Spearman rho on Unseen Brands (n=82)")
    ax.set_ylim(0.40, 0.75)
    ax.set_title("Figure 4. Predictive Performance on Unseen Brands (Cold-Start Tier 0)", fontsize=10.5)

    for bar, val in zip(bars, unseen_rhos):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.01, f"{val:.3f}", ha="center", fontsize=8.5, weight="bold")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig4_cold_start.png")
    plt.close(fig)
    print("Saved fig4_cold_start.png")

# FIGURE 5: Within-Category Performance
def make_fig5():
    df_cat = pd.read_csv(WITHIN_CAT_CSV)
    cats = [c.replace("_", " ").title() for c in df_cat["category"]]
    orig_rhos = df_cat["orig_rho"]
    new_rhos = df_cat["new_rho"]

    x = np.arange(len(cats))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7.5, 3.6), dpi=300)
    b1 = ax.bar(x - width/2, orig_rhos, width, label="Model_O (Baseline)", color="#8C96A0", edgecolor="#444")
    b2 = ax.bar(x + width/2, new_rhos, width, label="Model_New (Cold-Start Rich)", color=PRIMARY, edgecolor="#444")

    ax.set_ylabel("Spearman Rank Correlation (rho)")
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=8.5)
    ax.set_ylim(-0.15, 0.65)
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.legend(frameon=True, fontsize=8.5, loc="upper right")
    ax.set_title("Figure 5. Head-to-Head Within-Category Ranking Performance", fontsize=10.5)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig5_within_category.png")
    plt.close(fig)
    print("Saved fig5_within_category.png")

# FIGURE 6: Ablation Analysis
def make_fig6():
    df_ab = pd.read_csv(ABLATION_CSV)
    configs = [
        "A0: Baseline Model_O",
        "A1: No Mentions",
        "A2: + Tech Attrs",
        "A3: Model_New (+ Spec Density)",
        "A4: + Tech + Density",
        "A5: Without Brand",
        "A6: Without Category",
        "A7: Without Price",
    ]
    rhos = df_ab["spearman_rho"]

    fig, ax = plt.subplots(figsize=(7.5, 3.6), dpi=300)
    colors = [PRIMARY if "Model_New" in c else "#5C8BB5" if c.startswith("A") and int(c[1]) < 5 else "#A0AAB2" for c in configs]
    bars = ax.barh(np.arange(len(configs)), rhos, color=colors, height=0.6, edgecolor="#333", linewidth=0.6)
    ax.set_yticks(np.arange(len(configs)))
    ax.set_yticklabels(configs, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("Temporal Spearman Rank Correlation (rho)")
    ax.set_xlim(0.50, 0.72)
    ax.set_title("Figure 6. Controlled Feature Ablation Study (A0 - A7)", fontsize=10.5)

    for bar, val in zip(bars, rhos):
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2, f"{val:.3f}", va="center", fontsize=8, weight="bold")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig6_ablation.png")
    plt.close(fig)
    print("Saved fig6_ablation.png")

# FIGURE 7: Predicted vs Observed Scatter
def make_fig7():
    df_pred = pd.read_csv(PRED_CSV)
    p = df_pred["predicted_new"]
    y = df_pred["actual"]

    fig, ax = plt.subplots(figsize=(5.5, 4.2), dpi=300)
    scatter = ax.scatter(p, y, alpha=0.75, c=PRIMARY, edgecolors="#111", s=35, linewidth=0.5)

    # 45-degree reference line
    ax.plot([10, 90], [10, 90], color="#C5221F", linestyle="--", linewidth=1.5, label="Ideal Parity (1:1)")

    ax.set_xlabel("Model_New Predicted Viability [0, 100]")
    ax.set_ylabel("Actual Market Success Proxy [0, 100]")
    ax.set_xlim(15, 85)
    ax.set_ylim(5, 95)
    ax.set_title("Figure 7. Predicted Viability vs. Review-Derived Outcome (n=124)", fontsize=10.5)

    ax.text(0.05, 0.90, f"Spearman rho = 0.672 (p < 1e-16)\nPearson r = 0.700\nRMSE = 19.75, MAE = 16.66",
            transform=ax.transAxes, fontsize=8, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#F8F9FA", edgecolor="#D0D5DD"))
    ax.legend(loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig7_scatter.png")
    plt.close(fig)
    print("Saved fig7_scatter.png")

def main():
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    make_fig6()
    make_fig7()
    print("All publication figures generated successfully in Legitimate/figures/.")

if __name__ == "__main__":
    main()
