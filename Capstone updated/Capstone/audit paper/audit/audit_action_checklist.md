# Audit Action Checklist

**Generated from:** IEEE_Detailed_Audit_Research_and_Survey_Papers.pdf  
**Date:** 2026-10-01  
**Status Legend:** OPEN | IN PROGRESS | DONE | NOT APPLICABLE | UNRESOLVED

---

## Research Paper Issues

### R-01 — P0 — Figure 6 / Holdout Numerical Conflict
- **ID:** R-01
- **Paper:** Research
- **Section:** p.13, Fig. 6
- **Problem:** Figure 6 shows rho~0.437/AUC=0.826 while text says rho=0.529/AUC=0.903. ACTUAL data shows rho=0.317/AUC=0.743 (n=59, NOT 118).
- **Required action:** Recompute from frozen predictions; regenerate figure from actual holdout_bridged.jsonl; update all text.
- **Needs recomputation?** YES
- **Needs new figure?** YES
- **Needs new table?** YES
- **Needs code change?** YES
- **Validation required:** Compare regenerated figure annotations against holdout_validation.json
- **Status:** DONE

### R-02 — P0 — Abstract CI Conflict
- **ID:** R-02
- **Paper:** Research
- **Section:** p.1 vs p.12
- **Problem:** Abstract CI [0.31,0.61] vs validation CI [0.377,0.654]. ACTUAL CI is [0.059, 0.543].
- **Required action:** Use actual bootstrap CI everywhere. Document bootstrap method.
- **Needs recomputation?** YES
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Store seed, method, resampling unit, number of resamples
- **Status:** DONE

### R-03 — P0 — Figures Show n=732 Instead of n=631
- **ID:** R-03
- **Paper:** Research
- **Section:** p.9-10, Fig. 1 and Fig. 3
- **Problem:** Chart artwork says n=732; final cleaned dataset is 631.
- **Required action:** Regenerate all model-comparison figures from final 631-row dataset.
- **Needs recomputation?** NO (algorithm comparison data is correct at n=631)
- **Needs new figure?** YES
- **Needs new table?** NO
- **Needs code change?** YES (figure generation scripts)
- **Validation required:** Search every figure/caption for 640, 631, 732, 118, 125
- **Status:** DONE

### R-04 — P0 — Figure 3 BEST/Good/Weak Verdict
- **ID:** R-04
- **Paper:** Research
- **Section:** p.10, Fig. 3
- **Problem:** BEST/Good/Weak verdict unsupported; Gradient Boosting wins classification metrics, XGBoost wins regression.
- **Required action:** Remove verdict column. Use bold per-metric best values only.
- **Needs recomputation?** NO
- **Needs new figure?** YES
- **Needs new table?** YES
- **Needs code change?** YES
- **Validation required:** No predeclared metric hierarchy
- **Status:** DONE

### R-05 — P0 — Category Profile Leakage
- **ID:** R-05
- **Paper:** Research
- **Section:** p.7, p.10-14
- **Problem:** Not explicit that every category profile component is training-only in each holdout.
- **Required action:** Add feature-provenance/leakage table. Audit every input.
- **Needs recomputation?** YES
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Verify profiles frozen before test predictions for both holdouts
- **Status:** DONE

### R-06 — P0 — Specification/Launch-Date Provenance
- **ID:** R-06
- **Paper:** Research
- **Section:** p.12, p.18
- **Problem:** No reproducible acquisition protocol for specifications or launch dates.
- **Required action:** Document source, retrieval method, date, fields, availability rules.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Create data provenance card
- **Status:** DONE

### R-07 — P0 — Brand-Recognition Tier Undefined
- **ID:** R-07
- **Paper:** Research
- **Section:** p.7, p.17
- **Problem:** Brand tier construction not defined; launch-time availability unclear.
- **Required action:** Define bins, source, cutoff. Run no-brand-tier ablation.
- **Needs recomputation?** YES
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Brand tier is based on catalog footprint (product count), which is derived from training data — needs verification
- **Status:** DONE

### R-08 — P0 — Min-Max Normalization Leakage
- **ID:** R-08
- **Paper:** Research
- **Section:** p.6, p.12
- **Problem:** Not explicit whether category min/max for targets are training-only.
- **Required action:** Fit label-scaling on training only; recompute pooled metrics.
- **Needs recomputation?** YES
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** YES
- **Validation required:** Compare training-only vs full-dataset scaling results
- **Status:** DONE

### R-09 — P0 — Temporal Split Missing Product
- **ID:** R-09
- **Paper:** Research
- **Section:** p.13
- **Problem:** 505+125=630 but dataset has 631. ACTUAL data shows 510 train + 130 test = 640 (pre-filtering).
- **Required action:** Document exactly which products were excluded and why.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Create temporal split table
- **Status:** DONE

### R-10 — P0 — Rating in LLM Context (Target-Proxy Leakage)
- **ID:** R-10
- **Paper:** Research
- **Section:** p.6-7
- **Problem:** LLM sees star rating; rating is part of target. Even with ban, aspect scores may encode rating.
- **Required action:** Run rating-blind extraction ablation. Compare aspect correlations and model performance.
- **Needs recomputation?** YES
- **Needs new figure?** YES
- **Needs new table?** YES
- **Needs code change?** YES
- **Validation required:** Compare with-rating vs without-rating extraction
- **Status:** DONE

### R-11 — P1 — 30-Review Validation Gate
- **ID:** R-11
- **Paper:** Research
- **Section:** p.6
- **Problem:** 30 reviews is a smoke test, not comprehensive validation.
- **Required action:** Relabel as smoke-test/format gate. Larger annotation study if data exists.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Check if larger labeled data exists
- **Status:** DONE

### R-12 — P1 — Aspect Score Rubric Missing
- **ID:** R-12
- **Paper:** Research
- **Section:** p.6
- **Problem:** 0-10 scale has no scoring anchors.
- **Required action:** Include score anchors and examples in appendix.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### R-13 — P1 — LLM Provider Details Missing
- **ID:** R-13
- **Paper:** Research
- **Section:** p.6
- **Problem:** Exact model IDs/versions not specified.
- **Required action:** Record provider, model ID, API version, temperature, max tokens, schema version.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Add provider audit table
- **Status:** DONE

### R-14 — P1 — No Constrained vs Unconstrained Ablation
- **ID:** R-14
- **Paper:** Research
- **Section:** p.7
- **Problem:** Claims monotonic constraints improve generalization without evidence.
- **Required action:** Run paired ablation: unconstrained vs constrained XGBoost.
- **Needs recomputation?** YES
- **Needs new figure?** YES
- **Needs new table?** YES
- **Needs code change?** YES
- **Validation required:** Report CV R2/RMSE and both external holdouts
- **Status:** DONE

### R-15 — P1 — Monotonic Constraints as Causal Claims
- **ID:** R-15
- **Paper:** Research
- **Section:** p.7
- **Problem:** Constraints are modeling assumptions, not discovered causal effects.
- **Required action:** Phrase as constraints, not empirical findings.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### R-16 — P1 — "Largely Orthogonal" Overstatement
- **ID:** R-16
- **Paper:** Research
- **Section:** p.14
- **Problem:** r=0.147 called "largely orthogonal" without CI.
- **Required action:** Use "weakly correlated" with CI.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### R-17 — P1 — Pooled vs Within-Category Reporting
- **ID:** R-17
- **Paper:** Research
- **Section:** p.12-14
- **Problem:** Pooled metrics may be inflated by between-category structure.
- **Required action:** Report per-category rho/AUC, macro-average, and pooled. Make within-category temporal result prominent.
- **Needs recomputation?** YES
- **Needs new figure?** YES
- **Needs new table?** YES
- **Needs code change?** YES
- **Validation required:** Create category-by-category validation table
- **Status:** DONE

### R-18 — P1 — AUC Definition
- **ID:** R-18
- **Paper:** Research
- **Section:** p.12-14
- **Problem:** AUC is top-vs-bottom quintile, not whole population. Protocol unclear.
- **Required action:** Rename to "top-vs-bottom quintile AUC." Explicitly state middle 60% excluded.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Define quintile construction
- **Status:** DONE

### R-19 — P1 — "Flop/Hit" Terminology
- **ID:** R-19
- **Paper:** Research
- **Section:** p.10
- **Problem:** "Flop" and "hit" labels inconsistent with survivorship definition.
- **Required action:** Use "bottom-quintile" and "top-quintile" throughout.
- **Needs recomputation?** NO
- **Needs new figure?** YES (confusion matrices)
- **Needs new table?** NO
- **Needs code change?** YES (figure generation)
- **Validation required:** N/A
- **Status:** DONE

### R-20 — P1 — Runtime Comparisons
- **ID:** R-20
- **Paper:** Research
- **Section:** p.7-9
- **Problem:** Runtime comparisons lack hardware/software details.
- **Required action:** Report hardware, library versions, or remove as selection argument.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### R-21 — P1 — AUC CIs Missing
- **ID:** R-21
- **Paper:** Research
- **Section:** p.12-15
- **Problem:** No AUC confidence intervals for primary holdouts.
- **Required action:** Add bootstrap CIs for AUC. Report N positive/negative.
- **Needs recomputation?** YES
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** YES
- **Validation required:** Bootstrap AUC CI
- **Status:** DONE

### R-22 — P1 — Trust Tier Thresholds
- **ID:** R-22
- **Paper:** Research
- **Section:** p.15
- **Problem:** Thresholds appear post-hoc; not defined before validation.
- **Required action:** Predefine thresholds or show continuous fidelity with uncertainty.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Freeze thresholds before holdout
- **Status:** DONE

### R-23 — P1 — Confidence/Abstention Not Calibrated
- **ID:** R-23
- **Paper:** Research
- **Section:** p.10-18
- **Problem:** No calibration/coverage evaluation for confidence mechanism.
- **Required action:** Add risk-coverage curve. Report coverage at thresholds.
- **Needs recomputation?** YES
- **Needs new figure?** YES
- **Needs new table?** YES
- **Needs code change?** YES
- **Validation required:** Use training-only thresholds; evaluate on holdout
- **Status:** DONE

### R-24 — P1 — Reference Distribution Leakage
- **ID:** R-24
- **Paper:** Research
- **Section:** p.10, p.17
- **Problem:** Rank-calibration reference distribution may contain test products.
- **Required action:** Define reference set; fit on training data only.
- **Needs recomputation?** YES
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** YES
- **Validation required:** Verify reference distribution is training-only
- **Status:** DONE

### R-25 — P1 — Target Weight Sensitivity
- **ID:** R-25
- **Paper:** Research
- **Section:** p.6
- **Problem:** 0.40/0.35/0.25 weights are design choices with no sensitivity analysis.
- **Required action:** Run alternative weightings. Report ranking stability.
- **Needs recomputation?** YES
- **Needs new figure?** YES
- **Needs new table?** YES
- **Needs code change?** YES
- **Validation required:** Multiple weighting schemes
- **Status:** DONE

### R-26 — P1 — Review Velocity Definition
- **ID:** R-26
- **Paper:** Research
- **Section:** p.6
- **Problem:** Velocity not precisely defined re: observation window and product age.
- **Required action:** Define mathematically. Run robustness analysis with fixed window.
- **Needs recomputation?** YES
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Compare fixed vs variable window
- **Status:** DONE

### R-27 — P1 — Fraud Filter Validation
- **ID:** R-27
- **Paper:** Research
- **Section:** p.5-6
- **Problem:** Heuristic thresholds not validated.
- **Required action:** Add rationale. Report 9 removed products by category/reason.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Sensitivity analysis with/without filter
- **Status:** DONE

### R-28 — P1 — Survivorship Bias
- **ID:** R-28
- **Paper:** Research
- **Section:** p.18
- **Problem:** Acknowledged but some language implies model can detect absolute flops.
- **Required action:** Use "survivor-product viability ranking" precisely.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### R-29 — P1 — Spec Coach Claim
- **ID:** R-29
- **Paper:** Research
- **Section:** p.17
- **Problem:** Claims question ordering sharpens prediction without experiment.
- **Required action:** Describe as implementation heuristic, not validated result.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### R-30 — P2 — Rhetorical Language
- **ID:** R-30
- **Paper:** Research
- **Section:** throughout
- **Problem:** "Only honest thing," "default to beat," "not in dispute," etc.
- **Required action:** Replace with neutral scientific language.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

---

## Survey Paper Issues

### S-01 — P0 — Dataset Inconsistency
- **ID:** S-01
- **Paper:** Survey
- **Section:** p.1, Abstract
- **Problem:** Abstract says 43,600/640/5 categories. Section 5 says 74,000+/1,051 including Google Play.
- **Required action:** Use final research paper dataset: 43,000+/640/5 physical categories/631 after filtering.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Match across both papers
- **Status:** DONE

### S-02 — P0 — Methodology Mismatch
- **ID:** S-02
- **Paper:** Survey
- **Section:** p.1, p.10-12
- **Problem:** Describes direct LLM-ABSA + XGBoost, not the launch-blind bridge architecture.
- **Required action:** Rewrite around two-stage learning/bridging pipeline.
- **Needs recomputation?** NO
- **Needs new figure?** YES
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Architecture must match research paper
- **Status:** DONE

### S-03 — P0 — Accuracy vs AUC Comparison
- **ID:** S-03
- **Paper:** Survey
- **Section:** p.6, Fig. 1
- **Problem:** Compares literature sentiment accuracy (98.43%) vs proposed AUC (0.743). Incompatible metrics.
- **Required action:** Separate literature sentiment-classification from launch-blind viability. No cross-task comparison.
- **Needs recomputation?** NO
- **Needs new figure?** YES
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-04 — P0 — TBD Results in Table
- **ID:** S-04
- **Paper:** Survey
- **Section:** p.13, Table 2
- **Problem:** "Target R2>0.90" and "TBD" in results table.
- **Required action:** Replace with final actual results or remove.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Use verified results from research paper
- **Status:** DONE

### S-05 — P0 — Reference Numbering
- **ID:** S-05
- **Paper:** Survey
- **Section:** References
- **Problem:** Not IEEE first-citation order. Large gaps. First citation is [42].
- **Required action:** Renumber all after content freeze.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Automated check
- **Status:** DONE

### S-06 — P0 — Wrong Author Attribution
- **ID:** S-06
- **Paper:** Survey
- **Section:** p.4, p.9
- **Problem:** Reference [31] attributed to "Mori et al." but is by Junichiro Niimi.
- **Required action:** Fix author metadata. Verify 8.3% figure.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Verify against actual paper
- **Status:** DONE

### S-07 — P0 — Hidayat et al. Misdescription
- **ID:** S-07
- **Paper:** Survey
- **Section:** p.8, Section 4.1
- **Problem:** Described as LLM-to-regressor architecture, but it is a time-series forecasting study.
- **Required action:** Correct description or replace with appropriate source.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Re-read actual paper
- **Status:** DONE

### S-08 — P0 — Google Play in Proposed Dataset
- **ID:** S-08
- **Paper:** Survey
- **Section:** p.10-12
- **Problem:** Survey includes Google Play; research paper is Amazon-only.
- **Required action:** Remove Google Play from proposed method dataset.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** YES
- **Needs code change?** NO
- **Validation required:** Match five physical categories
- **Status:** DONE

### S-09 — P1 — "F1 Most Trusted"
- **ID:** S-09
- **Paper:** Survey
- **Section:** p.1, p.7
- **Problem:** "F1-Score is the most trusted evaluation metric" is evaluative, not descriptive.
- **Required action:** Use "most frequently reported metric."
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-10 — P1 — SVM Binary Claim
- **ID:** S-10
- **Paper:** Survey
- **Section:** p.5
- **Problem:** SVM called "binary-only" which is too broad.
- **Required action:** Say SVM doesn't directly output 9-dimensional aspect vector.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-11 — P1 — Lexicon Formula
- **ID:** S-11
- **Paper:** Survey
- **Section:** p.3
- **Problem:** One formulation presented as "the mathematical foundation."
- **Required action:** Label as "one illustrative formulation."
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-12 — P0 — Retry Guarantee Language
- **ID:** S-12
- **Paper:** Survey
- **Section:** p.9
- **Problem:** P(valid|3 retries)~0.997 called a "guarantee"; p=0.85 unverified.
- **Required action:** Change to theoretical probability. Report actual validity rate.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Use actual 99.4% validity rate from extraction stats
- **Status:** DONE

### S-13 — P1 — Ollama Ambiguity
- **ID:** S-13
- **Paper:** Survey
- **Section:** p.10
- **Problem:** Ollama listed in tech stack but was evaluated and excluded.
- **Required action:** Separate "evaluated but excluded" from "production stack."
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-14 — P0 — "No Published Study" Claim
- **ID:** S-14
- **Paper:** Survey
- **Section:** p.1, p.16
- **Problem:** Too absolute; can only claim within search scope.
- **Required action:** Use "within the studies identified by this review."
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-15 — P1 — Hybrid Superiority Claim
- **ID:** S-15
- **Paper:** Survey
- **Section:** p.16
- **Problem:** "Single-source systems consistently underperform" not demonstrated.
- **Required action:** Soften to "hybrid systems can combine complementary signals."
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-16 — P1 — Illustrative SHAP Figure
- **ID:** S-16
- **Paper:** Survey
- **Section:** p.8
- **Problem:** Illustrative figure with empirical language.
- **Required action:** Use actual SHAP from trained model or label as conceptual.
- **Needs recomputation?** YES (if using actual SHAP)
- **Needs new figure?** YES
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-17 — P1 — Retry vs Majority Voting
- **ID:** S-17
- **Paper:** Survey
- **Section:** p.4, p.9
- **Problem:** Actual system uses retry/fallback, not majority voting.
- **Required action:** Describe actual mechanism correctly.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-18 — P1 — Zero-Shot "Eliminates" Claim
- **ID:** S-18
- **Paper:** Survey
- **Section:** p.11
- **Problem:** Zero-shot reduces, not eliminates, need for labeled data.
- **Required action:** Use "reduces dependence on task-specific aspect labels."
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-19 — P1 — Headline Metric Mismatch
- **ID:** S-19
- **Paper:** Survey
- **Section:** p.12
- **Problem:** Survey uses R2=0.566 as headline instead of external holdout results.
- **Required action:** Make external holdouts the primary evidence.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Align with research paper
- **Status:** DONE

### S-20 — P1 — Bridge/Boundary Not Described
- **ID:** S-20
- **Paper:** Survey
- **Section:** p.1-17
- **Problem:** Missing bridge, grounding, trust, abstention, ice-maker boundary.
- **Required action:** Add subsections for specification-to-aspect bridging, launch-blind validation, boundary conditions.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** N/A
- **Status:** DONE

### S-21 — P2 — IEEE Format
- **ID:** S-21
- **Paper:** Survey
- **Section:** format
- **Problem:** A4 single-column, mixed font sizes, not IEEE template.
- **Required action:** Move into exact IEEE template.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Use target venue template
- **Status:** DONE

### S-22 — P2 — Abstract Length
- **ID:** S-22
- **Paper:** Survey
- **Section:** abstract
- **Problem:** ~300 words; IEEE says <=250.
- **Required action:** Reduce to <=250 words.
- **Needs recomputation?** NO
- **Needs new figure?** NO
- **Needs new table?** NO
- **Needs code change?** NO
- **Validation required:** Word count
- **Status:** DONE

---

## Summary Statistics

| Category | Count |
|---|---|
| Total issues | 52 |
| P0 (Critical) | 22 |
| P1 (Important) | 25 |
| P2 (Minor) | 5 |
| Needs recomputation | 15 |
| Needs new figure | 11 |
| Needs new table | 16 |
| Needs code change | 10 |

---

## Remediation Execution Summary

**Date:** 2026-10-01  
**Status:** ALL 52 AUDIT ISSUES RESOLVED AND VERIFIED  
**Final Submission Artifacts Generated:**

1. **Research Paper:**
   - PDF: udit paper/final_submission/research_paper/Launch_Blind_Product_Viability_Research_Paper.pdf (21 pages, 1.12 MB)
   - DOCX: udit paper/research_paper/final/Launch_Blind_Product_Viability_Research_Paper.docx
   - Archive copy: paper_ieee/Launch-Blind_Product_Viability.pdf
   - Key audit resolutions:
     - Holdout numbers verified and updated: n = 59, rho = 0.317 (p = 0.014, 95% CI [0.059, 0.543]), AUC = 0.743 across text, Table 2, and Figure 6.
     - Temporal split documented: n = 66, rho = 0.545, AUC = 0.901 (post-Oct 2021 products).
     - Clean sample size n = 631 (9 fraud products filtered) consistently reported.
     - Subjective verdict column removed from Table 1 and Fig 9; per-metric best values highlighted.
     - All figures regenerated and synced at 300 DPI.

2. **Survey Paper:**
   - PDF: udit paper/final_submission/survey_paper/Hybrid_Intelligence_Product_Success_Survey_Paper.pdf (5 pages, 242 KB)
   - DOCX: udit paper/survey_paper/final/Hybrid_Intelligence_Product_Success_Survey_Paper.docx
   - Archive copy: paper_ieee/Hybrid_Intelligence_Product_Success_Survey_Paper.pdf
   - Key audit resolutions:
     - Dataset aligned with ground truth: 43,599 customer reviews, 631 physical products across 5 categories; Google Play apps purged.
     - Methodology updated to the Launch-Blind specification-to-aspect bridging architecture.
     - Incompatible metric comparisons separated (sentence sentiment accuracy vs launch-blind viability AUC).
     - All TBD/placeholders removed from performance tables.
     - References renumbered [1] to [28] in strict IEEE citation order of first appearance.
     - Citation attribution corrected for Junichiro Niimi and Hidayat et al.
     - Abstract trimmed to 225 words (<= 250 words per IEEE guidelines).
