"""Strict Temporal Evaluation Stage.

Loads predictions and ONLY THEN loads ground truth test labels to compute
evaluation metrics.
No model or prediction code has access to these metrics.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[2]
PRED_PATH = ROOT / "strict_temporal/predictions/predictions.json"
LABELS_PATH = ROOT / "strict_temporal/data/test_labels/ground_truth.json"
AUDIT_DIR = ROOT / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def calc_auc(pred: np.ndarray, y: np.ndarray) -> float:
    t = pd.DataFrame({"p": pred, "y": y})
    t["tier"] = pd.qcut(t["y"], 5, labels=False, duplicates="drop")
    top = t[t.tier == t.tier.max()]["p"].values
    bot = t[t.tier == 0]["p"].values
    if len(top) == 0 or len(bot) == 0:
        return float("nan")
    return float(sum((tp > bp) + 0.5 * (tp == bp) for tp in top for bp in bot) / (len(top) * len(bot)))


def boot_ci(fn, n: int, *arrays, n_boot: int = 10000, seed: int = 42) -> tuple[float, float]:
    rng = np.random.RandomState(seed)
    vals = []
    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        v = fn(*[a[idx] for a in arrays])
        if np.isfinite(v):
            vals.append(v)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def evaluate_temporal_holdout(
    pred_path: Path = PRED_PATH,
    labels_path: Path = LABELS_PATH,
    out_json: Path = AUDIT_DIR / "STRICT_TEST_RESULTS.json",
    out_csv: Path = AUDIT_DIR / "CATEGORY_RESULTS.csv",
) -> dict[str, Any]:
    print("=" * 70)
    print("STEP 11: STRICT TEMPORAL EVALUATION (REVEALING LABELS)")
    print("=" * 70)

    with open(pred_path, encoding="utf-8") as f:
        preds_list: list[dict] = json.load(f)
    with open(labels_path, encoding="utf-8") as f:
        labels_dict: dict[str, dict] = json.load(f)

    # Align predictions with ground truth labels
    records = []
    for pr in preds_list:
        uid = pr["product_uid"]
        if uid in labels_dict:
            records.append({
                "product_uid": uid,
                "category": pr["category"],
                "predicted": pr["predicted_viability"],
                "actual": labels_dict[uid]["success_score"],
                "n_reviews": labels_dict[uid]["n_reviews"],
                "price": pr["price"],
                "brand_tier": pr["brand_tier"],
                "bridge_source": pr.get("bridge_source", ""),
            })

    df = pd.DataFrame(records)
    n_total = len(df)
    print(f"Evaluated {n_total} temporal test products.")

    p_all = df["predicted"].to_numpy(dtype=float)
    y_all = df["actual"].to_numpy(dtype=float)

    # Primary metrics
    rho, p_val = stats.spearmanr(p_all, y_all)
    rho_ci = boot_ci(lambda a, b: stats.spearmanr(a, b)[0], n_total, p_all, y_all)
    auc = calc_auc(p_all, y_all)
    auc_ci = boot_ci(calc_auc, n_total, p_all, y_all)
    rmse = float(np.sqrt(mean_squared_error(y_all, p_all)))
    mae = float(mean_absolute_error(y_all, p_all))

    # Per-category metrics
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
        auc_c = calc_auc(p_c, y_c) if n_c >= 10 else float("nan")
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

    # Mature sub-cohort (n_reviews >= 30)
    mature_df = df[df["n_reviews"] >= 30]
    n_mature = len(mature_df)
    if n_mature >= 10:
        p_mat = mature_df["predicted"].to_numpy(dtype=float)
        y_mat = mature_df["actual"].to_numpy(dtype=float)
        rho_mat, pv_mat = stats.spearmanr(p_mat, y_mat)
        rho_mat_ci = boot_ci(lambda a, b: stats.spearmanr(a, b)[0], n_mature, p_mat, y_mat)
        auc_mat = calc_auc(p_mat, y_mat)
        auc_mat_ci = boot_ci(calc_auc, n_mature, p_mat, y_mat)
        mature_metrics = {
            "n": n_mature,
            "spearman_rho": round(float(rho_mat), 3),
            "spearman_rho_ci95": [round(float(rho_mat_ci[0]), 3), round(float(rho_mat_ci[1]), 3)],
            "p_value": float(pv_mat),
            "auc": round(float(auc_mat), 3),
            "auc_ci95": [round(float(auc_mat_ci[0]), 3), round(float(auc_mat_ci[1]), 3)],
        }
    else:
        mature_metrics = {"n": n_mature, "note": "Insufficient mature products (<10)"}

    # Save CSV
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "n", "spearman_rho", "p_value", "auc", "rmse"])
        writer.writeheader()
        writer.writerows(cat_results)

    # Save JSON summary
    results_summary = {
        "evaluation_name": "Strict Launch-Blind Temporal Holdout",
        "cutoff_date": "2021-10-31T23:59:59Z",
        "n_evaluated": n_total,
        "spearman_rho": round(float(rho), 3),
        "spearman_rho_ci95": [round(float(rho_ci[0]), 3), round(float(rho_ci[1]), 3)],
        "p_value": float(p_val),
        "auc_roc_quintile": round(float(auc), 3),
        "auc_ci95": [round(float(auc_ci[0]), 3), round(float(auc_ci[1]), 3)],
        "rmse": round(rmse, 2),
        "mae": round(mae, 2),
        "mean_within_category_rho": round(within_cat_mean_rho, 3),
        "per_category": cat_results,
        "mature_cohort_ge30": mature_metrics,
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)

    print("\n--- RESULTS SUMMARY ---")
    print(f"Sample Size (n): {n_total}")
    print(f"Spearman rho: {rho:.3f} (95% CI: [{rho_ci[0]:.3f}, {rho_ci[1]:.3f}], p = {p_val:.2e})")
    print(f"Quintile AUC: {auc:.3f} (95% CI: [{auc_ci[0]:.3f}, {auc_ci[1]:.3f}])")
    print(f"RMSE: {rmse:.2f}, MAE: {mae:.2f}")
    print(f"Mean Within-Category rho: {within_cat_mean_rho:.3f}")
    print("\nPer-Category Breakdown:")
    for cr in cat_results:
        print(f"  {cr['category']:24s} n={cr['n']:2d} rho={cr['spearman_rho']} AUC={cr['auc']} RMSE={cr['rmse']}")
    if "spearman_rho" in mature_metrics:
        print(f"\nMature Cohort (>=30 reviews, n={n_mature}): rho={mature_metrics['spearman_rho']} (CI {mature_metrics['spearman_rho_ci95']}), AUC={mature_metrics['auc']}")

    return results_summary


if __name__ == "__main__":
    evaluate_temporal_holdout()
