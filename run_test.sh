#!/bin/bash
# ─────────────────────────────────────────────
# OpenSmell Test Runner
# The Christman AI Project | Luma Cognify AI
# ─────────────────────────────────────────────
# Change INJECT to switch what you're testing.
# Available profiles:
#   prostate_cancer    lung_cancer       breast_cancer
#   colorectal_cancer  ovarian_cancer    alzheimers
#   parkinsons         diabetes_t1t2     liver_disease
#   sepsis             covid19           cortisol_spike
#   adrenaline_surge   neurological_prefit  serotonin_drop
# ─────────────────────────────────────────────

INJECT="alzheimers"       # ← CHANGE THIS LINE ONLY
RATE="0.4"                # injection rate (0.0–1.0)
CYCLES="1000"             # cycles per run
SPEED="turbo"             # normal | fast | turbo

echo ""
echo "  OpenSmell Test Runner"
echo "  Injection: $INJECT @ ${RATE} rate"
echo "  Cycles:    $CYCLES | Speed: $SPEED"
echo ""

python opensmell_test_loop.py \
    --inject "$INJECT" \
    --inject-rate "$RATE" \
    --cycles "$CYCLES" \
    --speed "$SPEED"
