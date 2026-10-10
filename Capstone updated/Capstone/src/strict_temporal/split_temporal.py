"""Temporal Data Splitter and Physical Barrier Generator.

Establishes strict launch-blind partitioning:
- Cutoff: 2021-10-31 23:59:59 UTC (ts = 1635724799)
- Pre-cutoff products (train pool): launch proxy <= cutoff
- Post-cutoff products (final temporal test): launch proxy > cutoff
- Physical separation:
    strict_temporal/data/train/
    strict_temporal/data/test_inputs/  (strictly specs only, NO labels)
    strict_temporal/data/test_labels/  (ground truth, isolated for evaluation)
"""

from __future__ import annotations

import csv
import datetime
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CUTOFF_ISO = "2021-10-31T23:59:59Z"
CUTOFF_DT = datetime.datetime(2021, 10, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
CUTOFF_TS = int(CUTOFF_DT.timestamp())

DATA_FINAL = ROOT / "data/final"
EXTRACTED = ROOT / "data/extracted"
OUT_BASE = ROOT / "strict_temporal/data"
AUDIT_DIR = ROOT / "audit"


def split_and_isolate() -> dict[str, Any]:
    print("=" * 70)
    print("STEP 2: FORMAL TEMPORAL PARTITIONING & INFORMATION BARRIER")
    print(f"Cutoff Date: {CUTOFF_ISO} (Epoch: {CUTOFF_TS})")
    print("=" * 70)

    # 1. Load raw final products & reviews
    with open(DATA_FINAL / "products_physical.json", encoding="utf-8") as f:
        products_raw: list[dict] = json.load(f)
    with open(DATA_FINAL / "reviews_physical.json", encoding="utf-8") as f:
        reviews_raw: list[dict] = json.load(f)

    # Load suspect products from label engineering if available, or compute
    labels_path = EXTRACTED / "labels.json"
    suspect_uids = set()
    if labels_path.exists():
        labels_raw = json.load(open(labels_path, encoding="utf-8"))
        suspect_uids = {uid for uid, info in labels_raw.items() if info.get("suspect_reviews")}
    print(f"Total raw products: {len(products_raw)}")
    print(f"Excluded suspect products: {len(suspect_uids)}")

    clean_products = [p for p in products_raw if p["product_uid"] not in suspect_uids]
    print(f"Clean physical products: {len(clean_products)}")

    # 2. Split by cutoff
    train_products = []
    test_products = []
    for p in clean_products:
        ts = p.get("first_review_ts", 0)
        if ts <= CUTOFF_TS:
            train_products.append(p)
        else:
            test_products.append(p)

    train_uids = {p["product_uid"] for p in train_products}
    test_uids = {p["product_uid"] for p in test_products}

    print(f"Pre-cutoff training products: {len(train_products)}")
    print(f"Post-cutoff temporal test products: {len(test_products)}")

    # 3. Create physical directories
    train_dir = OUT_BASE / "train"
    test_inputs_dir = OUT_BASE / "test_inputs"
    test_labels_dir = OUT_BASE / "test_labels"
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    train_dir.mkdir(parents=True, exist_ok=True)
    test_inputs_dir.mkdir(parents=True, exist_ok=True)
    test_labels_dir.mkdir(parents=True, exist_ok=True)

    # 4. Save Train Data (all pre-cutoff product and pre-cutoff review records)
    train_reviews = [r for r in reviews_raw if r["product_uid"] in train_uids]
    with open(train_dir / "products.json", "w", encoding="utf-8") as f:
        json.dump(train_products, f, indent=2)
    with open(train_dir / "reviews.json", "w", encoding="utf-8") as f:
        json.dump(train_reviews, f, indent=2)
    print(f"Wrote {train_dir / 'products.json'} ({len(train_products)} products)")
    print(f"Wrote {train_dir / 'reviews.json'} ({len(train_reviews)} reviews)")

    # 5. Save Test Inputs: STRIP ALL LABELS AND REVIEWS
    # Only specifications knowable at launch: product_uid, category, name, brand, price, specs
    test_inputs = []
    for p in test_products:
        input_record = {
            "product_uid": p["product_uid"],
            "category": p["category"],
            "name": p.get("name") or p.get("title") or "",
            "brand": (p.get("brand") or "").strip(),
            "price": float(p.get("price", 0.0)),
            "specs": p.get("specs") or {},
            "first_review_ts": p.get("first_review_ts"),  # metadata only
        }
        # Explicitly verify NO target fields are present
        assert "success_score" not in input_record
        assert "avg_rating" not in input_record
        assert "rating_count" not in input_record
        assert "review_velocity" not in input_record
        test_inputs.append(input_record)

    with open(test_inputs_dir / "products_test_specs.json", "w", encoding="utf-8") as f:
        json.dump(test_inputs, f, indent=2)
    print(f"Wrote {test_inputs_dir / 'products_test_specs.json'} ({len(test_inputs)} products, strictly specs only)")

    # 6. Save Test Labels: ISOLATED GROUND TRUTH
    # Compute test product ground truth using pre-cutoff reference distribution scaling
    # Pre-cutoff reference min/max per category:
    months_between = lambda a, b: abs(b - a) / (86400 * 30.44)
    cat_prods = {}
    for p in train_products:
        cat_prods.setdefault(p["category"], []).append(p)

    rev_counts = {}
    for r in reviews_raw:
        rev_counts[r["product_uid"]] = rev_counts.get(r["product_uid"], 0) + 1

    import numpy as np
    cat_scalers = {}
    for cat, prods in cat_prods.items():
        vols = np.log1p([rev_counts[p["product_uid"]] for p in prods])
        rats = np.array([p["avg_rating"] for p in prods], dtype=float)
        vels = np.array([
            rev_counts[p["product_uid"]] / max(months_between(p["first_review_ts"], p["latest_review_ts"]), 1.0)
            for p in prods
        ])
        cat_scalers[cat] = {
            "vol_min": float(np.min(vols)), "vol_max": float(np.max(vols)),
            "rat_min": float(np.min(rats)), "rat_max": float(np.max(rats)),
            "vel_min": float(np.min(vels)), "vel_max": float(np.max(vels)),
        }

    test_labels = {}
    for p in test_products:
        cat = p["category"]
        sc = cat_scalers[cat]
        cnt = rev_counts.get(p["product_uid"], 0)
        vol = float(np.log1p(cnt))
        rat = float(p["avg_rating"])
        vel = float(cnt / max(months_between(p["first_review_ts"], p["latest_review_ts"]), 1.0))

        # Normalize with frozen training scalers
        scale = lambda x, mn, mx: (x - mn) / (mx - mn) if (mx - mn) > 1e-12 else 0.5
        vn = max(0.0, min(1.0, scale(vol, sc["vol_min"], sc["vol_max"])))
        rn = max(0.0, min(1.0, scale(rat, sc["rat_min"], sc["rat_max"])))
        veln = max(0.0, min(1.0, scale(vel, sc["vel_min"], sc["vel_max"])))
        score = 100.0 * (0.40 * vn + 0.35 * rn + 0.25 * veln)

        test_labels[p["product_uid"]] = {
            "product_uid": p["product_uid"],
            "category": cat,
            "success_score": round(score, 3),
            "n_reviews": cnt,
            "avg_rating": rat,
            "velocity": round(vel, 3),
            "first_review_ts": p["first_review_ts"],
            "latest_review_ts": p["latest_review_ts"],
            "volume_norm": round(vn, 4),
            "rating_norm": round(rn, 4),
            "velocity_norm": round(veln, 4)
        }

    with open(test_labels_dir / "ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(test_labels, f, indent=2)
    print(f"Wrote {test_labels_dir / 'ground_truth.json'} ({len(test_labels)} ground truth labels, ISOLATED)")

    # 7. Write DATA_SPLIT_MANIFEST.csv
    manifest_path = AUDIT_DIR / "DATA_SPLIT_MANIFEST.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "product_uid", "split", "category", "brand", "first_review_ts",
            "first_review_date_utc", "price", "has_specs"
        ])
        for p in train_products:
            ts = p.get("first_review_ts", 0)
            dt_str = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
            writer.writerow([
                p["product_uid"], "TRAIN", p["category"], (p.get("brand") or "").strip(),
                ts, dt_str, p.get("price"), bool(p.get("specs", {}).get("features"))
            ])
        for p in test_products:
            ts = p.get("first_review_ts", 0)
            dt_str = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
            writer.writerow([
                p["product_uid"], "FINAL_TEST", p["category"], (p.get("brand") or "").strip(),
                ts, dt_str, p.get("price"), bool(p.get("specs", {}).get("features"))
            ])
    print(f"Wrote {manifest_path} ({len(clean_products)} rows)")

    # Summary dictionary
    summary = {
        "cutoff_date": CUTOFF_ISO,
        "cutoff_timestamp": CUTOFF_TS,
        "train_n": len(train_products),
        "test_n": len(test_products),
        "train_uids": sorted(list(train_uids)),
        "test_uids": sorted(list(test_uids)),
        "by_category_train": {c: sum(1 for p in train_products if p["category"] == c) for c in cat_prods},
        "by_category_test": {c: sum(1 for p in test_products if p["category"] == c) for c in cat_prods},
    }
    return summary


if __name__ == "__main__":
    split_and_isolate()
