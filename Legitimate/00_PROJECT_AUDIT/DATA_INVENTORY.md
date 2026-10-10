# Data Inventory: Strict Temporal Protocol (Cutoff: Oct 31, 2021)

## 1. Primary Datasets
| Dataset | Location | Product Count | Review Count | Access Restriction |
|---|---|---|---|---|
| Pre-Cutoff Training Pool | `strict_temporal/data/train/products.json` | 507 | 43,599 (`reviews.json`) | Training & 5-fold CV only |
| Launch-Blind Test Inputs | `strict_temporal/data/test_inputs/products_test_specs.json` | 124 | 0 (specs only) | Inference input only; no review text |
| Isolated Ground Truth | `strict_temporal/data/test_labels/ground_truth.json` | 124 | Post-cutoff reviews | Sealed; loaded strictly at evaluation |

## 2. Category Distribution
| Category | Train Products (n=507) | Test Products (n=124) | Total (n=631) |
|---|---|---|---|
| Bluetooth Speakers | 128 | 7 | 135 |
| Ice Makers | 109 | 36 | 145 |
| Power Banks | 80 | 19 | 99 |
| Smartwatches | 75 | 39 | 114 |
| Wireless Headphones | 115 | 23 | 138 |

## 3. Brand Footprint & Cold-Start Stratification
- **Training Brands**: 252 unique brands mapped into Tiers 0-3 based strictly on pre-cutoff catalog footprint.
- **Test Brand Overlap**: 42 products from known brands (Tier >= 1), 82 products from unseen / new brands (Tier 0).
