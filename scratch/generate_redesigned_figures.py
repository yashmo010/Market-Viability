"""Generate Publication-Quality Redesigned Figure 1 and Figure 2 for IEEE / Scopus Publication.

Refined Layout with Perfect Proportions, Zero Text Collisions, and No Dates.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

BG_COLOR = "#FFFFFF"
TEXT_MAIN = "#0F172A"
TEXT_MUTED = "#334155"
TEXT_LIGHT = "#64748B"

# Stage Color Palettes (Refined IEEE Transactions Style)
STAGE1_ACCENT = "#1D4ED8"       # Deep Blue
STAGE1_BG = "#F0F6FF"
STAGE1_BORDER = "#93C5FD"

STAGE2_ACCENT = "#0F766E"       # Deep Teal
STAGE2_BG = "#F0FDFA"
STAGE2_BORDER = "#99F6E4"

STAGE3_ACCENT = "#B45309"       # Deep Amber
STAGE3_BG = "#FFFBEB"
STAGE3_BORDER = "#FDE68A"

STAGE4_ACCENT = "#BE123C"       # Deep Crimson
STAGE4_BG = "#FFF1F2"
STAGE4_BORDER = "#FECDD3"

STAGE5_ACCENT = "#047857"       # Deep Emerald
STAGE5_BG = "#ECFDF5"
STAGE5_BORDER = "#A7F3D0"

QUARANTINE_ACCENT = "#991B1B"   # Wine Red
QUARANTINE_BG = "#FEF2F2"
QUARANTINE_BORDER = "#F87171"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": BG_COLOR,
    "savefig.facecolor": BG_COLOR,
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
})

def draw_card(ax, x, y, w, h, bg_color, border_color, lw=1.5, corner_rad=1.0):
    card = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={corner_rad}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=lw,
        zorder=2
    )
    ax.add_patch(card)
    return card

def generate_figure_1(save_path):
    fig, ax = plt.subplots(figsize=(15.5, 6.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")

    # Master Title
    ax.text(50, 48.2, "End-to-End Launch-Blind Product Viability Estimation Architecture",
            ha="center", va="center", fontsize=15.5, fontweight="bold", color=TEXT_MAIN)
    ax.text(50, 45.8, "Strict Pre-Launch Feature Extraction Pipeline via LLM Aspect Bridging to Monotonic Gradient Boosted Regressor",
            ha="center", va="center", fontsize=9.8, color=TEXT_MUTED)

    # Top Rule
    ax.plot([2, 98], [44.5, 44.5], color="#E2E8F0", lw=1.2, zorder=1)

    # -------------------------------------------------------------
    # STAGE 1: Pre-Launch Inputs (x: 2 to 18, w: 16)
    # -------------------------------------------------------------
    s1_x, s1_w = 2.0, 16.5
    s1_y, s1_h = 4.0, 37.5
    draw_card(ax, s1_x, s1_y, s1_w, s1_h, STAGE1_BG, STAGE1_BORDER, lw=1.6)

    # Stage Badge
    ax.add_patch(FancyBboxPatch((s1_x + 1.2, s1_y + s1_h - 4.2), s1_w - 2.4, 3.0,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor=STAGE1_ACCENT, edgecolor="none", zorder=4))
    ax.text(s1_x + s1_w/2, s1_y + s1_h - 2.7, "STAGE 1: INPUTS",
            ha="center", va="center", fontsize=8.8, fontweight="bold", color="#FFFFFF", zorder=5)
    ax.text(s1_x + s1_w/2, s1_y + s1_h - 5.8, "Pre-Launch Information Boundary",
            ha="center", va="center", fontsize=7.2, fontweight="bold", color=STAGE1_ACCENT, zorder=5)

    # Inner Box 1: Specs
    draw_card(ax, s1_x + 0.8, s1_y + 20.0, s1_w - 1.6, 10.5, "#FFFFFF", STAGE1_BORDER, lw=1.0)
    ax.text(s1_x + 1.6, s1_y + 28.8, "Technical Specifications", fontsize=7.8, fontweight="bold", color=TEXT_MAIN, zorder=4)
    spec_txt = (
        "• Unstructured catalog text\n"
        "• Feature claims & capabilities\n"
        "• Hardware measurements\n"
        "• Component specifications"
    )
    ax.text(s1_x + 1.6, s1_y + 27.2, spec_txt, fontsize=6.9, color=TEXT_MUTED, va="top", linespacing=1.35, zorder=4)

    # Inner Box 2: Context Metadata
    draw_card(ax, s1_x + 0.8, s1_y + 1.2, s1_w - 1.6, 17.6, "#FFFFFF", STAGE1_BORDER, lw=1.0)
    ax.text(s1_x + 1.6, s1_y + 17.3, "Launch Context Metadata", fontsize=7.8, fontweight="bold", color=TEXT_MAIN, zorder=4)
    
    meta_txt = (
        "1. Launch Price ($)\n"
        "   Log-normalized MSRP\n\n"
        "2. Category Taxonomy (5)\n"
        "   • Bluetooth Speakers\n"
        "   • Ice Makers\n"
        "   • Power Banks\n"
        "   • Smartwatches\n"
        "   • Wireless Headphones\n\n"
        "3. Brand Historical Tier\n"
        "   Tier 0 (Unseen), 1, or 2"
    )
    ax.text(s1_x + 1.6, s1_y + 15.8, meta_txt, fontsize=6.8, color=TEXT_MUTED, va="top", linespacing=1.2, zorder=4)

    # -------------------------------------------------------------
    # STAGE 2: LLM Aspect Bridging (x: 21.5 to 41.5, w: 20)
    # -------------------------------------------------------------
    s2_x, s2_w = 21.2, 19.8
    s2_y, s2_h = 4.0, 37.5
    draw_card(ax, s2_x, s2_y, s2_w, s2_h, STAGE2_BG, STAGE2_BORDER, lw=1.6)

    # Stage 2 Header Badge
    ax.add_patch(FancyBboxPatch((s2_x + 1.0, s2_y + s2_h - 4.2), s2_w - 2.0, 3.0,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor=STAGE2_ACCENT, edgecolor="none", zorder=4))
    ax.text(s2_x + s2_w/2, s2_y + s2_h - 2.7, "STAGE 2: LLM ASPECT BRIDGE",
            ha="center", va="center", fontsize=8.2, fontweight="bold", color="#FFFFFF", zorder=5)
    ax.text(s2_x + s2_w/2, s2_y + s2_h - 5.8, "Evidence Grounding & Enrichment",
            ha="center", va="center", fontsize=7.2, fontweight="bold", color=STAGE2_ACCENT, zorder=5)

    # Sub-card 2.1: 9 Aspects
    draw_card(ax, s2_x + 0.8, s2_y + 16.0, s2_w - 1.6, 14.5, "#FFFFFF", STAGE2_BORDER, lw=1.0)
    ax.text(s2_x + 1.6, s2_y + 29.0, "A. 9-Aspect Quality Extraction", fontsize=7.8, fontweight="bold", color=TEXT_MAIN, zorder=4)
    ax.text(s2_x + 1.6, s2_y + 27.5, "Null-Forcing Evidence Grounding [0, 10]", fontsize=6.8, color=STAGE2_ACCENT, fontweight="bold", zorder=4)
    
    aspects_col1 = "1. Value for Money\n2. Utility\n3. Ease of Use\n4. Reliability\n5. Design Appeal"
    aspects_col2 = "6. After-Sales\n7. Build Quality\n8. Durability\n9. Repairability\n✓ 0.0% Hallucination"
    ax.text(s2_x + 1.6, s2_y + 25.8, aspects_col1, fontsize=6.8, color=TEXT_MUTED, va="top", linespacing=1.28, zorder=4)
    ax.text(s2_x + 10.8, s2_y + 25.8, aspects_col2, fontsize=6.8, color=TEXT_MUTED, va="top", linespacing=1.28, zorder=4)

    # Sub-card 2.2: Density
    draw_card(ax, s2_x + 0.8, s2_y + 1.2, s2_w - 1.6, 13.6, "#FFFFFF", STAGE2_BORDER, lw=1.0)
    ax.text(s2_x + 1.6, s2_y + 13.4, "B. Technical Density Metrics", fontsize=7.8, fontweight="bold", color=TEXT_MAIN, zorder=4)
    ax.text(s2_x + 1.6, s2_y + 12.0, "Item-Side Specification Rigor", fontsize=6.8, color=STAGE2_ACCENT, fontweight="bold", zorder=4)
    density_txt = (
        "• attr_spec_bullets:\n"
        "  Count of technical feature items\n\n"
        "• attr_word_count:\n"
        "  Length of specification description\n\n"
        "• attr_number_density:\n"
        "  Ratio of numeric parameters to words"
    )
    ax.text(s2_x + 1.6, s2_y + 10.6, density_txt, fontsize=6.6, color=TEXT_MUTED, va="top", linespacing=1.18, zorder=4)

    # -------------------------------------------------------------
    # STAGE 3: Structured Feature Vector (x: 43.5 to 61.0, w: 17.5)
    # -------------------------------------------------------------
    s3_x, s3_w = 43.5, 17.5
    s3_y, s3_h = 4.0, 37.5
    draw_card(ax, s3_x, s3_y, s3_w, s3_h, STAGE3_BG, STAGE3_BORDER, lw=1.6)

    ax.add_patch(FancyBboxPatch((s3_x + 1.2, s3_y + s3_h - 4.2), s3_w - 2.4, 3.0,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor=STAGE3_ACCENT, edgecolor="none", zorder=4))
    ax.text(s3_x + s3_w/2, s3_y + s3_h - 2.7, "STAGE 3: 24-D VECTOR",
            ha="center", va="center", fontsize=8.8, fontweight="bold", color="#FFFFFF", zorder=5)
    ax.text(s3_x + s3_w/2, s3_y + s3_h - 5.8, "Structured Cold-Start Features",
            ha="center", va="center", fontsize=7.2, fontweight="bold", color=STAGE3_ACCENT, zorder=5)

    draw_card(ax, s3_x + 0.8, s3_y + 1.2, s3_w - 1.6, 29.3, "#FFFFFF", STAGE3_BORDER, lw=1.0)
    ax.text(s3_x + 1.6, s3_y + 29.0, "Feature Manifest (p = 24)", fontsize=7.8, fontweight="bold", color=TEXT_MAIN, zorder=4)

    features_txt = (
        "1. LLM Aspect Priors (9)\n"
        "   Scalar quality scores [0, 10]\n\n"
        "2. Aspect Mention Rates (9)\n"
        "   Category evidence frequency\n\n"
        "3. Technical Density (3)\n"
        "   Bullets, word count, numbers\n\n"
        "4. Launch Metadata (3)\n"
        "   • Log-scaled launch price ($)\n"
        "   • Historical brand tier [0, 1, 2]\n"
        "   • One-hot category identity\n\n"
        "Normalization & Scaling:\n"
        "• Bounds fitted strictly on pre-cutoff\n"
        "  training pool (n = 507 products)\n"
        "• Test pool evaluated zero-shot"
    )
    ax.text(s3_x + 1.6, s3_y + 27.2, features_txt, fontsize=6.8, color=TEXT_MUTED, va="top", linespacing=1.22, zorder=4)

    # -------------------------------------------------------------
    # STAGE 4: Regressor Ensemble (x: 63.5 to 79.0, w: 15.5)
    # -------------------------------------------------------------
    s4_x, s4_w = 63.5, 15.5
    s4_y, s4_h = 4.0, 37.5
    draw_card(ax, s4_x, s4_y, s4_w, s4_h, STAGE4_BG, STAGE4_BORDER, lw=1.6)

    ax.add_patch(FancyBboxPatch((s4_x + 1.2, s4_y + s4_h - 4.2), s4_w - 2.4, 3.0,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor=STAGE4_ACCENT, edgecolor="none", zorder=4))
    ax.text(s4_x + s4_w/2, s4_y + s4_h - 2.7, "STAGE 4: XGBOOST",
            ha="center", va="center", fontsize=8.8, fontweight="bold", color="#FFFFFF", zorder=5)
    ax.text(s4_x + s4_w/2, s4_y + s4_h - 5.8, "Monotonic Tree Regressor",
            ha="center", va="center", fontsize=7.2, fontweight="bold", color=STAGE4_ACCENT, zorder=5)

    draw_card(ax, s4_x + 0.8, s4_y + 1.2, s4_w - 1.6, 29.3, "#FFFFFF", STAGE4_BORDER, lw=1.0)
    ax.text(s4_x + 1.6, s4_y + 29.0, "Model Architecture", fontsize=7.8, fontweight="bold", color=TEXT_MAIN, zorder=4)

    s4_txt = (
        "Hyperparameter Setup:\n"
        "• tree_method: hist\n"
        "• n_estimators: 100\n"
        "• max_depth: 5\n"
        "• learning_rate: 0.05\n"
        "• subsample: 0.8\n"
        "• colsample_bytree: 0.8\n\n"
        "Directional Inductive Priors:\n"
        "• Price monotone: -1\n"
        "• Brand tier: +1\n"
        "• Quality aspects: +1\n\n"
        "Prevents pathological\n"
        "overfitting under sparse\n"
        "cold-start regimes."
    )
    ax.text(s4_x + 1.6, s4_y + 27.2, s4_txt, fontsize=6.8, color=TEXT_MUTED, va="top", linespacing=1.22, zorder=4)

    # -------------------------------------------------------------
    # TEMPORAL QUARANTINE DIVIDER (x: 80.8)
    # -------------------------------------------------------------
    ax.plot([80.8, 80.8], [2.5, 41.7], color=QUARANTINE_ACCENT, linestyle="--", lw=2.2, zorder=10)
    
    # Boundary Marker Tag (Cleanly positioned in the clear band between cards and top rule)
    ax.add_patch(FancyBboxPatch((74.0, 41.8), 13.6, 2.0,
                               boxstyle="round,pad=0,rounding_size=0.6",
                               facecolor=QUARANTINE_ACCENT, edgecolor="none", zorder=11))
    ax.text(80.8, 42.8, "LABEL QUARANTINE BARRIER", ha="center", va="center",
            fontsize=6.5, fontweight="bold", color="#FFFFFF", zorder=12)

    # -------------------------------------------------------------
    # STAGE 5: Inference & Quarantined Validation (x: 82.5 to 98.0, w: 15.5)
    # -------------------------------------------------------------
    s5_x, s5_w = 82.5, 15.5
    s5_y, s5_h = 4.0, 37.5
    draw_card(ax, s5_x, s5_y, s5_w, s5_h, STAGE5_BG, STAGE5_BORDER, lw=1.6)

    ax.add_patch(FancyBboxPatch((s5_x + 1.2, s5_y + s5_h - 4.2), s5_w - 2.4, 3.0,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor=STAGE5_ACCENT, edgecolor="none", zorder=4))
    ax.text(s5_x + s5_w/2, s5_y + s5_h - 2.7, "STAGE 5: INFERENCE",
            ha="center", va="center", fontsize=8.8, fontweight="bold", color="#FFFFFF", zorder=5)
    ax.text(s5_x + s5_w/2, s5_y + s5_h - 5.8, "Launch-Blind Viability Score",
            ha="center", va="center", fontsize=7.2, fontweight="bold", color=STAGE5_ACCENT, zorder=5)

    # Output Card
    draw_card(ax, s5_x + 0.8, s5_y + 15.0, s5_w - 1.6, 15.5, "#FFFFFF", STAGE5_BORDER, lw=1.0)
    ax.text(s5_x + 1.6, s5_y + 28.8, "Viability Output", fontsize=7.8, fontweight="bold", color=TEXT_MAIN, zorder=4)
    ax.text(s5_x + s5_w/2, s5_y + 26.2, "SuccessScore ∈ [0, 100]", fontsize=7.6, fontweight="bold", color=STAGE5_ACCENT, ha="center", zorder=4)
    out_txt = (
        "• Review-derived market proxy\n"
        "• High rank consistency\n"
        "  (Spearman rho = 0.672)\n"
        "• Top/Bottom quintile AUC = 0.971\n"
        "• Evaluates viability conditional\n"
        "  on achieving market visibility"
    )
    ax.text(s5_x + 1.6, s5_y + 24.2, out_txt, fontsize=6.6, color=TEXT_MUTED, va="top", linespacing=1.2, zorder=4)

    # Quarantined Box (Below)
    draw_card(ax, s5_x + 0.8, s5_y + 1.2, s5_w - 1.6, 12.6, QUARANTINE_BG, QUARANTINE_BORDER, lw=1.0)
    ax.text(s5_x + 1.6, s5_y + 12.4, "Offline Ground Truth", fontsize=7.5, fontweight="bold", color=QUARANTINE_ACCENT, zorder=4)
    quar_txt = (
        "• Post-launch customer reviews\n"
        "• Star ratings & volume velocity\n"
        "• Completely isolated from model\n"
        "• Used exclusively for offline\n"
        "  benchmark evaluation"
    )
    ax.text(s5_x + 1.6, s5_y + 10.8, quar_txt, fontsize=6.5, color=TEXT_MUTED, va="top", linespacing=1.18, zorder=4)

    # Connecting Flow Arrows
    def draw_stage_arrow(x_start, x_end, y_pos):
        ax.annotate("", xy=(x_end, y_pos), xytext=(x_start, y_pos),
                    arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.7",
                                    color="#64748B", lw=2.0))

    draw_stage_arrow(s1_x + s1_w, s2_x, 22.0)
    draw_stage_arrow(s2_x + s2_w, s3_x, 22.0)
    draw_stage_arrow(s3_x + s3_w, s4_x, 22.0)
    draw_stage_arrow(s4_x + s4_w, s5_x, 22.0)

    fig.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"Generated clean Figure 1 to {save_path}")

def generate_figure_2(save_path):
    fig, ax = plt.subplots(figsize=(13.5, 5.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")

    # Master Title
    ax.text(50, 47.8, "Forward-in-Time Temporal Holdout & Quarantine Protocol",
            ha="center", va="center", fontsize=15.0, fontweight="bold", color=TEXT_MAIN)
    ax.text(50, 45.2, "Rigorous Temporal Partitioning and Information Quarantine Ensuring Strictly Launch-Blind Evaluation",
            ha="center", va="center", fontsize=9.6, color=TEXT_MUTED)

    # Horizontal Timeline Bar
    ax.plot([4, 96], [40.5, 40.5], color="#CBD5E1", lw=3.0, zorder=1)
    ax.annotate("", xy=(97, 40.5), xytext=(95, 40.5),
                arrowprops=dict(arrowstyle="->,head_width=0.5,head_length=0.8", color="#64748B", lw=3.0))

    ax.text(6, 42.2, "Pre-Launch Era (Historical Data Available)", fontsize=8.2, fontweight="bold", color=TEXT_MUTED)
    ax.text(94, 42.2, "Post-Launch Horizon (Future Generalization)", fontsize=8.2, fontweight="bold", color=TEXT_MUTED, ha="right")

    # -------------------------------------------------------------
    # LEFT CARD: Pre-Cutoff Training Pool (x: 4 to 44.5, w: 40.5)
    # -------------------------------------------------------------
    c1_x, c1_w = 4.0, 40.5
    c1_y, c1_h = 3.5, 33.5
    draw_card(ax, c1_x, c1_y, c1_w, c1_h, STAGE1_BG, STAGE1_BORDER, lw=1.8)

    # Header Badge
    ax.add_patch(FancyBboxPatch((c1_x + 2.0, c1_y + c1_h - 4.2), c1_w - 4.0, 3.2,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor=STAGE1_ACCENT, edgecolor="none", zorder=4))
    ax.text(c1_x + c1_w/2, c1_y + c1_h - 2.6, "PRE-CUTOFF TRAINING & TUNING POOL",
            ha="center", va="center", fontsize=9.2, fontweight="bold", color="#FFFFFF", zorder=5)

    # Inner Card
    draw_card(ax, c1_x + 1.2, c1_y + 1.2, c1_w - 2.4, 26.5, "#FFFFFF", STAGE1_BORDER, lw=1.0)

    ax.text(c1_x + 2.6, c1_y + 25.4, "Cohort Specification (n = 507 Products):", fontsize=8.5, fontweight="bold", color=TEXT_MAIN, zorder=4)
    ax.text(c1_x + 2.6, c1_y + 23.6, "• 43,599 historical customer reviews across 5 canonical categories", fontsize=7.6, color=TEXT_MUTED, zorder=4)
    
    cat_breakdown = (
        "  Bluetooth Speakers: 128 products | Ice Makers: 109 products\n"
        "  Power Banks: 80 products | Smartwatches: 75 products\n"
        "  Wireless Headphones: 115 products"
    )
    ax.text(c1_x + 2.6, c1_y + 21.8, cat_breakdown, fontsize=7.1, color=TEXT_LIGHT, va="top", linespacing=1.28, zorder=4)

    ax.plot([c1_x + 2.6, c1_x + c1_w - 2.6], [c1_y + 16.5, c1_y + 16.5], color="#E2E8F0", lw=0.9, zorder=4)

    ax.text(c1_x + 2.6, c1_y + 14.8, "Permitted Operations in Training Pool:", fontsize=8.2, fontweight="bold", color=TEXT_MAIN, zorder=4)
    perm_txt = (
        "✓ 5-Fold Stratified Group Cross-Validation (Seed = 42)\n"
        "✓ Preprocessing scalers (Min/Max, Log-price) fitted strictly on n = 507\n"
        "✓ LLM extraction prompt calibration & null-forcing schema audit\n"
        "✓ XGBoost hyperparameter tuning & directional monotone constraints\n"
        "✓ Historical review metrics used solely for training supervision"
    )
    ax.text(c1_x + 2.6, c1_y + 13.2, perm_txt, fontsize=7.2, color="#059669", va="top", linespacing=1.35, zorder=4)

    # -------------------------------------------------------------
    # CENTER DIVIDER CHANNEL (x: 45.0 to 55.0)
    # -------------------------------------------------------------
    ax.plot([50.0, 50.0], [2.0, 35.5], color=QUARANTINE_ACCENT, linestyle="--", lw=2.4, zorder=10)

    # Top Tag (positioned between timeline and cards)
    ax.add_patch(FancyBboxPatch((42.5, 36.5), 15.0, 3.0,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor=QUARANTINE_ACCENT, edgecolor="none", zorder=11))
    ax.text(50.0, 38.0, "TEMPORAL PARTITION", ha="center", va="center",
            fontsize=7.6, fontweight="bold", color="#FFFFFF", zorder=12)

    # Middle Flow Barrier
    ax.add_patch(FancyBboxPatch((44.5, 18.0), 11.0, 4.0,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor="#FFFFFF", edgecolor=QUARANTINE_ACCENT, lw=1.6, zorder=11))
    ax.text(50.0, 20.4, "STRICT FORWARD FLOW", ha="center", va="center",
            fontsize=6.8, fontweight="bold", color=QUARANTINE_ACCENT, zorder=12)
    ax.text(50.0, 19.0, "Zero Label Leakage", ha="center", va="center",
            fontsize=6.2, color=TEXT_MUTED, zorder=12)

    # -------------------------------------------------------------
    # RIGHT CARD: Launch-Blind Temporal Test Pool (x: 55.5 to 96, w: 40.5)
    # -------------------------------------------------------------
    c2_x, c2_w = 55.5, 40.5
    c2_y, c2_h = 3.5, 33.5
    draw_card(ax, c2_x, c2_y, c2_w, c2_h, QUARANTINE_BG, QUARANTINE_BORDER, lw=1.8)

    # Header Badge
    ax.add_patch(FancyBboxPatch((c2_x + 2.0, c2_y + c2_h - 4.2), c2_w - 4.0, 3.2,
                               boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor=QUARANTINE_ACCENT, edgecolor="none", zorder=4))
    ax.text(c2_x + c2_w/2, c2_y + c2_h - 2.6, "LAUNCH-BLIND TEMPORAL TEST POOL",
            ha="center", va="center", fontsize=9.2, fontweight="bold", color="#FFFFFF", zorder=5)

    # Inner Card
    draw_card(ax, c2_x + 1.2, c2_y + 1.2, c2_w - 2.4, 26.5, "#FFFFFF", QUARANTINE_BORDER, lw=1.0)

    ax.text(c2_x + 2.6, c2_y + 25.4, "Cohort Specification (n = 124 Products):", fontsize=8.5, fontweight="bold", color=TEXT_MAIN, zorder=4)
    ax.text(c2_x + 2.6, c2_y + 23.6, "• Strictly post-cutoff physical launches across 5 categories", fontsize=7.6, color=TEXT_MUTED, zorder=4)

    cat_breakdown_test = (
        "  Bluetooth Speakers: 7 products | Ice Makers: 36 products\n"
        "  Power Banks: 19 products | Smartwatches: 39 products\n"
        "  Wireless Headphones: 23 products\n"
        "  Includes n = 82 genuine unseen brands (Tier 0 cold-start)"
    )
    ax.text(c2_x + 2.6, c2_y + 21.8, cat_breakdown_test, fontsize=7.1, color=TEXT_LIGHT, va="top", linespacing=1.28, zorder=4)

    ax.plot([c2_x + 2.6, c2_x + c2_w - 2.6], [c2_y + 15.0, c2_y + 15.0], color="#E2E8F0", lw=0.9, zorder=4)

    ax.text(c2_x + 2.6, c2_y + 13.4, "Quarantine & Evaluation Protocol:", fontsize=8.2, fontweight="bold", color=TEXT_MAIN, zorder=4)
    quar_txt = (
        "• Model receives only launch specifications, launch price, category, brand\n"
        "• Reviews, star ratings, and sales volume are strictly isolated\n"
        "• Single-pass inference evaluated against ground_truth.json\n"
        "• Promoted model achieves rho = 0.672, AUC = 0.971 (delta = +0.110)\n"
        "• Byte-for-byte prediction integrity confirmed (SHA-256 invariant)"
    )
    ax.text(c2_x + 2.6, c2_y + 11.8, quar_txt, fontsize=7.2, color="#991B1B", va="top", linespacing=1.35, zorder=4)

    fig.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"Generated clean Figure 2 to {save_path}")

if __name__ == "__main__":
    t_dir = Path("scratch")
    t_dir.mkdir(exist_ok=True)
    generate_figure_1(t_dir / "test_fig1_v2.png")
    generate_figure_2(t_dir / "test_fig2_v2.png")
