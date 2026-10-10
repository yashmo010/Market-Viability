# Current Manuscript Claims Audit

Audit of existing claims across `Research_Paper_IEEE_Final.docx`, `paper_ieee/main.tex`, and `paper_full.md`:
1. **Target Terminology**: Correctly designated as a "review-derived market-success proxy" across abstract, intro, and methodology.
2. **Primary Performance Claim**: Claims pooled temporal Spearman rho = 0.562 [0.414, 0.681], AUC = 0.890.
3. **Ablation Claims**: Monotone constraints preserve AUC (0.903/0.890 vs 0.826) despite slight CV R^2 reduction.
4. **Cold Start Claim**: Evaluates 82 unseen brand products (Tier 0) with rho = 0.585.
5. **Oracle Claim**: Oracle review-aspect model achieves rho = 0.738, serving as a post-launch diagnostic ceiling.
6. **Identified Discrepancies to Reconcile**:
   - Some earlier drafts referenced R^2 = 0.566 vs 0.564 (unified to 0.564 in Table 1).
   - Ice maker within-category correlation is modest (rho = 0.179) and must be discussed cautiously.
