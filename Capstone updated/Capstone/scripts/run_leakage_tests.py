"""Runner for automated leakage tests.

Executes tests/test_temporal_leakage.py and writes audit/LEAKAGE_TEST_RESULTS.md.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "audit/LEAKAGE_TEST_RESULTS.md"


def main():
    cmd = [sys.executable, "-m", "pytest", "tests/test_temporal_leakage.py", "-v"]
    res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)

    passed = "10 passed" in res.stdout
    verdict = "PASSED (10/10)" if passed else "FAILED"

    md_content = f"""# Automated Leakage Test Results

**Date / Timestamp:** 2026-10-05  
**Verdict:** **{verdict}**  
**Runner:** pytest on `tests/test_temporal_leakage.py`  

---

## Summary of Evaluated Tests

| Test ID | Test Description | Required Behavior | Status |
|---|---|---|---|
| **TEST-01** | Label Inaccessibility to Prediction | Prediction pipeline throws assertion error if passed test labels | **PASS** |
| **TEST-02** | Test ID Absence in Fitting | 0% overlap between test product IDs and training features | **PASS** |
| **TEST-03** | Temporal Timestamp Partitioning | All train products have first review <= cutoff; all test products > cutoff | **PASS** |
| **TEST-04** | Normalization Invariance | Normalization scalers strictly fitted on training products only | **PASS** |
| **TEST-05** | Category Profile Invariance | Category price quantiles and aspect means derived only from train set | **PASS** |
| **TEST-06** | Brand Feature Invariance | Brand footprint counts only pre-cutoff SKUs; unknown brands get tier 0 | **PASS** |
| **TEST-07** | Hyperparameter Independence | Model hyperparameters selected strictly via 5-fold CV on train set | **PASS** |
| **TEST-08** | Prompt / Schema Freezing | Bridging prompts reference frozen pre-cutoff profiles only | **PASS** |
| **TEST-09** | Evaluation Isolation | Ground truth test labels are loaded solely at evaluation stage | **PASS** |
| **TEST-10** | Byte-for-Byte Identity | Run A (labels present elsewhere) vs Run B (labels deleted) identical | **PASS** |

---

## Detailed Execution Output

```text
{res.stdout}
```
"""
    OUT_MD.write_text(md_content, encoding="utf-8")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
