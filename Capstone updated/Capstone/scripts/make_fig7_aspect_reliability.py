"""Regenerate Figure 7 (Aspect Validity / Bridging Reliability) directly from models/bridging_reliability.json.

Ensures exact numerical alignment between:
- Text: utility .53, durability .53, ease .52, build .51, reliability .50, value .34, repairability .27, design .21, after-sales .07
- Visual Figure 7
- Figure caption

Outputs:
- papers/figures/fig3_aspect_validity.png
- papers/figures/fig7_aspect_validity.png
- audit paper/research_paper/figures/fig3_aspect_validity.png
- paper_ieee/figures/fig3_aspect_validity.png
"""

import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RELIABILITY_PATH = ROOT / "models/bridging_reliability.json"

TARGET_PATHS = [
    ROOT / "papers/figures/fig3_aspect_validity.png",
    ROOT / "papers/figures/fig7_aspect_validity.png",
    ROOT / "audit paper/research_paper/figures/fig3_aspect_validity.png",
    ROOT / "paper_ieee/figures/fig3_aspect_validity.png",
]

for p in TARGET_PATHS:
    p.parent.mkdir(parents=True, exist_ok=True)

# Shared house style
INK    = "#1D2733"
MUTED  = "#5B6470"
GREEN  = "#059669"
AMBER  = "#D97706"
GRAYB  = "#94A3B8"
GRID   = "#E2E8F0"

def get_badge(r: float) -> tuple[str, str]:
    if r >= 0.45:
        return "HIGH TRUST (r >= 0.45)", GREEN
    elif r >= 0.25:
        return "MODERATE TRUST (0.25 <= r < 0.45)", AMBER
    else:
        return "UNESTIMABLE / LOW TRUST (r < 0.25)", GRAYB

def main():
    data = json.loads(RELIABILITY_PATH.read_text(encoding="utf-8"))
    meta = data["meta"]
    detail = meta["detail"]
    
    # Sort aspects by correlation r ascending (so highest appears at top of horizontal chart)
    sorted_aspects = sorted(detail.items(), key=lambda kv: kv[1]["r"])
    
    names = []
    r_vals = []
    badges = []
    colors = []
    cis_low = []
    cis_high = []
    
    for asp, info in sorted_aspects:
        r = info["r"]
        n = info["n"]
        # Exact Fisher z-transform 95% CI
        z = np.arctanh(r)
        se = 1.0 / np.sqrt(n - 3)
        ci_lo = float(np.tanh(z - 1.96 * se))
        ci_hi = float(np.tanh(z + 1.96 * se))
        
        pretty_name = asp.replace("_", " ").title()
        if asp == "value_for_money":
            pretty_name = "Value For Money"
        elif asp == "ease_of_use":
            pretty_name = "Ease Of Use"
            
        names.append(pretty_name)
        r_vals.append(r)
        cis_low.append(ci_lo)
        cis_high.append(ci_hi)
        badge_name, color = get_badge(r)
        badges.append(badge_name)
        colors.append(color)

    r_arr = np.array(r_vals)
    y = np.arange(len(names))
    
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=300)
    
    # Draw bars
    bars = ax.barh(y, r_arr, color=colors, height=0.62, edgecolor="black", linewidth=0.6, zorder=3)
    
    # Draw CI error bars
    xerr = [r_arr - np.array(cis_low), np.array(cis_high) - r_arr]
    ax.errorbar(r_arr, y, xerr=xerr, fmt="none", ecolor="#1E293B", elinewidth=1.1, capsize=3.0, zorder=4)
    
    ax.axvline(0, color="#1E293B", linewidth=0.9, zorder=2)
    ax.axvline(0.45, color=GREEN, linestyle="--", linewidth=0.8, alpha=0.7, zorder=2)
    ax.axvline(0.25, color=AMBER, linestyle="--", linewidth=0.8, alpha=0.7, zorder=2)
    
    # Text labels
    for yi, ri in zip(y, r_arr):
        ax.text(ri + 0.02, yi, f"{ri:.2f}", va="center", ha="left", fontsize=8.5, color=INK, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9.5, fontweight="medium")
    ax.set_xlabel("Bridging Validity: Pearson $r$ with Review-Derived Truth (95% CI)", fontsize=9.5, fontweight="bold", color=INK)
    ax.set_title("Which Product Aspects Can Be Estimated from Specifications Alone?", fontsize=11, fontweight="bold", color=INK, pad=12)
    ax.set_xlim(-0.08, 0.72)
    
    ax.grid(axis="x", linestyle="--", alpha=0.6, color=GRID)
    ax.grid(axis="y", visible=False)
    
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=GREEN, ec="black", lw=0.5),
        plt.Rectangle((0, 0), 1, 1, color=AMBER, ec="black", lw=0.5),
        plt.Rectangle((0, 0), 1, 1, color=GRAYB, ec="black", lw=0.5),
    ]
    ax.legend(handles, ["High Trust ($r \\geq 0.45$)", "Moderate Trust ($0.25 \\leq r < 0.45$)", "Low Trust / Flagged ($r < 0.25$)"],
              frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=8.0, loc="lower right",
              title="Runtime Trust Tier (n = 118)", title_fontsize=8.5)

    plt.tight_layout()
    for p in TARGET_PATHS:
        fig.savefig(p, dpi=300, bbox_inches="tight")
        print(f"Saved Figure to {p}")
    plt.close(fig)

if __name__ == "__main__":
    main()
