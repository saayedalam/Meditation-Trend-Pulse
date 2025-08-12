# 🔍 Related Queries Page — Meditation Trend Pulse

import os
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.ui import (
    inject_app_theme,
    page_header,
    render_card,
    space,
    horizontal_rule,
    render_section_header,
    render_section_card,
    render_centered_styled_table,
    CHAKRA_THIRD_EYE,
    render_custom_footer,
)

# ─────────────────────────────────────────────────────────────
# Page config and styles
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Related Queries | Meditation Trend Pulse", layout="wide")
inject_app_theme()

# ─────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────
DATA_PATH = "../data/streamlit"
df_related_top10 = pd.read_csv(os.path.join(DATA_PATH, "related_queries_top10.csv"))
df_related_rising10 = pd.read_csv(os.path.join(DATA_PATH, "related_queries_rising10.csv"))
df_related_shared = pd.read_csv(os.path.join(DATA_PATH, "related_queries_shared.csv"))

# ─────────────────────────────────────────────────────────────
# Page header and overview card
# ─────────────────────────────────────────────────────────────
page_header(
    title="🔍 Related Search Queries",
    subtitle="Discover what the world is searching for alongside mindfulness, breathwork, and meditation",
)
space(1)

intro_html = """
🧭 This page explores what people frequently search <strong>with</strong> meditation-related keywords — offering insight into their intentions, challenges, and aspirations.<br/><br/>
Powered by <strong>Google Trends’ related queries</strong>, the visuals below help you identify top co-searches, fast-rising phrases, and common themes across terms like mindfulness, breathwork, and yoga nidra.<br/><br/>
🧵 Use the filters to explore <strong>top 10 related queries per keyword</strong>, <strong>rising searches</strong> over time, and <strong>shared queries</strong> across the full spectrum of interest.<br/><br/>
💡 Great for researchers, product builders, teachers — or anyone curious about the emotional and practical drivers behind meditation searches.<br/><br/>
📊 “Searches for 'how to meditate' often appear alongside phrases like ‘sleep better’, ‘calm anxiety’, and ‘meaning of life’.”
"""

render_card(
    title_html="Overview",
    body_html=intro_html,
    color_hex=CHAKRA_THIRD_EYE,
    side="left",
    center=False,
)

space(2)

# ─────────────────────────────────────────────────────────────
# Section 1 — Top vs Rising Related Queries
# ─────────────────────────────────────────────────────────────
render_section_header(
    title="Top vs Rising Related Queries",
    emoji="🧠",
    color_hex=CHAKRA_THIRD_EYE,
)

space()

keywords_combined = df_related_top10["keyword"].unique().tolist()

col1, col2 = st.columns(2)

with col1:
    render_section_card(
        icon="🔝",
        content_paragraph="Shows the <strong>top 10 most frequent search queries</strong> for each meditation keyword.",
        content_list=[
            "🧠 Commonly co-searched phrases, e.g., “guided meditation for anxiety”.",
            "🎯 Useful for understanding <strong>core search intent</strong>."
        ],
        gradient_color=CHAKRA_THIRD_EYE,
    )

with col2:
    render_section_card(
        icon="📈",
        content_paragraph="Shows the <strong>fastest-growing search queries</strong> from Google Trends “Rising” data.",
        content_list=[
            "🚀 Captures real-time spikes or sudden popularity shifts.",
            '📊 <strong>Scores may exceed 100</strong> — they reflect absolute growth, not normalized values.',
        ],
        gradient_color=CHAKRA_THIRD_EYE,
    )

space()

selected_keyword_combined = st.selectbox(
    "Select a keyword to update both tables:",
    options=keywords_combined
)

space()

col3, col4 = st.columns(2)

with col3:
    df_top_combined = (
        df_related_top10[df_related_top10["keyword"] == selected_keyword_combined]
        .rename(columns={"related_query": "Related Query", "popularity_score": "Relevance Score"})
        [["Related Query", "Relevance Score"]]
    )
    df_top_combined["Relevance Score"] = pd.to_numeric(df_top_combined["Relevance Score"], errors="coerce").round(1)
    html_table = df_top_combined.to_html(index=False, escape=False)
    render_centered_styled_table(html_table)

with col4:
    df_rising_combined = (
        df_related_rising10[df_related_rising10["keyword"] == selected_keyword_combined]
        .rename(columns={"related_query": "Related Query", "popularity_score": "Relevance Score"})
        [["Related Query", "Relevance Score"]]
    )
    df_rising_combined["Relevance Score"] = pd.to_numeric(df_rising_combined["Relevance Score"], errors="coerce").round(1)
    html_table = df_rising_combined.to_html(index=False, escape=False)
    render_centered_styled_table(html_table)

space()
horizontal_rule()

# ─────────────────────────────────────────────────────────────
# Section 2 — Shared Related Queries
# ─────────────────────────────────────────────────────────────
render_section_header(
    title="Shared Related Queries",
    emoji="🔗",
    color_hex=CHAKRA_THIRD_EYE,
)

render_section_card(
    icon="💬",
    content_paragraph="This section highlights <strong>search queries that appear under multiple keywords</strong>.",
    content_list=[
        "♻️ Helps uncover universal themes and overlapping intent across meditation-related terms",
        "🧠 Great for identifying high-impact queries with broad relevance",
        "🔽 Sorted by number of keyword appearances for clarity",
    ],
    gradient_color=CHAKRA_THIRD_EYE,
)

space()

df_grouped_shared = (
    df_related_shared.groupby("related_query")["keyword"]
    .apply(lambda x: ", ".join(sorted(x.unique())))
    .reset_index()
    .rename(columns={"related_query": "Shared Query", "keyword": "Appears Under"})
)

df_grouped_shared["# of Keywords"] = df_grouped_shared["Appears Under"].apply(lambda x: len(x.split(",")))
df_grouped_shared = df_grouped_shared.sort_values(by="# of Keywords", ascending=False)

html_table = df_grouped_shared[["Shared Query", "Appears Under"]].to_html(escape=False, index=False)
render_centered_styled_table(html_table)

space()

# ─────────────────────────────────────────────────────────────
# Footer with last updated timestamp
# ─────────────────────────────────────────────────────────────
now = datetime.now().strftime("%B %d, %Y")
render_custom_footer(show_last_updated=now, color_hex=CHAKRA_THIRD_EYE)
