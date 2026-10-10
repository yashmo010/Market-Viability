# Category Reconciliation & Canon Lock

## 1. Discrepancy Identification
An intermediate report generated during initial exploratory runs listed "Air Fryers" ($n=16$) as a sixth within-category row, altering test product counts for other categories.

## 2. Root Cause Analysis
- The raw dataset in `Capstone updated/Capstone/data/final/products_physical.json` and the frozen temporal split in `Capstone updated/Capstone/strict_temporal/data/test_inputs/products_test_specs.json` contain **EXACTLY 5 categories**:
  1. `bluetooth_speakers`
  2. `ice_makers`
  3. `power_banks`
  4. `smartwatches`
  5. `wireless_headphones`
- "Air Fryers" never existed in the frozen temporal test set (`124` products) or the training set (`507` products). It appeared only due to a hardcoded mapping in an experimental auxiliary visualization script.
- The actual computed results in `Legitimate/04_EXPERIMENTS/WITHIN_CATEGORY_ANALYSIS.csv` were always based on the canonical five categories:
  - `bluetooth_speakers`: $n = 7$
  - `ice_makers`: $n = 36$
  - `power_banks`: $n = 19$
  - `smartwatches`: $n = 39$
  - `wireless_headphones`: $n = 23$
  - Total: $7 + 36 + 19 + 39 + 23 = 124$ products.

## 3. Mandatory Remediation Action
- "Air Fryers" is completely purged from all manuscripts, figures, tables, code, manifests, and documentation.
- The canonical 5 categories are strictly enforced across:
  - Within-category tables and figures.
  - Application input dropdowns and evaluation sets.
  - Research text, captions, and abstracts.
