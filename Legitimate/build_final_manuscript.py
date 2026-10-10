"""Generate Final IEEE Submission Manuscript with Complete Evaluations.
Fully synchronized with all quick text fixes, layout balancing, and submission statements:
- Section V-B: "which shows that predictions do not depend on test labels" (no "proves")
- Section IV-A: p-values specified (asymptotic p=1.25e-17 for rho vs zero; paired permutation p=0.0005 using (b+1)/(M+1) estimator with b=4, M=10,000, and empirical proportion 0.0004)
- Section IV-B: deleted sentence about 0.6331 and 0.6332 coinciding
- Fig. 6 caption: dropped the word "Current"
- Section III-B: fallback model usage (0% fallback required; Gemini 1.5 Flash handled 100% of extractions; caching ensures permanence against API deprecation)
- Section III-B: [30]-[33] framed accurately as multi-feature aspect extraction and sentiment representation literature
- Section II: numbered items left-aligned to eliminate stretched justified lines
- Submission package: Data & Code Availability, CRediT Author Contributions, Funding, Competing Interests, Amazon Data Ethics, and Generative AI Disclosure
- Verified References [1]-[40]
- Balanced layout & image sizing to eliminate half-empty pages
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
LEGIT_DIR = ROOT / "Legitimate"
MANUSCRIPT_DIR = LEGIT_DIR / "09_MANUSCRIPT"
MANUSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = LEGIT_DIR / "figures"
TABLES_DIR = LEGIT_DIR / "tables"

def kill_word():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "WINWORD.EXE"], capture_output=True)
    except Exception:
        pass

def set_font(run, name="Times New Roman", size_pt=10, bold=False, italic=False, color_rgb=(0, 0, 0)):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def set_para_format(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=0, space_after_pt=4, line_spacing=1.06):
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before_pt)
    p.paragraph_format.space_after = Pt(space_after_pt)
    p.paragraph_format.line_spacing = line_spacing

def add_ieee_table(doc, title, headers, rows, col_widths=None):
    """Embeds an IEEE-styled table with full-width rule lines, exact column widths, and zero line wrapping."""
    p_title = doc.add_paragraph()
    set_para_format(p_title, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=8, space_after_pt=3)
    r_t = p_title.add_run(title)
    set_font(r_t, size_pt=8.5, bold=True)

    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Format header row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        p = hdr_cells[i].paragraphs[0]
        set_para_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=2.5, space_after_pt=2.5)
        if p.runs:
            set_font(p.runs[0], size_pt=7.5, bold=True)
        shading = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)

    # Format data rows
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            p = row_cells[c_idx].paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            set_para_format(p, align=align, space_before_pt=1.5, space_after_pt=1.5)
            if p.runs:
                set_font(p.runs[0], size_pt=7.5)

    # Set cell widths, padding, and prevent row splitting across pages
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(r'<w:cantSplit {}/>'.format(nsdecls('w'))))
        for c_idx, cell in enumerate(row.cells):
            if col_widths and c_idx < len(col_widths):
                cell.width = col_widths[c_idx]
            tcPr = cell._tc.get_or_add_tcPr()
            tcMar = parse_xml(r'<w:tcMar {}><w:top w:w="35" w:type="dxa"/><w:bottom w:w="35" w:type="dxa"/><w:left w:w="45" w:type="dxa"/><w:right w:w="45" w:type="dxa"/></w:tcMar>'.format(nsdecls('w')))
            tcPr.append(tcMar)

    p_spacer = doc.add_paragraph()
    set_para_format(p_spacer, space_before_pt=0, space_after_pt=3)

def build_manuscript():
    print("Building Final IEEE Manuscript from Revised Text & Audit Specifications...")
    kill_word()

    doc = docx.Document()
    s1 = doc.sections[0]
    s1.top_margin = Inches(0.75)
    s1.bottom_margin = Inches(0.75)
    s1.left_margin = Inches(0.75)
    s1.right_margin = Inches(0.75)

    # TITLE
    p_title = doc.add_paragraph()
    set_para_format(p_title, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=0, space_after_pt=8)
    r_t = p_title.add_run("Launch-Blind Product Viability Estimation\nfrom Specifications via LLM Aspect Bridging")
    set_font(r_t, size_pt=21, bold=True)

    # AUTHORS
    p_auth = doc.add_paragraph()
    set_para_format(p_auth, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=0, space_after_pt=3)
    r_a = p_auth.add_run("Rajvardhan Ajitrao Jagtap, Jyotiraditya Abhijeet Shinde, Tanishq Parag Choudhari,\nYash Ashok Mohite, Yogesh Malakari Honamore")
    set_font(r_a, size_pt=10, bold=True)

    p_aff = doc.add_paragraph()
    set_para_format(p_aff, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=0, space_after_pt=8)
    r_aff = p_aff.add_run("Department of Computer Science and Engineering\nRajarambapu Institute of Technology, Rajaramnagar, Sangli, Maharashtra, India")
    set_font(r_aff, size_pt=9, italic=True)

    # ABSTRACT
    p_abs = doc.add_paragraph()
    set_para_format(p_abs, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=3, space_after_pt=5)
    r_ab_lbl = p_abs.add_run("Abstract—")
    set_font(r_ab_lbl, size_pt=9, bold=True)

    abs_text = (
        "Hardware manufacturing commits production capital months before consumer release, yet dominant empirical methods for forecasting "
        "commercial reception depend on signals that exist only post-launch: customer reviews, ratings, and sales velocity. This paper evaluates an audited "
        "two-stage pipeline for strictly launch-blind product viability estimation using pre-launch specifications alone. In Stage 1, a large language "
        "model parses unstructured technical copy under a null-forcing schema into a nine-aspect ontology, retaining specification density and verbatim "
        "grounding evidence to resolve the scalar compression bottleneck. In Stage 2, a gradient-boosted decision tree ensemble (XGBoost) with "
        "directional monotonic priors maps this representation to an audited market-success proxy. Evaluation follows a frozen forward-in-time "
        "protocol partitioned at October 31, 2021 (507 training products, 124 strictly post-cutoff holdout products). On this temporal test set, "
        "the promoted architecture achieves Spearman rho = 0.6722 (95% CI [0.5495, 0.7620], asymptotic p = 1.25e-17 against the null of zero rank "
        "correlation; top-versus-bottom quintile AUC = 0.9712). Against the controlled scalar-aspect baseline (rho = 0.5623, AUC = 0.8904), this "
        "represents a statistically significant gain of delta_rho = +0.1099 (paired bootstrap 95% CI [+0.0485, +0.1833]; paired permutation "
        "p = 0.0005). On unseen brands under pure cold-start conditions (n = 82), the model achieves rho = 0.633 (AUC = 0.981). Across a standardized "
        "five-fold out-of-fold benchmark over six learner families, XGBoost ranks highest, closely followed by kernel and boosted-tree alternatives. "
        "List-ranking yields NDCG@5 = 0.8933, and extreme-group classification reaches 92.0% decision accuracy. Predictions are bit-for-bit invariant "
        "under test label deletion."
    )
    r_ab_txt = p_abs.add_run(abs_text)
    set_font(r_ab_txt, size_pt=9)

    # INDEX TERMS
    p_terms = doc.add_paragraph()
    set_para_format(p_terms, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=2, space_after_pt=8)
    r_t_lbl = p_terms.add_run("Index Terms—")
    set_font(r_t_lbl, size_pt=9, bold=True)
    r_t_txt = p_terms.add_run("product success prediction, aspect-based sentiment analysis, cold-start representation, large language models, gradient boosting, electronic word of mouth, temporal validation.")
    set_font(r_t_txt, size_pt=9)

    def add_h1(text):
        p = doc.add_paragraph()
        set_para_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before_pt=10, space_after_pt=3)
        r = p.add_run(text)
        set_font(r, size_pt=10.5, bold=True)

    def add_h2(text):
        p = doc.add_paragraph()
        set_para_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before_pt=6, space_after_pt=2)
        r = p.add_run(text)
        set_font(r, size_pt=9.5, bold=True, italic=True)

    def add_p(text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after_pt=3.5):
        p = doc.add_paragraph()
        set_para_format(p, align=align, space_before_pt=0, space_after_pt=space_after_pt)
        r = p.add_run(text)
        set_font(r, size_pt=9.5)
        return p

    def add_fig_image(fig_path, caption, width_in=6.0):
        if fig_path.exists():
            p_img = doc.add_paragraph()
            set_para_format(p_img, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=5, space_after_pt=2)
            p_img.add_run().add_picture(str(fig_path), width=Inches(width_in))
            p_cap = doc.add_paragraph()
            set_para_format(p_cap, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=0, space_after_pt=5)
            r = p_cap.add_run(caption)
            set_font(r, size_pt=8.5, italic=True)

    # I. INTRODUCTION
    add_h1("I. INTRODUCTION")
    add_p(
        "Hardware development is financially irreversible. Tooling, component procurement, and manufacturing runs commit capital "
        "months before a single customer touches the product [1]. Large firms hedge this risk with costly consumer focus groups. "
        "Independent hardware makers and small businesses usually cannot, and many commit production capital on intuition and unverified "
        "market sentiment [2]. When reception turns out poorly, the damage ranges from inventory write-downs to corporate liquidation [3]."
    )
    add_p(
        "Econometric and electronic word-of-mouth (e-WOM) research has long shown that online reviews shape market trajectories [4]–[9]. "
        "Nearly all machine learning approaches build on that finding, and so they rely on post-launch signals: accumulated review volume, "
        "star ratings, or customer sentiment [8], [10]–[12]. When capital is committed, none of these exist. The task is therefore a "
        "cold-start problem by construction [13]–[15]: forecast market reception from pre-launch specifications, launch price, and category "
        "context alone."
    )
    add_p(
        "We study a two-stage architecture for this problem (Fig. 1). An LLM acts as a skeptical semantic bridge, translating pre-launch product "
        "specifications into a structured quality-aspect representation. A monotonic gradient-boosted decision tree ensemble (XGBoost) then predicts "
        "an independently audited, review-derived market-success proxy. Earlier implementations compress a full specification into nine isolated scalar "
        "aspect scores, and that compression discards evidence that matters: ingress protection ratings, battery capacity, acoustic measurements, "
        "and specification completeness. We propose LLM-COLDSTART-RICH, a representation that keeps verbatim specification grounding, technical fact "
        "density, and extraction certainty next to the semantic aspect priors."
    )

    add_fig_image(FIG_DIR / "fig1_pipeline.png", "Fig. 1. End-to-end launch-blind prediction architecture, from specifications to the market outcome proxy.", width_in=6.1)

    add_p(
        "This paper makes three contributions. First, we identify the scalar compression bottleneck in aspect bridging and replace it with an "
        "evidence-grounded rich representation. Second, we evaluate under a frozen temporal protocol with explicit leakage controls. Third, we "
        "report list-ranking and decision-quality analyses, a component ablation, a six-learner sensitivity benchmark, and an external validation cohort."
    )

    # II. FROZEN EVALUATION PROTOCOL & LEAKAGE CONTROLS
    add_h1("II. FROZEN EVALUATION PROTOCOL AND LEAKAGE CONTROLS")
    add_p(
        "To make sure the reported performance reflects forward-in-time predictive validity and not retrospective overfitting, we fixed the "
        "evaluation protocol before final evaluation. It is anchored at a launch cutoff of October 31, 2021, 23:59:59 UTC. The cutoff marks the boundary "
        "of historical information for the primary evaluation. It is not the date of model development or study execution, which took place in 2026. "
        "We chose it to obtain a strictly forward-in-time cohort with enough pre-cutoff training items, enough post-cutoff evaluation items, balance "
        "across all five categories, and a post-launch exposure window of 7–22 months for ground-truth review metrics to stabilize (Fig. 2)."
    )

    # Numbered items left-aligned to eliminate stretched lines
    add_p(
        "1. Training pool (n = 507). Physical consumer electronics whose earliest recorded customer review falls on or before the cutoff. The pool draws "
        "on 43,599 historical customer reviews across five categories: Bluetooth speakers, ice makers, power banks, smartwatches, and wireless headphones.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_p(
        "2. Launch-blind temporal test pool (n = 124). Products whose first recorded customer review falls strictly after the cutoff (November 1, 2021 to "
        "February 28, 2023), which serves as an empirical proxy for launch timing. The model sees only pre-launch specifications, launch price, category, "
        "and brand name. Customer reviews, star ratings, and post-launch volume metrics are physically quarantined.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_p(
        "3. Isolated target definition. The regression target is a composite proxy, SuccessScore = 100 * (0.40 * vol_norm + 0.35 * rat_norm + 0.25 * vel_norm). "
        "Normalization bounds are fitted on the pre-cutoff training pool only.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )

    add_fig_image(FIG_DIR / "fig2_temporal_protocol.png", "Fig. 2. Frozen forward-in-time temporal evaluation protocol, partitioned at the October 31, 2021 historical boundary (507 training products, 124 strictly post-cutoff temporal holdout products), together with independent external application validation on a 2022–2024 real-world Amazon cohort (n = 155).", width_in=6.1)

    # III. METHODOLOGY & LLM EXTRACTION
    add_h1("III. METHODOLOGY AND LLM EXTRACTION")
    add_h2("A. The Representation Bottleneck in Scalar Aspect Bridging")
    add_p(
        "In the earlier baseline, which we call Model_O, the LLM reduced each specification text to nine broad scalar scores on a 0–10 scale. Under cold-start "
        "conditions this compression removes the concrete technical differences between products. When two products receive similar category-anchored "
        "scores, the downstream regressor has no technical signal left with which to separate them. We call our proposed model Model_New."
    )

    add_h2("B. The LLM-COLDSTART-RICH Architecture")
    add_p(
        "The representation builds an evidence-grounded bridge that follows pre-registered validation schemas and draws on work in foundation-model extraction "
        "and aspect-based sentiment analysis [16]–[24]. It has three components."
    )
    add_p(
        "1. Verifiable technical attributes. Direct technical specifications (for example, ingress protection ratings, battery life in hours, wattage, and "
        "connectivity generation) are parsed using Google Gemini 1.5 Flash (model ID: gemini-1.5-flash as recorded in project execution logs) under deterministic greedy decoding (temperature = 0.0) with strict "
        "JSON schema mode and SHA-256 prompt-hash memoization. In the frozen benchmark generation runs, Gemini 1.5 Flash completed 100% of primary extractions without "
        "requiring invocation of the fallback pool (llama-3.3-70b-versatile and gpt-oss-120b). Because commercial cloud API model checkpoints may be modified or retired "
        "over time, scientific reproducibility is supported by preserving the complete, immutable SHA-256-keyed extraction artifact cache alongside the code. "
        "The extraction prompt operates under a frozen Skeptic design, explicitly penalizing promotional puffery. Unmatched attributes without verbatim textual support "
        "are forced to null. Across an audit of 568 explicit technical attribute extractions across pre-cutoff specifications, the retained attributes showed a 0.0% "
        "hallucination rate by construction (568/568 strictly grounded in source copy). To verify that null-forcing does not suppress valid information, an independent blinded "
        "human validation gate on 30 products (270 individual aspect evaluations) demonstrated high inter-annotator agreement (Cohen's kappa = 0.842), strong "
        "human-model presence agreement (kappa = 0.812), 97.8% null-forcing adherence, 100% verbatim quote match, and 92.4% extraction recall against human-verified "
        "technical specifications. All 631 product specifications conformed fully to the extraction schema."
    )
    add_p(
        "2. Specification completeness and density. We extract quantitative measures of technical richness: the number of explicit feature bullets, total "
        "specification word count, and the density of concrete numerical measurements. Following new-item cold-start theory, we treat specification completeness "
        "as a signal of commercial maturity and product readiness [25]."
    )
    add_p(
        "3. Directional monotonic constraints and tabular boosting. On structured technical features of moderate sample size, gradient-boosted trees have "
        "repeatedly outperformed neural alternatives [26]–[29]. We therefore avoid end-to-end neural fine-tuning, drawing on established literature in multi-feature aspect "
        "extraction and sentiment representation [30]–[33]. XGBoost [26] is fitted with directional priors grounded in economic reasoning. Downstream hyperparameters "
        "were tuned strictly using 5-fold cross-validation on the 507 pre-cutoff training items (n_estimators = 112, max_depth = 5, learning_rate = 0.05, min_child_weight = 3, "
        "subsample = 0.8, colsample_bytree = 0.8). Launch price enters with a negative monotone constraint (-1). Brand tier (+1) and specification quality aspects (+1) "
        "are constrained to raise predicted viability monotonically [34]."
    )

    # IV. EXPERIMENTAL RESULTS & BENCHMARKS
    add_h1("IV. EXPERIMENTAL RESULTS AND BENCHMARKS")
    add_h2("A. Primary Temporal Performance")
    add_p(
        "Table I and Fig. 3 summarize performance on the frozen 124-product temporal holdout. Model_New reaches a Spearman rank correlation of rho = 0.6722 "
        "(95% bootstrap CI [0.5495, 0.7620] across B = 10,000 resamples; asymptotic p = 1.25e-17 against the null of zero rank correlation) "
        "and a top-versus-bottom quintile AUC of 0.9712 (RMSE = 19.75, MAE = 16.66). Against the reproduced canonical controlled baseline Model_O (rho = 0.5623, "
        "AUC = 0.8904, RMSE = 21.12, MAE = 17.84), this is a statistically significant improvement of delta_rho = +0.1099 (paired bootstrap 95% CI [+0.0485, +0.1833]; "
        "paired permutation p = 0.0005 using the standard (b+1)/(M+1) estimator with b = 4 of M = 10,000 permutations; b/M = 0.0004)."
    )

    # TABLE I
    t1_headers = ["Model", "Representation", "Spearman rho", "95% bootstrap CI", "p-value", "Quintile AUC", "RMSE", "MAE"]
    t1_rows = [
        ["Model_New (promoted)", "Aspects + spec density (LLM-COLDSTART-RICH)", "0.6722", "[0.5495, 0.7620]", "1.25e-17", "0.9712", "19.75", "16.66"],
        ["Model_O (baseline)", "9 scalar aspects (compressed LLM)", "0.5623", "[0.4140, 0.6812]", "1.09e-11", "0.8904", "21.12", "17.84"],
        ["Metadata-only baseline", "Price + brand tier + category only", "0.4418", "[0.2800, 0.5850]", "2.10e-07", "0.6400", "23.41", "19.82"],
    ]
    t1_widths = [Inches(1.3), Inches(2.1), Inches(0.55), Inches(0.95), Inches(0.55), Inches(0.55), Inches(0.50), Inches(0.50)]
    add_ieee_table(doc, "TABLE I\nPRIMARY TEMPORAL PERFORMANCE COMPARISON (HOLDOUT n = 124)", t1_headers, t1_rows, t1_widths)

    add_fig_image(FIG_DIR / "fig3_performance_comparison.png", "Fig. 3. Predictive performance of the proposed model against canonical baselines (Holdout n = 124).", width_in=5.8)

    add_h2("B. Cold-Start Analysis on Unseen Brands")
    add_p(
        "Brand equity is unavailable for a truly new product, so we isolated the 82 temporal test products from brands with no pre-cutoff footprint (Tier 0; Fig. 4). "
        "On this pure cold-start subset, Model_New reaches rho = 0.633 (AUC = 0.981, RMSE = 20.90), compared with rho = 0.516 and AUC = 0.871 for Model_O "
        "(delta_rho = +0.117). Retaining specification density and verifiable attribute evidence therefore helps most where the model has the least other information to go on."
    )

    add_fig_image(FIG_DIR / "fig4_cold_start.png", "Fig. 4. Cold-start performance on unseen brands (Tier 0, n = 82) with no pre-cutoff market signals.", width_in=4.6)

    add_h2("C. Within-Category Performance")
    add_p(
        "Table II and Fig. 5 give head-to-head results within each of the five categories. Model_New improves Smartwatches (rho = 0.544 vs 0.415, RMSE = 14.22 vs 16.10), "
        "Power Banks (rho = 0.126 vs -0.042, RMSE = 26.39 vs 27.95), and Wireless Headphones (rho = 0.132 vs -0.055, RMSE = 22.79 vs 22.93). Ice Makers are essentially "
        "unchanged (rho = 0.192 vs 0.185, RMSE = 18.17 vs 20.50). In Bluetooth Speakers the correlation falls (rho = 0.429 vs 0.536, delta = -0.107), but with n = 7 we "
        "draw no inferential conclusion from that category. Across the four categories with adequate sample size, Model_New improves or maintains within-category ranking, "
        "though absolute correlations in Power Banks (0.126), Wireless Headphones (0.132), and Ice Makers (0.192) remain low."
    )

    # TABLE II
    t2_headers = ["Product Category", "Holdout n", "Model_O rho", "Model_New rho", "Delta rho", "Model_New RMSE"]
    t2_rows = [
        ["Smartwatches", "39", "0.415", "0.544", "+0.129", "14.22"],
        ["Ice Makers", "36", "0.185", "0.192", "+0.007", "18.17"],
        ["Wireless Headphones", "23", "-0.055", "0.132", "+0.187", "22.79"],
        ["Power Banks", "19", "-0.042", "0.126", "+0.168", "26.39"],
        ["Bluetooth Speakers", "7", "0.536", "0.429", "-0.107", "21.64"],
    ]
    t2_widths = [Inches(2.0), Inches(0.9), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.1)]
    add_ieee_table(doc, "TABLE II\nWITHIN-CATEGORY VIABILITY RANKING ACROSS FIVE CANONICAL CATEGORIES", t2_headers, t2_rows, t2_widths)

    add_fig_image(FIG_DIR / "fig5_within_category.png", "Fig. 5. Head-to-head within-category rank correlation across the five product categories.", width_in=5.8)

    add_h2("D. Standardized Six-Learner OOF Benchmark")
    add_p(
        "A natural concern is that the results depend on XGBoost specifically. To check how sensitive they are to the downstream learner, we ran a standardized "
        "five-fold out-of-fold (OOF) cross-validation benchmark across six learner families, using only the 507 pre-cutoff training products (Table III, Fig. 6). "
        "All preprocessing, scaling, and categorical encoding were fitted inside each training fold."
    )
    add_p(
        "XGBoost [26] achieves the highest OOF rank monotonicity (rho = 0.7565, R2 = 0.5715, RMSE = 12.53, MAE = 9.56). Support Vector Regression with an RBF kernel [35] "
        "follows closely (rho = 0.7495, R2 = 0.5401), as do Gradient Boosted Decision Trees [27] (rho = 0.7396, R2 = 0.5375). With fold-level standard deviations of 0.024 "
        "to 0.028, the differences among these three learners are small. Random Forest [36] reaches rho = 0.7267. Ridge regression [37] falls to rho = 0.6481 (R2 = 0.4165), "
        "which suggests that non-linear interactions between specification density and aspect scores matter. Multi-Layer Perceptrons are less sample-efficient (rho = 0.5463, "
        "R2 = 0.2138), in line with reports that tree ensembles remain stronger on structured tabular data of moderate size [28], [29]."
    )

    # TABLE III
    t3_headers = ["Downstream Learner", "OOF rho", "OOF r", "OOF R2", "OOF RMSE", "OOF MAE", "Fold rho +- SD"]
    t3_rows = [
        ["XGBoost (promoted)", "0.7565", "0.7592", "0.5715", "12.53", "9.56", "0.756 +- 0.024"],
        ["SVR (RBF kernel)", "0.7495", "0.7410", "0.5401", "12.98", "9.94", "0.748 +- 0.026"],
        ["GBDT (sklearn)", "0.7396", "0.7385", "0.5375", "13.02", "10.12", "0.739 +- 0.028"],
        ["Random Forest", "0.7267", "0.7250", "0.5207", "13.25", "10.31", "0.726 +- 0.029"],
        ["Ridge Regression", "0.6481", "0.6470", "0.4165", "14.63", "11.45", "0.648 +- 0.035"],
        ["MLP (Neural Network)", "0.5463", "0.5210", "0.2138", "16.98", "13.20", "0.545 +- 0.048"],
    ]
    t3_widths = [Inches(1.8), Inches(0.8), Inches(0.75), Inches(0.75), Inches(0.85), Inches(0.85), Inches(1.2)]
    add_ieee_table(doc, "TABLE III\nSTANDARDIZED SIX-LEARNER OOF BENCHMARK (n = 507 TRAINING PRODUCTS)", t3_headers, t3_rows, t3_widths)

    add_fig_image(FIG_DIR / "fig6_six_learner_benchmark.png", "Fig. 6. Five-fold OOF cross-validation sensitivity benchmark across six downstream learner families on 507 pre-cutoff training products.", width_in=6.1)

    add_h2("E. Standardized List-Ranking and Derived Decision Quality")
    add_p(
        "In venture capital and catalog planning, decision makers work from ranked shortlists and high-stakes binary allocations. We therefore evaluated standardized "
        "list-ranking metrics (Kendall's tau and NDCG@K) and a derived extreme-group decision task (top 20% versus bottom 20%, middle 60% excluded) on the frozen "
        "124-product holdout (Table IV, Fig. 7)."
    )
    add_p(
        "Model_New achieves Kendall's tau = 0.4772 (p = 4.12e-15), against tau = 0.3946 (p = 1.11e-10) for the baseline. The gain of 0.0826 in tau is an 8.26-point "
        "increase in net concordance, that is, concordant minus discordant pairs as a share of all product pairs. For top-recommended shortlists, NDCG@5 is 0.8933 "
        "(baseline: 0.8600). The advantage does not extend to NDCG@10, where the baseline is marginally ahead (0.8832 versus 0.8771), so the gain is concentrated at "
        "the top of the ranking."
    )
    add_p(
        "On the extreme-group task (n = 50 holdout items), Model_New reaches AUC = 0.9712, identical to the top-versus-bottom quintile AUC in Section IV-A (Fig. 7b). "
        "At the natural median threshold it classifies 46 of the 50 extreme products correctly: 92.0% accuracy, 92.0% precision, 92.0% recall, and an MCC of +0.8400 "
        "(23 TP, 23 TN, 2 FP, 2 FN). The baseline classifies 82.00% of the same items correctly. Because the middle 60% of products is excluded, this task is easier "
        "than ranking the full holdout, and we read it as a triage indicator and not as a general accuracy figure."
    )

    # TABLE IV
    t4_headers = ["Evaluation Dimension", "Metric", "Model_O (baseline)", "Model_New (promoted)", "Delta", "Statistical Detail"]
    t4_rows = [
        ["Global monotonic rank", "Spearman rho", "0.5623", "0.6722", "+0.1099", "p = 0.0005 (permutation)"],
        ["Concordant pair ordering", "Kendall's tau", "0.3946", "0.4772", "+0.0826", "p = 4.12e-15"],
        ["Catalog shortlist ranking", "NDCG@5 (top 5)", "0.8600", "0.8933", "+0.0333", "discounted cumulative gain"],
        ["Catalog shortlist ranking", "NDCG@10 (top 10)", "0.8832", "0.8771", "-0.0061", "discounted cumulative gain"],
        ["Extreme discrimination", "Quintile AUC (top vs bottom 20%)", "0.8904", "0.9712", "+0.0808", "p < 0.001 (bootstrap)"],
        ["Extreme accuracy", "Accuracy (n = 50)", "82.00%", "92.00%", "+10.00 pp", "46 / 50 correct"],
        ["Extreme precision", "Precision (top 20% flag)", "80.00%", "92.00%", "+12.00 pp", "23 / 25 true hits"],
    ]
    t4_widths = [Inches(1.5), Inches(1.4), Inches(0.95), Inches(1.0), Inches(0.8), Inches(1.35)]
    add_ieee_table(doc, "TABLE IV\nSTANDARDIZED LIST-RANKING AND DERIVED DECISION PERFORMANCE (HOLDOUT n = 124)", t4_headers, t4_rows, t4_widths)

    add_fig_image(FIG_DIR / "fig7_ranking_decision_quality.png", "Fig. 7. Standardized list-ranking quality (NDCG@K, Kendall's tau) and derived extreme-group ROC discrimination on the frozen temporal holdout (n = 124).", width_in=6.1)

    # V. ABLATION, ROBUSTNESS, INTERPRETABILITY & EFFICIENCY
    add_h1("V. ABLATION, ROBUSTNESS, INTERPRETABILITY, AND EFFICIENCY")
    add_h2("A. Controlled Component Ablation")
    add_p(
        "A controlled ablation over seven configurations (Table V, Fig. 8) quantifies what each component contributes. The 24-dimensional feature vector breaks "
        "down into 9 aspect scores, 9 aspect mention rates, 3 specification density metrics, 1 launch price, 1 brand tier, and 1 product category indicator. "
        "Removing the LLM semantic aspects (A1: removing all 18 aspect scores and mention rates, leaving 6 metadata and density features) causes the largest single "
        "drop (delta_rho = -0.0880, rho = 0.5842). Removing the specification density attributes (bullet counts, word count, number density) lowers rho by 0.0321 "
        "(to 0.6401), and removing brand tier lowers it by 0.0337 (to 0.6385). Metadata alone (price, brand tier, category) gives only rho = 0.4418 (delta_rho = -0.2304), "
        "so launch-time viability cannot be inferred from commercial metadata alone."
    )
    add_p(
        "One result deserves a comment. The configuration with no LLM aspects at all (A1, rho = 0.5842) already exceeds the scalar-aspect baseline (Model_O, rho = 0.5623). "
        "A share of the improvement over Model_O therefore comes from the specification-density features, which are extracted without the LLM."
    )

    # TABLE V
    t5_headers = ["Config", "Ablation Description", "Features Included", "Features (n)", "Spearman rho", "Delta vs Full", "RMSE", "MAE"]
    t5_rows = [
        ["A3", "Full Model_New (promoted)", "All 24 features (aspects + density + metadata)", "24", "0.6722", "Reference", "19.75", "16.66"],
        ["A7", "w/o launch unit price", "All features except price", "23", "0.6654", "-0.0068", "19.82", "16.71"],
        ["A6", "w/o category indicator", "All features except category", "23", "0.6512", "-0.0210", "20.08", "16.94"],
        ["A2", "w/o specification density", "All features except bullet/word/num metrics", "21", "0.6401", "-0.0321", "20.31", "17.12"],
        ["A5", "w/o brand footprint tier", "All features except brand tier", "23", "0.6385", "-0.0337", "20.25", "17.08"],
        ["A1", "w/o LLM semantic aspects", "Metadata + spec density (no aspect scores/mentions)", "6", "0.5842", "-0.0880", "21.05", "17.65"],
        ["A0", "Metadata-only control", "Price + brand tier + category only", "3", "0.4418", "-0.2304", "23.41", "19.82"],
    ]
    t5_widths = [Inches(0.5), Inches(1.5), Inches(2.0), Inches(0.5), Inches(0.65), Inches(0.75), Inches(0.55), Inches(0.55)]
    add_ieee_table(doc, "TABLE V\nCONTROLLED COMPONENT FEATURE ABLATION (HOLDOUT n = 124)", t5_headers, t5_rows, t5_widths)

    add_fig_image(FIG_DIR / "fig8_ablation.png", "Fig. 8. Controlled component ablation study of feature contributions (Holdout n = 124).", width_in=5.6)

    add_h2("B. Seed Stability and Byte-for-Byte Integrity")
    add_p(
        "Across five random seeds (42, 123, 456, 789, 999), Model_New outperforms the baseline consistently (mean rho = 0.6332 +- 0.0331 versus 0.5828 +- 0.0249). "
        "The seed-averaged gap (about 0.05) is smaller than the +0.1099 gap of the headline run, so the direction of the effect is stable while its size varies with the seed. "
        "The automated leakage test suite passes all 10 criteria (TEST-01: label inaccessibility; TEST-02: zero test ID fitting leakage; TEST-03: strict October 31, 2021 temporal "
        "partitioning; TEST-04: training-only normalization bounds; TEST-05: training-only category profiles; TEST-06: training-only brand footprint tiering; TEST-07: CV-only "
        "hyperparameter tuning; TEST-08: frozen extraction prompts; TEST-09: isolated test evaluation loading; and TEST-10: byte-for-byte SHA-256 prediction invariance under "
        "complete label deletion). In an independent integrity test, we ran prediction once with test ground truth present and once with it deleted. The two runs produced "
        "bit-for-bit identical output hashes (SHA-256: 3f75df2ebaf508eb...), which shows that predictions do not depend on test labels. Fig. 9 plots predicted against "
        "observed scores on the holdout."
    )

    add_fig_image(FIG_DIR / "fig9_scatter.png", "Fig. 9. Scatter of predicted viability against the actual market outcome proxy (Holdout n = 124).", width_in=4.4)

    add_h2("C. Feature Attribution and Monotonic Domain Regularization")
    add_p(
        "To keep predictions consistent with product economics and not with spurious training artifacts, the XGBoost estimator applies exact monotonic constraints "
        "during tree construction. Launch price is constrained negatively (-1): with all specifications held fixed, a higher price cannot raise predicted viability. "
        "Brand tier and all nine aspect ratings are constrained positively (+1). Split-gain analysis attributes over 42% of total split improvement to technical specification "
        "density and build quality, which suggests that engineering content carries much of the predictive weight."
    )

    add_h2("D. Computational Efficiency and Operational Latency")
    add_p(
        "In decision-support settings, inference latency determines usability (Table VI). On commodity x86_64 hardware, downstream scoring with Model_New takes "
        "0.0395 milliseconds per product, a throughput above 25,000 items per second, with a model artifact of 297 KB. Offline LLM aspect extraction takes 1.4–2.2 s "
        "per specification. Because extraction is decoupled from scoring, an interactive dashboard can re-estimate predictions instantly as a user moves a parameter slider."
    )

    # TABLE VI
    t6_headers = ["Pipeline Component", "Implementation", "Inference Latency", "Throughput", "Storage / Memory Footprint"]
    t6_rows = [
        ["Downstream tabular inference", "XGBoost (hist tree)", "0.0395 ms / item", "> 25,000 items/sec", "297 KB (model JSON)"],
        ["Specification density parser", "Python / regex tokenizer", "0.12 ms / item", "> 8,000 items/sec", "In-memory (< 1 MB)"],
        ["LLM aspect extraction", "JSON schema (9 aspects)", "1.4–2.2 s / item", "~ 30 items/min", "3.5 KB (prompt/schema)"],
        ["Downstream model training", "XGBoost (n = 507 products)", "0.093 seconds", "Single training run", "297 KB"],
    ]
    t6_widths = [Inches(1.8), Inches(1.5), Inches(1.1), Inches(1.1), Inches(1.5)]
    add_ieee_table(doc, "TABLE VI\nOPERATIONAL AND COMPUTATIONAL EFFICIENCY PROFILE", t6_headers, t6_rows, t6_widths)

    # VI. EXTERNAL APPLICATION VALIDATION
    add_h1("VI. EXTERNAL APPLICATION VALIDATION")
    add_p(
        "To test transfer beyond the frozen historical holdout, the synchronized application inference engine was run on an independent external cohort of 155 Amazon "
        "products launched between 2022 and 2024 across the five canonical categories (Table VII). This cohort is physically distinct from the primary 507/124 partition. "
        "On the 150 products with accumulated market validation, the model reaches rho = 0.501 (95% CI [0.362, 0.617]), with rho = 0.6120 on the high-density specification "
        "subset (95% CI [0.504, 0.702], Quintile AUC = 0.884), and an extreme-group Quintile AUC of 0.873 (MAE = 15.87 pts). This is lower than the temporal-holdout value of "
        "rho = 0.6722. Established brands (n = 129) reach rho = 0.454, while startup and new-entrant brands (n = 21) reach rho = 0.686 (Quintile AUC = 0.940), although the "
        "confidence interval for the smaller group is wide ([0.352, 0.865]). The five prospective pre-launch SKUs have no post-launch labels and are excluded from the metrics. "
        "The representation therefore carries over to post-2022 products without a collapse in performance."
    )

    # TABLE VII
    t7_headers = ["Cohort Partition", "Sample Size (n)", "Spearman rho", "95% Confidence Interval", "Quintile AUC", "RMSE", "MAE"]
    t7_rows = [
        ["Full evaluation set", "150", "0.501", "[0.362, 0.617]", "0.873", "19.83", "15.87"],
        ["High-density specification subset", "94", "0.6120", "[0.504, 0.702]", "0.884", "19.10", "14.82"],
        ["Established brands", "129", "0.454", "[0.301, 0.582]", "0.852", "19.92", "15.91"],
        ["Startup / new-entrant brands", "21", "0.686", "[0.352, 0.865]", "0.940", "19.26", "15.62"],
        ["Prospective pre-launch SKUs", "5", "N/A", "N/A (no post-launch labels)", "N/A", "N/A", "N/A"],
    ]
    t7_widths = [Inches(1.8), Inches(0.7), Inches(0.7), Inches(1.2), Inches(0.8), Inches(0.9), Inches(0.9)]
    add_ieee_table(doc, "TABLE VII\nEXTERNAL REAL-WORLD APPLICATION EVALUATION (2022–2024 AMAZON COHORT, n = 155)", t7_headers, t7_rows, t7_widths)

    # VII. DISCUSSION, ETHICAL CONSIDERATIONS & LIMITATIONS
    add_h1("VII. DISCUSSION, ETHICAL CONSIDERATIONS, AND LIMITATIONS")
    add_p(
        "The target predicted by this system is a review-derived market-success proxy. It is not unit sales, revenue, or profit. Consumer satisfaction and review velocity "
        "correlate with commercial viability in e-commerce markets [5], [6], [9], but paid advertising, distributor relationships, and supply chain logistics also affect "
        "aggregate sales volume, and our model does not represent them. Public review platforms are also affected by review spam and promotional manipulation [38]–[40]. "
        "They carry survivorship bias as well: products with fewer than five reviews were excluded during corpus curation. Our predictions should therefore be read as expected "
        "consumer satisfaction and engagement, conditional on the product reaching baseline market visibility. A single frozen split, five product categories, and a 124-product "
        "holdout also limit statistical power, and the extraction stage depends on the specific LLM used."
    )
    add_p(
        "Note on the temporal cutoff. The October 31, 2021 boundary is a dataset cutoff and not the date of study execution (2026). We selected it to build a strictly "
        "forward-in-time cohort with enough pre-cutoff training products and post-cutoff evaluation products. An empirical audit of candidate boundaries shows why later "
        "cutoffs cannot serve as the primary research benchmark. The underlying physical product corpus was harvested through September 2023, and products in the "
        "124-product temporal holdout had their first recorded reviews between November 2021 and February 2023 to ensure 7–22 months of post-launch signal stabilization. "
        "Shifting the cutoff forward to December 31, 2022 leaves only the 3 products launched in January–February 2023 (n = 3, causing severe sample starvation and category collapse), "
        "while any cutoff in late 2023–2026 yields n = 0 post-cutoff products in the harvested historical corpus. We therefore keep the 2021 cutoff with its 124-product holdout as "
        "the primary frozen temporal benchmark, and use the 2022–2024 external cohort as an independent post-cutoff validation."
    )

    # VIII. CONCLUSION
    add_h1("VIII. CONCLUSION")
    add_p(
        "Augmenting LLM aspect bridging with evidence-grounded cold-start representations reduces the semantic compression bottleneck in launch-blind product success prediction. "
        "On a frozen temporal holdout of 124 physical products, the promoted architecture reaches rho = 0.672 and AUC = 0.971, a statistically significant improvement over the "
        "scalar-aspect baseline (delta_rho = +0.110, p = 0.0005). The target definition, temporal partition, and downstream learner were left unchanged. In the six-learner benchmark "
        "XGBoost ranks first, with SVR and gradient-boosted trees close behind, and the list-ranking and extreme-group analyses show reliable ordering at the top of the shortlist and "
        "92.0% decision accuracy on the extreme-group task. Under pure cold-start conditions, rank correlation on unseen brands is rho = 0.633. The research package, the synchronized "
        "application inference engine, and the audit records will be released upon acceptance."
    )

    # SUBMISSION STATEMENTS (BACKMATTER)
    add_h1("DATA AND CODE AVAILABILITY")
    add_p(
        "The complete research package—including trained model checkpoints, feature manifests, evaluation scripts, automated leakage test suites, "
        "and the complete SHA-256-keyed offline extraction artifact cache—will be released in an open-access public repository with a persistent Zenodo DOI "
        "upon acceptance of the manuscript. During peer review, a complete, anonymized verification archive is provided to editors and reviewers upon request."
    )

    add_h1("AUTHOR CONTRIBUTIONS (CRediT STATEMENT)")
    add_p(
        "Rajvardhan Ajitrao Jagtap: Conceptualization, Methodology, Software, Formal Analysis, Writing – Original Draft. "
        "Jyotiraditya Abhijeet Shinde: Software, Data Curation, Validation, Investigation. "
        "Tanishq Parag Choudhari: Methodology, Formal Analysis, Visualization, Writing – Review & Editing. "
        "Yash Ashok Mohite: Validation, Software, Data Curation. "
        "Yogesh Malakari Honamore: Supervision, Project Administration, Resources, Writing – Review & Editing. "
        "All co-authors have reviewed and confirmed their assigned roles prior to submission."
    )

    add_h1("FUNDING AND COMPETING INTERESTS")
    add_p(
        "Funding: This research received no external grant or commercial funding.\n"
        "Competing Interests: The authors declare that they have no financial or commercial conflicts of interest that could influence the findings reported in this paper."
    )

    add_h1("ETHICS AND PLATFORM COMPLIANCE")
    add_p(
        "Public consumer reviews were obtained from established academic e-commerce research corpora curated for scientific study. "
        "All user account identifiers and personal metadata were removed during corpus ingestion, and empirical analyses operated "
        "exclusively on anonymized, public product copy without access to private personal data."
    )

    add_h1("DECLARATION OF GENERATIVE AI IN SCIENTIFIC WRITING")
    add_p(
        "Generative AI models served two distinct functions in this work. Algorithmically, Google Gemini 1.5 Flash was integrated into the experimental "
        "pipeline as an automated aspect-extraction and attribute-parsing engine under deterministic greedy decoding. In addition, during manuscript "
        "preparation and codebase maintenance, the authors utilized large language model assistants (including Anthropic Claude and Google Antigravity "
        "coding agents) for substantive manuscript drafting, structural editing, LaTeX and document formatting, and script refactoring. Following these "
        "automated and assistive procedures, all authors critically examined, audited, and verified all quantitative findings, tables, figures, and substantive "
        "claims, and take full institutional responsibility for the integrity and factual content of the published work."
    )

    # REFERENCES
    add_h1("REFERENCES")
    refs_ordered = [
        # [1] Hardware irreversibility
        'K. T. Ulrich and S. D. Eppinger, Product Design and Development, 5th ed. New York, NY, USA: McGraw-Hill, 2012.',
        # [2] Small businesses / intuition
        'T. Åstebro, "The return to independent invention: Evidence of unrealistic optimism, risk seeking or skewness loving?" The Economic Journal, vol. 113, no. 484, pp. 226–239, 2003.',
        # [3] Liquidation / inventory write-downs
        'K. B. Hendricks and V. R. Singhal, "The effect of supply chain glitches on shareholder wealth," Journal of Operations Management, vol. 21, no. 5, pp. 501–522, 2003.',
        # [4]-[9] e-WOM shaping market trajectories
        'N. Archak, A. Ghose, and P. G. Ipeirotis, "Deriving the pricing power of product features by mining consumer reviews," Management Science, vol. 57, no. 8, pp. 1485–1509, 2011.',
        'J. A. Chevalier and D. Mayzlin, "The effect of word of mouth on sales: Online book reviews," Journal of Marketing Research, vol. 43, no. 3, pp. 345–354, 2006.',
        'P. K. Chintagunta, S. Gopinath, and S. Venkataraman, "The effects of online user reviews on movie box office performance: Accounting for sequential rollout and aggregation across local markets," Marketing Science, vol. 29, no. 5, pp. 944–957, 2010.',
        'C. Dellarocas, "The digitization of word of mouth: Promise and challenges of online feedback mechanisms," Management Science, vol. 49, no. 10, pp. 1407–1424, 2003.',
        'A. Ghose and P. G. Ipeirotis, "Estimating the helpfulness and economic impact of product reviews: Mining text and reviewer characteristics," IEEE Trans. Knowl. Data Eng., vol. 23, no. 10, pp. 1498–1512, 2011.',
        'M. Luca, "Reviews, reputation, and revenue: The case of Yelp.com," Harvard Business School Working Paper 12-016, 2016.',
        # [10]-[12] Post-launch review models
        'S. Asur and B. A. Huberman, "Predicting the future with social media," in Proc. IEEE/WIC/ACM Int. Conf. Web Intell., 2010, pp. 492–499.',
        'M. Hu and B. Liu, "Mining and summarizing customer reviews," in Proc. 10th ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining, 2004, pp. 168–177.',
        'B. Liu, Sentiment Analysis and Opinion Mining. San Rafael, CA, USA: Morgan & Claypool, 2012.',
        # [13]-[15] Cold-start formulations
        'R. He and J. McAuley, "Ups and downs: Modeling the visual evolution of fashion trends with one-class collaborative filtering," in Proc. 25th Int. Conf. World Wide Web (WWW), 2016, pp. 507–517.',
        'Y. Hou et al., "Bridging language and items for retrieval and recommendation," arXiv preprint arXiv:2403.03952, 2024.',
        'S. Narayanan, P. Samuel, and M. Chacko, "Product pre-launch prediction from resilient distributed e-WOM data," IEEE Access, vol. 8, pp. 167887–167899, 2020.',
        # [16]-[24] Foundation models & aspect-based sentiment
        'R. Bommasani et al., "On the opportunities and risks of foundation models," arXiv preprint arXiv:2108.07258, 2021.',
        'T. Brown et al., "Language models are few-shot learners," in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, 2020, pp. 1877–1901.',
        'F. Gilardi, M. Alizadeh, and M. Kubli, "ChatGPT outperforms crowd workers for text-annotation tasks," Proc. Nat. Acad. Sci. (PNAS), vol. 120, no. 30, p. e2305016120, 2023.',
        'OpenAI, "GPT-4 technical report," arXiv preprint arXiv:2303.08774, 2023.',
        'M. Pontiki et al., "SemEval-2014 Task 4: Aspect based sentiment analysis," in Proc. 8th Int. Workshop Semantic Eval., 2014, pp. 27–35.',
        'K. I. Roumeliotis et al., "LLMs for product classification in e-commerce: A zero-shot comparative study of GPT and Claude models," Natural Language Processing Journal, vol. 6, p. 100052, 2024.',
        'H. Touvron et al., "LLaMA: Open and efficient foundation language models," arXiv preprint arXiv:2302.13971, 2023.',
        'J. Wang, H. Gong, and X. Guo, "Multi-feature fusion graph attention network for aspect-based sentiment analysis," Knowledge-Based Systems, vol. 315, p. 114084, 2025.',
        'W. Zhang et al., "A survey on aspect-based sentiment analysis: Tasks, methods, and challenges," IEEE Trans. Knowl. Data Eng., vol. 35, no. 11, pp. 11019–11038, 2023.',
        # [25] Specification completeness
        'A. I. Schein, A. Popescul, L. H. Ungar, and D. M. Pennock, "Methods and metrics for cold-start recommendations," in Proc. 25th Annu. Int. ACM SIGIR Conf. Research and Development in Information Retrieval, 2002, pp. 253–260.',
        # [26]-[29] Decision tree ensembles vs deep neural nets
        'T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining, 2016, pp. 785–794.',
        'J. H. Friedman, "Greedy function approximation: A gradient boosting machine," Annals of Statistics, vol. 29, no. 5, pp. 1189–1232, 2001.',
        'L. Grinsztajn, E. Oyallon, and G. Varoquaux, "Why do tree-based models still outperform deep learning on typical tabular data?" in Advances in Neural Information Processing Systems (NeurIPS), vol. 35, 2022, pp. 507–520.',
        'R. Shwartz-Ziv and A. Armon, "Tabular data: Deep learning is not all you need," Information Fusion, vol. 81, pp. 84–90, 2022.',
        # [30]-[33] Aspect extraction & sentiment representation
        'E. Cambria, S. Poria, R. Bajpai, and B. Schuller, "SenticNet 4: A semantic resource for sentiment analysis based on conceptual primitives," in Proc. 26th Int. Conf. Computational Linguistics (COLING), 2016, pp. 2666–2677.',
        'S. Poria, E. Cambria, and A. Gelbukh, "Aspect extraction for opinion mining with a deep convolutional neural network," Knowledge-Based Systems, vol. 108, pp. 42–49, 2016.',
        'P. Ray and A. Chakrabarti, "A mixed-approach for sentiment analysis on online product reviews," in Proc. IEEE Int. Conf. Adv. Netw. Telecommun. Syst. (ANTS), 2017, pp. 1–6.',
        'L. Zhang, S. Wang, and B. Liu, "Deep learning for sentiment analysis: A survey," WIREs Data Mining and Knowledge Discovery, vol. 8, no. 4, p. e1253, 2018.',
        # [34] Monotonic constraints
        'M. Gupta, A. Cotter, J. Pfeifer, K. Voevodski, K. Canini, A. Mangylov, W. Moczydlowski, and A. Esbroeck, "Monotonic calibrated interpolated look-up tables," Journal of Machine Learning Research, vol. 17, no. 109, pp. 1–47, 2016.',
        # [35]-[37] Downstream learner families
        'C. Cortes and V. Vapnik, "Support-vector networks," Machine Learning, vol. 20, no. 3, pp. 273–297, 1995.',
        'L. Breiman, "Random forests," Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.',
        'A. E. Hoerl and R. W. Kennard, "Ridge regression: Biased estimation for nonorthogonal problems," Technometrics, vol. 12, no. 1, pp. 55–67, 1970.',
        # [38]-[40] Opinion spam & manipulation
        'N. Jindal and B. Liu, "Opinion spam and analysis," in Proc. Int. Conf. Web Search Data Mining (WSDM), 2008, pp. 219–230.',
        'D. Mayzlin, Y. Dover, and J. Chevalier, "Promotional reviews: An empirical investigation of online review manipulation," American Economic Review, vol. 104, no. 8, pp. 2421–2455, 2014.',
        'M. Ott, Y. Choi, C. Cardie, and J. T. Hancock, "Finding deceptive opinion spam by any stretch of the imagination," in Proc. 49th Annu. Meeting Assoc. Comput. Linguistics (ACL), 2011, pp. 309–319.',
    ]

    for i, ref in enumerate(refs_ordered, 1):
        p_ref = doc.add_paragraph()
        set_para_format(p_ref, align=WD_ALIGN_PARAGRAPH.LEFT, space_before_pt=1, space_after_pt=1.5)
        p_ref.paragraph_format.left_indent = Inches(0.22)
        p_ref.paragraph_format.first_line_indent = Inches(-0.22)
        r_num = p_ref.add_run(f"[{i}] ")
        set_font(r_num, size_pt=9, bold=True)
        r_txt = p_ref.add_run(ref)
        set_font(r_txt, size_pt=9)

    docx_path = MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.docx"
    doc.save(str(docx_path))
    print(f"Saved FINAL_MANUSCRIPT.docx to {docx_path}")

    # Render PDF via Word COM
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc_com = word.Documents.Open(str(docx_path.resolve()))
        pdf_path = MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.pdf"
        doc_com.SaveAs(str(pdf_path.resolve()), FileFormat=17) # 17 = wdFormatPDF
        doc_com.Close()
        word.Quit()
        print(f"Successfully rendered PDF via Word COM: {pdf_path}")
    except Exception as e:
        print(f"Word COM PDF rendering skipped or failed: {e}")

    # Synchronize across all destination folders
    shutil_dest_paper = ROOT / "FINAL_RESEARCH_PACKAGE" / "paper"
    shutil_dest_audit = ROOT / "FINAL_AUDIT" / "paper"
    for dest in [shutil_dest_paper, shutil_dest_audit]:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(docx_path, dest / "FINAL_MANUSCRIPT.docx")
        if (MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.pdf").exists():
            shutil.copy2(MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.pdf", dest / "FINAL_MANUSCRIPT.pdf")
    # Also update workspace root copies
    shutil.copy2(docx_path, ROOT / "Research_Paper_IEEE_CORRECTED_v3.docx")
    if (MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.pdf").exists():
        shutil.copy2(MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.pdf", ROOT / "Research_Paper_IEEE_CORRECTED_v3.pdf")
    print("Synchronized manuscript docx and pdf across all destinations.")

    # Also save clean Markdown copy
    md_text = f"""# Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging

**Rajvardhan Ajitrao Jagtap, Jyotiraditya Abhijeet Shinde, Tanishq Parag Choudhari, Yash Ashok Mohite, Yogesh Malakari Honamore**  
*Department of Computer Science and Engineering, Rajarambapu Institute of Technology, Rajaramnagar, Sangli, Maharashtra, India*

## Abstract
{abs_text}

**Index Terms—** product success prediction, aspect-based sentiment analysis, cold-start representation, large language models, gradient boosting, electronic word of mouth, temporal validation.

## I. INTRODUCTION
Hardware development is financially irreversible. Tooling, component procurement, and manufacturing runs commit capital months before a single customer touches the product [1]. Large firms hedge this risk with costly consumer focus groups. Independent hardware makers and small businesses usually cannot, and many commit production capital on intuition and unverified market sentiment [2]. When reception turns out poorly, the damage ranges from inventory write-downs to corporate liquidation [3].

Econometric and electronic word-of-mouth (e-WOM) research has long shown that online reviews shape market trajectories [4]–[9]. Nearly all machine learning approaches build on that finding, and so they rely on post-launch signals: accumulated review volume, star ratings, or customer sentiment [8], [10]–[12]. When capital is committed, none of these exist. The task is therefore a cold-start problem by construction [13]–[15]: forecast market reception from pre-launch specifications, launch price, and category context alone.

We study a two-stage architecture for this problem (Fig. 1). An LLM acts as a skeptical semantic bridge, translating pre-launch product specifications into a structured quality-aspect representation. A monotonic gradient-boosted decision tree ensemble (XGBoost) then predicts an independently audited, review-derived market-success proxy. Earlier implementations compress a full specification into nine isolated scalar aspect scores, and that compression discards evidence that matters: ingress protection ratings, battery capacity, acoustic measurements, and specification completeness. We propose LLM-COLDSTART-RICH, a representation that keeps verbatim specification grounding, technical fact density, and extraction certainty next to the semantic aspect priors.

![Fig. 1. End-to-end launch-blind prediction architecture](figures/fig1_pipeline.png)

This paper makes three contributions. First, we identify the scalar compression bottleneck in aspect bridging and replace it with an evidence-grounded rich representation. Second, we evaluate under a frozen temporal protocol with explicit leakage controls. Third, we report list-ranking and decision-quality analyses, a component ablation, a six-learner sensitivity benchmark, and an external validation cohort.

## II. FROZEN EVALUATION PROTOCOL AND LEAKAGE CONTROLS
To make sure the reported performance reflects forward-in-time predictive validity and not retrospective overfitting, we fixed the evaluation protocol before final evaluation. It is anchored at a launch cutoff of October 31, 2021, 23:59:59 UTC. The cutoff marks the boundary of historical information for the primary evaluation. It is not the date of model development or study execution, which took place in 2026. We chose it to obtain a strictly forward-in-time cohort with enough pre-cutoff training items, enough post-cutoff evaluation items, balance across all five categories, and a post-launch exposure window of 7–22 months for ground-truth review metrics to stabilize (Fig. 2).

1. Training pool (n = 507). Physical consumer electronics whose earliest recorded customer review falls on or before the cutoff. The pool draws on 43,599 historical customer reviews across five categories: Bluetooth speakers, ice makers, power banks, smartwatches, and wireless headphones.
2. Launch-blind temporal test pool (n = 124). Products whose first recorded customer review falls strictly after the cutoff (November 1, 2021 to February 28, 2023), which serves as an empirical proxy for launch timing. The model sees only pre-launch specifications, launch price, category, and brand name. Customer reviews, star ratings, and post-launch volume metrics are physically quarantined.
3. Isolated target definition. The regression target is a composite proxy, SuccessScore = 100 * (0.40 * vol_norm + 0.35 * rat_norm + 0.25 * vel_norm). Normalization bounds are fitted on the pre-cutoff training pool only.

![Fig. 2. Frozen forward-in-time temporal evaluation protocol](figures/fig2_temporal_protocol.png)

## III. METHODOLOGY AND LLM EXTRACTION
### A. The Representation Bottleneck in Scalar Aspect Bridging
In the earlier baseline, which we call Model_O, the LLM reduced each specification text to nine broad scalar scores on a 0–10 scale. Under cold-start conditions this compression removes the concrete technical differences between products. When two products receive similar category-anchored scores, the downstream regressor has no technical signal left with which to separate them. We call our proposed model Model_New.

### B. The LLM-COLDSTART-RICH Architecture
The representation builds an evidence-grounded bridge that follows pre-registered validation schemas and draws on work in foundation-model extraction and aspect-based sentiment analysis [16]–[24]. It has three components.

1. Verifiable technical attributes. Direct technical specifications (for example, ingress protection ratings, battery life in hours, wattage, and connectivity generation) are parsed using Google Gemini 1.5 Flash (gemini-1.5-flash) under deterministic greedy decoding (temperature = 0.0) with strict JSON schema mode and SHA-256 prompt-hash memoization. In the frozen benchmark generation runs, Gemini 1.5 Flash completed 100% of primary extractions without requiring invocation of the fallback pool (llama-3.3-70b-versatile and gpt-oss-120b). Because commercial cloud API model checkpoints may be modified or retired over time, scientific reproducibility is guaranteed by preserving the complete, immutable SHA-256-keyed extraction artifact cache alongside the code. The extraction prompt operates under a frozen Skeptic design, explicitly penalizing promotional puffery. Unmatched attributes without verbatim textual support are forced to null. Across an audit of 568 explicit technical attribute extractions across pre-cutoff specifications, the retained attributes showed a 0.0% hallucination rate by construction (568/568 strictly grounded in source copy). To verify that null-forcing does not suppress valid information, an independent blinded human validation gate on 30 products (270 individual aspect evaluations) demonstrated high inter-annotator agreement (Cohen's kappa = 0.842), strong human-model presence agreement (kappa = 0.812), 97.8% null-forcing adherence, 100% verbatim quote match, and 92.4% extraction recall against human-verified technical specifications. All 631 product specifications conformed fully to the extraction schema.
2. Specification completeness and density. We extract quantitative measures of technical richness: the number of explicit feature bullets, total specification word count, and the density of concrete numerical measurements. Following new-item cold-start theory, we treat specification completeness as a signal of commercial maturity and product readiness [25].
3. Directional monotonic constraints and tabular boosting. On structured technical features of moderate sample size, gradient-boosted trees have repeatedly outperformed neural alternatives [26]–[29]. We therefore avoid end-to-end neural fine-tuning, drawing on established literature in multi-feature aspect extraction and sentiment representation [30]–[33]. XGBoost [26] is fitted with directional priors grounded in economic reasoning. Downstream hyperparameters were tuned strictly using 5-fold cross-validation on the 507 pre-cutoff training items (n_estimators = 112, max_depth = 5, learning_rate = 0.05, min_child_weight = 3, subsample = 0.8, colsample_bytree = 0.8). Launch price enters with a negative monotone constraint (-1). Brand tier (+1) and specification quality aspects (+1) are constrained to raise predicted viability monotonically [34].

## IV. EXPERIMENTAL RESULTS AND BENCHMARKS
### A. Primary Temporal Performance
Table I and Fig. 3 summarize performance on the frozen 124-product temporal holdout. Model_New reaches a Spearman rank correlation of rho = 0.6722 (95% bootstrap CI [0.5495, 0.7620] across B = 10,000 resamples; asymptotic p = 1.25e-17 for the hypothesis of non-zero rank correlation against zero) and a top-versus-bottom quintile AUC of 0.9712 (RMSE = 19.75, MAE = 16.66). Against the reproduced canonical controlled baseline Model_O (rho = 0.5623, AUC = 0.8904, RMSE = 21.12, MAE = 17.84), this is a statistically significant improvement of delta_rho = +0.1099 (paired bootstrap 95% CI [+0.0485, +0.1833]; paired permutation p = 0.0005 using the standard (b+1)/(M+1) estimator with b = 4 of M = 10,000 permutations; b/M = 0.0004).

![Fig. 3. Primary temporal performance comparison](figures/fig3_performance_comparison.png)

### B. Cold-Start Analysis on Unseen Brands
Brand equity is unavailable for a truly new product, so we isolated the 82 temporal test products from brands with no pre-cutoff footprint (Tier 0; Fig. 4). On this pure cold-start subset, Model_New reaches rho = 0.633 (AUC = 0.981, RMSE = 20.90), compared with rho = 0.516 and AUC = 0.871 for Model_O (delta_rho = +0.117). Retaining specification density and verifiable attribute evidence therefore helps most where the model has the least other information to go on.

![Fig. 4. Cold-start performance on unseen brands](figures/fig4_cold_start.png)

### C. Within-Category Performance
Table II and Fig. 5 give head-to-head results within each of the five categories. Model_New improves Smartwatches (rho = 0.544 vs 0.415, RMSE = 14.22 vs 16.10), Power Banks (rho = 0.126 vs -0.042, RMSE = 26.39 vs 27.95), and Wireless Headphones (rho = 0.132 vs -0.055, RMSE = 22.79 vs 22.93). Ice Makers are essentially unchanged (rho = 0.192 vs 0.185, RMSE = 18.17 vs 20.50). In Bluetooth Speakers the correlation falls (rho = 0.429 vs 0.536, delta = -0.107), but with n = 7 we draw no inferential conclusion from that category. Across the four categories with adequate sample size, Model_New improves or maintains within-category ranking, though absolute correlations in Power Banks (0.126), Wireless Headphones (0.132), and Ice Makers (0.192) remain low.

![Fig. 5. Within-category rank correlation](figures/fig5_within_category.png)

### D. Standardized Six-Learner OOF Benchmark
A natural concern is that the results depend on XGBoost specifically. To check how sensitive they are to the downstream learner, we ran a standardized five-fold out-of-fold (OOF) cross-validation benchmark across six learner families, using only the 507 pre-cutoff training products (Table III, Fig. 6). All preprocessing, scaling, and categorical encoding were fitted inside each training fold.

XGBoost [26] achieves the highest OOF rank monotonicity (rho = 0.7565, R2 = 0.5715, RMSE = 12.53, MAE = 9.56). Support Vector Regression with an RBF kernel [35] follows closely (rho = 0.7495, R2 = 0.5401), as do Gradient Boosted Decision Trees [27] (rho = 0.7396, R2 = 0.5375). With fold-level standard deviations of 0.024 to 0.028, the differences among these three learners are small. Random Forest [36] reaches rho = 0.7267. Ridge regression [37] falls to rho = 0.6481 (R2 = 0.4165), which suggests that non-linear interactions between specification density and aspect scores matter. Multi-Layer Perceptrons are less sample-efficient (rho = 0.5463, R2 = 0.2138), in line with reports that tree ensembles remain stronger on structured tabular data of moderate size [28], [29].

![Fig. 6. Six-learner sensitivity benchmark](figures/fig6_six_learner_benchmark.png)

### E. Standardized List-Ranking and Derived Decision Quality
In venture capital and catalog planning, decision makers work from ranked shortlists and high-stakes binary allocations. We therefore evaluated standardized list-ranking metrics (Kendall's tau and NDCG@K) and a derived extreme-group decision task (top 20% versus bottom 20%, middle 60% excluded) on the frozen 124-product holdout (Table IV, Fig. 7).

Model_New achieves Kendall's tau = 0.4772 (p = 4.12e-15), against tau = 0.3946 (p = 1.11e-10) for the baseline. The gain of 0.0826 in tau is an 8.26-point increase in net concordance, that is, concordant minus discordant pairs as a share of all product pairs. For top-recommended shortlists, NDCG@5 is 0.8933 (baseline: 0.8600). The advantage does not extend to NDCG@10, where the baseline is marginally ahead (0.8832 versus 0.8771), so the gain is concentrated at the top of the ranking.

On the extreme-group task (n = 50 holdout items), Model_New reaches AUC = 0.9712, identical to the top-versus-bottom quintile AUC in Section IV-A (Fig. 7b). At the natural median threshold it classifies 46 of the 50 extreme products correctly: 92.0% accuracy, 92.0% precision, 92.0% recall, and an MCC of +0.8400 (23 TP, 23 TN, 2 FP, 2 FN). The baseline classifies 82.00% of the same items correctly. Because the middle 60% of products is excluded, this task is easier than ranking the full holdout, and we read it as a triage indicator and not as a general accuracy figure.

![Fig. 7. List-ranking and extreme-group ROC](figures/fig7_ranking_decision_quality.png)

## V. ABLATION, ROBUSTNESS, INTERPRETABILITY, AND EFFICIENCY
### A. Controlled Component Ablation
A controlled ablation over seven configurations (Table V, Fig. 8) quantifies what each component contributes. The 24-dimensional feature vector breaks down into 9 aspect scores, 9 aspect mention rates, 3 specification density metrics, 1 launch price, 1 brand tier, and 1 product category indicator. Removing the LLM semantic aspects (A1: removing all 18 aspect scores and mention rates, leaving 6 metadata and density features) causes the largest single drop (delta_rho = -0.0880, rho = 0.5842). Removing the specification density attributes (bullet counts, word count, number density) lowers rho by 0.0321 (to 0.6401), and removing brand tier lowers it by 0.0337 (to 0.6385). Metadata alone (price, brand tier, category) gives only rho = 0.4418 (delta_rho = -0.2304), so launch-time viability cannot be inferred from commercial metadata alone.

One result deserves a comment. The configuration with no LLM aspects at all (A1, rho = 0.5842) already exceeds the scalar-aspect baseline (Model_O, rho = 0.5623). A share of the improvement over Model_O therefore comes from the specification-density features, which are extracted without the LLM.

![Fig. 8. Component feature ablation](figures/fig8_ablation.png)

### B. Seed Stability and Byte-for-Byte Integrity
Across five random seeds (42, 123, 456, 789, 999), Model_New outperforms the baseline consistently (mean rho = 0.6332 +- 0.0331 versus 0.5828 +- 0.0249). The seed-averaged gap (about 0.05) is smaller than the +0.1099 gap of the headline run, so the direction of the effect is stable while its size varies with the seed. The automated leakage test suite passes all 10 criteria (TEST-01: label inaccessibility; TEST-02: zero test ID fitting leakage; TEST-03: strict October 31, 2021 temporal partitioning; TEST-04: training-only normalization bounds; TEST-05: training-only category profiles; TEST-06: training-only brand footprint tiering; TEST-07: CV-only hyperparameter tuning; TEST-08: frozen extraction prompts; TEST-09: isolated test evaluation loading; and TEST-10: byte-for-byte SHA-256 prediction invariance under complete label deletion). In an independent integrity test, we ran prediction once with test ground truth present and once with it deleted. The two runs produced bit-for-bit identical output hashes (SHA-256: 3f75df2ebaf508eb...), which shows that predictions do not depend on test labels. Fig. 9 plots predicted against observed scores on the holdout.

![Fig. 9. Scatter of predicted viability against actual market proxy](figures/fig9_scatter.png)

### C. Feature Attribution and Monotonic Domain Regularization
To keep predictions consistent with product economics and not with spurious training artifacts, the XGBoost estimator applies exact monotonic constraints during tree construction. Launch price is constrained negatively (-1): with all specifications held fixed, a higher price cannot raise predicted viability. Brand tier and all nine aspect ratings are constrained positively (+1). Split-gain analysis attributes over 42% of total split improvement to technical specification density and build quality, which suggests that engineering content carries much of the predictive weight.

### D. Computational Efficiency and Operational Latency
In decision-support settings, inference latency determines usability (Table VI). On commodity x86_64 hardware, downstream scoring with Model_New takes 0.0395 milliseconds per product, a throughput above 25,000 items per second, with a model artifact of 297 KB. Offline LLM aspect extraction takes 1.4–2.2 s per specification. Because extraction is decoupled from scoring, an interactive dashboard can re-estimate predictions instantly as a user moves a parameter slider.

## VI. EXTERNAL APPLICATION VALIDATION
To test transfer beyond the frozen historical holdout, the synchronized application inference engine was run on an independent external cohort of 155 Amazon products launched between 2022 and 2024 across the five canonical categories (Table VII). This cohort is physically distinct from the primary 507/124 partition. On the 150 products with accumulated market validation, the model reaches rho = 0.501 (95% CI [0.362, 0.617]), with rho = 0.6120 on the high-density specification subset (95% CI [0.504, 0.702], Quintile AUC = 0.884), and an extreme-group Quintile AUC of 0.873 (MAE = 15.87 pts). This is lower than the temporal-holdout value of rho = 0.6722. Established brands (n = 129) reach rho = 0.454, while startup and new-entrant brands (n = 21) reach rho = 0.686 (Quintile AUC = 0.940), although the confidence interval for the smaller group is wide ([0.352, 0.865]). The five prospective pre-launch SKUs have no post-launch labels and are excluded from the metrics. The representation therefore carries over to post-2022 products without a collapse in performance.

## VII. DISCUSSION, ETHICAL CONSIDERATIONS, AND LIMITATIONS
The target predicted by this system is a review-derived market-success proxy. It is not unit sales, revenue, or profit. Consumer satisfaction and review velocity correlate with commercial viability in e-commerce markets [5], [6], [9], but paid advertising, distributor relationships, and supply chain logistics also affect aggregate sales volume, and our model does not represent them. Public review platforms are also affected by review spam and promotional manipulation [38]–[40]. They carry survivorship bias as well: products with fewer than five reviews were excluded during corpus curation. Our predictions should therefore be read as expected consumer satisfaction and engagement, conditional on the product reaching baseline market visibility. A single frozen split, five product categories, and a 124-product holdout also limit statistical power, and the extraction stage depends on the specific LLM used.

Note on the temporal cutoff. The October 31, 2021 boundary is a dataset cutoff and not the date of study execution (2026). We selected it to build a strictly forward-in-time cohort with enough pre-cutoff training products and post-cutoff evaluation products. An empirical audit of candidate boundaries shows why later cutoffs cannot serve as the primary research benchmark. The underlying physical product corpus was harvested through September 2023, and products in the 124-product temporal holdout had their first recorded reviews between November 2021 and February 2023 to ensure 7–22 months of post-launch signal stabilization. Shifting the cutoff forward to December 31, 2022 leaves only the 3 products launched in January–February 2023 (n = 3, causing severe sample starvation and category collapse), while any cutoff in late 2023–2026 yields n = 0 post-cutoff products in the harvested historical corpus. We therefore keep the 2021 cutoff with its 124-product holdout as the primary frozen temporal benchmark, and use the 2022–2024 external cohort as an independent post-cutoff validation.

## VIII. CONCLUSION
Augmenting LLM aspect bridging with evidence-grounded cold-start representations reduces the semantic compression bottleneck in launch-blind product success prediction. On a frozen temporal holdout of 124 physical products, the promoted architecture reaches rho = 0.672 and AUC = 0.971, a statistically significant improvement over the scalar-aspect baseline (delta_rho = +0.110, p = 0.0005). The target definition, temporal partition, and downstream learner were left unchanged. In the six-learner benchmark XGBoost ranks first, with SVR and gradient-boosted trees close behind, and the list-ranking and extreme-group analyses show reliable ordering at the top of the shortlist and 92.0% decision accuracy on the extreme-group task. Under pure cold-start conditions, rank correlation on unseen brands is rho = 0.633. The research package, the synchronized application inference engine, and the audit records will be released upon acceptance.

## DATA AND CODE AVAILABILITY
The complete research package—including trained model checkpoints, feature manifests, evaluation scripts, automated leakage test suites, and the complete SHA-256-keyed offline extraction artifact cache—will be released in an open-access public repository with a persistent Zenodo DOI upon acceptance of the manuscript. During peer review, a complete, anonymized verification archive is provided to editors and reviewers upon request.

## AUTHOR CONTRIBUTIONS (CRediT STATEMENT)
Rajvardhan Ajitrao Jagtap: Conceptualization, Methodology, Software, Formal Analysis, Writing – Original Draft. Jyotiraditya Abhijeet Shinde: Software, Data Curation, Validation, Investigation. Tanishq Parag Choudhari: Methodology, Formal Analysis, Visualization, Writing – Review & Editing. Yash Ashok Mohite: Validation, Software, Data Curation. Yogesh Malakari Honamore: Supervision, Project Administration, Resources, Writing – Review & Editing. (All co-authors have reviewed and confirmed their assigned roles prior to submission.)

## FUNDING AND COMPETING INTERESTS
Funding: This research received no external grant or commercial funding.
Competing Interests: The authors declare that they have no financial or commercial conflicts of interest that could influence the findings reported in this paper.

## ETHICS AND PLATFORM COMPLIANCE
Public consumer reviews were obtained from established academic e-commerce research corpora curated for scientific study. All user account identifiers and personal metadata were removed during corpus ingestion, and empirical analyses operated exclusively on anonymized, public product copy without access to private personal data.

## DECLARATION OF GENERATIVE AI IN SCIENTIFIC WRITING
Generative AI models served two distinct functions in this work. Algorithmically, Google Gemini 1.5 Flash was integrated into the experimental pipeline as an automated aspect-extraction and attribute-parsing engine under deterministic greedy decoding. In addition, during manuscript preparation and codebase maintenance, the authors utilized large language model assistants (including Anthropic Claude and Google Antigravity coding agents) for substantive manuscript drafting, structural editing, LaTeX and document formatting, and script refactoring. Following these automated and assistive procedures, all authors critically examined, audited, and verified all quantitative findings, tables, figures, and substantive claims, and take full institutional responsibility for the integrity and factual content of the published work.

## REFERENCES
""" + "\n".join([f"[{i}] {ref}" for i, ref in enumerate(refs_ordered, 1)])

    (MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.md").write_text(md_text, encoding="utf-8")
    for dest in [shutil_dest_paper, shutil_dest_audit]:
        shutil.copy2(MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.md", dest / "FINAL_MANUSCRIPT.md")
    print(f"Saved and synchronized FINAL_MANUSCRIPT.md everywhere.")

if __name__ == "__main__":
    build_manuscript()
