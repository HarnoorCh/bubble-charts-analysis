#!/bin/bash
# Weekly Seamless anomaly analysis — invoked by launchd every 2hrs from Mon 10:00 → Wed 22:00.
#
# SCOPE: generate the report from live BigQuery AND send it to the three Slack DMs — the
# behaviour that ran automatically W22–W26. Sending depends on the Slack OAuth plugin token
# being valid in headless runs; that token EXPIRED between W26 (Jun 29, sent OK) and W27
# (Jul 6, first failure). When it lapses, re-authorize Slack once interactively to refresh it.
#
# Dedup is PROVENANCE-based, not existence-based: the gate is a marker file
#   /Users/harnoor.chahal/ai/seamless-reports/.state/sent-<ISO_WEEK>.ok
# that the agent writes ONLY after a live-SQL report AND all 3 Slack sends succeed.
# Rationale:
#   - The dense 2-hourly schedule is a sleep workaround (launchd doesn't wake the Mac; it
#     coalesces one catch-up on wake). The marker dedups redundant fires so we send exactly
#     once per week while staying sleep-tolerant.
#   - Gating on the report .md existing (the old behaviour) served a STALE or hand-substituted
#     file forever (the 2026W27 / "June MBR" incident) AND marked done even when sends failed.
#     A missing marker => re-run: it regenerates stale files AND keeps retrying sends every 2h
#     until they succeed ("send as and when you can"). Self-heals once the token is refreshed.
#   - To force a fresh regeneration + resend, delete the marker: rm .state/sent-<ISO_WEEK>.ok

set -euo pipefail

# --- Paths & environment ---
export PATH="/Users/harnoor.chahal/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/harnoor.chahal"

REPO_ROOT="/Users/harnoor.chahal/ai"
DART_FILE="$REPO_ROOT/Command files/DART-v1.md"
REPORT_DIR="$REPO_ROOT/seamless-reports"
LOG_DIR="$REPORT_DIR/logs"

mkdir -p "$LOG_DIR"

# Target week = the most recently completed ISO Mon–Sun week.
# On any day, the latest fully complete week ended last Sunday.
# Use Python for reliable ISO-week math (BSD date on macOS lacks --iso-8601).
ISO_WEEK="$(python3 -c '
import datetime as dt
today = dt.date.today()
# Last Sunday (weekday 6 in ISO: Mon=1..Sun=7)
days_since_sunday = (today.weekday() + 1) % 7  # weekday(): Mon=0..Sun=6
last_sunday = today - dt.timedelta(days=days_since_sunday or 7)
iso = last_sunday.isocalendar()
print(f"{iso.year}W{iso.week:02d}")
')"

TS="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_FILE="$LOG_DIR/run-$TS.log"
CANONICAL_REPORT="$REPORT_DIR/report-$ISO_WEEK.md"
STATE_DIR="$REPORT_DIR/.state"
SENT_MARKER="$STATE_DIR/sent-$ISO_WEEK.ok"

mkdir -p "$STATE_DIR"

{
  echo "=== Seamless analysis check $TS ==="
  echo "Target week: $ISO_WEEK"
  echo "Canonical report: $CANONICAL_REPORT"
  echo "Sent marker: $SENT_MARKER"
} | tee -a "$LOG_FILE"

# --- Provenance gate (NOT existence-based; see header) ---
# Skip only if a prior run produced a live-SQL report AND all 3 sends succeeded.
# A stale/substituted .md with no marker is regenerated; unsent weeks keep retrying.
if [[ -s "$SENT_MARKER" ]]; then
  echo "Marker present for $ISO_WEEK — already generated + sent; skipping." | tee -a "$LOG_FILE"
  exit 0
fi

# --- Prompt (DART-v1 computes + saves the report, sends to Slack, then writes the marker) ---
read -r -d '' PROMPT <<EOF || true
Read /Users/harnoor.chahal/ai/Command files/DART-v1.md and execute the /run-seamless-analysis workflow defined in it end-to-end for ISO week $ISO_WEEK.

Follow the Execution Sequence in DART-v1.md exactly. Idempotency is BYPASSED (step 0): do NOT read or emit any cached report — always run Query 1/2/3 against live BigQuery, apply the Determinism Rules, and OVERWRITE /Users/harnoor.chahal/ai/seamless-reports/report-$ISO_WEEK.md with the freshly computed report.

After saving, send the final formatted report verbatim to THREE Slack DMs using the mcp__plugin_slack_slack__slack_send_message tool:
- channel_id "U036E4LSTCP" (Harnoor)
- channel_id "U4QNW0MJ7" (Daniel Rüdiger)
- channel_id "U0710JS2BPZ" (Nicolò Luti)

Do not ask for confirmation. Proceed autonomously and do all three sends. Print the final report to stdout as well so it gets captured to the log.

If the Slack send tool is unavailable (headless token lapsed), do NOT fabricate a send and do NOT write the marker — just report the sends as failed; the next scheduled fire will retry.

FINAL STEP — completion marker (governs dedup): ONLY if all three Slack sends returned success, write the current UTC timestamp to /Users/harnoor.chahal/ai/seamless-reports/.state/sent-$ISO_WEEK.ok. If the report could not be computed, or ANY of the three sends failed, do NOT create that marker — leaving it absent lets the next scheduled fire retry.
EOF

# --- Execute ---
echo "Running analysis for $ISO_WEEK..." | tee -a "$LOG_FILE"

if claude \
  --print \
  --dangerously-skip-permissions \
  --output-format text \
  "$PROMPT" \
  >> "$LOG_FILE" \
  2>&1; then
  if [[ ! -s "$CANONICAL_REPORT" ]]; then
    echo "=== Claude finished but $CANONICAL_REPORT was NOT written — treating as failure ===" | tee -a "$LOG_FILE"
    exit 2
  fi
  if [[ -s "$SENT_MARKER" ]]; then
    echo "=== Completed OK at $(date). Report generated + all 3 sends confirmed: $CANONICAL_REPORT ===" | tee -a "$LOG_FILE"
    exit 0
  else
    # Report exists but no marker => a send failed (likely the headless Slack token lapsed).
    # Leave the marker absent so the next fire retries; re-authorize Slack to self-heal.
    echo "=== Report written but NO marker for $ISO_WEEK — sends failed (check Slack token); will retry next fire ===" | tee -a "$LOG_FILE"
    exit 3
  fi
else
  EXIT_CODE=$?
  echo "=== Claude FAILED with exit $EXIT_CODE at $(date) ===" | tee -a "$LOG_FILE"
  exit $EXIT_CODE
fi
