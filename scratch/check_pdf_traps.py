import pypdf
import re

reader = pypdf.PdfReader('Legitimate/09_MANUSCRIPT/FINAL_MANUSCRIPT.pdf')
text = ' '.join([p.extract_text() for p in reader.pages])

traps = [
    'October 31,2021',
    'Air Fryer',
    'air fryer',
    'n = 82',
    'n=82',
    '82/90',
    '0.6720',
    '17.84',
    'causal drivers',
    '8.26%',
    'commercial triage',
    'venture capital',
    'domain collapse',
    'market winner',
    'actual market outcome',
    'sales prediction',
    'revenue prediction'
]

print("=== AUDIT TRAPS EVALUATION IN PDF ===")
all_passed = True
for t in traps:
    count = len(re.findall(re.escape(t), text, re.IGNORECASE))
    print(f'"{t}": {count} occurrences')
    if count > 0:
        all_passed = False

if all_passed:
    print("ALL TRAP CHECKS PASSED: ZERO DEFECTS FOUND!")
else:
    print("SOME TRAPS FOUND! NEED CORRECTION.")
