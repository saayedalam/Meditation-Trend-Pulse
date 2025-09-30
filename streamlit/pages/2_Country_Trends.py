# 🌍 Country Trends Page — Meditation Trend Pulse

import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

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
    render_custom_footer,
    CHAKRA_THROAT,
    get_flag_emoji,
)

# ─────────────────────────────────────────────────────────────
# Page config and global style injection
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Country Trends | Meditation Trend Pulse", layout="wide")
inject_app_theme()

# ─────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────
df_country = read_data_csv("country_interest_summary.csv")
df_total   = read_data_csv("country_total_interest_by_keyword.csv")
df_top5    = read_data_csv("country_top5_appearance_counts.csv")
df_trend_long = read_data_csv("global_trend_summary.csv", parse_dates=["date"])
df_trend_long["date"] = pd.to_datetime(df_trend_long["date"])

# ─────────────────────────────────────────────────────────────
# Page header + intro card
# ─────────────────────────────────────────────────────────────
page_header(
    title="Country-Level Meditation Trends",
    subtitle="A calming look into how the world connects through stillness, breath, and awareness",
)
space(1)

intro_html = """
🧘‍♀️ This page explores how people across the globe are turning to <strong>meditation, mindfulness, breathwork,</strong> and related practices — not just as trends, but as tools for peace and clarity.<br/><br/>
Sourced from <strong>Google Trends</strong> and updated weekly, this dashboard helps you discover which countries are most engaged with these practices — and how interest is evolving over time.<br/><br/>
🌐 <span style="color:#5B21B6; font-weight: 600;">Use the filters to explore <strong>top countries by search volume</strong>, view keyword-level breakdowns, and uncover meaningful regional patterns.</span><br/><br/>
💡 <em>Whether you're a teacher, entrepreneur, researcher, or simply curious — this tool gives you a peaceful window into global interest in stillness and self-awareness.</em>
"""

render_card(
    title_html="Overview",
    body_html=intro_html,
    color_hex=CHAKRA_THROAT,
    side="left",
    center=False,
)
space(2)

# ─────────────────────────────────────────────────────────────
# Section 1 — Top Countries by Interest
# ─────────────────────────────────────────────────────────────
render_section_header(
    title="Top Countries by Interest",
    emoji="🏆",
    color_hex=CHAKRA_THROAT,
)

render_section_card(
    icon="🌍",
    content_paragraph="This bar chart highlights countries showing the strongest interest in your selected meditation keywords.",
    content_list=[
        "🔢 Choose how many countries to view — top 10, 25, or 50 — using the filter below.",
        "🎯 Each bar is grouped by keyword so you can compare interest patterns globally.",
        "📊 Hover to view total interest and % contribution to global totals.",
    ],
    gradient_color=CHAKRA_THROAT,
)
space()

with st.expander("🔧 Adjust Filters", expanded=False):
    col1, col2 = st.columns([2, 1])
    with col1:
        keywords = df_country["keyword"].unique().tolist()
        selected_keywords = st.multiselect("Select keywords:", keywords, default=keywords[:1])
    with col2:
        top_n_choice = st.radio("Top N countries:", options=[10, 25, 50], index=1, horizontal=True)

if not selected_keywords:
    st.warning("Please select at least one keyword to display country interest trends.")
else:
    df_filtered = df_country[df_country["keyword"].isin(selected_keywords)]

    top_keyword = df_filtered.groupby("keyword")["interest"].sum().idxmax()
    top_value = df_filtered.groupby("keyword")["interest"].sum().max()
    peak_interest = df_filtered["interest"].max()
    num_rows = len(df_filtered)

    space()
    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Top Keyword", f"{top_keyword}", f"{top_value:.0f} total")
        col2.metric("📈 Peak Score", f"{peak_interest:.0f}")
        col3.metric("📊 Records", f"{num_rows}")
    space()

    df_ranked = df_filtered.groupby(["country", "keyword"], as_index=False)["interest"].sum()
    df_ranked["percent_of_keyword"] = df_ranked.groupby("keyword")["interest"].transform(lambda x: (x / x.sum()) * 100)

    country_order = (
        df_ranked.groupby("country", as_index=False)["interest"].sum()
        .sort_values("interest", ascending=False)
        .head(top_n_choice)["country"]
        .tolist()
    )
    df_topn = df_ranked[df_ranked["country"].isin(country_order)]

    bar_chart = alt.Chart(df_topn).mark_bar().encode(
        x=alt.X("country:N", sort=country_order, title="Country"),
        y=alt.Y("interest:Q", title="Search Interest"),
        color=alt.Color("keyword:N", title="Keyword"),
        tooltip=[
            alt.Tooltip("country:N", title="Country"),
            alt.Tooltip("keyword:N", title="Keyword"),
            alt.Tooltip("interest:Q", title="Interest"),
            alt.Tooltip("percent_of_keyword:Q", title="% of Global Keyword Interest", format=".1f"),
        ],
    ).properties(height=500)

    #st.altair_chart(bar_chart, use_container_width=True) ##depecreated
    st.altair_chart(bar_chart, use_container_width="stretch")
    space()
    horizontal_rule()

# ─────────────────────────────────────────────────────────────
# Section 2 — Global Totals by Country & Keyword
# ─────────────────────────────────────────────────────────────
render_section_header(
    title="Global Totals by Country & Keyword",
    emoji="📊",
    color_hex=CHAKRA_THROAT,
)

render_section_card(
    icon="📦",
    content_paragraph="This table shows total search interest for each keyword in each country across the full dataset.",
    content_list=[
        "🔍 Great for exports or precise filtering by analysts and researchers.",
    ],
    gradient_color=CHAKRA_THROAT,
)
space()

df_total_cleaned = df_total.rename(
    columns={
        "country": "Country",
        "keyword": "Keyword",
        "total_interest": "Total Interest",
    }
)
df_total_cleaned["Total Interest"] = pd.to_numeric(df_total_cleaned["Total Interest"], errors="coerce")

column_config = {
    "Country": st.column_config.TextColumn(label="Country"),
    "Keyword": st.column_config.TextColumn(label="Keyword"),
    "Total Interest": st.column_config.NumberColumn(label="Total Interest"),
}

# ##depecreated
# st.data_editor(
#     df_total_cleaned,
#     column_config=column_config,
#     use_container_width=True,
#     hide_index=True,
#     disabled=True,
# )

st.data_editor(
    df_total_cleaned,
    column_config=column_config,
    width="stretch",
    hide_index=True,
    disabled=True,
)

space()
horizontal_rule()

# ─────────────────────────────────────────────────────────────
# Section 3 — Most Frequently Featured Countries
# ─────────────────────────────────────────────────────────────
render_section_header(
    title="Most Frequently Featured Countries",
    emoji="🌍",
    color_hex=CHAKRA_THROAT,
)

render_section_card(
    icon="📌",
    content_paragraph="This section shows the top 5 countries that appear most frequently across all keywords.",
    content_list=[
        "🏅 Country names are paired with flags for easy recognition.",
        "🔍 Expand each keyword to view its top 5 countries ranked by frequency.",
    ],
    gradient_color=CHAKRA_THROAT,
)
space()

df_top5["Country"] = df_top5["country"].apply(lambda x: f"{get_flag_emoji(x)} {x}")
df_top5 = df_top5.rename(columns={"keyword": "Keyword"})
df_top5["Rank"] = df_top5.groupby("Keyword").cumcount() + 1
df_top5 = df_top5[["Keyword", "Rank", "Country"]]

for keyword in df_top5["Keyword"].unique():
    df_subset = df_top5[df_top5["Keyword"] == keyword].sort_values("Rank")
    df_display = df_subset[["Rank", "Country"]].reset_index(drop=True)

    with st.expander(f"📌 Top 5 Countries — {keyword.title()}"):
        st.markdown(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

space()

# ─────────────────────────────────────────────────────────────
# Footer — Interest Score Explanation + last updated
# ─────────────────────────────────────────────────────────────
latest_date = df_trend_long["date"].max().strftime("%B %d, %Y")
render_custom_footer(show_last_updated=latest_date, color_hex=CHAKRA_THROAT)
