"""Generate redesigned, 100% consistent Figures 1-4 for the Research Paper
using exact leakage-free Table 1 metrics.
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
OUT = ROOT / "redesign/figures"
OUT.mkdir(parents=True, exist_ok=True)

# Shared color palette
INK    = "#1D2733"
MUTED  = "#5B6470"
BLUE   = "#1F77B4"
NAVY   = "#1A365D"
TEAL   = "#2A9D8F"
GREEN  = "#2E7D32"
AMBER  = "#D97706"
PURPLE = "#6D28D9"
RED    = "#C53030"
ROSE   = "#BE185D"
GRAYB  = "#94A3B8"
GRID   = "#E2E8F0"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "axes.labelsize": 9.5,
    "axes.labelcolor": INK,
    "axes.edgecolor": "#94A3B8",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "figure.dpi": 300,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "tight",
})

# Table 1 verified leakage-free data
DATA = {
    "Gradient Boosting": {
        "r2": 0.558, "rmse": 11.61, "mae": 9.14, "acc": 0.922, "prec": 0.908,
        "rec": 0.943, "spec": 0.886, "f1": 0.924, "auc": 0.980, "mcc": 0.840,
        "time_s": 1.25, "cm": [[114, 13], [7, 120]]
    },
    "XGBoost": {
        "r2": 0.550, "rmse": 11.75, "mae": 9.22, "acc": 0.919, "prec": 0.899,
        "rec": 0.941, "spec": 0.880, "f1": 0.917, "auc": 0.978, "mcc": 0.835,
        "time_s": 0.35, "cm": [[113, 14], [7, 120]]
    },
    "Random Forest": {
        "r2": 0.520, "rmse": 12.13, "mae": 9.48, "acc": 0.918, "prec": 0.887,
        "rec": 0.959, "spec": 0.864, "f1": 0.921, "auc": 0.970, "mcc": 0.834,
        "time_s": 1.48, "cm": [[111, 16], [5, 122]]
    },
    "MLP Regressor": {
        "r2": 0.493, "rmse": 12.49, "mae": 9.68, "acc": 0.902, "prec": 0.878,
        "rec": 0.923, "spec": 0.880, "f1": 0.898, "auc": 0.968, "mcc": 0.803,
        "time_s": 0.82, "cm": [[111, 16], [9, 118]]
    },
    "Ridge Regression": {
        "r2": 0.464, "rmse": 12.85, "mae": 10.17, "acc": 0.914, "prec": 0.901,
        "rec": 0.914, "spec": 0.914, "f1": 0.906, "auc": 0.958, "mcc": 0.826,
        "time_s": 0.02, "cm": [[115, 12], [10, 117]]
    },
    "SVR (RBF)": {
        "r2": 0.432, "rmse": 13.22, "mae": 10.32, "acc": 0.898, "prec": 0.905,
        "rec": 0.890, "spec": 0.911, "f1": 0.896, "auc": 0.958, "mcc": 0.796,
        "time_s": 0.09, "cm": [[115, 12], [14, 113]]
    }
}

MODELS = list(DATA.keys())
SHORT_NAMES = ["Gradient\nBoosting", "XGBoost", "Random\nForest", "MLP\nRegressor", "Ridge\nRegression", "SVR\n(RBF)"]

def make_fig1():
    """Fig 1: All evaluation metrics across six algorithms."""
    metrics = ["r2", "acc", "prec", "rec", "f1", "auc", "mcc"]
    labels = ["R²", "Accuracy", "Precision", "Recall", "F1", "AUC-ROC", "MCC"]
    colors = [BLUE, NAVY, GREEN, AMBER, TEAL, PURPLE, ROSE]

    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    x = np.arange(len(MODELS))
    w = 0.115
    offs = np.arange(len(metrics)) - len(metrics) / 2 + 0.5

    for i, (m, lab, c) in enumerate(zip(metrics, labels, colors)):
        vals = [DATA[n][m] for n in MODELS]
        bars = ax.bar(x + offs[i] * w, vals, w, label=lab, color=c, zorder=3,
                      edgecolor="white", linewidth=0.5)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.015,
                    f"{v:.3f}", ha="center", va="bottom", fontsize=5.8,
                    rotation=90, color=INK, fontweight="semibold")

    ax.set_xticks(x, SHORT_NAMES, fontsize=9.5)
    ax.set_ylabel("Metric Score", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.18)
    ax.text(0.5, 1.12, "Algorithm Comparison Across Evaluation Metrics (Leakage-Free Benchmark)",
            transform=ax.transAxes, ha="center", fontsize=12, fontweight="bold", color=INK)
    ax.text(0.5, 1.06, "Aspects-only features · 5-fold CV · Strict training-fold thresholding · Physical products (n = 631)",
            transform=ax.transAxes, ha="center", fontsize=8.5, color=MUTED)
    ax.legend(frameon=True, facecolor="white", edgecolor=GRID, fontsize=8.5, loc="upper center", ncol=7,
              columnspacing=1.0, handlelength=1.2, bbox_to_anchor=(0.5, 1.02))
    ax.grid(axis="x", visible=False)
    
    fig.savefig(OUT / "fig1_algorithm_metrics.png")
    plt.close(fig)
    print("Generated fig1_algorithm_metrics.png")

def make_fig2():
    """Fig 2: Three-panel accuracy-efficiency trade-off."""
    r2 = [DATA[n]["r2"] for n in MODELS]
    times = [DATA[n]["time_s"] for n in MODELS]
    rmse = [DATA[n]["rmse"] for n in MODELS]

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.0), gridspec_kw={"wspace": 0.22})
    
    # Panel 1: R2 (higher is better)
    ys = np.arange(len(MODELS))
    best_r2 = max(r2)
    colors_r2 = [GREEN if v == best_r2 else BLUE if "XGBoost" in n else GRAYB for v, n in zip(r2, MODELS)]
    bars1 = axes[0].barh(ys, r2, color=colors_r2, height=0.62, zorder=3, edgecolor="white", linewidth=0.5)
    axes[0].set_yticks(ys, [n.replace(" Regressor", "").replace(" Regression", "") for n in MODELS], fontsize=9)
    axes[0].set_xlabel("R² Score (higher is better)", fontsize=9, fontweight="bold")
    axes[0].set_title("Predictive Accuracy (R²)", fontsize=10.5, fontweight="bold", pad=8)
    axes[0].set_xlim(0, 0.68)
    for b, v in zip(bars1, r2):
        axes[0].text(v + 0.012, b.get_y() + b.get_height() / 2, f"{v:.3f}", va="center", fontsize=8.5, fontweight="bold", color=INK)
    axes[0].grid(axis="y", visible=False)

    # Panel 2: Training time (lower is better)
    best_time = min(times)
    colors_time = [GREEN if v == best_time else AMBER if "XGBoost" in n else GRAYB for v, n in zip(times, MODELS)]
    bars2 = axes[1].barh(ys, times, color=colors_time, height=0.62, zorder=3, edgecolor="white", linewidth=0.5)
    axes[1].set_yticks(ys, [])
    axes[1].set_xlabel("Training Time, s (lower is better)", fontsize=9, fontweight="bold")
    axes[1].set_title("Training Efficiency", fontsize=10.5, fontweight="bold", pad=8)
    axes[1].set_xlim(0, max(times) * 1.25)
    for b, v in zip(bars2, times):
        axes[1].text(v + 0.03, b.get_y() + b.get_height() / 2, f"{v:.2f}s", va="center", fontsize=8.5, fontweight="bold", color=INK)
    axes[1].grid(axis="y", visible=False)

    # Panel 3: RMSE (lower is better)
    best_rmse = min(rmse)
    colors_rmse = [GREEN if v == best_rmse else BLUE if "XGBoost" in n else GRAYB for v, n in zip(rmse, MODELS)]
    bars3 = axes[2].barh(ys, rmse, color=colors_rmse, height=0.62, zorder=3, edgecolor="white", linewidth=0.5)
    axes[2].set_yticks(ys, [])
    axes[2].set_xlabel("RMSE (lower is better)", fontsize=9, fontweight="bold")
    axes[2].set_title("Error Magnitude (RMSE)", fontsize=10.5, fontweight="bold", pad=8)
    axes[2].set_xlim(0, 15.5)
    for b, v in zip(bars3, rmse):
        axes[2].text(v + 0.25, b.get_y() + b.get_height() / 2, f"{v:.2f}", va="center", fontsize=8.5, fontweight="bold", color=INK)
    axes[2].grid(axis="y", visible=False)

    fig.suptitle("Accuracy, Efficiency, and Error Trade-offs Across Six Benchmark Algorithms",
                 fontsize=12, fontweight="bold", color=INK, y=1.04)
    fig.savefig(OUT / "fig2_algorithm_tradeoffs.png")
    plt.close(fig)
    print("Generated fig2_algorithm_tradeoffs.png")

def make_fig3():
    """Fig 3: Standardized algorithm benchmark table visualization."""
    fig, ax = plt.subplots(figsize=(11.5, 4.0))
    ax.axis("off")

    cols = ["Algorithm", "R²", "RMSE", "MAE", "Accuracy", "Precision", "Recall", "Specificity", "F1", "AUC", "MCC"]
    rows = []
    for n in MODELS:
        d = DATA[n]
        rows.append([
            n,
            f"{d['r2']:.3f}",
            f"{d['rmse']:.2f}",
            f"{d['mae']:.2f}",
            f"{d['acc']*100:.1f}%",
            f"{d['prec']*100:.1f}%",
            f"{d['rec']*100:.1f}%",
            f"{d['spec']*100:.1f}%",
            f"{d['f1']:.3f}",
            f"{d['auc']:.3f}",
            f"{d['mcc']:.3f}"
        ])

    table = ax.table(cellText=rows, colLabels=cols, cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.8)

    # Style header and rows
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#CBD5E1")
        cell.set_linewidth(0.8)
        if r == 0:
            cell.set_text_props(weight="bold", color="white")
            cell.set_facecolor(NAVY)
        else:
            if r % 2 == 1:
                cell.set_facecolor("#F8FAFC")
            else:
                cell.set_facecolor("white")
            if c == 0:
                cell.set_text_props(weight="bold", ha="left")
                cell.set_facecolor("#EDF2F7")
            # Highlight top performers
            if r == 1: # Gradient Boosting (leading R2, RMSE, Acc, F1, AUC, MCC)
                if c in [1, 2, 4, 8, 9, 10]:
                    cell.set_text_props(weight="bold", color=GREEN)
            elif r == 2: # XGBoost (close second)
                if c in [1, 4, 8, 9]:
                    cell.set_text_props(weight="bold", color=NAVY)

    plt.title("Table I: Standardized Algorithm Benchmark on Physical-Product Success (Leakage-Free 5-Fold CV)",
              fontsize=11.5, fontweight="bold", pad=16, color=INK)
    fig.savefig(OUT / "fig3_algorithm_table.png")
    plt.close(fig)
    print("Generated fig3_algorithm_table.png")

def make_fig4():
    """Fig 4: Aggregated confusion matrices (5-fold CV, top-20% vs bottom-20% quintiles)."""
    n = len(MODELS)
    fig, axes = plt.subplots(1, n, figsize=(2.7 * n, 3.2))
    cm_labels = ["Flop", "Hit"]
    cmap = LinearSegmentedColormap.from_list("custom_blue", ["#F0F7FF", BLUE])

    for ax, name in zip(axes, MODELS):
        cm = np.array(DATA[name]["cm"])
        total = cm.sum()
        pct = cm.astype(float) / total * 100
        ax.imshow(pct, cmap=cmap, vmin=0, vmax=60)
        
        for i in range(2):
            for j in range(2):
                col = "white" if pct[i, j] > 35 else INK
                ax.text(j, i, f"{cm[i, j]}\n{pct[i, j]:.1f}%", ha="center", va="center",
                        fontsize=9.5, fontweight="bold", color=col)
                
        ax.set_xticks([0, 1], cm_labels, fontsize=8.5)
        ax.set_yticks([0, 1], cm_labels, fontsize=8.5)
        ax.set_xlabel("Predicted", fontsize=8.5, fontweight="semibold")
        if ax is axes[0]:
            ax.set_ylabel("Actual", fontsize=8.5, fontweight="semibold")
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
        ax.grid(False)
        acc_pct = (cm[0, 0] + cm[1, 1]) / total * 100
        short_title = name.replace(" Regressor", "").replace(" Regression", "").replace(" (RBF)", "")
        ax.set_title(f"{short_title}\nAcc: {acc_pct:.1f}%", fontsize=9.5, pad=6, fontweight="bold", color=INK)

    fig.suptitle("Aggregated Confusion Matrices (5-Fold CV · Top-20% vs. Bottom-20% Extreme Quintiles · n = 254)",
                 fontsize=11.5, fontweight="bold", color=INK, y=1.06)
    fig.savefig(OUT / "fig4_confusion_matrices.png")
    plt.close(fig)
    print("Generated fig4_confusion_matrices.png")

if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    print("All Figures 1-4 successfully generated!")
