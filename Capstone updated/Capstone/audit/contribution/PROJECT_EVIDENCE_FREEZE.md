# Project Evidence Freeze: Issues 1–6 Synthesis

**Freeze Date**: October 2026  
**Status**: STRICT SCIENTIFIC FREEZE  
**Evaluation Protocol**: Frozen Temporal Holdout ($N_{\text{train}}=507$ launched $\le$ Oct 31, 2021; $N_{\text{test}}=124$ launched $>$ Oct 31, 2021)  
**Target Variable**: Composite `SuccessScore` ($40\%$ log volume, $35\%$ average rating, $25\%$ review velocity), min-max normalized strictly using training-set category bounds.

---

## 1. Primary Operational Model Results

- **Architecture**: XGBoost Regressor with Monotonic Constraints on physical feature levers.
- **Feature Set**: 9 LLM-bridged aspect scores (`value_for_money`, `utility`, `ease_of_use`, `reliability`, `design_appeal`, `after_sales`, `build_quality`, `durability`, `repairability`), 9 category mention rates, launch price, brand recognition tier ($0..3$), and category indicators.
- **Pooled Test Spearman Correlation ($\rho$)**: **$0.562$** ($95\%$ CI $[0.428, 0.675]$, $p = 6.42 \times 10^{-11}$).
- **Quintile AUC (Top 20% vs. Bottom 20%)**: **$0.890$** ($95\%$ CI $[0.772, 0.963]$).
- **Error Metrics**: $\text{RMSE} = \mathbf{21.12}$, $\text{MAE} = \mathbf{17.84}$.
- **Seed Stability across 8 seeds $\{10, 42, 123, 456, 789, 999, 1337, 2026\}$**: $\text{Mean } \rho = 0.5623 \pm 0.0000$ (deterministic on frozen features).

---

## 2. Competitive Baseline Results (Pooled $N=124$)

| Model ID | Baseline Model Description | Features | Spearman $\rho$ | $95\%$ CI | $p$-value | Quintile AUC | RMSE | MAE |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Baseline F** | **Category + Brand Ridge** | One-hot Category + Brand Tier | $\mathbf{0.712}$ | $[0.613, 0.793]$ | $1.90 \times 10^{-20}$ | $\mathbf{0.994}$ | $\mathbf{17.58}$ | $\mathbf{14.12}$ |
| **Baseline H2** | **Gradient Boosting (GBDT)** | All features (unconstrained) | $\mathbf{0.698}$ | $[0.590, 0.785]$ | $2.55 \times 10^{-19}$ | $0.970$ | $18.00$ | $14.24$ |
| **Baseline H1** | **Random Forest** | All features (112 trees) | $\mathbf{0.694}$ | $[0.585, 0.781]$ | $4.41 \times 10^{-19}$ | $0.993$ | $17.92$ | $14.47$ |
| **Baseline D** | **Category Median** | Training Category Median | $\mathbf{0.691}$ | $[0.579, 0.776]$ | $9.21 \times 10^{-19}$ | $0.980$ | $18.06$ | $14.17$ |
| **Baseline I2** | **Spec TF-IDF + Price + Cat** | TF-IDF (300 tokens) + Price + Cat | $\mathbf{0.688}$ | $[0.575, 0.776]$ | $1.73 \times 10^{-18}$ | $0.979$ | $16.92$ | $14.24$ |
| **Baseline I1** | **Spec TF-IDF + Ridge** | TF-IDF (300 technical tokens) | $\mathbf{0.683}$ | $[0.569, 0.773]$ | $3.57 \times 10^{-18}$ | $0.979$ | $18.23$ | $14.61$ |
| **Baseline C** | **Category Mean** | Training Category Mean | $\mathbf{0.671}$ | $[0.557, 0.760]$ | $2.49 \times 10^{-17}$ | $0.980$ | $17.88$ | $14.28$ |
| **Baseline G1** | **Ridge Regression** | Numeric features + One-hot Cat | $0.665$ | $[0.548, 0.757]$ | $7.13 \times 10^{-17}$ | $0.988$ | $17.93$ | $14.73$ |
| **Baseline G2** | **Elastic Net** | Numeric features + One-hot Cat | $0.662$ | $[0.546, 0.755]$ | $1.15 \times 10^{-16}$ | $0.988$ | $17.98$ | $14.79$ |
| **Baseline I3** | **Spec TF-IDF + GBDT** | TF-IDF tokens with GBDT | $0.589$ | $[0.457, 0.697]$ | $3.86 \times 10^{-12}$ | $0.887$ | $21.22$ | $17.96$ |
| **PROPOSED** | **XGBoost Monotone** | LLM Aspects + Price + Brand + Cat | $\mathbf{0.562}$ | $[0.428, 0.675]$ | $6.42 \times 10^{-11}$ | $\mathbf{0.890}$ | $\mathbf{21.12}$ | $\mathbf{17.84}$ |
| **Baseline E** | **Brand-Only** | Brand Tier Regressor | $0.472$ | $[0.320, 0.601]$ | $3.68 \times 10^{-8}$ | $0.916$ | $21.90$ | $18.06$ |
| **Baseline A** | **Global Mean** | Scalar Mean ($53.07$) | $0.000$ | $[0.000, 0.000]$ | $1.000$ | $0.500$ | $23.63$ | $19.78$ |
| **Baseline B** | **Global Median** | Scalar Median ($52.88$) | $0.000$ | $[0.000, 0.000]$ | $1.000$ | $0.500$ | $23.63$ | $19.78$ |

---

## 3. Within-Category Head-to-Head Comparison ($N=124$)

| Category | $n$ | Proposed XGBoost | Cat + Brand Ridge | GBDT | Random Forest | TF-IDF + Ridge | Brand-Only | Category Mean/Median |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Bluetooth Speakers** | 7 | 0.536 | 0.578 | **0.643** | -0.143 | -0.286 | 0.578 | *Undefined (NaN)* |
| **Smartwatches** | 39 | 0.415 | **0.549** | 0.370 | 0.208 | 0.140 | **0.549** | *Undefined (NaN)* |
| **Ice Makers** | 36 | 0.179 | -0.160 | **0.272** | 0.141 | 0.106 | -0.160 | *Undefined (NaN)* |
| **Power Banks** | 19 | -0.042 | **0.368** | 0.255 | -0.175 | 0.068 | **0.368** | *Undefined (NaN)* |
| **Wireless Headphones** | 23 | -0.055 | 0.428 | **0.531** | 0.518 | 0.166 | 0.428 | *Undefined (NaN)* |
| **Macro-Average $\bar{\rho}$** | — | **0.207** | **0.352** | **0.414** | **0.110** | **0.039** | **0.352** | *Undefined (NaN)* |
| **Weighted-Average $\bar{\rho}_{\text{weighted}}$** | — | **0.196** | **0.294** | **0.369** | **0.168** | **0.100** | **0.294** | *Undefined (NaN)* |
| **Centered Pooled $\rho_{\text{centered}}$** | — | **0.177** | **0.321** | **0.264** | **0.144** | **0.095** | **0.321** | *Undefined (NaN)* |
| **Intra-Category $C_{\text{within}}$** | — | **0.575** | **0.568** | **0.609** | **0.557** | **0.531** | **0.568** | **0.500** |

---

## 4. Cold-Start Unseen-Brand Decomposition ($N=82$)

Subset of test products from brands never seen in pre-cutoff training ($N=82$):
- **Category Mean**: $\rho = \mathbf{0.686}$ ($p = 1.18 \times 10^{-12}$, $\text{RMSE} = 17.47$, $\text{MAE} = 14.59$)
- **Category + Brand Ridge**: $\rho = \mathbf{0.686}$ ($\text{MAE} = 14.70$, brand fallback = 0)
- **GBDT**: $\rho = \mathbf{0.670}$ ($\text{MAE} = 17.90$)
- **Ablation A (Remove LLM Aspects)**: $\rho = \mathbf{0.664}$ ($\text{MAE} = 14.11$)
- **Category Median**: $\rho = \mathbf{0.663}$ ($\text{MAE} = 13.30$)
- **Spec TF-IDF + Ridge**: $\rho = \mathbf{0.623}$ ($\text{MAE} = 14.70$)
- **Model 2 (LLM Aspects Alone)**: $\rho = \mathbf{0.621}$ ($\text{MAE} = 20.37$)
- **Proposed Full Model**: $\rho = \mathbf{0.585}$ ($\text{MAE} = 18.25$)
- **Ablation B (Remove Brand)**: $\rho = \mathbf{0.544}$ ($\text{MAE} = 20.38$)
- **Brand-Only**: *Undefined (NaN)* ($\text{MAE} = 20.41$)

---

## 5. Controlled Component Ablations ($N=124$)

| Configuration | Condition Tested | Spearman $\rho$ | AUC | RMSE | MAE | $\Delta \rho$ vs. Full | Key Finding |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| **Ablation A** | Remove LLM Aspects (Metadata Only) | **0.726** | **0.994** | 17.12 | 13.92 | **+0.164** | Omitting LLM aspects improves pooled accuracy |
| **Ablation F3** | Remove Commercial / Aesthetic Aspects | **0.667** | **0.957** | 18.42 | 15.01 | **+0.105** | Subjective aspects inject substantial noise |
| **Ablation H** | Text-Only TF-IDF XGBoost | **0.665** | **0.963** | 19.33 | 16.21 | **+0.103** | Raw TF-IDF tokens beat bridged aspects |
| **Ablation I** | Minimal Model (Price + Brand + Top 3 Aspects) | **0.620** | **0.970** | 17.65 | 14.51 | **+0.058** | Pruning noisy aspects improves rank score |
| **Ablation F1** | Remove Physical Build Aspects | **0.573** | **0.886** | 19.24 | 15.89 | **+0.011** | Build quality aspects have marginal impact |
| **Ablation C** | Remove Category Features | **0.571** | **0.916** | 21.37 | 17.95 | **+0.009** | Category is redundant given price + specs |
| **Full Model** | Canonical Reference | **0.562** | **0.890** | 21.12 | 17.84 | 0.000 | Frozen reference |
| **Ablation D** | Remove Monotonic Constraints | **0.542** | **0.879** | 21.52 | 18.05 | **-0.020** | No statistically significant difference ($p=0.453$) |
| **Model 2** | LLM Aspects Alone (No Metadata) | **0.526** | **0.886** | 22.58 | 18.98 | **-0.036** | Autonomous semantic quality signal from text |
| **Ablation G** | Numeric Only (Price + Brand Tier) | **0.512** | **0.953** | 23.47 | 18.78 | **-0.050** | Pure numerical metadata without text |
| **Ablation F2** | Remove Experiential Aspects | **0.494** | **0.842** | 21.08 | 17.71 | **-0.068** | Experiential aspects carry strongest signal |
| **Ablation B** | Remove Brand Tier | **0.458** | **0.842** | 22.47 | 18.91 | **-0.104** | Within-category collapses from $+0.207$ to $-0.180$ |
| **Ablation E** | Raw Target (Unnormalized) | **0.404** | **0.830** | 10.44 | 8.21 | **-0.158** | Normalization is mathematically vital |

---

## 6. Oracle Ceiling Benchmark

- **Oracle Model (True Review Aspects)**: Spearman $\rho = \mathbf{0.754}$ ($95\%$ CI $[0.669, 0.826]$), Quintile AUC $= \mathbf{0.992}$, $\text{RMSE} = 15.42$, $\text{MAE} = 12.45$.
- **Ratio of Spearman Rank Correlations**: $\frac{0.562}{0.7536} = \mathbf{74.5\%}$.
- **Ratio of Squared Spearman Correlations**: $\frac{0.3158}{0.5679} = \mathbf{55.6\%}$.
- **Inter-Prediction Agreement**: $\rho(\hat{y}_{\text{bridge}}, \hat{y}_{\text{oracle}}) = \mathbf{0.628}$ ($p = 3.58 \times 10^{-15}$).

---

## 7. Generalization Boundaries & Category Dissociation

- **Spec-Expressive Category (Smartwatches)**: High bridging fidelity ($r \approx 0.50$), positive within-category ranking ($\rho = 0.415$), positive cold-start ranking ($\rho = 0.253$).
- **Commoditized Capacity Category (Ice Makers)**: Capacity specs do not encode build or durability; bridging fidelity collapses to $r \approx 0.04$.
- **Commoditized Electronics (Wireless Headphones, Power Banks)**: Brand equity completely dominates; without brand tier, within-category correlations collapse to negative values ($\rho = -0.316$ and $-0.274$).

---

## 8. Current Manuscript Claims vs. Empirical Status

| Manuscript Location | Original Claim | Empirical Audit Status | Falsified or Supported |
|---|---|---|:---:|
| **Abstract & Intro** | "Specs-only predictions outperform baselines" | Category+Brand Ridge ($\rho=0.712$) and GBDT ($\rho=0.698$) outperform proposed model ($\rho=0.562$). | **FALSIFIED** |
| **Section IV-B** | "XGBoost posted the best $R^2$ (0.564)" | CV $R^2$ was 0.550; GBDT reached 0.558; temporal holdout $\rho$ is 0.562 vs. 0.698 for GBDT. | **FALSIFIED** |
| **Section V-A** | "Monotonic constraints improve holdout AUC from 0.826 to 0.903" | Paired test difference on temporal holdout is $\Delta \text{AUC} = +0.011$ ($p = 0.753$, insignificant). | **FALSIFIED** |
| **Section V-B** | "Bridging recovers four-fifths of attainable rank correlation" | Valid ratio of correlations is $74.5\%$ (squared correlation ratio $55.6\%$), not recovered information. | **REFINED** |
| **Section V-C** | "Price-only baseline correlates at $\rho = 0.147$, far below model" | Price rank alone is weak within-cat, but Category+Brand priors reach $\rho = 0.712$ pooled. | **MISLEADING AS WRITTEN** |
| **Section V-D** | "Specs predict experiential aspects (utility, durability) but not service or aesthetics" | Human audit and bridging fidelity confirm $r \approx 0.50$ for physical vs. $r \approx 0.07$ for service. | **SUPPORTED** |
| **Section VI** | "System provides calibrated honest decision support with abstention" | Reliability weights, trust badges, and abstention on flat specs function as designed. | **SUPPORTED** |
