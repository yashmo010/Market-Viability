import json
import csv
import datetime
from pathlib import Path
from collections import Counter

ROOT = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
CAPSTONE = ROOT / "Capstone updated/Capstone"
DATA_FINAL = CAPSTONE / "data/final"
EXTRACTED = CAPSTONE / "data/extracted"
OUT_DIR = ROOT / "FINAL_AUDIT/CUTOFF_AUDIT"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

# 1. TEMPORAL DATE DISTRIBUTION CSV
CUTOFF_TS = 1635724799 # 2021-10-31 23:59:59 UTC
dist_rows = []
for p in clean_prods:
    uid = p["product_uid"]
    cat = p.get("category", "")
    brand = (p.get("brand") or "").strip()
    f_ts = p.get("first_review_ts", 0)
    l_ts = p.get("latest_review_ts", 0)
    f_dt = datetime.datetime.fromtimestamp(f_ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if f_ts else ""
    l_dt = datetime.datetime.fromtimestamp(l_ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if l_ts else ""
    split = "TRAIN" if f_ts <= CUTOFF_TS else "TEMPORAL_TEST"
    n_rev = rev_counts.get(uid, 0)
    months_span = round(abs(l_ts - f_ts) / (86400 * 30.44), 2) if (f_ts and l_ts) else 0.0
    has_specs = bool(p.get("specs", {}).get("features"))
    
    dist_rows.append({
        "product_uid": uid,
        "split": split,
        "category": cat,
        "brand": brand,
        "first_review_ts": f_ts,
        "first_review_utc": f_dt,
        "latest_review_ts": l_ts,
        "latest_review_utc": l_dt,
        "review_count": n_rev,
        "exposure_months": months_span,
        "has_launch_specs": has_specs,
        "price": p.get("price", 0.0)
    })

# Sort chronologically by first review
dist_rows.sort(key=lambda x: x["first_review_ts"])

with open(OUT_DIR / "temporal_date_distribution.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(dist_rows[0].keys()))
    writer.writeheader()
    writer.writerows(dist_rows)

print(f"Wrote {OUT_DIR / 'temporal_date_distribution.csv'} ({len(dist_rows)} rows)")

# 2. CANDIDATE CUTOFF FEASIBILITY CSV
candidates = [
    ("2021-10-31 23:59:59 UTC (Current Frozen Protocol)", 1635724799, "2021-10-31"),
    ("2021-12-31 23:59:59 UTC (End-2021 Boundary)", int(datetime.datetime(2021, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()), "2021-12-31"),
    ("2022-06-30 23:59:59 UTC (Mid-2022 Boundary)", int(datetime.datetime(2022, 6, 30, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()), "2022-06-30"),
    ("2022-12-31 23:59:59 UTC (End-2022 Boundary)", int(datetime.datetime(2022, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()), "2022-12-31"),
    ("2023-06-30 23:59:59 UTC (Mid-2023 Boundary)", int(datetime.datetime(2023, 6, 30, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()), "2023-06-30"),
    ("2023-12-31 23:59:59 UTC (End-2023 Boundary)", int(datetime.datetime(2023, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()), "2023-12-31"),
    ("2024-12-31 23:59:59 UTC (End-2024 Boundary)", int(datetime.datetime(2024, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()), "2024-12-31"),
    ("2025-12-31 23:59:59 UTC (End-2025 Boundary)", int(datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()), "2025-12-31"),
]

feasibility_rows = []
for name, ts, date_label in candidates:
    train_p = [p for p in clean_prods if p.get("first_review_ts", 0) <= ts]
    test_p = [p for p in clean_prods if p.get("first_review_ts", 0) > ts]
    n_train = len(train_p)
    n_test = len(test_p)
    
    test_cats = Counter(p["category"] for p in test_p)
    cat_str = "; ".join(f"{c}: {test_cats.get(c, 0)}" for c in sorted(list(set(p['category'] for p in clean_prods))))
    
    months_between = lambda a, b: abs(b - a) / (86400 * 30.44)
    defensible_test = [
        p for p in test_p 
        if rev_counts.get(p["product_uid"], 0) >= 5 
        and months_between(p.get("first_review_ts", 0), p.get("latest_review_ts", 0)) >= 1.0
    ]
    
    if test_p:
        min_test_dt = datetime.datetime.fromtimestamp(min(p["first_review_ts"] for p in test_p), tz=datetime.timezone.utc).strftime("%Y-%m-%d")
        max_test_dt = datetime.datetime.fromtimestamp(max(p["first_review_ts"] for p in test_p), tz=datetime.timezone.utc).strftime("%Y-%m-%d")
        date_cov = f"{min_test_dt} to {max_test_dt}"
        pct_retained = f"{n_test / len(clean_prods) * 100:.2f}%"
        has_specs = sum(1 for p in test_p if bool(p.get("specs", {}).get("features")))
        train_brands = {p.get("brand", "").strip().casefold() for p in train_p if p.get("brand")}
        unseen_test = [p for p in test_p if p.get("brand", "").strip().casefold() not in train_brands]
        specs_avail = "YES (100%)" if has_specs == n_test else f"PARTIAL ({has_specs}/{n_test})"
        label_maturity = "ADEQUATE (>= 7 mo exposure)" if min([months_between(p["first_review_ts"], p["latest_review_ts"]) for p in test_p]) >= 1.0 else "INADEQUATE"
        unseen_eval = f"YES (n={len(unseen_test)})" if len(unseen_test) >= 10 else f"MARGINAL/INSUFFICIENT (n={len(unseen_test)})"
        feasible = "YES (PRIMARY FROZEN)" if ts == 1635724799 else ("FEASIBLE BUT FEWER SAMPLES" if n_test >= 100 else "INFEASIBLE (STARVATION)")
    else:
        date_cov = "NONE (No Products)"
        pct_retained = "0.00%"
        specs_avail = "N/A"
        label_maturity = "N/A (0 Products)"
        unseen_eval = "NO (0 Products)"
        feasible = "INFEASIBLE (ZERO SAMPLES)"
        
    feasibility_rows.append({
        "candidate_cutoff": name,
        "n_training_products": n_train,
        "n_temporal_test_products": n_test,
        "pct_products_retained_test": pct_retained,
        "category_distribution": cat_str,
        "date_coverage": date_cov,
        "defensible_labels_count": f"{len(defensible_test)} / {n_test}",
        "launch_specs_available": specs_avail,
        "label_maturity_adequate": label_maturity,
        "unseen_brand_eval_possible": unseen_eval,
        "feasibility_verdict": feasible
    })

with open(OUT_DIR / "candidate_cutoff_feasibility.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(feasibility_rows[0].keys()))
    writer.writeheader()
    writer.writerows(feasibility_rows)

print(f"Wrote {OUT_DIR / 'candidate_cutoff_feasibility.csv'} ({len(feasibility_rows)} rows)")
