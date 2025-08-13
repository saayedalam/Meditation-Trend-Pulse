"""
Global Trends Page — Meditation Trend Pulse
Shows interactive charts and tables of global search interest data from Google Trends.
"""

from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

from utils.data_loader import read_data_csv
from utils.ui import (
    inject_app_theme,
    page_header,
    render_card,
    space,
    horizontal_rule,
    render_section_header,
    render_section_card,
    render_centered_styled_table,
    style_percent_change,
    format_interest,
    render_custom_footer,
    CHAKRA_HEART,
)

# ─────────────────────────────────────────────────────────────
# Page setup and style injection
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Global Trends | Meditation Trend Pulse", layout="wide")
inject_app_theme()

# ─────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────
df_trend_long = read_data_csv("global_trend_summary.csv", parse_dates=["date"])
df_pct_change = read_data_csv("trend_pct_change.csv")
df_top_peaks  = read_data_csv("trend_top_peaks.csv")

df_trend_long["date"] = pd.to_datetime(df_trend_long["date"])

# ─────────────────────────────────────────────────────────────
# Page header + intro card
# ─────────────────────────────────────────────────────────────
page_header(
    title="📊 Global Trends in Meditation",
    subtitle="A worldwide view of mindfulness, breathwork, and inner stillness over time.",
)
space(1)

intro_html = """
🌐 This page reveals the global rhythm of search interest in meditation-related topics — including <strong>mindfulness</strong>, <strong>breathwork</strong>, and <strong>guided meditation</strong>.<br/><br/>
Built with data from <strong>Google Trends</strong>, it captures long-term growth, seasonal shifts, and spikes tied to cultural events, crises, and collective curiosity.<br/><br/>
🎯 <span style="color:#5B21B6; font-weight: 600;">Use the tools below to filter keywords, adjust time windows, and surface the stories hidden in the trends.</span><br/><br/>
🧘 <em>Whether you're a researcher, wellness coach, or mindful observer — this is your window into how the world is tuning inward.</em>
"""

render_card(
    title_html="Overview",
    body_html=intro_html,
    color_hex=CHAKRA_HEART,
    side="left",
    center=False,
)

space(2)

# ─────────────────────────────────────────────────────────────
# Section 1 — Global Interest Over Time
# ─────────────────────────────────────────────────────────────
render_section_header(
    title="Global Search Interest Over Time",
    emoji="📅",
    color_hex=CHAKRA_HEART,
)

render_section_card(
    icon="🧿",
    content_paragraph="This line chart illustrates how global interest in each keyword has evolved over time.",
    content_list=[
        "📈 See growth in mindfulness, breathwork, and related practices year by year.",
        "🌀 Spot seasonal patterns — such as New Year peaks or post-pandemic surges.",
        "🔍 Explore spikes tied to world events, news, or viral trends.",
        "💡 Use the filters below to explore specific keywords and time periods.",
    ],
    gradient_color=CHAKRA_HEART,
)

space()

with st.expander("🔧 Adjust Filters ", expanded=False):
    col1, col2 = st.columns([2, 2])

    with col1:
        keywords = df_trend_long["keyword"].unique().tolist()
        selected_keywords = st.multiselect("Select keywords:", keywords, default=keywords)

    with col2:
        min_date = df_trend_long["date"].min().date()
        max_date = df_trend_long["date"].max().date()
        date_range = st.slider(
            "Select Date Range:",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="MMM YYYY",
            key="date_slider_1",
        )

if not selected_keywords:
    st.warning("Please select at least one keyword to continue.")
else:
    df_filtered = df_trend_long[
        (df_trend_long["keyword"].isin(selected_keywords))
        & (df_trend_long["date"] >= pd.to_datetime(date_range[0]))
        & (df_trend_long["date"] <= pd.to_datetime(date_range[1]))
    ]

    total_by_keyword = df_filtered.groupby("keyword")["search_interest"].sum()
    top_keyword = total_by_keyword.idxmax()
    top_keyword_val = total_by_keyword.max()
    peak_interest = df_filtered["search_interest"].max()
    num_points = len(df_filtered)

    space()
    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Top Keyword", top_keyword, f"{top_keyword_val:.0f} total")
        col2.metric("📈 Peak Score", f"{peak_interest:.0f}")
        col3.metric("📊 Records", f"{num_points}")

    space()

    line_chart = (
        alt.Chart(df_filtered)
        .mark_line(interpolate="monotone")
        .encode(
            x=alt.X(
                "date:T",
                title="Date",
                scale=alt.Scale(nice="month"),
                axis=alt.Axis(format="%b %Y", labelAngle=0, labelOverlap=True),
            ),
            y=alt.Y("search_interest:Q", title="Search Interest"),
            color="keyword:N",
            tooltip=["date:T", "keyword:N", "search_interest:Q"],
        )
        .properties(height=420)
        .interactive(bind_y=False)
    )
    st.altair_chart(line_chart, use_container_width=True)
    space(2)
    horizontal_rule()

# ─────────────────────────────────────────────────────────────
# Section 2 — 5-Year % Change
# ─────────────────────────────────────────────────────────────
render_section_header(
    title="5-Year Growth or Decline by Search Term",
    emoji="📈",
    color_hex=CHAKRA_HEART,
)

render_section_card(
    icon="📋",
    content_paragraph="This table shows how global interest in each search term has changed over the past 5 years, based on Google Trends data.",
    content_list=[
        "🟢 <strong>Positive %</strong> means global interest increased.",
        "🔴 <strong>Negative %</strong> means global interest declined.",
        "💡 Use this view to identify which practices are gaining traction — and which are fading.",
    ],
    gradient_color=CHAKRA_HEART,
)

space()

df_pct_cleaned = df_pct_change.rename(
    columns={"keyword": "Search Term", "percent_change": "5-Year Change (%)"}
).copy()

df_pct_cleaned["5-Year Change (%)"] = df_pct_cleaned["5-Year Change (%)"].round(0).astype(int)
df_pct_cleaned = df_pct_cleaned.sort_values("5-Year Change (%)", ascending=False)

df_pct_styled = df_pct_cleaned.copy()
df_pct_styled["5-Year Change (%)"] = df_pct_styled["5-Year Change (%)"].apply(style_percent_change)

render_centered_styled_table(df_pct_styled.to_html(escape=False, index=False))

horizontal_rule()

# ─────────────────────────────────────────────────────────────
# Section 3 — Top Peak Dates by Keyword
# ─────────────────────────────────────────────────────────────
render_section_header(
    title="Top Peak Dates by Keyword",
    emoji="🌟",
    color_hex=CHAKRA_HEART,
)

render_section_card(
    icon="📅",
    content_paragraph="See when each keyword reached its highest level of global interest.",
    content_list=[
        "📆 Pinpoint cultural events or awareness weeks driving spikes.",
        "🌍 Spot time-specific behaviors in how people seek stillness.",
        "🧠 Great for insights, storytelling, or campaign planning.",
    ],
    gradient_color=CHAKRA_HEART,
)

space()

df_top_cleaned = df_top_peaks.rename(
    columns={"keyword": "Search Term", "date": "Peak Date", "search_interest": "Interest Score"}
).copy()

df_top_cleaned = df_top_cleaned.sort_values("Interest Score", ascending=False)
df_top_cleaned = df_top_cleaned.drop_duplicates(subset="Search Term", keep="first")

df_top_cleaned["Peak Date"] = pd.to_datetime(df_top_cleaned["Peak Date"]).dt.date

event_mapping = {
    "meditation": "🧘 New Year's Resolution Spike",
    "mindfulness": "🧠 Back-to-School + Wellness Push",
    "guided meditation": "🎧 Mid-Pandemic Anxiety Relief",
    "yoga nidra": "🛌 Winter Sleep Trends + TikTok Surge",
    "breathwork": "🌬️ New Year Recovery + Biohacking",
}
df_top_cleaned["Event"] = df_top_cleaned["Search Term"].map(event_mapping).fillna("—")

df_top_cleaned = df_top_cleaned[["Search Term", "Peak Date", "Event", "Interest Score"]]

styled_df = df_top_cleaned.style.map(format_interest, subset=["Interest Score"])

st.dataframe(styled_df, use_container_width=True, hide_index=True)

space()

# ─────────────────────────────────────────────────────────────
# Footer — Interest Score Explanation + last updated
# ─────────────────────────────────────────────────────────────
now = datetime.now().strftime("%B %d, %Y")
render_custom_footer(show_last_updated=now, color_hex=CHAKRA_HEART)
