import json
import csv
import datetime
from pathlib import Path
import numpy as np

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
CAPSTONE = ROOT / "Capstone updated/Capstone"
DATA_FINAL = CAPSTONE / "data/final"
EXTRACTED = CAPSTONE / "data/extracted"
STRICT_DIR = CAPSTONE / "strict_temporal/data"

def examine():
    # 1. Load products
    with open(DATA_FINAL / "products_physical.json", encoding="utf-8") as f:
        prods_raw = json.load(f)
    with open(DATA_FINAL / "reviews_physical.json", encoding="utf-8") as f:
        revs_raw = json.load(f)

    labels_raw = {}
    labels_path = EXTRACTED / "labels.json"
    if labels_path.exists():
        labels_raw = json.load(open(labels_path, encoding="utf-8"))
    
    suspect_uids = {uid for uid, info in labels_raw.items() if info.get("suspect_reviews")}
    clean_prods = [p for p in prods_raw if p["product_uid"] not in suspect_uids]
    
    print(f"Total raw products: {len(prods_raw)}")
    print(f"Suspect excluded: {len(suspect_uids)}")
    print(f"Clean physical products: {len(clean_prods)}")

    # Check timestamps
    CUTOFF_TS = 1635724799 # 2021-10-31 23:59:59 UTC
    CUTOFF_DT = datetime.datetime(2021, 10, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
    
    train_prods = [p for p in clean_prods if p.get("first_review_ts", 0) <= CUTOFF_TS]
    test_prods = [p for p in clean_prods if p.get("first_review_ts", 0) > CUTOFF_TS]
    
    print(f"Pre-cutoff (<= 2021-10-31): {len(train_prods)}")
    print(f"Post-cutoff (> 2021-10-31): {len(test_prods)}")
    
    # Train date ranges
    train_first_ts = [p["first_review_ts"] for p in train_prods if p.get("first_review_ts")]
    train_min_dt = datetime.datetime.fromtimestamp(min(train_first_ts), tz=datetime.timezone.utc)
    train_max_dt = datetime.datetime.fromtimestamp(max(train_first_ts), tz=datetime.timezone.utc)
    
    test_first_ts = [p["first_review_ts"] for p in test_prods if p.get("first_review_ts")]
    test_min_dt = datetime.datetime.fromtimestamp(min(test_first_ts), tz=datetime.timezone.utc)
    test_max_dt = datetime.datetime.fromtimestamp(max(test_first_ts), tz=datetime.timezone.utc)
    
    print(f"Train first review date range: {train_min_dt} to {train_max_dt}")
    print(f"Test first review date range: {test_min_dt} to {test_max_dt}")
    
    # All products first review distribution by year
    years = {}
    for p in clean_prods:
        ts = p.get("first_review_ts")
        if ts:
            dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
            years[dt.year] = years.get(dt.year, 0) + 1
        else:
            years["unknown"] = years.get("unknown", 0) + 1
            
    print("\nClean products first review year distribution:")
    for yr in sorted(years.keys()):
        print(f"  {yr}: {years[yr]} products")
        
    # Check reviews date distribution
    rev_years = {}
    for r in revs_raw:
        ts = r.get("timestamp") or r.get("review_ts")
        if ts:
            dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
            rev_years[dt.year] = rev_years.get(dt.year, 0) + 1
    print("\nReviews timestamp year distribution:")
    for yr in sorted(rev_years.keys()):
        print(f"  {yr}: {rev_years[yr]} reviews")
        
    # Overall min and max review dates
    all_rev_ts = [r.get("timestamp") or r.get("review_ts") for r in revs_raw if r.get("timestamp") or r.get("review_ts")]
    min_rev_dt = datetime.datetime.fromtimestamp(min(all_rev_ts), tz=datetime.timezone.utc)
    max_rev_dt = datetime.datetime.fromtimestamp(max(all_rev_ts), tz=datetime.timezone.utc)
    print(f"\nAll reviews date range: {min_rev_dt} to {max_rev_dt}")
    
    # Also check latest_review_ts for test products
    test_latest_ts = [p.get("latest_review_ts") for p in test_prods if p.get("latest_review_ts")]
    if test_latest_ts:
        test_max_latest_dt = datetime.datetime.fromtimestamp(max(test_latest_ts), tz=datetime.timezone.utc)
        print(f"Test products latest review max date: {test_max_latest_dt}")

examine()
