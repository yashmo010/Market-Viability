# Reliability Report — Market Success Viability Predictor

_Physical-only system · 5 categories · 631 trained products (~43.6k reviews) · generated 2026-09-23_

This document states how reliable the system's viability predictions are, how that was
measured, and where the honest limits lie. Two evaluations are reported:

1. **In-sample cross-validation (CV)** — how well the model fits, on real extracted aspects.
2. **Out-of-sample external holdout** — the honest test: predict *unseen* products from their
   **specs** (via the LLM bridging chain), compare to their actual success.

The external holdout is the number to cite for "does the system generalize."

---

## 1. Headline numbers

| Measure | Value | Notes |
|---|---|---|
| **External holdout ρ (Spearman, pooled 5-cat)** | **+0.437** | p = 7.6e-07, 95% CI **[+0.275, +0.576]** |
| **External holdout AUC** (flop vs. top-tier) | **0.826** | |
| **Mean within-category ρ** | **≈ 0.39** | stricter measure (see §4) |
| CV R² — aspects-only (production headline) | 0.603 | PASS (gate ≥ 0.35) |
| CV R² — aspects-only, *pure* (no brand_tier) | 0.566 | the "pure ABSA contribution" figure |
| CV R² — full model | 0.893 | inflated by rating leakage (see §5) |

**Interpretation:** the system reliably **rank-orders** product viability out-of-sample
(ρ ≈ 0.4, AUC ≈ 0.83, p < 1e-6) from specs alone. It is trustworthy at the level of
"which products will do better," **not** precise point prediction.

---

## 2. External holdout protocol (the honest test)

- **Holdout set:** 118 products, all 5 categories, each with aspect scores produced by the
  **frozen production bridging pipeline** (skeptic prompt v2) from the product's specs —
  i.e. the exact specs→aspects path a live prediction uses, never the product's real reviews.
- **No leakage:** the model was **retrained from scratch on the other 513 products**, with
  every holdout product excluded. Category mention-rate priors were computed on the training
  split only.
- **Evaluation:** predict each holdout product's viability from its bridged specs → correlate
  against its actual within-category `success_score`. Spearman ρ (rank), AUC (top-quintile vs.
  bottom-quintile separation), 5000-sample bootstrap CI.
- **Result file:** `models/benchmarks/fresh_holdout_5cat.json`.

> Supersedes the earlier ρ = 0.317 figure, which was **contaminated** — those holdout
> products were present in the training set. The clean number is both higher and trustworthy.

### Secondary (4-category, zero fresh LLM cost)
Retrained on 532, evaluated on the 99 products with pre-cached bridged specs:
ρ = +0.347, 95% CI [+0.155, +0.523], AUC = 0.748.

### Temporal (forward-in-time) holdout — strictest test [RIGOROUS]
Train **only** on products launched ≤ Oct 2021 (n=505, CV-selected best_iteration=178);
predict **all** products launched Oct 2021 → Feb 2023 from specs alone (the real "predict before
launch" scenario). Coverage 125/126 newest-20% products.
- **Pooled ρ = +0.559**, p = 1.2e-11, 95% CI **[+0.429, +0.666]**; **AUC = 0.925**; n = 125.
- The signal **does not collapse forward in time** — pre-empts the "you only did a random split"
  objection. But the pooled number is **largely between-category** (see below): the model ranks
  the whole market forward in time, mostly by separating categories.
- **Per-category forward ρ (the honest within-category skill):** smartwatches **+0.41**,
  wireless_headphones **+0.31**, power_banks **−0.03**, ice_makers **−0.03**
  (bluetooth_speakers n=7, not reported). **Mean within-category ρ ≈ +0.16.**
- **Key finding:** within-category forward skill is modest and uneven. Only smartwatches and
  headphones hold up forward in time. **power_banks collapses** (0.43 random-split → ~0 forward =
  genuine temporal drift, e.g. newer GaN/USB-C designs); **ice_makers stays ~0** (the §7 bridging
  boundary). Forecasting the future within a category (0.16) is harder than interpolating a random
  split (0.39) — exactly what a proper temporal test should expose. The rigorous run corrected the
  earlier indicative (n=66) optimism.
- **Paper framing:** forward validity is strongest for spec-expressive personal electronics
  (smartwatches, headphones) and weakest for fast-evolving (power banks) or commodity
  (ice makers) categories.
- Result file: `models/benchmarks/temporal_holdout_rigorous.json` (indicative n=66 run in
  `temporal_holdout.json`, superseded).

---

## 3. Per-category external validity

| Category | n | Holdout ρ | CV R² (aspects-only) |
|---|---:|---:|---:|
| smartwatches | 25 | +0.596 | 0.553 |
| bluetooth_speakers | 24 | +0.511 | 0.618 |
| power_banks | 25 | +0.425 | 0.595 |
| wireless_headphones | 25 | +0.310 | 0.349 |
| ice_makers | 19 | +0.114 | 0.338 |

**ice_makers is weak for a specific, diagnosed reason — not thin data** (it has 145 products,
more than power_banks). Its bridged predictions are weak because spec sheets don't let the LLM
differentiate ice makers on experiential aspects; see **§7 (boundary condition)**. Per-category
n is only 19–25, so individual per-category ρ values are high-variance — the **pooled ρ with its
CI** is the reliable summary.

---

## 4. Pooled vs. within-category (honesty note)

`success_score` is min-max normalized **within category**, so the pooled ρ = 0.437 benefits
partly from *between-category* rank structure, not purely from within-category predictive
skill. The stricter measure — the **mean of the five per-category ρ values (≈ 0.39)** — is the
true "can it rank products *within* a category" number. Both are solid; cite the per-category
mean for the conservative claim and the pooled ρ/AUC (with CI) for the headline.

---

## 5. Leakage guard

- `corr(avg_rating, success_score) = 0.457` — `avg_rating` is 35% of the label by construction,
  so the **full model (R² 0.893) is optimistic** and must not be the headline claim.
- The **aspects-only model** drops the label-correlated metadata
  (`price, avg_rating, rating_count_log, review_velocity`) and is the honest measure of what the
  LLM-extracted aspects contribute. It drives the production `viability_pct`.

---

## 6. Model design decisions affecting reliability

- **brand_tier feature** (ordinal 0–3, from brand catalog footprint; *not* label-derived).
  #2 feature by SHAP in the headline model. Lifted aspects-only CV R² 0.566 → 0.603, with the
  gain concentrated in repeat-brand categories (speakers/power_banks/smartwatches). Lets the
  model *learn* the brand-maturity effect (established-brand trust transfers; unknown-brand does
  not) instead of relying on a hand-tuned penalty. Greenfield/new brand → tier 0; known
  established brand → its real tier; unspecified → neutral established prior.
- **Price monotonicity** (`monotone_constraints={"price": -1}` on the full model): fixes a
  spurious *rising*-price effect the unconstrained model had learned (higher price → higher
  predicted viability at fixed quality). Post-fix price is non-increasing; full-model R² held
  at 0.893.
- **Rank-preserving calibration** of the headline onto a readable 0–100 scale (interpolated
  percentile map vs. a real-product reference distribution). Cosmetic/monotonic only — provably
  does **not** change ρ or AUC.
- **Reliability-weighted confidence.** Confidence no longer counts grounded aspects uniformly;
  each aspect contributes in proportion to its **measured** spec→aspect bridging fidelity
  (Pearson r of bridged-vs-real, `models/bridging_reliability.json`). Fixes a miscalibration in
  the LLM's self-reported "grounded" flag: uninformative aspects (after_sales, r≈0.07) no longer
  move confidence; high-fidelity aspects (utility/reliability/durability, r≈0.5) carry it. Built
  by `scripts/compute_bridging_reliability.py`; mean per-aspect bridging r ≈ 0.39 (n=118).

---

## 7. Category boundary condition — when spec→aspect bridging works

The system's predictive power tracks **how well a category's specifications encode experiential
quality**. This is the clearest evidence in the study of *when the method works and when it does
not*, and it explains the ice_makers result without excluding the category.

Diagnostic (ice_makers vs. the other four):
- **Not an extraction problem** — ice_makers has the *best* aspect coverage (8.7 of 9 aspects
  discussed per product) and normal mention rates.
- **Not a label / no-signal problem** — ice_makers has the **strongest within-category
  aspect→success correlation of any category** (mean |r| = 0.32 vs. 0.09–0.24 elsewhere). The
  signal is present in the real reviews.
- **The weakness is entirely in bridging.** The LLM assigns nearly **identical** aspect scores
  to every ice maker (bridged-score std across products: reliability 0.08, build_quality 0.13,
  durability 0.13, ease_of_use 0.15 — effectively flat). Flat inputs carry no ranking
  information, so ice-maker bridging fidelity is **r ≈ 0.04**, vs. ~0.39 pooled and 0.45–0.56
  for the same aspects in personal-electronics categories.
- **Root cause:** headphone/speaker/smartwatch specs describe experiential attributes (sound,
  comfort, battery) that map to aspects; ice-maker specs are capacity/speed numbers
  ("26 lb/day, 9 cubes in 6 min") that convey nothing about reliability, durability, or build —
  so the LLM cannot differentiate products and defaults them all to the category prior.

**Framing for the paper:** *"The approach is bounded to spec-expressive categories. Where
specifications encode experiential quality (personal electronics), bridging fidelity is high
(r ≈ 0.5) and forward prediction works; where they encode only physical capacity (commodity
appliances), bridging cannot differentiate products (r ≈ 0.04), bounding predictive validity.
Ice makers serve as the negative control that demonstrates this behavior is principled rather
than random."* Possible future lever: few-shot anchoring in the bridging prompt (show contrasting
real exemplars) to induce score spread; root cause is fundamental, so treat as future work.

---

## 8. Honest limitations

- **Proxy label, not sales.** The target is review-popularity
  (0.40·volume + 0.35·rating + 0.25·velocity), not units sold. A better label (e.g. Amazon Best
  Sellers Rank) is the highest-leverage future improvement.
- **Survivorship bias.** Every training product already accumulated reviews (median
  rating_count ≈ 5,100; 10th pct ≈ 314). There are **no launch-failures or zero-traction
  products** in the data, so genuine new-brand ("greenfield") prediction is extrapolation and
  carries irreducible uncertainty (distribution/marketing effects specs can't capture). The
  abstain/confidence machinery manages this rather than removing it.
- **Data volume.** ~99–147 products/category (want 500–1000+). Weak categories most affected.
- **Point precision.** The system is reliable for *ranking*, not exact viability percentages.

---

## 9. Reproduce

```bash
python src/training/run_training.py --force        # retrain (brand_tier + monotone), prints CV + gates
python scripts/compute_bridging_reliability.py     # per-aspect bridging r -> confidence weights
# external holdout: retrain-on-513, evaluate 118 via cached bridged specs
#   -> models/benchmarks/fresh_holdout_5cat.json
# temporal holdout: train launches <= 2021-10, test newer via bridging
#   -> models/benchmarks/temporal_holdout.json
```
