# Model Inventory: Upstream Representations & Downstream Models

## 1. Upstream Semantic Representation (Original Model_O)
- **Concept**: Skeptical LLM aspect scoring (`audit/llm/FINAL_PROMPT.txt`).
- **Aspect Ontology**: 9 physical product aspects:
  1. `value_for_money` (0-10)
  2. `utility` (0-10)
  3. `ease_of_use` (0-10)
  4. `reliability` (0-10)
  5. `design_appeal` (0-10)
  6. `after_sales` (0-10)
  7. `build_quality` (0-10)
  8. `durability` (0-10)
  9. `repairability` (0-10)
- **Mention Rates**: 9 aspect mention rates derived from training category profiles.
- **Compression Bottleneck**: Product specification text is compressed into 9 broad scalar ratings, discarding fine-grained technical attribute values (e.g. 5000 mAh, 120 Hz, IP67).

## 2. Downstream Model Architecture (XGBoost Regressor)
- **Artifact**: `strict_temporal/frozen_state/xgb_physical_aspects_only.json`
- **Feature Manifest**: 22 features:
  - Launch price (1)
  - 9 physical aspect scores (9)
  - 9 aspect mention rates (9)
  - Brand tier (1)
  - Category categorical (1)
  - [Target: success_score]
- **Hyperparameters**:
  - `objective`: `reg:squarederror`
  - `n_estimators`: 112 (selected via 5-fold CV early stopping on training set)
  - `learning_rate`: 0.05
  - `max_depth`: 5
  - `min_child_weight`: 3
  - `subsample`: 0.8
  - `colsample_bytree`: 0.8
  - `tree_method`: `hist`
  - `random_state`: 42
  - `monotone_constraints`: `price`: -1, `brand_tier`: +1, all 9 aspect scores: +1

## 3. Canonical Baseline Models
- **Baseline A/B**: Global Mean & Median (rho = 0.0)
- **Baseline C/D**: Category Mean (rho = 0.671), Category Median (rho = 0.691)
- **Baseline E**: Brand-Only Ridge (rho = 0.227)
- **Baseline F**: Category + Brand Ridge (rho = 0.712)
- **Baseline G1/G2**: Ridge (rho = 0.651), ElasticNet (rho = 0.652)
- **Baseline H1/H2**: Random Forest (rho = 0.694), Gradient Boosting (rho = 0.698)
- **Baseline I1/I2/I3**: Raw Specs TF-IDF + Ridge (rho = 0.683), TF-IDF + Price + Cat (rho = 0.688), TF-IDF + GBDT (rho = 0.693)
