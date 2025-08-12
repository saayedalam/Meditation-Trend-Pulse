# 🏠 Home Page — Meditation Trend Pulse

import os
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.ui import (
    inject_app_theme,
    render_card,
    page_header,
    space,
    CHAKRA_ROOT, CHAKRA_SACRAL, CHAKRA_SOLAR_PLEXUS,
    CHAKRA_HEART, CHAKRA_THROAT, CHAKRA_THIRD_EYE, CHAKRA_CROWN,
    hex_to_rgb,
)

# ─────────────────────────────────────────────────────────────
# Page setup and style injection
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Meditation Trend Pulse", layout="wide")
inject_app_theme()

# ─────────────────────────────────────────────────────────────
# Load Data and Compute Last Updated
# ─────────────────────────────────────────────────────────────
DATA_PATH = "../data/streamlit"
df_trend_long = pd.read_csv(os.path.join(DATA_PATH, "global_trend_summary.csv"))
last_updated = pd.to_datetime(df_trend_long["date"]).max().strftime("%B %d, %Y")





# ✨ Title and tagline
def soft_rgba(hex_color: str, alpha: float = 0.15) -> str:
    rgb = hex_to_rgb(hex_color)
    return f"rgba({rgb}, {alpha})"

# Build soft rainbow gradient
soft_rainbow_gradient = (
    "linear-gradient(135deg, "
    f"{soft_rgba(CHAKRA_ROOT)}, "
    f"{soft_rgba(CHAKRA_SACRAL)}, "
    f"{soft_rgba(CHAKRA_SOLAR_PLEXUS)}, "
    f"{soft_rgba(CHAKRA_HEART)}, "
    f"{soft_rgba(CHAKRA_THROAT)}, "
    f"{soft_rgba(CHAKRA_THIRD_EYE)}, "
    f"{soft_rgba(CHAKRA_CROWN)}"
    ")"
)

page_header(
    title="Meditation Trend Pulse",
    subtitle="Explore how the world is tuning into stillness — from meditation to breathwork.",
)
space(1)

intro_html = """
Meditation Trend Pulse brings you an <strong>interactive, automated dashboard</strong> built with Python, Streamlit, and real Google Trends data.<br/><br/>
This app helps you explore how public interest in meditation, mindfulness, and related practices has evolved <strong>over time, across countries, and through search behavior</strong>.
"""

render_card(
    title_html="Overview",
    body_html=intro_html,
    color_hex=soft_rainbow_gradient,
    side="left",
    center=False,
)

space(2)


# 📌 What You Can Explore — Cards layout
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🌐 What You Can Explore</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <a href="/Global_Trends" target="_self" style="text-decoration: none;">
        <div class='card'>
            <h4>📈 Global Trends</h4>
            <ul>
                <li>5-year trendlines</li>
                <li>Seasonality & peaks</li>
                <li>Growth patterns</li>
            </ul>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='card'>
        <h4>🌍 Country View</h4>
        <ul>
            <li>Top countries by interest</li>
            <li>Proportional comparisons</li>
            <li>Keyword-level breakdown</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='card'>
        <h4>🔍 Related Queries</h4>
        <ul>
            <li>What else people search for</li>
            <li>Fastest-growing queries</li>
            <li>Shared search themes</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 🛠️ How it works
st.markdown("<h2 class='fade-in' style='color:#4B8BBE;'>🛠️ How It Works</h2>", unsafe_allow_html=True)
st.markdown("""
- 📊 <strong>Google Trends API</strong> via `pytrends`  
- ⚙️ <strong>Automated data update</strong> pipeline  
- 📈 <strong>Altair + Streamlit</strong> for interactive charts  
- 📓 <strong>Jupyter Notebooks</strong> for data prep  
""", unsafe_allow_html=True)

# 🔄 Last updated date with animation
st.markdown(f"""
<p class='fade-in' style='color: gray; font-style: italic;'>📅 Last updated: <span style='animation: fadeIn 1.2s ease-in;'>{last_updated}</span></p>
""", unsafe_allow_html=True)

st.markdown("---")

# 👨‍💻 Author and links
st.markdown("""
<h3>👨‍💻 Built by Saayed Alam</h3>
<p style='font-size: 1rem;'>
Data Analyst • Python Enthusiast • Insight Explorer  
🔗 <a href='https://github.com/saayedalam' target='_blank'>GitHub</a> | 
<a href='https://www.linkedin.com/in/saayedalam/' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)