"""Compile the redesign docx papers to PDF using Microsoft Word COM, then audit them.
"""
from pathlib import Path
import win32com.client
import pypdf
import time
import pythoncom

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
REDESIGN_DIR = ROOT / "redesign"

RP_DOCX = REDESIGN_DIR / "Research_Paper_IEEE_Final.docx"
RP_PDF = REDESIGN_DIR / "Research_Paper_IEEE_Final.pdf"

SP_DOCX = REDESIGN_DIR / "Survey_Paper_IEEE_Final.docx"
SP_PDF = REDESIGN_DIR / "Survey_Paper_IEEE_Final.pdf"

def compile_to_pdf(docx_path: Path, pdf_path: Path):
    print(f"Compiling {docx_path.name} -> {pdf_path.name}...")
    pythoncom.CoInitialize()
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(str(docx_path.resolve()))
        # FileFormat=17 is wdFormatPDF
        doc.SaveAs(str(pdf_path.resolve()), FileFormat=17)
        doc.Close(False)
        print(f"  Successfully exported {pdf_path.name} ({pdf_path.stat().st_size} bytes)")
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

def audit_pdfs():
    print("\n" + "=" * 50)
    print("AUDITING REDESIGNED COMPILED PDFS")
    print("=" * 50)
    
    # 1. Research Paper PDF
    reader_rp = pypdf.PdfReader(str(RP_PDF))
    text_rp = " ".join(page.extract_text() for page in reader_rp.pages)
    print(f"\nResearch Paper ({len(reader_rp.pages)} pages):")
    print("  Contains 'Gradient Boosting achieves the leading predictive accuracy (R² = 0.558':", 
          "0.558" in text_rp and "Gradient Boosting" in text_rp)
    print("  Contains 'corpus of 43,599 customer reviews':", "43,599" in text_rp)
    print("  Contains '32,477':", "32,477" in text_rp)
    print("  Contains '29,410':", "29,410" in text_rp)
    print("  Contains old 'thresholding predictions at the median of the true validation values':",
          "median of the true validation values" in text_rp)
    print("  Contains 'thresh = median(y_train)':", "median(y_train)" in text_rp)
    print("  Contains '0.476':", "0.476" in text_rp)
    print("  Contains old '0.475':", "0.475" in text_rp)
    print("  Contains [50] (Bibliography complete):", "[50]" in text_rp)
    
    # 2. Survey Paper PDF
    reader_sp = pypdf.PdfReader(str(SP_PDF))
    text_sp = " ".join(page.extract_text() for page in reader_sp.pages)
    print(f"\nSurvey Paper ({len(reader_sp.pages)} pages):")
    print("  Contains '0.595':", "0.595" in text_sp)
    print("  Contains old '0.562':", "0.562" in text_sp)
    print("  Contains '32,477':", "32,477" in text_sp)
    print("  Contains '29,410':", "29,410" in text_sp)
    print("  Contains [28] (Bibliography complete):", "[28]" in text_sp)

if __name__ == "__main__":
    compile_to_pdf(RP_DOCX, RP_PDF)
    compile_to_pdf(SP_DOCX, SP_PDF)
    audit_pdfs()
