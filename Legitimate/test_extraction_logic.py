"""Test and validate extraction logic on pre-cutoff products.
"""

import json
import re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT_PROJECT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Capstone updated\Capstone")
TRAIN_PRODUCTS = ROOT_PROJECT / "strict_temporal/data/train/products.json"

def parse_technical_specs(title: str, features: list[str]) -> dict:
    full_text = title + " " + " ".join(features)
    text_lower = full_text.lower()

    # 1. Battery Hours
    bat_hrs = np.nan
    m = re.search(r"(\d{1,3}(?:\.\d)?)\s*(?:hours?|hrs?)\s*(?:of\s*)?(?:playtime|battery|playback|continuous|play|runtime|music)", text_lower)
    if not m:
        m = re.search(r"(?:up\s*to\s*)(\d{1,3}(?:\.\d)?)\s*(?:hours?|hrs?)", text_lower)
    if m:
        try:
            val = float(m.group(1))
            if 1 <= val <= 200:
                bat_hrs = val
        except ValueError:
            pass

    # 2. Battery mAh
    bat_mah = np.nan
    m = re.search(r"(\d{3,5})\s*mah", text_lower)
    if m:
        try:
            val = float(m.group(1))
            if 100 <= val <= 50000:
                bat_mah = val
        except ValueError:
            pass

    # 3. Waterproof / Ingress Protection Level
    ip_level = 0
    m = re.search(r"ip([x0-9])([0-9])", text_lower)
    if m:
        try:
            water_digit = int(m.group(2))
            ip_level = water_digit
        except ValueError:
            ip_level = 5
    elif "waterproof" in text_lower or "water-resistant" in text_lower or "rainproof" in text_lower or "splashproof" in text_lower:
        ip_level = 4

    # 4. Bluetooth Version
    bt_ver = np.nan
    m = re.search(r"bluetooth\s*(?:v(?:ersion)?)?\s*([45]\.\d)", text_lower)
    if not m:
        m = re.search(r"\bbt\s*([45]\.\d)", text_lower)
    if m:
        try:
            bt_ver = float(m.group(1))
        except ValueError:
            pass

    # 5. Wattage
    watts = np.nan
    m = re.search(r"(\d{1,3})\s*(?:watts?|w)\b", text_lower)
    if m:
        try:
            val = float(m.group(1))
            if 1 <= val <= 500:
                watts = val
        except ValueError:
            pass

    # 6. Ice Maker Specs
    ice_lbs = np.nan
    m = re.search(r"(\d{1,3}(?:\.\d)?)\s*(?:lbs?|pounds?)\s*(?:of\s*ice)?\s*(?:per\s*day|/day|in\s*24\s*hours?|daily)", text_lower)
    if m:
        try:
            val = float(m.group(1))
            if 5 <= val <= 100:
                ice_lbs = val
        except ValueError:
            pass

    ice_mins = np.nan
    m = re.search(r"(\d{1,2})\s*(?:mins?|minutes?)\b", text_lower)
    if m:
        try:
            val = float(m.group(1))
            if 3 <= val <= 30:
                ice_mins = val
        except ValueError:
            pass

    # 7. Boolean Feature Indicators
    has_anc = 1 if ("active noise cancel" in text_lower or "anc" in text_lower or "noise cancelling" in text_lower) else 0
    has_mic = 1 if ("microphone" in text_lower or "built-in mic" in text_lower or "hands-free" in text_lower) else 0
    has_warranty = 1 if ("warranty" in text_lower or "guarantee" in text_lower) else 0
    has_display = 1 if ("display" in text_lower or "screen" in text_lower or "amoled" in text_lower or "lcd" in text_lower) else 0
    has_fast_charge = 1 if ("fast charg" in text_lower or "quick charg" in text_lower or "pd " in text_lower or "power delivery" in text_lower) else 0

    # 8. Text Information Density
    words = full_text.split()
    word_count = len(words)
    num_matches = len(re.findall(r"\b\d+(?:\.\d+)?\b", full_text))
    num_density = num_matches / max(word_count, 1)

    return {
        "attr_battery_hrs": bat_hrs,
        "attr_battery_mah": bat_mah,
        "attr_ip_level": ip_level,
        "attr_bluetooth_ver": bt_ver,
        "attr_watts": watts,
        "attr_ice_lbs": ice_lbs,
        "attr_ice_mins": ice_mins,
        "attr_has_anc": has_anc,
        "attr_has_mic": has_mic,
        "attr_has_warranty": has_warranty,
        "attr_has_display": has_display,
        "attr_has_fast_charge": has_fast_charge,
        "attr_spec_bullets": len(features),
        "attr_word_count": word_count,
        "attr_number_density": round(num_density, 4),
    }

def main():
    with open(TRAIN_PRODUCTS, encoding="utf-8") as f:
        products = json.load(f)

    rows = []
    for p in products:
        specs = p.get("specs", {}).get("features", [])
        parsed = parse_technical_specs(p.get("name", ""), specs)
        parsed["product_uid"] = p["product_uid"]
        parsed["category"] = p["category"]
        parsed["price"] = float(p.get("price", 0.0))
        rows.append(parsed)

    df = pd.DataFrame(rows)
    print(f"Extracted technical specs for {len(df)} training products.")
    print("Non-null rates:")
    for col in df.columns:
        if col.startswith("attr_"):
            rate = df[col].notna().mean()
            print(f"  {col}: {rate:.1%}")

if __name__ == "__main__":
    main()
