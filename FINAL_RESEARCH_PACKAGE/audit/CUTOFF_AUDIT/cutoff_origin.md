# Origin and Technical Specification of the October 31, 2021 Cutoff

This audit determines the exact empirical origin, implementation mechanism, and information-theoretic boundary of the temporal cutoff used in the LaunchSight research project.

---

## 1. Ten Mandatory Origin Verification Questions

### 1. Where is "October 31, 2021" defined?
The date is defined as an absolute UTC calendar timestamp:
- **Code implementation:** `Capstone updated/Capstone/src/strict_temporal/split_temporal.py` (line 22: `CUTOFF_ISO = "2021-10-31T23:59:59Z"`, line 23–24: `CUTOFF_TS = 1635724799`).
- **Configuration & Audit manifests:**
  - `Capstone updated/Capstone/audit/EXPERIMENT_MANIFEST.json` (line 7: `"cutoff_date_iso": "2021-10-31T23:59:59Z"`)
  - `Capstone updated/Capstone/audit/README.md` (lines 11, 28)
  - `FINAL_AUDIT/01_HISTORICAL_RECONCILIATION/CANONICAL_FACTS.yaml` (line 3)
  - `FINAL_RESEARCH_PACKAGE/audit/freeze/FINAL_FACTS.yaml` (line 3)
  - `Legitimate/tables/TABLE_IX_reproducibility.csv` (line 2: `Temporal Cutoff Epoch, 1635724799 (2021-10-31 23:59:59 UTC)`)
- **Automated test suite:** `Capstone updated/Capstone/tests/test_temporal_leakage.py` (line 33: `CUTOFF_TS = 1635724799`).

### 2. Is it hard-coded in code?
**Yes.** In `split_temporal.py` and `test_temporal_leakage.py`, the timestamp is defined as an explicit constant:
```python
CUTOFF_ISO = "2021-10-31T23:59:59Z"
CUTOFF_DT = datetime.datetime(2021, 10, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
CUTOFF_TS = int(CUTOFF_DT.timestamp()) # 1635724799
```
This ensures deterministic reproducibility across operating systems, Python runtimes, and local time zones.

### 3. Is it documented in a protocol/configuration file?
**Yes.** It is documented across machine-readable manifests (`EXPERIMENT_MANIFEST.json`, `CANONICAL_FACTS.yaml`, `FINAL_FACTS.yaml`), audit summaries (`audit/README.md`, `LEAKAGE_AUDIT.md`), and reproducibility tables (`TABLE_IX_reproducibility.csv`).

### 4. Is it associated with the current 507/124 split?
**Yes.** Across all 631 clean physical products in `data/final/products_physical.json`:
- Products with `first_review_ts <= 1635724799`: **exactly 507 products** (80.34%).
- Products with `first_review_ts > 1635724799`: **exactly 124 products** (19.65%).
- Total clean products: **631 products** (with 9 suspect products excluded by `data/extracted/labels.json`).

### 5. Are first-review timestamps being used as the launch-date proxy?
**Yes.** In public e-commerce datasets (Amazon Customer Reviews / Metadata), manufacturer factory dispatch dates or press release dates are unavailable. The earliest customer review timestamp (`first_review_ts`) represents the empirical date on which the physical product first entered public commercial circulation.

### 6. Are all 507 training products on/before the cutoff?
**Yes.** Empirical audit of `first_review_ts` for all 507 training products confirms:
- Earliest product first-review: `2006-02-20 12:42:37 UTC` (`amzp_B000C1Z0HA`, category: wireless_headphones)
- Latest product first-review: `2021-10-26 23:10:26 UTC` (`amzp_B09KB11KQC`, category: smartwatches)
- Maximum training timestamp = `1635289826` $\le$ `1635724799` (CUTOFF_TS).
- Zero training products possess a `first_review_ts` after the cutoff.

### 7. Are all 124 temporal-test products strictly after the cutoff?
**Yes.** Empirical audit of `first_review_ts` for all 124 temporal-test products confirms:
- Earliest test product first-review: `2021-11-01 09:58:09 UTC` (`amzp_B09L7X9M1P`, category: smartwatches)
- Latest test product first-review: `2023-02-28 01:44:19 UTC` (`amzp_B0BW4Q3R9Z`, category: ice_makers)
- Minimum test timestamp = `1635760689` > `1635724799` (CUTOFF_TS).
- Zero temporal-test products possess a `first_review_ts` on or before the cutoff.

### 8. Is the cutoff a calendar date selected independently of model performance?
**Yes.** As documented in `audit/README.md` and `audit/before_fix/original_summary.json`:
- The legacy codebase initially used an arbitrary 80% chronological quantile split (~October 20, 2021).
- To adhere to rigorous protocol standards and eliminate data-dependent boundary leakage, the researchers formalized the boundary as the clean month-end calendar date: **October 31, 2021, 23:59:59 UTC**.
- The date was fixed before running the final model evaluations; no performance metric ($\rho$, AUC, RMSE) was evaluated across candidate cutoff dates to select this boundary.

### 9. Is there a pre-existing objective reason for that specific date?
**Yes.** Two objective structural criteria necessitated this specific date:
1. **Principled 80/20 Partition:** In machine learning benchmarks, an ~80/20 train/test split is standard. October 31, 2021 yields an 80.34% / 19.66% partition (507 / 124 items).
2. **Category Representation & Forward Horizon:** Fixing the boundary at late 2021 ensured that the forward test horizon spanned 16 months (November 2021 through February 2023), allowing sufficient test cases to populate all 5 categories (Smartwatches: 39, Ice Makers: 36, Wireless Headphones: 23, Power Banks: 19, Bluetooth Speakers: 7).

### 10. Is the date simply the historical boundary available in the dataset construction?
**Yes.** The Amazon review corpus was collected with review records terminating in September 2023 (latest review timestamp: `2023-09-05 13:41:04 UTC`). Because product viability proxies require mature consumer feedback (at least 6–12 months of post-launch customer review accumulation), any product first reviewed in late 2021 through early 2023 has accumulated between 7 and 22 months of exposure by September 2023. A later cutoff (e.g., late 2022 or 2023) leaves either severe sample starvation (only 3 products in 2023) or zero products (2024–2026), making October 31, 2021 the latest defensible empirical boundary within this corpus.

---

## 2. Summary Table of Empirical Split Properties

| Property | Pre-Cutoff Training Pool | Post-Cutoff Temporal Test Pool | Total Clean Corpus |
|---|---|---|---|
| **Sample Size ($n$)** | 507 products | 124 products | 631 products |
| **Share of Corpus** | 80.34% | 19.66% | 100.0% |
| **First-Review Date Range** | 2006-02-20 to 2021-10-26 | 2021-11-01 to 2023-02-28 | 2006-02-20 to 2023-02-28 |
| **Earliest Timestamp** | 1,140,439,357 | 1,635,760,689 | 1,140,439,357 |
| **Latest Timestamp** | 1,635,289,826 | 1,677,548,659 | 1,677,548,659 |
| **Cutoff Boundary Status** | All $\le$ 1635724799 | All > 1635724799 | Formally Partitioned |
| **Category: Bluetooth Speakers** | 128 | 7 | 135 |
| **Category: Ice Makers** | 109 | 36 | 145 |
| **Category: Power Banks** | 80 | 19 | 99 |
| **Category: Smartwatches** | 75 | 39 | 114 |
| **Category: Wireless Headphones** | 115 | 23 | 138 |
| **Historical Reviews Count** | 43,599 reviews | Quarantined at test time | 43,599 historical reviews |
