# Project Structure Specification

## Root Layout
```
c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\
├── Capstone updated/Capstone/     # ORIGINAL REPOSITORY (Immutable & Protected)
│   ├── src/                       # Production source code
│   ├── models/                    # Model weights & benchmarks
│   ├── data/                      # Raw, extracted, and final datasets
│   ├── strict_temporal/           # Frozen temporal split (507 train / 124 test)
│   ├── tests/                     # Test suite (74 project-wide tests)
│   └── audit/                     # Initial audits and logs
├── Legitimate/                    # INDEPENDENT EXPERIMENTAL BRANCH
│   ├── 00_PROJECT_AUDIT/          # Initial phase audit
│   ├── 01_BASELINE_REPRODUCTION/  # Baseline Model_O artifacts
│   ├── 02_LLM_REPRESENTATION/     # Extraction prompt and schema
│   ├── 03_REPRESENTATION_AUDIT/   # Training-only audit
│   ├── 04_EXPERIMENTS/            # Pre-registered candidate experiments
│   ├── 05_STATISTICS/             # Paired bootstrap & permutation tests
│   ├── 06_COLD_START/             # Unseen brand evaluation
│   ├── 07_FAILURE_ANALYSIS/       # Error cases & residuals
│   ├── 08_FINAL_MODEL/            # Promoted model & single source of truth
│   ├── 09_MANUSCRIPT/             # Compiled IEEE manuscript (DOCX, PDF, MD)
│   ├── 10_REPRODUCIBILITY/        # Environment, seeds, execution scripts
│   └── 11_FINAL_AUDIT/            # Quality gate checklists
├── FINAL_AUDIT/                   # COMPREHENSIVE FINAL AUDIT PASS (One-Shot Reconciliation)
│   ├── 00_INVENTORY/              # Project inventory and integrity hashes
│   ├── 01_HISTORICAL_RECONCILIATION/# Reconciliation with canonical facts
│   ├── 02_BASELINE_FAIRNESS/      # Historical vs controlled baseline audit
│   ├── 03_FINAL_NUMERICAL_SOURCE/ # Recomputed final single source of truth
│   ├── 04_PDF/                    # Visual inspection of rendered manuscript
│   └── 05_VISUAL_SOURCE_OF_TRUTH/ # System architecture & Nano Banana specifications
└── FINAL_RESEARCH_PACKAGE/        # Submission distribution package
```
