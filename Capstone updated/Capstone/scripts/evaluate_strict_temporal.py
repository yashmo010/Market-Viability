"""Canonical Evaluation Script for Strict Temporal Holdout (Issue 3 Audited).

Entry point for reproducible evaluation of the launch-blind forward-in-time
temporal test set under the frozen October 31, 2021 cutoff protocol.

Usage:
    python scripts/evaluate_strict_temporal.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
PRED_PATH = ROOT / "strict_temporal/predictions/predictions.json"
LABELS_PATH = ROOT / "strict_temporal/data/test_labels/ground_truth.json"
OUT_JSON = ROOT / "audit/statistics/STRICT_EVALUATION_REPORT.json"
OUT_CSV = ROOT / "audit/statistics/STRICT_CATEGORY_METRICS.csv"
OUT_TABLE = ROOT / "audit/statistics/PRIMARY_RESULT_TABLE.txt"


def calc_auc_strict(pred: np.ndarray, y: np.ndarray) -> tuple[float, int, int]:
    """Calculate AUC between top and bottom actual success quintiles."""
    t = pd.DataFrame({"p": pred, "y": y})
    t["tier"] = pd.qcut(t["y"], 5, labels=False, duplicates="drop")
    top = t[t.tier == t.tier.max()]["p"].values
    bot = t[t.tier == 0]["p"].values
    if len(top) == 0 or len(bot) == 0:
        return float("nan"), len(top), len(bot)
    u_val = sum((tp > bp) + 0.5 * (tp == bp) for tp in top for bp in bot)
    return float(u_val / (len(top) * len(bot))), len(top), len(bot)


def boot_ci(fn, n: int, *arrays, n_boot: int = 10000, seed: int = 42) -> tuple[float, float]:
    """10,000-replicate non-parametric percentile bootstrap confidence interval."""
    rng = np.random.RandomState(seed)
    vals = []
    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        v = fn(*[a[idx] for a in arrays])
        if np.isfinite(v):
            vals.append(v)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def delong_auc_ci(pred: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """DeLong asymptotic standard error and 95% CI for ROC AUC."""
    t = pd.DataFrame({"p": pred, "y": y})
    t["tier"] = pd.qcut(t["y"], 5, labels=False, duplicates="drop")
    top = t[t.tier == t.tier.max()]["p"].values
    bot = t[t.tier == 0]["p"].values
    m, n = len(top), len(bot)
    if m == 0 or n == 0:
        return float("nan"), float("nan"), float("nan")
    
    auc_val = float(sum((tp > bp) + 0.5 * (tp == bp) for tp in top for bp in bot) / (m * n))
    v10 = np.array([np.mean(tp > bot) + 0.5 * np.mean(tp == bot) for tp in top])
    v01 = np.array([np.mean(bp < top) + 0.5 * np.mean(bp == top) for bp in bot])
    s10 = np.var(v10, ddof=1) if m > 1 else 0.0
    s01 = np.var(v01, ddof=1) if n > 1 else 0.0
    se = float(np.sqrt((s10 / m) + (s01 / n)))
    ci_low = float(np.clip(auc_val - 1.95996 * se, 0.0, 1.0))
    ci_high = float(np.clip(auc_val + 1.95996 * se, 0.0, 1.0))
    return auc_val, ci_low, ci_high


def run_canonical_evaluation(
    pred_path: Path = PRED_PATH,
    labels_path: Path = LABELS_PATH,
) -> dict[str, Any]:
    print("=" * 75)
    print("CANONICAL STRICT TEMPORAL EVALUATION (ISSUE 3 AUDITED)")
    print("=" * 75)

    assert pred_path.exists(), f"Missing prediction file: {pred_path}"
    assert labels_path.exists(), f"Missing ground truth file: {labels_path}"

    with open(pred_path, encoding="utf-8") as f:
        pred_bytes = f.read()
        preds_list = json.loads(pred_bytes)
        pred_hash = hashlib.sha256(pred_bytes.encode("utf-8")).hexdigest()

    with open(labels_path, encoding="utf-8") as f:
        label_bytes = f.read()
        labels_dict = json.loads(label_bytes)
        label_hash = hashlib.sha256(label_bytes.encode("utf-8")).hexdigest()

    records = []
    for pr in preds_list:
        uid = pr["product_uid"]
        if uid in labels_dict:
            records.append({
                "product_uid": uid,
                "category": pr["category"],
                "predicted": float(pr["predicted_viability"]),
                "actual": float(labels_dict[uid]["success_score"]),
                "n_reviews": int(labels_dict[uid]["n_reviews"]),
                "price": float(pr["price"]),
                "brand_tier": int(pr["brand_tier"]),
            })

    df = pd.DataFrame(records)
    n_total = len(df)
    assert n_total == 124, f"Expected exactly 124 evaluated test products, got {n_total}"

    p_all = df["predicted"].to_numpy(dtype=float)
    y_all = df["actual"].to_numpy(dtype=float)

    # Primary metrics
    rho, p_val = stats.spearmanr(p_all, y_all)
    rho_ci = boot_ci(lambda a, b: stats.spearmanr(a, b)[0], n_total, p_all, y_all)
    pearson_r, p_pearson = stats.pearsonr(p_all, y_all)
    auc_val, n_top, n_bot = calc_auc_strict(p_all, y_all)
    auc_boot_ci = boot_ci(lambda a, b: calc_auc_strict(a, b)[0], n_total, p_all, y_all)
    _, delong_low, delong_high = delong_auc_ci(p_all, y_all)
    rmse = float(np.sqrt(mean_squared_error(y_all, p_all)))
    mae = float(mean_absolute_error(y_all, p_all))
    r2 = float(r2_score(y_all, p_all))

    # Category breakdown
    cat_results = []
    cat_rhos = []
    for cat, g in df.groupby("category", observed=True):
        p_c = g["predicted"].to_numpy(dtype=float)
        y_c = g["actual"].to_numpy(dtype=float)
        n_c = len(g)
        if n_c >= 5 and np.var(y_c) > 1e-9:
            r_c, pv_c = stats.spearmanr(p_c, y_c)
            cat_rhos.append(r_c)
        else:
            r_c, pv_c = 0.0, 1.0
        auc_c, _, _ = calc_auc_strict(p_c, y_c) if n_c >= 10 else (float("nan"), 0, 0)
        rmse_c = float(np.sqrt(mean_squared_error(y_c, p_c)))
        cat_results.append({
            "category": str(cat),
            "n": int(n_c),
            "spearman_rho": round(float(r_c), 3) if np.isfinite(r_c) else None,
            "p_value": float(pv_c),
            "auc": round(float(auc_c), 3) if np.isfinite(auc_c) else None,
            "rmse": round(float(rmse_c), 2),
        })

    within_cat_mean_rho = float(np.mean(cat_rhos)) if cat_rhos else 0.0

    # Mature cohort (n_reviews >= 30)
    df_mat = df[df["n_reviews"] >= 30]
    n_mat = len(df_mat)
    p_mat = df_mat["predicted"].to_numpy(dtype=float)
    y_mat = df_mat["actual"].to_numpy(dtype=float)
    rho_mat, p_mat_val = stats.spearmanr(p_mat, y_mat)
    rho_mat_ci = boot_ci(lambda a, b: stats.spearmanr(a, b)[0], n_mat, p_mat, y_mat)
    auc_mat, _, _ = calc_auc_strict(p_mat, y_mat)
    auc_mat_ci = boot_ci(lambda a, b: calc_auc_strict(a, b)[0], n_mat, p_mat, y_mat)

    # Save outputs
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "n", "spearman_rho", "p_value", "auc", "rmse"])
        writer.writeheader()
        writer.writerows(cat_results)

    report_dict = {
        "evaluation_name": "Canonical Strict Temporal Holdout",
        "cutoff_epoch": 1635724799,
        "cutoff_date": "2021-10-31T23:59:59Z",
        "prediction_file_sha256": pred_hash,
        "ground_truth_file_sha256": label_hash,
        "n_evaluated": n_total,
        "metrics": {
            "spearman_rho": round(float(rho), 3),
            "spearman_rho_exact": float(rho),
            "spearman_ci95_bootstrap": [round(float(rho_ci[0]), 3), round(float(rho_ci[1]), 3)],
            "p_value_asymptotic": float(p_val),
            "pearson_r": round(float(pearson_r), 3),
            "pearson_p_value": float(p_pearson),
            "auc_roc_quintile": round(float(auc_val), 3),
            "auc_ci95_bootstrap": [round(float(auc_boot_ci[0]), 3), round(float(auc_boot_ci[1]), 3)],
            "auc_ci95_delong": [round(float(delong_low), 3), round(float(delong_high), 3)],
            "rmse": round(float(rmse), 2),
            "mae": round(float(mae), 2),
            "r2_score": round(float(r2), 4),
            "mean_within_category_rho": round(float(within_cat_mean_rho), 3),
        },
        "mature_cohort_ge30": {
            "n": n_mat,
            "spearman_rho": round(float(rho_mat), 3),
            "spearman_ci95_bootstrap": [round(float(rho_mat_ci[0]), 3), round(float(rho_mat_ci[1]), 3)],
            "p_value": float(p_mat_val),
            "auc": round(float(auc_mat), 3),
            "auc_ci95_bootstrap": [round(float(auc_mat_ci[0]), 3), round(float(auc_mat_ci[1]), 3)],
        },
        "per_category": cat_results,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    # Pretty-print formatted primary table
    table_text = (
        f"-----------------------------------------------------------------------\n"
        f"CANONICAL STRICT TEMPORAL EVALUATION REPORT (n = {n_total})\n"
        f"-----------------------------------------------------------------------\n"
        f"Spearman rho (Pooled):        {rho:.3f} (95% CI [{rho_ci[0]:.3f}, {rho_ci[1]:.3f}], p = {p_val:.2e})\n"
        f"Pearson r:                    {pearson_r:.3f} (p = {p_pearson:.2e})\n"
        f"AUC-ROC (Top vs Bot Quintile):{auc_val:.3f} (95% CI [{auc_boot_ci[0]:.3f}, {auc_boot_ci[1]:.3f}], DeLong [{delong_low:.3f}, {delong_high:.3f}])\n"
        f"RMSE:                         {rmse:.2f}\n"
        f"MAE:                          {mae:.2f}\n"
        f"R-squared:                    {r2:.4f}\n"
        f"Mean Within-Category rho:     {within_cat_mean_rho:.3f}\n"
        f"Mature Cohort (n={n_mat}) rho:       {rho_mat:.3f} (95% CI [{rho_mat_ci[0]:.3f}, {rho_mat_ci[1]:.3f}], AUC = {auc_mat:.3f})\n"
        f"-----------------------------------------------------------------------\n"
        f"Prediction SHA256: {pred_hash[:16]}...\n"
        f"Labels SHA256:     {label_hash[:16]}...\n"
        f"-----------------------------------------------------------------------\n"
    )
    print(table_text)
    with open(OUT_TABLE, "w", encoding="utf-8") as f:
        f.write(table_text)

    return report_dict


if __name__ == "__main__":
    run_canonical_evaluation()
