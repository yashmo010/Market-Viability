# Scientific Justification: Why an October 31, 2021 Cutoff is Used in a 2026 Paper

## 1. Executive Summary: The Core Question

**The Reviewer's Question:**  
*"Why is a 2021 temporal cutoff being used in a research paper prepared and reported in 2026?"*

**The Scientific Answer:**  
The October 31, 2021 date is an **empirical information boundary** within a fixed historical e-commerce dataset, **not the date of study execution or model development**. 

The research was conducted and reported in 2026. The 2021 boundary was established to construct a rigorous, forward-in-time temporal benchmark where the model is trained strictly on historical products (pre-November 2021) and evaluated launch-blind on subsequent market entrants (November 2021 through February 2023). 

Within the empirical dataset (whose review collection terminates in September 2023), October 31, 2021 represents the **latest defensible calendar cutoff** that preserves adequate test sample size ($n = 124$), multi-category representation across all five device categories, and sufficient post-launch maturity for customer review signals to stabilize. 

Furthermore, to evaluate real-world transferability beyond this frozen research holdout, the model was separately validated on an independent external cohort of 155 Amazon products launched between 2022 and 2024.

---

## 2. Principle of Three Distinct Dates

To eliminate any ambiguity in the scientific literature, three distinct dates must be maintained separately:

```
[Date A: Research Execution (2026)]
  └── When the study, analyses, algorithms, and manuscript were produced.

[Date B: Temporal Cutoff (October 31, 2021 23:59:59 UTC)]
  └── Historical information boundary dividing pre-cutoff training from post-cutoff holdout.

[Date C: External Application Window (2022–2024)]
  └── Independent external cohort evaluated to verify real-world transfer to later markets.
```

- **Date A $\neq$ Date B:** The manuscript must never imply that the research was performed in 2021. The experiments were conducted in 2026 using a frozen 2021 historical boundary.
- **Date B $\neq$ Date C:** The external validation cohort (155 products from 2022–2024) is a secondary transfer test, not part of the primary 507/124 research holdout split.
- **Date B does not claim to be 2026:** The model does not claim to predict "the 2026 market" from launch specifications; it claims that pre-launch specifications can forecast forward-in-time commercial reception under rigorous temporal quarantine.

---

## 3. Why Later Cutoffs Cannot Serve as the Primary Benchmark

Screening candidate cutoff dates on current clean data (without inspecting model performance, ensuring complete performance blindness) yields the following empirical findings:

| Candidate Cutoff Boundary | Train ($n$) | Test ($n$) | Test % | Category Balance in Test Pool | Verdict |
|---|---|---|---|---|---|
| **2021-10-31 (Current Frozen)** | **507** | **124** | **19.65%** | **All 5 Categories Populated** (7, 36, 19, 39, 23) | **Scientifically Valid & Optimal** |
| **2021-12-31 (End-2021)** | 524 | 107 | 16.96% | All 5 Categories Populated (5, 33, 15, 34, 20) | Feasible, but loses 17 test cases |
| **2022-06-30 (Mid-2022)** | 590 | 41 | 6.50% | Severe category starvation (Speakers: $n=1$) | Infeasible: Insufficient statistical power |
| **2022-12-31 (End-2022)** | 628 | 3 | 0.48% | 3 categories completely empty ($n=0$) | Infeasible: Sample starvation |
| **2023-06-30 (Mid-2023)** | 631 | 0 | 0.00% | Zero products post-cutoff | Infeasible: No test cases exist |
| **2023-12-31 (End-2023)** | 631 | 0 | 0.00% | Zero products post-cutoff | Infeasible: Dataset collection ended Sep 2023 |
| **2024–2026** | 631 | 0 | 0.00% | Zero products post-cutoff | Infeasible: No products exist |

### Structural Constraints Enforcing the 2021 Boundary:
1. **Corpus Collection Horizon:** The underlying web scraping corpus of physical product reviews concludes in September 2023. Products launched in 2024, 2025, or 2026 do not exist in the primary benchmark database (`products_physical.json`).
2. **Label Maturity Window:** Product success metrics (review volume, star rating, velocity) require a minimum maturation period (typically 6–12 months) post-launch. For products launched between November 2021 and February 2023, the collection window (ending September 2023) provides 7 to 22 months of accumulated consumer feedback. Pushing the cutoff later would truncate the maturation window, introducing high variance and survival bias into the target proxy.
3. **Multi-Category Power:** A temporal test set must maintain statistical validity across distinct hardware categories. At the October 31, 2021 cutoff, all 5 categories retain sufficient test products. Any cutoff after mid-2022 reduces Bluetooth speakers to $n \le 1$ and power banks to $n \le 6$.

---

## 4. Performance Blindness Guarantee

In accordance with strict protocol auditing principles:
- **No model metrics ($\rho$, AUC, RMSE, MAE, NDCG, Kendall's $\tau$) were calculated across candidate cutoffs.**
- The October 31, 2021 boundary was audited solely on data-availability, category balance, label maturity, and protocol integrity.
- The decision to maintain October 31, 2021 is driven by scientific validity and sample adequacy, never by metric optimization.

---

## 5. Relationship Between Primary Benchmark and External Validation

The paper establishes a clear two-tier evaluation hierarchy:

1. **Primary Research Benchmark:**  
   - **Protocol:** Frozen forward-in-time holdout partitioned strictly at October 31, 2021 23:59:59 UTC ($n_{\text{train}} = 507$, $n_{\text{test}} = 124$).
   - **Role:** Controlled benchmark against baseline models with identical features, target scalers, and hyperparameter protocols.
2. **Secondary External Application Evaluation:**  
   - **Protocol:** Deployment of synchronized application engine across an independent external cohort of 155 Amazon products launched between 2022 and 2024.
   - **Role:** Confirms real-world transferability to post-2022 product cohorts without compromising the historical research baseline.

---

## 6. Recommended Manuscript Clarification Language

The following exact wording is incorporated into the methodology and limitation sections of the manuscript:

> *"The temporal cutoff of October 31, 2021, 23:59:59 UTC defines the historical information boundary for the primary forward-in-time evaluation; it is not the date of model development or study execution. Products whose earliest recorded customer review occurred on or before this boundary constitute the pre-cutoff training pool ($n = 507$), while products whose first review appeared strictly after the boundary form the launch-blind test cohort ($n = 124$). This boundary was fixed as the study's frozen protocol prior to final evaluation to ensure adequate sample size across all five device categories and a sufficient post-launch exposure window (7–22 months) for ground-truth review metric stabilization. To confirm temporal transfer beyond this historical cohort, the synchronized decision-support engine was independently evaluated on an external real-world cohort of 155 products launched between 2022 and 2024."*
