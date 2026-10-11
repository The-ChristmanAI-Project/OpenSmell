# Archive: OpenSmell_flagship_correction_20261011

**Date:** 2026-10-11
**Policy:** ARCHIVE_POLICY.md, never erase the past. Every file below is the full
pre-change body from commit 55559e5.

## Why

1. **Cycle double-count.** `opensmell_test_loop.py` and `opensmell_test_loopV2.py`
   incremented `total_cycles` twice per cycle (in `run()` and in
   `SessionStats.record()`). The July 5, 2026 flagship report printed 23,686
   cycles. The real count is 11,843. At normal speed (2.0 s per cycle),
   11,843 cycles take 6h 34m 46s, which matches the 6h 35m run time. The
   doubled total inflated the detection rate (96.19% reported, 92.38% real) and
   halved the alert rate (2.13% reported, 4.26% real). Injection accuracy,
   77.81% (2,276 / 2,925), used separate counters and is unaffected.
2. **Ground-truth logging only half applied.** The ground-truth columns were in
   `opensmell_test_loopV2.py`, but `run_test.sh` and `run_grant_batch.sh` call
   `opensmell_test_loop.py`, which still wrote the old 11-column format. The
   batch script also set `OPENSMELL_LOG_FILE`, which neither loop read.
3. **Mixed log removed from the working tree.** `opensmell_log.csv` held
   10,222 rows with ground truth and 4,769 rows without, all written on
   2026-07-08 by two loops appending to the same file at once. The short rows
   sat under the 14-column header and misread by column name. It is preserved
   here in full and cannot be cited as an audited log.
4. **Labeled accuracy settled.** Docs said 88.7%; `opensmell_engine_truth.json`
   said 87.2%. The committed `opensmell2_labeled_experiment.csv` gives 87.22%
   exact (54,951 / 63,000) and 89.05% group (56,102 / 63,000). 88.7% does not
   reproduce from committed data. Docs now state 87.2% exact and 89.1% group.

## Paths (pre-change bodies)

- CLAIM_LOCK.md
- VALIDATION.md
- BIOMARKER_SPECIFICITY.md
- SCORECARD.md
- README.md
- regulatory/q_sub_outline.md
- NOTICE_PACKAGE/README.md
- NOTICE_PACKAGE/01_METHODS.md
- NOTICE_PACKAGE/docs/CLAIM_LOCK.md
- NOTICE_PACKAGE/docs/VALIDATION.md
- NOTICE_PACKAGE/docs/SCORECARD.md
- opensmell_test_loop.py
- opensmell_test_loopV2.py
- run_grant_batch.sh
- opensmell_log.csv (removed from working tree, mixed schema)

## Not done in this change

- Deposit to the storage repo (`EverettNC/storage`, `OpenSmell/archives/`) per
  policy section 1.3. Needs credentials that were not available in this session.
- The Round 1 figure (78.8%) in BIOMARKER_SPECIFICITY.md has no committed data
  behind it and was left as written.
