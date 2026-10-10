"""Comprehensive end-to-end repair script for both IEEE papers.
Updates:
1. Research Paper:
   - Replace Fig 8c (rId30) with fresh Chrome screenshot (image22_new.jpg)
   - Replace Fig 5 (rId17) with verified pipeline diagram (image9_new.jpg)
   - Remove orphaned old Table 2 image (rId18 -> media/image10.png)
   - Update P15, P37 extraction coverage (32,477 extraction rows, 29,410 matched reviews)
   - Update P46 headline model metrics (CV R² = 0.595 ± 0.030, RMSE = 11.17, MAE = 8.65)
   - Update P48 leakage-free Table 1 description
   - Update Table 1 (Table 0 in DOCX) with leakage-free 6-algorithm results
   - Update Table 2 (Table 1 in DOCX) row 1 with CV R² = 0.595 ± 0.030, mean per-cat R² = 0.48
   - Update P84: reproducible price-free rho = 0.476, remove unsupported brand-tier sentence, add Reddit A/B finding
   - Update P106: CV R² = 0.595 vs 0.570
   - Split merged bibliography paragraphs into clean separate entries
2. Survey Paper:
   - Fix awkward phrasing in P15 & P42 (43,599 corpus, 640 collected, 631 retained, 29,410 matched reviews, 32,477 extraction rows)
   - Verify literature table (Shan et al., Sayyad et al., Alantari et al., Wang et al.)
   - Update LaunchSight CV row in Table 0 to CV R² = 0.595 ± 0.030, RMSE = 11.17, MAE = 8.65
   - Split merged references [5]/[6], [16]/[17], [22]/[23], [27]/[28] into distinct paragraphs
"""
import copy
import os
import re
import shutil
import zipfile
from pathlib import Path
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
RP_DOCX = ROOT / "Research_Paper_IEEE_CORRECTED_v3.docx"
SP_DOCX = ROOT / "Survey_Paper_IEEE_CORRECTED_v3.docx"
IMG9_PATH = ROOT / "scratch_inspect/image9_new.jpg"
IMG22_PATH = ROOT / "scratch_inspect/image22_new.jpg"

def repair_research_paper():
    print("=== REPAIRING RESEARCH PAPER ===")
    doc = docx.Document(str(RP_DOCX))
    
    # 1. Update Figure 8c screenshot (rId30)
    if "rId30" in doc.part.rels and IMG22_PATH.exists():
        new_bytes = IMG22_PATH.read_bytes()
        doc.part.rels["rId30"].target_part._blob = new_bytes
        print(f"  [Fig 8c] Updated rId30 with live Chrome screenshot ({len(new_bytes)} bytes)")
    else:
        print("  [Fig 8c] WARNING: rId30 or IMG22_PATH not found!")

    # 2. Update Figure 5 diagram (rId17)
    if "rId17" in doc.part.rels and IMG9_PATH.exists():
        new_bytes = IMG9_PATH.read_bytes()
        doc.part.rels["rId17"].target_part._blob = new_bytes
        print(f"  [Fig 5] Updated rId17 with verified pipeline diagram ({len(new_bytes)} bytes)")
    else:
        print("  [Fig 5] WARNING: rId17 or IMG9_PATH not found!")

    # 3. Update P15
    p15 = doc.paragraphs[15]
    p15_text = p15.text
    new_p15 = (
        "C1. A null-forcing aspect-extraction scheme across 32,477 catalog extraction rows "
        "(spanning 29,410 matched customer reviews from the 43,599-review corpus): the LLM may "
        "score an aspect only when the review gives verbatim evidence for it, never by inference, "
        "backed by typed validation and a crash-safe multi-provider pipeline."
    )
    p15.text = new_p15
    print("  [P15] Updated extraction contribution wording.")

    # 4. Update P37
    p37 = doc.paragraphs[37]
    new_p37 = (
        "The corpus comes from the Amazon Reviews 2023 dataset [40], filtered to five physical product "
        "categories: wireless headphones (138 products), Bluetooth speakers (136), smartwatches (116), "
        "power banks (103), and ice makers (147). From an initial collection of 640 products and 43,599 "
        "customer reviews, automated fraud filtering excluded 9 products (6 for unnatural review bursts "
        "and 3 for extreme J-shaped rating distributions; the near-duplicate rule flagged none), retaining "
        "631 clean products with 43,472 customer reviews (median 47 reviews per product, interquartile range "
        "21–74.5; reviews are capped at 300 per product). Retained products per category: headphones 138, ice "
        "makers 145, speakers 135, smartwatches 114, power banks 99. Across the corpus, aspect-level sentiment "
        "extraction yielded 29,410 matched reviews (67.5% review-level coverage, spanning 100% of retained "
        "products). In total, 32,477 extraction rows are aggregated across the 640 catalog products (32,353 across "
        "the 631 retained products) to build the product feature matrix. Pre-launch specifications were scraped "
        "from manufacturer catalog fields."
    )
    p37.text = new_p37
    print("  [P37] Updated corpus and extraction coverage details.")

    # 5. Update P46
    p46 = doc.paragraphs[46]
    new_p46 = (
        "Product-level features roll the extraction stream up into a mean score and a mention rate per aspect. "
        "An unmentioned aspect stays missing rather than imputed, which XGBoost handles natively. On top of "
        "these we add launch-available metadata: price, a brand-recognition tier, and category indicators. "
        "The regressors are gradient-boosted (600 estimators, depth 5, learning rate 0.05, seed 42) under "
        "5-fold cross-validation. Each review aspect and the brand tier is constrained non-decreasing (+1), while "
        "price is constrained non-increasing (-1). The production headline model achieves cross-validation "
        "R² = 0.595 ± 0.030 (RMSE = 11.17, MAE = 8.65), compared to an unconstrained variant (CV R² = 0.616 ± 0.048, "
        "RMSE = 10.86, MAE = 8.43) and the full leaky metadata ceiling (CV R² = 0.892, RMSE = 5.76, MAE = 4.34). "
        "When early stopping is evaluated on an inner training split (leaving outer validation folds strictly untouched), "
        "cross-validated R² is 0.570 (constrained) and 0.578 (unconstrained). The headline model removes average "
        "rating, rating count, and review velocity while retaining price, brand tier, category, and LLM-derived aspect features."
    )
    p46.text = new_p46
    print("  [P46] Updated production headline CV metrics and unconstrained comparison.")

    # 6. Update P48
    p48 = doc.paragraphs[48]
    new_p48 = (
        "Algorithm selection. We benchmarked six algorithms under identical 5-fold cross-validation on the "
        "standardized feature set used by the benchmark script: LLM-derived aspect means and mention rates plus "
        "brand tier, with price and category excluded and missing aspect values filled with zero for every model. "
        "To eliminate evaluation leakage, classification decision thresholds were derived strictly from training folds "
        "(median of training success scores), top/bottom quintiles were established on training folds, and early stopping "
        "for XGBoost used an inner 85/15 training split. Under this strict leakage-free protocol, Gradient Boosting and "
        "XGBoost lead the benchmark with R² = 0.558 and R² = 0.550 (RMSE 11.6 and 11.8), while achieving top-vs-bottom "
        "discrimination AUC of 0.980 and 0.978 (Accuracy 92.2% and 91.9%, F1 0.924 and 0.917; Table 1). These values "
        "evaluate an aspect-derived feature set and are distinct from the headline production model which incorporates "
        "launch price and category priors (cross-validated R² = 0.595)."
    )
    p48.text = new_p48
    print("  [P48] Updated algorithm selection to document leakage-free protocol.")

    # 7. Update Table 1 (Table 0 in DOCX)
    t0 = doc.tables[0]
    t0_data = [
        ["Algorithm", "R²", "RMSE", "Acc.", "Prec.", "Rec.", "Spec.", "F1", "AUC", "MCC"],
        ["XGBoost", ".550", "11.8", ".919", ".899", ".941", ".880", ".917", ".978", ".835"],
        ["Grad. Boosting", ".558", "11.6", ".922", ".908", ".943", ".886", ".924", ".980", ".840"],
        ["Random Forest", ".520", "12.1", ".918", ".887", ".959", ".864", ".921", ".970", ".834"],
        ["MLP Regr.", ".493", "12.5", ".902", ".878", ".923", ".880", ".898", ".968", ".803"],
        ["Ridge Regr.", ".464", "12.8", ".914", ".901", ".914", ".914", ".906", ".958", ".826"],
        ["SVR (RBF)", ".432", "13.2", ".898", ".905", ".890", ".911", ".896", ".958", ".796"],
    ]
    for r_idx, row_vals in enumerate(t0_data):
        row = t0.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            row.cells[c_idx].text = val
    print("  [Table 1] Updated Table 0 with verified leakage-free metrics.")

    # 8. Update Table 2 (Table 1 in DOCX) row 1
    t1 = doc.tables[1]
    t1.rows[1].cells[0].text = "Cross-validation (5-fold CV, n = 631)"
    t1.rows[1].cells[1].text = "CV R² = 0.595 ± 0.030"
    t1.rows[1].cells[2].text = "—"
    t1.rows[1].cells[3].text = "mean per-category R² = 0.48"
    print("  [Table 2] Updated Row 1 with CV R² = 0.595 ± 0.030 and mean per-cat R² = 0.48.")

    # 9. Update P84
    p84 = doc.paragraphs[84]
    new_p84 = (
        "Price enters the model as a monotone non-increasing feature. A price-free ablation removes product "
        "price and the deterministic value-for-money ratio while retaining LLM-extracted aspect scores, mention "
        "rates, category indicators, and brand-recognition tier; it maintains ρ = 0.476 on the extended deployment "
        "cohort (n = 118, p = 5.09 × 10⁻⁸). A price-only baseline is weak: within-category price percentile correlates "
        "with the success score at ρ = 0.147 across all 631 products (95% range 0.023–0.271 over 40 random "
        "category-stratified draws of 117 products), far below the model's 0.529, and the relationship differs sharply "
        "by category (smartwatches 0.54, headphones 0.35, speakers 0.22, power banks 0.01, ice makers −0.26). "
        "Evaluating the contribution of Reddit consumer-priorities via an A/B trial on real products (seed 42, n = 89) "
        "yielded Spearman ρ = 0.359 with Reddit context versus ρ = 0.311 without (Δρ = +0.049, 95% CI [−0.024, 0.127], "
        "AUC 0.752 vs. 0.728); because the confidence interval spans zero, the observed lift is not statistically significant. "
        "These baseline and ablation figures provide supporting evidence from the archived evaluation sample."
    )
    p84.text = new_p84
    print("  [P84] Updated price-free ablation to 0.476, removed unsupported baseline, added Reddit A/B finding.")

    # 10. Update P106
    p106 = doc.paragraphs[106]
    p106_text = p106.text
    p106_text = p106_text.replace("cross-validated R² 0.577 vs. 0.554", "cross-validated R² 0.595 vs. 0.570")
    p106.text = p106_text
    print("  [P106] Updated discussion CV R² reference.")

    # 11. Separate merged bibliography paragraphs in Research Paper
    split_count = 0
    # Collect paragraph texts and references
    for p_idx in range(len(doc.paragraphs) - 1, 110, -1):
        p = doc.paragraphs[p_idx]
        text = p.text.strip()
        # Find all [X] at the start of entries
        parts = re.split(r'(?=\[\d+\])', text)
        parts = [pt.strip() for pt in parts if pt.strip()]
        if len(parts) > 1:
            # First part stays in current paragraph
            p.text = parts[0]
            # Subsequent parts are inserted as new paragraphs right after
            curr_p = p
            for pt in parts[1:]:
                new_p = doc.add_paragraph(pt)
                # Move new_p._p right after curr_p._p in XML
                curr_p._p.addnext(new_p._p)
                curr_p = new_p
                split_count += 1
    print(f"  [Bibliography] Separated {split_count} merged reference entries into individual paragraphs.")

    doc.save(str(RP_DOCX))
    print("  Saved updated Research Paper DOCX.")

    # 12. Purge orphaned rId18 (media/image10.png) from DOCX zip package
    _purge_orphaned_image(RP_DOCX, "rId18", "media/image10.png")


def _purge_orphaned_image(docx_path: Path, rid: str, image_path_in_zip: str):
    temp_zip = docx_path.with_suffix(".tmp.zip")
    with zipfile.ZipFile(docx_path, "r") as zin:
        with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == f"word/{image_path_in_zip}":
                    print(f"  [Purge] Removed orphaned file word/{image_path_in_zip} ({item.file_size} bytes)")
                    continue
                data = zin.read(item.filename)
                if item.filename == "word/_rels/document.xml.rels":
                    # Remove the Relationship element for this rId
                    text = data.decode("utf-8")
                    pattern = rf'<Relationship[^>]*Id="{rid}"[^>]*/>'
                    new_text = re.sub(pattern, "", text)
                    if new_text != text:
                        print(f"  [Purge] Removed relationship {rid} from document.xml.rels")
                    data = new_text.encode("utf-8")
                zout.writestr(item, data)
    shutil.move(temp_zip, docx_path)
    print("  [Purge] Successfully rebuilt DOCX without orphaned image.")


def repair_survey_paper():
    print("\n=== REPAIRING SURVEY PAPER ===")
    doc = docx.Document(str(SP_DOCX))

    # 1. Update P15
    p15 = doc.paragraphs[15]
    new_p15 = (
        "Within the 28 selected publications synthesized in this survey, this paper examines the "
        "methodological landscape bridging unstructured natural language reviews and predictive viability modeling. "
        "Using a corpus of 43,599 customer reviews across 640 initially collected products (631 retained after "
        "fraud filtering), with aspect-level representations extracted for the documented subset of 29,410 matched "
        "reviews (32,477 total catalog extraction rows), we evaluate how state-of-the-art sentiment and ABSA "
        "architectures map onto product-level viability forecasting."
    )
    p15.text = new_p15
    print("  [P15] Updated awkward phrasing and extraction coverage.")

    # 2. Update P42
    p42 = doc.paragraphs[42]
    new_p42 = (
        "The case study corpus comprises 43,599 customer reviews across 640 initially collected products in "
        "five Amazon categories (Bluetooth speakers, ice makers, power banks, smartwatches, and wireless headphones). "
        "Automated fraud filtering retained 631 products. Aspect-level extraction yielded 29,410 matched reviews from "
        "this corpus (67.5% review-level coverage), providing 100% product-level representation across all 631 retained "
        "products, with 32,477 total extraction rows aggregated in the catalog feature table."
    )
    p42.text = new_p42
    print("  [P42] Updated Section IV.A corpus and extraction coverage description.")

    # 3. Update Table 0 LaunchSight CV row
    t0 = doc.tables[0]
    for row in t0.rows:
        row_txt = " | ".join(c.text for c in row.cells)
        if "LaunchSight (in-sample CV)" in row_txt:
            row.cells[0].text = "LaunchSight (in-sample CV)"
            row.cells[1].text = "Aspect-to-success viability modeling"
            row.cells[2].text = "XGBoost regressor (n = 631)"
            row.cells[3].text = "5-fold CV R², RMSE, MAE"
            row.cells[4].text = "R² = 0.595 ± 0.030, RMSE = 11.17, MAE = 8.65"
            print("  [Table 0] Updated LaunchSight in-sample CV row to verified R² = 0.595.")
            break

    # 4. Separate merged bibliography entries [5]/[6], [16]/[17], [22]/[23], [27]/[28]
    split_count = 0
    for p_idx in range(len(doc.paragraphs) - 1, 55, -1):
        p = doc.paragraphs[p_idx]
        text = p.text.strip()
        parts = re.split(r'(?=\[\d+\])', text)
        parts = [pt.strip() for pt in parts if pt.strip()]
        if len(parts) > 1:
            p.text = parts[0]
            curr_p = p
            for pt in parts[1:]:
                new_p = doc.add_paragraph(pt)
                curr_p._p.addnext(new_p._p)
                curr_p = new_p
                split_count += 1
    print(f"  [Bibliography] Separated {split_count} merged references into individual paragraphs.")

    doc.save(str(SP_DOCX))
    print("  Saved updated Survey Paper DOCX.")


if __name__ == "__main__":
    repair_research_paper()
    repair_survey_paper()
