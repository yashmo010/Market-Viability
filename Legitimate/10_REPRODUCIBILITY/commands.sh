#!/usr/bin/env bash
# Complete End-to-End Execution Sequence for Legitimate Research Branch
set -e

echo "1. Running Project Audit..."
python Legitimate/build_audit.py

echo "2. Running Baseline Model_O Reproduction..."
python Legitimate/run_baseline_reproduction.py

echo "3. Running Training-Only Representation Quality Audit..."
python Legitimate/run_representation_audit.py

echo "4. Evaluating Pre-Registered Candidate Models..."
python Legitimate/run_candidate_experiments.py

echo "5. Running Statistical Significance and Seed Stability..."
python Legitimate/run_statistical_tests.py

echo "6. Exporting Promoted Model and Single Source of Truth..."
python Legitimate/save_promoted_model.py

echo "7. Generating Publication Figures (300 DPI)..."
python Legitimate/generate_publication_figures.py

echo "8. Testing Application Parity (100% numerical consistency)..."
python Legitimate/test_application_parity.py

echo "9. Evaluating Real-World External Application Cohort..."
python Legitimate/build_application_evaluation.py

echo "10. Generating Publication Tables I-IX..."
python Legitimate/generate_tables.py

echo "11. Compiling IEEE Final Manuscript (DOCX, PDF, MD)..."
python Legitimate/build_final_manuscript.py

echo "12. Running Leakage & Byte-For-Byte Integrity Tests..."
python Legitimate/test_leakage_and_integrity.py

echo "Complete! All artifacts generated in Legitimate/ and FINAL_RESEARCH_PACKAGE/."
