import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
from src.prediction.predictor import Predictor

df = pd.read_parquet(ROOT / "data/extracted/features_physical.parquet").set_index("product_uid")
with open(ROOT / "data/final/products_physical.json", encoding="utf-8") as f:
    products = {p["product_uid"]: p for p in json.load(f)}

sources = [
    ROOT / "models/benchmarks/retro_bridged_v2.jsonl",
    ROOT / "models/benchmarks/holdout_bridged.jsonl",
    ROOT / "models/benchmarks/ice_holdout_bridged.jsonl"
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

predictor = Predictor(use_mock_llm=False)

# Let's run prediction for each product with price
preds_with_price = []
preds_zero_price = []
preds_median_price = []
preds_no_vfm = []
actual_scores = []
price_pctls = []
prices = []

for uid, r in cache.items():
    cat = str(df.at[uid, "category"])
    bridged = dict(r["bridged"])
    user_specs = dict(products[uid].get("specs", {}))
    user_specs["brand"] = products[uid].get("brand")
    user_specs["name"] = products[uid].get("name")
    orig_price = float(products[uid].get("price", df.at[uid, "price"]))
    user_specs["price"] = orig_price
    
    # 1. Normal prediction (as deployed)
    pred_res = predictor.predict_from_bridged(bridged, cat, user_specs)
    v_norm = pred_res["viability_pct"]
    
    # 2. Zero price
    specs_zero = dict(user_specs)
    specs_zero["price"] = 0.0
    # Also if value_for_money was deterministic from price, what did it do?
    pred_zero = predictor.predict_from_bridged(bridged, cat, specs_zero)["viability_pct"]
    
    # 3. Median price
    specs_med = dict(user_specs)
    cat_med = predictor.profiles[cat]["price"]["median"]
    specs_med["price"] = cat_med
    pred_med = predictor.predict_from_bridged(bridged, cat, specs_med)["viability_pct"]
    
    actual = float(df.at[uid, "success_score"])
    
    # price percentile in category
    cat_prices = df[df.category == cat]["price"]
    pctl = float(stats.percentileofscore(cat_prices, orig_price))
    
    preds_with_price.append(v_norm)
    preds_zero_price.append(pred_zero)
    preds_median_price.append(pred_med)
    actual_scores.append(actual)
    price_pctls.append(pctl)
    prices.append(orig_price)

preds_with_price = np.array(preds_with_price)
preds_zero_price = np.array(preds_zero_price)
preds_median_price = np.array(preds_median_price)
actual_scores = np.array(actual_scores)
price_pctls = np.array(price_pctls)

print(f"Normal deployed model: Spearman rho = {stats.spearmanr(preds_with_price, actual_scores)[0]:.4f}")
print(f"Zero price: Spearman rho = {stats.spearmanr(preds_zero_price, actual_scores)[0]:.4f}")
print(f"Median price: Spearman rho = {stats.spearmanr(preds_median_price, actual_scores)[0]:.4f}")
print(f"Price percentile alone vs actual: Spearman rho = {stats.spearmanr(price_pctls, actual_scores)[0]:.4f}")

corr_norm_price = np.corrcoef(preds_with_price, price_pctls)[0, 1]
corr_zero_price = np.corrcoef(preds_zero_price, price_pctls)[0, 1]
corr_med_price = np.corrcoef(preds_median_price, price_pctls)[0, 1]

print(f"Pearson r(pred_norm, price_pctl) = {corr_norm_price:.4f}")
print(f"Pearson r(pred_zero, price_pctl) = {corr_zero_price:.4f}")
print(f"Pearson r(pred_med, price_pctl) = {corr_med_price:.4f}")

# Also check what if we predict using row_aspects directly without predictor._adj_confidence / calibration:
