"""
Agent Hub landing screen - displays all agent categories as cards.
"""
import streamlit as st
from backend.config import AGENT_CATEGORIES


def render():
    """Render the agent hub landing page."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Cortex Agent Hub</h1>
        <p>AI-powered analytics agents for Primary Care data exploration</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Select a Category</p>', unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, category in enumerate(AGENT_CATEGORIES):
        with cols[idx % 3]:
            agent_count = len(category["agents"])

            st.markdown(f"""
            <div class="agent-category-card" style="margin-bottom:16px; min-height:180px;">
                <div class="category-icon">{category['icon']}</div>
                <div class="category-name">{category['name']}</div>
                <div class="category-desc">{category['description']}</div>
                <div style="margin-top:12px;">
                    <span style="font-size:12px; color:var(--accent); font-weight:600;">{agent_count} agents available</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Explore {category['name']}", key=f"agent_cat_{category['id']}", use_container_width=True):
                st.session_state["agent_screen"] = "ta"
                st.session_state["agent_category"] = category["id"]
                st.rerun()
