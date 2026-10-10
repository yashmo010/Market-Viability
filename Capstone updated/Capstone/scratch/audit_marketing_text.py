import json
import re

with open('strict_temporal/data/test_inputs/products_test_specs.json', encoding='utf-8') as f:
    items = json.load(f)

promo_words = [
    'state-of-art', 'incredible', 'ultimate', 'crystal-clear', 'powerful', 
    'perfect', 'superior', 'unbeatable', 'premium', 'exclusive', 'best', 
    'flawless', 'exceptional', 'amazing', 'revolutionary', 'high-quality',
    'cutting-edge', 'innovative', 'extraordinary', 'breathtaking'
]

tech_patterns = [
    r'\d+\s*(?:mah|wh|w|v|a|ma)\b', 
    r'\d+\s*(?:mm|cm|inch)\b', 
    r'\d+\s*(?:hr|hour|hours)\b', 
    r'\bip[x\d]{1,2}\b', 
    r'\bbluetooth\s*\d', 
    r'\busb[- ]?c\b',
    r'\d+\s*(?:ft|feet|m|meter)\b',
    r'\d+\s*lb\b',
]

total_bullets = 0
promo_bullets = 0
tech_bullets = 0
pure_tech_bullets = 0

for it in items:
    specs = it.get('specs') or {}
    bullets = specs.get('features') or []
    for b in bullets:
        total_bullets += 1
        b_lower = b.lower()
        has_promo = any(w in b_lower for w in promo_words)
        has_tech = any(re.search(pat, b_lower) for pat in tech_patterns)
        if has_promo:
            promo_bullets += 1
        if has_tech:
            tech_bullets += 1
        if has_tech and not has_promo:
            pure_tech_bullets += 1

print(f"Total specification bullets: {total_bullets}")
print(f"Bullets containing marketing buzzwords: {promo_bullets} ({promo_bullets/total_bullets*100:.1f}%)")
print(f"Bullets containing technical specs: {tech_bullets} ({tech_bullets/total_bullets*100:.1f}%)")
print(f"Pure factual technical bullets: {pure_tech_bullets} ({pure_tech_bullets/total_bullets*100:.1f}%)")
