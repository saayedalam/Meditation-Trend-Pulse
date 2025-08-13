# 🧘 Final Reflections | Meditation Trend Pulse
import os
from datetime import datetime

import streamlit as st

# ⬇️ Shared UI helpers
from utils.ui import (
    inject_app_theme,
    page_header,
    render_card,
    space,
    last_updated_from_file,
    soft_date_span,
    # palette + footer
    CHAKRA_HEART,
    CHAKRA_SOLAR_PLEXUS,
    CHAKRA_SACRAL,
    CHAKRA_ROOT,
    CHAKRA_CROWN,
    CHAKRA_THROAT,
    render_site_footer,
    # context manager for card width
    card_width,
)

from utils.home_ui import render_home_author_card

# ─────────────────────────────────────────────────────────────
# 🔧 Page settings + theme
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Final Reflections | Meditation Trend Pulse", layout="wide")
inject_app_theme()

# ─────────────────────────────────────────────────────────────
# 📁 Data paths + last-updated stamp
# ─────────────────────────────────────────────────────────────
DATA_PATH = "../data/streamlit"
MAIN_DATA_FILE = os.path.join(DATA_PATH, "global_trend_summary.csv")
LAST_UPDATED_STR = last_updated_from_file(MAIN_DATA_FILE)

# Journaling path (ensure directory exists)
JOURNAL_PATH = "../data/journal_entries.txt"
os.makedirs(os.path.dirname(JOURNAL_PATH), exist_ok=True)

# ─────────────────────────────────────────────────────────────
# 🖼 Header
# ─────────────────────────────────────────────────────────────
page_header(
    "✨ Final Reflections",
    "From these insights, we see how meditation and mindfulness trends connect across cultures —"
    "revealing a shared human search for calm and clarity. Now, take a moment to reflect on what these practices mean in your own life."
)

# ─────────────────────────────────────────────────────────────
# 🟩 Card 1 — What We Noticed (Heart)
# ─────────────────────────────────────────────────────────────
render_card(
    title_html=f"🔍 What We Noticed {soft_date_span(f'Since {LAST_UPDATED_STR}')}",
    body_html=(
        "📈 <strong>Breathwork</strong> is becoming a popular gateway into mindfulness, especially after 2020.<br/>"
        "🌍 Interest in <strong>yoga nidra</strong> has spiked in many non‑Western countries — suggesting a broader spiritual search.<br/>"
        "🔄 Terms like <strong>guided meditation</strong> are often co‑searched with topics like <em>anxiety</em>, <em>meaning</em>, or <em>sleep</em>.<br/>"
        "⏳ These patterns reveal a universal desire for <strong>calm, clarity, and connection</strong>."
    ),
    color_hex=CHAKRA_ROOT,
    side="left",
    center=False
)

# ─────────────────────────────────────────────────────────────
# 🟨 Card 2 — Start Your Meditation Journey (Solar Plexus)
# ─────────────────────────────────────────────────────────────
render_card(
    title_html="🌱 Start Your Meditation Journey Today",
    body_html=(
        "Whether you're new or returning, let this be your sign. Take one deep breath. Feel the present moment.<br/>"
        "Even <strong>2 minutes of stillness</strong> can reshape your day."
    ),
    color_hex=CHAKRA_SACRAL,
    side="right",
    center=True
)
# ─────────────────────────────────────────────────────────────
# 🟧 Card 3 — Reflect On Your Journey (Sacral)
# ─────────────────────────────────────────────────────────────
render_card(
    title_html="📝 Reflect On Your Journey",
    body_html="What’s one insight, intention, or realization you’re taking away from this exploration?",
    color_hex=CHAKRA_SOLAR_PLEXUS,
    side="left",
    center=False
)

# 🗒️ Journaling (card-width wrapper between Card 3 and Card 4)
with card_width():
    journal_entry = st.text_area(
        label="Reflection notes", 
        placeholder="Type your reflection here...",
        height=150, 
        key="final_insights_journal",
        label_visibility="visible",
    )
    col_save, col_clear = st.columns(2)

    with col_save:
        if st.button("💾 Save Reflection", use_container_width=True, key="btn_save_reflection"):
            text = (journal_entry or "").strip()
            if not text:
                st.warning("Please write something before saving.")
            else:
                try:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
                        f.write(f"[{ts}] {text}\n---\n")
                    st.success("Reflection saved! 🧘")
                    st.session_state["final_insights_journal"] = ""  # clear after save
                except Exception as e:
                    st.error(f"Could not save your reflection. ({e})")

    with col_clear:
        if st.button("🧹 Clear", use_container_width=True, key="btn_clear_reflection"):
            st.session_state["final_insights_journal"] = ""
            st.toast("Cleared.")

space(0.5)

# ─────────────────────────────────────────────────────────────
# 🟥 Card 4 — Closing Quote (Root)
# ─────────────────────────────────────────────────────────────
render_card(
    title_html="💬 Closing Mantra",
    body_html='“The quieter you become, the more you can hear.” — Ram Dass',
    color_hex=CHAKRA_HEART,
    side="right",
    center=True
)

# ─────────────────────────────────────────────────────────────
# 🔗 Footer
# ─────────────────────────────────────────────────────────────
# Author / links card
render_home_author_card()
