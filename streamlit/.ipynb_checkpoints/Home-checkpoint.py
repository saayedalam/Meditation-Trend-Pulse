# 🏠 Homepage: Meditation Trend Pulse

import streamlit as st
import pandas as pd
import os
#from utils.ui import inject_base_css  # 🔁 Reusable CSS/animation styles

# 📁 Load trend data to extract last updated date
DATA_PATH = "../data/streamlit"
df_trend_long = pd.read_csv(os.path.join(DATA_PATH, "global_trend_summary.csv"))
last_updated = pd.to_datetime(df_trend_long['date']).max().strftime("%B %d, %Y")

# 🌐 Set Streamlit config and inject global styles
st.set_page_config(page_title="Meditation Trend Pulse", layout="wide")
#inject_base_css()

# 🖼️ Banner image (custom local image)
current_dir = os.path.dirname(__file__)
image_path = os.path.join(current_dir, "assets", "meditation_trend_pulse_banner.png")
st.image(image_path, use_container_width=True)



# ✨ Title and tagline
st.markdown("""
<div class="fade-in">
    <h1 style='font-size: 2.5rem; color: #4B8BBE;'>Meditation Trend Pulse</h1>
    <p style='font-size: 1.2rem;'>Explore how the world is tuning into stillness — from meditation to breathwork.</p>
</div>
""", unsafe_allow_html=True)

# 📖 Project summary
st.markdown("""
<div class="fade-in">
<p>Meditation Trend Pulse brings you an <strong>interactive, automated dashboard</strong> built with Python, Streamlit, and real Google Trends data.</p>
<p>This app helps you explore how public interest in meditation, mindfulness, and related practices has evolved <strong>over time, across countries, and through search behavior</strong>.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

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

# 💬 Floating FAQ button
st.markdown("""
<a class='floating-button' href='#' title='Need help navigating?'>💬 FAQ / Help</a>
""", unsafe_allow_html=True)