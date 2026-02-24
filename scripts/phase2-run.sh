#!/bin/bash
# LinkedIn Phase 2 — Overnight Runner
#
# Loops until all 107 contacts are processed.
# On rate limit: waits 70 minutes then retries.
# Safe to kill and restart at any time.
#
# Usage:
#   ./scripts/phase2-run.sh              # run overnight
#   ./scripts/phase2-run.sh --max 10     # test with 10 contacts

set -e
cd "$(dirname "$0")/.."

MAX=${2:-25}  # contacts per batch, default 25
WAIT=4200     # 70 minutes between batches if rate limited

echo "================================================"
echo "LinkedIn Phase 2 Search — $(date)"
echo "Max per batch: $MAX | Wait on rate limit: ${WAIT}s"
echo "================================================"

while true; do
    # Check how many are still pending
    PENDING=$(python3 -c "
import json
d = json.load(open('Notes/active/linkedin-phase2-list.json'))
print(len([c for c in d['contacts'] if c.get('status') == 'pending']))
")

    if [ "$PENDING" = "0" ]; then
        echo ""
        echo "All contacts processed! Generating report..."
        python3 scripts/phase2-report.py
        break
    fi

    echo ""
    echo "$(date) — $PENDING contacts remaining"
    python3 scripts/phase2-search.py --max "$MAX"
    EXIT=$?

    # If script exited cleanly (rate limit), wait before retrying
    PENDING_AFTER=$(python3 -c "
import json
d = json.load(open('Notes/active/linkedin-phase2-list.json'))
print(len([c for c in d['contacts'] if c.get('status') == 'pending']))
")

    if [ "$PENDING_AFTER" = "$PENDING" ]; then
        echo "$(date) — Rate limited. Waiting $(($WAIT / 60)) minutes..."
        sleep $WAIT
    elif [ "$PENDING_AFTER" = "0" ]; then
        echo "All done!"
        python3 scripts/phase2-report.py
        break
    else
        echo "$(date) — Batch complete. Short pause before next batch..."
        sleep 120
    fi
done
