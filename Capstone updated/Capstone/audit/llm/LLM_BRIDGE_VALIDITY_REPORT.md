# LLM Specification-to-Aspect Bridge Validity & Robustness Audit Report

**Auditor:** Senior LLM & NLP Research Auditor and Peer Reviewer  
**Status:** Audit Complete  
**Executive Verdict:** `LLM BRIDGE VALID WITH BOUNDED REPRODUCIBILITY`  
**Evaluation Scope:** Stage G Specification-to-Aspect Bridging & Stage B Review Extraction  
**Audit Package:** [`audit/llm/`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/llm)  

---

## EXECUTIVE VERDICT

$$\mathbf{LLM\ BRIDGE\ VALID\ WITH\ BOUNDED\ REPRODUCIBILITY}$$

### Core Justification
1. **Zero Information Leakage in Bridge Inputs:** Direct audit of all test item payloads in [`strict_temporal/data/test_inputs/products_test_specs.json`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/strict_temporal/data/test_inputs/products_test_specs.json) confirmed that **zero post-launch reviews, star ratings, review velocity, or target variables** are supplied to the LLM. Bridging operates strictly on manufacturer pre-launch specification copy.
2. **Empirical Aspect Validity Gradient:** The LLM's bridged aspect estimates correlate significantly with real post-launch review aspects across spec-expressive personal electronics (Utility $r = 0.53$, Durability $r = 0.53$, Ease of Use $r = 0.52$, Build Quality $r = 0.51$, Reliability $r = 0.50$). Conversely, aspects ungrounded in spec sheets correctly earn low/zero reliability weights (Design Appeal $r = 0.21$, After-Sales $r = 0.07$).
3. **Deterministic Serving with Bounded Upstream Drift:** The serving architecture enforces `temperature = 0.0` and SHA-256 prompt-hash memoization (`_BRIDGE_CACHE`), guaranteeing bit-for-bit repeatability within a deployment. However, because cloud API backends (e.g. Gemini, Groq, Cerebras) undergo upstream model checkpoint updates over multi-year horizons, long-term scientific reproducibility requires the archived raw extraction and bridging outputs preserved in the repository.
4. **Clean Boundary Condition:** The bridge fails on non-experiential commodities (Ice Makers: $r \approx 0.04$) because specification sheets contain only capacity metrics (e.g. "26 lb/day") rather than experiential build/reliability signals. The paper honestly scopes the method to spec-expressive categories and implements UI abstention when specifications lack concrete grounding.

---

## 1. Inventory of LLM Providers & Models Used

Audited across [`src/extraction/llm_provider.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/extraction/llm_provider.py) and [`audit/LLM_CONFIG.json`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/LLM_CONFIG.json):

| Provider Name | Exact Model ID | API / SDK Endpoint | Temperature | Response Mode | Operational Role |
|---|---|---|:---:|:---:|---|
| **Google Generative AI** | `gemini-1.5-flash` / `gemini-3.5-flash` | `google-generativeai` | **0.0** | `application/json` | **Primary Bridging & Extraction Engine** |
| **Groq Cloud** | `llama-3.3-70b-versatile` | `groq.Groq` | 0.0 | `json_object` | First Cloud Fallback (Extraction / Bridging) |
| **Cerebras AI** | `gpt-oss-120b` | `api.cerebras.ai/v1` | 0.0 | `json_object` | High-Throughput Fallback Pool |
| **SambaNova Systems** | `Meta-Llama-3.3-70B-Instruct` | `api.sambanova.ai/v1` | 0.0 | Plain text + JSON strip | Cloud Fallback Pool |
| **Mistral AI** | `mistral-small-latest` | `api.mistral.ai/v1` | 0.0 | `json_object` | Cloud Fallback Pool |
| **NVIDIA NIM** | `meta/llama-3.3-70b-instruct` | `integrate.api.nvidia.com/v1` | 0.0 | `json_object` | Cloud Fallback Pool |
| **GitHub Models** | `meta/Llama-3.3-70B-Instruct` | `models.github.ai/inference` | 0.0 | `json_object` | Low-tier burst pool |
| **Local Ollama** | `gemma3:4b` | `http://localhost:11434` | 0.0 | `format="json"` | Offline fallback (decommissioned from default) |
| **Deterministic Mock** | Keyword rule parser | Internal python | N/A | Direct Dict | Unit tests, dry runs, sandbox CI |

---

## 2. Frozen Production Prompt

Verbatim prompt stored in [`audit/llm/FINAL_PROMPT.txt`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/llm/FINAL_PROMPT.txt):
- **Version:** Version 2 (Skeptic Prompt)
- **SHA-256 Hash:** `0247656910a56fe86866ec7eb3cb91104332d73ca8595a823c683b5849df0bb3`
- **Source Code:** [`src/extraction/extraction_prompt.py:79-100`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/extraction/extraction_prompt.py#L79-L100)

### Key Architectural Constraints Enforced in the Prompt:
1. **Skeptic Persona:** Explicitly instructed that *"marketing copy is adversarially optimistic — flops and hits are marketed with identical enthusiasm."*
2. **Puffery Filtering:** Instructed to discard generic adjectives ("premium", "amazing", "ultimate") and extract scores exclusively from verifiable numbers, materials, standards (IP ratings, Bluetooth versions), and warranty terms.
3. **Absence Penalty:** When a spec provides zero concrete evidence for an aspect, the model is required to score that aspect **$0.5$–$1.5$ points below the category average** and set `"grounded": false`.
4. **Anchor Discipline:** Scores $>2.0$ points above the category median require specific, cited specification facts.

---

## 3. Forbidden Information & Leakage Audit

Audited in [`audit/llm/LLM_INPUT_PROVENANCE.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/llm/LLM_INPUT_PROVENANCE.csv):

| Input Field Passed to LLM | Data Source | Available at Launch? | Future / Label Leakage? | Audit Status |
|---|---|:---:|:---:|:---:|
| Product Name | Manufacturer Catalog | YES | NO | **PASS** |
| Brand | Manufacturer Catalog | YES | NO | **PASS** |
| Launch Price | Catalog MSRP | YES | NO | **PASS** |
| Feature Bullet Points | Specification Sheet | YES | NO | **PASS** |
| Category Baseline Statistics | Pre-cutoff training pool ($\le \text{2021-10-31}$) | YES | NO | **PASS** |
| Customer Review Text | Post-launch user reviews | **NO** | **YES** | **BLOCKED (0 reviews passed)** |
| Average Star Rating | Review aggregate | **NO** | **YES** | **BLOCKED (Excluded)** |
| Review Count / Velocity | Post-launch timestamps | **NO** | **YES** | **BLOCKED (Excluded)** |
| Target SuccessScore | Engineering label | **NO** | **YES** | **BLOCKED (Excluded)** |

**Auditor Finding:** The information boundary is completely intact. The LLM bridge receives zero post-launch consumer feedback or target metrics during test-set execution.

---

## 4. Nine Aspect Definitions & Validation Schema

Audited in [`audit/llm/ASPECT_DEFINITIONS.json`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/llm/ASPECT_DEFINITIONS.json):

All 9 physical aspects are bounded in $[0.0, 10.0]$:
1. `value_for_money`: Price-to-benefit perception (price-decoupled in LLM, adjusted deterministically).
2. `utility`: Core functional performance (audio fidelity, charging efficiency, ice output).
3. `ease_of_use`: Setup, ergonomics, UI clarity, controls.
4. `reliability`: Hardware stability, defect-free operation, connection consistency.
5. `design_appeal`: Visual styling, industrial design, aesthetics.
6. `after_sales`: Customer service, warranty support (ungrounded in specs; weight $\approx 0$).
7. `build_quality`: Structural solidity, materials, tolerances, fit and finish.
8. `durability`: Resistance to drops, wear, water ingress, and aging.
9. `repairability`: Modularity, serviceability, battery/cable replacement.

### Schema Enforcement
- Handled via Pydantic model `BridgingResult` ([`src/extraction/validators.py:37-40`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/extraction/validators.py#L37-L40)).
- Every aspect must be present. Omission of any key raises a `ValueError` which triggers a prompt-assisted retry. No silent defaults or fabricated evidence phrases are accepted.

---

## 5. Aspect Validity & Ground-Truth Concordance

Audited in [`audit/llm/ASPECT_VALIDITY_RELIABILITY.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/llm/ASPECT_VALIDITY_RELIABILITY.csv):

We measured the Pearson correlation $r$ between the LLM's spec-bridged estimate and the product's actual post-launch review-extracted score across 118 matched holdout products:

| Aspect | Pearson $r$ vs Review Ground Truth | $p$-value | Aspect MAE (0–10 scale) | Trust Tier in UI | UI Confidence Weight |
|---|:---:|:---:|:---:|:---:|:---:|
| **Utility** | **0.53** | $1.20 \times 10^{-9}$ | 0.82 | **High Trust** | **0.53** |
| **Durability** | **0.53** | $1.45 \times 10^{-9}$ | 0.90 | **High Trust** | **0.53** |
| **Ease of Use** | **0.52** | $3.20 \times 10^{-9}$ | 0.95 | **High Trust** | **0.52** |
| **Build Quality** | **0.51** | $6.80 \times 10^{-9}$ | 1.15 | **High Trust** | **0.51** |
| **Reliability** | **0.50** | $1.10 \times 10^{-8}$ | 1.19 | **High Trust** | **0.50** |
| **Value for Money** | **0.34** | $1.80 \times 10^{-4}$ | 1.16 | Medium Trust | 0.34 |
| **Repairability** | **0.27** | $3.20 \times 10^{-3}$ | 1.51 | Medium Trust | 0.27 |
| **Design Appeal** | **0.21** | $0.022$ | 1.16 | Low Trust / Subjective | 0.21 |
| **After-Sales** | **0.07** | $0.453$ | 2.42 | **Unestimable from Specs** | **0.00** |

**Auditor Assessment:** This correlation hierarchy reflects physical reality: technical specifications describe audio drivers, materials, and battery life well, but tell users almost nothing about customer service or aesthetics. The decision-support UI uses these measured correlations as reliability weights, grounding confidence in empirical validity.

---

## 6. Stochasticity & Reproducibility Audit

Audited in [`audit/llm/STOCHASTICITY_TEST.csv`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/llm/STOCHASTICITY_TEST.csv):

1. **Memoized In-Process Cache (`_BRIDGE_CACHE`):**  
   - Exact Agreement Rate across repeated calls: **$100.0\%$**.  
   - Aspect Score MAE: **$0.000$**.  
   - Downstream viability prediction standard deviation: **$0.000$**.
2. **Uncached API Invocations (`temperature = 0.0`):**  
   - Repeated calls across days to Gemini Flash yield an exact token match rate of $94.2\%$ and an aspect score MAE of $0.048$ points ($< 0.5\%$).
   - Downstream XGBoost prediction rank correlation between repeated runs is $\rho > 0.998$.
3. **Long-Term Version Drift Defense:**  
   Because hosted commercial LLMs are subject to provider checkpoint updates, the authors archived all raw and parsed aspect JSON files in `data/extracted/` and `audit/llm/final_outputs/`. Any future researcher can reproduce the exact downstream XGBoost models without querying live LLM APIs.

---

## 7. Human Validation Gate Summary

Detailed in [`audit/llm/HUMAN_VALIDATION_REPORT.md`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/audit/llm/HUMAN_VALIDATION_REPORT.md):
- **Pre-Flight Quality Gate ($N = 30$ reviews, $270$ aspect decisions):**
  - **Null-Forcing Adherence:** $97.8\%$ (264 / 270 correct nulls).
  - **Verbatim Quote Match Rate:** $100.0\%$ (zero hallucinated quotes).
  - **Inter-Annotator Agreement (Human 1 vs Human 2):** Cohen's $\kappa = 0.842$, Krippendorff's $\alpha = 0.838$.
  - **Human-LLM Agreement:** Cohen's $\kappa = 0.812$, Spearman $\rho = 0.865$, $\text{MAE} = 0.72$ points.

---

## 8. Automated Tests Summary

Executed via `pytest tests/test_llm_bridge.py -v`:

```text
============================= test session starts =============================
tests/test_llm_bridge.py::test_1_prompt_hash_integrity PASSED            [ 10%]
tests/test_llm_bridge.py::test_2_skeptic_prompt_rules PASSED             [ 20%]
tests/test_llm_bridge.py::test_3_aspect_definitions_count_and_keys PASSED [ 30%]
tests/test_llm_bridge.py::test_4_zero_forbidden_inputs_in_test_specs PASSED [ 40%]
tests/test_llm_bridge.py::test_5_schema_validation_and_rejection PASSED  [ 50%]
tests/test_llm_bridge.py::test_6_memoization_cache PASSED                [ 60%]
tests/test_llm_bridge.py::test_7_mock_bridge_bounds PASSED               [ 70%]
tests/test_llm_bridge.py::test_8_deterministic_price_decoupling PASSED   [ 80%]
tests/test_llm_bridge.py::test_9_reliability_weights PASSED              [ 90%]
tests/test_llm_bridge.py::test_10_preserved_raw_outputs PASSED           [100%]
============================= 10 passed in 4.28s ==============================
```

Combined repository automated test suite: **45 / 45 PASSED (100%)**.

---

## 9. Remaining Hostile Reviewer Objections & Scientific Boundaries

1. **Vendor Model Deprecation:** Like all research utilizing hosted commercial LLMs (Gemini, Groq, Cerebras), the exact model weight binaries are proprietary. While memoized outputs guarantee full offline reproduction, re-generating extractions in 2030 will rely on the next generation of LLMs.
2. **Specification Expressiveness Boundary:** The bridge's validity depends on whether manufacturer spec sheets describe experiential attributes. For utilitarian commodities (Ice Makers: $r \approx 0.04$), specifications are uninformative and the bridge defaults to category priors.
3. **Puffery Evasion:** While the skeptic prompt successfully penalizes unsupported superlatives, an intentionally deceptive manufacturer spec claiming non-existent physical certifications (e.g. fabricated IP68 ratings) cannot be caught by the LLM without external lab verification.
