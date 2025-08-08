# 📈 Global Trends Page — Meditation Trend Pulse

import os
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

# Import shared UI helpers and styles
from utils.ui import inject_app_theme, page_header, render_card, space, CHAKRA_HEART

# ─────────────────────────────────────────────────────────────
# 🔧 Page configuration and global style injection
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Global Trends | Meditation Trend Pulse", layout="wide")
inject_app_theme()  # Inject baseline global styles and animations

# ─────────────────────────────────────────────────────────────
# 📁 Data loading
# ─────────────────────────────────────────────────────────────
DATA_PATH = "../data/streamlit"
df_trend_long = pd.read_csv(os.path.join(DATA_PATH, "global_trend_summary.csv"))
df_pct_change = pd.read_csv(os.path.join(DATA_PATH, "trend_pct_change.csv"))
df_top_peaks = pd.read_csv(os.path.join(DATA_PATH, "trend_top_peaks.csv"))

df_trend_long["date"] = pd.to_datetime(df_trend_long["date"])

# ─────────────────────────────────────────────────────────────
# 🖼 Page header
# ─────────────────────────────────────────────────────────────
page_header(
    title="📊 Global Trends in Meditation",
    subtitle="A worldwide view of mindfulness, breathwork, and inner stillness over time",
)

space(1)  # Add vertical spacing after header

# ─────────────────────────────────────────────────────────────
# 🟩 'What We Noticed' card with exact styled text
# ─────────────────────────────────────────────────────────────
body_html = """
🌐 This page reveals the global rhythm of search interest in meditation-related topics — including <strong>mindfulness</strong>, <strong>breathwork</strong>, and <strong>guided meditation</strong>.<br/><br/>
Built with data from <strong>Google Trends</strong>, it captures long-term growth, seasonal shifts, and spikes tied to cultural events, crises, and collective curiosity.<br/><br/>
🎯 <span style="color:#5B21B6; font-weight: 600;">Use the tools below to filter keywords, adjust time windows, and surface the stories hidden in the trends.</span><br/><br/>
🧘 <em>Whether you're a researcher, wellness coach, or mindful observer — this is your window into how the world is tuning inward.</em>
"""

render_card(
    title_html="",  # no title, so no extra space
    body_html=body_html,
    color_hex=CHAKRA_HEART,
    side="left",
    center=False,
)

space(2)  # Additional spacing before next content
# ─────────────────────────────────────────────────────────────
# (Future sections like visualizations, filters, etc. go here)
# ─────────────────────────────────────────────────────────────
# 📊 Section 1 — Global Interest Over Time
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>📅 Global Search Interest Over Time</h2>", unsafe_allow_html=True)

st.markdown("""
<style>
.chakra-card-1 {
    background: linear-gradient(135deg, #fafaff, #f9f6ff, #f4f0fb);
    padding: 1.25rem 1.5rem;
    border-radius: 10px;
    color: #2e2e2e;
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    animation: fadeUp 1s ease-out;
}
</style>

<div class='chakra-card-1'>
    <p style='font-size: 1.05rem;'><span style='font-size: 1.4rem;'>🧿</span> This line chart illustrates how global interest in each keyword has evolved over time.</p>
    <ul style='margin-top: 0; padding-left: 1.2rem;'>
      <li>📈 See growth in mindfulness, breathwork, and related practices year by year.</li>
      <li>🌀 Spot seasonal patterns — such as New Year peaks or post-pandemic surges.</li>
      <li>🔍 Explore spikes tied to world events, news, or viral trends.</li>
      <li>💡 Use the filters below to explore specific keywords and time periods.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

space()

# 🎛️ Filter Panel (collapsible and subtle)
with st.expander("🔧 Adjust filters", expanded=False):
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
            key="date_slider_1"
        )

# 🛑 Guard Clause
if not selected_keywords:
    st.warning("Please select at least one keyword to continue.")
else:
    # 🧹 Apply both filters
    df_filtered = df_trend_long[
        (df_trend_long["keyword"].isin(selected_keywords)) &
        (df_trend_long["date"] >= pd.to_datetime(date_range[0])) &
        (df_trend_long["date"] <= pd.to_datetime(date_range[1]))
    ]

    # 📌 Summary Metrics
    total_by_keyword = df_filtered.groupby("keyword")["search_interest"].sum()
    top_keyword = total_by_keyword.idxmax()
    top_keyword_val = total_by_keyword.max()
    peak_interest = df_filtered["search_interest"].max()
    num_points = len(df_filtered)

    space()
    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Top Keyword", f"{top_keyword}", f"{top_keyword_val:.0f} total")
        col2.metric("📈 Peak Score", f"{peak_interest:.0f}")
        col3.metric("📊 Records", f"{num_points}")

    space()

    # 📈 Line Chart — Responsive + Clean Zoom
    line_chart = alt.Chart(df_filtered).mark_line(interpolate='monotone').encode(
        x=alt.X(
            'date:T',
            title="Date",
            scale=alt.Scale(nice="month"),
            axis=alt.Axis(format="%b %Y", labelAngle=0, labelOverlap=True)
        ),
        y=alt.Y('search_interest:Q', title="Search Interest"),
        color='keyword:N',
        tooltip=['date:T', 'keyword:N', 'search_interest:Q']
    ).properties(
        height=420
    ).interactive(bind_y=False)

    st.altair_chart(line_chart, use_container_width=True)
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("---")

# 📊 Section 2 — 5-Year % Change
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>📈 5-Year Growth or Decline by Search Term</h2>", unsafe_allow_html=True)

st.markdown("""
<style>
.chakra-card-2 {
    background: linear-gradient(135deg, #fafaff, #f9f6ff, #f4f0fb);
    padding: 1.25rem 1.5rem;
    border-radius: 10px;
    color: #2e2e2e;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.04);
    animation: fadeUp 1s ease-out;
}
</style>

<div class='chakra-card-2'>
  <p style='font-size: 1.05rem;'>This table shows how global interest in each search term has changed over the past 5 years, based on Google Trends data.</p>
  <ul style='margin-top: 0; padding-left: 1.2rem;'>
    <li>🟢 <strong>Positive %</strong> means global interest increased</li>
    <li>🔴 <strong>Negative %</strong> means global interest declined</li>
    <li>💡 Use this view to identify which practices are gaining traction — and which are fading</li>
  </ul>
</div>
""", unsafe_allow_html=True)

space()

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
# Center the styled table with a max width for balance
table_html = f"""
<div style="display: flex; justify-content: center; width: 100%; margin-top: 1rem; margin-bottom: 1rem;">
  <div style="max-width: 600px; width: 100%;">
    {df_pct_styled.to_html(escape=False, index=False)}
  </div>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)
st.markdown("""
<style>
table tr:hover {
    background-color: #f3f0ff !important;
    transition: background-color 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

st.markdown("---")

# 🌟 Section 3 — Top Peak Dates by Keyword
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🌟 Top Peak Dates by Keyword</h2>", unsafe_allow_html=True)

st.markdown("""
<style>
.chakra-card-3 {
    background: linear-gradient(135deg, #fafaff, #f9f6ff, #f4f0fb);
    padding: 1.25rem 1.5rem;
    border-radius: 10px;
    color: #2e2e2e;
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    animation: fadeUp 1s ease-out;
}
</style>

<div class='chakra-card-3'>
    <p style='font-size: 1.05rem;'>See when each keyword reached its highest level of global interest.</p>
    <ul style='margin-top: 0; padding-left: 1.2rem;'>
      <li>📆 Pinpoint cultural events or awareness weeks driving spikes</li>
      <li>🌍 Spot time-specific behaviors in how people seek stillness</li>
      <li>🧠 Great for insights, storytelling, or campaign planning</li>
    </ul>
</div>
""", unsafe_allow_html=True)

space()

# 🧹 Rename columns for clarity
df_top_cleaned = df_top_peaks.rename(columns={
    "keyword": "Search Term",
    "date": "Peak Date",
    "search_interest": "Interest Score"
}).copy()

# 🎯 Keep only top peak per keyword
df_top_cleaned = df_top_cleaned.sort_values("Interest Score", ascending=False)
df_top_cleaned = df_top_cleaned.drop_duplicates(subset="Search Term", keep="first")

# 📅 Clean Peak Date
df_top_cleaned["Peak Date"] = pd.to_datetime(df_top_cleaned["Peak Date"]).dt.date

# 🧠 Add event mapping manually
event_mapping = {
    "meditation": "🧘 New Year's Resolution Spike",
    "mindfulness": "🧠 Back-to-School + Wellness Push",
    "guided meditation": "🎧 Mid-Pandemic Anxiety Relief",
    "yoga nidra": "🛌 Winter Sleep Trends + TikTok Surge",
    "breathwork": "🌬️ New Year Recovery + Biohacking"
}
df_top_cleaned["Event"] = df_top_cleaned["Search Term"].map(event_mapping).fillna("—")

# 🔀 Reorder columns to place Interest Score at the end
df_top_cleaned = df_top_cleaned[["Search Term", "Peak Date", "Event", "Interest Score"]]

# ✨ Style only the Interest Score column
def format_interest(val):
    return "font-weight: bold; text-align: center;" if pd.notnull(val) else ""

styled_df = df_top_cleaned.style.applymap(format_interest, subset=["Interest Score"])
st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

# 📋 Display
st.dataframe(styled_df, use_container_width=True, hide_index=True)
space()

# 🧾 Footer — Interest Score Explanation
footer_html = """
<div style="
    margin-top: 3.5rem;
    padding: 1.75rem 2rem 1.5rem 2rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #fafaff, #f9f6ff, #f4f0fb);
    border-right: 5px solid #7C3AED;
    max-width: 880px;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
    color: #333;
">

  <!-- Optional watermark icon -->
  <img src="https://img.icons8.com/ios-glyphs/30/7C3AED/search--v1.png" 
       style="position: absolute; bottom: 12px; right: 14px; opacity: 0.08; width: 42px;" 
       alt="Search Icon" />

  <h4 style="margin: 0 0 0.8rem 0; color: #1F4E79;">📊 Understanding the Interest Score</h4>

  <p style="margin: 0 0 0.5rem 0; font-size: 1.05rem;">
    Scores range from <strong>0 to 100</strong> and show how popular a search term was — <strong>relative to its own peak</strong>.
  </p>

  <ul style="margin: 0 0 0.5rem 1.25rem; padding-left: 0; font-size: 0.98rem; color: #444;">
    <li><strong>100</strong> = Highest interest ever recorded</li>
    <li><strong>50</strong> = Half as popular as peak</li>
    <li><strong>0</strong> = Not enough data</li>
  </ul>

  <p style="font-size: 0.93rem; color: #666; font-style: italic; margin-top: 1rem;">
    This score is normalized — not raw volume — helping you spot peaks, not totals.
  </p>

</div>
"""

st.html(footer_html, width="stretch")

#Last updates
now = datetime.now().strftime("%B %d, %Y")
st.markdown(f"<p style='text-align:center; font-size: 0.85rem; color: #888;'>📅 Last updated: {now}</p>", unsafe_allow_html=True)

