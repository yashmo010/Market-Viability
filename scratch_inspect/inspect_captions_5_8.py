import docx

doc = docx.Document(r'redesign\Research_Paper_IEEE_Final.docx')
for i in [70, 78, 88, 103]:
    p = doc.paragraphs[i]
    print(f"P{i}: {p.text}\n")
