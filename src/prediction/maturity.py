"""Company / product maturity adjustment (Requirement 2).

A brand-new company or a first-of-its-kind product has no market track record, so
consumer-trust and longevity aspects (after-sales support, repairability, reliability,
durability) cannot yet be earned — reviews of comparable products systematically show
lower scores here for unknown brands. This module grades those aspects down and lowers
the overall bridging confidence when maturity signals indicate "new", and returns a
plain-language explanation so the UI can show *why* the score moved.

Kept as a standalone, config-driven module so penalties can be tuned in one place.
Applied AFTER bridging and BEFORE the XGBoost row is built, so the adjustment flows
through both the prediction and its SHAP explanation consistently.
"""

from __future__ import annotations

# ---- tunable configuration -------------------------------------------------

# Aspects penalised when the COMPANY is new (no brand track record for trust/service).
COMPANY_NEW_PENALTIES = {
    "after_sales": 1.5,
    "repairability": 1.0,
    "reliability": 0.5,
}

# Aspects penalised when the PRODUCT is new (first gen / new line — unproven longevity).
PRODUCT_NEW_PENALTIES = {
    "durability": 1.0,
    "reliability": 0.5,
    "repairability": 0.5,
}

# Multiplicative confidence haircuts (compounded when both are new).
COMPANY_NEW_CONFIDENCE_FACTOR = 0.90
PRODUCT_NEW_CONFIDENCE_FACTOR = 0.95

# Accepted values (anything else is treated as the established / mature default).
COMPANY_NEW_VALUES = {"new"}
PRODUCT_NEW_VALUES = {"new", "new_line", "first"}


def is_company_new(v: str | None) -> bool:
    return (v or "").strip().lower() in COMPANY_NEW_VALUES


def is_product_new(v: str | None) -> bool:
    return (v or "").strip().lower() in PRODUCT_NEW_VALUES


def apply_maturity_adjustments(scores: dict[str, float], grounded: dict[str, bool],
                               confidence: float, company_maturity: str | None,
                               product_maturity: str | None) -> dict:
    """Return the maturity-adjusted view of a bridged prediction.

    Args:
        scores:     {aspect: score 0-10}   (mutated copy returned, input untouched)
        grounded:   {aspect: bool}         evidence-backed flags from bridging
        confidence: float 0-1              grounding-adjusted bridging confidence
        company_maturity / product_maturity: 'new' | 'established'/'iterated' | None

    Returns dict with adjusted scores/grounded/confidence, the set of aspects that
    were graded down, and human-readable notes for the UI.
    """
    company_new = is_company_new(company_maturity)
    product_new = is_product_new(product_maturity)

    adj_scores = dict(scores)
    adj_grounded = dict(grounded)
    penalties: dict[str, float] = {}

    def _accumulate(table: dict[str, float]):
        for aspect, pen in table.items():
            if aspect in adj_scores:
                penalties[aspect] = penalties.get(aspect, 0.0) + pen

    if company_new:
        _accumulate(COMPANY_NEW_PENALTIES)
    if product_new:
        _accumulate(PRODUCT_NEW_PENALTIES)

    adjusted_aspects: dict[str, dict] = {}
    for aspect, pen in penalties.items():
        before = float(adj_scores[aspect])
        after = max(0.0, round(before - pen, 2))
        if after != before:
            adj_scores[aspect] = after
            # NOTE: we do NOT touch `grounded` here. `grounded` means "backed by
            # spec evidence" and feeds grounded_frac + the abstain gate; overloading
            # it with a maturity flag double-penalised confidence and could wrongly
            # suppress a well-described new-brand product. The maturity flag lives in
            # `adjusted_aspects` (used for the trust badge + confidence haircut only).
            adjusted_aspects[aspect] = {"before": round(before, 2), "after": after,
                                        "penalty": round(pen, 2)}

    conf = float(confidence)
    if company_new:
        conf *= COMPANY_NEW_CONFIDENCE_FACTOR
    if product_new:
        conf *= PRODUCT_NEW_CONFIDENCE_FACTOR
    conf = round(conf, 2)

    notes = _build_notes(company_new, product_new, adjusted_aspects)

    return {
        "scores": adj_scores,
        "grounded": adj_grounded,
        "confidence": conf,
        "adjusted_aspects": adjusted_aspects,
        "company_new": company_new,
        "product_new": product_new,
        "notes": notes,
        "applied": bool(adjusted_aspects) or company_new or product_new,
    }


def _build_notes(company_new: bool, product_new: bool,
                 adjusted: dict[str, dict]) -> list[str]:
    notes: list[str] = []
    if not (company_new or product_new):
        return notes
    names = ", ".join(a.replace("_", " ") for a in adjusted) or "trust-related aspects"
    if company_new and product_new:
        notes.append(
            f"New company and new product: {names} were graded down and flagged "
            "lower-trust because there is no market history yet to earn them, and "
            "overall confidence was reduced accordingly."
        )
    elif company_new:
        notes.append(
            f"New company: {names} were graded down and flagged lower-trust — an "
            "unknown brand has no track record for after-sales support or servicing."
        )
    elif product_new:
        notes.append(
            f"New / first-generation product: {names} were graded down — an unproven "
            "product line has no longevity or reliability history yet."
        )
    return notes
