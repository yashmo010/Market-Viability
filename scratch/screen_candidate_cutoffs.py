import json
import csv
import datetime
from pathlib import Path
from collections import Counter

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
CAPSTONE = ROOT / "Capstone updated/Capstone"
DATA_FINAL = CAPSTONE / "data/final"
EXTRACTED = CAPSTONE / "data/extracted"

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

rev_counts = Counter(r["product_uid"] for r in revs_raw)

# Let's check candidate cutoffs
candidate_dates = [
    ("2021-10-31 23:59:59 UTC (Current Frozen)", 1635724799),
    ("2021-12-31 23:59:59 UTC (End-2021)", int(datetime.datetime(2021, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp())),
    ("2022-06-30 23:59:59 UTC (Mid-2022)", int(datetime.datetime(2022, 6, 30, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp())),
    ("2022-12-31 23:59:59 UTC (End-2022)", int(datetime.datetime(2022, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp())),
    ("2023-06-30 23:59:59 UTC (Mid-2023)", int(datetime.datetime(2023, 6, 30, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp())),
    ("2023-12-31 23:59:59 UTC (End-2023)", int(datetime.datetime(2023, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp())),
    ("2024-12-31 23:59:59 UTC (End-2024)", int(datetime.datetime(2024, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp())),
    ("2025-12-31 23:59:59 UTC (End-2025)", int(datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp())),
]

print("CANDIDATE CUTOFF SCREENING (PERFORMANCE-BLIND):")
for name, ts in candidate_dates:
    train_p = [p for p in clean_prods if p.get("first_review_ts", 0) <= ts]
    test_p = [p for p in clean_prods if p.get("first_review_ts", 0) > ts]
    
    # Category distribution in test
    test_cats = Counter(p["category"] for p in test_p)
    cat_str = "; ".join(f"{c}: {cnt}" for c, cnt in sorted(test_cats.items()))
    
    # Defensible labels: products with >= 5 reviews and duration >= 1 month
    months_between = lambda a, b: abs(b - a) / (86400 * 30.44)
    defensible_test = [
        p for p in test_p 
        if rev_counts.get(p["product_uid"], 0) >= 5 
        and months_between(p.get("first_review_ts", 0), p.get("latest_review_ts", 0)) >= 1.0
    ]
    
    # Specs available
    has_specs = sum(1 for p in test_p if bool(p.get("specs", {}).get("features")))
    
    # Unseen brands: brands not in train_p
    train_brands = {p.get("brand", "").strip().casefold() for p in train_p if p.get("brand")}
    unseen_test = [p for p in test_p if p.get("brand", "").strip().casefold() not in train_brands]
    
    # Date coverage of test products
    if test_p:
        min_test_dt = datetime.datetime.fromtimestamp(min(p["first_review_ts"] for p in test_p), tz=datetime.timezone.utc).strftime("%Y-%m-%d")
        max_test_dt = datetime.datetime.fromtimestamp(max(p["first_review_ts"] for p in test_p), tz=datetime.timezone.utc).strftime("%Y-%m-%d")
        date_cov = f"{min_test_dt} to {max_test_dt}"
    else:
        date_cov = "None"
        
    print(f"\n--- {name} ---")
    print(f"Train N: {len(train_p)} ({len(train_p)/len(clean_prods)*100:.1f}%)")
    print(f"Test N: {len(test_p)} ({len(test_p)/len(clean_prods)*100:.1f}%)")
    print(f"Test Categories: {cat_str if cat_str else 'NONE'}")
    print(f"Test Date Coverage: {date_cov}")
    print(f"Defensible Labels: {len(defensible_test)} / {len(test_p)}")
    print(f"Specs Available: {has_specs} / {len(test_p)}")
    print(f"Unseen Brands Available: {len(unseen_test)} / {len(test_p)}")
