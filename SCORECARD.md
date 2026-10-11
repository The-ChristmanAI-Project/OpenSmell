# OpenSmell — Per-Profile Simulation Scorecard

**The Christman AI Project / Luma Cognify AI**  
**Generated from:** `opensmell2_labeled_experiment.csv` + `opensmell2_per_profile_recall.csv`  
**Classifier:** `open_smell2.py` · **21 live profiles**  
**Status:** Closed-loop **synthetic** labeled experiment — **not clinical accuracy**

---

## How to read this

| Column | Meaning |
|--------|---------|
| **Group recall** | Fraction of injected cycles where top match is the true profile **or** same degenerate group (`same_group`) |
| **Exact recall** | Top match key equals true key exactly |
| **Top confusions** | When exact match fails, where the classifier went (share of that profile’s cycles) |
| **n ch** | Number of sensor channels in the live signature |

**Honesty notes:**

- Channel names are **sensor proxy bands**, not GC-MS species IDs.  
- Diabetes T1/T2 share acetone and are a **degenerate group** (`diabetes_ketosis`). Exact T2→T1 swaps are group-correct; acetone stealing by ketoacidosis is a real limit.  
- High sim recall ≠ clinical performance.  

**Headline labeled run (historical write-up):** see `BIOMARKER_SPECIFICITY.md` (87.2% exact top-1 · 89.1% group, recomputed from the committed CSV).  
**Flagship endurance (full noise):** 77.81% injection accuracy · 11,843 cycles (originally reported as 23,686; see correction in `VALIDATION.md`) — `VALIDATION.md`.

---

## Scorecard (all 21 live)

Sorted weakest → strongest by **group recall** (from `opensmell2_per_profile_recall.csv`).

| Profile key | Condition | Cat | n ch | Channels | Group recall | Exact recall | Top confusions (exact miss) | Limit / note |
|-------------|-----------|-----|------|----------|--------------|--------------|-----------------------------|--------------|
| `diabetes_type1` | Diabetes (Type 1) | metabolic | 1 | acetone | **0.373** | 37.3% | ketoacidosis 44%, rage_cortisol 15% | Degenerate with T2; acetone shared with keto/rage |
| `diabetes_type2` | Diabetes (Type 2) | metabolic | 1 | acetone | **0.384** | **0.0%** | ketoacidosis 45%, diabetes_type1 38%, rage_cortisol 13% | Exact often loses to T1; group = ketosis claim only |
| `liver_disease` | Liver Disease | metabolic | 1 | dimethyl_sulfide | **0.457** | 45.7% | depressive_spiral 50%, renal_failure 4% | Single-channel DMS; steals with depressive |
| `tuberculosis` | Tuberculosis | infectious | 1 | alkanes | **0.793** | 79.3% | ketoacidosis 8%, pre_seizure 5% | Single-channel alkanes; competes with multi-alkane profiles |
| `alzheimers` | Alzheimer's Disease | neurological | 1 | lipid_oxidation | **0.883** | 88.3% | ketoacidosis 7%, rage_cortisol 4% | Single-channel; needs second marker if literature+sensor allow |
| `bladder_cancer` | Bladder Cancer | cancer | 2 | alkanes, benzene | **0.915** | 91.5% | lung_cancer 8% | Overlap with lung alkane/aromatic set |
| `covid19` | COVID-19 | infectious | 2 | isoprene, aldehydes | **0.977** | 97.7% | rage_cortisol 2% | Sim-strong; clinical = unproven |
| `fight_or_flight` | Fight-or-Flight Escalation | psychiatric | 2 | isoprene, ammonia | **0.977** | 97.7% | rage_cortisol 2% | Behavioral screening-support only |
| `sepsis` | Sepsis | infectious | 3 | aliphatic_acids, ammonia, dimethyl_sulfide | **0.984** | 98.4% | renal_failure 2% | Round-2 markers; sim only |
| `depressive_spiral` | Depressive Spiral | psychiatric | 2 | dimethyl_sulfide, acetone | **0.987** | 98.7% | ketoacidosis 1% | Not a psychiatric diagnosis |
| `rage_cortisol` | Rage / Cortisol Spike | psychiatric | 2 | acetone, isoprene | **0.992** | 99.2% | ketoacidosis 1% | Proxy stress signature |
| `pre_seizure` | Pre-Seizure / Fit Warning | psychiatric | 2 | ammonia, alkanes | **0.995** | 99.5% | — | Screening-support only |
| `ovarian_cancer` | Ovarian Cancer | cancer | 2 | aldehydes, hydrocarbons | **0.996** | 99.6% | — | Sim only; oncology needs GC-MS anchors later |
| `prostate_cancer` | Prostate Cancer | cancer | 2 | aldehydes, ketones | **0.996** | 99.6% | — | Same |
| `breast_cancer` | Breast Cancer | cancer | 2 | aliphatic_acids, hydrocarbons | **0.996** | 99.6% | — | Same |
| `parkinsons` | Parkinson's Disease | neurological | 2 | sebum_vocs, aldehydes | **0.997** | 99.7% | — | Sim only |
| `ketoacidosis` | Ketoacidosis | metabolic | 2 | acetone, propanol | **0.999** | 99.9% | — | Strong sim; clinical unproven |
| `colorectal_cancer` | Colorectal Cancer | cancer | 3 | ammonia, sulfur, skatole | **1.000** | 100% | — | Sim only |
| `c_diff` | C. difficile | infectious | 3 | aliphatic_acids, propanol, skatole | **1.000** | 100% | — | Separated from sepsis in sim |
| `lung_cancer` | Lung Cancer | cancer | 3 | alkanes, benzene, aldehydes | **1.000** | 100% | — | Sim only |
| `renal_failure` | Renal Failure | metabolic | 3 | ammonia, dimethyl_sulfide, toluene | **1.000** | 100% | — | Round-2 markers; sim only |

---

## Weakest five (priority for science, not for hiding)

1. **diabetes_type1 / diabetes_type2** — honest ketosis group; do not invent T1/T2 separators  
2. **liver_disease** — DMS single channel vs depressive_spiral  
3. **tuberculosis** — alkanes single channel  
4. **alzheimers** — lipid_oxidation single channel  
5. **bladder_cancer** — lung_cancer overlap  

---

## Degenerate groups

| Group | Members | Honest claim |
|-------|---------|--------------|
| `diabetes_ketosis` | `diabetes_type1`, `diabetes_type2` | Detects diabetic ketosis-class acetone signal — **not** T1 vs T2 |

---

## Reproduce

```bash
# Unit + integration (expect OK)
python3 -m unittest test_open_smell2 test_alert_integration

# Rebuild labeled CSV + per-profile recall (long run)
python3 run_labeled_experiment.py

# Seeded short inject
python3 opensmell_test_loop.py --cycles 100 --inject alzheimers --inject-rate 0.5 --speed turbo --seed 42
```

---

## Research-only (not on this scorecard)

Excluded from live matching: melanoma, multiple sclerosis, lupus, autism (preliminary), schizophrenia (preliminary).  
See `VALIDATION.md`.

---

*Simulation self-consistency only. Never present this table as clinical performance.*
