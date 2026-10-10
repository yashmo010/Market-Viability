import docx
import re
import sys
import zipfile
import shutil
from pathlib import Path

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")

def purge_all_orphans(docx_path: Path):
    doc = docx.Document(str(docx_path))
    body_xml = doc._part._element.xml
    referenced_rids = set(re.findall(r'rId\d+', body_xml))
    
    orphans = set()
    for rid, rel in doc.part.rels.items():
        if "image" in rel.target_ref and rid not in referenced_rids:
            orphans.add((rid, Path(rel.target_ref).name))
            
    print(f"{docx_path.name}: found {len(orphans)} orphaned images: {orphans}")
    sys.stdout.flush()
    if not orphans:
        return
        
    orphan_rids = {o[0] for o in orphans}
    orphan_files = {f"word/media/{o[1]}" for o in orphans}
    
    temp_zip = docx_path.with_suffix(".clean.zip")
    with zipfile.ZipFile(docx_path, "r") as zin:
        with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename in orphan_files:
                    print(f"  Purged file: {item.filename} ({item.file_size} bytes)")
                    sys.stdout.flush()
                    continue
                data = zin.read(item.filename)
                if item.filename == "word/_rels/document.xml.rels":
                    text = data.decode("utf-8")
                    for rid in orphan_rids:
                        pattern = rf'<Relationship[^>]*Id="{rid}"[^>]*/>'
                        text = re.sub(pattern, "", text)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    shutil.move(temp_zip, docx_path)
    print(f"Rebuilt {docx_path.name} cleanly.")
    sys.stdout.flush()

if __name__ == "__main__":
    purge_all_orphans(ROOT / "Research_Paper_IEEE_CORRECTED_v3.docx")
    purge_all_orphans(ROOT / "Survey_Paper_IEEE_CORRECTED_v3.docx")
