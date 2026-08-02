"""
Persistent sidebar component for the Primary Care Intelligence Hub.
Matches reference HTML sidebar structure: brand > divider > section label > nav items > footer.
"""
import streamlit as st


def render_sidebar():
    """
    Render the persistent sidebar navigation.
    Returns the currently active screen key.
    """
    with st.sidebar:
        # ─── Brand (logo + title + subtitle) ────────────────────────────
        st.markdown("""
        <div class="sidebar-brand">
            <img src="https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png" alt="Pfizer" class="sidebar-brand-logo">
            <div>
                <div class="sidebar-brand-title">Primary Care<br>Intelligence Hub</div>
                <div class="sidebar-brand-subtitle">Pfizer Analytics</div>
            </div>
        </div>
        <div class="sidebar-divider"></div>
        <p class="sidebar-section-header">Primary Care Workspace</p>
        """, unsafe_allow_html=True)

        # ─── Nav Buttons ────────────────────────────────────────────────
        current = st.session_state.get("screen", "dashboards")

        if current == "dashboards":
            st.markdown('<div class="nav-active-marker"></div>', unsafe_allow_html=True)
        if st.button("Deep Dive Dashboards", key="nav_dashboards", use_container_width=True):
            if current != "dashboards":
                st.session_state["screen"] = "dashboards"
                st.rerun()

        if current == "agents":
            st.markdown('<div class="nav-active-marker"></div>', unsafe_allow_html=True)
        if st.button("CoWork Agents", key="nav_agents", use_container_width=True):
            if current != "agents":
                st.session_state["screen"] = "agents"
                st.rerun()

        # ─── Footer ────────────────────────────────────────────────────
        st.markdown("""
        <div class="sidebar-footer">
            <p><strong>IIS Primary Care Analytics</strong></p>
            <p>Team_ZS_PC_Analytics@zs.com</p>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.get("screen", "dashboards")
