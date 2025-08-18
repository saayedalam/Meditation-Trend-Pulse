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

from __future__ import annotations

import os
import sys
import time
import random
import warnings
from datetime import datetime
from typing import List

import pandas as pd
from pytrends.request import TrendReq

warnings.simplefilter(action="ignore", category=FutureWarning)

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

KEYWORDS: List[str] = [
    "meditation",
    "mindfulness",
    "breathwork",
    "guided meditation",
    "yoga nidra",
]

# Resolve paths robustly:
# - Prefer env var MTP_DATA_DIR if set
# - Otherwise use ../data/streamlit relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data", "streamlit"))
DATA_DIR = os.environ.get("MTP_DATA_DIR", DEFAULT_DATA_DIR)

GLOBAL_TREND_PATH = os.path.join(DATA_DIR, "global_trend_summary.csv")
RUN_TRACK_FILE = os.path.join(SCRIPT_DIR, ".last_run_date")

# Create data dir if missing
os.makedirs(DATA_DIR, exist_ok=True)

# Pytrends client with sane timeouts + built-in retry/backoff
pytrends = TrendReq(
    hl="en-US",
    tz=360,
    timeout=(15, 45),  # (connect, read) seconds
)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def already_ran_today() -> bool:
    """Return True if the script has already run today, based on the timestamp file."""
    if os.path.exists(RUN_TRACK_FILE):
        with open(RUN_TRACK_FILE, "r", encoding="utf-8") as f:
            last_run = f.read().strip()
            return last_run == datetime.today().strftime("%Y-%m-%d")
    return False


def mark_today_as_ran() -> None:
    """Update the run tracking file with today's date."""
    with open(RUN_TRACK_FILE, "w", encoding="utf-8") as f:
        f.write(datetime.today().strftime("%Y-%m-%d"))


def _sleep_with_jitter(base: float) -> None:
    """Polite sleep to avoid hammering Google; adds small jitter."""
    time.sleep(base + random.uniform(0.1, 0.6))


def fetch_interest_over_time_single_keyword(kw: str, timeframe: str = "today 5-y") -> pd.DataFrame:
    """
    Robust fetch for a single keyword with manual retries around the pytrends call.
    Returns a 3-col DataFrame: [date, keyword, search_interest] or empty df on failure.
    """
    max_attempts = 6
    for attempt in range(1, max_attempts + 1):
        try:
            pytrends.build_payload([kw], timeframe=timeframe)
            df = pytrends.interest_over_time()

            if df is None or df.empty:
                raise RuntimeError("Empty dataframe from Google Trends")

            out = (
                df.reset_index()[["date", kw]]
                  .rename(columns={kw: "search_interest"})
                  .assign(keyword=kw)[["date", "keyword", "search_interest"]]
            )
            return out

        except Exception as e:
            if attempt == max_attempts:
                print(f"❌ {kw}: failed after {max_attempts} attempts ({e})")
                return pd.DataFrame(columns=["date", "keyword", "search_interest"])

            backoff = (2 ** attempt) * 0.6 + random.uniform(0, 0.8)
            print(f"⚠️  {kw}: attempt {attempt}/{max_attempts} failed ({e}); retrying in {backoff:.1f}s...")
            time.sleep(backoff)


def pull_full_weekly_data(keywords: List[str]) -> pd.DataFrame:
    """
    Pulls 5 years of weekly data for all keywords (robust).
    Returns a long df: [date, keyword, search_interest]
    """
    frames = []
    for kw in keywords:
        df = fetch_interest_over_time_single_keyword(kw, timeframe="today 5-y")
        if not df.empty:
            frames.append(df)
        _sleep_with_jitter(0.5)  # be polite between keywords

    if not frames:
        return pd.DataFrame(columns=["date", "keyword", "search_interest"])

    out = pd.concat(frames, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date"]).sort_values(["date", "keyword"])
    return out


def load_existing_or_empty(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["date", "keyword", "search_interest"])
    return pd.read_csv(csv_path, parse_dates=["date"])


# ─────────────────────────────────────────────────────────────
# TASK: Update global_trend_summary.csv (latest Sunday only)
# ─────────────────────────────────────────────────────────────

def update_global_trend_dataset() -> None:
    print("🔄 Updating global_trend_summary.csv...")

    df_existing = load_existing_or_empty(GLOBAL_TREND_PATH)
    latest_existing_date = pd.Timestamp.min if df_existing.empty else df_existing["date"].max()

    df_full = pull_full_weekly_data(KEYWORDS)
    if df_full.empty:
        print("⚠️ No data retrieved from Google Trends. Keeping existing file unchanged.")
        return

    latest_available_date = df_full["date"].max()
    df_latest = df_full[df_full["date"] == latest_available_date]

    if latest_available_date <= latest_existing_date:
        print(f"🔁 Replacing data for {latest_available_date.date()} (Google may revise weekly values).")
        df_existing = df_existing[df_existing["date"] != latest_available_date]
    else:
        print(f"➕ Appending new week: {latest_available_date.date()}")

    df_combined = (
        pd.concat([df_existing, df_latest], ignore_index=True)
          .sort_values(["date", "keyword"])
          .reset_index(drop=True)
    )

    df_combined.to_csv(GLOBAL_TREND_PATH, index=False)
    print(f"✅ global_trend_summary.csv updated with {latest_available_date.date()}")



# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if already_ran_today():
        print("⏳ Already ran today. Exiting.")
        sys.exit(0)

    try:
        update_global_trend_dataset()
        mark_today_as_ran()
    except Exception as ex:
        # Non-zero exit helps schedulers alert you
        print(f"❌ Fatal error: {ex}")
        sys.exit(1)