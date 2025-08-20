#!/bin/bash
set -euo pipefail  # fail fast: stop on errors (-e), undefined vars (-u), and pipeline errors (-o pipefail)

# ════════════════════════════════════════════════════════════════════════════════
# 📜 Script: run_update.sh
# 🧠 Purpose: Orchestrate daily dataset updates for Meditation Trend Pulse under cron.
#    - Ensure the right environment (PATH, HOME, venv) since cron is minimal
#    - cd into the project so relative paths resolve
#    - Append a timestamped header to a rolling monthly log file
#    - Run the Python updater and capture BOTH stdout/stderr into the same log
#    - Prune old logs to keep the repo clean
#    - If (and only if) the global dataset was actually overwritten, stage/commit/push
# 🧪 Note: This script is intentionally minimal — do not change commands, only comments.
# ════════════════════════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────
# Environment for cron (cron has a tiny environment by default)
# ──────────────────────────────────────────────
export HOME="/Users/saayedalam"   # make sure git uses my user-level config (name/email/credentials)
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/Users/saayedalam/jupyterlab-env/bin"  # ensure python/poetry/pip etc. are on PATH

# ──────────────────────────────────────────────
# 🧠 Automation: Run update script + manage logs
# ──────────────────────────────────────────────

# Activate virtual environment so the correct Python + packages are used
source /Users/saayedalam/jupyterlab-env/bin/activate

# Move into the project root; exit with code 1 if the directory is missing
cd /Users/saayedalam/Documents/data_portfolio/meditation-trend-pulse || exit 1

# Make sure a logs folder exists (safe if it already exists)
mkdir -p logs

# Build the absolute path to a monthly log file (e.g., update_log_2025_08.txt)
# Using an absolute path avoids cron confusion about the working directory
LOG_FILE="/Users/saayedalam/Documents/data_portfolio/meditation-trend-pulse/logs/update_log_$(date '+%Y_%m').txt"

# Write a visual header for this run into the monthly log (blank line + separators + timestamp)
{
  echo ""
  echo "────────────────────────────────────────────"
  echo "🕒 Update Run — $(date '+%Y-%m-%d %H:%M:%S')"
  echo "────────────────────────────────────────────"
} >> "$LOG_FILE"

# Run the Python updater and append BOTH stdout and stderr to the same log file
# (the '2>&1' redirects errors to stdout so everything lands in $LOG_FILE)
# DO NOT CHANGE: this keeps behavior stable for cron + logging
/Users/saayedalam/jupyterlab-env/bin/python3 automation/update_all_datasets.py >> "$LOG_FILE" 2>&1

# Remove monthly log files older than ~6 months (180 days)
# The '|| true' ensures the script never fails if 'find' encounters a transient issue
find logs/ -name "update_log_*.txt" -mtime +180 -delete || true

# ──────────────────────────────────────────────
# ✅ Git Auto Commit ONLY if Global Dataset Updated
# ──────────────────────────────────────────────
# We grep the log for the exact success marker printed by the Python script when it overwrites global_trend_summary.csv.
# If that marker is present, we stage potential dataset outputs, then commit/push ONLY if there is an actual diff.
if grep -q "✅ Overwrote global_trend_summary.csv" "$LOG_FILE"; then
  echo "📤 Checking if any dataset was updated..." >> "$LOG_FILE"

  # Stage all datasets that might have changed during a real update
  git add \
    data/streamlit/global_trend_summary.csv \
    data/streamlit/trend_pct_change.csv \
    data/streamlit/trend_top_peaks.csv \
    data/streamlit/country_interest_summary.csv \
    data/streamlit/country_total_interest_by_keyword.csv \
    data/streamlit/country_top5_appearance_counts.csv \
    data/streamlit/related_queries_top10.csv \
    data/streamlit/related_queries_rising10.csv \
    data/streamlit/related_queries_shared.csv

  # If nothing is staged (no diff), skip committing to keep the repo noise-free
  if git diff --cached --quiet; then
    echo "✅ Update script completed — no dataset changes detected." >> "$LOG_FILE"
  else
    # Commit with a timestamped message; '|| true' prevents the script from failing if commit/push hits a transient issue
    git commit -m "🔄 Auto update: datasets on $(date +'%Y-%m-%d')" >> "$LOG_FILE" 2>&1 || true
    git push origin main >> "$LOG_FILE" 2>&1 || true
    echo "🚀 Changes pushed to GitHub." >> "$LOG_FILE"
  fi
else
  # If the global dataset was not overwritten, everything downstream is intentionally skipped
  echo "📂 No new global dataset — skipping GitHub push." >> "$LOG_FILE"
fi