# utils/home_ui.py

import textwrap
import streamlit as st

from utils.ui import (
    render_card,
    hex_to_rgb,
    CHAKRA_ROOT, CHAKRA_SACRAL, CHAKRA_SOLAR_PLEXUS,
    CHAKRA_HEART, CHAKRA_THROAT, CHAKRA_THIRD_EYE, CHAKRA_CROWN,
)


def _inject_home_css_once() -> None:
    """
    Inject CSS for the animated header once per session.
    Respects reduced-motion user preferences.
    """
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


def render_home_header(
    *,
    title: str = "Meditation Trend Pulse",
    subtitle: str = "Explore how the world is tuning into stillness — from meditation to breathwork.",
) -> None:
    """
    Render the page header (animated title + subtitle).
    """
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


def _gradient_stops_rgba() -> str:
    chakra_hexes = [
        CHAKRA_ROOT, CHAKRA_SACRAL, CHAKRA_SOLAR_PLEXUS,
        CHAKRA_HEART, CHAKRA_THROAT, CHAKRA_THIRD_EYE, CHAKRA_CROWN
    ]
    return ", ".join(f"rgba({hex_to_rgb(h)},0.08)" for h in chakra_hexes)


def _pills_html(topic_tags: tuple[str, ...]) -> str:
    return "".join(
        f'<span style="font-size:0.85rem; padding:0.28rem 0.55rem; border-radius:999px; background:#ffffffcc; color:#374151;">{t}</span>'
        for t in topic_tags
    )


def _tile_html(href: str, border_color: str, title: str, subtitle: str) -> str:
    return f"""
      <a href="{href}" target="_self" style="text-decoration:none; display:block; height:100%;">
        <div style="background:#ffffffdd; border-left:6px solid {border_color}; border-radius:12px; padding:0.8rem 0.9rem; box-shadow:0 2px 8px rgba(0,0,0,0.04); height:100%; display:flex; flex-direction:column; justify-content:center;">
          <div style="font-weight:700; margin-bottom:0.2rem; color:#1f2937;">{title}</div>
          <div style="font-size:0.95rem; color:#4b5563;">{subtitle}</div>
        </div>
      </a>
    """.strip()


def render_home_intro_card(
    *,
    topic_tags: tuple[str, ...] = ("Google Trends", "Python + Streamlit", "Altair Charts", "Weekly Updates"),
) -> None:
    """
    Render the overview card with topic tags and navigation tiles.
    """
    pills_html = _pills_html(topic_tags)
    chakra_rgba_stops = _gradient_stops_rgba()

    tiles = [
        _tile_html("/Global_Trends",  CHAKRA_HEART,      "📈 Global Trends",   "Peaks, seasonality, growth"),
        _tile_html("/Country_Trends", CHAKRA_THROAT,     "🌍 Country View",    "Top countries & comparisons"),
        _tile_html("/Related_Queries", CHAKRA_THIRD_EYE, "🔍 Related Queries", "What else people search"),
        _tile_html("/Final_Insights", CHAKRA_CROWN,      "🧠 Final Insights",  "Big takeaways & reflection"),
    ]
    tiles_html = "\n".join(tiles)

    intro_html = f"""
<div style="background:linear-gradient(135deg,{chakra_rgba_stops}); border-radius:12px; padding:1.25rem;">
  <div style="max-width:860px; margin:0 auto; text-align:center;">
    <div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin:-0.15rem 0 0.8rem 0;">{pills_html}</div>
    <p style="font-size:1.08rem; line-height:1.85; margin:0.2rem 0 0.9rem 0; color:#2e2e2e;">
      Meditation Trend Pulse is an <strong>interactive, automated dashboard</strong> that visualizes real search behavior around
      <strong>meditation</strong>, <strong>mindfulness</strong>, and <strong>breathwork</strong>. Explore long-term growth, seasonal patterns,
      and spikes tied to cultural moments.
    </p>
    <style>
      .home-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, min(180px, 1fr));
        gap: 12px;
        align-items: stretch;
        justify-content: center;
        width: 100%;
      }}
    </style>
    <div class="home-grid">
      {tiles_html}
    </div>
  </div>
</div>
""".strip()

    render_card(
        title_html="Project Overview",
        body_html=intro_html,
        color_hex=CHAKRA_ROOT,
        side=None,
        center=True,
    )


def render_home_author_card(
    *,
    name_html: str = '<a href="https://www.datascienceportfol.io/saayedalam" target="_blank" rel="noopener noreferrer" style="color:#7b3fe4; text-decoration:none;">Saayed Alam</a>',
    tagline_html: str = "<em>Data Analyst • Machine Learning Explorer • Interactive Dashboard Creator</em>",
    github_url: str = "https://github.com/saayedalam/Meditation-Trend-Pulse",
    linkedin_url: str = "https://www.linkedin.com/in/saayedalam/",
) -> None:
    """
    Render the author card with name and external links.
    """
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