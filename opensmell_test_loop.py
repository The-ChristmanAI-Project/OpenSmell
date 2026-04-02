"""
OpenSmell Continuous Testing Loop
The Christman AI Project — Luma Cognify AI
Author: Everett Christman + Claude (grounding board)

SIMULATION MODE — No hardware required.
Simulates VOC sensor readings and runs the full pipeline:
  1. Read sensor (simulated)
  2. Classify VOC compound
  3. Detect anomaly → trigger AI alert
  4. Match against scent profile database (2400+ profiles)
  5. Log results continuously
  6. Generate publication-ready session report

MODES:
  Normal:      python opensmell_test_loop.py
  High-Speed:  python opensmell_test_loop.py --speed fast
  Benchmark:   python opensmell_test_loop.py --cycles 1000
  Seeded Run:  python opensmell_test_loop.py --cycles 500 --inject diabetes_t1t2 --inject-rate 0.4

To install:
    pip install pandas colorama
"""

import time
import random
import json
import csv
import os
import argparse
from datetime import datetime
from collections import defaultdict
from colorama import Fore, Style, init
from opensmell_bio_sim import bio_simulate_sensor_reading, generate_patient_baseline

init(autoreset=True)

# ─────────────────────────────────────────────
# SCENT PROFILE DATABASE (Condensed Core Set)
# Expand this dict toward 2400+ entries over time
# ─────────────────────────────────────────────
SCENT_PROFILES = {
    # ── Emotional / Behavioral ──────────────────
    "cortisol_spike":       {"category": "behavioral",   "condition": "Stress / Rage Onset",       "vocs": ["acetone", "isoprene"],            "alert": True,  "severity": "high"},
    "serotonin_drop":       {"category": "behavioral",   "condition": "Depressive Spiral",          "vocs": ["dimethyl_sulfide", "acetone"],    "alert": True,  "severity": "high"},
    "adrenaline_surge":     {"category": "behavioral",   "condition": "Fight-or-Flight Escalation", "vocs": ["isoprene", "ammonia"],            "alert": True,  "severity": "critical"},
    "neurological_prefit":  {"category": "behavioral",   "condition": "Pre-Seizure / Fit Warning",  "vocs": ["ammonia", "alkanes"],             "alert": True,  "severity": "critical"},
    "calm_baseline":        {"category": "behavioral",   "condition": "Calm / Stable",              "vocs": ["ethanol_trace"],                  "alert": False, "severity": "none"},

    # ── Cancer Signatures ───────────────────────
    "lung_cancer":          {"category": "oncology",     "condition": "Lung Cancer",                "vocs": ["alkanes", "benzene", "aldehydes"],        "alert": True,  "severity": "critical"},
    "breast_cancer":        {"category": "oncology",     "condition": "Breast Cancer",              "vocs": ["aliphatic_acids", "hydrocarbons"],        "alert": True,  "severity": "critical"},
    "colorectal_cancer":    {"category": "oncology",     "condition": "Colorectal Cancer",          "vocs": ["ammonia", "sulfur", "skatole"],           "alert": True,  "severity": "critical"},
    "ovarian_cancer":       {"category": "oncology",     "condition": "Ovarian Cancer",             "vocs": ["aldehydes", "hydrocarbons"],              "alert": True,  "severity": "critical"},
    "prostate_cancer":      {"category": "oncology",     "condition": "Prostate Cancer",            "vocs": ["aldehydes", "ketones"],                   "alert": True,  "severity": "critical"},

    # ── Neurological / Degenerative ─────────────
    "parkinsons":           {"category": "neurological", "condition": "Parkinson's Disease",        "vocs": ["sebum_vocs", "aldehydes"],                "alert": True,  "severity": "high"},
    "alzheimers":           {"category": "neurological", "condition": "Alzheimer's Disease",        "vocs": ["lipid_oxidation"],                        "alert": True,  "severity": "high"},

    # ── Metabolic / Infectious ──────────────────
    "diabetes_t1t2":        {"category": "metabolic",   "condition": "Diabetes (Type 1/2)",        "vocs": ["acetone", "propanol"],                    "alert": True,  "severity": "high"},
    "liver_disease":        {"category": "metabolic",   "condition": "Liver Disease",              "vocs": ["dimethyl_sulfide"],                       "alert": True,  "severity": "high"},
    "covid19":              {"category": "infectious",   "condition": "COVID-19",                   "vocs": ["isoprene", "aldehydes"],                  "alert": True,  "severity": "high"},
    "sepsis":               {"category": "infectious",   "condition": "Sepsis",                     "vocs": ["ammonia", "sulfur"],                      "alert": True,  "severity": "critical"},
}

# All known VOC compounds in the simulation pool
ALL_VOCS = [
    "acetone", "isoprene", "ammonia", "benzene", "alkanes",
    "aldehydes", "hydrocarbons", "dimethyl_sulfide", "sulfur",
    "aliphatic_acids", "skatole", "ketones", "sebum_vocs",
    "lipid_oxidation", "ethanol_trace", "toluene", "ethane",
    "propanol", "butane", "methane_trace"
]

SEVERITY_COLORS = {
    "critical": Fore.RED,
    "high":     Fore.YELLOW,
    "none":     Fore.GREEN,
}

# ─────────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="OpenSmell Continuous Testing Loop")
    parser.add_argument("--speed",       choices=["normal", "fast", "turbo"], default="normal",
                        help="Cycle speed: normal=2s, fast=0.5s, turbo=0.05s")
    parser.add_argument("--cycles",      type=int, default=0,
                        help="Number of cycles to run (0 = infinite)")
    parser.add_argument("--inject",      type=str, default=None,
                        help="Force-inject a specific profile key each cycle (e.g. diabetes_t1t2)")
    parser.add_argument("--inject-rate", type=float, default=0.25,
                        help="Probability of injection per cycle (0.0–1.0, default 0.25)")
    parser.add_argument("--seed",        type=int, default=None,
                        help="Random seed for reproducible runs (e.g. --seed 42)")
    return parser.parse_args()

SPEED_MAP = {"normal": 2.0, "fast": 0.5, "turbo": 0.05}

# ─────────────────────────────────────────────
# PATIENT DEMOGRAPHICS
# Profile-aware — prostate cancer = male only, weighted older
# ─────────────────────────────────────────────

# Profiles that are biologically male-only
MALE_ONLY_PROFILES = {"prostate_cancer"}

# Profiles that are biologically female-only
FEMALE_ONLY_PROFILES = {"breast_cancer", "ovarian_cancer"}

def generate_patient(top_profile=None, injected_profile=None):
    """
    Generates a simulated patient demographic record.
    Sex is locked by injected_profile first — clinically authoritative.
    top_profile used only as fallback when no injection fired.
    Age skewed older for cancer/neurological profiles.
    """
    # Injected profile is the clinical ground truth — always wins
    authority = injected_profile if injected_profile else top_profile

    if authority in MALE_ONLY_PROFILES:
        sex = "Male"
    elif authority in FEMALE_ONLY_PROFILES:
        sex = "Female"
    else:
        sex = random.choice(["Male", "Female"])

    older_skew = {"lung_cancer", "breast_cancer", "colorectal_cancer", "ovarian_cancer",
                  "prostate_cancer", "parkinsons", "alzheimers", "liver_disease"}
    if authority in older_skew:
        year_of_birth = random.randint(1935, 1975)
    else:
        year_of_birth = random.randint(1950, 2005)

    age = 2026 - year_of_birth

    return {
        "sex":           sex,
        "year_of_birth": year_of_birth,
        "age":           age,
    }

# ─────────────────────────────────────────────
# SENSOR SIMULATION
# ─────────────────────────────────────────────
def simulate_sensor_reading(inject_profile=None, inject_rate=0.25):
    """
    Simulates a gas sensor reading.
    Returns a dict of VOC compounds and ppm-like intensity values (0.0–1.0).
    In real hardware: replace with GPIO / serial reads from MQ or BME680 sensor.
    """
    active_vocs = random.sample(ALL_VOCS, k=random.randint(3, 6))
    reading = {voc: round(random.uniform(0.05, 1.0), 3) for voc in active_vocs}

    injected_key = None

    if inject_profile and inject_profile in SCENT_PROFILES:
        # Targeted injection mode — ONLY inject the specified profile, no random fallback
        if random.random() < inject_rate:
            profile = SCENT_PROFILES[inject_profile]
            for voc in profile["vocs"]:
                reading[voc] = round(random.uniform(0.6, 1.0), 3)
            injected_key = inject_profile
            reading["__injected__"] = inject_profile
    elif not inject_profile and random.random() < inject_rate:
        # Free-run mode only — random injection when no profile is specified
        injected_key = random.choice(list(SCENT_PROFILES.keys()))
        profile = SCENT_PROFILES[injected_key]
        for voc in profile["vocs"]:
            reading[voc] = round(random.uniform(0.6, 1.0), 3)
        reading["__injected__"] = injected_key

    reading["__injected_key__"] = injected_key  # track what actually fired

    return reading

# ─────────────────────────────────────────────
# VOC CLASSIFIER
# ─────────────────────────────────────────────
def classify_vocs(reading):
    detected_vocs = set(k for k, v in reading.items()
                        if not k.startswith("__") and v > 0.3)
    matches = []
    for profile_id, profile in SCENT_PROFILES.items():
        required = set(profile["vocs"])
        overlap = detected_vocs & required
        if not overlap:
            continue
        intensity_sum = sum(reading.get(v, 0) for v in overlap)
        confidence = round((len(overlap) / len(required)) * (intensity_sum / len(overlap)), 3)
        if confidence > 0.2:
            matches.append({
                "profile_id":   profile_id,
                "condition":    profile["condition"],
                "category":     profile["category"],
                "confidence":   confidence,
                "severity":     profile["severity"],
                "alert":        profile["alert"],
                "matched_vocs": list(overlap)
            })
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    return matches

# ─────────────────────────────────────────────
# ANOMALY DETECTOR
# ─────────────────────────────────────────────
def detect_anomaly(matches):
    if not matches:
        return None
    top = matches[0]
    if top["alert"] and top["confidence"] >= 0.4:
        return {
            "triggered":  True,
            "condition":  top["condition"],
            "severity":   top["severity"],
            "confidence": top["confidence"],
            "category":   top["category"],
            "action":     get_alert_action(top["severity"], top["category"])
        }
    return None

def get_alert_action(severity, category):
    actions = {
        ("critical", "behavioral"):   "DISPATCH Sierra/Eruptor — grounding protocol NOW",
        ("high",     "behavioral"):   "Notify caregiver — monitor closely",
        ("critical", "oncology"):     "FLAG for medical review — oncology signature detected",
        ("critical", "infectious"):   "ALERT — possible sepsis signature — contact emergency care",
        ("high",     "neurological"): "LOG for neurologist — degenerative marker present",
        ("high",     "metabolic"):    "Notify care team — metabolic anomaly detected",
        ("high",     "infectious"):   "Monitor — possible infection signature",
    }
    return actions.get((severity, category), "Log and continue monitoring")

# ─────────────────────────────────────────────
# LOGGER
# ─────────────────────────────────────────────
LOG_FILE = "opensmell_log.csv"

def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "sex", "year_of_birth", "age",
                "top_match", "category", "confidence", "severity",
                "alert_triggered", "action", "raw_vocs"
            ])

def log_result(reading, matches, alert):
    top = matches[0] if matches else {}
    patient = reading.get("__patient__", {})
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            patient.get("sex", "—"),
            patient.get("year_of_birth", "—"),
            patient.get("age", "—"),
            top.get("condition", "No match"),
            top.get("category", "—"),
            top.get("confidence", 0),
            top.get("severity", "none"),
            alert is not None,
            alert["action"] if alert else "—",
            json.dumps({k: v for k, v in reading.items() if not k.startswith("__")})
        ])

# ─────────────────────────────────────────────
# SESSION STATS TRACKER
# ─────────────────────────────────────────────
class SessionStats:
    def __init__(self):
        self.start_time    = datetime.now()
        self.total_cycles  = 0
        self.alerts        = 0
        self.by_category      = defaultdict(int)
        self.by_condition     = defaultdict(int)
        self.by_severity      = defaultdict(int)
        self.by_sex           = defaultdict(int)
        self.age_buckets      = defaultdict(int)
        self.no_match         = 0
        self.injected_cycles  = 0
        self.non_injected_conditions = defaultdict(int)   # what fired on background cycles
        self.female_detail    = defaultdict(int)          # what females tested for (non-injected)

    def record(self, matches, alert, patient, injected_key):
        self.total_cycles += 1

        # Only count demographics when injection actually fired
        # Non-injected cycles have random sex and would corrupt targeted test results
        if injected_key is not None:
            self.injected_cycles += 1
            sex = patient.get("sex", "Unknown")
            age = patient.get("age", 0)
            self.by_sex[sex] += 1
            if age < 30:   self.age_buckets["Under 30"] += 1
            elif age < 45: self.age_buckets["30–44"] += 1
            elif age < 60: self.age_buckets["45–59"] += 1
            elif age < 75: self.age_buckets["60–74"] += 1
            else:          self.age_buckets["75+"] += 1

        if not matches:
            self.no_match += 1
            return
        top = matches[0]
        self.by_category[top["category"]] += 1
        self.by_condition[top["condition"]] += 1
        self.by_severity[top["severity"]] += 1
        if alert:
            self.alerts += 1

        # Track non-injected cycle conditions and female detail separately
        if injected_key is None:
            self.non_injected_conditions[top["condition"]] += 1
            if patient.get("sex") == "Female":
                self.female_detail[top["condition"]] += 1

    def detection_rate(self):
        if self.total_cycles == 0:
            return 0.0
        return round((self.total_cycles - self.no_match) / self.total_cycles * 100, 2)

    def alert_rate(self):
        if self.total_cycles == 0:
            return 0.0
        return round(self.alerts / self.total_cycles * 100, 2)

    def elapsed(self):
        delta = datetime.now() - self.start_time
        return str(delta).split(".")[0]

# ─────────────────────────────────────────────
# SESSION REPORT (publication-ready)
# ─────────────────────────────────────────────
def write_session_report(stats, args):
    report_file = f"opensmell_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    lines = [
        "=" * 60,
        "  OpenSmell — Session Report",
        "  The Christman AI Project | Luma Cognify AI",
        "=" * 60,
        f"  Date/Time:        {stats.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Duration:         {stats.elapsed()}",
        f"  Speed Mode:       {args.speed}",
        f"  Seed:             {args.seed if args.seed is not None else 'random (unseeded)'}",
        f"  Total Cycles:     {stats.total_cycles}",
        f"  Detection Rate:   {stats.detection_rate()}%",
        f"  Alert Rate:       {stats.alert_rate()}%",
        f"  Total Alerts:     {stats.alerts}",
        f"  No-Match Cycles:  {stats.no_match}",
        "",
        "  ── Detections by Category ──────────────",
    ]
    for cat, count in sorted(stats.by_category.items(), key=lambda x: -x[1]):
        pct = round(count / stats.total_cycles * 100, 1)
        lines.append(f"    {cat:<20} {count:>5} cycles  ({pct}%)")
    lines += ["", "  ── Detections by Severity ──────────────"]
    for sev, count in sorted(stats.by_severity.items(), key=lambda x: -x[1]):
        pct = round(count / stats.total_cycles * 100, 1)
        lines.append(f"    {sev:<20} {count:>5} cycles  ({pct}%)")
    lines += ["", "  ── Top Conditions Detected ─────────────"]
    top_conditions = sorted(stats.by_condition.items(), key=lambda x: -x[1])[:10]
    for cond, count in top_conditions:
        pct = round(count / stats.total_cycles * 100, 1)
        lines.append(f"    {cond:<35} {count:>5}  ({pct}%)")
    lines += ["", "  ── Simulated Patient Demographics ──────"]
    lines.append(f"  (based on {stats.injected_cycles} injected cycles)")
    demo_base = stats.injected_cycles if stats.injected_cycles else 1
    for sex, count in sorted(stats.by_sex.items()):
        pct = round(count / demo_base * 100, 1)
        lines.append(f"    {sex:<20} {count:>5} patients  ({pct}%)")
    lines += ["", "  ── Age Distribution ─────────────────────"]
    for bucket in ["Under 30", "30–44", "45–59", "60–74", "75+"]:
        count = stats.age_buckets.get(bucket, 0)
        pct = round(count / demo_base * 100, 1)
        lines.append(f"    {bucket:<20} {count:>5} patients  ({pct}%)")
    lines += [
        "",
        f"  Log file: {LOG_FILE}",
        "",
        "  ── Background (Non-Injected) Cycle Conditions ──",
    ]
    if stats.non_injected_conditions:
        for cond, count in sorted(stats.non_injected_conditions.items(), key=lambda x: -x[1])[:10]:
            pct = round(count / stats.total_cycles * 100, 1)
            lines.append(f"    {cond:<35} {count:>5}  ({pct}%)")
    else:
        lines.append("    None recorded.")

    lines += ["", "  ── Female Patient Detail (Non-Injected) ────"]
    if stats.female_detail:
        lines.append("  Female patients appeared in background cycles only.")
        lines.append("  Conditions they tested for:")
        for cond, count in sorted(stats.female_detail.items(), key=lambda x: -x[1]):
            lines.append(f"    {cond:<35} {count:>5} female patients")
    else:
        lines.append("    No female patients recorded in non-injected cycles.")
    lines += [
        "",
        "=" * 60,
        "  © The Christman AI Project. All Rights Reserved.",
        "=" * 60,
    ]
    report_text = "\n".join(lines)
    with open(report_file, "w") as f:
        f.write(report_text)
    print(f"\n{Fore.CYAN}{report_text}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}  Report saved → {report_file}{Style.RESET_ALL}\n")

# ─────────────────────────────────────────────
# DISPLAY
# ─────────────────────────────────────────────
def print_cycle(cycle, reading, matches, alert, stats, target_cycles):
    ts = datetime.now().strftime("%H:%M:%S")
    injected = reading.get("__injected__", None)
    patient  = reading.get("__patient__", {})
    cycle_label = f"{cycle}/{target_cycles}" if target_cycles else f"{cycle:04d}"

    print(f"\n{Fore.CYAN}{'─'*60}")
    print(f"{Fore.CYAN}  OpenSmell  │  Cycle {cycle_label}  │  {ts}  │  Alerts: {stats.alerts}")
    print(f"{Fore.CYAN}  Patient:   │  {patient.get('sex','—')}  │  DOB: {patient.get('year_of_birth','—')}  │  Age: {patient.get('age','—')}")
    print(f"{Fore.CYAN}  Phase:     │  {reading.get('__phase__','—')}  — {reading.get('__phase_desc__','—')}")
    if injected:
        print(f"{Fore.MAGENTA}  [TEST INJECT] → {injected}")
    print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")

    active = {k: v for k, v in reading.items() if not k.startswith("__") and v > 0.3}
    print(f"  {Fore.WHITE}Active VOCs:{Style.RESET_ALL} {', '.join(f'{k}({v})' for k,v in active.items())}")

    if matches:
        print(f"\n  {Fore.WHITE}Top Matches:{Style.RESET_ALL}")
        for m in matches[:3]:
            col = SEVERITY_COLORS.get(m["severity"], Fore.WHITE)
            bar = "█" * int(m["confidence"] * 20)
            print(f"    {col}{bar:<20} {m['confidence']:.2f}  {m['condition']}  [{m['severity'].upper()}]{Style.RESET_ALL}")
    else:
        print(f"  {Fore.GREEN}  No significant matches — baseline normal{Style.RESET_ALL}")

    if alert:
        col = SEVERITY_COLORS.get(alert["severity"], Fore.WHITE)
        print(f"\n  {col}⚠  ALERT: {alert['condition']}{Style.RESET_ALL}")
        print(f"  {col}   Action: {alert['action']}{Style.RESET_ALL}")
    else:
        print(f"\n  {Fore.GREEN}  ✓ No alert  │  Detection rate: {stats.detection_rate()}%{Style.RESET_ALL}")

# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
def run():
    args = parse_args()
    interval = SPEED_MAP[args.speed]
    target_cycles = args.cycles
    stats = SessionStats()

    init_log()

    if args.seed is not None:
        random.seed(args.seed)
        print(f"{Fore.MAGENTA}  Seed locked: {args.seed} — run is fully reproducible{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}  OpenSmell Continuous Testing Loop")
    print(f"  The Christman AI Project — Simulation Mode")
    print(f"  Speed: {args.speed} ({interval}s/cycle)  |  Cycles: {'∞' if not target_cycles else target_cycles}")
    if args.inject:
        print(f"  Seeded inject: {args.inject} @ {int(args.inject_rate*100)}% rate")
    print(f"  Logging to: {LOG_FILE}")
    print(f"  Press Ctrl+C to stop and generate report\n{Style.RESET_ALL}")
    time.sleep(1)

    try:
        while True:
            stats.total_cycles += 1
            # Generate fresh patient baseline each cycle — unique biological fingerprint
            patient_baseline = generate_patient_baseline(ALL_VOCS)
            reading      = bio_simulate_sensor_reading(
                               ALL_VOCS, SCENT_PROFILES,
                               inject_profile=args.inject,
                               inject_rate=args.inject_rate,
                               patient_baseline=patient_baseline
                           )
            matches      = classify_vocs(reading)
            alert        = detect_anomaly(matches)
            injected_key = reading.get("__injected_key__", None)
            top_profile  = matches[0]["profile_id"] if matches else None
            patient      = generate_patient(top_profile=top_profile, injected_profile=injected_key)
            reading["__patient__"] = patient
            stats.record(matches, alert, patient, injected_key)
            log_result(reading, matches, alert)
            print_cycle(stats.total_cycles, reading, matches, alert, stats, target_cycles)

            if target_cycles and stats.total_cycles >= target_cycles:
                print(f"\n{Fore.CYAN}  Target of {target_cycles} cycles reached.{Style.RESET_ALL}")
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}  OpenSmell stopped after {stats.total_cycles} cycles.{Style.RESET_ALL}")

    write_session_report(stats, args)

if __name__ == "__main__":
    run()
