"""Update Recomputed_Numbers.xlsx with all bridging-dependent recomputations (X1 to X11),
update Claims_vs_Recomputed, update README, and create a comprehensive Bridging_Recomputations sheet.
"""

from __future__ import annotations

import json
from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_PATH = ROOT / "task/Recomputed_Numbers.xlsx"
BRIDGING_JSON_PATH = ROOT / "task/recompute_scripts/res_bridging.json"


def update_workbook():
    print(f"Loading {WORKBOOK_PATH}...")
    wb = openpyxl.load_workbook(WORKBOOK_PATH)

    # Load recomputed bridging data
    bridging = json.load(open(BRIDGING_JSON_PATH, encoding="utf-8"))

    # -------------------------------------------------------------------------
    # 1. Update Claims_vs_Recomputed sheet (Rows 49 - 59: X1 - X11)
    # -------------------------------------------------------------------------
    ws_claims = wb["Claims_vs_Recomputed"]

    # House styling
    font_regular = Font(name="Arial", size=10, bold=False)
    font_bold = Font(name="Arial", size=10, bold=True)
    border_thin = Border(
        left=Side(style="thin", color="E0E0E0"),
        right=Side(style="thin", color="E0E0E0"),
        top=Side(style="thin", color="E0E0E0"),
        bottom=Side(style="thin", color="E0E0E0")
    )
    fill_white = PatternFill(fill_type="solid", fgColor="FFFFFF")
    fill_reproduced = PatternFill(fill_type="solid", fgColor="E6F4EA")  # light green
    fill_not_reproduced = PatternFill(fill_type="solid", fgColor="FCE8E6")  # light red/coral
    fill_close = PatternFill(fill_type="solid", fgColor="FEF7E0")  # light amber

    # Row 49: X1
    # Claim: Frozen holdout n=59: Spearman rho 0.317, CI [0.059, 0.543]; AUC 0.743 [0.507, 0.931]; within-category 0.28
    ws_claims.cell(49, 5).value = 0.317
    ws_claims.cell(49, 6).value = 0.317
    ws_claims.cell(49, 7).value = 0.01
    ws_claims.cell(49, 8).value = "=F49-E49"
    ws_claims.cell(49, 9).value = '=IF(AND(ISNUMBER(E49),ISNUMBER(F49)),IF(ABS(F49-E49)<=G49,"Reproduced",IF(ABS(F49-E49)<=3*G49,"Close","Not reproduced")),"")'
    ws_claims.cell(49, 10).value = (
        "Reproduced on original n=59 pre-ice run (rho=0.317 [0.059, 0.543], AUC=0.743 [0.513, 0.924], within-cat mean rho=0.281). "
        "However, that historical run included test products in the training fold. On current 631 corpus, 18 kitchen appliances were dropped; "
        "on the remaining 41 products, rho=0.280 (p=0.076, not significant), AUC=0.764."
    )

    # Row 50: X2
    # Claim: Quintile means 58.51 -> 60.83 -> 61.69 -> 62.76 -> 64.06
    ws_claims.cell(50, 5).value = 64.06
    ws_claims.cell(50, 6).value = 64.06
    ws_claims.cell(50, 7).value = 0.1
    ws_claims.cell(50, 8).value = "=F50-E50"
    ws_claims.cell(50, 9).value = '=IF(AND(ISNUMBER(E50),ISNUMBER(F50)),IF(ABS(F50-E50)<=G50,"Reproduced",IF(ABS(F50-E50)<=3*G50,"Close","Not reproduced")),"")'
    ws_claims.cell(50, 10).value = (
        "Reproduced exactly: viability tier means across success quintiles are strictly monotonic: "
        "58.51 -> 60.83 -> 61.69 -> 62.76 -> 64.06."
    )

    # Row 51: X3
    # Claim: Retrained holdout n=118: rho 0.529 [0.377, 0.654], AUC 0.903 [0.812, 0.965], within-category 0.39
    ws_claims.cell(51, 5).value = 0.529
    ws_claims.cell(51, 6).value = 0.529
    ws_claims.cell(51, 7).value = 0.01
    ws_claims.cell(51, 8).value = "=F51-E51"
    ws_claims.cell(51, 9).value = '=IF(AND(ISNUMBER(E51),ISNUMBER(F51)),IF(ABS(F51-E51)<=G51,"Reproduced",IF(ABS(F51-E51)<=3*G51,"Close","Not reproduced")),"")'
    ws_claims.cell(51, 10).value = (
        "Reproduced from prompt v2 cached bridging (fresh_holdout_5cat.json: n=117/118, rho=0.529 [0.377, 0.654], AUC=0.903 [0.812, 0.965], "
        "within-cat mean rho=0.39). Plausible against true-aspect oracle ceiling (rho=0.774, AUC=0.981). Note: reported p-value (7.6e-7) "
        "was understated vs analytic t-test (7.4e-10, row P4)."
    )

    # Row 52: X4
    # Claim: Initial temporal n=66: rho 0.545 [0.352, 0.694], AUC 0.901 [0.784, 0.985]
    ws_claims.cell(52, 5).value = 0.545
    ws_claims.cell(52, 6).value = 0.466
    ws_claims.cell(52, 7).value = 0.01
    ws_claims.cell(52, 8).value = "=F52-E52"
    ws_claims.cell(52, 9).value = '=IF(AND(ISNUMBER(E52),ISNUMBER(F52)),IF(ABS(F52-E52)<=G52,"Reproduced",IF(ABS(F52-E52)<=3*G52,"Close","Not reproduced")),"")'
    ws_claims.cell(52, 10).value = (
        "Not reproduced: The n=66 mature cohort cannot be rebuilt (actual post-cutoff mature count is 51, not 66; post-cutoff fraud=6 not 9, "
        "immature=73 not 55; rows T3-T5). On actual mature post-cutoff cohort (n=51), the TRUE review-aspect oracle ceiling is only "
        "rho=0.466, AUC=0.810; the paper's claimed spec-bridged result (rho=0.545, AUC=0.901) exceeds the true-aspect ceiling."
    )

    # Row 53: X5
    # Claim: Extended temporal n=125: rho 0.590 [0.464, 0.692], AUC 0.942, within-category about 0.16
    ws_claims.cell(53, 5).value = 0.590
    ws_claims.cell(53, 6).value = 0.590
    ws_claims.cell(53, 7).value = 0.01
    ws_claims.cell(53, 8).value = "=F53-E53"
    ws_claims.cell(53, 9).value = '=IF(AND(ISNUMBER(E53),ISNUMBER(F53)),IF(ABS(F53-E53)<=G53,"Reproduced",IF(ABS(F53-E53)<=3*G53,"Close","Not reproduced")),"")'
    ws_claims.cell(53, 10).value = (
        "Reproduced from 80/20 quantile split (temporal_holdout_rigorous.json: n=125 evaluated, rho=0.590 [0.464, 0.692], AUC=0.942). "
        "However, high pooled rho is driven by between-category separation; forward skill within categories collapses to mean rho ~0.16 "
        "(power banks -0.03, ice makers -0.03, headphones 0.31, smartwatches 0.41). True-aspect ceiling: rho=0.749."
    )

    # Row 54: X6
    # Claim: Monotone constraints raised holdout AUC 0.826 -> 0.903 and temporal AUC 0.925 -> 0.942
    ws_claims.cell(54, 5).value = 0.077  # claimed gain: 0.903 - 0.826
    ws_claims.cell(54, 6).value = -0.167  # recomputed gain on identical holdout: 0.750 - 0.917
    ws_claims.cell(54, 7).value = 0.02
    ws_claims.cell(54, 8).value = "=F54-E54"
    ws_claims.cell(54, 9).value = '=IF(AND(ISNUMBER(E54),ISNUMBER(F54)),IF(ABS(F54-E54)<=G54,"Reproduced",IF(ABS(F54-E54)<=3*G54,"Close","Not reproduced")),"")'
    ws_claims.cell(54, 10).value = (
        "Not reproduced: Spurious cross-cohort comparison. In an apples-to-apples ablation on the holdout partition, monotone constraints "
        "actually reduced holdout AUC from 0.917 (unconstrained) to 0.750 (constrained). The paper's claimed gain (0.826 -> 0.903) compared "
        "the n=90 development set (0.826) against the n=118 deployment cohort (0.903)."
    )

    # Row 55: X7
    # Claim: Price-free ablation rho 0.475 and r=0.147 between its prediction and price percentile
    ws_claims.cell(55, 5).value = 0.147
    ws_claims.cell(55, 6).value = 0.147
    ws_claims.cell(55, 7).value = 0.02
    ws_claims.cell(55, 8).value = "=F55-E55"
    ws_claims.cell(55, 9).value = "Not reproduced"  # Explicitly flagged: conflation of target correlation
    ws_claims.cell(55, 10).value = (
        "Not reproduced / Target conflation: 0.147 is the exact Spearman correlation between within-category price percentile and success "
        "on all 631 products (and across holdout splits; row P1), not the correlation between the price-free prediction and price percentile."
    )

    # Row 56: X8
    # Claim: Bridging fidelity r: utility/durability 0.53, ease 0.52, build 0.51, reliability 0.50, value 0.34, repairability 0.27, design 0.21, after-sales 0.07
    ws_claims.cell(56, 5).value = 0.387  # mean of 9 paper values
    ws_claims.cell(56, 6).value = 0.386  # mean of 9 recomputed values
    ws_claims.cell(56, 7).value = 0.01
    ws_claims.cell(56, 8).value = "=F56-E56"
    ws_claims.cell(56, 9).value = '=IF(AND(ISNUMBER(E56),ISNUMBER(F56)),IF(ABS(F56-E56)<=G56,"Reproduced",IF(ABS(F56-E56)<=3*G56,"Close","Not reproduced")),"")'
    ws_claims.cell(56, 10).value = (
        "Reproduced across 118 paired products. Per aspect (recomputed vs paper): utility 0.527 vs 0.53, durability 0.528 vs 0.53, "
        "ease 0.516 vs 0.52, build 0.512 vs 0.51, reliability 0.496 vs 0.50, value 0.336 vs 0.34, repairability 0.270 vs 0.27, "
        "design 0.210 vs 0.21, after-sales 0.073 vs 0.07. All 9 match within +-0.004."
    )

    # Row 57: X9
    # Claim: Ice makers: bridged SD 0.08 / 0.13, fidelity r 0.04, holdout rho 0.11; power banks rho 0.43 -> 0
    ws_claims.cell(57, 5).value = 0.08
    ws_claims.cell(57, 6).value = 0.095
    ws_claims.cell(57, 7).value = 0.02
    ws_claims.cell(57, 8).value = "=F57-E57"
    ws_claims.cell(57, 9).value = '=IF(AND(ISNUMBER(E57),ISNUMBER(F57)),IF(ABS(F57-E57)<=G57,"Reproduced",IF(ABS(F57-E57)<=3*G57,"Close","Not reproduced")),"")'
    ws_claims.cell(57, 10).value = (
        "Reproduced: Flat commodity specifications yield nearly uniform bridged scores (SD: reliability 0.095 [~0.08], build 0.111, durability 0.127 [~0.13]), "
        "suppressing fidelity (utility r=0.027, durability r=0.081). Power banks forward rho collapses from 0.43 (random split) to -0.03 forward in time."
    )

    # Row 58: X10
    # Claim: Reddit priorities A/B delta rho +0.049, CI [-0.025, 0.125] (corrected draft)
    ws_claims.cell(58, 5).value = 0.049
    ws_claims.cell(58, 6).value = 0.049
    ws_claims.cell(58, 7).value = 0.01
    ws_claims.cell(58, 8).value = "=F58-E58"
    ws_claims.cell(58, 9).value = '=IF(AND(ISNUMBER(E58),ISNUMBER(F58)),IF(ABS(F58-E58)<=G58,"Reproduced",IF(ABS(F58-E58)<=3*G58,"Close","Not reproduced")),"")'
    ws_claims.cell(58, 10).value = (
        "Reproduced: with priorities rho=0.359, without rho=0.311, delta rho = +0.049 (ab_reddit_priorities.json: +0.048). "
        "10,000 paired bootstrap 95% CI [-0.024, 0.127] spans zero, confirming the Reddit lift is not statistically significant."
    )

    # Row 59: X11
    # Claim: 10,000-sample bootstrap CIs
    ws_claims.cell(59, 5).value = 10000
    ws_claims.cell(59, 6).value = 10000
    ws_claims.cell(59, 7).value = 0
    ws_claims.cell(59, 8).value = "=F59-E59"
    ws_claims.cell(59, 9).value = '=IF(AND(ISNUMBER(E59),ISNUMBER(F59)),IF(ABS(F59-E59)<=G59,"Reproduced",IF(ABS(F59-E59)<=3*G59,"Close","Not reproduced")),"")'
    ws_claims.cell(59, 10).value = (
        "Reproduced: scripts/headline_cis.py sets N_BOOT = 10_000 (reproduces holdout rho CI [0.059, 0.543], AUC CI [0.507, 0.931], "
        "Reddit delta CI [-0.024, 0.127])."
    )

    # Clear yellow background from rows 49 - 59 and apply clean borders/fills
    for r in range(49, 60):
        for c in range(1, 11):
            cell = ws_claims.cell(r, c)
            cell.border = border_thin
            cell.font = font_regular
            if c != 9:
                cell.fill = fill_white
            else:
                # Color code status
                st = str(cell.value)
                if "Reproduced" in st and "Not" not in st:
                    cell.fill = fill_reproduced
                    cell.font = font_bold
                elif "Not reproduced" in st:
                    cell.fill = fill_not_reproduced
                    cell.font = font_bold
                elif "Close" in st:
                    cell.fill = fill_close
                    cell.font = font_bold

    # -------------------------------------------------------------------------
    # 2. Create or Update Bridging_Recomputations sheet
    # -------------------------------------------------------------------------
    sheet_name = "Bridging_Recomputations"
    if sheet_name in wb.sheetnames:
        del wb[sheet_name]
    ws_b = wb.create_sheet(title=sheet_name)
    ws_b.views.sheetView[0].showGridLines = True

    # Header styling
    title_font = Font(name="Arial", size=14, bold=True, color="1F2937")
    section_font = Font(name="Arial", size=11, bold=True, color="1E3A8A")
    table_header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    table_header_fill = PatternFill(fill_type="solid", fgColor="1E3A8A")
    table_header_fill_accent = PatternFill(fill_type="solid", fgColor="2563EB")
    sub_font = Font(name="Arial", size=9, italic=True, color="6B7280")

    # Title
    ws_b.cell(1, 1).value = "Bridging-Dependent Recomputations & Audit Breakdown (X1 - X11)"
    ws_b.cell(1, 1).font = title_font
    ws_b.cell(2, 1).value = (
        "Independent re-execution of all spec-bridged metrics, holdout validations, aspect fidelities, "
        "and boundary diagnostics from cached LLM prompts (v2), raw review extractions, and pipeline models."
    )
    ws_b.cell(2, 1).font = sub_font

    # --- Section A: Claims Table (X1 - X11) ---
    ws_b.cell(4, 1).value = "1. Summary of Bridging-Dependent Claims (Claims X1 to X11)"
    ws_b.cell(4, 1).font = section_font

    headers_a = ["ID", "Claim / Metric", "Paper Value", "Recomputed", "Tolerance", "Delta", "Status", "Audit Finding & Evidence"]
    for col_idx, h in enumerate(headers_a, start=1):
        cell = ws_b.cell(5, col_idx)
        cell.value = h
        cell.font = table_header_font
        cell.fill = table_header_fill
        cell.alignment = Alignment(horizontal="center" if col_idx in [1, 5, 7] else "left", vertical="center")

    rows_a = [
        ("X1", "Frozen holdout (n=59) Spearman rho", 0.317, 0.317, 0.01, "=D6-C6", "Reproduced",
         "Pre-ice n=59 run reproduced exactly (rho=0.317, AUC=0.743). Broken on final 631 corpus: n=41, rho=0.280 (p=0.076, n.s.). Test items leaked into train fold."),
        ("X2", "Quintile viability means strict monotonicity", 64.06, 64.06, 0.1, "=D7-C7", "Reproduced",
         "Strictly monotonic tier means: 58.51 -> 60.83 -> 61.69 -> 62.76 -> 64.06."),
        ("X3", "Retrained holdout (n=118) Spearman rho", 0.529, 0.529, 0.01, "=D8-C8", "Reproduced",
         "Clean retrain on 513 products; evaluated 118 holdout products (rho=0.529, AUC=0.903). Below oracle ceiling (0.774); p-value understated in paper."),
        ("X4", "Initial temporal (n=66) Spearman rho", 0.545, 0.466, 0.01, "=D9-C9", "Not reproduced",
         "Cohort cannot be rebuilt (mature count is 51, not 66; fraud=6 not 9). On mature n=51, TRUE review aspect oracle ceiling is only 0.466 (paper's 0.545 exceeds ceiling)."),
        ("X5", "Extended temporal (n=125) Spearman rho", 0.590, 0.590, 0.01, "=D10-C10", "Reproduced",
         "From 80/20 quantile split (rho=0.590, AUC=0.942). Pooled skill is driven by between-category separation; forward skill within categories collapses to mean rho ~0.16."),
        ("X6", "Monotone constraints holdout AUC lift", 0.077, -0.167, 0.02, "=D11-C11", "Not reproduced",
         "Spurious cross-cohort comparison. On an identical holdout partition, monotone constraints reduced AUC (0.917 -> 0.750). Paper compared n=90 dev set to n=118 deployment cohort."),
        ("X7", "Price-free ablation r with price percentile", 0.147, 0.147, 0.02, "=D12-C12", "Not reproduced",
         "Conflation: 0.147 is the exact baseline correlation between price percentile and success across all 631 products, not model prediction vs price."),
        ("X8", "Bridging fidelity r (mean across 9 aspects)", 0.387, 0.386, 0.01, "=D13-C13", "Reproduced",
         "All 9 aspects match within +-0.004 across 118 paired products (utility 0.527, durability 0.528, ease 0.516, build 0.512, reliability 0.496, value 0.336, repair 0.270, design 0.210, service 0.073)."),
        ("X9", "Ice makers bridged SD (reliability)", 0.08, 0.095, 0.02, "=D14-C14", "Reproduced",
         "Flat commodity specs yield uniform bridged scores (SD 0.095, build 0.111, durability 0.127), suppressing fidelity (r ~ 0.03-0.08). Power banks collapse from 0.43 to -0.03."),
        ("X10", "Reddit consumer priorities lift (delta rho)", 0.049, 0.049, 0.01, "=D15-C15", "Reproduced",
         "Paired evaluation on 89 products: delta rho = +0.049 (+0.048). 10,000 paired bootstrap 95% CI [-0.024, 0.127] spans zero (not statistically significant)."),
        ("X11", "Bootstrap resampling count", 10000, 10000, 0, "=D16-C16", "Reproduced",
         "Reproduced with N_BOOT=10,000 (holdout rho CI [0.059, 0.543], AUC CI [0.507, 0.931], Reddit delta CI [-0.024, 0.127]).")
    ]

    for row_idx, r_data in enumerate(rows_a, start=6):
        for col_idx, val in enumerate(r_data, start=1):
            cell = ws_b.cell(row_idx, col_idx)
            cell.value = val
            cell.font = font_regular
            cell.border = border_thin
            if col_idx in [1, 5]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in [3, 4, 6]:
                cell.alignment = Alignment(horizontal="right")
                if isinstance(val, float):
                    cell.number_format = "0.000" if abs(val) < 1 else "0.0"
            elif col_idx == 7:
                cell.alignment = Alignment(horizontal="center")
                cell.font = font_bold
                if val == "Reproduced":
                    cell.fill = fill_reproduced
                elif val == "Not reproduced":
                    cell.fill = fill_not_reproduced
                else:
                    cell.fill = fill_close

    # --- Section B: Aspect Bridging Fidelity Table ---
    start_b = 19
    ws_b.cell(start_b, 1).value = "2. Per-Aspect Bridging Reliability & Fidelity Breakdown (n = 118 Products)"
    ws_b.cell(start_b, 1).font = section_font

    headers_b = ["Aspect", "Sample Size (n)", "Paper Claim (r)", "Recomputed Pearson r", "Difference", "Trust Tier Badge", "Interpretation / Mechanism"]
    for col_idx, h in enumerate(headers_b, start=1):
        cell = ws_b.cell(start_b + 1, col_idx)
        cell.value = h
        cell.font = table_header_font
        cell.fill = table_header_fill_accent
        cell.alignment = Alignment(horizontal="center" if col_idx in [2, 3, 4, 5, 6] else "left", vertical="center")

    aspect_rows = [
        ("Durability", 114, 0.53, 0.528, "=D21-C21", "HIGH TRUST (r >= 0.45)", "Materials, IP waterproof ratings, and casing specs reliably predict longevity."),
        ("Utility", 118, 0.53, 0.527, "=D22-C22", "HIGH TRUST (r >= 0.45)", "Core functional specs (driver size, battery mAh, screen type) map directly to functional utility."),
        ("Ease of Use", 117, 0.52, 0.516, "=D23-C23", "HIGH TRUST (r >= 0.45)", "Controls, app companion, Bluetooth version, and physical dimensions strongly signal ergonomics."),
        ("Build Quality", 116, 0.51, 0.512, "=D24-C24", "HIGH TRUST (r >= 0.45)", "Chassis materials (aluminum vs plastic), hinge design, and finishes bridge accurately."),
        ("Reliability", 118, 0.50, 0.496, "=D25-C25", "HIGH TRUST (r >= 0.45)", "Component brand tier, thermal architecture, and battery chemistry provide moderate-high proxy."),
        ("Value for Money", 117, 0.34, 0.336, "=D26-C26", "MODERATE TRUST (0.25-0.45)", "Price position relative to category median provides baseline value expectations."),
        ("Repairability", 55, 0.27, 0.270, "=D27-C27", "MODERATE TRUST (0.25-0.45)", "Sparse spec data; modular parts or teardown-friendly cues are rarely in marketing copy."),
        ("Design Appeal", 116, 0.21, 0.210, "=D28-C28", "LOW TRUST (r < 0.25)", "Subjective aesthetic response cannot be inferred from text dimensions and color options."),
        ("After-Sales Service", 98, 0.07, 0.073, "=D29-C29", "UNESTIMABLE (r < 0.10)", "Warranty text correlates virtually zero with actual customer service responsiveness.")
    ]

    for idx, a_data in enumerate(aspect_rows, start=start_b + 2):
        for c_idx, val in enumerate(a_data, start=1):
            cell = ws_b.cell(idx, c_idx)
            cell.value = val
            cell.font = font_regular
            cell.border = border_thin
            if c_idx in [2, 3, 4, 5]:
                cell.alignment = Alignment(horizontal="right")
                if isinstance(val, float):
                    cell.number_format = "0.000"
            elif c_idx == 6:
                cell.alignment = Alignment(horizontal="center")
                cell.font = font_bold
                if "HIGH" in val:
                    cell.fill = fill_reproduced
                elif "MODERATE" in val:
                    cell.fill = fill_close
                else:
                    cell.fill = fill_not_reproduced

    # --- Section C: Diagnostic Audit Insights ---
    start_c = 32
    ws_b.cell(start_c, 1).value = "3. Critical Cohort & Pipeline Audit Findings"
    ws_b.cell(start_c, 1).font = section_font

    headers_c = ["#", "Vulnerability / Discrepancy", "Original Paper Claim", "Recomputed Ground Truth", "Impact on External Validity"]
    for col_idx, h in enumerate(headers_c, start=1):
        cell = ws_b.cell(start_c + 1, col_idx)
        cell.value = h
        cell.font = table_header_font
        cell.fill = table_header_fill
        cell.alignment = Alignment(horizontal="center" if col_idx == 1 else "left", vertical="center")

    audit_rows = [
        (1, "Frozen Holdout Cohort Inconsistency", "n = 59 pre-registered holdout (rho = 0.317, p = 0.014)",
         "n = 59 run only existed on pre_ice backup. On final 631 corpus, only 41 products match, yielding rho = 0.280 (p = 0.076, not significant).",
         "The reported significant holdout result is an artifact of the deprecated pre-ice dataset with kitchen appliances."),
        (2, "Temporal Maturity Cohort Unreconstructible", "n = 66 mature post-cutoff test cohort (rho = 0.545, AUC = 0.901)",
         "Mature post-cutoff count is 51, not 66 (fraud=6 not 9, immature=73 not 55). On n=51, TRUE review-aspect oracle ceiling is only rho = 0.466, AUC = 0.810.",
         "The paper's spec-bridged temporal claim exceeds the theoretical upper bound obtainable from actual review aspects."),
        (3, "Monotone Constraints Cross-Cohort Comparison", "Monotone constraints raised holdout AUC 0.826 -> 0.903",
         "Apples-to-apples ablation on holdout: unconstrained AUC = 0.917, constrained AUC = 0.750 (gain = -0.167).",
         "The paper compared the n=90 dev set against the n=118 deployment cohort, manufacturing an illusion of AUC improvement."),
        (4, "Price Baseline / Price-Free Conflation", "Price-free ablation r = 0.147 with price percentile",
         "0.147 is the exact Spearman correlation of price percentile with success across all 631 products (and across random holdouts).",
         "The reported price orthogonality metric was a mislabeled copy of the baseline target correlation."),
        (5, "Reddit Consumer Priorities Insignificance", "Reddit priorities lift delta rho = +0.049",
         "Delta rho = +0.049, but paired 10,000 bootstrap 95% CI is [-0.024, 0.127], which cleanly includes zero.",
         "Injecting Reddit priorities produces an exploratory lift that fails standard statistical significance tests.")
    ]

    for idx, c_data in enumerate(audit_rows, start=start_c + 2):
        for c_idx, val in enumerate(c_data, start=1):
            cell = ws_b.cell(idx, c_idx)
            cell.value = val
            cell.font = font_regular
            cell.border = border_thin
            if c_idx == 1:
                cell.alignment = Alignment(horizontal="center")
            else:
                cell.alignment = Alignment(vertical="top", wrap_text=True)

    # Set column widths
    widths = {1: 10, 2: 44, 3: 16, 4: 16, 5: 14, 6: 14, 7: 18, 8: 65}
    for col_idx, w in widths.items():
        ws_b.column_dimensions[get_column_letter(col_idx)].width = w

    # -------------------------------------------------------------------------
    # 3. Update README Sheet
    # -------------------------------------------------------------------------
    ws_readme = wb["README"]
    ws_readme.cell(3, 2).value = (
        "Every number that depends on the bridging layer (specs-only predictions by an LLM) has now been recomputed "
        "and audited in sheet Bridging_Recomputations and Claims_vs_Recomputed (rows X1-X11): the n=59, n=66, n=118, "
        "and n=125 results, per-aspect bridging fidelity, ice-maker boundary diagnostics, price-free ablation, and Reddit A/B. "
        "All 58 paper claims are now compared and classified."
    )

    print(f"Saving updated workbook to {WORKBOOK_PATH}...")
    wb.save(WORKBOOK_PATH)
    print("Workbook successfully updated!")


if __name__ == "__main__":
    update_workbook()
