import json
import numpy as np
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\LENOVO\OneDrive\Desktop\Capstone updated (3)")
df_test = pd.read_csv(ROOT_DIR / "Legitimate" / "08_FINAL_MODEL" / "test_predictions.csv")

y = df_test["actual"].to_numpy()
p = df_test["predicted_new"].to_numpy()

q20, q80 = np.percentile(y, [20, 80])
top_mask = y >= q80
bot_mask = y <= q20

extreme_mask = top_mask | bot_mask
y_ext = (y[extreme_mask] >= q80).astype(int) # 1=top, 0=bottom
p_ext = p[extreme_mask]

# Decision threshold: midpoint of extreme predictions or median
thresh = np.median(p_ext)
p_pred = (p_ext >= thresh).astype(int)

tp = int(np.sum((y_ext == 1) & (p_pred == 1)))
fp = int(np.sum((y_ext == 0) & (p_pred == 1)))
fn = int(np.sum((y_ext == 1) & (p_pred == 0)))
tn = int(np.sum((y_ext == 0) & (p_pred == 0)))

print(f"Temporal Holdout (n={len(y_ext)} extreme items): TP={tp}, FP={fp}, FN={fn}, TN={tn}")
print(f"Accuracy: {(tp+tn)/len(y_ext):.4f}, Precision: {tp/(tp+fp):.4f}, Recall: {tp/(tp+fn):.4f}")
