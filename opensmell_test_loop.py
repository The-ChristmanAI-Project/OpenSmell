"""
OpenSmell Continuous Testing Loop
The Christman AI Project — Luma Cognify AI
Author: Everett Christman + Claude (grounding board)

SIMULATION MODE — No hardware required.
Simulates VOC sensor readings and runs the full pipeline:
  1. Read sensor (simulated)
  2. Classify VOC compound
  3. Detect anomaly → trigger AI alert
  4. Match against scent profile database (21 live profiles via open_smell2)
  5. Log results continuously
  6. Generate publication-ready session report

MODES:
  Normal:      python opensmell_test_loop.py
  High-Speed:  python opensmell_test_loop.py --speed fast
  Benchmark:   python opensmell_test_loop.py --cycles 1000
  Seeded Run:  python opensmell_test_loop.py --cycles 500 --inject alzheimers --inject-rate 0.4

Classifier: open_smell2.classify() — single engine for sim + production.

To install:
    pip install colorama
"""

import time
import random
import json
import csv
import os
import argparse
import sys
from datetime import datetime
from collections import defaultdict
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _DummyColor:
        def __getattr__(self, _name: str) -> str:
            return ""

    Fore = Style = _DummyColor()  # type: ignore[misc, assignment]

    def init(*_args, **_kwargs) -> None:
        pass

from opensmell_bio_sim import bio_simulate_sensor_reading, generate_patient_baseline
from open_smell2 import classify, PROFILE_SIGNATURES, SCENT_PROFILES, SENSOR_CHANNELS

# Sensor-grounded injection map — same channels the classifier matches against.
INJECTION_PROFILES = {k: {"vocs": v} for k, v in PROFILE_SIGNATURES.items()}
ALL_VOCS = SENSOR_CHANNELS
LIVE_PROFILE_COUNT = len(PROFILE_SIGNATURES)

# Legacy inject keys from run_test.sh / earlier sim runs.
INJECT_ALIASES = {
    "diabetes_t1t2": "diabetes_type1",
    "cortisol_spike": "rage_cortisol",
    "serotonin_drop": "depressive_spiral",
    "adrenaline_surge": "fight_or_flight",
    "neurological_prefit": "pre_seizure",
}

SEVERITY_COLORS = {
    "critical":   Fore.RED,
    "high":       Fore.YELLOW,
    "moderate":   Fore.YELLOW,
    "monitoring": Fore.GREEN,
    "none":       Fore.GREEN,
}


def resolve_inject_profile(key):
    """Map CLI inject key to a live open_smell2 profile key."""
    if key is None:
        return None
    resolved = INJECT_ALIASES.get(key, key)
    if resolved not in PROFILE_SIGNATURES:
        live = ", ".join(sorted(PROFILE_SIGNATURES))
        aliases = ", ".join(f"{k}→{v}" for k, v in sorted(INJECT_ALIASES.items()))
        print(f"{Fore.RED}Unknown inject profile: {key!r}{Style.RESET_ALL}")
        print(f"  Live profiles: {live}")
        print(f"  Legacy aliases: {aliases}")
        sys.exit(1)
    return resolved

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
                        help="Force-inject a live profile key (e.g. alzheimers, lung_cancer)")
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
# VOC CLASSIFIER (delegates to open_smell2)
# ─────────────────────────────────────────────
def classify_vocs(reading):
    """Classify a sensor reading via open_smell2.classify()."""
    return [
        {
            "profile_id":   m["profile_key"],
            "condition":    m["condition"],
            "category":     m["category"],
            "confidence":   m["confidence"],
            "severity":     m["severity"],
            "alert":        m["alert"],
            "matched_vocs": m["matched_channels"],
        }
        for m in classify(reading, top_n=10)
    ]

# ─────────────────────────────────────────────
# ANOMALY DETECTOR
# ─────────────────────────────────────────────
def detect_anomaly(matches):
    if not matches:
        return None
    top = matches[0]
    threshold = SCENT_PROFILES[top["profile_id"]].confidence_threshold
    if top["alert"]:
        return {
            "triggered":  True,
            "condition":  top["condition"],
            "severity":   top["severity"],
            "confidence": top["confidence"],
            "category":   top["category"],
            "profile_id": top["profile_id"],
            "threshold":  threshold,
            "action":     get_alert_action(top["severity"], top["category"])
        }
    return None

def get_alert_action(severity, category):
    actions = {
        ("critical", "psychiatric"):  "DISPATCH Sierra/Eruptor — grounding protocol NOW",
        ("high",     "psychiatric"):  "Notify caregiver — monitor closely",
        ("critical", "cancer"):       "FLAG for medical review — oncology signature detected",
        ("critical", "infectious"):   "ALERT — possible sepsis/infection — contact emergency care",
        ("high",     "neurological"): "LOG for neurologist — degenerative marker present",
        ("high",     "metabolic"):    "Notify care team — metabolic anomaly detected",
        ("critical", "metabolic"):    "URGENT — metabolic crisis signature — contact care team",
        ("high",     "infectious"):   "Monitor — possible infection signature",
    }
    return actions.get((severity, category), "Log and continue monitoring")

# ─────────────────────────────────────────────
# LOGGER
# ─────────────────────────────────────────────
# OPENSMELL_LOG_FILE lets a batch runner send its rows to its own file
# (run_grant_batch.sh sets it). Default stays opensmell_log.csv.
LOG_FILE = os.environ.get("OPENSMELL_LOG_FILE", "opensmell_log.csv")

# Canonical header, same as opensmell_test_loopV2.py. Ground-truth columns
# (is_injected / injected_key / injected_condition) sit BEFORE the prediction
# columns so every row reads truth | prediction | features. Without them a
# log can show coverage but can never be audited for accuracy.
LOG_HEADER = [
    "timestamp", "sex", "year_of_birth", "age",
    "is_injected", "injected_key", "injected_condition",
    "top_match", "category", "confidence", "severity",
    "alert_triggered", "action", "raw_vocs"
]

def init_log():
    """Create the log with the canonical header.

    If a log already exists with a different header (the pre-ground-truth
    11-column schema), it is renamed to a timestamped backup so labeled rows
    are never appended under an incompatible schema.
    """
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", newline="") as f:
            first = next(csv.reader(f), [])
        if first != LOG_HEADER:
            stem = os.path.splitext(LOG_FILE)[0]
            backup = f"{stem}.pre_gt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(LOG_FILE, backup)
            print(f"  [logger] existing log had a legacy schema — archived to {backup}")
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(LOG_HEADER)

def log_result(reading, matches, alert):
    top = matches[0] if matches else {}
    patient = reading.get("__patient__", {})

    # Ground truth: the simulator records which profile it injected this cycle
    # in reading["__injected_key__"] (None on background cycles, whose true
    # label is "Healthy / Background" and correct prediction is "No match").
    injected_key = reading.get("__injected_key__")
    is_injected = injected_key is not None
    if is_injected:
        prof = SCENT_PROFILES.get(injected_key)
        injected_condition = prof.condition if prof is not None else injected_key
    else:
        injected_condition = "Healthy / Background"

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            patient.get("sex", "—"),
            patient.get("year_of_birth", "—"),
            patient.get("age", "—"),
            is_injected,
            injected_key if is_injected else "—",
            injected_condition,
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
        self.non_injected_conditions = defaultdict(int)
        self.female_detail    = defaultdict(int)
        self.inject_hits      = 0
        self.inject_misses    = 0

    def record(self, matches, alert, patient, injected_key):
        # total_cycles is incremented once per cycle in run(); incrementing it
        # here as well doubled every cycle count, which inflated the detection
        # rate and halved the alert and category rates. Fixed 2026-10-11.
        if injected_key is not None:
            self.injected_cycles += 1
            if matches and matches[0]["profile_id"] == injected_key:
                self.inject_hits += 1
            else:
                self.inject_misses += 1
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

    def inject_accuracy(self):
        if self.injected_cycles == 0:
            return 0.0
        return round(self.inject_hits / self.injected_cycles * 100, 2)

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
        f"  Live Profiles:    {LIVE_PROFILE_COUNT} (open_smell2 engine)",
        "",
    ]
    if stats.injected_cycles:
        lines += [
            f"  Injection Accuracy: {stats.inject_accuracy()}% "
            f"({stats.inject_hits} hits / {stats.injected_cycles} injected cycles)",
            "",
        ]
    lines += ["  ── Detections by Category ──────────────"]
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
    lines += ["", f"  Log file: {LOG_FILE}", "", "  ── Background (Non-Injected) Cycle Conditions ──"]
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
    lines += ["", "=" * 60, "  © The Christman AI Project. All Rights Reserved.", "=" * 60]
    report_text = "\n".join(lines)
    with open(report_file, "w") as f:
        f.write(report_text)
    print(f"\n{Fore.CYAN}{report_text}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}  Report saved → {report_file}{Style.RESET_ALL}\n")

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

def run():
    args = parse_args()
    interval = SPEED_MAP[args.speed]
    target_cycles = args.cycles
    stats = SessionStats()
    init_log()
    if args.seed is not None:
        random.seed(args.seed)
        print(f"{Fore.MAGENTA}  Seed locked: {args.seed} — run is fully reproducible{Style.RESET_ALL}")
    inject_profile = resolve_inject_profile(args.inject)
    print(f"\n{Fore.CYAN}  OpenSmell Continuous Testing Loop")
    print(f"  The Christman AI Project — Simulation Mode")
    print(f"  Classifier: open_smell2 ({LIVE_PROFILE_COUNT} live profiles)")
    print(f"  Speed: {args.speed} ({interval}s/cycle)  |  Cycles: {'∞' if not target_cycles else target_cycles}")
    if inject_profile:
        alias_note = f" (alias of {args.inject})" if args.inject != inject_profile else ""
        print(f"  Seeded inject: {inject_profile}{alias_note} @ {int(args.inject_rate*100)}% rate")
    print(f"  Logging to: {LOG_FILE}")
    print(f"  Press Ctrl+C to stop and generate report\n{Style.RESET_ALL}")
    time.sleep(1)
    try:
        while True:
            stats.total_cycles += 1
            patient_baseline = generate_patient_baseline(ALL_VOCS)
            reading = bio_simulate_sensor_reading(ALL_VOCS, INJECTION_PROFILES, inject_profile=inject_profile, inject_rate=args.inject_rate, patient_baseline=patient_baseline)
            matches = classify_vocs(reading)
            alert = detect_anomaly(matches)
            injected_key = reading.get("__injected_key__", None)
            top_profile = matches[0]["profile_id"] if matches else None
            patient = generate_patient(top_profile=top_profile, injected_profile=injected_key)
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
