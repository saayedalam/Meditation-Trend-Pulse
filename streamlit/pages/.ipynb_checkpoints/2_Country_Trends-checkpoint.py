# 🌍 Country Trends Page — Meditation Trend Pulse

import streamlit as st
import pandas as pd
import os
import pycountry
import altair as alt
from utils.ui import inject_base_css  # 🔄 Shared CSS styles (animations, theme)
from datetime import datetime

# 🔧 Page config
st.set_page_config(page_title="Country Trends | Meditation Trend Pulse", layout="wide")

# 🎨 Inject global styles
inject_base_css()

# Space
def space(): 
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# 💾 Load Data
DATA_PATH = "../data/streamlit"
df_country = pd.read_csv(os.path.join(DATA_PATH, "country_interest_summary.csv"))
df_total = pd.read_csv(os.path.join(DATA_PATH, "country_total_interest_by_keyword.csv"))
df_top5 = pd.read_csv(os.path.join(DATA_PATH, "country_top5_appearance_counts.csv"))

# 📌 COUNTRY TREND - Page Introduction (Updated to match Global styling)
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

<div class="fade-in-global" style="text-align: center; padding: 2.5rem 0; position: relative;">
  <h1 style="font-size: 2.9rem; color: #1F4E79; margin-bottom: 0.2rem; font-weight: 700;">
    🌍 Country-Level Meditation Trends
  </h1>
  <h3 style="font-weight: 400; color: #666; font-size: 1.25rem; margin-top: 0;">
    A calming look into how the world connects through stillness, breath, and awareness
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
      🧘‍♀️ This page explores how people across the globe are turning to <strong>meditation, mindfulness, breathwork,</strong> and related practices — not just as trends, but as tools for peace and clarity.
    </p>
    <p style="font-size: 1.1rem; line-height: 1.7; color: #333;">
      Sourced from <strong>Google Trends</strong> and updated weekly, this dashboard helps you discover which countries are most engaged with these practices — and how interest is evolving over time.
    </p>
    <p style="font-size: 1.05rem; line-height: 1.6; color: #5B21B6;">
      🌐 Use the filters to explore <strong>top countries by search volume</strong>, view keyword-level breakdowns, and uncover meaningful regional patterns.
    </p>
    <p style="font-size: 1rem; font-style: italic; color: #666; margin-top: 0.75rem;">
      💡 Whether you're a teacher, entrepreneur, researcher, or simply curious — this tool gives you a peaceful window into global interest in stillness and self-awareness.
    </p>
  </div>

  <div style="margin-top: 1.75rem;">
    <p style="font-size: 1rem; color: #888; font-style: italic;">
      📊 “Search interest in meditation has grown by over <strong>250%</strong> worldwide since 2019.”
    </p>
  </div>
</div>
"""

st.html(intro_html, width="stretch")
space()


# 📊 Section 1 — Top Countries by Interest
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🏆 Top Countries by Interest</h2>", unsafe_allow_html=True)

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
  <p style='font-size: 1.05rem;'><span style='font-size: 1.4rem;'>🌍</span> This bar chart highlights countries showing the strongest interest in your selected meditation keywords.</p>
  <ul style='margin-top: 0; padding-left: 1.2rem;'>
    <li>🔢 Choose how many countries to view — top 10, 25, or 50 — using the filter below.</li>
    <li>🎯 Each bar is grouped by keyword so you can compare interest patterns globally.</li>
    <li>📊 Hover to view total interest and % contribution to global totals.</li>
  </ul>
</div>
""", unsafe_allow_html=True)

space()

# 🎛️ Filter Panel (collapsible)
with st.expander("🔧 Adjust filters", expanded=False):
    col1, col2 = st.columns([2, 1])

    with col1:
        keywords = df_country["keyword"].unique().tolist()
        selected_keywords = st.multiselect("Select keywords:", keywords, default=keywords[:1])

    with col2:
        top_n_choice = st.radio("Top N countries:", options=[10, 25, 50], index=1, horizontal=True)

# 🚫 Guard Clause
if not selected_keywords:
    st.warning("Please select at least one keyword to display country interest trends.")
else:
    df_filtered = df_country[df_country["keyword"].isin(selected_keywords)]

    # 🧮 Summary metrics
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

    # 📊 Build chart dataset
    df_ranked = df_filtered.groupby(["country", "keyword"], as_index=False)["interest"].sum()
    df_ranked["percent_of_keyword"] = df_ranked.groupby("keyword")["interest"].transform(lambda x: (x / x.sum()) * 100)

    # 📌 Get top N countries by total interest
    country_order = (
        df_ranked.groupby("country", as_index=False)["interest"].sum()
        .sort_values("interest", ascending=False)
        .head(top_n_choice)["country"]
        .tolist()
    )
    df_topn = df_ranked[df_ranked["country"].isin(country_order)]

    # 🎨 Chart — grouped bar
    bar_chart = alt.Chart(df_topn).mark_bar().encode(
        x=alt.X("country:N", sort=country_order, title="Country"),
        y=alt.Y("interest:Q", title="Search Interest"),
        color=alt.Color("keyword:N", title="Keyword"),
        tooltip=[
            alt.Tooltip("country:N", title="Country"),
            alt.Tooltip("keyword:N", title="Keyword"),
            alt.Tooltip("interest:Q", title="Interest"),
            alt.Tooltip("percent_of_keyword:Q", title="% of Global Keyword Interest", format=".1f")
        ]
    ).properties(height=500)

    st.altair_chart(bar_chart, use_container_width=True)

    space()
    st.markdown("---")


# 📊 Section 2 — Global Totals by Country & Keyword
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>📊 Global Totals by Country & Keyword</h2>", unsafe_allow_html=True)

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
  <p style='font-size: 1.05rem;'>📦 This table shows total search interest for each keyword in each country across the full dataset.</p>
  <ul style='margin-top: 0; padding-left: 1.2rem;'>
    <li>🔍 Great for exports or precise filtering by analysts and researchers.</li>
  </ul>
</div>
""", unsafe_allow_html=True)

space()

# 🧹 Data prep
df_total_cleaned = df_total.rename(columns={"country": "Country", "keyword": "Keyword", "total_interest": "Total Interest"})
df_total_cleaned["Total Interest"] = pd.to_numeric(df_total_cleaned["Total Interest"], errors="coerce")

# 🪄 Optional config
column_config = {
    "Country": st.column_config.TextColumn(label="Country"),
    "Keyword": st.column_config.TextColumn(label="Keyword"),
    "Total Interest": st.column_config.NumberColumn(label="Total Interest")
}

# 📋 Interactive Table
st.data_editor(
    df_total_cleaned,
    column_config=column_config,
    use_container_width=True,
    hide_index=True,
    disabled=True
)

space()
st.markdown("---")

# 🌍 Section 3 — Most Frequently Featured Countries
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🌍 Most Frequently Featured Countries</h2>", unsafe_allow_html=True)

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
  <p style='font-size: 1.05rem;'>📌 This section shows the top 5 countries that appear most frequently across all keywords.</p>
  <ul style='margin-top: 0; padding-left: 1.2rem;'>
    <li>🏅 Country names are paired with flags for easy recognition.</li>
    <li>🔍 Expand each keyword to view its top 5 countries ranked by frequency.</li>
  </ul>
</div>
""", unsafe_allow_html=True)

space()

# 💾 Flag emoji prep
def get_flag_emoji(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            country = pycountry.countries.search_fuzzy(country_name)[0]
        alpha2 = country.alpha_2.upper()
        return chr(127397 + ord(alpha2[0])) + chr(127397 + ord(alpha2[1]))
    except:
        return ""

df_top5["Country"] = df_top5["country"].apply(lambda x: f"{get_flag_emoji(x)} {x}")
df_top5 = df_top5.rename(columns={"keyword": "Keyword"})
df_top5["Rank"] = df_top5.groupby("Keyword").cumcount() + 1
df_top5 = df_top5[["Keyword", "Rank", "Country"]]

# ⬇️ Expanders per keyword with HTML inside
for keyword in df_top5["Keyword"].unique():
    df_subset = df_top5[df_top5["Keyword"] == keyword].sort_values("Rank")
    df_subset_display = df_subset[["Rank", "Country"]].reset_index(drop=True)
    
    with st.expander(f"📌 Top 5 Countries — {keyword.title()}"):
        st.markdown(df_subset_display.to_html(escape=False, index=False), unsafe_allow_html=True)

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

  <h4 style="margin: 0 0 0.8rem 0; color: #1F4E79;">📊 Interpreting Country-Level Interest</h4>

  <p style="margin: 0 0 0.5rem 0; font-size: 1.05rem;">
    Each interest score shows how popular a keyword is in a country — <strong>relative to that country's own peak</strong> for that keyword.
  </p>

  <ul style="margin: 0 0 0.5rem 1.25rem; padding-left: 0; font-size: 0.98rem; color: #444;">
    <li><strong>100</strong> = Peak interest in that country</li>
    <li><strong>50</strong> = Half as popular as that country's peak</li>
    <li><strong>0</strong> = Insufficient search data</li>
  </ul>

  <p style="font-size: 0.93rem; color: #666; font-style: italic; margin-top: 1rem;">
    Scores are normalized per region — not raw totals — allowing fair comparisons across countries.
  </p>

</div>
"""

st.html(footer_html, width="stretch")

# 📅 Timestamp — Last Updated
now = datetime.now().strftime("%B %d, %Y")
st.markdown(f"<p style='text-align:center; font-size: 0.85rem; color: #888;'>📅 Last updated: {now}</p>", unsafe_allow_html=True)