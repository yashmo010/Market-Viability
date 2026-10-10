Run from the repo root (Capstone updated/Capstone) with data/final, data/extracted/aspect_scores.jsonl, models/benchmarks/*.jsonl, and src/ present.

Order:
  step1.py (labels + fraud filter from raw reviews/products)
  -> step2.py (dataset stats, features rebuilt from aspect_scores.jsonl)
  -> step3.py (CV + Table 1 replication)
  -> step4.py (oracle ceilings, price percentile baseline, analytic p-values)
  -> step5.py (extra CV variants)
  -> step6_bridging.py (bridging-dependent recomputations: X1-X11, holdouts, temporal splits, aspect fidelity, ablation diagnostics, ice makers, Reddit A/B, 10k bootstrap CIs).

Outputs:
  res_A_B.json        - dataset statistics and label sensitivity
  res_cv.json         - cross-validation R2, RMSE, MAE for model variants
  res_table1.json     - Table 1 six-algorithm benchmark replication
  res_model.json      - price baseline, review-aspect correlations, analytic p-values, oracle benchmarks
  res_cv_extra.json   - unconstrained CV variant and per-category R2
  res_bridging.json   - bridging-dependent evaluations (holdout n=59/118, temporal n=66/125, aspect fidelity, ice makers, Reddit A/B)

No saved metric/result files from the repo (e.g. models/*.json, fresh_holdout_5cat.json) are read as ground truth; all calculations are executed directly on the raw review data, extraction rows, cached LLM evaluation JSONL outputs, and repository model code.
