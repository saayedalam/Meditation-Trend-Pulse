# 🏠 Homepage: Meditation Trend Pulse

import streamlit as st
import datetime  

# Page config must be the first Streamlit call
st.set_page_config(page_title="Meditation Trend Pulse", layout="wide")

# Heartbeat: log when ?ping=1 is present (for UptimeRobot)
params = st.experimental_get_query_params()
if "ping" in params:  # e.g., https://.../?ping=1
    print(f"✅ Ping received at {datetime.datetime.now().isoformat(timespec='seconds')}")

from utils.ui import inject_app_theme
from utils.home_ui import (
    render_home_header,
    render_home_intro_card,
    render_home_author_card,
)

# Global styles (shared across the app)
inject_app_theme()

# Animated title + subtitle
render_home_header()

# Intro gradient card with nav tiles
render_home_intro_card()

# Author / links card
render_home_author_card()