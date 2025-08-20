"""
Automation script for Meditation Trend Pulse data pipeline.

Updates the following datasets:
- ✅ global_trend_summary.csv: weekly interest over time (Google Trends)
- ✅ trend_pct_change.csv: 5-year percent change (only if global data updates)
- ✅ trend_top_peaks.csv: top 3 peaks per keyword (only if global data updates)
- ✅ country_interest_summary.csv: latest country-level interest (only if content has changed)
- ✅ country_total_interest_by_keyword.csv: total interest by country & keyword (if country data updated)
- ✅ country_top5_appearance_counts.csv: count of Top 5 appearances across keywords (if country data updated)
- ✅ related_queries_top10.csv: Top 10 related queries for each keyword (only if global data updates)
- ✅ related_queries_rising10.csv: Rising Top 10 related queries for each keyword (only if global data updates)
- ✅ related_queries_shared.csv: Queries appearing under 2+ keywords (only if global data updates)

⏳ Script is designed to run once per day. If already run today, it will exit.
"""

from __future__ import annotations  # allow forward type annotations (cleaner type hints in older Python)

# ─────────────────────────────────────────────────────────────
# Standard library imports
# ─────────────────────────────────────────────────────────────
import os  # filesystem paths and existence checks
import sys  # for clean process exit codes
import time  # sleeps/backoff
import random  # jitter for polite throttling
import warnings  # silence noisy library warnings
from datetime import datetime  # date stamp for run tracking
from typing import List  # typed KEYWORDS list

# ─────────────────────────────────────────────────────────────
# Third‑party imports
# ─────────────────────────────────────────────────────────────
import pandas as pd  # dataframe workhorse
from pytrends.request import TrendReq  # Google Trends client

# Reduce pandas future warnings to keep logs readable
warnings.simplefilter(action="ignore", category=FutureWarning)

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

# The five public keywords my dashboard tracks (ordered for consistent output)
KEYWORDS: List[str] = [
    "meditation",
    "mindfulness",
    "breathwork",
    "guided meditation",
    "yoga nidra",
]

# Resolve paths relative to this file so cron/CLI both work the same
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # folder containing this script
DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data", "streamlit"))  # all CSVs land here

# CSV output paths (one place to edit if I ever move files)
GLOBAL_TREND_PATH = os.path.join(DATA_DIR, "global_trend_summary.csv")
TREND_PCT_PATH = os.path.join(DATA_DIR, "trend_pct_change.csv")
TREND_TOP_PEAKS_PATH = os.path.join(DATA_DIR, "trend_top_peaks.csv")
COUNTRY_TREND_PATH = os.path.join(DATA_DIR, "country_interest_summary.csv")
COUNTRY_TOTAL_INTEREST_PATH = os.path.join(DATA_DIR, "country_total_interest_by_keyword.csv")
COUNTRY_TOP5_COUNTS_PATH = os.path.join(DATA_DIR, "country_top5_appearance_counts.csv")
RELATED_TOP10_PATH = os.path.join(DATA_DIR, "related_queries_top10.csv")
RELATED_RISING10_PATH = os.path.join(DATA_DIR, "related_queries_rising10.csv")
RELATED_SHARED_PATH = os.path.join(DATA_DIR, "related_queries_shared.csv")
RUN_TRACK_FILE = os.path.join(SCRIPT_DIR, ".last_run_date")  # simple run-once-per-day guard

# Ensure output directory exists (safe if it already exists)
os.makedirs(DATA_DIR, exist_ok=True)

# Create a single pytrends client for the whole run (reasonable timeouts)
pytrends = TrendReq(
    hl="en-US",   # interface language
    tz=360,       # timezone offset minutes (UTC-6 here aligns with dataset expectations)
    timeout=(15, 45),  # (connect timeout, read timeout) seconds
)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def already_ran_today() -> bool:
    """Return True if the script has already run today, based on the timestamp file."""
    # If tracking file exists, compare stored date string to today's date
    if os.path.exists(RUN_TRACK_FILE):
        with open(RUN_TRACK_FILE, "r", encoding="utf-8") as f:
            last_run = f.read().strip()
            return last_run == datetime.today().strftime("%Y-%m-%d")
    # No tracking file → hasn't run yet today
    return False


def mark_today_as_ran() -> None:
    """Update the run tracking file with today's date."""
    # Write today's YYYY-MM-DD into the guard file (idempotent if called again)
    with open(RUN_TRACK_FILE, "w", encoding="utf-8") as f:
        f.write(datetime.today().strftime("%Y-%m-%d"))


def _sleep_with_jitter(base: float) -> None:
    """Polite sleep to avoid hammering Google; adds small jitter."""
    # Sleep for a base + small random component to decorrelate requests
    time.sleep(base + random.uniform(0.1, 0.6))


def pull_full_weekly_data(keywords: List[str]) -> pd.DataFrame:
    """
    Single-call version:
    Builds one pytrends payload for ALL keywords at once (today 5-y),
    then returns a long df: [date, keyword, search_interest].
    """
    max_attempts = 6  # bounded retries for robustness
    for attempt in range(1, max_attempts + 1):
        try:
            # One payload for all KEYWORDS → fewer requests; consistent time window
            pytrends.build_payload(keywords, timeframe="today 5-y", geo="")
            df = pytrends.interest_over_time()  # returns wide df with one column per keyword
            if df is None or df.empty:
                raise RuntimeError("Empty dataframe from Google Trends")

            # Drop helper column if present; move 'date' back to a normal column
            df = df.drop(columns=["isPartial"], errors="ignore").reset_index()

            # Convert from wide to long → (date, keyword, search_interest)
            long_df = (
                df.melt(id_vars=["date"], value_vars=keywords,
                        var_name="keyword", value_name="search_interest")
                  .dropna(subset=["date"])
            )

            # Ensure date column is datetime and rows are clean/sorted
            long_df["date"] = pd.to_datetime(long_df["date"], errors="coerce")
            long_df = (
                long_df.dropna(subset=["date"])
                       .sort_values(["date", "keyword"])
                       .reset_index(drop=True)
            )
            return long_df  # success path

        except Exception as e:
            # Out of retries → return empty and log terminal failure
            if attempt == max_attempts:
                print(f"❌ global weekly fetch: failed after {max_attempts} attempts ({e})")
                return pd.DataFrame(columns=["date", "keyword", "search_interest"])
            # Otherwise backoff and retry
            backoff = (2 ** attempt) * 0.6 + random.uniform(0, 0.8)
            print(f"⚠️  global weekly fetch: attempt {attempt}/{max_attempts} failed ({e}); retrying in {backoff:.1f}s...")
            time.sleep(backoff)


def load_existing_or_empty(csv_path: str) -> pd.DataFrame:
    """Read a CSV if it exists; otherwise return an empty df with expected columns."""
    # If file is missing → return expected schema so downstream comparisons don't break
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["date", "keyword", "search_interest"])
    # Parse 'date' column as datetime for consistent comparisons
    return pd.read_csv(csv_path, parse_dates=["date"])


def write_trend_pct_change(df_long: pd.DataFrame) -> None:
    """
    Build trend_pct_change.csv from the long global df (date, keyword, search_interest).
    % change = (last - first) / first * 100 for each keyword over the full 5-year window.
    """
    # If no data, there's nothing to compute
    if df_long.empty:
        return

    # Pivot to wide so I can compare first vs last value per keyword
    wide = (
        df_long.pivot(index="date", columns="keyword", values="search_interest")
              .sort_index()
    )

    # Fill internal gaps so the first/last row are defined for each keyword
    filled = wide.ffill().bfill()

    # Extract first row (start of window) and last row (end of window)
    first = filled.iloc[0]
    last = filled.iloc[-1]

    # Compute percentage change across the whole window
    pct = ((last - first) / first) * 100.0

    # Normalize to (keyword, percent_change) and round for readability
    out = (
        pct.rename("percent_change")
           .reset_index()
           .rename(columns={"keyword": "keyword"})
           .loc[:, ["keyword", "percent_change"]]
    )
    out["percent_change"] = out["percent_change"].round(2)

    # Overwrite the CSV (this is derived, so no gate needed)
    out.to_csv(TREND_PCT_PATH, index=False)

# ─────────────────────────────────────────────────────────────
# TASK: Update datasets (global + derived + country + related)
# ─────────────────────────────────────────────────────────────

def update_global_trend_dataset() -> bool:
    """Fetch 5-year weekly interest for all keywords and write to global_trend_summary.csv if new week arrived."""
    print("🔄 Updating global_trend_summary.csv...")

    # Pull one long dataframe for all keywords at once
    df_full = pull_full_weekly_data(KEYWORDS)
    if df_full.empty:
        print("⚠️ No data retrieved from Google Trends. Keeping existing file unchanged.")
        return False  # nothing to do

    # Ensure dates are clean and rows are sorted predictably
    df_full = (
        df_full.dropna(subset=["date"])
               .sort_values(["date", "keyword"])
               .reset_index(drop=True)
    )

    # Compare the last available date to detect a fresh weekly update
    df_existing = load_existing_or_empty(GLOBAL_TREND_PATH)
    if not df_existing.empty:
        last_existing = df_existing["date"].max()
        last_new = df_full["date"].max()
        if last_existing == last_new:
            print(f"⏭️ No new weekly data (latest date = {last_new.date()}). Skipping overwrite.")
            return False  # gate everything downstream

    # New week present → write the file and rebuild % change
    df_full.to_csv(GLOBAL_TREND_PATH, index=False)
    write_trend_pct_change(df_full)

    # Log the new window for visibility in logs
    start = df_full["date"].min().date()
    end = df_full["date"].max().date()
    print(f"✅ Overwrote global_trend_summary.csv with window {start} → {end}")
    print(f"✅ Rebuilt trend_pct_change.csv")
    return True  # signal: global updated


def rebuild_trend_top_peaks() -> None:
    """
    Build top 3 peak rows per keyword from the current global_trend_summary.csv
    and save to trend_top_peaks.csv.
    """
    # If global df is missing or empty → there's nothing to rank
    if not os.path.exists(GLOBAL_TREND_PATH):
        print("⚠️ Cannot build top peaks: global_trend_summary.csv not found.")
        return

    df = pd.read_csv(GLOBAL_TREND_PATH, parse_dates=["date"])
    if df.empty:
        print("⚠️ Cannot build top peaks: global_trend_summary.csv is empty.")
        return

    # Sort by keyword then by interest descending, and take top 3 per keyword
    df_top = (
        df.sort_values(["keyword", "search_interest"], ascending=[True, False])
          .groupby("keyword", as_index=False, sort=False)
          .head(3)
          .sort_values(["keyword", "search_interest"], ascending=[True, False])
          .reset_index(drop=True)
    )

    # Persist as a simple CSV consumed by the app
    df_top.to_csv(TREND_TOP_PEAKS_PATH, index=False)
    print("✅ Rebuilt trend_top_peaks.csv")


def update_country_interest_dataset() -> bool:
    """
    Pulls Google Trends region-level interest for each keyword over past 5 years.
    Cleans and combines into long-form country_interest_summary.csv.
    Only writes if the data has changed.
    """
    print("🌍 Updating country_interest_summary.csv...")

    frames = []  # accumulate one df per keyword

    # Query regions per keyword (pytrends API requires per-keyword builds here)
    for kw in KEYWORDS:
        try:
            pytrends.build_payload([kw], timeframe="today 5-y", geo="")  # build payload for this keyword
            df_region = pytrends.interest_by_region()  # region-level interest (wide df)
            if df_region.empty:
                continue  # skip empties quietly

            # Normalize to (country, keyword, search_interest) rows and drop zero rows
            df_kw = (
                df_region.reset_index()[["geoName", kw]]
                         .rename(columns={"geoName": "country", kw: "search_interest"})
                         .query("search_interest > 0")
                         .assign(keyword=kw)
            )
            frames.append(df_kw)  # collect cleaned block
            _sleep_with_jitter(0.5)  # be polite between requests

        except Exception as e:
            # On error for this keyword, log and move on — others may still succeed
            print(f"⚠️ Skipped {kw} due to error: {e}")

    # If we got nothing for all keywords → don't overwrite existing file
    if not frames:
        print("⚠️ No country-level data retrieved. Skipping file update.")
        return False

    # Combine all keywords, drop duplicates, and rename to 'interest' for app clarity
    df_all = pd.concat(frames, ignore_index=True)
    df_all = df_all.drop_duplicates()
    df_all = df_all[["country", "keyword", "search_interest"]]
    df_all = df_all.rename(columns={"search_interest": "interest"})

    # If content is identical to the existing file → skip write to avoid Git noise
    if os.path.exists(COUNTRY_TREND_PATH):
        df_existing = pd.read_csv(COUNTRY_TREND_PATH)
        if df_existing.equals(df_all):
            print("⏭️ No change in country data. Skipping overwrite.")
            return False

    # Content changed → write the file
    df_all.to_csv(COUNTRY_TREND_PATH, index=False)
    print(f"✅ Wrote {COUNTRY_TREND_PATH} with shape {df_all.shape}")
    return True  # signal: country data changed


def update_country_total_interest_dataset() -> bool:
    """
    Builds a dataset that sums country-level interest by keyword.
    Only runs if COUNTRY_TREND_PATH has changed (and exists).
    """
    print("🌍 Building country_total_interest_by_keyword.csv...")

    # Guard: need the base country dataset to exist
    if not os.path.exists(COUNTRY_TREND_PATH):
        print("⚠️ Cannot build total interest: country_interest_summary.csv not found.")
        return False

    # Load the latest country interest file
    df = pd.read_csv(COUNTRY_TREND_PATH)
    if df.empty:
        print("⚠️ country_interest_summary.csv is empty. Skipping.")
        return False

    # Group by (country, keyword) and sum interest
    df_total = (
        df.groupby(["country", "keyword"], as_index=False)
          .agg(total_interest=("interest", "sum"))
          .sort_values(["keyword", "total_interest"], ascending=[True, False])
    )

    # Write derived dataset
    df_total.to_csv(COUNTRY_TOTAL_INTEREST_PATH, index=False)
    print(f"✅ Wrote {COUNTRY_TOTAL_INTEREST_PATH} with shape {df_total.shape}")
    return True


def update_country_top5_counts_dataset() -> bool:
    """
    Builds dataset of countries that appear most frequently in the Top 5 
    (by interest) across keywords. Based on country_interest_summary.csv.
    """
    print("🌍 Building country_top5_appearance_counts.csv...")

    # Require base file
    if not os.path.exists(COUNTRY_TREND_PATH):
        print("⚠️ Cannot build Top 5 counts: country_interest_summary.csv not found.")
        return False

    # Load and guard against empties
    df = pd.read_csv(COUNTRY_TREND_PATH)
    if df.empty:
        print("⚠️ country_interest_summary.csv is empty. Skipping.")
        return False

    # Normalize text columns to avoid subtle grouping bugs
    df["keyword"] = df["keyword"].astype(str).str.strip().str.lower()
    df["country"] = df["country"].astype(str).str.strip()

    # For each keyword, take the top 5 rows by interest; then count country occurrences
    df_top5 = (
        df.sort_values("interest", ascending=False)
          .groupby("keyword")
          .head(5)
          .groupby(["keyword", "country"])
          .size()
          .reset_index(name="top5_count")
    )

    # Persist derived dataset
    df_top5.to_csv(COUNTRY_TOP5_COUNTS_PATH, index=False)
    print(f"✅ Wrote {COUNTRY_TOP5_COUNTS_PATH} with shape {df_top5.shape}")
    return True


def fetch_all_related_queries() -> pd.DataFrame:
    """
    Returns a DataFrame with columns:
    [keyword, related_query, query_type, popularity_score]
    Aggregates both 'top' and 'rising' buckets for each keyword with retries.
    """
    rows = []  # collected normalized rows for all keywords

    # pytrends related_queries requires per-keyword fetches
    for kw in KEYWORDS:
        max_attempts = 6  # bound retries to avoid infinite loops
        for attempt in range(1, max_attempts + 1):
            try:
                pytrends.build_payload([kw], timeframe="today 5-y", geo="")  # build request for this keyword
                rq = pytrends.related_queries()  # returns dict keyed by keyword → {top: df, rising: df}
                bucket = rq.get(kw, {}) if isinstance(rq, dict) else {}  # safe get

                # Normalize 'top' and 'rising' buckets into long rows
                for qtype in ("top", "rising"):
                    df_q = bucket.get(qtype) if isinstance(bucket, dict) else None
                    if isinstance(df_q, pd.DataFrame) and not df_q.empty:
                        tmp = (
                            df_q.dropna(subset=["query"])
                                .assign(
                                    keyword=kw,
                                    related_query=lambda d: d["query"].astype(str).str.strip(),
                                    query_type=qtype,
                                    popularity_score=pd.to_numeric(df_q.get("value", pd.Series(dtype=float)), errors="coerce"),
                                )[["keyword", "related_query", "query_type", "popularity_score"]]
                                .drop_duplicates(subset=["keyword", "related_query", "query_type"])
                        )
                        rows.extend(tmp.to_dict(orient="records"))  # accumulate normalized records
                break  # success for this kw → stop retrying
            except Exception as e:
                # Final failure → log and move on to next keyword
                if attempt == max_attempts:
                    print(f"❌ related_queries {kw}: failed after {max_attempts} attempts ({e})")
                else:
                    # Retry later with exponential backoff + jitter
                    backoff = (2 ** attempt) * 0.5 + random.uniform(0, 0.8)
                    print(f"⚠️  related_queries {kw}: attempt {attempt}/{max_attempts} failed ({e}); retrying in {backoff:.1f}s...")
                    time.sleep(backoff)
        _sleep_with_jitter(0.5)  # politeness gap between keywords

    # If nothing collected → return a correctly-shaped empty df
    if not rows:
        return pd.DataFrame(columns=["keyword", "related_query", "query_type", "popularity_score"])
    # Otherwise build a dataframe from all rows
    return pd.DataFrame(rows)


def update_related_queries_top10(df_all: pd.DataFrame | None = None) -> bool:
    """Build Dataset 1 — related_queries_top10.csv (can reuse provided df_all)."""
    print("🔎 Building related_queries_top10.csv...")
    # If caller didn't pass the combined df, fetch once here
    if df_all is None:
        df_all = fetch_all_related_queries()
    # If fetch failed/empty → do not overwrite existing file
    if df_all.empty:
        print("⚠️ No related query data retrieved. Skipping file update.")
        return False

    # For each keyword, take top 10 rows by popularity_score from the 'top' bucket
    df_top10 = (
        df_all[df_all["query_type"] == "top"]
        .sort_values(["keyword", "popularity_score"], ascending=[True, False])
        .groupby("keyword", as_index=False)
        .head(10)
        .reset_index(drop=True)
    )

    # If file exists and content hasn't changed → skip overwrite (avoid Git noise)
    if os.path.exists(RELATED_TOP10_PATH):
        try:
            existing = pd.read_csv(RELATED_TOP10_PATH)
            if list(existing.columns) == list(df_top10.columns) and existing.equals(df_top10[existing.columns]):
                print("⏭️ No change in related top10 data. Skipping overwrite.")
                return False
        except Exception:
            # If comparison fails for any reason, fall through and overwrite
            pass

    # Persist dataset
    df_top10.to_csv(RELATED_TOP10_PATH, index=False)
    print(f"✅ Wrote {RELATED_TOP10_PATH} with shape {df_top10.shape}")
    return True


def update_related_queries_rising10(df_all: pd.DataFrame) -> bool:
    """Build Dataset 2 — related_queries_rising10.csv (requires df_all from the same fetch)."""
    print("🔎 Building related_queries_rising10.csv...")
    # Require the combined df (built once) to avoid an extra network call
    if df_all is None or df_all.empty:
        print("⚠️ No rising related query data retrieved. Skipping file update.")
        return False

    # For each keyword, take top 10 rows by popularity_score from the 'rising' bucket
    df_rising10 = (
        df_all[df_all["query_type"] == "rising"]
        .sort_values(["keyword", "popularity_score"], ascending=[True, False])
        .groupby("keyword", as_index=False)
        .head(10)
        .reset_index(drop=True)
    )

    # Skip write if nothing changed
    if os.path.exists(RELATED_RISING10_PATH):
        try:
            existing = pd.read_csv(RELATED_RISING10_PATH)
            if list(existing.columns) == list(df_rising10.columns) and existing.equals(df_rising10[existing.columns]):
                print("⏭️ No change in related rising10 data. Skipping overwrite.")
                return False
        except Exception:
            pass

    # Persist dataset
    df_rising10.to_csv(RELATED_RISING10_PATH, index=False)
    print(f"✅ Wrote {RELATED_RISING10_PATH} with shape {df_rising10.shape}")
    return True


def update_related_queries_shared(df_all: pd.DataFrame) -> bool:
    """
    Build Dataset 3 — related_queries_shared.csv from the already-fetched df_all.
    Schema: [keyword, related_query, query_type, popularity_score, num_keywords]
    Only writes if content changed.
    """
    print("🔎 Building related_queries_shared.csv...")
    # Require combined df; if missing/empty, skip
    if df_all is None or df_all.empty:
        print("⚠️ No related query data available. Skipping file update.")
        return False

    # Count distinct keywords per related_query to identify "shared" queries
    shared_counts = (
        df_all.groupby("related_query")["keyword"]
              .nunique()
              .rename("num_keywords")
              .reset_index()
    )

    # Merge counts back to full rows, sort by (num_keywords desc, query asc, keyword asc)
    merged = (
        df_all.merge(shared_counts, on="related_query", how="inner")
              .sort_values(by=["num_keywords", "related_query", "keyword"], ascending=[False, True, True])
              .reset_index(drop=True)
    )

    # Keep only queries that appear under 2+ keywords to match the dashboard behavior
    out = (
        merged.loc[merged["num_keywords"] >= 2,
                   ["keyword", "related_query", "query_type", "popularity_score", "num_keywords"]]
    )

    # If file exists and content unchanged → skip overwrite
    if os.path.exists(RELATED_SHARED_PATH):
        try:
            existing = pd.read_csv(RELATED_SHARED_PATH)
            if list(existing.columns) == list(out.columns) and existing.equals(out[existing.columns]):
                print("⏭️ No change in related shared data. Skipping overwrite.")
                return False
        except Exception:
            pass

    # Persist dataset
    out.to_csv(RELATED_SHARED_PATH, index=False)
    print(f"✅ Wrote {RELATED_SHARED_PATH} with shape {out.shape}")
    return True

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Daily run-once guard: exit early if we already ran today
    if already_ran_today():
        print("⏳ Already ran today. Exiting.")
        sys.exit(0)

    try:
        # Step 1: Attempt to refresh the global weekly dataset
        updated = update_global_trend_dataset()

        if updated:
            # Step 2a: Rebuild peaks from local global CSV (no extra network)
            rebuild_trend_top_peaks()

            # Step 2b: Update country-level dataset (may or may not change)
            country_updated = update_country_interest_dataset()

            # Step 2c: If country file changed, rebuild its derivatives
            if country_updated:
                update_country_total_interest_dataset()
                update_country_top5_counts_dataset()
            else:
                print("🛑 Skipping total interest update (no new country data).")

            # Step 3: Build all related query datasets from a single fetch
            df_related_all = fetch_all_related_queries()
            if not df_related_all.empty:
                update_related_queries_top10(df_related_all)
                update_related_queries_rising10(df_related_all)
                update_related_queries_shared(df_related_all)
            else:
                print("⚠️ Skipping related queries: empty fetch.")
        else:
            # If global didn't update, everything downstream is intentionally skipped
            print("🛑 Skipping country update (no new global data).")
            print("🛑 Skipping related update (no new global data).")

        # Mark that we ran today (even if nothing updated) to avoid repeated cron work
        mark_today_as_ran()

    except Exception as ex:
        # Any unhandled error → log and return a non-zero exit for cron visibility
        print(f"❌ Fatal error: {ex}")
        sys.exit(1)