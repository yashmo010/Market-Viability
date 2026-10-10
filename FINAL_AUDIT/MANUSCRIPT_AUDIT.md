# FINAL MANUSCRIPT AUDIT REPORT
**Exhaustive Textual, Statistical, & Cross-Reference Audit — Current Modified Project**  
**Manuscript Title**: *Launch-Blind Product Viability Estimation from Specifications via LLM Aspect Bridging*  
**Format**: IEEE Two-Column Layout (`FINAL_MANUSCRIPT.docx`, `FINAL_MANUSCRIPT.pdf`, `FINAL_MANUSCRIPT.md`)  
**Date**: October 2026  
**Audit Status**: **PASSED (100% FACTUAL CONFORMANCE — ZERO DISCREPANCIES)**  

---

## 1. Core Numerical Verification Against Source of Truth

Every numerical claim in the manuscript prose was traced to `FINAL_RESULTS.json`:

| Statistic / Claim | Target in Text | Source-of-Truth Value | Status |
|---|---|---|---|
| **Promoted Model Spearman $\rho$** | 0.6722 | 0.6722 | **MATCH** |
| **Promoted 95% Bootstrap CI** | [0.5495, 0.7620] | [0.5495, 0.7620] | **MATCH** |
| **Promoted Asymptotic $p$-value** | $1.25 \times 10^{-17}$ | $1.25399 \times 10^{-17}$ | **MATCH** |
| **Promoted Extreme-Group AUC** | 0.9712 | 0.9712 | **MATCH** |
| **Promoted RMSE** | 19.75 | 19.75 | **MATCH** |
| **Promoted MAE** | 16.66 | 16.66 | **MATCH** |
| **Controlled Baseline $\rho$** | 0.5623 | 0.5623 | **MATCH** |
| **Controlled Baseline 95% CI** | [0.4140, 0.6812] | [0.4140, 0.6812] | **MATCH** |
| **Controlled Baseline Asymptotic $p$** | $1.08 \times 10^{-11}$ | $1.07803 \times 10^{-11}$ | **MATCH** |
| **Controlled Baseline AUC** | 0.8904 | 0.8904 | **MATCH** |
| **Controlled Baseline RMSE** | 21.12 | 21.12 | **MATCH** |
| **Paired Improvement $\Delta\rho$** | +0.1099 | +0.1099 | **MATCH** |
| **Paired Bootstrap 95% CI for $\Delta\rho$** | [+0.0485, +0.1833] | [+0.0485, +0.1833] | **MATCH** |
| **Paired Permutation $p$-value** | 0.0004 | 0.0004 | **MATCH** |
| **Unseen Brand Cold-Start $\rho$ ($n=90$)** | 0.6328 (vs 0.5155) | 0.6328 (vs 0.5155) | **MATCH** |
| **Unseen Brand Cold-Start AUC** | 0.9815 (vs 0.8843) | 0.9815 (vs 0.8843) | **MATCH** |
| **External Real-World Cohort ($n=155$) $\rho$** | 0.6120 | 0.6120 | **MATCH** |
| **External Real-World Cohort AUC** | 0.8840 | 0.8840 | **MATCH** |

---

## 2. Statistical Terminology & Distinction Audit

- [x] **Asymptotic $p$-value vs Paired Permutation $p$-value**:
  - The manuscript explicitly labels the asymptotic Spearman test ($p = 1.25 \times 10^{-17}$ under $H_0: \rho = 0$).
  - The manuscript separately and explicitly labels the paired permutation test ($p = 0.0004$ under $H_0: \Delta\rho \le 0$ across 10,000 paired sign-flips).
  - The two quantities are never conflated or presented as interchangeable.
- [x] **Regression vs Classification**:
  - Regression loss is strictly termed **RMSE** and **MAE** on the continuous 0–100 proxy scale.
  - No generic or misleading usage of "accuracy" for regression outputs exists.
  - Classification metrics (ROC-AUC = 0.9712) are explicitly confined to the derived extreme-group decision task (top 20% vs bottom 20%).

---

## 3. Strict Boundary & Non-Contamination Verification

- [x] **Air Fryer Purge**: Global grep across `FINAL_MANUSCRIPT.docx`, `.pdf`, `.md`, and all tables/figures yields exactly **0 occurrences**.
- [x] **Canonical Category Set**: All tables and discussions cite exclusively the 5 canonical categories:
  1. Bluetooth speakers
  2. Ice makers
  3. Power banks
  4. Smartwatches
  5. Wireless headphones
- [x] **Feature Count**: Exactly 24 engineered features (1 price + 9 aspect scores + 9 mention rates + 1 brand tier + 1 category + 3 specification density attributes).
- [x] **Seed Consistency**: Audited seed set `[42, 123, 456, 789, 999]` cited across all reproducibility sections and Table VII.
- [x] **Target Integrity**: Bounded strictly as a *review-derived market-success proxy*. Zero claims of direct unit sales, revenue, profit, or commercial guarantees.

---

## 4. Figure & Table Cross-Reference Integrity

All figures (Figs 1–7) and tables (Tables I–IX) are cited in proper sequential order in the manuscript prose:
- **Fig. 1**: Cited in Section I & Section III (End-to-end architecture pipeline, date-free 300 DPI vector design).
- **Fig. 2**: Cited in Section III (Frozen forward-in-time protocol, strict quarantine barrier, date-free).
- **Fig. 3**: Cited in Section IV-A (Primary performance comparison with bootstrap CIs).
- **Fig. 4**: Cited in Section IV-B (Cold-start unseen brand generalization).
- **Fig. 5**: Cited in Section IV-C (Within-category disaggregated breakdown across 5 categories).
- **Fig. 6**: Cited in Section IV-D (Controlled component ablation study).
- **Fig. 7**: Cited in Section IV-E (Predicted viability vs observed proxy scatter diagnostic).
- **Table I**: Corpus statistics ($n_{\text{train}}=507$, $n_{\text{test}}=124$, $N=631$).
- **Table II**: 24-feature taxonomy & extraction definitions.
- **Table III**: Primary model benchmark (Holdout $n=124$).
- **Table IV**: Controlled component ablation results.
- **Table V**: Within-category breakdown.
- **Table VI**: Cold-start unseen brand performance ($n=90$).
- **Table VII**: Rigorous paired statistical comparisons.
- **Table VIII**: External real-world validation ($n=155$).
- **Table IX**: 6-learner cross-validated benchmark ($n=507$ OOF).

---

## 5. Bibliography & Citation Integrity

- Exactly **50 references** in the bibliography.
- 100% of references (1..50) are cited in sequential order in the main text.
- Zero orphaned or uncited references.
- All references represent verified, reputable peer-reviewed venues (IEEE, ACM, Springer, Elsevier, NeurIPS, ICML, KDD).
