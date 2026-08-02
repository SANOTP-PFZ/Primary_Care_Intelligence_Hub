"""
Persistent sidebar component for the Primary Care Intelligence Hub.
Renders frosted-glass containerized navigation with Pfizer branding.
"""
import streamlit as st
from backend.config import BRAND_CONFIG


def render_sidebar():
    """
    Render the persistent sidebar navigation.
    Updates st.session_state["screen"] on click.
    Returns the currently active screen key.
    """
    with st.sidebar:
        # ─── Pfizer Logo + Title Bar ────────────────────────────────────
        st.markdown("""
        <div class="sidebar-brand">
            <img src="https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png" alt="Pfizer" class="sidebar-brand-logo">
            <div>
                <div class="sidebar-brand-title">Primary Care<br>Intelligence Hub</div>
                <div class="sidebar-brand-subtitle">Pfizer Analytics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ─── Divider ────────────────────────────────────────────────────
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # ─── Earnings Reports Brand Analytics ───────────────────────────
        st.markdown('<p class="sidebar-section-header">Earnings Reports Brand Analytics</p>', unsafe_allow_html=True)

        for key, config in BRAND_CONFIG.items():
            _nav_button(config['display_name'], key)

        # ─── Footer ────────────────────────────────────────────────────
        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sidebar-footer">
            <p><strong>IIS Primary Care Analytics</strong></p>
            <p>Team_ZS_PC_Analytics@zs.com</p>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.get("screen", "home")


def _nav_button(label, screen_key):
    """Render a sidebar nav button. Highlights if it's the active screen."""
    current = st.session_state.get("screen", "home")
    is_active = current == screen_key

    if is_active:
        st.markdown('<div class="nav-active">', unsafe_allow_html=True)

    clicked = st.button(label, key=f"nav_{screen_key}", use_container_width=True)

    if is_active:
        st.markdown('</div>', unsafe_allow_html=True)

    if clicked and current != screen_key:
        st.session_state["screen"] = screen_key
        st.rerun()

    return clicked
