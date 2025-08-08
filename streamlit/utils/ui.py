"""
Shared UI utilities for Meditation Trend Pulse (Streamlit)
- Centralizes visual style and common layout helpers
- Safe to import across all pages (Home, Global, Country, Related, Final Insights)
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

import streamlit as st

# ========== 📏 Layout constants ==========
CARD_MAX_WIDTH = "850px"

# ========== 🎨 Chakra Palette (7) ==========
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

# ========== 🎨 Base Theme ==========
def inject_app_theme() -> None:
    """
    Inject base CSS styles for all pages:
    - Fade-in animation (respects prefers-reduced-motion)
    - Card base styling (rounded, shadow, width)
    - Consistent font stack
    - .mtp-card-wrap helper to align widgets to card width
    """
    st.markdown(
        f"""
        <style>
        /* Motion: respect user preference */
        @media (prefers-reduced-motion: reduce) {{
          * {{
            animation-duration: 0.001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.001ms !important;
            scroll-behavior: auto !important;
          }}
        }}

        /* Fade-in animation */
        @keyframes fadeUp {{
            0% {{opacity: 0; transform: translateY(10px);}}
            100% {{opacity: 1; transform: translateY(0);}}
        }}
        .fade-in {{animation: fadeUp 0.6s ease-out;}}

        /* Card base */
        .chakra-card {{
            border-radius: 14px;
            padding: 1.5rem 2rem;
            margin: 1.5rem auto;
            max-width: {CARD_MAX_WIDTH};
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
                         Ubuntu, Cantarell, "Helvetica Neue", Arial, "Apple Color Emoji",
                         "Segoe UI Emoji", "Segoe UI Symbol", sans-serif;
            background: #fff; /* keeps charts readable if parent theme changes */
        }}

        .chakra-card a {{ color: #4B8BBE; text-decoration: none; }}
        .chakra-card a:hover {{ text-decoration: underline; }}

        /* ------- Card-width wrapper -------
           Use begin_card_width()/end_card_width() or card_width() to wrap widgets
           so they align with card width and center on the page.
        */
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
        </style>
        """,
        unsafe_allow_html=True,
    )

# ========== 📏 Spacing ==========
def space(rem: float = 2.0) -> None:
    """Add vertical spacing (in rem units)."""
    try:
        rem = float(rem)
    except Exception:
        rem = 2.0
    st.markdown(f"<div style='margin-top:{rem}rem;'></div>", unsafe_allow_html=True)

# ========== 🕒 File mtime helper ==========
def last_updated_from_file(path: str) -> str:
    """Return last modified date for a file in 'Mon DD, YYYY' format (fallback: today)."""
    try:
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts).strftime("%b %d, %Y")
    except Exception:
        return datetime.now().strftime("%b %d, %Y")

# ========== 🪶 Soft date span ==========
def soft_date_span(date_str: str) -> str:
    """Return a muted, italic HTML span for inline date metadata."""
    safe = (date_str or "").replace("<", "&lt;").replace(">", "&gt;")
    return f"<span style='color:#777; font-size:0.9rem; font-style:italic;'>({safe})</span>"

# ========== 🧾 Last-updated line ==========
def last_updated_html(date_str: Optional[str]) -> str:
    """Return the standardized 'Last updated' line or empty string."""
    if not date_str:
        return ""
    safe = (date_str or "").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f"<p style='text-align:center; font-size:0.85rem; color:#888; "
        f"margin:0.75rem 0 0 0;'>📅 Last updated: {safe}</p>"
    )

# ========== 🖼 Page header ==========
def page_header(title: str, subtitle: str) -> None:
    """Render a centered page header with fade-in effect."""
    st.markdown(
        f"""
        <div class="fade-in" style="text-align: center; padding: 2.5rem 0;">
            <h1 style="font-size: 2.8rem; color: #4B8BBE; font-weight: 700;">{_escape_minimal(title)}</h1>
            <p style="font-size: 1.2rem; color: #666; max-width: 760px; margin: 0 auto;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========== 🧩 Shared panel style builder ==========
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
    rgb = hex_to_rgb(accent_hex)
    gradient_dir = "to right" if side == "left" else "to left"
    return (
        f"border-{side}: {border_px}px solid {accent_hex};"
        f"background: linear-gradient({gradient_dir}, rgba({rgb},0.08), rgba({rgb},0.02));"
        f"max-width: {max_width}; padding: {padding};"
    )

# ========== 🗂 Card component ==========
def render_card(
    title_html: str,
    body_html: str,
    color_hex: str,
    side: str = "left",
    center: bool = False,
) -> None:
    """
    Render a colored accent card with a soft gradient tint.
    Used across all pages for consistent card styling (avoid re-implementing).
    """
    side_norm = (side or "left").lower().strip()
    if side_norm not in ("left", "right"):
        side_norm = "left"

    safe_body = body_html or ""

    style = _panel_style(color_hex, side_norm, max_width=CARD_MAX_WIDTH, padding="1.5rem 2rem", border_px=6)
    text_align = "center" if center else "left"
    maxw = "740px" if center else "900px"

    title_block = ""
    if title_html and title_html.strip():
        title_block = f'<h3 style="color:{color_hex}; margin-bottom: 0.6rem;">{title_html}</h3>'

    # Build HTML content carefully with no extra indentation inside triple quotes
    html_content = f"""<div class="chakra-card" style="{style} text-align:{text_align};">
{title_block}
<div style="font-size: 1.05rem; line-height: 1.8; color: #333; max-width: {maxw}; margin: 0 auto;">
{safe_body}
</div>
</div>"""

    st.markdown(html_content, unsafe_allow_html=True)
# ========== 🪪 Footer component (site links) ==========
def render_site_footer(
    *,
    github_url: str = "https://github.com/saayedalam",
    linkedin_url: Optional[str] = None,
    portfolio_url: str = "https://saayedalam.me",
    accent_hex: str = CHAKRA_THROAT,  # 5th in sequence after the four cards
    show_last_updated: Optional[str] = None,
) -> None:
    """
    Branded footer block with subtle gradient, accent border (left), and optional timestamp.
    Uses the shared panel style to remove duplication.
    """
    style = _panel_style(accent_hex, "left", max_width="900px", padding="1.25rem 1.5rem", border_px=5)

    links_html = [
        f"🌐 <a href='{_escape_url(portfolio_url)}' target='_blank'><strong>saayedalam.me</strong></a>",
        f"💻 <a href='{_escape_url(github_url)}' target='_blank'><strong>GitHub</strong></a>",
    ]
    if linkedin_url:
        links_html.append(
            f"🔗 <a href='{_escape_url(linkedin_url)}' target='_blank'><strong>LinkedIn</strong></a>"
        )

    st.markdown(
        f"""
        <div style="
            margin-top: 2.25rem;
            {style}
            margin-left: auto;
            margin-right: auto;
            position: relative;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
            color: #333;
            text-align: center;
            border-radius: 12px;
        ">
          <div style="font-size: 0.98rem; color: #555;">
            {" &nbsp;•&nbsp; ".join(links_html)}
          </div>
          {last_updated_html(show_last_updated)}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========== 🧱 Card-width container helpers ==========
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

# ========== 🎨 Helper: hex to RGB ==========
def hex_to_rgb(hex_color: str) -> str:
    """Convert HEX color (e.g., '#43A047' or '#3a7') to 'R,G,B'."""
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

# ========== 🔒 Minimal escaping ==========
def _escape_minimal(text: Optional[str]) -> str:
    """Minimal HTML escaping for titles; allows emojis and punctuation."""
    if text is None:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _escape_url(url: Optional[str]) -> str:
    """Very small sanitizer for URLs used in href/src."""
    if not url:
        return ""
    return url.replace('"', "%22").replace("'", "%27")

# ========== 📦 Public API ==========
__all__ = [
    # constants
    "CARD_MAX_WIDTH",
    # palettes
    "CHAKRA_ROOT", "CHAKRA_SACRAL", "CHAKRA_SOLAR_PLEXUS", "CHAKRA_HEART",
    "CHAKRA_THROAT", "CHAKRA_THIRD_EYE", "CHAKRA_CROWN", "CHAKRAS",
    # theme + layout
    "inject_app_theme", "space", "page_header",
    # meta
    "last_updated_from_file", "soft_date_span", "last_updated_html",
    # components
    "render_card", "render_site_footer",
    # wrappers
    "begin_card_width", "end_card_width", "card_width",
    # helpers
    "hex_to_rgb",
]