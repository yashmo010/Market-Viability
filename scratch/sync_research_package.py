"""Synchronize all latest audit, evaluation, figure, table, and paper artifacts to FINAL_RESEARCH_PACKAGE.
"""

import shutil
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
PKG_DIR = ROOT_DIR / "FINAL_RESEARCH_PACKAGE"
AUDIT_DIR = ROOT_DIR / "FINAL_AUDIT"
CURRENT_AUDIT_DIR = ROOT_DIR / "FINAL_CURRENT_PROJECT_AUDIT"

SUPP_DIR = PKG_DIR / "supplementary"
AUDIT_PKG_DIR = PKG_DIR / "audit"
FIG_PKG_DIR = PKG_DIR / "figures"
TAB_PKG_DIR = PKG_DIR / "tables"
PAPER_PKG_DIR = PKG_DIR / "paper"

for d in [SUPP_DIR, AUDIT_PKG_DIR, FIG_PKG_DIR, TAB_PKG_DIR, PAPER_PKG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 1. Synchronize figures (Figs 1-9)
for fig in (ROOT_DIR / "Legitimate" / "figures").glob("*.png"):
    shutil.copy2(fig, FIG_PKG_DIR / fig.name)
    shutil.copy2(fig, AUDIT_DIR / "figures" / fig.name)
print("Synchronized Figs 1-9 to all destinations.")

# 2. Synchronize tables (Tables I-XI)
for tab in (ROOT_DIR / "Legitimate" / "tables").glob("*.csv"):
    shutil.copy2(tab, TAB_PKG_DIR / tab.name)
    shutil.copy2(tab, AUDIT_DIR / "tables" / tab.name)
print("Synchronized Tables I-XI to all destinations.")

# 3. Synchronize paper (docx, pdf, md)
for doc in (ROOT_DIR / "Legitimate" / "09_MANUSCRIPT").glob("*.*"):
    shutil.copy2(doc, PAPER_PKG_DIR / doc.name)
    shutil.copy2(doc, AUDIT_DIR / "paper" / doc.name)
print("Synchronized paper to all destinations.")

# 4. Synchronize supplementary
eval_dirs = [
    "CURRENT_EVALUATION_LITERATURE",
    "CURRENT_OOF_BENCHMARK",
    "CURRENT_DECISION_METRICS",
    "CURRENT_RANKING_METRICS",
    "CURRENT_CONFUSION_ANALYSIS",
    "CURRENT_EFFICIENCY",
    "CURRENT_INTERPRETABILITY",
    "CURRENT_ERROR_ANALYSIS"
]
for ed in eval_dirs:
    src_ed = AUDIT_DIR / ed
    dst_ed = SUPP_DIR / ed
    if src_ed.exists():
        shutil.copytree(src_ed, dst_ed, dirs_exist_ok=True)

# Copy supplementary files
supp_files = [
    AUDIT_DIR / "CURRENT_OOF_RESULTS.json",
    AUDIT_DIR / "SIX_LEARNER_CURRENT_BENCHMARK_REPORT.md",
    AUDIT_DIR / "CONFUSION_MATRIX_DECISION.md",
    AUDIT_DIR / "RANKING_METRIC_DECISION.md",
    AUDIT_DIR / "EFFICIENCY_DECISION.md",
    AUDIT_DIR / "INTERPRETABILITY_DECISION.md",
    AUDIT_DIR / "METRIC_DECISION_MATRIX.csv",
    AUDIT_DIR / "REVIEWER_QUESTION_MAP.md"
]
for sf in supp_files:
    if sf.exists():
        shutil.copy2(sf, SUPP_DIR / sf.name)
print("Synchronized supplementary package.")

# 5. Synchronize audit directory
for p in AUDIT_DIR.glob("*"):
    if p.is_file():
        shutil.copy2(p, AUDIT_PKG_DIR / p.name)

for p in CURRENT_AUDIT_DIR.glob("*"):
    if p.is_file():
        shutil.copy2(p, AUDIT_PKG_DIR / p.name)
print("Synchronized audit package.")
