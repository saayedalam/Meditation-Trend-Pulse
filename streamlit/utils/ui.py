# utils/ui.py
"""
Shared UI utilities for Meditation Trend Pulse (Streamlit).
Centralizes visual style and common layout helpers used across pages.
"""

import os
from datetime import datetime
from contextlib import contextmanager
from typing import Optional

import pandas as pd
import pycountry
import streamlit as st

# ====== Layout ======
CARD_MAX_WIDTH = "850px"

# ====== Default URLs (can be overridden) ======
GITHUB_URL_DEFAULT = "https://github.com/saayedalam"
PORTFOLIO_URL_DEFAULT = "https://saayedalam.me"
LINKEDIN_URL_DEFAULT = "https://www.linkedin.com/in/saayedalam/"

# ====== Chakra Palette (7) ======
CHAKRA_ROOT = "#E53935"          # Red
CHAKRA_SACRAL = "#F57C00"        # Orange
CHAKRA_SOLAR_PLEXUS = "#FBC02D"  # Yellow
CHAKRA_HEART = "#43A047"         # Green
CHAKRA_THROAT = "#1E88E5"        # Blue
CHAKRA_THIRD_EYE = "#5E35B1"     # Indigo
CHAKRA_CROWN = "#7C3AED"         # Violet

CHAKRAS = [
    {"name": "Root", "hex": CHAKRA_ROOT},
    {"name": "Sacral", "hex": CHAKRA_SACRAL},
    {"name": "Solar Plexus", "hex": CHAKRA_SOLAR_PLEXUS},
    {"name": "Heart", "hex": CHAKRA_HEART},
    {"name": "Throat", "hex": CHAKRA_THROAT},
    {"name": "Third Eye", "hex": CHAKRA_THIRD_EYE},
    {"name": "Crown", "hex": CHAKRA_CROWN},
]

# ====== Base Theme ======
def inject_app_theme() -> None:
    """Inject base CSS styles and (once per page load) collapse the sidebar."""
    st.markdown(
        f"""
        <style>
        @media (prefers-reduced-motion: reduce) {{
          * {{
            animation-duration: 0.001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.001ms !important;
            scroll-behavior: auto !important;
          }}
        }}

        @keyframes fadeUp {{
            0% {{opacity: 0; transform: translateY(10px);}}
            100% {{opacity: 1; transform: translateY(0);}}
        }}

        .fade-in {{ animation: fadeUp 0.6s ease-out; }}

        .chakra-card {{
            border-radius: 14px;
            padding: 1.5rem 2rem;
            margin: 1.5rem auto;
            max-width: {CARD_MAX_WIDTH};
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
                         Ubuntu, Cantarell, "Helvetica Neue", Arial, "Apple Color Emoji",
                         "Segoe UI Emoji", "Segoe UI Symbol", sans-serif;
            background: #fff;
        }}

        .chakra-card a {{ color: #4B8BBE; text-decoration: none; }}
        .chakra-card a:hover {{ text-decoration: underline; }}

        .mtp-card-wrap {{
            max-width: {CARD_MAX_WIDTH};
            margin-left: auto;
            margin-right: auto;
        }}
        .mtp-card-wrap .stTextArea,
        .mtp-card-wrap .stTextInput,
        .mtp-card-wrap .stSelectbox,
        .mtp-card-wrap .stMultiSelect,
        .mtp-card-wrap .stSlider,
        .mtp-card-wrap .stNumberInput,
        .mtp-card-wrap .stDateInput,
        .mtp-card-wrap .stColorPicker,
        .mtp-card-wrap .stForm,
        .mtp-card-wrap .stDataFrame,
        .mtp-card-wrap .element-container,
        .mtp-card-wrap .stMarkdown,
        .mtp-card-wrap .stButton {{
            max-width: {CARD_MAX_WIDTH};
            margin-left: auto;
            margin-right: auto;
        }}
        .mtp-card-wrap .stButton > button {{
            display: block;
            margin-left: auto;
            margin-right: auto;
        }}

        .chakra-card-section {{
            padding: 1.25rem 1.5rem;
            border-radius: 10px;
            color: #2e2e2e;
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
            animation: fadeUp 1s ease-out;
            max-width: 900px;
            margin: 1rem auto 2rem auto;
        }}
        .chakra-card-section p {{ font-size: 1.05rem; }}
        .chakra-card-section ul {{ margin-top: 0; padding-left: 1.2rem; }}

        /* Once-per-app table styles (CSS dedupe) */
        .mtp-centered-table table thead th {{
            text-align: center !important;
            vertical-align: middle;
        }}
        .mtp-centered-table table tr:hover {{
            background-color: #f3f0ff !important;
            transition: background-color 0.3s ease;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "_mtp_sidebar_collapsed" not in st.session_state:
        st.session_state["_mtp_sidebar_collapsed"] = True
        st.markdown(
            """
            <script>
            (function() {
              const doc = window.parent.document;
              function collapse() {
                const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
                const toggle  = doc.querySelector('button[aria-label="Close sidebar"]')
                              || doc.querySelector('button[aria-label="Open sidebar"]');
                if (sidebar && sidebar.offsetWidth > 0 && toggle && toggle.getAttribute('aria-label') === 'Close sidebar') {
                  toggle.click();
                }
              }
              setTimeout(collapse, 60);
              setTimeout(collapse, 350);
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )

# ====== Spacing ======
def space(rem: float = 2.0) -> None:
    """Add vertical spacing (in rem units)."""
    try:
        rem = float(rem)
    except Exception:
        rem = 2.0
    st.markdown(f"<div style='margin-top:{rem}rem;'></div>", unsafe_allow_html=True)

def horizontal_rule() -> None:
    """Render a simple horizontal rule."""
    st.markdown("---")

# ====== File mtime helper ======
def last_updated_from_file(path: str) -> str:
    """Return last modified date for a file in 'Mon DD, YYYY' format (fallback: today)."""
    try:
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts).strftime("%b %d, %Y")
    except Exception:
        return datetime.now().strftime("%b %d, %Y")

# ====== Soft date span ======
def soft_date_span(date_str: str) -> str:
    """Return a muted, italic HTML span for inline date metadata."""
    safe = (date_str or "").replace("<", "&lt;").replace(">", "&gt;")
    return f"<span style='color:#777; font-size:0.9rem; font-style:italic;'>({safe})</span>"

# ====== Last-updated line ======
def last_updated_html(date_str: Optional[str]) -> str:
    """Return a standardized 'Last updated' line or empty string."""
    if not date_str:
        return ""
    safe = (date_str or "").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f"<p style='text-align:center; font-size:0.85rem; color:#888; "
        f"margin:0.75rem 0 0 0;'>📅 Last updated: {safe}</p>"
    )

# ====== Page header ======
def page_header(title: str, subtitle: str) -> None:
    """Render a centered page header with fade-in effect."""
    st.markdown(
        f"""
        <div class="fade-in" style="text-align: center; padding: 2.5rem 0;">
            <h1 style="font-size: 2.8rem; color: #4B8BBE; font-weight: 700;">{_escape_minimal(title)}</h1>
            <p style="font-size: 1.2rem; color: #666; max-width: 760px; margin: 0 auto;">
                {_escape_minimal(subtitle)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ====== Shared panel style builder ======
def _soft_gradient_css(hex_color: str, a1: float = 0.12, a2: float = 0.04, angle: str = "to right") -> str:
    """Return a linear-gradient CSS string using a hex color and alpha stops."""
    rgb = hex_to_rgb(hex_color)
    return f"linear-gradient({angle}, rgba({rgb},{a1}), rgba({rgb},{a2}))"

def _panel_style(
    accent_hex: str,
    side: str,
    *,
    max_width: str = CARD_MAX_WIDTH,
    padding: str = "1.5rem 2rem",
    border_px: int = 6,
) -> str:
    """Build the common gradient + border style for cards/footers."""
    side = side if side in ("left", "right") else "left"
    angle = "to right" if side == "left" else "to left"
    return (
        f"border-{side}: {border_px}px solid {accent_hex};"
        f"background: {_soft_gradient_css(accent_hex, 0.08, 0.02, angle)};"
        f"max-width: {max_width}; padding: {padding};"
    )

# ====== Card component ======
def render_card(
    title_html: str,
    body_html: str,
    color_hex: str,
    side: str = "left",
    center: bool = False,
) -> None:
    """Render a colored accent card with a soft gradient tint and optional side border."""
    if side is None or str(side).lower().strip() == "none":
        side_norm = None
    else:
        side_norm = str(side).lower().strip()
        if side_norm not in ("left", "right"):
            side_norm = "left"

    safe_body = body_html or ""
    text_align = "center" if center else "left"
    maxw = "740px" if center else "900px"

    if side_norm:
        angle = "to right" if side_norm == "left" else "to left"
        border_style = f"border-{side_norm}: 6px solid {color_hex}; "
        bg_style = f"background: {_soft_gradient_css(color_hex, 0.12, 0.04, angle)}; "
    else:
        border_style = ""
        bg_style = f"background: rgba({hex_to_rgb(color_hex)},0.04); "

    style = f"{border_style}{bg_style}max-width: {CARD_MAX_WIDTH}; padding: 1.5rem 2rem;"

    title_block = ""
    if title_html and title_html.strip():
        title_block = f'<h3 style="color:{color_hex}; margin-bottom: 0.6rem;">{title_html}</h3>'

    html_content = f"""<div class="chakra-card" style="{style} text-align:{text_align};">
{title_block}
<div style="font-size: 1.05rem; line-height: 1.8; color: #333; max-width: {maxw}; margin: 0 auto;">
{safe_body}
</div>
</div>"""
    st.markdown(html_content, unsafe_allow_html=True)

# ====== Section helpers ======
def render_section_header(title: str, emoji: str, color_hex: str = "#4B8BBE") -> None:
    """Render a styled section header with emoji and color."""
    html = f"""
    <h2 class="fade-in" style="color:{color_hex};">
        {emoji} {_escape_minimal(title)}
    </h2>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_section_card(
    *,
    icon: str,
    content_paragraph: str,
    content_list: list[str],
    max_width: str = "900px",
    gradient_color: str = CHAKRA_HEART,
) -> None:
    """Section info card with soft gradient background and fade-in."""
    list_html = "".join(f"<li>{_escape_minimal(item)}</li>" for item in content_list)
    html = f"""
    <div class="chakra-card-section fade-in"
         style="max-width:{max_width}; margin:1rem auto 2rem auto;
                background: {_soft_gradient_css(gradient_color, 0.12, 0.05, "135deg")};
                border-radius:10px; color:#2e2e2e; box-shadow:0 4px 10px rgba(0,0,0,0.04);
                padding:1.25rem 1.5rem;">
        <p><span style="font-size: 1.4rem;">{icon}</span> {_escape_minimal(content_paragraph)}</p>
        <ul>{list_html}</ul>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_centered_styled_table(df_html: str, max_width: str = "600px") -> None:
    """Center a DataFrame (already rendered as HTML) with a max-width and hover feedback."""
    if not df_html:
        return
    container_html = f"""
    <div class="mtp-centered-table" style="display:flex; justify-content:center; width:100%; margin-top:1rem; margin-bottom:1rem;">
      <div style="max-width:{max_width}; width:100%;">{df_html}</div>
    </div>
    """
    st.markdown(container_html, unsafe_allow_html=True)

def style_percent_change(val: int | float) -> str:
    """Return an HTML span with an emoji and color based on sign of percent change."""
    s = f"{val:.1f}%".rstrip("0").rstrip(".")
    if val > 0:
        return f"<span style='color:green;'>📈 +{s}</span>"
    if val < 0:
        return f"<span style='color:red;'>📉 {s}</span>"
    return f"<span style='color:gray;'>➖ {s}</span>"

def format_interest(val) -> str:
    """CSS style for bold, centered cells in pandas Styler."""
    if pd.notnull(val):
        return "font-weight: bold; text-align: center;"
    return ""

# ====== Footer components ======
def render_site_footer(
    *,
    github_url: str = GITHUB_URL_DEFAULT,
    linkedin_url: Optional[str] = LINKEDIN_URL_DEFAULT,
    portfolio_url: str = PORTFOLIO_URL_DEFAULT,
    accent_hex: str = CHAKRA_THROAT,
    show_last_updated: Optional[str] = None,
) -> None:
    """Footer with links and optional timestamp."""
    style = _panel_style(accent_hex, "left", max_width="900px", padding="1.25rem 1.5rem", border_px=5)
    links_html = [
        f"🌐 <a href='{_escape_url(portfolio_url)}' target='_blank'><strong>saayedalam.me</strong></a>",
        f"💻 <a href='{_escape_url(github_url)}' target='_blank'><strong>GitHub</strong></a>",
    ]
    if linkedin_url:
        links_html.append(f"🔗 <a href='{_escape_url(linkedin_url)}' target='_blank'><strong>LinkedIn</strong></a>")

    st.markdown(
        f"""
        <div style="margin-top:2.25rem; {style} margin-left:auto; margin-right:auto; position:relative;
                    box-shadow:0 2px 12px rgba(0,0,0,0.03); color:#333; text-align:center; border-radius:12px;">
          <div style="font-size:0.98rem; color:#555;">
            {" &nbsp;•&nbsp; ".join(links_html)}
          </div>
          {last_updated_html(show_last_updated)}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_custom_footer(
    *,
    show_last_updated: Optional[str] = None,
    color_hex: str = CHAKRA_HEART,
) -> None:
    """Footer variant with descriptive text and dynamic accent color."""
    rgb = hex_to_rgb(color_hex)
    st.markdown(
        f"""
        <style>
        .footer-watermark-icon {{
            position: absolute; bottom: 12px; right: 14px;
            opacity: 0.08; width: 42px;
        }}
        .custom-footer {{
            margin-top: 3.5rem;
            padding: 1.75rem 2rem 1.5rem 2rem;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba({rgb},0.1), rgba({rgb},0.03), rgba({rgb},0.02));
            border-right: 5px solid {color_hex};
            max-width: 880px; margin-left: auto; margin-right: auto;
            position: relative; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
            color: #333; text-align: left;
        }}
        .custom-footer h4 {{ margin: 0 0 0.8rem 0; color: {color_hex}; }}
        .custom-footer p {{ margin: 0 0 0.5rem 0; font-size: 1.05rem; }}
        .custom-footer ul {{ margin: 0 0 0.5rem 1.25rem; padding-left: 0; font-size: 0.98rem; color: #444; }}
        .custom-footer small {{ font-size: 0.93rem; color: #666; font-style: italic; margin-top: 1rem; display: block; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="custom-footer">
          <img src="https://img.icons8.com/ios-glyphs/30/7C3AED/search--v1.png"
               class="footer-watermark-icon" alt="Search Icon" />
          <h4>📊 Understanding the Interest Score</h4>
          <p>Scores range from <strong>0 to 100</strong> and show how popular a search term was — <strong>relative to its own peak</strong>.</p>
          <ul>
            <li><strong>100</strong> = Highest interest ever recorded</li>
            <li><strong>50</strong> = Half as popular as peak</li>
            <li><strong>0</strong> = Not enough data</li>
          </ul>
          <small>This score is normalized — not raw volume — helping you spot peaks, not totals.</small>
          {last_updated_html(show_last_updated)}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ====== Card-width wrappers ======
def begin_card_width() -> None:
    """Open a wrapper that constrains following widgets to card width."""
    st.markdown("<div class='mtp-card-wrap'>", unsafe_allow_html=True)

def end_card_width() -> None:
    """Close the card-width wrapper."""
    st.markdown("</div>", unsafe_allow_html=True)

@contextmanager
def card_width():
    """Context manager to constrain enclosed widgets to card width."""
    begin_card_width()
    try:
        yield
    finally:
        end_card_width()

# ====== Helpers ======
def hex_to_rgb(hex_color: str) -> str:
    """Convert hex color (e.g., '#43A047' or '#3a7') to 'R,G,B'."""
    if not isinstance(hex_color, str):
        raise ValueError("hex_color must be a string like '#RRGGBB' or '#RGB'.")
    h = hex_color.lstrip("#").strip()
    if len(h) == 3:
        h = "".join([ch * 2 for ch in h])
    if len(h) != 6:
        raise ValueError(f"Invalid hex color: {hex_color!r}")
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
    except Exception as e:
        raise ValueError(f"Invalid hex color: {hex_color!r}") from e
    return f"{r},{g},{b}"

def get_flag_emoji(country_name: str) -> str:
    """Return the emoji flag for a given country name using ISO alpha-2 codes."""
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            country = pycountry.countries.search_fuzzy(country_name)[0]
        alpha2 = country.alpha_2.upper()
        return chr(127397 + ord(alpha2[0])) + chr(127397 + ord(alpha2[1]))
    except Exception:
        return ""

# ====== Minimal escaping ======
def _escape_minimal(text: Optional[str]) -> str:
    """Minimal HTML escaping for titles; allows emojis and punctuation."""
    if text is None:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _escape_url(url: Optional[str]) -> str:
    """Small sanitizer for URLs used in href/src."""
    if not url:
        return ""
    return url.replace('"', "%22").replace("'", "%27")

# ====== Public API ======
__all__ = [
    # constants
    "CARD_MAX_WIDTH",
    "GITHUB_URL_DEFAULT", "PORTFOLIO_URL_DEFAULT", "LINKEDIN_URL_DEFAULT",
    # palettes
    "CHAKRA_ROOT", "CHAKRA_SACRAL", "CHAKRA_SOLAR_PLEXUS", "CHAKRA_HEART",
    "CHAKRA_THROAT", "CHAKRA_THIRD_EYE", "CHAKRA_CROWN", "CHAKRAS",
    # theme + layout
    "inject_app_theme", "space", "horizontal_rule", "page_header",
    # meta
    "last_updated_from_file", "soft_date_span", "last_updated_html",
    # components
    "render_card", "render_custom_footer", "render_site_footer",
    # wrappers
    "begin_card_width", "end_card_width", "card_width",
    # helpers
    "hex_to_rgb", "get_flag_emoji",
    # visual sections
    "render_section_header", "render_section_card",
    # styling helpers
    "render_centered_styled_table", "style_percent_change", "format_interest",
]