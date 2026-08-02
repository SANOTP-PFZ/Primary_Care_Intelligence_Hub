"""
Persistent sidebar component for the Primary Care Intelligence Hub.
Frosted-glass containerized panel with Pfizer branding and icon-based nav.
"""
import streamlit as st


# SVG icons for nav items
_ICON_DASHBOARDS = '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>'
_ICON_AGENTS = '<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="10" rx="2"/><path d="M9 16v3M15 16v3M9 6V3M15 6V3M3 11h3M18 11h3"/></svg>'


def render_sidebar():
    """
    Render the persistent sidebar navigation.
    Returns the currently active screen key.
    """
    with st.sidebar:
        # ─── Brand Title ────────────────────────────────────────────────
        st.markdown("""
        <div class="sidebar-brand">
            <img src="https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png" alt="Pfizer" class="sidebar-brand-logo">
            <div class="sidebar-brand-text">
                <div class="sidebar-brand-title">Primary Care<br>Intelligence Hub</div>
                <div class="sidebar-brand-subtitle">Pfizer Analytics</div>
            </div>
        </div>
        <div class="sidebar-divider"></div>
        """, unsafe_allow_html=True)

        # ─── Primary Care Workspace ─────────────────────────────────────
        st.markdown('<p class="sidebar-section-header">Primary Care Workspace</p>', unsafe_allow_html=True)

        current = st.session_state.get("screen", "dashboards")

        # Nav items rendered as styled Streamlit buttons
        _nav_button("Deep Dive Dashboards", "dashboards", _ICON_DASHBOARDS, "8", current)
        _nav_button("CoWork Agents", "agents", _ICON_AGENTS, "6", current)

        # ─── Footer ────────────────────────────────────────────────────
        st.markdown("""
        <div class="sidebar-footer">
            <p><strong>IIS Primary Care Analytics</strong></p>
            <p>Team_ZS_PC_Analytics@zs.com</p>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.get("screen", "dashboards")


def _nav_button(label, screen_key, icon_svg, count, current):
    """Render a nav item with icon. Uses Streamlit button for click."""
    is_active = current == screen_key

    if is_active:
        st.markdown(f'<div class="nav-active-marker"></div>', unsafe_allow_html=True)

    clicked = st.button(label, key=f"nav_{screen_key}", use_container_width=True)

    if clicked and not is_active:
        st.session_state["screen"] = screen_key
        st.rerun()
