# Project Inventory: Existing Launch-Blind Product Success Prediction Research

**Audit Date:** 2026-10-07  
**Branch:** Legitimate/00_PROJECT_AUDIT  
**Integrity State:** Original workspace preserved byte-for-byte; read-only inspection.

## 1. Directory Structure Overview
- **`src/`**: Core library modules:
  - `src/strict_temporal/`: Frozen training pipeline (`fit_freeze.py`) and test predictor (`predict_test.py`).
  - `src/prediction/`: Deployed inference service (`predictor.py`), spec coach (`spec_coach.py`), bridging layer (`bridging_layer.py`), input gate (`input_gate.py`).
  - `src/training/`: Legacy training scripts (`run_training.py`).
  - `src/extraction/`: LLM prompt construction, provider management (`llm_provider.py`, `extraction_prompt.py`).
  - `src/app/`: FastAPI application (`api.py`) and Streamlit launcher (`app.py`), React frontend (`frontend/dist/`).
- **`strict_temporal/`**: Isolated research environment enforcing temporal cutoff:
  - `data/train/`: 507 pre-cutoff products (`products.json`) and 43,599 historical reviews (`reviews.json`).
  - `data/test_inputs/`: 124 launch-blind test products specs (`products_test_specs.json`).
  - `data/test_labels/`: Strictly isolated test labels (`ground_truth.json`).
  - `frozen_state/`: Frozen model (`xgb_physical_aspects_only.json`), feature manifest (`xgb_physical_aspects_only_features.json`), brand tiers (`brand_tier_map.json`), category profiles (`category_profiles.json`), target scalers (`target_scalers.json`), train features (`train_features.parquet`).
  - `predictions/`: Canonical predictions (`predictions.json`).
- **`tests/`**: Automated test suite (74/74 passing):
  - `test_temporal_leakage.py`: 10/10 strict temporal leakage checks.
  - `test_baseline_validity.py`: 14/14 baseline model checks.
  - `test_statistical_validity.py`: 15/15 statistical recomputation and bootstrap checks.
  - `test_generalization_validity.py`: 15/15 generalization, cold start, and category checks.
  - `test_target_validity.py`: 10/10 target definition and scaling checks.
  - `test_llm_bridge.py`: 10/10 LLM bridging schema and grounding checks.
- **`audit/`**: Comprehensive experimental and statistical audit records:
  - `statistics/`: Canonical evaluation reports, early stopping audits, bootstrap calculations.
  - `baselines/`: Benchmark results, cold-start decompositions, paired model comparisons.
  - `llm/`: Aspect definitions, prompt versioning, stochasticity checks.
- **`paper_ieee/`**: Publication source files (`main.tex`, `refs.bib`, `paper_full.md`, high-res figures).
- **`submission/` & `redesign/`**: Generated docx and pdf manuscripts (`Research_Paper_IEEE_Final.docx/pdf`, `Survey_Paper_IEEE_Final.docx/pdf`).
