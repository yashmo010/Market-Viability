"""Gather project inventory statistics for the audit."""
import json, os, sys
import pandas as pd
import numpy as np
from datetime import datetime

os.chdir(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)\Capstone updated\Capstone")

# Load products
with open('data/final/products_physical.json', 'r', encoding='utf-8') as f:
    prods = json.load(f)
print(f"Products physical: {len(prods)}")
cats = {}
for p in prods:
    cats.setdefault(p['category'], []).append(p)
for c, ps in sorted(cats.items()):
    print(f"  {c}: {len(ps)} products")

# Load reviews
with open('data/final/reviews_physical.json', 'r', encoding='utf-8') as f:
    revs = json.load(f)
print(f"Reviews physical: {len(revs)}")

# Load labels
with open('data/extracted/labels.json', 'r', encoding='utf-8') as f:
    labels = json.load(f)
print(f"Labels total: {len(labels)}")
suspects = sum(1 for v in labels.values() if v['suspect_reviews'])
print(f"Suspect products: {suspects}")
non_suspect = len(labels) - suspects
print(f"Non-suspect (training): {non_suspect}")

# Suspect details
for uid, v in labels.items():
    if v['suspect_reviews']:
        print(f"  SUSPECT: {uid} cat={v['category']} reasons={v.get('suspect_reasons',[])}")

# Load features
df = pd.read_parquet('data/extracted/features_physical.parquet')
print(f"\nFeature matrix rows: {len(df)}")
print(f"Feature columns: {list(df.columns)}")
print(f"Categories in features: {df['category'].value_counts().to_dict()}")

# Holdout UIDs
ho_uids = json.loads(open('models/benchmarks/holdout_uids.json', encoding='utf-8').read())
print(f"\nHoldout UIDs file count: {len(ho_uids)}")

# Holdout validation
ho_val = json.loads(open('models/benchmarks/holdout_validation.json', encoding='utf-8').read())
print(f"Holdout validation n: {ho_val['n']}")
print(f"Holdout rho: {ho_val['spearman_rho']}")
print(f"Holdout AUC: {ho_val['auc']}")

# Temporal holdout
temp = json.loads(open('models/benchmarks/temporal_holdout.json', encoding='utf-8').read())
print(f"\nTemporal holdout n: {temp['n']}")
print(f"Temporal rho: {temp['rho']}")
print(f"Temporal AUC: {temp['auc']}")
print(f"Temporal by_cat_n: {temp['by_cat_n']}")

# Temporal split analysis
cutoff = datetime(2021, 10, 31).timestamp()
train_count = 0
test_count = 0
no_ts = 0
for p in prods:
    frt = p.get('first_review_ts', 0)
    if frt == 0:
        no_ts += 1
    elif frt <= cutoff:
        train_count += 1
    else:
        test_count += 1
print(f"\nTemporal split (cutoff 2021-10-31):")
print(f"  Train: {train_count}")
print(f"  Test: {test_count}")
print(f"  No timestamp: {no_ts}")
print(f"  Total: {train_count + test_count + no_ts}")

# Check labels vs products
prod_uids = set(p['product_uid'] for p in prods)
label_uids = set(labels.keys())
in_labels_not_prods = label_uids - prod_uids
in_prods_not_labels = prod_uids - label_uids
print(f"\nIn labels but not products: {len(in_labels_not_prods)}")
print(f"In products but not labels: {len(in_prods_not_labels)}")

# Check features vs labels
feat_uids = set(df['product_uid'].tolist())
print(f"In features: {len(feat_uids)}")
print(f"In features not labels: {len(feat_uids - label_uids)}")
print(f"In labels (non-suspect) not features: {len({u for u,v in labels.items() if not v['suspect_reviews']} - feat_uids)}")

# Training report
tr = json.loads(open('models/training_report.json', encoding='utf-8').read())
print(f"\nTraining report n_products: {tr['physical']['n_products']}")
print(f"Aspects-only CV R2: {tr['physical']['aspects_only']['mean_r2']:.4f}")
print(f"Full CV R2: {tr['physical']['full']['mean_r2']:.4f}")
print(f"N excluded suspect: {tr['n_excluded_suspect']}")

# Algorithm comparison
algo = json.loads(open('models/benchmarks/algorithm_comparison.json', encoding='utf-8').read())
print(f"\nAlgorithm comparison models: {list(algo.keys())}")
for name, m in algo.items():
    print(f"  {name}: R2={m['r2']:.4f} RMSE={m['rmse']:.2f} AUC={m['auc_roc']:.4f}")

# Headline CIs
hcis = json.loads(open('models/benchmarks/headline_cis.json', encoding='utf-8').read())
print(f"\nHeadline CIs holdout: n={hcis['holdout']['n']}, rho={hcis['holdout']['spearman_rho']}, CI={hcis['holdout']['rho_ci95']}, AUC={hcis['holdout']['auc']}, AUC_CI={hcis['holdout']['auc_ci95']}")

# Check bridged data files
import os
bridged_files = ['holdout_bridged.jsonl', 'retro_bridged.jsonl', 'retro_bridged_v2.jsonl']
for bf in bridged_files:
    path = f'models/benchmarks/{bf}'
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            lines = [l for l in f if l.strip()]
        print(f"\n{bf}: {len(lines)} records")
    else:
        print(f"\n{bf}: NOT FOUND")

# Aspect scores count
count = 0
with open('data/extracted/aspect_scores.jsonl', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            count += 1
print(f"\nAspect scores total records: {count}")

# Failed reviews
count = 0
with open('data/extracted/failed_reviews.jsonl', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            count += 1
print(f"Failed reviews: {count}")

print("\n=== INVENTORY COMPLETE ===")
