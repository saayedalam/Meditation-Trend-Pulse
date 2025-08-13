# utils/home_ui.py
from __future__ import annotations

from typing import Sequence
import textwrap
import streamlit as st

from utils.ui import (
    render_card,
    hex_to_rgb,
    CHAKRA_ROOT, CHAKRA_SACRAL, CHAKRA_SOLAR_PLEXUS,
    CHAKRA_HEART, CHAKRA_THROAT, CHAKRA_THIRD_EYE, CHAKRA_CROWN,
)

# ─────────────────────────────────────────────────────────────
# Internal: inject pulsing chakra CSS once
# ─────────────────────────────────────────────────────────────
def _inject_home_css_once() -> None:
    if st.session_state.get("_home_css_injected"):
        return
    st.markdown(
        """
        <style>
        @media (prefers-reduced-motion: reduce) {
          .chakra-pulse { animation: none !important; }
        }
        .chakra-pulse {
          display: inline-block;
          background: linear-gradient(
            90deg,
            #E53935, #F57C00, #FBC02D, #43A047, #1E88E5, #5E35B1, #7C3AED, #E53935
          );
          background-size: 400% 100%;
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
          -webkit-text-fill-color: transparent;
          animation: chakraShift 8s linear infinite;
          will-change: background-position;
        }
        @keyframes chakraShift {
          0%   { background-position:   0% 50%; }
          100% { background-position: 100% 50%; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["_home_css_injected"] = True


# ─────────────────────────────────────────────────────────────
# 1) Animated header
# ─────────────────────────────────────────────────────────────
def render_home_header(
    *,
    title: str = "Meditation Trend Pulse",
    subtitle: str = "Explore how the world is tuning into stillness — from meditation to breathwork.",
) -> None:
    _inject_home_css_once()
    st.markdown(
        f"""
        <div style="text-align:center; padding: 2.5rem 0;">
          <h1 class="chakra-pulse" style="font-size:2.8rem; font-weight:700; margin:0;">
            {title}
          </h1>
          <p style="font-size:1.2rem; color:#666; max-width:760px; margin:0.35rem auto 0;">
            {subtitle}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# 2) Intro card (7‑chakra gradient + nav tiles)
# ─────────────────────────────────────────────────────────────
def render_home_intro_card(
    *,
    topic_tags=("Google Trends", "Python + Streamlit", "Altair Charts", "Weekly Updates"),
):
    chakra_hexes = [
        CHAKRA_ROOT, CHAKRA_SACRAL, CHAKRA_SOLAR_PLEXUS,
        CHAKRA_HEART, CHAKRA_THROAT, CHAKRA_THIRD_EYE, CHAKRA_CROWN
    ]
    chakra_rgba_stops = ", ".join([f"rgba({hex_to_rgb(h)},0.08)" for h in chakra_hexes])

    pills_html = "".join(
        f'<span style="font-size:0.85rem; padding:0.28rem 0.55rem; border-radius:999px; background:#ffffffcc; color:#374151;">{t}</span>'
        for t in topic_tags
    )

    intro_html = f"""
<div style="background:linear-gradient(135deg,{chakra_rgba_stops}); border-radius:12px; padding:1.25rem;">
  <div style="max-width:720px; margin:0 auto; text-align:center;">
    <div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin:-0.15rem 0 0.8rem 0;">{pills_html}</div>
    <p style="font-size:1.08rem; line-height:1.85; margin:0.2rem 0 0.9rem 0; color:#2e2e2e;">
      Meditation Trend Pulse is an <strong>interactive, automated dashboard</strong> that visualizes real search behavior around
      <strong>meditation</strong>, <strong>mindfulness</strong>, and <strong>breathwork</strong>. Explore long-term growth, seasonal patterns,
      and spikes tied to cultural moments.
    </p>
    <style>
      .home-grid {{
        display:grid;
        width: 100%;  
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); 
        gap:10px;
        align-items:stretch;
      }}
      @media (max-width:860px) {{ .home-grid {{ grid-template-columns: repeat(3, minmax(165px,1fr)); }} }}
      @media (max-width:640px) {{ .home-grid {{ grid-template-columns: repeat(2, minmax(165px,1fr)); }} }}
      @media (max-width:420px) {{ .home-grid {{ grid-template-columns: 1fr; }} }}
    </style>
    <div class="home-grid">
      <a href="/Global_Trends" target="_self" style="text-decoration:none; display:block; height:100%;">
        <div style="background:#ffffffdd; border-left:6px solid {CHAKRA_HEART}; border-radius:12px; padding:0.8rem 0.9rem; box-shadow:0 2px 8px rgba(0,0,0,0.04); height:100%; display:flex; flex-direction:column; justify-content:center;">
          <div style="font-weight:700; margin-bottom:0.2rem; color:#1f2937;">📈 Global Trends</div>
          <div style="font-size:0.95rem; color:#4b5563;">Peaks, seasonality, growth</div>
        </div>
      </a>
      <a href="/Country_Trends" target="_self" style="text-decoration:none; display:block; height:100%;">
        <div style="background:#ffffffdd; border-left:6px solid {CHAKRA_THROAT}; border-radius:12px; padding:0.8rem 0.9rem; box-shadow:0 2px 8px rgba(0,0,0,0.04); height:100%; display:flex; flex-direction:column; justify-content:center;">
          <div style="font-weight:700; margin-bottom:0.2rem; color:#1f2937;">🌍 Country View</div>
          <div style="font-size:0.95rem; color:#4b5563;">Top countries & comparisons</div>
        </div>
      </a>
      <a href="/Related_Queries" target="_self" style="text-decoration:none; display:block; height:100%;">
        <div style="background:#ffffffdd; border-left:6px solid {CHAKRA_THIRD_EYE}; border-radius:12px; padding:0.8rem 0.9rem; box-shadow:0 2px 8px rgba(0,0,0,0.04); height:100%; display:flex; flex-direction:column; justify-content:center;">
          <div style="font-weight:700; margin-bottom:0.2rem; color:#1f2937;">🔍 Related Queries</div>
          <div style="font-size:0.95rem; color:#4b5563;">What else people search</div>
        </div>
      </a>
      <a href="/Final_Insights" target="_self" style="text-decoration:none; display:block; height:100%;">
        <div style="background:#ffffffdd; border-left:6px solid {CHAKRA_CROWN}; border-radius:12px; padding:0.8rem 0.9rem; box-shadow:0 2px 8px rgba(0,0,0,0.04); height:100%; display:flex; flex-direction:column; justify-content:center;">
          <div style="font-weight:700; margin-bottom:0.2rem; color:#1f2937;">🧠 Final Insights</div>
          <div style="font-size:0.95rem; color:#4b5563;">Big takeaways & reflection</div>
        </div>
      </a>
    </div>
  </div>
</div>
"""

    render_card(
        title_html="Project Overview",
        body_html=intro_html,
        color_hex=CHAKRA_ROOT,
        side=None,
        center=True,
    )

# ─────────────────────────────────────────────────────────────
# 3) Author + links
# ─────────────────────────────────────────────────────────────
def render_home_author_card(
    *,
    name_html: str = '<a href="https://www.datascienceportfol.io/saayedalam" target="_blank" rel="noopener noreferrer" style="color:#7b3fe4; text-decoration:none;">Saayed Alam</a>',
    tagline_html: str = "<em>Data Analyst • Machine Learning Explorer • Interactive Dashboard Creator</em>",
    github_url: str = "https://github.com/saayedalam/Meditation-Trend-Pulse",
    linkedin_url: str = "https://www.linkedin.com/in/saayedalam/",
) -> None:
    author_html = f"""
    <div style='text-align:center; margin-top:2rem; padding:1.5rem; 
                background: linear-gradient(135deg, rgba(131,58,180,0.05), rgba(253,29,29,0.05), rgba(252,176,69,0.05));
                border-radius: 14px; 
                box-shadow: 0 4px 16px rgba(0,0,0,0.04);'>

      <h3 style='margin-bottom:0.4rem; font-size:1.4rem; font-weight:700;'>
        👨‍💻 Built by {name_html}
      </h3>
      
      <p style='font-size:1rem; color:#444; margin-bottom:0.8rem;'>
        {tagline_html}
      </p>

      <p style='font-size:1.05rem; font-weight:500;'>
        🔗 
        <a href='{github_url}' target='_blank' rel="noopener noreferrer" style='color:#0366d6; text-decoration:none;'>GitHub</a> 
        &nbsp;|&nbsp;
        <a href='{linkedin_url}' target='_blank' rel="noopener noreferrer" style='color:#0a66c2; text-decoration:none;'>LinkedIn</a>
      </p>
    </div>
    """
    st.markdown(textwrap.dedent(author_html).strip(), unsafe_allow_html=True)