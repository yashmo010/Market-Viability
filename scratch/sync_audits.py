"""Synchronize and create the complete audit package in FINAL_AUDIT/ and FINAL_CURRENT_PROJECT_AUDIT/.
"""

import shutil
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
AUDIT_DIR = ROOT_DIR / "FINAL_AUDIT"
FREEZE_DIR = ROOT_DIR / "FINAL_FREEZE"
CURRENT_AUDIT_DIR = ROOT_DIR / "FINAL_CURRENT_PROJECT_AUDIT"

def sync_audits():
    # 1. APPLICATION_AUDIT.md
    shutil.copy2(FREEZE_DIR / "FINAL_APPLICATION_AUDIT.md", AUDIT_DIR / "APPLICATION_AUDIT.md")
    print("Synchronized APPLICATION_AUDIT.md")

    # 2. PDF_AUDIT.md
    shutil.copy2(FREEZE_DIR / "FINAL_PDF_AUDIT.md", AUDIT_DIR / "PDF_AUDIT.md")
    print("Synchronized PDF_AUDIT.md")

    # 3. CITATION_AUDIT.md
    shutil.copy2(FREEZE_DIR / "FINAL_REFERENCE_AUDIT.md", AUDIT_DIR / "CITATION_AUDIT.md")
    print("Synchronized CITATION_AUDIT.md")

    # 4. REVIEWER_AUDIT.md
    shutil.copy2(FREEZE_DIR / "FINAL_REVIEWER_AUDIT.md", AUDIT_DIR / "REVIEWER_AUDIT.md")
    print("Synchronized REVIEWER_AUDIT.md")

    # 5. FINAL_CROSS_ARTIFACT_MATRIX.csv
    shutil.copy2(FREEZE_DIR / "FINAL_CROSS_ARTIFACT_MATRIX.csv", AUDIT_DIR / "FINAL_CROSS_ARTIFACT_MATRIX.csv")
    shutil.copy2(FREEZE_DIR / "FINAL_CROSS_ARTIFACT_MATRIX.csv", CURRENT_AUDIT_DIR / "FINAL_CROSS_ARTIFACT_MATRIX.csv")
    print("Synchronized FINAL_CROSS_ARTIFACT_MATRIX.csv")

if __name__ == "__main__":
    sync_audits()
