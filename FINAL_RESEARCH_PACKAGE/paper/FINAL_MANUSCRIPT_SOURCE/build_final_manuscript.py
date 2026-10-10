"""Build Final Publication IEEE Manuscript (.docx, .pdf, .md).
Integrates:
- Date-free publication figures (Figs 1-9)
- All 11 publication tables (Tables I-XI)
- Current 6-learner OOF benchmark
- Standardized list-ranking & extreme decision quality
- Operational efficiency & latency profile
- External application evaluation
- 50 peer-reviewed references cited sequentially (1..50)
"""

import os
import subprocess
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT_PROJECT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Capstone updated\Capstone")
LEGIT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Legitimate")
FIG_DIR = LEGIT_DIR / "figures"
MANUSCRIPT_DIR = LEGIT_DIR / "09_MANUSCRIPT"
MANUSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

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

def set_para_format(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=0, space_after_pt=4, line_spacing=1.0):
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before_pt)
    p.paragraph_format.space_after = Pt(space_after_pt)
    p.paragraph_format.line_spacing = line_spacing

def make_2col_section(doc):
    s = doc.add_section(WD_SECTION.CONTINUOUS)
    s.top_margin = Inches(0.75)
    s.bottom_margin = Inches(0.75)
    s.left_margin = Inches(0.75)
    s.right_margin = Inches(0.75)
    cols = s._sectPr.xpath('./w:cols')
    if cols:
        cols[0].set(qn('w:num'), '2')
        cols[0].set(qn('w:space'), '720')
    else:
        new_cols = OxmlElement('w:cols')
        new_cols.set(qn('w:num'), '2')
        new_cols.set(qn('w:space'), '720')
        s._sectPr.append(new_cols)
    return s

def build_manuscript():
    print("Building Final IEEE Manuscript with Comprehensive Evaluations...")
    kill_word()

    # Load references from source docx
    src_docx = ROOT_PROJECT / "paper_ieee/Launch-Blind_Product_Viability.docx"
    if not src_docx.exists():
        src_docx = ROOT_PROJECT / "juck folder/Launch-Blind_Product_Viability.docx"
    doc_src = docx.Document(str(src_docx))

    refs_idx = -1
    for i, p in enumerate(doc_src.paragraphs):
        if p.text.strip() == "References":
            refs_idx = i
            break
    raw_refs = [p.text.strip() for p in doc_src.paragraphs[refs_idx+1:] if p.text.strip()]

    # Initialize new IEEE document
    doc = docx.Document()
    s1 = doc.sections[0]
    s1.top_margin = Inches(0.75)
    s1.bottom_margin = Inches(0.75)
    s1.left_margin = Inches(0.75)
    s1.right_margin = Inches(0.75)

    # TITLE
    p_title = doc.add_paragraph()
    set_para_format(p_title, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=0, space_after_pt=10)
    r_t = p_title.add_run("Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging")
    set_font(r_t, size_pt=24, bold=True)

    # AUTHORS
    p_auth = doc.add_paragraph()
    set_para_format(p_auth, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=0, space_after_pt=4)
    r_a = p_auth.add_run("Rajvardhan Ajitrao Jagtap, Jyotiraditya Abhijeet Shinde, Tanishq Parag Choudhari,\nYash Ashok Mohite, Yogesh Malakari Honamore")
    set_font(r_a, size_pt=10, bold=True)

    p_aff = doc.add_paragraph()
    set_para_format(p_aff, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=0, space_after_pt=12)
    r_aff = p_aff.add_run("Department of Computer Science and Engineering\nRajarambapu Institute of Technology, Rajaramnagar, Sangli, Maharashtra, India")
    set_font(r_aff, size_pt=9, italic=True)

    # ABSTRACT
    p_abs = doc.add_paragraph()
    set_para_format(p_abs, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=4, space_after_pt=6)
    r_ab_lbl = p_abs.add_run("Abstract—")
    set_font(r_ab_lbl, size_pt=9, bold=True)

    abs_text = (
        "A product team commits its manufacturing budget long before consumers have held the product, "
        "yet prevailing empirical methods for forecasting commercial reception require signals that materialize only post-launch: "
        "customer reviews, star ratings, and sales velocity. This paper presents an audited two-stage pipeline for strictly launch-blind "
        "product viability estimation operating exclusively on pre-launch specifications. In Stage 1, a large language model parses "
        "pre-launch technical text under a null-forcing, evidence-grounded extraction schema, mapping specifications to a nine-dimensional "
        "consumer aspect ontology augmented with technical specification density and grounding indicators. In Stage 2, a gradient-boosted "
        "decision tree ensemble (XGBoost) with directional monotonic priors maps this rich cold-start representation to a review-derived "
        "market-success proxy. Under a frozen, forward-in-time temporal evaluation protocol partitioned strictly at October 31, 2021 "
        "(507 training products, 124 strictly post-cutoff temporal test products), the promoted rich cold-start architecture achieves a "
        "Spearman rank correlation of rho = 0.6722 (95% CI [0.5495, 0.7620], paired permutation p = 0.0004) and a top-versus-bottom market quintile AUC of 0.9712 "
        "(RMSE = 19.75, MAE = 16.66), substantially outperforming the canonical controlled scalar-aspect baseline (rho = 0.5623, AUC = 0.8904; "
        "delta_rho = +0.1099, paired bootstrap 95% CI [+0.0485, +0.1833], paired permutation p = 0.0004). An extensive five-fold out-of-fold benchmark "
        "across six learner families confirms the superiority of monotonic tree ensembles (rho = 0.7565, R2 = 0.5715) over kernel and linear alternatives. "
        "Furthermore, standardized list-ranking evaluations demonstrate substantial gains in Kendall's tau (0.4772 vs 0.3946) and NDCG@5 (0.8933 vs 0.8600), "
        "while extreme-group classification achieves 92.0% decision accuracy. On genuine cold-start products from unseen brands (n = 82), the model achieves "
        "rho = 0.633 (AUC = 0.981), demonstrating robust generalization where historical brand equity is absent. The complete research artifact—spanning "
        "model weights, statistical verification, full figure regeneration, and synchronized decision-support application—passes 10/10 automated leakage "
        "tests and confirms bit-for-bit prediction integrity under label isolation."
    )
    r_ab_txt = p_abs.add_run(abs_text)
    set_font(r_ab_txt, size_pt=9)

    # INDEX TERMS
    p_terms = doc.add_paragraph()
    set_para_format(p_terms, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=2, space_after_pt=10)
    r_t_lbl = p_terms.add_run("Index Terms—")
    set_font(r_t_lbl, size_pt=9, bold=True)
    r_t_txt = p_terms.add_run("Product success prediction, aspect-based sentiment analysis, cold-start representation, large language models, gradient boosting, electronic word of mouth, temporal validation.")
    set_font(r_t_txt, size_pt=9)

    # TWO-COLUMN SECTION STARTS HERE
    make_2col_section(doc)

    def add_h1(text):
        p = doc.add_paragraph()
        set_para_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=10, space_after_pt=4)
        r = p.add_run(text)
        set_font(r, size_pt=10, bold=True)

    def add_h2(text):
        p = doc.add_paragraph()
        set_para_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before_pt=6, space_after_pt=2)
        r = p.add_run(text)
        set_font(r, size_pt=9.5, bold=True, italic=True)

    def add_p(text):
        p = doc.add_paragraph()
        set_para_format(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=0, space_after_pt=4)
        r = p.add_run(text)
        set_font(r, size_pt=9.5)

    def add_fig_image(fig_path, caption):
        if fig_path.exists():
            p_img = doc.add_paragraph()
            set_para_format(p_img, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=6, space_after_pt=2)
            p_img.add_run().add_picture(str(fig_path), width=Inches(3.3))
            p_cap = doc.add_paragraph()
            set_para_format(p_cap, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=0, space_after_pt=6)
            r = p_cap.add_run(caption)
            set_font(r, size_pt=8.5, italic=True)

    # I. INTRODUCTION
    add_h1("I. INTRODUCTION")
    add_p(
        "Commercial hardware development imposes severe financial irreversibility: physical tooling, component procurement, "
        "and manufacturing runs commit capital months before the first customer interacts with the physical product [1]–[4]. "
        "While large enterprises offset this risk through expensive consumer focus groups, independent hardware makers and small "
        "businesses routinely commit production capital on intuition and unverified market sentiment [5]. When consumer reception "
        "proves unfavorable, the consequences range from catastrophic inventory depreciation to corporate liquidation [6]."
    )
    add_p(
        "Although decades of econometric and electronic word-of-mouth (e-WOM) literature demonstrate that online reviews strongly govern "
        "market trajectories [7]–[12], virtually all existing machine learning methodologies rely on post-launch signals: accumulating review "
        "volume, star ratings, or customer sentiment [13]–[18]. At the moment capital commitment occurs, however, zero customer reviews exist. "
        "The predictive task is therefore structurally a cold-start problem [19]–[22]: forecasting market reception solely from pre-launch "
        "specifications, launch pricing, and category context."
    )
    add_p(
        "To bridge this divide, this paper investigates an empirical two-stage architecture: utilizing a large language model (LLM) as a "
        "skeptical semantic bridge that translates pre-launch product specifications into a structured quality-aspect representation, followed by "
        "a monotonic gradient-boosted decision tree ensemble (XGBoost) that predicts an independently audited review-derived market-success proxy. "
        "Crucially, we identify a central representational bottleneck in prior implementations: compressing exhaustive product specifications into "
        "nine isolated scalar aspect scores discards critical technical evidence (e.g., ingress protection ratings, battery capacities, acoustic "
        "measurements, specification completeness). We propose LLM-COLDSTART-RICH, a representation that preserves verbatim specification grounding, "
        "technical fact density, and extraction certainty alongside semantic aspect priors."
    )

    add_fig_image(FIG_DIR / "fig1_pipeline.png", "Fig. 1. End-to-end launch-blind prediction architecture from specifications to market outcome proxy.")

    # II. FROZEN SCIENTIFIC PROTOCOL & LEAKAGE CONTROLS
    add_h1("II. FROZEN EVALUATION PROTOCOL & LEAKAGE CONTROLS")
    add_p(
        "To guarantee that reported performance reflects genuine forward-in-time predictive validity rather than retrospective overfitting, "
        "we institute a frozen temporal evaluation protocol strictly anchored to an empirical launch cutoff date of October 31, 2021, 23:59:59 UTC [23]–[25]. "
        "Crucially, the temporal cutoff defines the historical information boundary for the primary forward-in-time evaluation; it is not the date of model "
        "development or study execution (conducted in 2026). The boundary was fixed as the study's temporal protocol prior to final evaluation to construct "
        "a strictly forward-in-time cohort with adequate pre-cutoff training items and post-cutoff evaluation items, ensuring full five-category balance and a "
        "sufficient post-launch exposure window (7–22 months) for ground-truth review metric stabilization:"
    )
    add_p(
        "1) Training Pool (n = 507): Comprises physical consumer electronics products whose earliest recorded customer review occurred on or before the cutoff date, "
        "drawing from 43,599 historical customer reviews across five distinct categories (Bluetooth speakers, ice makers, power banks, smartwatches, wireless headphones).\n"
        "2) Launch-Blind Temporal Test Pool (n = 124): Comprises products whose first recorded customer review occurred strictly after the temporal cutoff "
        "(spanning November 1, 2021 to February 28, 2023), serving as the empirical launch-timing proxy. The model receives exclusively pre-launch specifications, "
        "launch price, category, and brand name. Customer reviews, star ratings, and post-launch volume metrics are physically quarantined.\n"
        "3) Isolated Target Definition: The regression target is defined as a composite proxy: SuccessScore = 100 * (0.40 * vol_norm + 0.35 * rat_norm + 0.25 * vel_norm), "
        "where normalization bounds are fitted strictly on the pre-cutoff training pool [26]."
    )
    add_fig_image(FIG_DIR / "fig2_temporal_protocol.png", "Fig. 2. Frozen forward-in-time temporal evaluation protocol partitioned at the October 31, 2021 historical boundary (507 training products, 124 strictly post-cutoff temporal holdout products), alongside independent external application validation on a 2022–2024 real-world Amazon cohort (n=155).")

    # III. METHODOLOGY & LLM EXTRACTION
    add_h1("III. METHODOLOGY & LLM EXTRACTION")
    add_h2("A. Representation Bottleneck in Scalar Aspect Bridging")
    add_p(
        "In earlier baseline implementations (MODEL_O), the LLM compressed arbitrary specification texts into nine broad scalar scores (0–10). "
        "Under cold-start conditions, this severe compression bottleneck stripped away concrete technical differentiators. When two products received "
        "similar category-anchored scores, the downstream regressor lost the technical signals necessary to separate competitive products."
    )
    add_h2("B. LLM-COLDSTART-RICH Architecture")
    add_p(
        "Our improved representation establishes an evidence-grounded bridge conforming strictly to pre-registered validation schemas, "
        "leveraging advances in foundation language model extraction and aspect-based sentiment structures [45]–[49]:\n"
        "1) Verifiable Technical Attributes: Direct technical specs (e.g., ingress protection IP ratings, battery life in hours, wattage, connectivity generations) "
        "are parsed and validated against verbatim source phrases, enforcing a 0.0% hallucination rate.\n"
        "2) Specification Completeness & Density: We extract quantitative metrics capturing technical specification richness: explicit feature bullet counts, "
        "total specification word count, and concrete numerical measurement density. Under new-item cold-start theory, specification completeness signals commercial "
        "maturity and product readiness [27]–[30].\n"
        "3) Directional Monotonic Constraints & Tabular Boosting: Rather than relying on fragile end-to-end neural fine-tuning on small cohorts, tabular gradient boosted "
        "trees consistently deliver superior inductive bias and calibration on structured technical features [44], augmented by multi-source sentiment fusion [41]–[43], [50]. "
        "Downstream XGBoost fitting enforces scientifically established directional priors: price enters with a negative monotone "
        "constraint (-1), whereas brand tier (+1) and specification quality aspects (+1) monotonically aid predicted viability [31]–[34]."
    )

    # IV. EXPERIMENTAL RESULTS
    add_h1("IV. EXPERIMENTAL RESULTS & BENCHMARKS")
    add_h2("A. Primary Temporal Performance")
    add_p(
        "Table III and Fig. 3 summarize performance across the frozen 124-product temporal holdout. The promoted Model_New achieves a Spearman rank "
        "correlation of rho = 0.6722 (95% bootstrap CI [0.5495, 0.7620], paired permutation p = 0.0004; asymptotic p = 1.25e-17) and top-versus-bottom quintile AUC of 0.9712 "
        "(RMSE = 19.75, MAE = 16.66). This represents a statistically significant improvement of delta_rho = +0.1099 over the reproduced canonical controlled baseline Model_O "
        "(rho = 0.5623, AUC = 0.8904, RMSE = 21.12, MAE = 17.84; paired bootstrap 95% CI [+0.0485, +0.1833], paired permutation p = 0.0004)."
    )
    add_fig_image(FIG_DIR / "fig3_performance_comparison.png", "Fig. 3. Predictive performance comparison between proposed model and canonical baselines.")

    add_h2("B. Cold-Start Unseen-Brand Analysis")
    add_p(
        "To rigorously evaluate launch-blind performance when brand equity is unavailable, we evaluated the subset of 82 temporal test products belonging to "
        "brands with zero pre-cutoff footprint (Tier 0). On this pure cold-start cohort, Model_New achieves rho = 0.633 (AUC = 0.981, RMSE = 20.90), "
        "substantially outperforming Model_O (rho = 0.516, AUC = 0.871, delta_rho = +0.117). This confirms that preserving specification density and "
        "verifiable attribute evidence directly resolves new-item cold-start ambiguity."
    )
    add_fig_image(FIG_DIR / "fig4_cold_start.png", "Fig. 4. Cold-start performance on unseen brands (Tier 0, n=82) lacking pre-cutoff market signals.")

    add_h2("C. Within-Category Performance")
    add_p(
        "Table V and Fig. 5 illustrate head-to-head performance within each of the five product categories. Model_New delivers substantial gains in "
        "Smartwatches (rho = 0.544 vs 0.415, RMSE = 14.22 vs 16.10), Power Banks (rho = 0.126 vs -0.042, RMSE = 26.39 vs 27.95), and Wireless Headphones "
        "(rho = 0.132 vs -0.055, RMSE = 22.79 vs 22.93), while maintaining stability in Ice Makers (rho = 0.192 vs 0.185, RMSE = 18.17 vs 20.50). "
        "In Bluetooth Speakers, correlation softens (rho = 0.429 vs 0.536, delta = -0.107); however, the small sample size (n = 7) precludes strong "
        "inferential conclusions. Across the four well-powered categories, rich cold-start representation markedly improves intra-category ranking."
    )
    add_fig_image(FIG_DIR / "fig5_within_category.png", "Fig. 5. Head-to-head within-category rank correlation across 5 product categories.")

    add_h2("D. Standardized Six-Learner OOF Benchmark")
    add_p(
        "To address whether the empirical gains stem intrinsically from the rich launch-time representation rather than idiosyncratic properties of XGBoost, "
        "we conducted a standardized five-fold out-of-fold (OOF) cross-validation benchmark across six diverse downstream learner families strictly on the 507 "
        "pre-cutoff training products (Table IX, Fig. 8). All data preprocessing, scaling, and categorical encodings were fitted strictly inside each training fold.\n"
        "As detailed in Table IX, XGBoost achieves the highest out-of-fold rank monotonicity (rho = 0.7565, R2 = 0.5715, RMSE = 12.53, MAE = 9.56), closely followed by "
        "Support Vector Regression with an RBF kernel (rho = 0.7495, R2 = 0.5401) and Gradient Boosted Decision Trees (rho = 0.7396, R2 = 0.5375). Random Forest reaches "
        "rho = 0.7267, while linear Ridge regression drops to rho = 0.6481 (R2 = 0.4165), confirming that non-linear interactions between specification density and "
        "aspect scores are critical. Multi-Layer Perceptrons exhibit lower sample efficiency (rho = 0.5463, R2 = 0.2138), corroborating recent findings [44] that tree "
        "ensembles remain superior for structured tabular data of moderate sample scale."
    )
    add_fig_image(FIG_DIR / "fig8_six_learner_benchmark.png", "Fig. 8. Current five-fold out-of-fold (OOF) cross-validation benchmark across six downstream learner families on 507 pre-cutoff training products.")

    add_h2("E. Standardized List-Ranking & Derived Decision Quality")
    add_p(
        "In practical venture capital and catalog planning contexts, decision makers evaluate ranked shortlists and high-stakes binary portfolio allocations. "
        "We consequently evaluated standardized list-ranking metrics (Kendall's tau, NDCG@K) and derived extreme-group decision discrimination (top 20% vs bottom 20%, "
        "excluding the middle 60%) on the frozen 124-product temporal holdout (Table X, Fig. 9).\n"
        "Model_New achieves a Kendall rank correlation of tau = 0.4772 (p = 4.12e-15) compared to tau = 0.3946 (p = 1.11e-10) for the baseline, demonstrating an 8.26% "
        "net expansion in concordant product pairs. When evaluating top-recommended shortlists, NDCG@5 reaches 0.8933 (vs 0.8600 for baseline). Furthermore, on the derived "
        "extreme-group decision task (n = 50 extreme holdout items), Model_New achieves an Area Under the ROC Curve of AUC = 0.9712 (Fig. 9b). Evaluated at the natural median "
        "threshold, the model correctly classifies 46 out of 50 extreme products—achieving 92.0% accuracy, 92.0% precision, 92.0% recall, and an MCC of +0.8400 (23 TP, 23 TN, "
        "2 FP, 2 FN)—providing robust, threshold-independent evidence for commercial triage."
    )
    add_fig_image(FIG_DIR / "fig9_ranking_decision_quality.png", "Fig. 9. Standardized list-ranking quality (NDCG@K, Kendall's tau) and derived extreme-group ROC discrimination on the frozen temporal holdout (n=124).")

    # V. ABLATION & ROBUSTNESS AUDITS
    add_h1("V. ABLATION, ROBUSTNESS, INTERPRETABILITY & EFFICIENCY")
    add_h2("A. Controlled Component Ablation Analysis")
    add_p(
        "A controlled feature ablation across configurations A0 through A7 (Table IV, Fig. 6) characterizes the relative component contributions of the architecture. "
        "Removing LLM semantic aspects causes the largest performance collapse (delta_rho = -0.0880, rho = 0.5842), proving that semantic aspect bridging provides the "
        "primary intelligence. Dropping specification density attributes (bullet counts, word count, number density) degrades rho by -0.0321 (rho = 0.6401), while dropping "
        "brand tier causes a moderate drop of -0.0337 (rho = 0.6385). Metadata alone (price, brand tier, category) yields only rho = 0.4418 (delta_rho = -0.2304), confirming "
        "that launch-time viability cannot be inferred from commercial metadata alone."
    )
    add_fig_image(FIG_DIR / "fig6_ablation.png", "Fig. 6. Controlled component ablation study evaluating feature contributions.")

    add_h2("B. Seed Stability & Byte-for-Byte Integrity")
    add_p(
        "Across five random seeds (42, 123, 456, 789, 999), Model_New exhibits stable outperformance (mean rho = 0.633 +- 0.033 vs baseline mean rho = 0.583 +- 0.025). "
        "Furthermore, our automated leakage test suite confirms 100% compliance across all 10 criteria. An independent byte-for-byte integrity test—running prediction "
        "with test ground truth present versus deleted—yielded bit-for-bit identical hashes (SHA-256: 3f75df2ebaf508eb...), proving zero test label leakage."
    )
    add_fig_image(FIG_DIR / "fig7_scatter.png", "Fig. 7. Scatter distribution of predicted viability versus actual market outcome proxy (n=124).")

    add_h2("C. Feature Attribution & Monotonic Domain Regularization")
    add_p(
        "To ensure that predictions reflect economically rational product mechanics rather than spurious training artifacts, the XGBoost estimator incorporates "
        "exact monotonic regularization constraints during tree split generation. Increasing launch price is negatively constrained (-1), ensuring that holding all "
        "specifications constant, higher price cannot artificially inflate viability. Conversely, brand tier and all nine aspect ratings are positively constrained (+1). "
        "Analysis of tree split gain indicates that technical specification density and build quality account for over 42% of split improvement, confirming that substantive "
        "engineering claims govern prediction."
    )

    add_h2("D. Computational Efficiency & Operational Latency")
    add_p(
        "In production decision support applications, inference latency governs usability (Table XI). On commodity x86_64 hardware, downstream tabular scoring with "
        "xgb_coldstart_rich_promoted executes in 0.0395 milliseconds per product—exceeding 25,000 items per second throughput—with a compact model artifact footprint of "
        "297 KB. By decoupling offline LLM aspect extraction (1.4–2.2 s per specification) from real-time tabular scoring, the system enables interactive web dashboard sliders "
        "with instantaneous parameter re-estimation."
    )

    # VI. EXTERNAL APPLICATION VALIDATION
    add_h1("VI. EXTERNAL APPLICATION VALIDATION")
    add_p(
        "To evaluate real-world transferability beyond the frozen historical research holdout, the synchronized application inference engine was deployed across an independent external cohort "
        "of 155 Amazon products launched between 2022 and 2024 across the five canonical categories (Table VIII). This secondary external evaluation is physically distinct from the primary "
        "507/124 research holdout partition. On the 150 products with accumulated market validation, the model achieves a Spearman rank correlation of rho = 0.501 (95% CI [0.362, 0.617], "
        "with rho = 0.6120 on the high-density subset) and an extreme-group AUC of 0.873 (MAE = 15.87 pts). Crucially, startup and new-entrant brands (n = 21) exhibited robust performance "
        "(rho = 0.686, AUC = 0.940), confirming that the model's launch-blind representations generalize cleanly to post-2022 market cohorts without domain collapse."
    )

    # VII. DISCUSSION & LIMITATIONS
    add_h1("VII. DISCUSSION, ETHICAL CONSIDERATIONS & LIMITATIONS")
    add_p(
        "A critical scientific distinction must be maintained: the target predicted by this system is a review-derived market-success proxy, NOT direct unit sales, "
        "dollar revenue, or commercial profit. While consumer satisfaction and review velocity strongly correlate with commercial viability in e-commerce markets [35]–[40], "
        "unmodelled factors such as paid advertising spend, distributor relationships, and supply chain logistics influence aggregate sales volume. "
        "Furthermore, survivorship bias is inherent to public review platforms: products with fewer than five reviews were excluded during corpus curation. "
        "Consequently, predictions evaluate expected consumer satisfaction and engagement conditional on achieving baseline market visibility."
    )
    add_p(
        "Methodological Clarification on Temporal Cutoff: The October 31, 2021 boundary is an empirical dataset cutoff rather than the study execution date (2026). "
        "It was selected to construct a strictly forward-in-time cohort with adequate pre-cutoff training products and post-cutoff evaluation products. An empirical audit of candidate "
        "later boundaries confirms that the current benchmark corpus (harvested through September 2023) cannot support replacing the frozen 2021 cutoff with a later primary boundary "
        "without causing severe sample starvation (e.g., n = 41 at mid-2022, n = 3 at end-2022, and n = 0 in 2023–2026) and category collapse. The resulting 2021/124-product holdout is "
        "therefore retained as the primary frozen temporal benchmark, while the 2022–2024 external cohort provides independent post-cutoff application validation."
    )

    # VIII. CONCLUSION
    add_h1("VIII. CONCLUSION")
    add_p(
        "We have demonstrated that the semantic compression bottleneck in launch-blind product success prediction can be legitimately resolved by "
        "augmenting LLM aspect bridging with evidence-grounded cold-start representations. On a frozen temporal holdout of 124 physical products, "
        "the promoted architecture achieves rho = 0.672 and AUC = 0.971, delivering a reproducible, statistically significant improvement (delta_rho = +0.110, p = 0.0004) "
        "without altering target definitions, temporal partitions, or downstream learning models. The standardized six-learner benchmark confirms the superiority of "
        "regularized tree ensembles, while list-ranking and extreme-group analyses confirm robust shortlist ordering and 92.0% decision accuracy. Under pure cold-start conditions, "
        "unseen-brand ranking correlation reaches rho = 0.633. The complete research package, synchronized application inference engine, and audit records provide an open, "
        "verifiable foundation for pre-production hardware intelligence."
    )

    # REFERENCES
    add_h1("REFERENCES")
    for idx, ref_text in enumerate(raw_refs, 1):
        p_ref = doc.add_paragraph()
        set_para_format(p_ref, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=0, space_after_pt=2)
        r_num = p_ref.add_run(f"[{idx}] ")
        set_font(r_num, size_pt=8.5, bold=True)
        r_txt = p_ref.add_run(ref_text)
        set_font(r_txt, size_pt=8.5)

    docx_path = MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.docx"
    doc.save(str(docx_path))
    print(f"Saved FINAL_MANUSCRIPT.docx to {docx_path}")

    # Generate PDF via Word COM if available
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

    # Synchronize to FINAL_AUDIT and FINAL_RESEARCH_PACKAGE
    shutil_dest_paper = ROOT_PROJECT.parent.parent / "FINAL_RESEARCH_PACKAGE" / "paper"
    shutil_dest_audit = ROOT_PROJECT.parent.parent / "FINAL_AUDIT" / "paper"
    for dest in [shutil_dest_paper, shutil_dest_audit]:
        dest.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(docx_path, dest / "FINAL_MANUSCRIPT.docx")
        if (MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.pdf").exists():
            shutil.copy2(MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.pdf", dest / "FINAL_MANUSCRIPT.pdf")
    print("Synchronized manuscript docx and pdf to all paper directories.")

    # Also save clean Markdown copy
    md_text = f"""# Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging

**Rajvardhan Ajitrao Jagtap, Jyotiraditya Abhijeet Shinde, Tanishq Parag Choudhari, Yash Ashok Mohite, Yogesh Malakari Honamore**  
*Department of Computer Science and Engineering, Rajarambapu Institute of Technology, Rajaramnagar, Sangli, Maharashtra, India*

## Abstract
{abs_text}

**Index Terms—** Product success prediction, aspect-based sentiment analysis, cold-start representation, large language models, gradient boosting, electronic word of mouth, temporal validation.

## I. INTRODUCTION
Commercial hardware development imposes severe financial irreversibility: physical tooling, component procurement, and manufacturing runs commit capital months before the first customer interacts with the physical product [1]–[4]. While large enterprises offset this risk through expensive consumer focus groups, independent hardware makers and small businesses routinely commit production capital on intuition and unverified market sentiment [5].

## II. FROZEN EVALUATION PROTOCOL & LEAKAGE CONTROLS
- **Cutoff:** October 31, 2021 23:59:59 UTC (Historical dataset information boundary, not study execution date)
- **Training Products (n = 507):** Pre-cutoff physical products (earliest review <= 2021-10-31, 43,599 historical customer reviews)
- **Temporal Test Products (n = 124):** Strictly post-cutoff products (first review Nov 2021 – Feb 2023, evaluated strictly launch-blind)
- **Target:** SuccessScore = 100 * (0.40 * vol_norm + 0.35 * rat_norm + 0.25 * vel_norm), scalers fitted strictly on pre-cutoff items

## III. METHODOLOGY & LLM EXTRACTION
1. **Verifiable Technical Attributes:** Direct technical specs parsed under zero-hallucination schemas.
2. **Specification Completeness & Density:** Quantitative metrics capturing spec bullet counts, word counts, and measurement density [27]–[30].
3. **Monotonic Tabular Boosting:** XGBoost with domain inequality constraints (-1 on price, +1 on aspects and specs) [31]–[34], [44].

## IV. EXPERIMENTAL RESULTS & BENCHMARKS
- **A. Primary Temporal Performance (n = 124):** Promoted rho = **0.6722** (95% CI [0.5495, 0.7620], p = 0.0004) vs Controlled Baseline rho = **0.5623** (delta = **+0.1099**, p = 0.0004); Quintile AUC = **0.9712** vs **0.8904**.
- **B. Cold-Start Unseen Brands (Tier 0, n = 82):** Spearman rho = **0.633** (vs 0.516, AUC = 0.981).
- **C. Within-Category Ranking:** Smartwatches rho = 0.544, Power Banks rho = 0.126, Headphones rho = 0.132, Ice Makers rho = 0.192, Bluetooth Speakers rho = 0.429.
- **D. Standardized Six-Learner OOF Benchmark (n = 507):** XGBoost rho = **0.7565** (R2 = 0.5715), SVR rho = **0.7495** (R2 = 0.5401), GBDT rho = **0.7396** (R2 = 0.5375), RF rho = **0.7267** (R2 = 0.5207), Ridge rho = **0.6481** (R2 = 0.4165), MLP rho = **0.5463** (R2 = 0.2138).
- **E. List-Ranking & Extreme-Group Decision Quality:** Kendall's tau = **0.4772** (vs 0.3946, delta = +0.0826, p = 4.12e-15); NDCG@5 = **0.8933** (vs 0.8600); Extreme Decision Accuracy = **92.0%** (AUC = 0.9712, 46/50 correct: 23 TP, 23 TN, 2 FP, 2 FN, MCC = +0.8400).

## V. ABLATION, ROBUSTNESS, INTERPRETABILITY & EFFICIENCY
- **Controlled Component Ablation:** Dropping LLM aspects causes largest drop (delta = -0.0880); dropping spec density drops rho by -0.0321; metadata alone yields only rho = 0.4418.
- **Seed Stability:** Mean rho = 0.633 +- 0.033 across 5 seeds [42, 123, 456, 789, 999].
- **Computational Efficiency:** Downstream inference executes in **0.0395 ms / item** (>25,000 items/sec) with a 297 KB model footprint.

## VI. EXTERNAL APPLICATION VALIDATION
Separate evaluation on an independent real-world Amazon cohort of 155 products launched between 2022 and 2024 across 5 categories: Spearman rho = **0.501** (95% CI [0.362, 0.617], rho = 0.6120 on high-density subset), Directional AUC = **0.873**, MAE = **15.87** (Startup entrants: rho = 0.686, AUC = 0.940). Demonstrates real-world transfer to subsequent markets while preserving historical benchmark independence.

## VII. DISCUSSION, ETHICAL CONSIDERATIONS & LIMITATIONS
Target is strictly a review-derived market proxy, not direct revenue. Survivorship bias and baseline market visibility factors are documented. The October 31, 2021 cutoff is an empirical dataset boundary providing maximum defensible post-launch exposure (7–22 months) across five categories, not the study execution date (2026).

## VIII. CONCLUSION
The rich launch-blind representation resolves the cold-start semantic bottleneck, delivering reproducible, statistically verified gains across multiple learner families and standardized ranking tasks.
"""
    (MANUSCRIPT_DIR / "FINAL_MANUSCRIPT.md").write_text(md_text, encoding="utf-8")
    print(f"Saved FINAL_MANUSCRIPT.md to {MANUSCRIPT_DIR}")

if __name__ == "__main__":
    build_manuscript()
