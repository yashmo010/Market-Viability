# Current Leakage Controls Audit

The existing system implements strict temporal leakage isolation:
1. **Physical File Separation**: Test ground truth is stored in `strict_temporal/data/test_labels/ground_truth.json` and blocked during inference.
2. **Zero Test ID Overlap**: Verified 0% overlap between 124 test IDs and 507 training rows.
3. **Strict Timestamp Partitioning**: Max train review timestamp <= 1635724799; Min test first review timestamp > 1635724799.
4. **Scaler Isolation**: Normalization scalers (min/max for volume, rating, velocity) computed exclusively on 507 training products.
5. **Category Profile Invariance**: Price medians, quartiles, and aspect baselines derived solely from training products.
6. **Brand Tier Invariance**: Brand footprint counts only pre-cutoff SKUs; unseen brands default to Tier 0.
7. **Cross-Validation Isolation**: Hyperparameter tuning (tree count 112) performed strictly on 5-fold CV within the 507 training products.
8. **Byte-for-Byte Prediction Invariance**: Test predictions are bit-for-bit identical whether test ground truth files exist or are completely deleted.
9. **Test Suite Status**: 10/10 automated leakage tests pass via `tests/test_temporal_leakage.py`.
