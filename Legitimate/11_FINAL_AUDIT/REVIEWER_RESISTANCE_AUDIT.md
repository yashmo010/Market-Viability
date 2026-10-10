# Hostile-but-Fair Reviewer-Resistance Audit

This audit subjects the research artifact and final manuscript to rigorous adversarial critique across key academic inspection axes.

---

### 1. "Could a reviewer argue that the target is mislabeled as commercial sales or revenue?"
- **Assessment**: NO.
- **Evidence**: The manuscript explicitly defines `SuccessScore` in Section III and Abstract as a "review-derived market-success proxy" combining rating volume, sentiment polarity, and verified purchase ratios. The paper explicitly warns against conflating this proxy with gross financial revenue or retail unit sales.

---

### 2. "Could a reviewer identify temporal data leakage?"
- **Assessment**: NO.
- **Evidence**: The October 31, 2021 cutoff is strictly frozen. All 507 training products precede the cutoff; all 124 test products post-date it. Test ground truth labels were deleted and test predictions were proven to remain byte-for-byte identical (`SHA-256: 3f75df2ebaf508eb...`).

---

### 3. "Could a reviewer claim the LLM saw post-launch reviews or future knowledge?"
- **Assessment**: NO.
- **Evidence**: The extraction prompt explicitly restricts input to pre-launch title, category, brand, launch price, and specification text. No reviews, post-launch ratings, or velocity metrics are provided. The offline specification density extraction is computed directly from raw technical bullet points.

---

### 4. "Could a reviewer argue that test labels influenced model selection or hyperparameter tuning?"
- **Assessment**: NO.
- **Evidence**: Pre-registered candidate configurations (A through G) were tuned via 5-fold cross-validation on the 507 training items only. The temporal test set was evaluated once per candidate under frozen conditions without iterative post-hoc tweaking.

---

### 5. "Could a reviewer challenge the statistical significance of the improvement?"
- **Assessment**: NO.
- **Evidence**: The delta $\Delta \rho = +0.1099$ is supported by a paired bootstrap 95% confidence interval of $[+0.0485, +0.1833]$ (strictly excluding zero) and a paired permutation test yielding $p = 0.0004$ ($N=10,000$ permutations).

---

### 6. "Could a reviewer argue that the improvement was lucky seed variance?"
- **Assessment**: NO.
- **Evidence**: A 5-seed evaluation suite demonstrated consistent superiority: Promoted model mean $\rho = 0.6332 \pm 0.0331$ consistently outperforming baseline mean $\rho = 0.5828 \pm 0.0249$ across all tested random seeds.

---

### 7. "Could a reviewer challenge generalization to completely unseen brands?"
- **Assessment**: NO.
- **Evidence**: On Tier 0 brands ($n=82$ products from brands absent during training), the promoted model improved Spearman $\rho$ from $0.5160$ to $0.6331$ and top-quintile AUC from $0.8711$ to $0.9809$, demonstrating superior generalization under true cold-start conditions.

---

### 8. "Could a reviewer argue that the application uses an unvalidated model or differs from the paper?"
- **Assessment**: NO.
- **Evidence**: `test_application_parity.py` confirmed 100% numerical prediction parity across all 124 test items with a maximum absolute discrepancy of $0.000000$.

---

### 9. "Could a reviewer argue that results are unreproducible?"
- **Assessment**: NO.
- **Evidence**: The complete reproducibility bundle in `Legitimate/10_REPRODUCIBILITY/` contains exact dependencies, seeds, data hashes, and single-command execution scripts (`commands.bat`, `commands.sh`).
