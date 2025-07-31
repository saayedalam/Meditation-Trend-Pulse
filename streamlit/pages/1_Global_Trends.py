# 📈 Global Trends Page — Meditation Trend Pulse

import streamlit as st
import pandas as pd
import os
import altair as alt
from utils.ui import inject_base_css  # 🔄 Shared CSS styles (animations, theme)

# 🔧 Page config
st.set_page_config(page_title="Global Trends | Meditation Trend Pulse", layout="wide")

# 🎨 Inject global styles
inject_base_css()

# 💾 Load Data
DATA_PATH = "../data/streamlit"
df_trend_long = pd.read_csv(os.path.join(DATA_PATH, "global_trend_summary.csv"))
df_pct_change = pd.read_csv(os.path.join(DATA_PATH, "trend_pct_change.csv"))
df_top_peaks = pd.read_csv(os.path.join(DATA_PATH, "trend_top_peaks.csv"))
df_trend_long["date"] = pd.to_datetime(df_trend_long["date"])

# 📌 Page Introduction

st.markdown("""
<div class="fade-in">
    <h1 style='font-size: 2.25rem; color: #1F4E79; margin-bottom: 0.3rem;'>📊 Global Trends in Meditation</h1>
    <h3 style='font-weight: normal; color: #555; margin-top: 0;'>Explore how the world is tuning into mindfulness, breathwork, and inner stillness</h3>
</div>

<br>

<div class="fade-in" style="background-color: #F0F4F8; padding: 1.5rem 2rem; border-radius: 8px; border-left: 6px solid #4B8BBE;">
    <p style="font-size: 1.1rem; line-height: 1.6;">
        Powered by <strong>Google Trends</strong> and refreshed weekly through an automated pipeline, this dashboard captures 
        <strong>long-term patterns</strong>, <strong>emerging spikes</strong>, and <strong>seasonal behaviors</strong> across multiple meditation-related keywords.
        Whether you're an educator, wellness brand, or policymaker, these insights reveal how public interest in mindfulness is evolving globally.
    </p>
    <p style="font-size: 1rem; font-style: italic; color: #555;">
        💡 Use the filters below to uncover meaningful insights behind the global rise in meditation interest.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)



# 📊 Section 1: Global Search Interest Over Time
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>📅 Global Search Interest Over Time</h2>", unsafe_allow_html=True)

st.markdown("""
<div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
<p style='margin-bottom: 0.5rem;'>
This interactive line chart shows how interest in each selected keyword has evolved from 2019 to today. 
</p>
<ul style='margin-top: 0; padding-left: 1.2rem;'>
  <li>🌀 Identify <strong>seasonal cycles</strong> such as New Year resolution spikes.</li>
  <li>📈 Spot <strong>sustained growth trends</strong> in mindfulness-related practices.</li>
  <li>🔥 Detect <strong>interest surges</strong> triggered by global events or cultural shifts.</li>
</ul>
<p style='margin-top: 0.75rem;'>Use the date slider below to zoom in on specific timeframes and get a focused view of short-term changes.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 🎛️ Keyword Filter
keywords = df_trend_long["keyword"].unique().tolist()
selected_keywords = st.multiselect("🎯 Choose keywords to visualize:", keywords, default=keywords)

# 🚫 Handle no selection
if not selected_keywords:
    st.warning("Please select at least one keyword to display the chart and summary.")
else:
    # 🔍 Filter by selected keywords
    df_filtered = df_trend_long[df_trend_long["keyword"].isin(selected_keywords)]

    # 📅 Date Range Slider
    min_date = df_trend_long["date"].min().date()
    max_date = df_trend_long["date"].max().date()
    date_range = st.slider(
        "📆 Select Date Range:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MMM YYYY",
        key="date_slider_1"  # 🔑 Prevent duplicate slider ID
    )

    # ⏱️ Filter by selected date range
    df_filtered_date = df_filtered[
        (df_filtered["date"] >= pd.to_datetime(date_range[0])) &
        (df_filtered["date"] <= pd.to_datetime(date_range[1]))
    ]

    # 📌 Summary Metrics
    total_by_keyword = df_filtered_date.groupby("keyword")["search_interest"].sum()
    top_keyword = total_by_keyword.idxmax()
    top_keyword_val = total_by_keyword.max()
    peak_interest = df_filtered_date["search_interest"].max()
    num_points = len(df_filtered_date)

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Most Popular Keyword", f"{top_keyword}", f"{top_keyword_val:.0f} total")
    col2.metric("📈 Peak Interest Score", f"{peak_interest:.0f}")
    col3.metric("📊 Data Points Shown", f"{num_points}")

    # 📈 Altair Line Chart
    line_chart = alt.Chart(df_filtered_date).mark_line(interpolate='monotone').encode(
        x=alt.X('date:T', title="Date"),
        y=alt.Y('search_interest:Q', title="Search Interest"),
        color='keyword:N',
        tooltip=['date:T', 'keyword:N', 'search_interest:Q']
    ).properties(
        height=420
    ).interactive()

    st.altair_chart(line_chart, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")


# 📊 Section 2: 5-Year Percent Change
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>📊 5-Year Percent Change in Interest</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
<p style='margin-bottom: 0.5rem;'>
This table summarizes the <strong>relative growth or decline</strong> in global interest for each keyword, comparing search volume today to what it was five years ago.
</p>
<ul style='margin-top: 0; padding-left: 1.2rem;'>
  <li>🔺 Keywords with positive change indicate <strong>rising popularity</strong>.</li>
  <li>🔻 Negative change may signal <strong>declining public attention</strong>.</li>
  <li>📊 A useful reference for evaluating <strong>long-term trends</strong> at a glance.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.dataframe(df_pct_change, use_container_width=True)

st.markdown("---")

# 🌟 Section 3: Top Peak Dates
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🌟 Top Peak Dates by Keyword</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
<p style='margin-bottom: 0.5rem;'>
This table identifies the <strong>exact dates</strong> when each keyword hit its highest recorded global interest.
</p>
<ul style='margin-top: 0; padding-left: 1.2rem;'>
  <li>📆 Helps tie spikes to <strong>cultural moments, crises, or global campaigns</strong>.</li>
  <li>🌍 Useful for spotting <strong>event-based behavior</strong> in wellness-related search habits.</li>
  <li>💬 Ideal for <strong>storytelling</strong> in reports or presentations.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.dataframe(df_top_peaks, use_container_width=True)

# 💬 Floating nav / FAQ
st.markdown("""
<button class="floating-button" onclick="window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });">💬 FAQ</button>
""", unsafe_allow_html=True)
