# 🔍 Related Queries Page — Meditation Trend Pulse

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.ui import inject_base_css  # 🔄 Shared CSS styles (animations, theme)

# 🔧 Page config
st.set_page_config(page_title="Related Queries | Meditation Trend Pulse", layout="wide")

# 🎨 Inject global styles
inject_base_css()

# Space
def space(): 
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# 💾 Load Data
DATA_PATH = "../data/streamlit"
df_related_top10 = pd.read_csv(os.path.join(DATA_PATH, "related_queries_top10.csv"))
df_related_rising10 = pd.read_csv(os.path.join(DATA_PATH, "related_queries_rising10.csv"))
df_related_shared = pd.read_csv(os.path.join(DATA_PATH, "related_queries_shared.csv"))

# 📌 RELATED QUERIES — Page Introduction (Finalized Color-Matched Version)
intro_html = """
<style>
@keyframes fadeUp {
  from {opacity: 0; transform: translateY(20px) scale(0.97);}
  to {opacity: 1; transform: translateY(0) scale(1);}
}
.fade-in-queries {
  animation: fadeUp 1s ease-out;
}
.chakra-card-1 {
    background: linear-gradient(135deg, #fafaff, #f9f6ff, #f4f0fb);
    padding: 1.25rem 1.5rem;
    border-radius: 10px;
    color: #2e2e2e;
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    animation: fadeUp 1s ease-out;
}
thead tr th:nth-child(2),
tbody tr td:nth-child(2) {
    text-align: right;
    padding-right: 12px;
}
tbody tr:nth-child(odd) {
    background-color: #FAFAFA;
}
thead th {
    color: #333;
    font-weight: 600;
}
table {
    width: 100%;
    max-width: 680px;
    margin-left: auto;
    margin-right: auto;
}
tbody tr:hover {
    background-color: #f0f4ff;
}
</style>

<div class="fade-in-queries" style="text-align: center; padding: 2.5rem 0; position: relative;">
  <h1 style="font-size: 2.9rem; color: #1F4E79; margin-bottom: 0.2rem; font-weight: 700;">
    🔍 Related Search Queries
  </h1>
  <h3 style="font-weight: 400; color: #666; font-size: 1.25rem; margin-top: 0;">
    Discover what the world is searching for alongside mindfulness, breathwork, and meditation
  </h3>
  <br>
  <div style="
      display: inline-block;
      background: linear-gradient(135deg, #fafaff, #f9f6ff, #f4f0fb);
      padding: 2rem 2.5rem;
      border-radius: 14px;
      border-left: 6px solid #7C3AED;
      text-align: left;
      max-width: 820px;
      margin-top: 1.5rem;
      box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.04);
      position: relative;
      z-index: 1;
  ">
    <p style="font-size: 1.15rem; line-height: 1.75; color: #333;">
      🧭 This page explores what people frequently search <strong>with</strong> meditation-related keywords — offering insight into their intentions, challenges, and aspirations.
    </p>
    <p style="font-size: 1.1rem; line-height: 1.7; color: #333;">
      Powered by <strong>Google Trends’ related queries</strong>, the visuals below help you identify top co-searches, fast-rising phrases, and common themes across terms like mindfulness, breathwork, and yoga nidra.
    </p>
    <p style="font-size: 1.05rem; line-height: 1.6; color: #5B21B6;">
      🧵 Use the filters to explore <strong>top 10 related queries per keyword</strong>, <strong>rising searches</strong> over time, and <strong>shared queries</strong> across the full spectrum of interest.
    </p>
    <p style="font-size: 1rem; font-style: italic; color: #666; margin-top: 0.75rem;">
      💡 Great for researchers, product builders, teachers — or anyone curious about the emotional and practical drivers behind meditation searches.
    </p>
  </div>
  <div style="margin-top: 1.75rem;">
    <p style="font-size: 1rem; color: #888; font-style: italic;">
      📊 “Searches for 'how to meditate' often appear alongside phrases like ‘sleep better’, ‘calm anxiety’, and ‘meaning of life’.”
    </p>
  </div>
</div>
"""

st.html(intro_html, width="stretch")
space()

# 🧪 Combined Section (Aligned Cards + Shared Dropdown)
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🧠 Top vs Rising Related Queries</h3>", unsafe_allow_html=True)
st.markdown("<p style='color:#666; font-size: 1rem;'>Compare frequent vs emerging search patterns side-by-side</p>", unsafe_allow_html=True)

# 🔽 Shared Dropdown — now below intro cards
keywords_combined = df_related_top10["keyword"].unique().tolist()

# 🔲 Columns for layout
col1, col2 = st.columns(2)

# 🔝 Left: Top 10
with col1:
    st.markdown("<h3 style='color:#4B8BBE;'>🔝 Top 10 Related Queries</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div class='chakra-card-1'>
      <p style='font-size: 1.05rem;'>🔍 Shows the <strong>top 10 most frequent search queries</strong> for each meditation keyword.</p>
      <ul style='margin-top: 0; padding-left: 1.2rem;'>
        <li>🧠 Commonly co-searched phrases, e.g., “guided meditation for anxiety”.</li>
        <li>🎯 Useful for understanding <strong>core search intent</strong>.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

# 🔼 Right: Rising
with col2:
    st.markdown("<h3 style='color:#4B8BBE;'>📈 Rising Related Queries</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div class='chakra-card-1'>
      <p style='font-size: 1.05rem;'>📈 Shows the <strong>fastest-growing search queries</strong> from Google Trends “Rising” data.</p>
      <ul style='margin-top: 0; padding-left: 1.2rem;'>
        <li>🚀 Captures real-time spikes or sudden popularity shifts.</li>
        <li>📊 <span style="color:#92400E;"><strong>Scores may exceed 100</strong> — they reflect absolute growth, not normalized values.</span></li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

# 🔽 Shared keyword selector (new position)
space()
selected_keyword_combined = st.selectbox("Select a keyword to update both tables:", options=keywords_combined)
space()

# 🔲 Table layout
col3, col4 = st.columns(2)

with col3:
    df_top_combined = df_related_top10[df_related_top10["keyword"] == selected_keyword_combined].copy()
    df_top_combined = df_top_combined.rename(columns={
        "related_query": "Related Query",
        "popularity_score": "Relevance Score"
    })[["Related Query", "Relevance Score"]]
    df_top_combined["Relevance Score"] = pd.to_numeric(df_top_combined["Relevance Score"], errors="coerce").round(1)
    st.markdown(df_top_combined.to_html(index=False, escape=False), unsafe_allow_html=True)

with col4:
    df_rising_combined = df_related_rising10[df_related_rising10["keyword"] == selected_keyword_combined].copy()
    df_rising_combined = df_rising_combined.rename(columns={
        "related_query": "Related Query",
        "popularity_score": "Relevance Score"
    })[["Related Query", "Relevance Score"]]
    df_rising_combined["Relevance Score"] = pd.to_numeric(df_rising_combined["Relevance Score"], errors="coerce").round(1)
    st.markdown(df_rising_combined.to_html(index=False, escape=False), unsafe_allow_html=True)

space()
st.markdown("---")

# 🔗 Section 3: Shared Related Queries
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🔗 Shared Related Queries</h2>", unsafe_allow_html=True)

# 💬 Visual intro block
st.markdown("""
<div class='chakra-card-1'>
  <p style='font-size: 1.05rem;'>🔗 This section highlights <strong>search queries that appear under multiple keywords</strong>.</p>
  <ul style='margin-top: 0; padding-left: 1.2rem;'>
    <li>♻️ Helps uncover universal themes and overlapping intent across meditation-related terms</li>
    <li>🧠 Great for identifying high-impact queries with broad relevance</li>
    <li>🔽 Sorted by number of keyword appearances for clarity</li>
  </ul>
</div>
""", unsafe_allow_html=True)

space()

# 📦 Load shared queries data
df_shared = pd.read_csv(os.path.join(DATA_PATH, "related_queries_shared.csv"))

# 🧹 Group shared queries by the query itself
df_grouped_shared = (
    df_shared.groupby("related_query")["keyword"]
    .apply(lambda x: ", ".join(sorted(x.unique())))
    .reset_index()
    .rename(columns={"related_query": "Shared Query", "keyword": "Appears Under"})
)

# ➕ Add appearance count column for sorting
df_grouped_shared["# of Keywords"] = df_grouped_shared["Appears Under"].apply(lambda x: len(x.split(",")))

# 🔽 Sort by number of appearances (descending)
df_grouped_shared = df_grouped_shared.sort_values(by="# of Keywords", ascending=False)

# 📊 Display clean HTML table (centered)
st.markdown(
    df_grouped_shared[["Shared Query", "Appears Under"]].to_html(
        escape=False, index=False
    ),
    unsafe_allow_html=True
)

space()

# 🧾 Footer — Interest Score Explanation
footer_html = """
<div style="
    margin-top: 3.5rem;
    padding: 1.75rem 2rem 1.5rem 2rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #fafaff, #f9f6ff, #f4f0fb);
    border-right: 5px solid #4B8BBE;
    max-width: 880px;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
    color: #333;
">

  <!-- Optional watermark icon -->
  <img src="https://img.icons8.com/ios-glyphs/30/4B8BBE/search--v1.png" 
       style="position: absolute; bottom: 12px; right: 14px; opacity: 0.08; width: 42px;" 
       alt="Search Icon" />

  <h4 style="margin: 0 0 0.8rem 0; color: #1F4E79;">📊 Interpreting Interest & Relevance Scores</h4>

  <p style="margin: 0 0 0.5rem 0; font-size: 1.05rem;">
    Google Trends uses two types of scores across this dashboard:
  </p>

  <ul style="margin: 0 0 0.75rem 1.25rem; padding-left: 0; font-size: 0.98rem; color: #444;">
    <li><strong>Interest Score</strong> (Country Trends): Normalized from 0–100 based on <em>each region’s peak search activity</em> for that keyword.</li>
    <li><strong>Relevance Score</strong> (Rising Queries): May <strong>exceed 100</strong> and reflects <em>raw growth or breakout activity</em> — not normalized.</li>
  </ul>

  <p style="font-size: 0.93rem; color: #666; font-style: italic; margin-top: 1rem;">
    Normalized scores allow for geographic comparisons. Relevance scores highlight emerging search behavior, even for low-traffic keywords.
  </p>

</div>
"""

st.html(footer_html, width="stretch")

# 📅 Timestamp — Last Updated
now = datetime.now().strftime("%B %d, %Y")
st.markdown(f"<p style='text-align:center; font-size: 0.85rem; color: #888;'>📅 Last updated: {now}</p>", unsafe_allow_html=True)

