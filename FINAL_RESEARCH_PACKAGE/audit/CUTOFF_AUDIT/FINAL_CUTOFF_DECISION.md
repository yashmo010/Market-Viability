# Final Cutoff Decision Report

**Audit Protocol:** Protocol-Audit on Temporal Cutoff Validity  
**Execution Context:** 2026 Reporting Year  
**Status:** **VALID AS FROZEN 2021 (OUTCOME A)**

---

## 1. Why the Current Primary Cutoff is 2021
The primary temporal cutoff is formally set to **October 31, 2021, 23:59:59 UTC** ($T_{\text{epoch}} = 1635724799$). 
It represents an **empirical dataset boundary**, not the study execution date.
In the underlying dataset of physical consumer electronics (whose data collection concludes in September 2023), October 31, 2021 provides a natural, principled ~80/20 train/test partition:
- **507 Pre-Cutoff Training Products (80.34%):** First reviewed between February 2006 and October 2021, supported by 43,599 historical customer reviews.
- **124 Post-Cutoff Temporal-Test Products (19.66%):** First reviewed between November 2021 and February 2023, evaluated launch-blind from pre-launch specifications alone.

Crucially, this boundary provides all 124 test products with a post-launch exposure window of **7 to 22 months** before corpus closure, allowing consumer review volume, star ratings, and review velocity to mature into defensible outcome proxies.

---

## 2. Whether Later Cutoffs are Feasible from Current Data
**No later cutoff is feasible as a primary benchmark without severe sample starvation and category collapse:**
- **Mid-2022 Cutoff (2022-06-30):** Shrinks the test pool to $n = 41$ products (6.5% of dataset), reducing Bluetooth Speakers to a single product ($n = 1$) and Power Banks to $n = 6$.
- **End-2022 Cutoff (2022-12-31):** Collapses the test pool to only $n = 3$ products across only two categories (Ice Makers: 2, Smartwatches: 1), leaving three categories completely empty ($n = 0$).
- **2023, 2024, 2025, or 2026 Cutoffs:** Produce **$n = 0$ test products**, because the web harvesting of the benchmark database ended in September 2023.

Therefore, under objective, predeclared sample-adequacy criteria, no later cutoff can replace October 31, 2021.

---

## 3. Whether Any Cutoff Change Was Made
**NO.** The primary cutoff remains strictly frozen at **October 31, 2021, 23:59:59 UTC**.
Per prompt instructions:
- We do not change the cutoff merely because the research is being reported in 2026.
- We do not use today's date as the cutoff.
- We do not optimize the cutoff to inflate performance scores.
- The 2021 protocol is frozen as the **CURRENT PRIMARY PROTOCOL (OUTCOME A)**.

---

## 4. Why Performance Was Not Used to Choose the Cutoff
To prevent post-hoc overfitting and publication bias:
- All candidate cutoff assessments were conducted under **strict performance blindness**.
- Zero machine learning models were evaluated on candidate test splits during the feasibility audit.
- No metrics ($\rho$, AUC, RMSE, MAE, Kendall's $\tau$, NDCG) were computed for alternative dates.
- The decision to retain October 31, 2021 was determined solely by sample size adequacy ($n = 124$), five-category representation, and post-launch label maturity.

---

## 5. How the 2022–2024 External Cohort Relates to the Primary Temporal Protocol
The study maintains a strict hierarchical separation:
- **Primary Research Benchmark:** The frozen October 31, 2021 holdout ($n = 124$), strictly quarantined to evaluate launch-blind representations against reproduced canonical baselines under identical controlled conditions.
- **Secondary External Application Evaluation:** An independent real-world cohort of **155 Amazon products launched between 2022 and 2024** (150 quantitatively evaluable with accumulated post-launch market feedback, plus 5 prospective pre-launch items).
- The 2022–2024 external cohort demonstrates that the synchronized inference engine generalizes successfully to subsequent market eras ($\rho = 0.501$ pooled; $\rho = 0.686$ on new/startup entrants, AUC = 0.940). It provides external real-world validation without altering or contaminating the historical primary research benchmark.

---

## 6. Exact Wording Used in the Final Manuscript

### In Section II (Frozen Evaluation Protocol & Leakage Controls):
> *"To guarantee that reported performance reflects genuine forward-in-time predictive validity rather than retrospective overfitting, we institute a frozen temporal evaluation protocol strictly anchored to an empirical launch cutoff date of October 31, 2021, 23:59:59 UTC [23]–[25]. The October 31, 2021 boundary defines the historical information boundary for the primary evaluation; it is not the date of model development or study execution (conducted in 2026). It was fixed as the study's temporal protocol prior to final evaluation to ensure adequate sample size across all five device categories and a sufficient post-launch exposure window (7–22 months) for ground-truth review metric stabilization.*
>
> *1) Training Pool (n = 507): Comprises physical consumer electronics products whose earliest recorded customer review occurred on or before the cutoff date, drawing from 43,599 historical customer reviews across five distinct categories (Bluetooth speakers, ice makers, power banks, smartwatches, wireless headphones).*
>
> *2) Launch-Blind Temporal Test Pool (n = 124): Comprises products whose first recorded customer review occurred strictly after the temporal cutoff (spanning November 1, 2021 to February 28, 2023), serving as the empirical launch-timing proxy. The model receives only launch specifications, price, category, and brand name. Customer reviews, star ratings, and post-launch volume metrics are physically quarantined.*
>
> *3) Isolated Target Definition: The regression target is defined as a composite proxy: SuccessScore = 100 * (0.40 * vol_norm + 0.35 * rat_norm + 0.25 * vel_norm), where normalization bounds are fitted strictly on the pre-cutoff training pool [26]."*

### In Section VI (External Application Validation):
> *"To evaluate real-world transferability beyond the frozen historical research holdout, the synchronized application inference engine was deployed across an independent external cohort of 155 Amazon products launched between 2022 and 2024 across the five canonical categories (Table VIII). On the 150 products with accumulated market validation, the model achieves a Spearman rank correlation of rho = 0.501 (95% CI [0.362, 0.617]) and top-versus-bottom quintile AUC of 0.873 (MAE = 15.87 pts). Crucially, startup and new-entrant brands (n = 21) exhibited robust performance (rho = 0.686, AUC = 0.940), confirming that the model's launch-blind representations generalize cleanly to post-2022 market cohorts without domain collapse."*
