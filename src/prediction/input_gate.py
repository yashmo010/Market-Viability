"""Pre-prediction input sufficiency gate (Requirement 3: confidence threshold / refusal).

Before spending an LLM bridging call and returning a viability score, we check that
the user actually supplied enough concrete detail for a meaningful estimate. If the
input is too sparse, the API refuses to predict and tells the user exactly what to add,
rather than returning a number that would only echo category averages.

This is deliberately a small, self-contained, config-driven module so the threshold and
the scoring weights can be tuned in one place without touching the predictor or the API.
The post-bridging grounding confidence in predictor.py is a *second*, independent layer.
"""

from __future__ import annotations

# ---- tunable configuration -------------------------------------------------

# Minimum number of "meaningful signals" required to attempt a prediction.
MIN_SIGNALS = 3

# A description contributes 1 signal per this many characters, capped below.
CHARS_PER_DESCRIPTION_SIGNAL = 60
MAX_DESCRIPTION_SIGNALS = 4

# Independent of the signal count, we require at least a minimal amount of free-text
# OR a couple of structured spec fields, so a lone price can never pass the gate.
MIN_DESCRIPTION_CHARS = 40
MIN_STRUCTURED_FIELDS_IF_NO_TEXT = 2


def evaluate_sufficiency(description: str, price: float | None,
                         structured_specs: dict | None) -> dict:
    """Return a verdict dict describing whether the input is rich enough to predict.

    {
      "sufficient": bool,
      "signals": int,            # meaningful-signal count we computed
      "required": int,           # MIN_SIGNALS
      "reason": str,             # human-readable explanation (empty if sufficient)
      "suggestions": [str, ...]  # concrete things the user could add
    }
    """
    description = (description or "").strip()
    structured_specs = structured_specs or {}
    filled_specs = {k: v for k, v in structured_specs.items()
                    if v not in (None, "", "None")}
    n_specs = len(filled_specs)
    desc_len = len(description)

    desc_signals = min(desc_len // CHARS_PER_DESCRIPTION_SIGNAL, MAX_DESCRIPTION_SIGNALS)
    price_signal = 1 if (price is not None and price > 0) else 0
    signals = desc_signals + n_specs + price_signal

    has_min_text = desc_len >= MIN_DESCRIPTION_CHARS
    has_enough_specs = n_specs >= MIN_STRUCTURED_FIELDS_IF_NO_TEXT
    substantive = has_min_text or has_enough_specs

    sufficient = signals >= MIN_SIGNALS and substantive

    reason, suggestions = "", []
    if not sufficient:
        suggestions = _suggestions(desc_len, n_specs, price_signal)
        if not substantive:
            reason = (
                "The product details are too sparse for a confident prediction. "
                "Add a real description (materials, key features, battery/performance, "
                "reliability, warranty) or fill in a few category specification fields."
            )
        else:
            reason = (
                "There isn't yet enough concrete detail for a reliable estimate. "
                "A prediction now would mostly reflect category averages rather than "
                "your specific product."
            )
    return {
        "sufficient": sufficient,
        "signals": int(signals),
        "required": MIN_SIGNALS,
        "reason": reason,
        "suggestions": suggestions,
    }


def _suggestions(desc_len: int, n_specs: int, price_signal: int) -> list[str]:
    out: list[str] = []
    if desc_len < MIN_DESCRIPTION_CHARS:
        out.append("Describe the product: build materials, standout features, "
                   "battery/performance, reliability, and warranty.")
    if n_specs < MIN_STRUCTURED_FIELDS_IF_NO_TEXT:
        out.append("Fill in a few of the category-specific specification fields above.")
    if not price_signal:
        out.append("Set a realistic price so it can be judged against category norms.")
    return out
