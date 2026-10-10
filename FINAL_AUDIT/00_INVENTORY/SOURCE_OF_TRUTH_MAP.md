# Source of Truth Hierarchy Map

Per Section 3 of the Final Audit Master Protocol, when artifacts disagree, the following strict hierarchy applies:

1. **Immutable / Raw Source Data**  
   `Capstone updated/Capstone/strict_temporal/data/train/products.json` (507 products)  
   `Capstone updated/Capstone/strict_temporal/data/test_inputs/products_test_specs.json` (124 products)  
   `Capstone updated/Capstone/strict_temporal/data/test_labels/ground_truth.json` (124 isolated labels)

2. **Executable Research Code**  
   `Legitimate/run_candidate_experiments.py`  
   `Legitimate/run_statistical_tests.py`  
   `Legitimate/test_extraction_logic.py`

3. **Saved Prediction / Result Artifacts**  
   `FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_PREDICTIONS.csv`  
   `FINAL_AUDIT/02_BASELINE_FAIRNESS/`

4. **FINAL_RESULTS / Feature Manifests / Experiment Ledger**  
   `FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_RESULTS.json`  
   `FINAL_AUDIT/03_FINAL_NUMERICAL_SOURCE/FINAL_FEATURE_MANIFEST.json`

5. **Audit Reports**  
   `FINAL_AUDIT/FINAL_AUDIT_REPORT.md`

6. **Manuscript Source & Visuals**  
   `FINAL_MANUSCRIPT.docx`, `FINAL_MANUSCRIPT.pdf`, `FINAL_MANUSCRIPT.md`  
   Figures 1-7 and Tables I-IX

*Rule: Never force upstream evidence to agree with downstream prose. Downstream artifacts must always be regenerated from verified upstream evidence.*
