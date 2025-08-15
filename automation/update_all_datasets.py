"""
Script to update all datasets in the Meditation Trend Pulse project.
Currently updates:
- Global Trends dataset (global_trend_summary.csv)

Planned extensions:
- Country Trends
- Related Queries
- Other datasets...

This script is intended to be run once per day. If already run today, it will skip.
"""

import pandas as pd
from datetime import datetime
from pytrends.request import TrendReq
import os
import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

# Keywords for global trend dataset
KEYWORDS = ["meditation", "mindfulness", "breathwork", "guided meditation", "yoga nidra"]

# Paths
DATA_DIR = os.path.join("data", "streamlit")
GLOBAL_TREND_PATH = os.path.join(DATA_DIR, "global_trend_summary.csv")
RUN_TRACK_FILE = ".last_run_date"

# Pytrends setup
pytrends = TrendReq(hl='en-US', tz=360)

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def already_ran_today():
    """Return True if the script has already run today, based on the timestamp file."""
    if os.path.exists(RUN_TRACK_FILE):
        with open(RUN_TRACK_FILE, "r") as f:
            last_run = f.read().strip()
            if last_run == datetime.today().strftime("%Y-%m-%d"):
                return True
    return False

def mark_today_as_ran():
    """Update the run tracking file with today's date."""
    with open(RUN_TRACK_FILE, "w") as f:
        f.write(datetime.today().strftime("%Y-%m-%d"))

# ─────────────────────────────────────────────────────────────
# FUNCTION: Pull last 5 years of weekly data for consistency
# ─────────────────────────────────────────────────────────────

def pull_full_weekly_data(keywords: list) -> pd.DataFrame:
    """
    Pulls 5 years of weekly data for all keywords.
    """
    all_results = []
    for kw in keywords:
        pytrends.build_payload([kw], timeframe="today 5-y")
        df = pytrends.interest_over_time()
        if df.empty:
            continue
        df = df.reset_index()[["date", kw]].rename(columns={kw: "search_interest"})
        df["keyword"] = kw
        df = df[["date", "keyword", "search_interest"]]
        all_results.append(df)

    if not all_results:
        return pd.DataFrame()

    df_full = pd.concat(all_results, ignore_index=True)
    df_full["date"] = pd.to_datetime(df_full["date"])
    return df_full

# ─────────────────────────────────────────────────────────────
# FUNCTION: Update global_trend_summary.csv (latest Sunday only)
# ─────────────────────────────────────────────────────────────

def update_global_trend_dataset():
    print("🔄 Updating global_trend_summary.csv...")

    # Load existing dataset
    df_existing = pd.read_csv(GLOBAL_TREND_PATH, parse_dates=["date"])
    latest_existing_date = df_existing["date"].max()

    # Pull latest 5-year weekly data for all keywords
    df_full = pull_full_weekly_data(KEYWORDS)
    if df_full.empty:
        print("⚠️ No new data retrieved from Google Trends.")
        return

    # Filter only the latest full week from Google Trends
    latest_available_date = df_full["date"].max()
    df_latest = df_full[df_full["date"] == latest_available_date]

    if latest_available_date <= latest_existing_date:
        print("✅ No new data to append. Dataset already up to date.")
        return

    # Append and deduplicate
    df_combined = pd.concat([df_existing, df_latest], ignore_index=True)
    df_combined.drop_duplicates(subset=["date", "keyword"], inplace=True)
    df_combined = df_combined.sort_values(["date", "keyword"]).reset_index(drop=True)

    # Save to file
    df_combined.to_csv(GLOBAL_TREND_PATH, index=False)
    print(f"✅ Appended data for {latest_available_date.date()} to global_trend_summary.csv")


# ─────────────────────────────────────────────────────────────
# FUNCTION: Remove stray launchd logs if present
# ─────────────────────────────────────────────────────────────

def clean_launchd_logs(log_dir: str):
    """
    Deletes unnecessary launchd log files if they exist.
    """
    for fname in ["launchd_stdout.log", "launchd_stderr.log"]:
        fpath = os.path.join(log_dir, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception as e:
                print(f"⚠️ Could not delete {fname}: {e}")
                
# ─────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if already_ran_today():
        print("⏳ Already ran today. Exiting.")
        sys.exit()

    update_global_trend_dataset()
    mark_today_as_ran()
    clean_launchd_logs(os.path.join("logs"))