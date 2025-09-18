# Purpose: Daily automation for Meditation Trend Pulse (Google Trends → CSVs).
# 
# Usage
# -----
# $ python update_all_datasets.py
# (Runs once per day; exits early if already ran today.)
# Outputs are written to ../data/streamlit.
#
# Updates the following datasets:
# - ✅ global_trend_summary.csv: weekly interest over time (Google Trends)
# - ✅ trend_pct_change.csv: 5-year percent change (only if global data updates)
# - ✅ trend_top_peaks.csv: top 3 peaks per keyword (only if global data updates)
# - ✅ country_interest_summary.csv: latest country-level interest (only if content has changed)
# - ✅ country_total_interest_by_keyword.csv: total interest by country & keyword (if country data updated)
# - ✅ country_top5_appearance_counts.csv: count of Top 5 appearances across keywords (if country data updated)
# - ✅ related_queries_top10.csv: Top 10 related queries for each keyword (only if global data updates)
# - ✅ related_queries_rising10.csv: Rising Top 10 related queries for each keyword (only if global data updates)
# - ✅ related_queries_shared.csv: Queries appearing under 2+ keywords (only if global data updates)
#
# Design notes:
# - Idempotent daily guard via .last_run_date
# - Network: bounded retries with exponential backoff + jitter
# - Content-aware writes where appropriate to reduce repo noise
# - Derived datasets recomputed only when their sources update

# ─────────────────────────────────────────────────────────────
# Standard library
# ─────────────────────────────────────────────────────────────
import os
import sys
import time
import random
import warnings
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# Third-party
# ─────────────────────────────────────────────────────────────
import pandas as pd
from pytrends.request import TrendReq

warnings.simplefilter(action="ignore", category=FutureWarning)

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

# Public keywords tracked by the dashboard (ordered for consistent output)
KEYWORDS: list[str] = [
    "meditation",
    "mindfulness",
    "breathwork",
    "guided meditation",
    "yoga nidra",
]

# Resolve paths relative to this file so cron/CLI both behave the same
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data", "streamlit"))

# CSV output paths (single source of truth)
GLOBAL_TREND_PATH = os.path.join(DATA_DIR, "global_trend_summary.csv")
TREND_PCT_PATH = os.path.join(DATA_DIR, "trend_pct_change.csv")
TREND_TOP_PEAKS_PATH = os.path.join(DATA_DIR, "trend_top_peaks.csv")
COUNTRY_TREND_PATH = os.path.join(DATA_DIR, "country_interest_summary.csv")
COUNTRY_TOTAL_INTEREST_PATH = os.path.join(DATA_DIR, "country_total_interest_by_keyword.csv")
COUNTRY_TOP5_COUNTS_PATH = os.path.join(DATA_DIR, "country_top5_appearance_counts.csv")
RELATED_TOP10_PATH = os.path.join(DATA_DIR, "related_queries_top10.csv")
RELATED_RISING10_PATH = os.path.join(DATA_DIR, "related_queries_rising10.csv")
RELATED_SHARED_PATH = os.path.join(DATA_DIR, "related_queries_shared.csv")
RUN_TRACK_FILE = os.path.join(SCRIPT_DIR, ".last_run_date")  # daily run guard

# Ensure output directory exists (safe if it already exists)
os.makedirs(DATA_DIR, exist_ok=True)

# Single pytrends client for the run
pytrends = TrendReq(
    hl="en-US",          # interface language
    tz=360,              # minutes offset (keep as-is to match dataset expectations)
    timeout=(15, 45),    # (connect, read) seconds
)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _today_str() -> str:
    """Return today's date (YYYY-MM-DD)."""
    return datetime.today().strftime("%Y-%m-%d")


def already_ran_today() -> bool:
    """True if the script has already run today (based on RUN_TRACK_FILE)."""
    if os.path.exists(RUN_TRACK_FILE):
        with open(RUN_TRACK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() == _today_str()
    return False


def mark_today_as_ran() -> None:
    """Record today's date to prevent duplicate daily runs."""
    with open(RUN_TRACK_FILE, "w", encoding="utf-8") as f:
        f.write(_today_str())


def _sleep_with_jitter(base: float) -> None:
    """Polite sleep to avoid hammering Google; adds small jitter."""
    time.sleep(base + random.uniform(0.1, 0.6))


def load_existing_or_empty(csv_path: str) -> pd.DataFrame:
    """Read a CSV if it exists; otherwise return an empty df with expected columns."""
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["date", "keyword", "search_interest"])
    return pd.read_csv(csv_path, parse_dates=["date"])

# ─────────────────────────────────────────────────────────────
# GLOBAL TRENDS + DERIVATIVES
# ─────────────────────────────────────────────────────────────

def pull_full_weekly_data(keywords: list[str]) -> pd.DataFrame:
    """
    Build one pytrends payload for all keywords over 'today 5-y' and return long df:
    columns = [date, keyword, search_interest]
    """
    max_attempts = 6
    for attempt in range(1, max_attempts + 1):
        try:
            pytrends.build_payload(keywords, timeframe="today 5-y", geo="")
            df_wide = pytrends.interest_over_time()
            if df_wide is None or df_wide.empty:
                raise RuntimeError("Empty dataframe from Google Trends")

            df_wide = df_wide.drop(columns=["isPartial"], errors="ignore").reset_index()
            df_long = (
                df_wide.melt(
                    id_vars=["date"],
                    value_vars=keywords,
                    var_name="keyword",
                    value_name="search_interest",
                )
                .dropna(subset=["date"])
            )
            df_long["date"] = pd.to_datetime(df_long["date"], errors="coerce")
            df_long = (
                df_long.dropna(subset=["date"])
                       .sort_values(["date", "keyword"])
                       .reset_index(drop=True)
            )
            return df_long
        except Exception as e:
            if attempt == max_attempts:
                print(f"❌ global weekly fetch: failed after {max_attempts} attempts ({e})")
                return pd.DataFrame(columns=["date", "keyword", "search_interest"])
            backoff = (2 ** attempt) * 0.6 + random.uniform(0, 0.8)
            print(f"⚠️  global weekly fetch: attempt {attempt}/{max_attempts} failed ({e}); retrying in {backoff:.1f}s...")
            time.sleep(backoff)


def write_trend_pct_change(df_long: pd.DataFrame) -> None:
    """
    Overwrite trend_pct_change.csv from the long global df:
    percent_change = (last - first) / first * 100 for each keyword.
    """
    if df_long.empty:
        return

    wide = (
        df_long.pivot(index="date", columns="keyword", values="search_interest")
              .sort_index()
    )
    filled = wide.ffill().bfill()
    first = filled.iloc[0]
    last = filled.iloc[-1]
    pct = ((last - first) / first) * 100.0

    out = (
        pct.rename("percent_change")
           .reset_index()
           .loc[:, ["keyword", "percent_change"]]
    )
    out["percent_change"] = out["percent_change"].round(2)
    out.to_csv(TREND_PCT_PATH, index=False)


def update_global_trend_dataset() -> bool:
    """Fetch weekly interest and write global_trend_summary.csv if a new week exists; rebuild pct change."""
    print("🔄 Updating global_trend_summary.csv...")
    df_full = pull_full_weekly_data(KEYWORDS)
    if df_full.empty:
        print("⚠️ No data retrieved from Google Trends. Keeping existing file unchanged.")
        return False

    df_existing = load_existing_or_empty(GLOBAL_TREND_PATH)
    if not df_existing.empty:
        last_existing = df_existing["date"].max()
        last_new = df_full["date"].max()
        if last_existing == last_new:
            print(f"⏭️ No new weekly data (latest date = {last_new.date()}). Skipping overwrite.")
            return False

    df_full.to_csv(GLOBAL_TREND_PATH, index=False)
    write_trend_pct_change(df_full)

    start = df_full["date"].min().date()
    end = df_full["date"].max().date()
    print(f"✅ Overwrote global_trend_summary.csv with window {start} → {end}")
    print("✅ Rebuilt trend_pct_change.csv")
    return True


def rebuild_trend_top_peaks() -> None:
    """From global_trend_summary.csv, write top 3 (by interest) per keyword → trend_top_peaks.csv."""
    if not os.path.exists(GLOBAL_TREND_PATH):
        print("⚠️ Cannot build top peaks: global_trend_summary.csv not found.")
        return

    df = pd.read_csv(GLOBAL_TREND_PATH, parse_dates=["date"])
    if df.empty:
        print("⚠️ Cannot build top peaks: global_trend_summary.csv is empty.")
        return

    df_top = (
        df.sort_values(["keyword", "search_interest"], ascending=[True, False])
          .groupby("keyword", as_index=False, sort=False)
          .head(3)
          .sort_values(["keyword", "search_interest"], ascending=[True, False])
          .reset_index(drop=True)
    )
    df_top.to_csv(TREND_TOP_PEAKS_PATH, index=False)
    print("✅ Rebuilt trend_top_peaks.csv")

# ─────────────────────────────────────────────────────────────
# COUNTRY DATASETS
# ─────────────────────────────────────────────────────────────

def update_country_interest_dataset() -> bool:
    """
    Pull region-level interest per keyword and update country_interest_summary.csv
    only if content changed.
    """
    print("🌍 Updating country_interest_summary.csv...")
    frames: list[pd.DataFrame] = []

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
        return False

    df_all = (
        pd.concat(frames, ignore_index=True)
          .drop_duplicates()
          .rename(columns={"search_interest": "interest"})
          .loc[:, ["country", "keyword", "interest"]]
    )

    if os.path.exists(COUNTRY_TREND_PATH):
        df_existing = pd.read_csv(COUNTRY_TREND_PATH)
        if df_existing.equals(df_all):
            print("⏭️ No change in country data. Skipping overwrite.")
            return False

    df_all.to_csv(COUNTRY_TREND_PATH, index=False)
    print(f"✅ Wrote {COUNTRY_TREND_PATH} with shape {df_all.shape}")
    return True


def update_country_total_interest_dataset() -> bool:
    """Build country_total_interest_by_keyword.csv from country_interest_summary.csv."""
    print("🌍 Building country_total_interest_by_keyword.csv...")
    if not os.path.exists(COUNTRY_TREND_PATH):
        print("⚠️ Cannot build total interest: country_interest_summary.csv not found.")
        return False

    df = pd.read_csv(COUNTRY_TREND_PATH)
    if df.empty:
        print("⚠️ country_interest_summary.csv is empty. Skipping.")
        return False

    df_total = (
        df.groupby(["country", "keyword"], as_index=False)
          .agg(total_interest=("interest", "sum"))
          .sort_values(["keyword", "total_interest"], ascending=[True, False])
    )
    df_total.to_csv(COUNTRY_TOTAL_INTEREST_PATH, index=False)
    print(f"✅ Wrote {COUNTRY_TOTAL_INTEREST_PATH} with shape {df_total.shape}")
    return True


def update_country_top5_counts_dataset() -> bool:
    """
    Write country_top5_appearance_counts.csv:
    how often a country appears in the top 5 per keyword by interest.
    """
    print("🌍 Building country_top5_appearance_counts.csv...")
    if not os.path.exists(COUNTRY_TREND_PATH):
        print("⚠️ Cannot build Top 5 counts: country_interest_summary.csv not found.")
        return False

    df = pd.read_csv(COUNTRY_TREND_PATH)
    if df.empty:
        print("⚠️ country_interest_summary.csv is empty. Skipping.")
        return False

    df["keyword"] = df["keyword"].astype(str).str.strip().str.lower()
    df["country"] = df["country"].astype(str).str.strip()

    df_top5 = (
        df.sort_values("interest", ascending=False)
          .groupby("keyword")
          .head(5)
          .groupby(["keyword", "country"])
          .size()
          .reset_index(name="top5_count")
    )
    df_top5.to_csv(COUNTRY_TOP5_COUNTS_PATH, index=False)
    print(f"✅ Wrote {COUNTRY_TOP5_COUNTS_PATH} with shape {df_top5.shape}")
    return True

# ─────────────────────────────────────────────────────────────
# RELATED QUERIES
# ─────────────────────────────────────────────────────────────

def fetch_all_related_queries() -> pd.DataFrame:
    """
    Fetch 'top' and 'rising' related queries for each keyword.
    Return columns: [keyword, related_query, query_type, popularity_score]
    """
    rows: list[dict] = []

    for kw in KEYWORDS:
        max_attempts = 6
        for attempt in range(1, max_attempts + 1):
            try:
                pytrends.build_payload([kw], timeframe="today 5-y", geo="")
                rq = pytrends.related_queries()  # dict: kw -> {'top': df, 'rising': df}
                bucket = rq.get(kw, {}) if isinstance(rq, dict) else {}

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
                        rows.extend(tmp.to_dict(orient="records"))
                break
            except Exception as e:
                if attempt == max_attempts:
                    print(f"❌ related_queries {kw}: failed after {max_attempts} attempts ({e})")
                else:
                    backoff = (2 ** attempt) * 0.5 + random.uniform(0, 0.8)
                    print(f"⚠️  related_queries {kw}: attempt {attempt}/{max_attempts} failed ({e}); retrying in {backoff:.1f}s...")
                    time.sleep(backoff)
        _sleep_with_jitter(0.5)

    if not rows:
        return pd.DataFrame(columns=["keyword", "related_query", "query_type", "popularity_score"])
    return pd.DataFrame(rows)


def update_related_queries_top10(df_all: pd.DataFrame | None = None) -> bool:
    """Write related_queries_top10.csv (top 10 by popularity from 'top' bucket) if changed."""
    print("🔎 Building related_queries_top10.csv...")
    if df_all is None:
        df_all = fetch_all_related_queries()
    if df_all.empty:
        print("⚠️ No related query data retrieved. Skipping file update.")
        return False

    df_top10 = (
        df_all[df_all["query_type"] == "top"]
        .sort_values(["keyword", "popularity_score"], ascending=[True, False])
        .groupby("keyword", as_index=False)
        .head(10)
        .reset_index(drop=True)
    )

    if os.path.exists(RELATED_TOP10_PATH):
        try:
            existing = pd.read_csv(RELATED_TOP10_PATH)
            if list(existing.columns) == list(df_top10.columns) and existing.equals(df_top10[existing.columns]):
                print("⏭️ No change in related top10 data. Skipping overwrite.")
                return False
        except Exception:
            pass

    df_top10.to_csv(RELATED_TOP10_PATH, index=False)
    print(f"✅ Wrote {RELATED_TOP10_PATH} with shape {df_top10.shape}")
    return True


def update_related_queries_rising10(df_all: pd.DataFrame) -> bool:
    """Write related_queries_rising10.csv (top 10 by popularity from 'rising' bucket) if changed."""
    print("🔎 Building related_queries_rising10.csv...")
    if df_all is None or df_all.empty:
        print("⚠️ No rising related query data retrieved. Skipping file update.")
        return False

    df_rising10 = (
        df_all[df_all["query_type"] == "rising"]
        .sort_values(["keyword", "popularity_score"], ascending=[True, False])
        .groupby("keyword", as_index=False)
        .head(10)
        .reset_index(drop=True)
    )

    if os.path.exists(RELATED_RISING10_PATH):
        try:
            existing = pd.read_csv(RELATED_RISING10_PATH)
            if list(existing.columns) == list(df_rising10.columns) and existing.equals(df_rising10[existing.columns]):
                print("⏭️ No change in related rising10 data. Skipping overwrite.")
                return False
        except Exception:
            pass

    df_rising10.to_csv(RELATED_RISING10_PATH, index=False)
    print(f"✅ Wrote {RELATED_RISING10_PATH} with shape {df_rising10.shape}")
    return True


def update_related_queries_shared(df_all: pd.DataFrame) -> bool:
    """
    Write related_queries_shared.csv with queries that appear under 2+ keywords.
    Schema: [keyword, related_query, query_type, popularity_score, num_keywords]
    """
    print("🔎 Building related_queries_shared.csv...")
    if df_all is None or df_all.empty:
        print("⚠️ No related query data available. Skipping file update.")
        return False

    shared_counts = (
        df_all.groupby("related_query")["keyword"]
              .nunique()
              .rename("num_keywords")
              .reset_index()
    )

    merged = (
        df_all.merge(shared_counts, on="related_query", how="inner")
              .sort_values(["num_keywords", "related_query", "keyword"], ascending=[False, True, True])
              .reset_index(drop=True)
    )

    out = merged.loc[merged["num_keywords"] >= 2,
                     ["keyword", "related_query", "query_type", "popularity_score", "num_keywords"]]

    if os.path.exists(RELATED_SHARED_PATH):
        try:
            existing = pd.read_csv(RELATED_SHARED_PATH)
            if list(existing.columns) == list(out.columns) and existing.equals(out[existing.columns]):
                print("⏭️ No change in related shared data. Skipping overwrite.")
                return False
        except Exception:
            pass

    out.to_csv(RELATED_SHARED_PATH, index=False)
    print(f"✅ Wrote {RELATED_SHARED_PATH} with shape {out.shape}")
    return True

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Explicit > implicit: exit early if we've already run today.
    if already_ran_today():
        print("⏳ Already ran today. Exiting.")
        sys.exit(0)

    try:
        # 1) Global data is the single source of truth for downstream work.
        updated = update_global_trend_dataset()

        if updated:
            # 2) Derived-from-global (local only, no extra network)
            rebuild_trend_top_peaks()

            # 3) Country data (may or may not change)
            country_updated = update_country_interest_dataset()
            if country_updated:
                update_country_total_interest_dataset()
                update_country_top5_counts_dataset()
            else:
                print("🛑 Skipping total interest update (no new country data).")

            # 4) Related queries (single fetch, three outputs)
            df_related_all = fetch_all_related_queries()
            if not df_related_all.empty:
                update_related_queries_top10(df_related_all)
                update_related_queries_rising10(df_related_all)
                update_related_queries_shared(df_related_all)
            else:
                print("⚠️ Skipping related queries: empty fetch.")
        else:
            # Flat is better than nested: make gates explicit and brief.
            print("🛑 Skipping country update (no new global data).")
            print("🛑 Skipping related update (no new global data).")

        # Record success for the daily guard, even if no files changed.
        mark_today_as_ran()

    except Exception as ex:
        # Errors should never pass silently.  (Unless explicitly silenced.)
        print(f"❌ Fatal error: {ex}")
        sys.exit(1)