# LLM Specification-to-Aspect Pipeline Architecture

**Auditor:** Senior LLM & NLP Research Auditor  
**Date:** 2026-10-06  
**Pipeline Stage:** Stage G (Bridging) & Stage B (Extraction)  
**Primary Module:** [`src/prediction/bridging_layer.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/prediction/bridging_layer.py)  

---

## 1. End-to-End Data Flow

```text
       RAW PRODUCT SPECIFICATION (JSON / Dict)
  [product_uid, name, brand, price, specs.features]
                           │
                           ▼
                 STAGE 1: INPUT CLEANING
       • Text normalization (quotes, whitespace)
       • Price parsing & validation
       • Feature bullet points extraction (0 reviews allowed)
                           │
                           ▼
            STAGE 2: CATEGORY PROFILE RETRIEVAL
       • Frozen historical profiles: category_profiles.json
       • Median price, p25, p75
       • Average aspect scores (category anchor)
       • Top category pain points & strengths
       • Reddit consumer priorities (pre-cutoff)
                           │
                           ▼
            STAGE 3: PROMPT CONSTRUCTION
       • Skeptic Persona (BRIDGING_PROMPT_V2)
       • Injected specs vs category baseline
       • Absence rule + anchor discipline enforced
       • Output schema: strict JSON with grounded flag
                           │
                           ▼
             STAGE 4: DETERMINISTIC CACHE CHECK
       • Key: SHA-256(prompt.encode('utf-8'))
       • If cache hit: return frozen BridgingResult (0 API tokens)
                           │
                           ▼
              STAGE 5: LLM PROVIDER POOL
       • Primary: gemini_flash (gemini-1.5-flash / gemini-3.5-flash)
       • Hardcoded temperature: 0.0, top_p: 1.0, json_mode: True
       • Fallback on rate limit: groq_llama70b -> cerebras -> sambanova
                           │
                           ▼
          STAGE 6: STRUCTURED VALIDATION & REPAIR
       • Pydantic schema: BridgingResult / BridgingAspectScore
       • Clamping: score in [0.0, 10.0]
       • Missing key detection: raises ValueError (no nulls allowed)
       • Max retries: 2 with explicit correction prompt
                           │
                           ▼
       STAGE 7: POST-BRIDGING DETERMINISTIC PRICE ADJUSTMENT
       • Price-decoupled aspect reasoning
       • value_for_money adjusted from relative price deviation
                           │
                           ▼
           STAGE 8: FEATURE COMPOSITION & PREDICTION
       • Feature vector: 9 aspect scores + 9 mention rates + brand tier + price + category
       • Evaluated by frozen XGBoost regressor (xgb_physical_aspects_only.json)
```

---

## 2. Component Audits by Stage

### Stage 1: Input Cleaning
- **Source:** [`src/prediction/input_gate.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/prediction/input_gate.py)
- **Input:** Raw catalog fields.
- **Auditor Verification:** Verifies that no review text, star ratings, or sales statistics are passed into the input stream. All inputs are strictly pre-launch manufacturer product specifications.

### Stage 2: Category Profiles
- **Source:** [`strict_temporal/frozen_state/category_profiles.json`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/strict_temporal/frozen_state/category_profiles.json)
- **Input:** Pre-cutoff products ($n = 507, \le \text{2021-10-31}$).
- **Auditor Verification:** Profiles are frozen and contain zero information from post-cutoff test products.

### Stage 3: Prompt Construction
- **Source:** [`src/extraction/extraction_prompt.py:79-100`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/extraction/extraction_prompt.py#L79-L100)
- **Prompt:** `BRIDGING_PROMPT_V2` (Skeptic Prompt).
- **Core Rules:**
  1. Ignore marketing puffery and superlatives.
  2. Absence Rule: if an aspect is unmentioned in specs, score $0.5$–$1.5$ points below category mean and set `grounded: false`.
  3. Anchor Discipline: scores $>2.0$ above category average require verifiable spec facts.

### Stage 4: Memoization & Cache
- **Source:** [`src/prediction/bridging_layer.py:22, 56-59`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/prediction/bridging_layer.py#L22)
- **Mechanism:** In-process SHA-256 hash memoization dictionary `_BRIDGE_CACHE`.
- **Reproducibility Guarantee:** An identical product specification produces an identical prompt string, yielding a bit-for-bit identical cached aspect profile on subsequent invocations.

### Stage 5: Multi-Provider Generation
- **Source:** [`src/extraction/llm_provider.py`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/extraction/llm_provider.py)
- **Primary Model:** `gemini-1.5-flash` / `gemini-3.5-flash` (via Google Generative AI SDK).
- **Fallback Rotation:** `llama-3.3-70b-versatile` (Groq), `gpt-oss-120b` (Cerebras), `Meta-Llama-3.3-70B-Instruct` (SambaNova), `mistral-small-latest` (Mistral AI).
- **Parameters:** `temperature = 0.0`, `response_format = {"type": "json_object"}`.

### Stage 6: Validation & Schema Enforcement
- **Source:** [`src/extraction/validators.py:102-121`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/extraction/validators.py#L102-L121)
- **Pydantic Model:** `BridgingResult` containing 9 `BridgingAspectScore` instances.
- **Strict Policy:** All 9 aspect keys must be present. Clamped to $[0.0, 10.0]$. Missing or extra keys trigger an immediate retry with a diagnostic correction prompt.

### Stage 7: Deterministic Price Decoupling
- **Source:** [`src/strict_temporal/predict_test.py:81-93`](file:///c:/Users/LENOVO/OneDrive/Desktop/Capstone%20updated%20%283%29/Capstone%20updated/Capstone/src/strict_temporal/predict_test.py#L81-L93)
- **Mechanism:** In the primary pipeline, the LLM estimates physical quality aspects price-free. `value_for_money` is adjusted deterministically based on launch price deviation from category median price.
