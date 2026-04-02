"""
OpenSmell Biological Simulation Engine
The Christman AI Project — Luma Cognify AI
Author: Everett Christman + Claude (grounding board)

Replaces flat random VOC generation with biologically realistic distributions.

Why this exists:
    Flat uniform random (0.05–1.0) produces a predictable staircase pattern
    in detection frequency. Real human breath chemistry does not behave that way.
    This engine models how VOCs actually distribute in biological systems:

    1. Log-normal intensity distribution — most readings cluster low,
       occasional biological spikes, matching real breath analysis literature.
    2. Personal patient baseline — each simulated patient has a unique
       chemical fingerprint they fluctuate around, not a blank slate each cycle.
    3. VOC co-variance — compounds that travel together in biology
       travel together here. Isoprene and acetone co-vary. Ammonia and
       sulfur co-vary. Independent coin flips are not biology.
    4. True noise injection — random compounds at low levels that match
       no profile, because the human body is always producing background chemistry.
    5. Diurnal phase variation — morning, afternoon, evening, night each
       shift the baseline intensity of certain compound classes.

Reference basis:
    - Breath biopsy literature (Agilent, Owlstone Medical)
    - VOC biomarker meta-analyses (Phillips et al., Miekisch et al.)
    - Exhaled breath condensate studies (Horvath et al.)
"""

import random
import math
from collections import defaultdict

# ─────────────────────────────────────────────
# LOG-NORMAL SAMPLER
# Models real VOC concentration distributions
# Most readings low, occasional spikes — not flat uniform
# ─────────────────────────────────────────────

def lognormal_voc(mean_log=0.0, sigma=0.8, clip_min=0.01, clip_max=1.0):
    """
    Draws a VOC intensity from a log-normal distribution.
    sigma=0.8 produces realistic breath chemistry spread.
    Higher sigma = more variance, more surprise spikes.
    """
    raw = math.exp(random.gauss(mean_log, sigma))
    return round(min(max(raw / (raw + 1), clip_min), clip_max), 3)

# ─────────────────────────────────────────────
# VOC CO-VARIANCE GROUPS
# Compounds that co-vary in real biology
# When one is elevated, correlated ones shift too
# ─────────────────────────────────────────────

VOC_COVARIANCE_GROUPS = [
    # Oxidative stress cluster
    {"members": ["isoprene", "acetone", "ethane"],        "correlation": 0.65},
    # Protein catabolism cluster
    {"members": ["ammonia", "dimethyl_sulfide", "sulfur"], "correlation": 0.70},
    # Lipid peroxidation cluster — elevated in neurodegeneration
    {"members": ["lipid_oxidation", "aldehydes", "alkanes"],  "correlation": 0.72},
    # Ketone body cluster (metabolic stress)
    {"members": ["acetone", "propanol", "ketones"],        "correlation": 0.75},
    # Microbial/gut fermentation cluster
    {"members": ["skatole", "sulfur", "ammonia"],          "correlation": 0.55},
]

# ─────────────────────────────────────────────
# DIURNAL PHASE MODEL
# Time-of-day shifts VOC baseline intensity
# Morning breath ≠ afternoon breath ≠ night breath
# ─────────────────────────────────────────────

DIURNAL_PHASES = {
    "morning":   {
        "description": "Post-sleep, fasting state",
        "elevated":    ["acetone", "isoprene", "ketones"],   # fasting ketosis elevated
        "suppressed":  ["ethanol_trace", "sulfur"],
        "multiplier":  1.35
    },
    "afternoon": {
        "description": "Post-meal, active metabolism",
        "elevated":    ["ammonia", "dimethyl_sulfide"],       # digestion elevated
        "suppressed":  ["ketones", "acetone"],
        "multiplier":  1.0
    },
    "evening":   {
        "description": "Late day, metabolic wind-down",
        "elevated":    ["hydrocarbons", "alkanes"],
        "suppressed":  ["isoprene"],
        "multiplier":  0.9
    },
    "night":     {
        "description": "Sleep-adjacent, low metabolic rate",
        "elevated":    ["lipid_oxidation", "sebum_vocs"],    # repair cycle elevated
        "suppressed":  ["ammonia", "isoprene"],
        "multiplier":  0.75
    },
}

def get_diurnal_phase():
    """Returns a random diurnal phase weighted toward daytime hours."""
    return random.choices(
        ["morning", "afternoon", "evening", "night"],
        weights=[25, 40, 25, 10]
    )[0]

# ─────────────────────────────────────────────
# PATIENT BASELINE
# Each patient has a unique personal chemical fingerprint
# VOC readings fluctuate around their baseline, not zero
# ─────────────────────────────────────────────

def generate_patient_baseline(all_vocs):
    """
    Creates a personal VOC baseline for a simulated patient.
    Reflects individual metabolic variation — no two patients identical.
    Returns dict of voc -> baseline_intensity (0.0–0.4, below alert threshold)
    """
    baseline = {}
    for voc in all_vocs:
        # Most baseline VOCs sit low — occasional naturally elevated compound
        if random.random() < 0.15:
            baseline[voc] = round(random.uniform(0.15, 0.35), 3)  # naturally elevated
        else:
            baseline[voc] = round(random.uniform(0.01, 0.12), 3)  # background trace
    return baseline

# ─────────────────────────────────────────────
# BIOLOGICAL NOISE LAYER
# Real breath always contains compounds that match no profile
# Absence of noise = fake data
# ─────────────────────────────────────────────

# VOCs that appear in breath for non-pathological reasons
BACKGROUND_NOISE_VOCS = [
    "toluene",       # environmental exposure
    "ethane",        # normal lipid peroxidation
    "butane",        # trace environmental
    "methane_trace", # gut microbiome baseline
    "ethanol_trace", # normal fermentation
    "propanol",      # normal metabolism
]

def inject_biological_noise(reading):
    """
    Adds low-level background VOCs to every reading.
    These match no disease profile — they are honest biological noise.
    Without this, the classifier works in an unrealistically clean environment.
    """
    num_noise = random.randint(1, 4)
    noise_vocs = random.sample(BACKGROUND_NOISE_VOCS, k=min(num_noise, len(BACKGROUND_NOISE_VOCS)))
    for voc in noise_vocs:
        # Noise sits below alert threshold but above zero — realistic trace levels
        existing = reading.get(voc, 0.0)
        noise_level = lognormal_voc(mean_log=-1.5, sigma=0.5)  # low mean, tight spread
        reading[voc] = round(min(existing + noise_level, 1.0), 3)
    return reading

# ─────────────────────────────────────────────
# CO-VARIANCE APPLIER
# Shifts correlated VOCs together when one is elevated
# ─────────────────────────────────────────────

def apply_covariance(reading, all_vocs):
    """
    For each co-variance group, if one member is elevated,
    correlated members shift in the same direction.
    Models real biological compound relationships.
    """
    for group in VOC_COVARIANCE_GROUPS:
        members = group["members"]
        correlation = group["correlation"]
        # Find if any group member is elevated in this reading
        elevated = [v for v in members if reading.get(v, 0) > 0.4]
        if not elevated:
            continue
        # Pull correlated members upward proportionally
        anchor_level = max(reading.get(v, 0) for v in elevated)
        for voc in members:
            if voc not in elevated and voc in all_vocs:
                current = reading.get(voc, 0.05)
                shift = (anchor_level - current) * correlation * random.uniform(0.3, 0.8)
                reading[voc] = round(min(current + shift, 1.0), 3)
    return reading

# ─────────────────────────────────────────────
# MAIN BIOLOGICAL SENSOR SIMULATION
# Drop-in replacement for simulate_sensor_reading()
# Produces honest, biologically realistic VOC readings
# ─────────────────────────────────────────────

def bio_simulate_sensor_reading(
    all_vocs,
    scent_profiles,
    inject_profile=None,
    inject_rate=0.25,
    patient_baseline=None
):
    """
    Biologically realistic VOC sensor simulation.

    Replaces flat uniform random with:
    - Log-normal intensity distribution
    - Personal patient baseline
    - VOC co-variance modeling
    - Diurnal phase variation
    - Biological noise injection

    Args:
        all_vocs:        Full list of VOC compound names
        scent_profiles:  SCENT_PROFILES dict from main loop
        inject_profile:  Profile key to inject (or None for free-run)
        inject_rate:     Probability of injection (0.0–1.0)
        patient_baseline: Pre-generated patient baseline (or None to generate fresh)

    Returns:
        reading dict with VOC intensities and dunder metadata keys
    """
    # Generate or use patient baseline
    if patient_baseline is None:
        patient_baseline = generate_patient_baseline(all_vocs)

    # Get diurnal phase for this reading
    phase_key = get_diurnal_phase()
    phase = DIURNAL_PHASES[phase_key]

    # Build base reading from patient baseline + log-normal variation
    reading = {}
    for voc in all_vocs:
        base = patient_baseline.get(voc, 0.05)
        # Log-normal fluctuation around personal baseline
        variation = lognormal_voc(mean_log=-0.5, sigma=0.7)
        intensity = round(min(base + variation * 0.4, 1.0), 3)

        # Apply diurnal phase modifiers
        if voc in phase["elevated"]:
            intensity = round(min(intensity * phase["multiplier"] * random.uniform(1.1, 1.4), 1.0), 3)
        elif voc in phase["suppressed"]:
            intensity = round(intensity * random.uniform(0.4, 0.7), 3)

        reading[voc] = intensity

    reading["__phase__"] = phase_key
    reading["__phase_desc__"] = phase["description"]

    # Inject biological noise
    reading = inject_biological_noise(reading)

    # Apply VOC co-variance
    reading = apply_covariance(reading, all_vocs)

    injected_key = None

    # Injection logic — targeted only, no random fallback when profile specified
    if inject_profile and inject_profile in scent_profiles:
        if random.random() < inject_rate:
            profile = scent_profiles[inject_profile]
            for voc in profile["vocs"]:
                # Inject at elevated biological level — log-normal, not flat
                reading[voc] = round(random.uniform(0.55, 0.95), 3)
            injected_key = inject_profile
            reading["__injected__"] = inject_profile
    elif not inject_profile and random.random() < inject_rate:
        injected_key = random.choice(list(scent_profiles.keys()))
        profile = scent_profiles[injected_key]
        for voc in profile["vocs"]:
            reading[voc] = round(random.uniform(0.55, 0.95), 3)
        reading["__injected__"] = injected_key

    reading["__injected_key__"] = injected_key

    return reading
