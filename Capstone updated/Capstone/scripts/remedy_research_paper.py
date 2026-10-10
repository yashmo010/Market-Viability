"""Remediate Research Paper according to Audit Checklist (R-01 through R-30).

Updates docx text, captions, tables, and images, then compiles to PDF via Word COM.
"""
import os
import shutil
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
import win32com.client

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Capstone updated\Capstone")
DOCX_SRC = ROOT / "paper_ieee" / "Launch-Blind_Product_Viability.docx"

OUT_FINAL_SUB = ROOT / "audit paper" / "final_submission" / "research_paper"
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
        'rId15': ROOT / 'papers/figures/fig3_aspect_validity.png',
        'rId16': ROOT / 'papers/figures/fig6a_prediction.png',
        'rId17': ROOT / 'papers/figures/fig6b_spec_coach.png',
        'rId18': ROOT / 'papers/figures/fig6c_analyzer.png',
    }

    for rId, path in img_map.items():
        if rId in doc.part.rels and path.exists():
            target_part = doc.part.rels[rId].target_part
            target_part._blob = path.read_bytes()
            print(f"Updated {rId} with {path.name}")

    # 2. Update Table 2 (doc.tables[1]) - Reliability summary
    table2 = doc.tables[1]
    # Header: Evaluation, rho (pooled), AUC, within-cat. rho
    rows_data = [
        ["Evaluation Cohort", "Spearman \u03c1 (95% CI)", "Top vs. Bottom Quintile AUC", "Within-Category \u03c1 (mean)"],
        ["Cross-validation (5-fold CV, n=631)", "R\u00b2 = 0.566 (aspects-only pure); 0.892 (full metadata)", "AUC = 0.810 (classification threshold)", "Within-cat. R\u00b2 = 0.548"],
        ["Pre-registered Holdout (frozen, n=59)", "0.317 [0.059, 0.543] (p = 0.014)", "0.743 [0.507, 0.931]", "0.28 (mean across categories)"],
        ["Forward-in-Time Temporal Holdout (n=66)", "0.545 [0.352, 0.694] (p = 1.2\u00d710\u207b\u2075)", "0.901 [0.784, 0.985]", "0.16 (technological drift conservative)"],
        ["Extended Deployment Cohort (prompt v2, n=117)", "0.529 [0.377, 0.654] (p = 7.6\u00d710\u207b\u2077)", "0.903 [0.812, 0.965]", "0.39 (pooled across 5 categories)"],
    ]

    # Ensure table has enough rows
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

    # 3. Update paragraphs across the document
    for i, p in enumerate(doc.paragraphs):
        t = p.text

        # Abstract
        if t.startswith("Abstract") or "manufacturing budget long before anyone" in t:
            p.text = (
                "Abstract\u2014A product team commits its manufacturing budget long before anyone has held the product, "
                "yet almost every method for predicting whether an e-commerce product will succeed assumes reviews, ratings, "
                "or sales velocity already exist. We formulate pre-launch product viability estimation as a launch-blind task: "
                "predicting eventual market performance from nothing more than the product's pre-launch specification copy, "
                "category, price, and brand tier. Our system, LaunchSight, addresses this cold-start challenge through a "
                "two-stage hybrid architecture. In Stage 1, an LLM extracts aspect-level sentiment from over 43,500 historical "
                "customer reviews across five physical product categories (631 products post fraud-filtering), establishing "
                "empirical category reference distributions. In Stage 2, a skeptic-prompted bridging layer maps candidate "
                "product specifications into projected aspect scores, which feed a monotonic-constrained gradient boosted regressor "
                "for composite viability scoring. On a pre-registered out-of-sample holdout (n = 59), specs-only predicted viability "
                "correlates with actual post-launch market success at Spearman \u03c1 = 0.317 (p = 0.014, 95% bootstrap CI [0.059, 0.543]) "
                "and separates top-quintile from bottom-quintile products at AUC = 0.743 (95% CI [0.507, 0.931]). On a forward-in-time "
                "temporal holdout of products launched after October 2021 (n = 66 mature evaluation products), the model achieves "
                "\u03c1 = 0.545 (95% CI [0.352, 0.694]) and top-vs-bottom quintile AUC = 0.901. We document boundary conditions where "
                "spec expressiveness limits bridging, and provide calibrated reliability weighting and abstention mechanisms."
            )
            print(f"Updated Abstract (para {i})")

        # Contribution C1
        if "C1. A null-forcing aspect-extraction" in t:
            p.text = (
                "C1. A null-forcing aspect-extraction scheme over 43,599 customer reviews across 5 physical product categories "
                "(631 products after removing 9 review-fraud products): the LLM may score an aspect only when review text explicitly "
                "attests to it, falling back to null otherwise."
            )

        # Contribution C3
        if "C3. Two out-of-sample evaluations" in t:
            p.text = (
                "C3. Two rigorous out-of-sample evaluations\u2014a pre-registered leakage-controlled holdout (n = 59, \u03c1 = 0.317, "
                "95% CI [0.059, 0.543], AUC = 0.743) and a forward-in-time temporal holdout (n = 66, \u03c1 = 0.545, AUC = 0.901)\u2014that "
                "confirm a real, reproducible rank correlation from specifications alone."
            )

        # Contribution C4
        if "C4. An honest map of scope" in t:
            p.text = (
                "C4. An honest map of scope\u2014which aspects and categories a specification can predict and which it cannot\u2014together "
                "with an empirical autopsy of why ice makers fail to bridge despite having abundant review signal (specifications describe "
                "physical capacity rather than experiential quality)."
            )

        # Fig 1 caption
        if t.startswith("Figure 1.") or "All evaluation metrics across six algorithms" in t:
            p.text = (
                "Figure 1. All evaluation metrics across six algorithms on the aspects-only feature set (5-fold CV, n = 631). "
                "Metrics: R\u00b2, Accuracy, Precision, Recall, F1, AUC-ROC, MCC."
            )

        # Fig 3 caption
        if t.startswith("Figure 3.") or "Complete numerical comparison across all evaluation metrics" in t:
            p.text = (
                "Figure 3. Complete numerical comparison across all evaluation metrics (physical products, n = 631, 5-fold CV, seed 42). "
                "Per-metric best values are highlighted in green; no subjective single-metric ranking verdict is imposed."
            )

        # Text before Figure 3 about algorithm comparison
        if "Bold verdict column summarises the overall ranking" in t or "Why XGBoost. We did not take" in t:
            p.text = (
                "Why XGBoost. We benchmarked six algorithms under identical 5-fold cross-validation on the aspects-only feature set "
                "(n = 631 physical products, seed 42). Rather than declaring a single subjective verdict, Table 1 and Figure 3 report "
                "all regression and classification metrics side by side. XGBoost achieves the strongest regression performance (R\u00b2 = 0.566 "
                "pure aspects-only, RMSE = 7.1, MAE = 5.4), while Gradient Boosting slightly leads in classification metrics "
                "(Accuracy = 0.810, F1 = 0.812). XGBoost trains in 0.04 seconds\u2014over 140\u00d7 faster than Multi-Layer Perceptron (5.71 s) "
                "and Support Vector Regression (5.42 s)\u2014and supports native monotonic feature constraints, making it the most defensible "
                "production backbone."
            )

        # Paragraph 59: Holdout validation text
        if "We bridged 118 products" in t or "Leakage-Controlled Out-of-Sample Holdout" in doc.paragraphs[max(0, i-1)].text:
            p.text = (
                "We evaluated our frozen production bridging pipeline on a pre-registered out-of-sample holdout of n = 59 products drawn "
                "across all five categories. For every holdout product, all reviews, star ratings, and post-launch signals were completely "
                "quarantined. The model saw only pre-launch metadata (name, category, price, brand tier) and manufacturer specification copy. "
                "Category priors and min-max scalers were computed strictly on the training partition (n = 572). Specs-only predicted viability "
                "correlates with actual post-launch market success at Spearman \u03c1 = 0.317 (p = 0.014), with a 10,000-sample bootstrap 95% "
                "confidence interval of [0.059, 0.543] that strictly excludes zero. In top-quintile versus bottom-quintile discrimination "
                "(excluding the intermediate 60% of products), the model achieves AUC = 0.743 (95% bootstrap CI [0.507, 0.931]). Mean predicted "
                "viability climbs monotonically across the actual success quintiles (58.51 \u2192 60.83 \u2192 61.69 \u2192 62.76 \u2192 64.06; Fig. 6). "
                "In an extended production test across n = 117 products using updated specification prompt v2, the model achieved \u03c1 = 0.529 "
                "(95% CI [0.377, 0.654]) and AUC = 0.903. The primary conservative evidence remains the frozen holdout (\u03c1 = 0.317), which "
                "demonstrates a statistically significant screening signal across candidate product designs."
            )
            print(f"Updated Holdout Validation text (para {i})")

        # Fig 6 caption
        if t.startswith("Figure 6.") or "Leakage-controlled holdout (n=118)" in t or "specs-only predicted viability" in t:
            p.text = (
                "Figure 6. Pre-registered out-of-sample holdout (n = 59): specs-only predicted viability versus actual market success, "
                "with monotonic success-quintile means (\u03c1 = 0.317, 95% CI [0.059, 0.543], AUC = 0.743, p = 0.014)."
            )

        # Temporal holdout paragraph
        if "Forward-in-Time Temporal Holdout" in doc.paragraphs[max(0, i-1)].text or "A random split can still leak era-specific" in t:
            p.text = (
                "A random split can still leak era-specific market regularities, so we executed a forward-in-time temporal evaluation: "
                "predicting products launched in the future. Products were split strictly by the timestamp of their first recorded review "
                "at a cutoff of October 31, 2021. Models were trained on the 510 products launched on or before October 2021 (with 5-fold CV "
                "hyperparameter tuning). From the 130 products launched afterward, 9 review-fraud suspect products were excluded, leaving 66 "
                "test products with mature post-launch review velocity (>30 reviews). Evaluating on these 66 forward products from specifications "
                "alone yields Spearman \u03c1 = 0.545 (p = 1.2\u00d710\u207b\u2075, 95% bootstrap CI [0.352, 0.694]) and top-vs-bottom quintile "
                "AUC = 0.901 (95% CI [0.784, 0.985]). This demonstrates that the specification-to-viability relationship generalizes across time "
                "and does not degrade into contemporaneous memorization."
            )
            print(f"Updated Temporal Holdout text (para {i})")

        # Fig 7 caption
        if t.startswith("Figure 7.") or "Per-aspect validity of bridged estimates" in t:
            p.text = (
                "Figure 7. Per-aspect validity of bridged estimates (Pearson r with 95% CI), colored by the runtime trust tier presented to "
                "users. High-fidelity experiential aspects (utility, durability, build quality, reliability: r = 0.50\u20130.53) receive high-trust "
                "status, whereas design appeal (r = 0.21) and after-sales service (r = 0.07) are flagged as unestimable from specifications alone."
            )

        # Price orthogonality paragraph
        if "A launch-blind correlation is only worth something" in t:
            p.text = (
                "A launch-blind correlation is only valuable if it captures genuine design information rather than simply rediscovering price. "
                "On the holdout, a within-category price-percentile baseline reaches \u03c1 = 0.386 against actual success. Our model incorporates "
                "price as one monotonically constrained feature, but its LLM-extracted aspect scores contribute substantial independent variance: "
                "a price-free ablation (removing price entirely) maintains \u03c1 = 0.475 on the extended cohort, while the correlation between "
                "the aspect-only prediction and price percentile is weak (r = 0.147, 95% CI [0.02, 0.27]). The aspect features therefore "
                "complement pricing posture rather than acting as a surrogate for it."
            )

    # Save updated DOCX to target paths
    docx_rp_final = OUT_RP_FINAL / "Launch_Blind_Product_Viability_Research_Paper.docx"
    doc.save(str(docx_rp_final))
    shutil.copy2(str(docx_rp_final), str(DOCX_SRC))
    print(f"Saved updated DOCX to {docx_rp_final} and {DOCX_SRC}")

    # Compile to PDF via Word COM
    print("Compiling Research Paper to PDF via Word COM...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc_w = word.Documents.Open(str(docx_rp_final.resolve()))
        pdf_final_sub = OUT_FINAL_SUB / "Launch_Blind_Product_Viability_Research_Paper.pdf"
        pdf_rp_final = OUT_RP_FINAL / "Launch_Blind_Product_Viability_Research_Paper.pdf"
        pdf_paper_ieee = ROOT / "paper_ieee" / "Launch-Blind_Product_Viability.pdf"

        # Save PDF
        doc_w.SaveAs(str(pdf_final_sub.resolve()), FileFormat=17)
        doc_w.Close(False)
        print(f"Exported PDF to {pdf_final_sub} ({pdf_final_sub.stat().st_size} bytes)")

        # Copy to the other target locations
        shutil.copy2(str(pdf_final_sub), str(pdf_rp_final))
        shutil.copy2(str(pdf_final_sub), str(pdf_paper_ieee))
        print(f"Copied PDF to {pdf_rp_final} and {pdf_paper_ieee}")
    finally:
        word.Quit()

if __name__ == "__main__":
    update_research_paper()
    print("Research Paper remediation complete!")
