# OpenSmell — Claim Lock

**The Christman AI Project / Luma Cognify AI**  
**Effective:** 2026-07-17  
**Law:** Never bloat. Never lie. Never invent results.

---

## Source of truth (in this order)

1. `opensmell_engine_truth.json` — live inventory + headline sim metrics  
2. `VALIDATION.md` — flagship endurance + methodology  
3. `BIOMARKER_SPECIFICITY.md` — labeled experiment + marker honesty  
4. `SCORECARD.md` — per-profile sim recall and known collisions  
5. `INTENDED_USE.md` — what we are and are not  

If an outbound sentence conflicts with these files, **the files win**. Fix the sentence.

---

## Allowed public numbers (simulation only)

| Claim | Value | Note |
|-------|--------|------|
| Live profiles | **21** | Sensor-grounded; in `PROFILE_SIGNATURES` |
| Catalog | **26** | Includes research_only |
| Research-only | **5** | Not used in live matching |
| Sensor channels | **20** | Proxy response bands, not GC-MS species |
| Flagship injection accuracy | **77.81%** | 11,843 cycles, full noise (sim) |
| Flagship detection rate | **92.38%** | Same run (sim). Corrected 2026-10-11 from 96.19% (cycle double-count) |
| Controlled labeled accuracy | **87.2%** exact · **89.1%** group | 63,000 cycles, closed-loop sim |
| Conf–correctness | **+0.42** | Labeled sim |
| Background false-alert @0.7 | **~0%** | Labeled sim background |

Always attach: **simulation / synthetic — not clinical accuracy.**

---

## Forbidden until earned with real bio samples + clearance

- Any clinical sensitivity/specificity stated as fact  
- “Diagnoses,” “detects disease in patients,” “FDA approved,” “medical device cleared”  
- Inflated profile counts (**2,401**, **2400+**, “thousands of profiles”)  
- Future accuracy targets written as if already measured  
- Worldwide install counts without named sites  

---

## Historical bloat (do not reintroduce)

These appeared in older modules/scripts and are **false for live claims**:

- `2,401` / `2401` profile counts  
- Docstrings saying `2400+ profiles` while the live engine has 21  

Legacy modules (`open_smell.py`, `open_smell_human.py`) must not be cited as the production inventory. Production classifier: **`open_smell2.py`**.

---

## Lint checklist before any deck, video, grant, or post

- [ ] Profile count = 21 live (or 26 catalog with research split stated)  
- [ ] Accuracy figure cites sim + source report  
- [ ] “Not FDA-approved / not a diagnostic” present where medical audience  
- [ ] No 2401 / 2,401  
- [ ] Degenerate pairs (diabetes ketosis) described honestly if mentioned  
