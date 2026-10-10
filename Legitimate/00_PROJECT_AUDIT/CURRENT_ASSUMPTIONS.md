# Current Assumptions Audit

1. **Launch Date Proxy**: The date of the first recorded customer review is used as an empirical lower bound on commercial launch date.
2. **Review-Derived Success Proxy**: The target is explicitly defined as `SuccessScore = 100 * (0.40 * vol_norm + 0.35 * rat_norm + 0.25 * vel_norm)`. It is NOT sales, unit volume, or profit.
3. **9 Physical Aspects**: Assumes consumer perception in physical consumer electronics is adequately spanned by the 9 ontology aspects.
4. **Skeptical Extraction**: Assumes promotional marketing text can be filtered for objective specifications.
5. **Brand Footprint Tiering**: Assumes catalog SKU count prior to cutoff approximates brand market footprint (Tier 0 to 3).
6. **Directional Monotonicity**: Assumes price penalizes viability (-1), while brand tier (+1) and aspect performance (+1) monotonically aid viability.
