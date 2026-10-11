# OpenSmell

### Olfactory intelligence & VOC screening-support engine  
**The Christman AI Project — Luma Cognify AI**  
**Everett Nathaniel Christman**

---

> *The body tells the truth chemically long before it shows up physically.  
> OpenSmell is built to listen — honestly, early, and without harvesting anyone’s biology.*

---

## Purpose

OpenSmell listens to **volatile organic compounds (VOCs)** as **screening-support** signals — not as a diagnosis, not as an FDA-cleared device, and not as a data-harvest product.

| It is | It is not |
|-------|-----------|
| Continuous / research-ready VOC **proxy** classification | A clinical diagnostic |
| Low-cost hardware path (~$15–25) + full software sim | GC-MS species identification |
| Auditable local logs; **client owns data** | A biometric marketplace |
| Part of the Christman care constellation (optional alert routing) | A cure or treatment order |

**Live inventory (source of truth: `opensmell_engine_truth.json`):**  
**21** live sensor-grounded profiles · **26** catalog · **5** research-only (excluded from live matching) · **20** proxy channels.

---

## Progression (where we actually are)

Status date: **2026-07-19**. Only measured work is listed as done.

### Done

| Milestone | Evidence in repo |
|-----------|------------------|
| Single classify engine for sim + production path | `open_smell2.py` |
| Bio-realistic sim + continuous test harness | `opensmell_bio_sim.py`, `opensmell_test_loop.py` |
| Flagship sim endurance | `VALIDATION.md` — 11,843 cycles · **77.81%** injection accuracy · **92.38%** detection (sim, full noise) |
| Labeled sim specificity work + per-profile scorecard | `BIOMARKER_SPECIFICITY.md`, `SCORECARD.md` |
| Unit / integration tests | `python3 -m unittest test_open_smell2 test_alert_integration` (34 tests) |
| **Claim lock** (never inflated profile counts; no fantasy clinical claims) | `CLAIM_LOCK.md`, `scripts/claim_lint.py` |
| Intended use + prohibited claims | `INTENDED_USE.md` |
| **Notice package** for labs (methods, hardware, ask, reproduce) | `NOTICE_PACKAGE/` |
| Regulatory **drafts** (not filings) | `regulatory/` |
| Archive policy; past claim-lock bodies preserved | `ARCHIVE_POLICY.md`, `archives/` |

### In progress / next moves (in order)

| # | Move | Goal |
|---|------|------|
| **1** | **Sensor truth** | In progress — see [`SENSOR_TRUTH.md`](./SENSOR_TRUTH.md) (MQ-135 physics, L1–L3 protocol) |
| **2** | **License lock** | Resolve Apache file vs Sovereign README (`LICENSE_CLARITY.md`) before any MoU |
| **3** | **Lab / IRB outreach** | Ship `NOTICE_PACKAGE/` to people who can run real bio; non-diagnostic protocols |
| **4** | **Regulatory spine** | Counsel on Q-Sub / risk file; still **not** “FDA approved” |
| **5** | **Institutional kit** | On-prem research pilot packaging after notice converts |
| **6** | **Scale** | Multi-site and geography only on evidence |

We do **not** mark “worldwide hospitals” or “clinical accuracy” as complete. Those are earned.

---

## Honesty law (non-negotiable)

- **Simulation is simulation.** Never present sim metrics as clinical sensitivity/specificity.  
- **No inflated profile counts.** Live set is **21**, not thousands.  
- **Degenerate biology stays honest** (e.g. diabetes T1/T2 = ketosis group — not faked apart).  
- **Never erase the past** — corrections are archived (`ARCHIVE_POLICY.md`).  
- **No stubs** as finished work.  
- Channel names are **response-band proxies**, not GC-MS IDs.

Allowed public numbers: see `CLAIM_LOCK.md`.

---

## Notice package (for labs & partners)

Lab-facing pack — open in ~15 minutes:

```bash
# From repo root
chmod +x NOTICE_PACKAGE/reproduce.sh
./NOTICE_PACKAGE/reproduce.sh
```

| File | Contents |
|------|----------|
| [`NOTICE_PACKAGE/README.md`](./NOTICE_PACKAGE/README.md) | Pack index |
| [`NOTICE_PACKAGE/01_METHODS.md`](./NOTICE_PACKAGE/01_METHODS.md) | Classifier method + limits |
| [`NOTICE_PACKAGE/02_HARDWARE_STATION.md`](./NOTICE_PACKAGE/02_HARDWARE_STATION.md) | BOM, wiring, QC |
| [`NOTICE_PACKAGE/03_THE_ASK.md`](./NOTICE_PACKAGE/03_THE_ASK.md) | What we want from partners |
| [`NOTICE_PACKAGE/docs/`](./NOTICE_PACKAGE/docs/) | Scorecard, engine truth, intended use, validation snapshot |

Zip mirror: `archives/OpenSmell_NOTICE_PACKAGE_20260719.zip`

---

## Live profiles (21)

Categories: cancer · neurological · metabolic · infectious · psychiatric.

Full signatures and **simulation** per-profile recall: [`SCORECARD.md`](./SCORECARD.md).  
Research-only (not live): melanoma, multiple sclerosis, lupus, autism (preliminary), schizophrenia (preliminary).

Examples of live keys: `lung_cancer`, `alzheimers`, `ketoacidosis`, `sepsis`, `rage_cortisol`, `pre_seizure`, … (complete list in `opensmell_engine_truth.json`).

---

## How it works

```
[Human body] → VOC emissions
      ↓
[MQ-135-class sensor] → analog proxy (or software bio-sim)
      ↓
[MCU serial / host] → channel intensities 0..1
      ↓
[open_smell2.classify] → coverage × intensity × specificity
      ↓
[Alert threshold default 0.7] → optional Family routing (care-support)
      ↓
[CSV audit log] → client-owned trail
```

Cognitive cortex diagram (generated from live engine stats):

```bash
python3 generate_cortex_diagram.py   # → opensmell_cognitive_cortex.html
```

---

## Quick start

### Simulation (no hardware)

```bash
pip install colorama
python3 opensmell_test_loop.py
# or full notice reproduce:
./NOTICE_PACKAGE/reproduce.sh
```

### Hardware (optional)

| Component | Approx. |
|-----------|---------|
| Arduino Nano / Uno class | ~$8–12 |
| MQ-135 module | ~$3–5 |
| Jumpers / USB | ~$4 |
| **Typical total** | **~$15–25** |

```
MQ VCC  → 5V
MQ GND  → GND
MQ AOUT → A0
```

```bash
pip install pyserial colorama
# Upload station firmware when available; see NOTICE_PACKAGE/02_HARDWARE_STATION.md
```

---

## Architecture notes

- **Classifier:** specificity-aware confidence in `open_smell2.py` (documented in notice methods).  
- **Resonance-Q™:** proprietary framing for efficient local processing on ordinary hardware — not a claim of clinical clearance.  
- **Security direction:** post-quantum options via project crypto libraries where integrated; institutional hardening is ongoing.  
- **Regulatory:** drafts under `regulatory/`. **Not FDA-approved. Not a clinical diagnostic.**

---

## Core docs

| Doc | Role |
|-----|------|
| [`CLAIM_LOCK.md`](./CLAIM_LOCK.md) | Allowed / forbidden claims |
| [`SCORECARD.md`](./SCORECARD.md) | Per-profile **sim** scorecard |
| [`INTENDED_USE.md`](./INTENDED_USE.md) | Intended use + prohibited claims |
| [`VALIDATION.md`](./VALIDATION.md) | Flagship sim methodology |
| [`BIOMARKER_SPECIFICITY.md`](./BIOMARKER_SPECIFICITY.md) | Marker discrimination history |
| [`NOTICE_PACKAGE/`](./NOTICE_PACKAGE/) | Lab-facing pack |
| [`LICENSE_CLARITY.md`](./LICENSE_CLARITY.md) | License instrument decision still open |
| [`ARCHIVE_POLICY.md`](./ARCHIVE_POLICY.md) | Never erase the past |
| [`regulatory/`](./regulatory/) | Q-Sub / risk / labeling **drafts** |
| [`SENSOR_TRUTH.md`](./SENSOR_TRUTH.md) | MQ-135 research: physics, proxy map, L1–L3 experiments |

---

## Dignity Clause

Built for populations medicine often fails — nonverbal people, dementia care, veterans, neurodivergent people, cancer families.

**Biological data is never sold, harvested, or commodified.**  
Clients own their data. Always.

---

## License

**On disk today:** root [`LICENSE`](./LICENSE) is **Apache License 2.0** text.  
README previously referenced a Sovereign Architecture License — **those two statements conflict**.  

Until counsel locks one instrument, see [`LICENSE_CLARITY.md`](./LICENSE_CLARITY.md).  
**Dignity, client ownership, and no biometric harvest remain non-negotiable** regardless of open-source terms.  
Commercial institutional deployment still requires a signed agreement when that path is chosen.

---

## Carbon–Silicon Symbiosis (CSS)

Every Christman system answers to CSS: symbiosis before scale, truth over optics, role integrity, sacred information, departure over corruption. Full axioms are project law — not marketing copy.

> *Any system that sacrifices humanity, dignity, memory, or trust for performance, optics, or control is not CSS — regardless of capability.*  
> — Everett N. Christman

---

## Author

**Everett Nathaniel Christman**  
Founder — The Christman AI Project  
Operating under Luma Cognify AI  

*"How can we help you love yourself more?"*

---

© 2025–2026 The Christman AI Project. All Rights Reserved.  
Resonance-Q™ is a trademark of Everett Nathaniel Christman.
