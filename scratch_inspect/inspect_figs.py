import docx
import xml.etree.ElementTree as ET

doc = docx.Document('Research_Paper_IEEE_CORRECTED_v3.docx')
for i in range(45, 75):
    p = doc.paragraphs[i]
    rids = []
    for r in p.runs:
        if 'blip' in r._element.xml:
            tree = ET.fromstring(r._element.xml)
            for elem in tree.iter():
                if elem.tag.endswith('blip'):
                    rids.append(elem.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'))
    if rids or p.text.strip():
        img_names = [doc.part.rels[rid].target_ref for rid in rids if rid]
        print(f"P{i}: text=\"{p.text[:60]}\" images={img_names}")
