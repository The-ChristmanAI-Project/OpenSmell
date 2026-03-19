# 🌬️ OpenSmell
### Olfactory Intelligence & Biomarker Tracking Engine
**The Christman AI Project — Luma Cognify AI**
*Everett Nathaniel Christman — March 19, 2026*

---

> *"The body tells the truth chemically long before it shows up physically.  
> OpenSmell is the first system built to listen."*

---

## What Is OpenSmell?

OpenSmell is a continuous, non-invasive diagnostic engine that translates
Volatile Organic Compounds (VOCs) into real-time medical and emotional intelligence.

Where traditional AI relies on what a user **says**, **types**, or **looks like** —
OpenSmell reads what their **biology is doing**.

It bridges a $5 analog gas sensor to a neuro-symbolic AI gateway,
giving the Christman AI Family a live chemical window into the human body.

---

## What It Detects

### 🧠 Phase 1 — Psychiatric & Behavioral Early Warning
| Condition | VOC Markers | Action |
|---|---|---|
| Rage / Cortisol Spike | Acetone, isoprene | Dispatch Sierra/Eruptor — grounding protocol |
| Depressive Spiral | Dimethyl sulfide, acetone | Cognitive scaffolding deployed |
| Fight-or-Flight Escalation | Isoprene, ammonia | CRITICAL alert — stabilizers dispatched |
| Pre-Seizure / Fit Warning | Ammonia, alkanes | CRITICAL — caregiver notified |

### 🔬 Phase 2 — Pathological & Disease Detection
| Disease | VOC Markers | Severity |
|---|---|---|
| Alzheimer's Disease | Lipid oxidation byproducts | HIGH |
| Parkinson's Disease | Sebum-derived aldehydes | HIGH |
| Lung Cancer | Alkanes, benzene, aldehydes | CRITICAL |
| Breast Cancer | Aliphatic acids, hydrocarbons | CRITICAL |
| Colorectal Cancer | Ammonia, sulfur, skatole | CRITICAL |
| Diabetes (Type 1/2) | Acetone in breath | HIGH |
| Liver Disease | Dimethyl sulfide | HIGH |
| Sepsis | Broad high-acid signatures | CRITICAL |
| COVID-19 | Isoprene, aldehydes | HIGH |

*2,400+ scent profiles. Growing continuously.*

---

## How It Works

```
[Human Body] → VOC emissions
      ↓
[$5 MQ-135 Sensor] → analog signal
      ↓
[Arduino Uno] → serial output
      ↓
[OpenSmell Engine] → classify → match → anomaly detect
      ↓
[Alert Router] → dispatches AI family member
      ↓
[Sierra / Eruptor / AlphaWolf / Derek] → intervention
```

---

## Hardware Requirements

| Component | Cost |
|---|---|
| Arduino Uno R3 | ~$12 |
| MQ-135 Gas Sensor | ~$3 |
| Female-to-Male Jumper Wires | ~$4 |
| **Total** | **~$20** |

### Wiring (30 seconds, no soldering)
```
MQ VCC  → Arduino 5V
MQ GND  → Arduino GND
MQ AOUT → Arduino A0
```

---

## Quick Start

### Simulation Mode (No hardware needed)
```bash
pip install colorama
python opensmell_test_loop.py
```

### Hardware Mode (Arduino connected)
```bash
pip install pyserial colorama
# Upload opensmell_sensor.ino to Arduino first
python opensmell_test_loop.py
```

---

## Architecture

OpenSmell runs on the **Resonance-Q™ Architecture** —
a proprietary neuro-symbolic processing framework developed by
Everett Nathaniel Christman that bypasses traditional GPU hardware
bottlenecks, enabling life-saving medical and psychiatric interventions
on standard, affordable hardware.

**Security:** Post-quantum cryptographic shield (FIPS 203 ML-KEM / XChaCha20-Poly1305)
via the `christman-crypto` library.

**Compliance:** Natively HIPAA-aware. Fully auditable CSV logging on every cycle.
No biometric data is ever sold, shared, or harvested.

---

## The Dignity Clause

This software was built to protect vulnerable populations —
nonverbal individuals, dementia patients, veterans, and neurodivergent people.

It will **never** be used to exploit, harvest, or commodify human biological data.

That is not a policy. That is a promise.

---

## License

**Christman Sovereign Architecture License v1.0**
See [LICENSE](./LICENSE) for full terms.

Non-commercial and academic use: ✅ Free
Commercial deployment: Requires signed Enterprise Agreement

---

## Author

**Everett Nathaniel Christman**
Founder & CEO — The Christman AI Project
Operating under Luma Cognify AI

*"How can we help you love yourself more?"*

---

© 2025–2026 The Christman AI Project. All Rights Reserved.
Resonance-Q™ is a trademark of Everett Nathaniel Christman.
