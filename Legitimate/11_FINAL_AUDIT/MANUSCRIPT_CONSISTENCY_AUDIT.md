# Manuscript Consistency Audit

This audit evaluates the final manuscript (`FINAL_MANUSCRIPT.docx`, `FINAL_MANUSCRIPT.pdf`, `FINAL_MANUSCRIPT.md`) against the single source of truth (`FINAL_RESULTS.json`).

## 1. Automated Numerical Audit
The following values from `FINAL_RESULTS.json` were cross-checked across all manuscript text, tables, and figure captions:

| Metric / Term | Expected Value (`FINAL_RESULTS.json`) | Status in Manuscript |
| :--- | :--- | :--- |
| Temporal Cutoff Date | October 31, 2021 23:59:59 UTC | Verified |
| Training Sample Count | 507 products | Verified |
| Test Sample Count | 124 products | Verified |
| Baseline Spearman $\rho$ | 0.5621 (0.562) | Verified |
| Baseline AUC | 0.8899 (0.890) | Verified |
| Baseline RMSE | 21.12 | Verified |
| Promoted Spearman $\rho$ | 0.6720 (0.672) | Verified |
| Promoted AUC | 0.9710 (0.971) | Verified |
| Promoted RMSE | 19.75 | Verified |
| Delta $\Delta \rho$ | +0.1099 (+0.110) | Verified |
| Paired Bootstrap 95% CI | [+0.0485, +0.1833] | Verified |
| Paired Permutation $p$-value | 0.0004 | Verified |
| Unseen-Brand Baseline $\rho$ | 0.5160 (0.516) | Verified |
| Unseen-Brand Promoted $\rho$ | 0.6331 (0.633) | Verified |
| Application External $\rho$ | 0.501 | Verified |
| Application External AUC | 0.873 | Verified |

## 2. Forbidden Terminology Scan
The manuscript was scanned for prohibited or misleading marketing terms:
- **"Sales" as ground truth**: ZERO occurrences. The target is consistently described as a "review-derived market-success proxy".
- **"Revenue" or "units sold"**: ZERO occurrences claiming direct commercial measurement.
- **"Information recovered"**: Replaced with mathematically accurate rank correlation metrics.
- **"Guaranteed success"**: ZERO occurrences. All predictions framed as probabilistic viability estimations.

## 3. Discrepancy & Consistency Verdict
**STATUS: PASSED.** 100% of reported figures, tables, and in-text statistics match the audited experimental records.
