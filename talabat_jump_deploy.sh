#!/bin/bash
# Talabat Jump dashboard: rebuild from BigQuery + redeploy to the GCS site.
# Run manually any time, or via the daily launchd job
# (~/Library/LaunchAgents/com.dh.talabat-jump-refresh.plist).
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"

DIR="/Users/harnoor.chahal/ai"
BUCKET="gs://dh-cpl-seamless-dashboards"
FILE="talabat_jump_dashboard.html"
LOG="$DIR/talabat_jump_refresh.log"

{
  echo "================ refresh $(date '+%Y-%m-%d %H:%M:%S') ================"
  cd "$DIR"
  /usr/bin/python3 talabat_jump_build.py
  gcloud storage cp "$DIR/$FILE" "$BUCKET/$FILE" --content-type=text/html
  echo "deployed -> https://storage.cloud.google.com/dh-cpl-seamless-dashboards/$FILE"
  echo "done $(date '+%Y-%m-%d %H:%M:%S')"
} >> "$LOG" 2>&1
