# 📈 Global Trends Page — Meditation Trend Pulse

import streamlit as st
import pandas as pd
import os
import altair as alt
from utils.ui import inject_base_css  # 🔄 Shared CSS styles (animations, theme)

# 🔧 Page config
st.set_page_config(page_title="Global Trends | Meditation Trend Pulse", layout="wide")

# 🎨 Inject custom styles
inject_base_css()

# 💾 Load Data
DATA_PATH = "../data/streamlit"
df_trend_long = pd.read_csv(os.path.join(DATA_PATH, "global_trend_summary.csv"))
df_pct_change = pd.read_csv(os.path.join(DATA_PATH, "trend_pct_change.csv"))
df_top_peaks = pd.read_csv(os.path.join(DATA_PATH, "trend_top_peaks.csv"))
df_trend_long["date"] = pd.to_datetime(df_trend_long["date"])

# 💡 Intro — Global Trends Overview
intro_html = """
<style>
@keyframes fadeUp {
  from {opacity: 0; transform: translateY(20px) scale(0.97);}
  to {opacity: 1; transform: translateY(0) scale(1);}
}
.fade-in-global {
  animation: fadeUp 1s ease-out;
}
</style>

<div class="fade-in-global" style="text-align: center; padding: 2.5rem 0;">
  <h1 style="font-size: 2.9rem; color: #1F4E79; margin-bottom: 0.2rem; font-weight: 700;">
    📊 Global Trends in Meditation
  </h1>
  <h3 style="font-weight: 400; color: #666; font-size: 1.25rem; margin-top: 0;">
    A worldwide view of mindfulness, breathwork, and inner stillness over time
  </h3>

  <br>

  <div style="
      display: inline-block;
      background: linear-gradient(to right, #e4f0ff, #f7f9ff);
      padding: 2rem 2.5rem;
      border-radius: 14px;
      border-left: 6px solid #4B8BBE;
      text-align: left;
      max-width: 820px;
      margin-top: 1.5rem;
      box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.06);
  ">
    <p style="font-size: 1.15rem; line-height: 1.75; color: #333;">
      🌐 This page reveals the global rhythm of search interest in meditation-related topics — including <strong>mindfulness</strong>, <strong>breathwork</strong>, and <strong>guided meditation</strong>.
    </p>
    <p style="font-size: 1.1rem; line-height: 1.7; color: #333;">
      Built with data from <strong>Google Trends</strong>, it captures long-term growth, seasonal shifts, and spikes tied to cultural events, crises, and collective curiosity.
    </p>
    <p style="font-size: 1.05rem; line-height: 1.6; color: #4B8BBE;">
      🎯 Use the tools below to filter keywords, adjust time windows, and surface the stories hidden in the trends.
    </p>
    <p style="font-size: 1rem; font-style: italic; color: #666; margin-top: 0.75rem;">
      🧘 Whether you're a researcher, wellness coach, or mindful observer — this is your window into how the world is tuning inward.
    </p>
  </div>

  <div style="margin-top: 1.75rem;">
    <p style="font-size: 1rem; color: #888; font-style: italic;">
      📈 “Since 2020, global search interest in meditation has risen across every continent.”
    </p>
  </div>
</div>
"""

st.html(intro_html, width="stretch")
st.markdown("<br>", unsafe_allow_html=True)

# 📊 Section 1 — Global Interest Over Time
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>📅 Global Search Interest Over Time</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
<p>This line chart illustrates how global interest in each keyword has evolved over time.</p>
<ul style='margin-top: 0; padding-left: 1.2rem;'>
  <li>📈 See growth in mindfulness, breathwork, and related practices year by year.</li>
  <li>🌀 Spot seasonal patterns — such as New Year peaks or post-pandemic surges.</li>
  <li>🔍 Explore spikes tied to world events, news, or viral trends.</li>
</ul>
<p style='margin-top: 0.75rem;'>Use the filters below to explore specific keywords and time periods.</p>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 🎛️ Keyword filter
keywords = df_trend_long["keyword"].unique().tolist()
selected_keywords = st.multiselect("🎯 Choose keywords to visualize:", keywords, default=keywords)

# 🚫 Handle no selection
if not selected_keywords:
    st.warning("Please select at least one keyword to display the chart and summary.")
else:
    # 🔍 Filter by keyword and date
    df_filtered = df_trend_long[df_trend_long["keyword"].isin(selected_keywords)]

    min_date = df_trend_long["date"].min().date()
    max_date = df_trend_long["date"].max().date()
    date_range = st.slider(
        "📆 Select Date Range:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MMM YYYY",
        key="date_slider_1"
    )

    df_filtered = df_filtered[
        (df_filtered["date"] >= pd.to_datetime(date_range[0])) &
        (df_filtered["date"] <= pd.to_datetime(date_range[1]))
    ]

    # 📌 Summary Metrics
    total_by_keyword = df_filtered.groupby("keyword")["search_interest"].sum()
    top_keyword = total_by_keyword.idxmax()
    top_keyword_val = total_by_keyword.max()
    peak_interest = df_filtered["search_interest"].max()
    num_points = len(df_filtered)

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Top Keyword", f"{top_keyword}", f"{top_keyword_val:.0f} total")
    col2.metric("📈 Peak Score", f"{peak_interest:.0f}")
    col3.metric("📊 Records", f"{num_points}")

    # 📈 Line Chart
    line_chart = alt.Chart(df_filtered).mark_line(interpolate='monotone').encode(
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

# 📊 Section 2 — 5-Year % Change
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>📈 5-Year Growth or Decline by Search Term</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
<p>This table shows how global interest in each search term has changed over the past 5 years, based on Google Trends data.</p>
<ul style='margin-top: 0; padding-left: 1.2rem;'>
  <li>🟢  <strong>Positive %</strong> means global interest increased</li>
  <li>🔴 <strong>Negative %</strong> means global interest declined</li>
  <li>💡 Use this view to identify which practices are gaining traction — and which are fading</li>
</ul>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 🧹 Rename columns for clarity
df_pct_cleaned = df_pct_change.rename(columns={
    "keyword": "Search Term",
    "percent_change": "5-Year Change (%)"
}).copy()

# 🎯 Round values and sort by biggest gainers
df_pct_cleaned["5-Year Change (%)"] = df_pct_cleaned["5-Year Change (%)"].round(0).astype(int)
df_pct_cleaned = df_pct_cleaned.sort_values("5-Year Change (%)", ascending=False)

# 🎨 Style cells with emoji + color
def style_change(val):
    if val > 0:
        return f"<span style='color:green;'>📈 +{val}%</span>"
    elif val < 0:
        return f"<span style='color:red;'>📉 {val}%</span>"
    else:
        return f"<span style='color:gray;'>➖ {val}%</span>"

df_pct_styled = df_pct_cleaned.copy()
df_pct_styled["5-Year Change (%)"] = df_pct_styled["5-Year Change (%)"].apply(style_change)

# 📋 Render styled table as HTML
st.markdown(df_pct_styled.to_html(escape=False, index=False), unsafe_allow_html=True)



st.markdown("---")

# 🌟 Section 3 — Top Peak Dates
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🌟 Top Peak Dates by Keyword</h2>", unsafe_allow_html=True)

st.markdown("""
<div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
<p>See when each keyword reached its highest level of global interest.</p>
<ul style='margin-top: 0; padding-left: 1.2rem;'>
  <li>📅 Pinpoint cultural events or awareness weeks driving spikes</li>
  <li>🌍 Spot time-specific behaviors in how people seek stillness</li>
  <li>🧠 Great for insights, storytelling, or campaign planning</li>
</ul>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 📅 Event mapping
event_mapping = {
    "2021-01-17": "🧘‍♂️ New Year's Resolution Spike",
    "2020-09-06": "🎒 Back-to-School + Wellness Push",
    "2020-07-26": "💎 Mid-Pandemic Anxiety Relief",
    "2023-01-15": "🛌 Winter Sleep Trends + TikTok Surge",
    "2024-01-07": "🧬 New Year Recovery + Biohacking"
}

# 🧹 Clean and enrich data
df_top_peaks_cleaned = df_top_peaks.copy()
df_top_peaks_cleaned["Peak Date"] = pd.to_datetime(df_top_peaks_cleaned["date"]).dt.date.astype(str)
df_top_peaks_cleaned["Search Term"] = df_top_peaks_cleaned["keyword"]
df_top_peaks_cleaned["Interest Score"] = df_top_peaks_cleaned["search_interest"]
df_top_peaks_cleaned["Event"] = df_top_peaks_cleaned["Peak Date"].map(event_mapping)
df_top_peaks_cleaned = df_top_peaks_cleaned[["Peak Date", "Search Term", "Interest Score", "Event"]]

# 📊 Format styling
styled_df = df_top_peaks_cleaned.style \
    .set_properties(**{
        "text-align": "left",
        "font-size": "0.95rem"
    }) \
    .set_table_styles([
        {"selector": "th", "props": [("text-align", "left"), ("font-size", "1rem")]},
        {"selector": "td:nth-child(3)", "props": [("text-align", "center"), ("font-weight", "bold")]},  # Center + bold interest score
    ]) \
    .apply(lambda x: ['background-color: #F4F4F4' if i % 2 else '' for i in range(len(x))], axis=0)  # Alternating row shading

# 🖼️ Display styled table
st.dataframe(styled_df, use_container_width=True, hide_index=True)