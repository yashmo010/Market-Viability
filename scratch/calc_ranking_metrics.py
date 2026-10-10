import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import ndcg_score
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
df_test = pd.read_csv(ROOT_DIR / "Legitimate" / "08_FINAL_MODEL" / "test_predictions.csv")

y = df_test["actual"].to_numpy()
p_new = df_test["predicted_new"].to_numpy()
p_orig = df_test["predicted_orig"].to_numpy()

# Kendall tau
tau_new, p_tau_new = stats.kendalltau(p_new, y)
tau_orig, p_tau_orig = stats.kendalltau(p_orig, y)

# NDCG@5 and NDCG@10 overall and per category
ndcg5_new = ndcg_score([y], [p_new], k=5)
ndcg5_orig = ndcg_score([y], [p_orig], k=5)
ndcg10_new = ndcg_score([y], [p_new], k=10)
ndcg10_orig = ndcg_score([y], [p_orig], k=10)

print(f"Kendall Tau: Promoted = {tau_new:.4f} (p={p_tau_new:.2e}) vs Baseline = {tau_orig:.4f} (p={p_tau_orig:.2e})")
print(f"NDCG@5: Promoted = {ndcg5_new:.4f} vs Baseline = {ndcg5_orig:.4f}")
print(f"NDCG@10: Promoted = {ndcg10_new:.4f} vs Baseline = {ndcg10_orig:.4f}")
