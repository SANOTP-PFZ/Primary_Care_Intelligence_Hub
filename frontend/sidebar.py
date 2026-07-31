"""
Persistent sidebar component for the Primary Care Intelligence Hub.
Renders the navy-themed navigation with active state highlighting.
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
        # ─── Logo / Title ───────────────────────────────────────────────
        st.markdown("""
        <div class="sidebar-logo">
            <div style="font-size:28px; margin-bottom:4px;">💊</div>
            <h2>Primary Care<br>Intelligence Hub</h2>
            <p>Pfizer IIS Analytics</p>
        </div>
        """, unsafe_allow_html=True)

        # ─── Workspace Section ──────────────────────────────────────────
        st.markdown('<p class="sidebar-section-header">Workspace</p>', unsafe_allow_html=True)

        if _nav_button("🏠  Home", "home"):
            pass

        # ─── Earnings Reports Section ───────────────────────────────────
        st.markdown('<p class="sidebar-section-header">Earnings Reports</p>', unsafe_allow_html=True)

        for key, config in BRAND_CONFIG.items():
            label = f"{config['icon']}  {config['display_name']}"
            _nav_button(label, key)

        # ─── Cortex Agents Section ──────────────────────────────────────
        st.markdown('<p class="sidebar-section-header">Cortex Agents</p>', unsafe_allow_html=True)

        _nav_button("🤖  Agent Hub", "agents")

        # ─── Footer ────────────────────────────────────────────────────
        st.markdown("---")
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

    # Use a container with a class for active styling
    container_class = "nav-active" if is_active else ""

    # We use a markdown + button combo for styling control
    if is_active:
        st.markdown(f'<div class="nav-active">', unsafe_allow_html=True)

    clicked = st.button(label, key=f"nav_{screen_key}", use_container_width=True)

    if is_active:
        st.markdown('</div>', unsafe_allow_html=True)

    if clicked and current != screen_key:
        st.session_state["screen"] = screen_key
        # Reset agent sub-screen when navigating away from agents
        if screen_key != "agents":
            st.session_state.pop("agent_screen", None)
        st.rerun()

    return clicked
