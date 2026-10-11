# OpenSmell — FDA Q-Submission Outline (Draft)

**Version:** 0.1 draft — 2026-07-17  
**Type:** Q-Sub (Informational / Study Risk / Pre-Submission style package outline)  
**Status:** Outline for counsel and consultant packaging. Not submitted.

---

## 1. Meeting / package goal

Obtain FDA feedback on:

1. Whether the described intended use is appropriate for the near-term product.  
2. Classification and pathway options for software ± low-cost gas sensor.  
3. Evidence expectations for a **first narrow indication** while maintaining a multi-profile research software surface.  
4. Acceptable labeling language for screening-support vs diagnostic claims.  
5. Human factors and alert-fatigue expectations for continuous monitoring contexts.

## 2. Device / software description (to attach)

- Architecture diagram from Cognitive Cortex generator (21 live profiles, honest counts).  
- `open_smell2` classification method summary (coverage, intensity, specificity-aware confidence).  
- Hardware BOM and wiring for optional sensor path.  
- Data flow and client data ownership.  
- Alert routing optional Family link (research/care-support).

## 3. Proposed intended use (starting text)

Use locked text from `../INTENDED_USE.md`. Do not expand in the Q-Sub cover beyond that file without version control.

## 4. Current evidence (honest)

| Evidence | Status |
|----------|--------|
| Closed-loop synthetic labeled experiment | Documented; not clinical |
| Flagship endurance sim | 11,843 cycles; 77.81% injection accuracy |
| Unit/integration tests | 34 tests as of claim-lock session |
| Human breath/skin clinical study | Not yet in this repository |
| Analytical validation vs known VOC mixtures | Protocol planned; results when measured |

## 5. Questions for FDA (draft list)

1. For software that matches multi-channel VOC **proxy** signals to condition **profiles** and presents confidence scores for human review, what classification pathway is appropriate if the labeled indication is screening-support for [narrow indication to be selected]?  
2. What clinical evidence (study design, endpoints, comparators) would be expected for that narrow indication?  
3. How should additional profiles present in software but **not** in the labeled clinical indication be described (research-only UI segregation)?  
4. Are metal-oxide sensor continuous ambient/breath-adjacent measurements acceptable for the proposed context with disclosed cross-sensitivity limitations?  
5. What cybersecurity documentation is expected for on-prem institutional deployment?  
6. Any feedback on multi-indication expansion planning after first authorization?

## 6. Materials checklist before filing

- [ ] Intended use frozen (versioned)  
- [ ] Risk file draft reviewed by clinical advisor  
- [ ] Scorecard and methods attached  
- [ ] Claim lock verified (`python3 scripts/claim_lint.py`)  
- [ ] Counsel review  
- [ ] Misty informed if commercial exclusivity is discussed in parallel  

## 7. What this outline is not

- Not a promise of clearance  
- Not permission to market as FDA approved  
- Not a clinical protocol (protocol is a separate document when IRB path starts)

## 8. Revision history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-07-17 | Initial full outline |

---

© 2025–2026 The Christman AI Project. All Rights Reserved.
