import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import xgboost as xgb

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))

df = pd.read_parquet("data/extracted/features_physical.parquet").set_index("product_uid")
with open("data/final/products_physical.json", encoding="utf-8") as f:
    products = {p["product_uid"]: p for p in json.load(f)}

sources = [
    Path("models/benchmarks/retro_bridged_v2.jsonl"),
    Path("models/benchmarks/holdout_bridged.jsonl"),
    Path("models/benchmarks/ice_holdout_bridged.jsonl")
]
cache = {}
for p in sources:
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                uid = r.get("product_uid")
                if uid in df.index and r.get("bridged"):
                    cache[uid] = r

print(f"Paired products: {len(cache)}")

with open("models/brand_tier_map.json", encoding="utf-8") as f:
    bt = json.load(f)

with open("data/extracted/category_profiles.json", encoding="utf-8") as f:
    profiles = json.load(f)

# The 118 holdout products
uids = list(cache.keys())
y_true = np.array([float(df.at[u, "success_score"]) for u in uids])
cats = [str(df.at[u, "category"]) for u in uids]

bst_aspects = xgb.Booster()
bst_aspects.load_model("models/xgb_physical_aspects_only.json")
manifest_aspects = bst_aspects.feature_names

# Train set: products NOT in cache
train_uids = [u for u in df.index if u not in cache]
print(f"Train products count: {len(train_uids)}, test products count: {len(uids)}")

# Test different price values in row_aspects
for p_val_type in ["zero", "nan", "median", "drop"]:
    rows = []
    for u in uids:
        r = cache[u]
        cat = str(df.at[u, "category"])
        prof = profiles[cat]
        brand = (products[u].get("brand") or "").strip().casefold()
        btier = float(bt["brands"].get(brand, 1))
        
        row = {}
        for col in manifest_aspects:
            if col == "category":
                row[col] = cat
            elif col in r["bridged"]:
                row[col] = float(r["bridged"][col])
            elif col.endswith("_mention_rate"):
                asp = col[:-len("_mention_rate")]
                row[col] = prof["avg_mention_rates"].get(asp, np.nan)
            elif col == "brand_tier":
                row[col] = btier
            elif col == "price":
                if p_val_type == "zero":
                    row[col] = 0.0
                elif p_val_type == "nan":
                    row[col] = np.nan
                elif p_val_type == "median":
                    row[col] = float(prof["price"]["median"])
                elif p_val_type == "drop":
                    row[col] = 0.0
            else:
                row[col] = np.nan
        rows.append(row)
    
    df_test = pd.DataFrame(rows, columns=manifest_aspects)
    df_test["category"] = df_test["category"].astype("category")
    dmat = xgb.DMatrix(df_test, enable_categorical=True)
    preds = bst_aspects.predict(dmat)
    rho, pval = stats.spearmanr(preds, y_true)
    print(f"xgb_physical_aspects_only with price={p_val_type}: rho = {rho:.4f} (p={pval:.4e})")

# Now let's train a model on train_uids with NO price feature at all:
aspect_cols = [c for c in manifest_aspects if c != "price"]
X_train = df.loc[train_uids, aspect_cols].copy()
X_train["category"] = X_train["category"].astype("category")
y_train = df.loc[train_uids, "success_score"].values
X_test = pd.DataFrame(rows, columns=manifest_aspects)[aspect_cols].copy()
X_test["category"] = X_test["category"].astype("category")

dtrain = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
dtest = xgb.DMatrix(X_test, enable_categorical=True)

params = {
    "objective": "reg:squarederror",
    "n_estimators": 600,
    "learning_rate": 0.05,
    "max_depth": 5,
    "min_child_weight": 3,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "enable_categorical": True,
    "tree_method": "hist",
    "random_state": 42
}
model_no_price = xgb.train(params, dtrain, num_boost_round=300)
preds_no_price = model_no_price.predict(dtest)
rho_np, pval_np = stats.spearmanr(preds_no_price, y_true)
print(f"Retrained model with NO price feature: rho = {rho_np:.4f} (p={pval_np:.4e})")

# What if trained on all 631 products?
X_all = df[aspect_cols].copy()
X_all["category"] = X_all["category"].astype("category")
y_all = df["success_score"].values
dall = xgb.DMatrix(X_all, label=y_all, enable_categorical=True)
model_all_no_price = xgb.train(params, dall, num_boost_round=300)
preds_all_np = model_all_no_price.predict(dtest)
rho_all_np, pval_all_np = stats.spearmanr(preds_all_np, y_true)
print(f"Retrained model on all 631 with NO price feature: rho = {rho_all_np:.4f} (p={pval_all_np:.4e})")
