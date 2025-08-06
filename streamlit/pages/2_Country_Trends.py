# 🌍 Country Trends Page — Meditation Trend Pulse

import streamlit as st
import pandas as pd
import os
import pycountry
import altair as alt
from utils.ui import inject_base_css  # 🔄 Shared CSS styles (animations, theme)

# 🔧 Page config
st.set_page_config(page_title="Country Trends | Meditation Trend Pulse", layout="wide")

# 🎨 Inject global styles
inject_base_css()

# 💾 Load Data
DATA_PATH = "../data/streamlit"
df_country = pd.read_csv(os.path.join(DATA_PATH, "country_interest_summary.csv"))
df_total = pd.read_csv(os.path.join(DATA_PATH, "country_total_interest_by_keyword.csv"))
df_top5 = pd.read_csv(os.path.join(DATA_PATH, "country_top5_appearance_counts.csv"))

# 📌 Page Introduction
intro_html = """
<style>
@keyframes fadeUp {
  from {opacity: 0; transform: translateY(20px) scale(0.97);}
  to {opacity: 1; transform: translateY(0) scale(1);}
}
.intro-animated {
  animation: fadeUp 1s ease-out;
}
</style>

<div class="intro-animated" style="text-align: center; padding: 2.5rem 0;">
    <h1 style="font-size: 2.9rem; color: #143D59; margin-bottom: 0.2rem; font-weight: 700;">
        🌍 Country-Level Meditation Trends
    </h1>
    <h3 style="font-weight: 400; color: #666; font-size: 1.25rem; margin-top: 0;">
        A calming look into how the world connects through stillness, breath, and awareness
    </h3>
    <br>
    <div style="display: inline-block; background: linear-gradient(to right, #e4f0ff, #f7f9ff); padding: 2rem 2.5rem; border-radius: 14px; border-left: 6px solid #4B8BBE; text-align: left; max-width: 820px; margin-top: 1.5rem; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.06);">
        <p style="font-size: 1.15rem; line-height: 1.75; color: #333;">
            🧘‍♀️ This page explores how people across the globe are turning to <strong>meditation, mindfulness, breathwork,</strong> and related practices — not just as trends, but as tools for peace and clarity.
        </p>
        <p style="font-size: 1.1rem; line-height: 1.7; color: #333;">
            Sourced from <strong>Google Trends</strong> and updated weekly, this dashboard helps you discover which countries are most engaged with these practices — and how interest is evolving over time.
        </p>
        <p style="font-size: 1.05rem; line-height: 1.6; color: #4B8BBE;">
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
st.markdown("<br>", unsafe_allow_html=True)

# 🎯 Keyword Filter
keywords = df_country["keyword"].unique().tolist()
selected_keywords = st.multiselect("🎯 Choose a keyword to explore:", keywords, default=keywords[:1])

# 🚫 Handle no selection
if not selected_keywords:
    st.warning("Please select at least one keyword to display country interest trends.")
else:
    df_filtered = df_country[df_country["keyword"].isin(selected_keywords)]

    # 📊 Section 1: Top Countries by Interest
    st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🏆 Top Countries by Interest</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
    <p style='margin-bottom: 0.75rem; font-size: 1.05rem; color: #333;'>
    This visual highlights the countries showing the strongest interest in your selected meditation keywords.
    </p>
    <ul style='margin-top: 0; padding-left: 1.2rem; font-size: 0.95rem; color: #444;'>
      <li>🔢 Choose how many countries to view — top 10, 25, or 50 — using the toggle below.</li>
      <li>🎯 Each bar is grouped by keyword so you can compare how different practices resonate in different places.</li>
      <li>📊 Hover to view total interest and the percentage that country contributes to the global total for each keyword.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    top_n_choice = st.radio("🔎 Show top countries by total interest:", options=[10, 25, 50], index=1, horizontal=True)

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
        y=alt.Y("interest:Q", title="Average Interest"),
        color=alt.Color("keyword:N", title="Keyword"),
        tooltip=[
            alt.Tooltip("country:N", title="Country"),
            alt.Tooltip("keyword:N", title="Keyword"),
            alt.Tooltip("interest:Q", title="Interest"),
            alt.Tooltip("percent_of_keyword:Q", title="% of Global Keyword Interest", format=".1f")
        ]
    ).properties(height=500)

    st.altair_chart(bar_chart, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

# 📊 Section 2: Global Totals by Country & Keyword
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>📊 Global Totals by Country & Keyword</h2>", unsafe_allow_html=True)

st.markdown("""
<div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
<p style='margin-bottom: 0.75rem; font-size: 1.05rem; color: #333;'>
This table shows total search interest for each keyword in each country across the full dataset.
</p>
<ul style='margin-top: 0; padding-left: 1.2rem; font-size: 0.95rem; color: #444;'>
  <li>📦 Great for full exports or precision filtering by analysts or researchers.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
df_total_cleaned = df_total.rename(columns={"country": "Country", "keyword": "Keyword", "total_interest": "Total Interest"})
df_total_cleaned["Total Interest"] = pd.to_numeric(df_total_cleaned["Total Interest"], errors="coerce")

column_config = {
    "Country": st.column_config.TextColumn(label="Country"),
    "Keyword": st.column_config.TextColumn(label="Keyword"),
    "Total Interest": st.column_config.NumberColumn(label="Total Interest")
}

st.data_editor(
    df_total_cleaned,
    column_config=column_config,
    use_container_width=True,
    hide_index=True,
    disabled=True
)

st.markdown("---")

# 🔹 Section 3: Most Frequently Featured Countries
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🌍 Most Frequently Featured Countries</h2>", unsafe_allow_html=True)

st.markdown("""
<div class='fade-in' style='background-color:#F9FAFB; padding: 1rem 1.5rem; border-left: 4px solid #4B8BBE; border-radius: 6px;'>
<p style='margin-bottom: 0.75rem; font-size: 1.05rem; color: #333;'>
Explore the top 5 countries that consistently rank highest for each keyword.
</p>
<ul style='margin-top: 0; padding-left: 1.2rem; font-size: 0.95rem; color: #444;'>
  <li>🏅 Flags shown alongside country names</li>
  <li>📌 Click on each keyword to expand the top 5 countries</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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

df_top5["Flag"] = df_top5["country"].apply(get_flag_emoji)
df_top5["Country"] = df_top5["Flag"] + " " + df_top5["country"]
df_top5 = df_top5.rename(columns={"keyword": "Keyword"})
df_top5["Rank"] = df_top5.groupby("Keyword").cumcount() + 1
df_top5 = df_top5[["Keyword", "Rank", "Country"]]

# ⬇️ Expanders per keyword with HTML inside
for keyword in df_top5["Keyword"].unique():
    df_subset = df_top5[df_top5["Keyword"] == keyword].sort_values("Rank")
    df_subset_display = df_subset[["Rank", "Country"]].reset_index(drop=True)
    
    with st.expander(f"📌 Top 5 Countries — {keyword.title()}"):
        st.markdown(df_subset_display.to_html(escape=False, index=False), unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)

footer_html = """
<div style="
    margin-top: 3.5rem;
    padding: 1.75rem 2rem 1.5rem 2rem;
    border-radius: 12px;
    background: linear-gradient(to left, #f9fafc, #f3f4f6);
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