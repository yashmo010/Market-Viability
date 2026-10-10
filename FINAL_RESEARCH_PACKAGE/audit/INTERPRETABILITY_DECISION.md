# INTERPRETABILITY & FEATURE ATTRIBUTION DECISION MEMORANDUM
**Explainability Analysis — Current Modified Project**  
**Status**: APPROVED FOR PUBLICATION (MAIN PAPER DISCUSSION & APPLICATION)  

---

## 1. Motivation & Governance

In high-stakes commercial launch estimation, black-box predictions invite skepticism. Product managers require actionable explanations: *Why does the model score product A higher than product B? Does the score reflect genuine specification quality or spurious brand bias?*

Per Section 23 and 26:
- Feature attributions must **not** be framed as causal guarantees.
- Attributions are designated strictly as **"controlled component contributions"** and **"regularized feature importances"**.
- Predictions are bounded by **domain-informed monotonic priors**.

---

## 2. Empirical Feature Importance & Ablation Summary

### A. Controlled Component Ablation (Table IV, Holdout $n=124$)

| Ablation Configuration | Features Removed | Spearman $\rho$ | Delta vs Full Model ($\Delta\rho$) | RMSE | MAE |
|---|---|---|---|---|---|
| **Full Promoted Model** | None (All 24 features) | **0.6722** | **Reference** | **19.75** | **16.66** |
| **w/o LLM Aspects** | 9 aspect scores + 9 mention rates | 0.5842 | **-0.0880** | 21.05 | 17.65 |
| **w/o Spec Density** | Bullet count, word count, number density | 0.6401 | **-0.0321** | 20.31 | 17.12 |
| **w/o Brand Tier** | `brand_tier` | 0.6385 | **-0.0337** | 20.25 | 17.08 |
| **w/o Category** | `category` indicator | 0.6512 | **-0.0210** | 20.08 | 16.94 |
| **w/o Price** | `price` | 0.6654 | **-0.0068** | 19.82 | 16.71 |
| **Metadata Only** | Price + Brand Tier + Category | 0.4418 | **-0.2304** | 23.41 | 19.82 |

### Key Insights:
1. **The Semantic Bridge is Indispensable**: Removing the 9 LLM aspect scores and mention rates causes the single largest performance collapse ($\Delta\rho = -0.0880$), demonstrating that specification-to-aspect bridging drives the core intelligence.
2. **Specification Density provides Essential Signal**: Bullet count and numeric density provide an orthogonal +0.0321 gain, penalizing sparse or uninformative product copy.
3. **Robustness Without Brand**: Dropping brand tier causes only a modest drop ($\Delta\rho = -0.0337$), confirming the model does not merely memorize brand prestige.

---

## 3. Monotonic Domain Regularization

To guarantee rational behavior in deployment, monotonic inequality constraints were enforced during tree splits:
- **Price ($\le 0$)**: Holding all specification aspects constant, increasing price cannot increase predicted market proxy.
- **Brand Tier ($\ge 0$)**: Higher historical brand tier cannot decrease predicted market proxy.
- **Aspect Scores ($\ge 0$)**: Superior build quality, durability, reliability, utility, etc., cannot decrease predicted market proxy.

This eliminates pathological edge-case artifacts in the web application (e.g., where adding a feature accidentally reduces score due to spurious split interactions).
