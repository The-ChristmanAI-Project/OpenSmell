# OpenSmell — Methods Brief

**Audience:** scientists, labs, IRBs, technical partners  
**Engine:** `open_smell2.py` (single classification path for sim and production classify)  
**Not clinical validation.** All performance figures cited here are **closed-loop simulation** unless a future human-sample study is explicitly attached.

---

## 1. System overview

```
VOC reading (dict of channel → intensity 0..1)
        ↓
detect channels ≥ 0.3
        ↓
for each live profile signature:
  coverage · mean_intensity · specificity → confidence
        ↓
matches with confidence ≥ 0.2, sorted descending
        ↓
alert if top confidence ≥ profile threshold (default 0.7)
        ↓
optional alert router → Christman AI Family (care-support context)
        ↓
CSV audit log every cycle
```

**Live inventory:** 21 sensor-grounded profiles · 5 research_only excluded from live matching · 20 named sensor channels.

---

## 2. Sensor channels (proxies)

Channels are labels for **cross-sensitive response bands** on an MQ-135-class stack (or the bio-simulator that models them). They are **not** certified chemical IDs.

Examples of channel names used in signatures:  
`acetone`, `isoprene`, `ammonia`, `benzene`, `alkanes`, `aldehydes`, `hydrocarbons`, `dimethyl_sulfide`, `sulfur`, `aliphatic_acids`, `skatole`, `ketones`, `sebum_vocs`, `lipid_oxidation`, `propanol`, `toluene`, and others listed in `opensmell_engine_truth.json`.

Literature markers (e.g. `acetone_breath`) are mapped through `MARKER_ALIASES` in `open_smell2.py` before matching.

---

## 3. Confidence formula (production)

For each live profile with required channel set *S*:

```
detected     = { channel : intensity | intensity ≥ 0.3 }
matched      = channels in S that appear in detected
coverage     = |matched| / |S|
mean_intensity = average intensity over matched
specificity  = sqrt(|matched|) / sqrt(max signature length among live profiles)
confidence   = min(1.0, coverage × mean_intensity × specificity)
```

**Why specificity exists:** Without it, one-channel profiles (e.g. tuberculosis = `{alkanes}`) win on full coverage and steal multi-channel conditions (e.g. lung cancer). Specificity rewards signatures that explain more of the signal. On labeled synthetic data this recovered separability after a profile expansion (see `BIOMARKER_SPECIFICITY.md` in repo root). Those recoveries are **sim self-consistency**, not clinical accuracy.

**Defaults:**

| Parameter | Default |
|-----------|---------|
| Detect threshold | 0.3 |
| Minimum confidence to list a match | 0.2 |
| Default alert threshold | 0.7 |
| Top-N returned | 3 (classify) / 1 (classify_top) |

---

## 4. Degenerate groups (honest inseparability)

Some conditions share the same effective signature on this sensor class. Fabricating a separator would create false confidence in the field.

| Group | Members | Honest claim |
|-------|---------|--------------|
| `diabetes_ketosis` | `diabetes_type1`, `diabetes_type2` | Detects ketosis-class acetone signal — **not** T1 vs T2 |

Scoring for group-aware accuracy uses `same_group()` in `open_smell2.py`.

---

## 5. Simulation methodology (validation)

`opensmell_bio_sim.py` + `opensmell_test_loop.py`:

- Log-normal intensities, personal baselines, VOC co-variance, diurnal phase, background noise  
- Optional **targeted injection** of a profile’s channels for controlled recall  
- **Single engine:** test loop imports `classify` from `open_smell2` — no parallel toy classifier  

**Flagship endurance (reported in VALIDATION.md):**

- 11,843 cycles · unseeded · full noise · ~6h 35m  
- Detection rate 92.38%  
- Injection accuracy **77.81%** (when injection events occurred)  

**Labeled experiment:** per-profile group/exact recall in `docs/SCORECARD.md` (snapshot). Rebuild with `python3 run_labeled_experiment.py` from repo root (long run).

---

## 6. Alert routing

`alert.py` routes high-confidence matches to Family members (e.g. Sierra, Derek) for **care-support workflows**. Routing is not a medical order and does not constitute diagnosis or treatment.

Integration tests enforce: messy low-confidence cycles do not route; threshold-clearing cycles do.

---

## 7. Limitations (required reading)

1. **No multi-site human breath/skin clinical performance study is claimed in this pack.**  
2. MQ-135-class hardware does not resolve named VOCs like a GC-MS.  
3. Shared channels cause competition between related profiles (see SCORECARD confusions).  
4. Single-channel profiles (e.g. Alzheimer’s lipid_oxidation, TB alkanes) are weaker and documented as such.  
5. Environmental interferents, humidity, sensor aging, and fan/draw geometry are not fully characterized in-field in this pack.  
6. Screening-support only. Human review required for any care action.

---

## 8. What “success” means for a partner lab

Success is **not** matching our sim accuracy on day one. Success is:

- Running the reproduce script successfully  
- Understanding proxy channels and degenerate groups  
- Optionally comparing **known mixtures** or protocol samples to our channel map  
- Co-designing a non-diagnostic research protocol if the science warrants it  

---

## 9. References in-repo

| Document | Role |
|----------|------|
| `docs/VALIDATION.md` | Flagship run + reproducibility checklist |
| `docs/SCORECARD.md` | Per-profile sim recall |
| `docs/CLAIM_LOCK.md` | Public claim rules |
| `../BIOMARKER_SPECIFICITY.md` | Marker discrimination history (repo root) |
| `../open_smell2.py` | Source of truth for classify |

---

© 2025–2026 The Christman AI Project. All Rights Reserved.
