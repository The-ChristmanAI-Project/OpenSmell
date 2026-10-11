#!/bin/bash
# OpenSmell Grant Validation Batch Runner
# Runs labeled simulation across key profile categories.
# More cycles = stronger grant evidence. Logs go to $OPENSMELL_LOG_FILE
# (default opensmell_log_grant_batch.csv) with ground-truth columns.

set -e
cd "$(dirname "$0")"

CYCLES="${CYCLES:-1000}"
RATE="${RATE:-0.4}"
SPEED="${SPEED:-turbo}"
SEED="${SEED:-42}"
LOG_FILE="${OPENSMELL_LOG_FILE:-opensmell_log_grant_batch.csv}"
export OPENSMELL_LOG_FILE="$LOG_FILE"

# Representative profiles across cancer, neuro, metabolic, infectious, psychiatric
PROFILES=(
    alzheimers
    lung_cancer
    breast_cancer
    parkinsons
    diabetes_type1
    liver_disease
    covid19
    sepsis
    rage_cortisol
    pre_seizure
)

echo ""
echo "  OpenSmell Grant Batch Runner"
echo "  Profiles: ${#PROFILES[@]} | Cycles/profile: $CYCLES | Rate: $RATE | Seed: $SEED"
echo "  Total cycles: $((${#PROFILES[@]} * CYCLES))"
echo "  Log file:     $LOG_FILE"
echo ""

python3 test_open_smell2.py -q

# One-time legacy archive before batch (subsequent runs append safely).
python3 -c "
from opensmell_test_loop import init_log
init_log()
print('  [batch] log ready:', __import__('opensmell_test_loop').LOG_FILE)
"

for profile in "${PROFILES[@]}"; do
    echo "  ── Running: $profile ──"
    python3 opensmell_test_loop.py \
        --inject "$profile" \
        --inject-rate "$RATE" \
        --cycles "$CYCLES" \
        --speed "$SPEED" \
        --seed "$SEED"
done

echo ""
echo "  Grant batch complete."
echo "  Log: $LOG_FILE"
echo "  Reports: opensmell_report_*.txt"
echo ""