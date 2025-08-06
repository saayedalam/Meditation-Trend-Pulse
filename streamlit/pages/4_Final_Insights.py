# 🧘 Final Reflections | Meditation Trend Pulse

import streamlit as st
import pandas as pd
import os
from utils.ui import inject_base_css

# 🎨 Inject CSS styles
inject_base_css()

# 🌟 Page settings
st.set_page_config(page_title="Final Reflections | Meditation Trend Pulse", layout="wide")

# 📁 Optional journaling save location
JOURNAL_PATH = "../data/journal_entries.txt"

# 🧘‍♀️ Header with consistent styling
st.markdown("""
<div class="fade-in" style="text-align: center; padding: 2.5rem 0;">
    <h1 style="font-size: 2.8rem; color: #4B8BBE; font-weight: 700;">✨ Final Reflections</h1>
    <p style="font-size: 1.2rem; color: #666; max-width: 760px; margin: 0 auto;">
        As we close this exploration, take a moment to reflect on what meditation and mindfulness mean to you — and how global curiosity reveals deeper truths about our shared human experience.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 🧠 Insights (general + themed)
st.markdown("""
<div class="fade-in" style="max-width: 900px; margin: auto;">
    <h3 style="color:#7C3AED;">🔍 What We Noticed</h3>
    <ul style="font-size: 1.05rem; line-height: 1.8;">
        <li>📈 <strong>Breathwork</strong> is becoming a popular gateway into mindfulness, especially after 2020.</li>
        <li>🌍 Interest in <strong>yoga nidra</strong> has spiked in many non-Western countries — suggesting a broader spiritual search.</li>
        <li>🔁 Terms like <strong>guided meditation</strong> are often co-searched with topics like <em>anxiety</em>, <em>meaning</em>, or <em>sleep</em>.</li>
        <li>⏳ These patterns reveal a universal desire for <strong>calm, clarity, and connection</strong>.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 🌱 Call to Action
st.markdown("""
<div class="fade-in" style="text-align: center;">
    <h2 style="color: #10B981; font-weight: 700;">🌱 Start Your Meditation Journey Today</h2>
    <p style="font-size: 1.1rem; color: #444; max-width: 740px; margin: 0 auto;">
        Whether you're new or returning, let this be your sign. Take one deep breath. Feel the present moment. Even 2 minutes of stillness can reshape your day.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 📝 Reflective Journaling
st.markdown("""
<h3 style="color:#4B8BBE;">📝 Reflect on your journey</h3>
<p style='font-size: 1rem; color:#444;'>What’s one insight, intention, or realization you’re taking away from this exploration?</p>
""", unsafe_allow_html=True)

journal_entry = st.text_area("Type your reflection here...", height=150)
if st.button("💾 Save Reflection"):
    with open(JOURNAL_PATH, "a") as f:
        f.write(journal_entry + "\n---\n")
    st.success("Reflection saved! 🧘")

st.markdown("---")

# 🧘‍♀️ Closing Mantra
st.markdown("""
<div style="text-align: center; font-style: italic; font-size: 1.1rem; color: #5B21B6; max-width: 680px; margin: auto;">
    "The quieter you become, the more you can hear." — Ram Dass
</div>
""", unsafe_allow_html=True)

space = lambda: st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
space()

# 🔗 Footer
st.markdown("""
<div style='text-align: center; font-size: 0.95rem; color: #666;'>
    🔗 Explore more of my work at <a href='https://saayedalam.me' target='_blank'><strong>saayedalam.me</strong></a> or follow along at <a href='https://github.com/saayedalam' target='_blank'><strong>GitHub</strong></a>.
</div>
""", unsafe_allow_html=True)