# CURRENT EVALUATION LITERATURE SOURCES
**Methodological Foundations for Product Viability & Cold-Start Benchmarking**  
**Autonomous Publication Engineering System — Current Modified Project**  

---

## 1. Item Cold-Start & Content-Based Evaluation

1. **G. Adomavicius and A. Tuzhilin**, "Toward the next generation of recommender systems: A survey of the state-of-the-art and possible extensions," *IEEE Transactions on Knowledge and Data Engineering*, vol. 17, no. 6, pp. 734–749, 2005.  
   - *Relevance*: Establishes the foundational distinction between collaborative filtering and content-based feature bridging when historical user interaction histories are completely unavailable (launch-blind regime).
   
2. **F. Ricci, L. Rokach, and B. Shapira**, *Recommender Systems Handbook*, 3rd ed. New York, NY, USA: Springer, 2022.  
   - *Relevance*: Defines standardized item cold-start protocol requirements: strict quarantine of target interaction logs and evaluation of rank-order alignment on unseen items.

3. **C. Volkers, M. de Gemmis, P. Lops, and G. Semeraro**, "Improving cold-start recommendations using item-based stereotypes," *User Modeling and User-Adapted Interaction*, Springer, vol. 31, no. 3, pp. 493–527, 2021.  
   - *Relevance*: Demonstrates that semantic prior extraction from item catalog metadata mitigates cold-start sparsity and justifies evaluating top-$K$ list ranking metrics alongside point errors.

4. **S. Rendle, C. Freudenthaler, Z. Gantner, and L. Schmidt-Thieme**, "BPR: Bayesian personalized ranking from implicit feedback," in *Proc. 25th Conf. Uncertainty in Artificial Intelligence (UAI)*, AUAI Press, 2009, pp. 452–461.  
   - *Relevance*: Methodological justification for monotonic pair concordance and ranking metrics (Kendall's $\tau$ and Spearman's $\rho$) over uncalibrated mean squared errors alone.

---

## 2. Information Retrieval & List-Ranking Quality

5. **K. Järvelin and J. Kekäläinen**, "Cumulated gain-based evaluation of retrieval techniques," *ACM Transactions on Information Systems (TOIS)*, vol. 20, no. 4, pp. 422–446, 2002.  
   - *Relevance*: Primary authoritative formulation of Normalized Discounted Cumulative Gain (NDCG@$K$), confirming how continuous graded relevance scores (here, SuccessScore $\in [0, 100]$) are properly discounted by logarithmic rank positions.

6. **M. G. Kendall**, "A new measure of rank correlation," *Biometrika*, vol. 30, no. 1/2, pp. 81–93, 1938.  
   - *Relevance*: Establishes Kendall's tau ($\tau$) as the non-parametric probability difference between concordant and discordant pairs ($P(\text{concordant}) - P(\text{discordant})$), providing orthogonal rank agreement evidence complementary to Spearman's $\rho$.

---

## 3. Tabular Machine Learning & Out-of-Fold Model Comparison

7. **L. Grinsztajn, E. Oyallon, and G. Varoquaux**, "Why do tree-based models still outperform deep learning on tabular data?" in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 35, 2022, pp. 507–520.  
   - *Relevance*: Justifies the candidate learner suite (XGBoost, GBDT, Random Forest, Ridge, SVR, MLP) and explains why gradient-boosted decision trees inherently outperform deep neural nets on tabular datasets of moderate size ($n \approx 500$).

8. **T. Chen and C. Guestrin**, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD)*, 2016, pp. 785–794.  
   - *Relevance*: Validates exact gradient boosting implementation and native domain monotonic inequality regularization ($\frac{\partial \hat{y}}{\partial x_j} \ge 0$).

9. **T. Hastie, R. Tibshirani, and J. Friedman**, *The Elements of Statistical Learning: Data Mining, Inference, and Prediction*, 2nd ed. New York, NY, USA: Springer, 2009.  
   - *Relevance*: Establishes standard $K$-fold Out-of-Fold (OOF) cross-validation protocol, requiring fold-contained imputation, scaling, and hyperparameter selection.

---

## 4. Extreme-Group & Derived Decision Analysis

10. **T. Fawcett**, "An introduction to ROC analysis," *Pattern Recognition Letters*, vol. 27, no. 8, pp. 861–874, 2006.  
    - *Relevance*: Authoritative reference for Area Under the ROC Curve (ROC-AUC) as a threshold-independent, prevalence-invariant discrimination measure separating top-quintile from bottom-quintile outcomes.
