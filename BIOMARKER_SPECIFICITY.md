# OpenSmell — Biomarker Specificity & Classifier Validation

**The Christman AI Project / Luma Cognify AI** · synthetic-data R&D
Screening-support only. Not FDA-approved. Not a clinical device. Not deployed.
Every figure below is closed-loop simulation output, **not clinical accuracy.**

---

## What this round did

The prior round scaled the profile library from 16 to 26 conditions. Accuracy
on labeled synthetic data *dropped* from 79% to 43.8% — a real, expected result:
adding profiles that share VOC channels, without adding *discriminating* markers,
makes conditions collide. This round fixed that with literature-grounded
biomarkers and a specificity-aware confidence score.

> **Where this fits:** The **flagship run** is the July 5, 2026 endurance scan
> (11,843 cycles, unseeded, full noise; 92.38% detection, 77.81% injection accuracy) -
> see `VALIDATION.md`. The 87.2% below is the **controlled-conditions** benchmark
> from the labeled experiment. Both are real; the controlled number is higher
> because the test is cleaner. Neither is clinical accuracy.

## Headline (labeled synthetic data, 63,000 injected cycles)

| Stage | Top-1 accuracy |
|-------|----------------|
| 16-profile baseline | 79.3% |
| 26 profiles, no discriminating markers | 43.8% |
| **26 profiles + literature markers + specificity score** | **78.8%** |

Accuracy recovered to baseline **while covering 5 more live conditions**.
Confidence–correctness correlation flipped from **negative** (most-confident =
least-accurate) to **+0.39**. Background false-alert rate at the 0.7 alert
threshold dropped from ~24% to **~0%**.

These are self-consistency numbers on a closed-loop simulator (the same
signatures drive injection and scoring). They measure classifier separability,
**not clinical sensitivity/specificity.**

## The three degenerate pairs

Before this round, three profile pairs resolved to a single identical sensor
channel — physically indistinguishable, one twin always at 0% recall:

| Pair | Was | Fix | Grounding |
|------|-----|-----|-----------|
| Bladder cancer vs. Renal failure | both `{ammonia}` | bladder → `{alkanes, benzene}`, renal stays `{ammonia}` | Urinary VOC panels: bladder cancer elevates alkanes + aromatics, distinct from uremic ammonia (Metabolites 2021; Sci Rep 2025) |
| C. difficile vs. Sepsis | both `{aliphatic_acids}` | c_diff adds `{propanol, skatole}` | C. diff carries 1-propanol + indole/4-methylphenol (PLoS ONE 2019; J Breath Res 2024) |
| Diabetes T1 vs. T2 | both `{acetone}` | **not faked** — grouped as one class | No VOC species separates T1 from T2; both are acetone ketosis. Only a quantitative acetone shift exists in small studies. |

**Diabetes T1/T2 was deliberately NOT given a fabricated discriminator.**
Inventing a marker to lift the accuracy number would make the device
confidently wrong in the field. Instead it is declared inseparable
(`DEGENERATE_GROUPS`) and scored at the group level: the honest claim is
"detects diabetic ketosis," not "tells T1 from T2."

## The specificity-aware confidence score

Old: `confidence = coverage × mean_intensity`. A 1-channel profile
(tuberculosis = `{alkanes}`) always tied at coverage 1.0 and won on raw
intensity — stealing detections from multi-channel conditions and firing on
single-channel noise.

New: `confidence = min(1, coverage × mean_intensity × √matched / √max_sig_len)`.
The √matched term rewards profiles that explain *more* of the signal, so lung
cancer (`{alkanes, benzene, aldehydes}`) beats TB when all three fire, and lone
high channels no longer clear the alert bar.

## Round 2 — renal + sepsis discriminating markers

The two weakest live profiles after round 1 were **renal failure** (36.9% recall)
and **sepsis** (52.5% recall), mostly stolen by ammonia-only or acid-only
supersets. Round 2 adds literature-grounded multi-channel signatures:

| Profile | Was | Now | Grounding |
|---------|-----|-----|-----------|
| Renal failure | `{ammonia}` | `{ammonia, dimethyl_sulfide, toluene}` | Uremic ammonia + TMA (fishy) + phenolic aromatics on dialysis (Owlston kidney review; PLoS ONE 2012; phenol hemodialysis marker studies) |
| Sepsis | `{aliphatic_acids}` | `{aliphatic_acids, ammonia, dimethyl_sulfide}` | Systemic sepsis acidemia + hyperammonemia + sulfur metabolites — distinct from C. diff `{acids, propanol, skatole}` (Frontiers Cell Infect Microbiol 2020; sepsis e-nose ED studies) |

**Bio-sim labeled experiment (63,000 cycles, same closed-loop methodology):**

| Stage | Top-1 accuracy |
|-------|----------------|
| Round 1 (markers + specificity score) | 78.8% |
| **Round 2 (+ renal + sepsis markers)** | **87.2%** exact · 89.1% group (from committed `opensmell2_labeled_experiment.csv`; an earlier write-up said 88.7%, which the committed data does not reproduce) |

Renal recall: **36.9% → 100%**. Sepsis recall: **52.5% → 99.2%**.
Confidence–correctness correlation: **+0.42**. Background false-alert @0.7: **0%**.

## Honest limitations

- Synthetic self-consistency numbers, not clinical accuracy. Real breath-VOC
  screening tops out ~85–94% sensitivity/specificity on actual samples.
- **Alzheimer's** remains a single-channel profile (`lipid_oxidation`) and still
  confuses with ketoacidosis/rage on ~12% of bio-sim cycles — needs its own
  second marker when literature supports a distinct channel on this sensor class.
- The MQ-135 sensor stack does not literally resolve "benzene" vs "indole" as
  named species; channel names are proxies for cross-sensitive response bands.
  Real-sample validation is required before any of this maps to biology.

## Tests

34 unit tests pass (`python3 -m unittest test_alert_integration test_open_smell2`), including:
alert-router integration guards (0.38 messy cycle → no route; ≥0.7 → SIERRA/DEREK), plus
bladder/renal separation, C.diff/sepsis separation, renal/sepsis round-2 markers,
diabetes grouping (not faked), specificity ranking, confidence bounding, and
single-channel background rejection.

## Cognitive Cortex diagram (code-aligned)

Open `opensmell_cognitive_cortex.html` in a browser — generated from live engine
stats via `python3 generate_cortex_diagram.py`. Replaces inflated "2,401 profiles"
marketing with **21 live / 26 catalog / 20 channels** and the real classifier pipeline.
