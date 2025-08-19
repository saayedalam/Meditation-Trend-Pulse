#!/bin/bash
set -euo pipefail

# ──────────────────────────────────────────────
# 🧠 Automation: Run update script + manage logs
# ──────────────────────────────────────────────
# Activate virtual environment
source /Users/saayedalam/jupyterlab-env/bin/activate

# Set project root
cd /Users/saayedalam/Documents/data_portfolio/meditation-trend-pulse || exit 1

# Make sure logs folder exists
mkdir -p logs

# Generate monthly log filename (e.g. update_log_2025_08.txt)
LOG_FILE="logs/update_log_$(date '+%Y_%m').txt"

# Write header for this run
{
  echo ""
  echo "────────────────────────────────────────────"
  echo "🕒 Update Run — $(date '+%Y-%m-%d %H:%M:%S')"
  echo "────────────────────────────────────────────"
} >> "$LOG_FILE"

# Run Python update script and append output
/Users/saayedalam/jupyterlab-env/bin/python3 automation/update_all_datasets.py >> "$LOG_FILE" 2>&1

# Cleanup: Delete logs older than 6 months
find logs/ -name "update_log_*.txt" -mtime +180 -delete || true

# ──────────────────────────────────────────────
# 🔁 GitHub Auto Commit & Push (if file changed)
# ──────────────────────────────────────────────
# Only commit if new weekly data was added (based on script log output)
if grep -q "✅ Overwrote global_trend_summary.csv" "$LOG_FILE"; then
  git add \
    data/streamlit/global_trend_summary.csv \
    data/streamlit/trend_pct_change.csv \
    data/streamlit/trend_top_peaks.csv
  git commit -m "🔄 Auto update: datasets on $(date +'%Y-%m-%d')" >> "$LOG_FILE" 2>&1
  git push origin main >> "$LOG_FILE" 2>&1
  echo "🚀 Changes pushed to GitHub." >> "$LOG_FILE"
else
  echo "📂 No new weekly data — skipping GitHub push." >> "$LOG_FILE"
fi