# LLM Validation Rules: Cold-Start Rich Extraction

## 1. Schema Conformance
- Every extracted object MUST conform strictly to `LLM_SCHEMA.json`.
- Missing required fields, invalid enums, or out-of-range floats ([0.0, 1.0] or [0.0, 10.0]) result in immediate rejection.

## 2. Verbatim Evidence Grounding
- For any attribute labeled `inference_type == "technical_spec"`, `source_text` MUST be an exact substring match (case-insensitive normalized) of the input specifications.
- If an attribute claim is not directly found in the text, it MUST be labeled as `inference_type == "inferred_attribute"` or omitted entirely.
- Falsely claiming ungrounded facts as technical specifications triggers an anti-hallucination penalty.

## 3. Strict Pre-Launch Isolation (Anti-Leakage)
- The extraction prompt NEVER contains review text, star ratings, review counts, sales ranks, or market targets.
- Output features MUST NOT contain predictions of success score, sales volume, or customer review sentiment.
- `sentiment_direction` and `customer_relevance` represent input features modeling consumer design perception, NOT empirical market outcomes.

## 4. Determinism & Caching
- Extraction uses deterministic decoding (temperature = 0.0 or low fixed setting).
- Outputs are indexed and cached by SHA-256 hash of `(title + brand + category + price + specifications)`.
- If an exact input hash has already been processed, the verified cached representation is reused without duplicate network calls.
