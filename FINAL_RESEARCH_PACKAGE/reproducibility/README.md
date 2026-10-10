# Reproducibility Guide — Legitimate Research Branch

This directory documents the precise computational environment, execution order, random seeds, and instructions required to reproduce all findings, figures, tables, and manuscript metrics reported in the final research artifact.

## 1. System Requirements & Environment
- **Python**: 3.13.12 (compatible with 3.10+)
- **Key Packages**:
  - `xgboost==3.3.0`
  - `scikit-learn==1.8.0`
  - `numpy==2.4.2`
  - `scipy==3.0.1`
  - `pandas==3.0.1`
  - `matplotlib==3.10.0`
  - `seaborn==0.13.2`
  - `python-docx==1.1.2`
  - `pytest==9.0.2`

See `environment.txt` for the full dependency specification.

## 2. Seed Configuration
- Primary model fitting and cross-validation seed: `42`
- Seed stability suite: `[42, 100, 2024, 777, 999]`
- Paired bootstrap and permutation iterations: `10,000` resamples, seed `42`
- Semantic attribute extraction: Deterministic, regex-grounded parser guaranteeing zero stochastic drift.

See `seeds.txt` for full details.

## 3. Data Protocol & Integrity
- **Temporal Cutoff**: October 31, 2021 23:59:59 UTC
- **Training Set**: 507 products strictly pre-cutoff
- **Temporal Test Set**: 124 products strictly post-cutoff (launch-blind)
- **Label Isolation**: Ground truth labels (`SuccessScore`) are physically isolated during all preprocessing, extraction, feature scaling, and hyperparameter decisions.
- **Byte-for-Byte Invariance**: When test labels are physically removed, test predictions remain 100% bit-for-bit identical (`SHA-256: 3f75df2ebaf508ebd4802875f5631bb538fe21557007ba25f82223bb354c4f34`).

## 4. Execution Sequence
Run either `commands.bat` (Windows) or `commands.sh` (Linux/macOS) from the repository root:
```bash
# Windows
Legitimate\10_REPRODUCIBILITY\commands.bat

# Linux / macOS
bash Legitimate/10_REPRODUCIBILITY/commands.sh
```

All generated tables, figures, models, evaluation reports, and the compiled IEEE manuscript (`FINAL_MANUSCRIPT.docx` and `FINAL_MANUSCRIPT.pdf`) will be reproduced deterministically.
