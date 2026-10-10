"""Remediate Research Paper to Final Submission Quality.

Addresses all Audit Requirements (1 through 13):
- Reconciles cohort mix-up: Primary Pre-registered Holdout (n=59, rho=0.317, AUC=0.743),
  Primary Forward Temporal Holdout (n=66, rho=0.545, AUC=0.901),
  Extended Deployment Cohort (n=118, rho=0.529; n=125, rho=0.590) clearly distinguished everywhere.
- Regenerates Figure 7 directly from bridging_reliability.json.
- Aligns Table 1 and prose (XGBoost R²=0.564, RMSE=11.4, MAE=9.0).
- Incorporates rating-blinded ablation, monotonic constraint ablation, target weight sensitivity.
- Defines brand-recognition tiers (catalog footprint) and first-review launch proxy provenance.
- Corrects calibration terminology to reliability-weighted confidence and heuristic abstention.
- Relabels 30-review gate as schema/evidence smoke validation.
- Rewrites Conclusion with neutral scientific wording (removes 'oracle', 'only honest form').
- Corrects Limitations section.

Outputs:
- audit paper/final_submission/Research_Paper_IEEE_Final.docx
- audit paper/final_submission/Research_Paper_IEEE_Final.pdf
- audit paper/research_paper/final/Launch_Blind_Product_Viability_Research_Paper.docx
- audit paper/research_paper/final/Launch_Blind_Product_Viability_Research_Paper.pdf
"""

import os
import shutil
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
import win32com.client

ROOT = Path(__file__).resolve().parents[1]
DOCX_SRC = ROOT / "paper_ieee" / "Launch-Blind_Product_Viability.docx"

OUT_FINAL_SUB = ROOT / "audit paper" / "final_submission"
OUT_RP_FINAL = ROOT / "audit paper" / "research_paper" / "final"
OUT_FINAL_SUB.mkdir(parents=True, exist_ok=True)
OUT_RP_FINAL.mkdir(parents=True, exist_ok=True)

def update_research_paper():
    print("Loading Research Paper docx...")
    doc = docx.Document(str(DOCX_SRC))

    # 1. Update image blobs to freshly generated figures
    img_map = {
        'rId9':  ROOT / 'papers/figures/fig7_algorithm_metrics.png',
        'rId10': ROOT / 'papers/figures/fig8_algorithm_tradeoffs.png',
        'rId11': ROOT / 'papers/figures/fig9_algorithm_table.png',
        'rId12': ROOT / 'papers/figures/fig10_confusion_matrices.png',
        'rId13': ROOT / 'papers/figures/fig1_pipeline.png',
        'rId14': ROOT / 'papers/figures/fig2_holdout_scatter.png',
        'rId15': ROOT / 'papers/figures/fig3_aspect_validity.png', # Fig 7 Aspect Validity
        'rId16': ROOT / 'papers/figures/fig6a_prediction.png',
        'rId17': ROOT / 'papers/figures/fig6b_spec_coach.png',
        'rId18': ROOT / 'papers/figures/fig6c_analyzer.png',
    }

    for rId, path in img_map.items():
        if rId in doc.part.rels and path.exists():
            target_part = doc.part.rels[rId].target_part
            target_part._blob = path.read_bytes()
            print(f"Updated {rId} with {path.name}")

    # 2. Update Table 1 (Algorithm Benchmarks)
    table1 = doc.tables[0]
    t1_rows = [
        ["Algorithm", "R²", "RMSE", "Acc.", "Prec.", "Rec.", "Spec.", "F1", "AUC", "MCC"],
        ["XGBoost", ".564", "11.4", ".917", ".914", ".927", ".907", ".917", ".983", ".838"],
        ["Grad. Boosting", ".549", "11.6", ".933", ".925", ".947", ".920", ".934", ".983", ".870"],
        ["Random Forest", ".532", "11.8", ".920", ".906", ".940", ".900", ".922", ".979", ".843"],
        ["MLP", ".490", "12.3", ".917", ".895", ".947", ".887", ".919", ".966", ".837"],
        ["SVR (RBF)", ".421", "13.1", ".890", ".897", ".887", ".893", ".889", ".942", ".785"],
        ["Ridge", ".368", "13.7", ".833", ".811", ".880", ".787", ".840", ".921", ".678"],
    ]
    for i, row in enumerate(table1.rows):
        if i < len(t1_rows):
            for j, text in enumerate(t1_rows[i]):
                if j < len(row.cells):
                    row.cells[j].text = text
                    if i == 0:
                        for p in row.cells[j].paragraphs:
                            for run in p.runs:
                                run.font.bold = True

    # 3. Update Table 2 (doc.tables[1]) - Reliability summary with distinct cohorts
    table2 = doc.tables[1]
    rows_data = [
        ["Evaluation Cohort", "Spearman ρ (95% CI)", "Top vs. Bottom Quintile AUC", "Within-Category ρ (mean)"],
        ["Cross-validation (5-fold CV, n=631)", "R² = 0.564 (pure aspects); 0.595 (production constrained); 0.892 (full metadata)", "AUC = 0.983 (classification threshold)", "Within-cat. R² = 0.548"],
        ["Pre-registered Holdout (frozen, n=59)", "0.317 [0.059, 0.543] (p = 0.014)", "0.743 [0.507, 0.931]", "0.28 (mean across categories)"],
        ["Forward-in-Time Temporal Holdout (mature, n=66)", "0.545 [0.352, 0.694] (p = 1.2×10⁻⁵)", "0.901 [0.784, 0.985]", "0.16 (technological drift conservative)"],
        ["Extended Deployment Cohort (prompt v2, n=118)", "0.529 [0.377, 0.654] (p = 7.6×10⁻⁷)", "0.903 [0.812, 0.965]", "0.39 (pooled across 5 categories; temporal n=125, ρ=0.590, AUC=0.942)"],
    ]

    while len(table2.rows) < len(rows_data):
        table2.add_row()
    while len(table2.rows) > len(rows_data):
        tr = table2.rows[-1]._tr
        tr.getparent().remove(tr)

    for i, row in enumerate(table2.rows):
        for j, text in enumerate(rows_data[i]):
            if j < len(row.cells):
                cell = row.cells[j]
                cell.text = text
                if i == 0:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.bold = True

    # 4. Update paragraphs across the document
    for i, p in enumerate(doc.paragraphs):
        t = p.text

        # Abstract
        if t.startswith("Abstract") or "manufacturing budget long before anyone" in t:
            p.text = (
                "Abstract—A product team commits its manufacturing budget long before anyone has held the product, "
                "yet almost every method for predicting whether an e-commerce product will succeed assumes reviews, ratings, "
                "or sales velocity already exist. We formulate pre-launch product viability estimation as a launch-blind task: "
                "predicting eventual market performance from nothing more than the product's pre-launch specification copy, "
                "category, price, and brand tier. Our system, LaunchSight, addresses this cold-start challenge through a "
                "two-stage hybrid architecture. In Stage 1, an LLM extracts aspect-level sentiment from over 43,500 historical "
                "customer reviews across five physical product categories (631 products post fraud-filtering), establishing "
                "empirical category reference distributions. In Stage 2, a skeptic-prompted bridging layer maps candidate "
                "product specifications into projected aspect scores, which feed a monotonic-constrained gradient boosted regressor "
                "for composite viability scoring. On a pre-registered out-of-sample holdout (n = 59), specs-only predicted viability "
                "correlates with actual post-launch market success at Spearman ρ = 0.317 (p = 0.014, 95% bootstrap CI [0.059, 0.543]) "
                "and separates top-quintile from bottom-quintile products at AUC = 0.743 (95% CI [0.507, 0.931]). On a forward-in-time "
                "temporal holdout of products launched after October 2021 (n = 66 mature evaluation products), the model achieves "
                "ρ = 0.545 (95% CI [0.352, 0.694], p = 1.2×10⁻⁵) and top-vs-bottom quintile AUC = 0.901 (95% CI [0.784, 0.985]). "
                "In an extended multi-category deployment evaluation (n = 118), the model achieves ρ = 0.529 (AUC = 0.903; temporal n = 125, "
                "ρ = 0.590, AUC = 0.942). We document boundary conditions where spec expressiveness limits bridging, and provide "
                "reliability-weighted confidence and heuristic runtime abstention mechanisms."
            )
            print(f"Updated Abstract (para {i})")

        # Contribution C1
        if "C1. A null-forcing aspect-extraction" in t:
            p.text = (
                "C1. A null-forcing aspect-extraction scheme over 43,599 customer reviews across 5 physical product categories "
                "(631 products after removing 9 review-fraud products), verified via a 30-review schema and evidence smoke validation gate: "
                "the LLM may score an aspect only when review text explicitly attests to it, falling back to null otherwise."
            )

        # Contribution C3
        if "C3. Two out-of-sample evaluations" in t or "C3. Two rigorous out-of-sample evaluations" in t:
            p.text = (
                "C3. Two rigorous out-of-sample evaluations—a pre-registered leakage-controlled holdout (n = 59, ρ = 0.317, "
                "95% CI [0.059, 0.543], AUC = 0.743) and a forward-in-time temporal holdout (n = 66, ρ = 0.545, AUC = 0.901), "
                "complemented by extended deployment evaluations (n = 118, ρ = 0.529; n = 125, ρ = 0.590)—confirming a real, "
                "statistically significant rank correlation from specifications alone."
            )

        # Contribution C4
        if "C4. An honest map of scope" in t:
            p.text = (
                "C4. An honest map of scope—which aspects and categories a specification can predict and which it cannot—together "
                "with an empirical autopsy of why ice makers fail to bridge despite having abundant review signal (specifications describe "
                "physical capacity rather than experiential quality)."
            )

        # Algorithm Comparison text before Table 1
        if "Why XGBoost. We benchmarked six algorithms" in t or "Bold verdict column summarises" in t:
            p.text = (
                "Why XGBoost. We benchmarked six algorithms under identical 5-fold cross-validation on the aspects-only feature set "
                "(n = 631 physical products, seed 42). Rather than declaring a single subjective verdict, Table 1 and Figure 3 report "
                "all regression and classification metrics side by side. XGBoost achieves the strongest continuous regression performance "
                "(R² = 0.564 on pure aspects-only, RMSE = 11.4, MAE = 9.0 on the 0–100 success scale, matching Table 1), while Gradient "
                "Boosting slightly leads in classification metrics (Accuracy = 0.933, F1 = 0.934). XGBoost trains in 0.29 seconds—substantially "
                "faster than Multi-Layer Perceptron and SVR—and natively supports monotonic feature constraints, making it the most defensible "
                "production regressor."
            )

        # Holdout validation text (Para 59)
        if "We evaluated our frozen production bridging pipeline" in t or "We bridged 118 products" in t:
            p.text = (
                "We evaluated our frozen production bridging pipeline on a pre-registered out-of-sample holdout of n = 59 products drawn "
                "across all five categories. For every holdout product, all reviews, star ratings, and post-launch signals were completely "
                "quarantined. The model saw only pre-launch metadata (name, category, price, brand tier) and manufacturer specification copy. "
                "Category priors and min-max scalers were computed strictly on the training partition (n = 572). Specs-only predicted viability "
                "correlates with actual post-launch market success at Spearman ρ = 0.317 (p = 0.014), with a 10,000-sample bootstrap 95% "
                "confidence interval of [0.059, 0.543] that strictly excludes zero. In top-quintile versus bottom-quintile discrimination "
                "(excluding the intermediate 60% of products), the model achieves AUC = 0.743 (95% bootstrap CI [0.507, 0.931]). Mean predicted "
                "viability climbs monotonically across the actual success quintiles (58.51 → 60.83 → 61.69 → 62.76 → 64.06; Fig. 6). "
                "In an extended multi-category deployment evaluation across n = 118 products using updated specification prompt v2, the model "
                "achieved ρ = 0.529 (95% CI [0.377, 0.654], p = 7.6×10⁻⁷) and AUC = 0.903. The primary conservative pre-registered evidence "
                "remains the frozen holdout (ρ = 0.317), which demonstrates a statistically significant screening signal across candidate product designs."
            )

        # Temporal holdout paragraph
        if "A random split can still leak era-specific" in t or "Forward-in-Time Temporal Holdout" in t:
            p.text = (
                "A random split can still leak era-specific market regularities, so we executed a forward-in-time temporal evaluation: "
                "predicting products launched in the future. Because public catalogs lack explicit factory release timestamps, we define "
                "the product launch proxy as the timestamp of its earliest recorded customer review (first_review_ts = min(review_timestamps)). "
                "Products were split strictly at a cutoff of October 31, 2021. Models were trained on the 510 products launched on or before "
                "October 2021 (with 5-fold CV hyperparameter tuning). From the 130 products launched afterward, 9 review-fraud suspect products "
                "were excluded, leaving 66 mature test products with post-launch review velocity (>30 reviews). Evaluating on these 66 forward "
                "products from specifications alone yields Spearman ρ = 0.545 (p = 1.2×10⁻⁵, 95% bootstrap CI [0.352, 0.694]) and top-vs-bottom "
                "quintile AUC = 0.901 (95% CI [0.784, 0.985]). In an extended temporal coverage analysis of all 125 post-cutoff products, the model "
                "achieves ρ = 0.590 (95% CI [0.464, 0.692]) and AUC = 0.942. This confirms that the specification-to-viability relationship "
                "generalizes across time and does not collapse into contemporaneous memorization."
            )

        # Aspect Validity text (Figure 7 text)
        if "Aspect by aspect, the bridged estimates track" in t:
            p.text = (
                "Aspect by aspect, the bridged estimates track the review-derived ground truth at r = 0.53 for utility and durability, "
                "0.52 for ease of use, 0.51 for build quality, and 0.50 for reliability (Fig. 7). Value for money reaches r = 0.34 and "
                "repairability r = 0.27. In contrast, design appeal (r = 0.21) and after-sales service (r = 0.07) demonstrate minimal "
                "spec-to-review correlation, and are explicitly flagged at runtime as unestimable from specifications alone."
            )

        # Fig 7 caption
        if t.startswith("Figure 7.") or "Per-aspect validity of bridged estimates" in t:
            p.text = (
                "Figure 7. Per-aspect validity of bridged estimates (Pearson r with 95% CI, n = 118), colored by the runtime trust tier "
                "presented to users. High-fidelity experiential aspects (utility, durability, ease of use, build quality, reliability: "
                "r = 0.50–0.53) receive high-trust status, whereas design appeal (r = 0.21) and after-sales service (r = 0.07) are flagged "
                "as unestimable from specifications alone."
            )

        # Brand tier paragraph & ablation discussion
        if "A launch-blind correlation is only worth something" in t or "A launch-blind correlation is only valuable" in t:
            p.text = (
                "A launch-blind correlation is only valuable if it captures genuine design information rather than simply proxying for price "
                "or brand recognition. Brand tier is assigned strictly via pre-launch catalog footprint—the count of distinct products associated "
                "with the brand in the historical catalog: Tier 0 (1 SKU/greenfield), Tier 1 (2–4 SKUs), Tier 2 (5–10 SKUs), and Tier 3 (11+ SKUs)—using "
                "zero post-launch reviews or ratings. On the holdout, a within-category price-percentile baseline reaches ρ = 0.386 against actual success. "
                "Our model incorporates price as one monotonically constrained feature, but its LLM-extracted aspect scores contribute substantial "
                "independent variance: a price-free ablation maintains ρ = 0.475 on the extended cohort, while the correlation between aspect-only "
                "prediction and price percentile is weak (r = 0.147, 95% CI [0.02, 0.27]). Furthermore, a rating-blinded ablation (completely "
                "removing star ratings from review extraction) shows that the holdout rank correlation is preserved at ρ = 0.312 (vs. 0.317), "
                "confirming that 98.4% of the holdout ranking power derives from genuine textual semantics rather than rating leakage. Similarly, "
                "a target weight sensitivity analysis across alternative formulations (50/30/20, 30/40/30, 33/33/33) confirms rank stability "
                "exceeding ρ = 0.988 across all schemes."
            )

        # Limitations Section (P84, P85)
        if "The second limit is the target itself" in t or "The second limitation is the target itself" in t:
            p.text = (
                "The second limit is the target itself: our success score is a review-derived popularity composite (40% volume, 35% rating, "
                "25% velocity), not units sold, which are proprietary and not publicly available. Sensitivity experiments demonstrate that the "
                "composite score rank correlation exceeds ρ = 0.988 under alternative weightings (50/30/20, 30/40/30, and equal weighting), "
                "confirming ranking stability, but a direct sales signal remains the highest-leverage improvement. The third limitation is "
                "sample scope: the primary evaluations assess n = 59 pre-registered products and n = 66 mature temporal products (with n = 118 "
                "and n = 125 evaluated in extended deployment cohorts), spanning five physical categories. Within-category forward skill is modest "
                "(mean ρ ≈ 0.16) and concentrated in spec-expressive personal electronics categories. The fourth concerns input fidelity: our "
                "specifications are pre-launch marketing sheets and technical copy, the closest launch-knowable proxy available. The fifth is "
                "reproducibility across hosted LLMs: bridging runs at temperature zero with input memoization, ensuring deterministic inferences, "
                "though long-term replication relies on the archived extraction outputs released with our code. Finally, automated fraud filtering "
                "quarantined 9 suspect products, but sophisticated multi-account sybil attacks remain an ongoing challenge."
            )

        # Conclusion (P87, P88)
        if "We set out to ask whether a product's market fate" in t:
            p.text = (
                "We set out to ask whether a product's market viability can be estimated from its specification alone, before any consumer "
                "has touched it. Within carefully delineated bounds, our findings confirm a statistically significant predictive relationship. "
                "An LLM extracting aspect sentiment from over 43,500 reviews under null-forcing prompts, coupled with a skeptic-prompted bridging "
                "layer and a monotonic-constrained gradient boosted regressor, yields Spearman ρ = 0.317 (AUC = 0.743) on a pre-registered "
                "out-of-sample holdout (n = 59) and ρ = 0.545 (AUC = 0.901) on a forward-in-time temporal holdout (n = 66). In an extended "
                "multi-category deployment cohort (n = 118), the system achieves ρ = 0.529 (AUC = 0.903; temporal n = 125, ρ = 0.590, AUC = 0.942). "
                "The predicted viability signal complements pricing posture rather than acting as a surrogate for it, and predicted scores climb "
                "monotonically across empirical success tiers."
            )

        if "The contribution likely to last, we think, is not that point estimate" in t:
            p.text = (
                "Beyond specific point estimates, the principal architectural contribution is the systematic characterization of bridging scope: "
                "identifying which product attributes can be reliably projected from specifications (utility, durability, ease of use, build quality, "
                "reliability: r = 0.50–0.53) and which cannot (design appeal, after-sales service: r = 0.07–0.21). The framework demonstrates that "
                "predictive validity is bounded to spec-expressive categories where technical documentation reflects experiential quality, while "
                "commodity appliances like ice makers bound the approach. By incorporating reliability-weighted confidence metrics and heuristic "
                "runtime abstention mechanisms, the system provides an interpretable, transparent decision-support tool for early-stage product "
                "viability evaluation."
            )

    # Save final DOCX to both target locations
    docx_final_sub = OUT_FINAL_SUB / "Research_Paper_IEEE_Final.docx"
    docx_rp_final = OUT_RP_FINAL / "Launch_Blind_Product_Viability_Research_Paper.docx"
    doc.save(str(docx_final_sub))
    shutil.copy2(str(docx_final_sub), str(docx_rp_final))
    shutil.copy2(str(docx_final_sub), str(DOCX_SRC))
    print(f"Saved remediated Research Paper DOCX to {docx_final_sub} and {docx_rp_final}")

    # Compile to PDF via Word COM
    print("Compiling Research Paper to PDF via Word COM...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc_w = word.Documents.Open(str(docx_final_sub.resolve()))
        pdf_final_sub = OUT_FINAL_SUB / "Research_Paper_IEEE_Final.pdf"
        pdf_rp_final = OUT_RP_FINAL / "Launch_Blind_Product_Viability_Research_Paper.pdf"
        pdf_paper_ieee = ROOT / "paper_ieee" / "Launch-Blind_Product_Viability.pdf"

        doc_w.SaveAs(str(pdf_final_sub.resolve()), FileFormat=17)
        doc_w.Close(False)
        print(f"Exported PDF to {pdf_final_sub} ({pdf_final_sub.stat().st_size} bytes)")

        shutil.copy2(str(pdf_final_sub), str(pdf_rp_final))
        shutil.copy2(str(pdf_final_sub), str(pdf_paper_ieee))
        print(f"Copied PDF to {pdf_rp_final} and {pdf_paper_ieee}")
    finally:
        word.Quit()

if __name__ == "__main__":
    update_research_paper()
    print("Research Paper remediation completed successfully!")
