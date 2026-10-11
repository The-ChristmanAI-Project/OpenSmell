# OpenSmell — Notice Package

**The Christman AI Project / Luma Cognify AI**  
**For:** VOC / breath / ambient labs · hospital innovation · IRBs · scientific partners  
**Open this pack in ~15 minutes.**  
**Status:** Screening-support / investigational. **Not FDA-approved. Not a clinical diagnostic.**

---

## What OpenSmell is (purpose)

Listen to the body **chemically, early**. Volatile organic compound (VOC) signals are classified against a fixed, literature-grounded library on low-cost hardware. Matches and confidence scores support **human review** — not autonomous diagnosis. Client owns all biological data. Dignity first.

---

## Pack contents

| # | File | What you get |
|---|------|----------------|
| 0 | `README.md` | This index |
| 1 | `01_METHODS.md` | Classifier method, thresholds, limits, metrics |
| 2 | `02_HARDWARE_STATION.md` | BOM, wiring, serial path, QC |
| 3 | `03_THE_ASK.md` | What we want from serious partners |
| 4 | `reproduce.sh` | One command: unit tests + short seeded sim inject |
| 5 | `docs/SCORECARD.md` | Per-profile **simulation** recall (all 21 live) |
| 6 | `docs/opensmell_engine_truth.json` | Live inventory + headline sim metrics |
| 7 | `docs/INTENDED_USE.md` | Intended use + prohibited claims |
| 8 | `docs/CLAIM_LOCK.md` | Allowed public numbers only |
| 9 | `docs/VALIDATION.md` | Flagship endurance methodology |
| 10 | `docs/SNAPSHOT_UTC.txt` | When this pack’s docs were copied |
| 11 | `../SENSOR_TRUTH.md` | MQ-135 physics + characterization protocol (repo root) |

Repo root (parent of this folder) holds the full engine: `open_smell2.py`, bio-sim, tests.

---

## Numbers you may quote (simulation only)

From `docs/opensmell_engine_truth.json` and `docs/VALIDATION.md` at pack snapshot:

| Fact | Value |
|------|--------|
| Live profiles | **21** |
| Catalog / research_only | **26** / **5** |
| Sensor channels (proxy bands) | **20** |
| Flagship injection accuracy (full noise) | **77.81%** · 11,843 cycles |
| Flagship detection rate | **92.38%** |
| Controlled labeled (see SCORECARD / BIOMARKER docs) | closed-loop sim only |
| Clinical accuracy | **Not claimed** |

Channel names (e.g. “benzene”) are **MQ-135-class response-band proxies**, not GC-MS species IDs.

---

## Reproduce in under 5 minutes

From the **OpenSmell repository root** (parent of `NOTICE_PACKAGE/`):

```bash
chmod +x NOTICE_PACKAGE/reproduce.sh
./NOTICE_PACKAGE/reproduce.sh
```

Expect: unit/integration tests OK · short seeded inject · report path printed · claim lint OK.

---

## Honesty law

- Simulation is simulation.  
- No inflated profile counts (live set is 21).  
- No diagnostic marketing language.  
- Degenerate pairs (e.g. diabetes T1/T2 ketosis) are not faked.  
- Past corrections are archived; we do not erase history.

---

## Contact

**Everett Nathaniel Christman**  
Founder — The Christman AI Project  
Operating under Luma Cognify AI  

**Ask:** see `03_THE_ASK.md`

© 2025–2026 The Christman AI Project. All Rights Reserved.
