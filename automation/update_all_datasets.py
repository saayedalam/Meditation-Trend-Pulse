"""
Script to update all datasets in the Meditation Trend Pulse project.
Currently updates:
- Global Trends dataset (global_trend_summary.csv)
- Percent change dataset (trend_pct_change.csv)

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
# Paths (always write into ../data/streamlit relative to this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data", "streamlit"))

GLOBAL_TREND_PATH = os.path.join(DATA_DIR, "global_trend_summary.csv")
TREND_PCT_PATH   = os.path.join(DATA_DIR, "trend_pct_change.csv") 
TREND_TOP_PEAKS_PATH = os.path.join(DATA_DIR, "trend_top_peaks.csv")
COUNTRY_TREND_PATH = os.path.join(DATA_DIR, "country_interest_summary.csv")
RUN_TRACK_FILE   = os.path.join(SCRIPT_DIR, ".last_run_date")

# Create data dir if missing
os.makedirs(DATA_DIR, exist_ok=True)

# Pytrends client with sane timeouts
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


def write_trend_pct_change(df_long: pd.DataFrame) -> None:
    """
    Build trend_pct_change.csv from the long global df (date, keyword, search_interest).
    % change = (last - first) / first * 100 for each keyword over the full 5-year window.
    """
    if df_long.empty:
        return

    wide = (
        df_long.pivot(index="date", columns="keyword", values="search_interest")
              .sort_index()
    )

    # Use forward/back fill to avoid leading NaN issues before first non-null.
    filled = wide.ffill().bfill()

    # First/last values by keyword across the 5-year window
    first = filled.iloc[0]
    last  = filled.iloc[-1]

    pct = ((last - first) / first) * 100.0
    out = (
        pct.rename("percent_change")
           .reset_index()
           .rename(columns={"keyword": "keyword"})
           .loc[:, ["keyword", "percent_change"]]
    )
    out["percent_change"] = out["percent_change"].round(2)
    out.to_csv(TREND_PCT_PATH, index=False)

# ─────────────────────────────────────────────────────────────
# TASK: Update datasets
# ─────────────────────────────────────────────────────────────

def update_global_trend_dataset() -> None:
    print("🔄 Updating global_trend_summary.csv...")

    # Pull a fresh 5‑year weekly window for all keywords
    df_full = pull_full_weekly_data(KEYWORDS)
    if df_full.empty:
        print("⚠️ No data retrieved from Google Trends. Keeping existing file unchanged.")
        return

    # Clean & order
    df_full = (
        df_full.dropna(subset=["date"])
               .sort_values(["date", "keyword"])
               .reset_index(drop=True)
    )

    # Load existing file to compare
    df_existing = load_existing_or_empty(GLOBAL_TREND_PATH)

    if not df_existing.empty:
        last_existing = df_existing["date"].max()
        last_new = df_full["date"].max()

        if last_existing == last_new:
            print(f"⏭️ No new weekly data (latest date = {last_new.date()}). Skipping overwrite.")
            return

    # OVERWRITE the file (only if new week is available)
    df_full.to_csv(GLOBAL_TREND_PATH, index=False)

    # NEW: also refresh the percent-change file
    write_trend_pct_change(df_full)

    start = df_full["date"].min().date()
    end   = df_full["date"].max().date()
    print(f"✅ Overwrote global_trend_summary.csv with window {start} → {end}")
    print(f"✅ Rebuilt trend_pct_change.csv")


def rebuild_trend_top_peaks() -> None:
    """
    Build top 3 peak rows per keyword from the current global_trend_summary.csv
    and save to trend_top_peaks.csv.
    """
    if not os.path.exists(GLOBAL_TREND_PATH):
        print("⚠️ Cannot build top peaks: global_trend_summary.csv not found.")
        return

    df = pd.read_csv(GLOBAL_TREND_PATH, parse_dates=["date"])
    if df.empty:
        print("⚠️ Cannot build top peaks: global_trend_summary.csv is empty.")
        return

    # Sort by keyword then descending interest, take top 3 per keyword
    df_top = (
        df.sort_values(["keyword", "search_interest"], ascending=[True, False])
          .groupby("keyword", as_index=False, sort=False)
          .head(3)
          .sort_values(["keyword", "search_interest"], ascending=[True, False])
          .reset_index(drop=True)
    )

    df_top.to_csv(TREND_TOP_PEAKS_PATH, index=False)
    print("✅ Rebuilt trend_top_peaks.csv")


def update_country_interest_dataset() -> None:
    """
    Pulls Google Trends region-level interest for each keyword over past 5 years.
    Cleans and combines into long-form country_interest_summary.csv
    """
    print("🌍 Updating country_interest_summary.csv...")

    frames = []

    for kw in KEYWORDS:
        try:
            pytrends.build_payload([kw], timeframe="today 5-y", geo="")
            df_region = pytrends.interest_by_region()

            if df_region.empty:
                continue

            df_kw = (
                df_region.reset_index()[["geoName", kw]]
                         .rename(columns={"geoName": "country", kw: "search_interest"})
                         .query("search_interest > 0")
                         .assign(keyword=kw)
            )
            frames.append(df_kw)
            _sleep_with_jitter(0.5)

        except Exception as e:
            print(f"⚠️ Skipped {kw} due to error: {e}")

    if not frames:
        print("⚠️ No country-level data retrieved. Skipping file update.")
        return

    df_all = pd.concat(frames, ignore_index=True)
    df_all = df_all.drop_duplicates()
    df_all = df_all[["country", "keyword", "search_interest"]]

    # 🔁 Rename to match Streamlit app expectations
    df_all = df_all.rename(columns={"search_interest": "interest"})

    df_all.to_csv(COUNTRY_TREND_PATH, index=False)
    print(f"✅ Wrote {COUNTRY_TREND_PATH} with shape {df_all.shape}")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if already_ran_today():
        print("⏳ Already ran today. Exiting.")
        sys.exit(0)

    try:
        update_global_trend_dataset()
        rebuild_trend_top_peaks()
        update_country_interest_dataset()  # ← ✅ Add this line
        mark_today_as_ran()
    except Exception as ex:
        print(f"❌ Fatal error: {ex}")
        sys.exit(1)