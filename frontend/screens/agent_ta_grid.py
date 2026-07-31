"""
Agent TA grid - shows agents within a selected category.
"""
import streamlit as st
from backend.config import AGENT_CATEGORIES


def render():
    """Render the TA-level agent grid for the selected category."""
    category_id = st.session_state.get("agent_category")

    # Find the selected category
    category = next((c for c in AGENT_CATEGORIES if c["id"] == category_id), None)
    if not category:
        st.warning("No category selected.")
        if st.button("← Back to Agent Hub"):
            st.session_state["agent_screen"] = "landing"
            st.rerun()
        return

    # Breadcrumb
    st.markdown(f"""
    <div class="breadcrumb">
        <a href="#" onclick="return false;">Agent Hub</a>
        <span>›</span>
        <strong>{category['name']}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="main-header">
        <h1>{category['icon']} {category['name']}</h1>
        <p>{category['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Back button
    if st.button("← Back to Categories", key="back_to_categories"):
        st.session_state["agent_screen"] = "landing"
        st.rerun()

    # Agent cards grid
    st.markdown('<p class="section-header">Available Agents</p>', unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, agent in enumerate(category["agents"]):
        with cols[idx % 2]:
            tags_html = "".join(f'<span class="agent-tag">{tag}</span>' for tag in agent["tags"])

            st.markdown(f"""
            <div class="glass-card" style="margin-bottom:16px; cursor:pointer;">
                <div style="font-family:'Manrope',sans-serif; font-size:15px; font-weight:700; color:var(--navy-900); margin-bottom:8px;">
                    {agent['name']}
                </div>
                <div style="font-size:13px; color:var(--slate-600); margin-bottom:12px; line-height:1.5;">
                    {agent['description']}
                </div>
                <div>{tags_html}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open {agent['name']}", key=f"agent_{agent['id']}", use_container_width=True):
                st.session_state["agent_screen"] = "detail"
                st.session_state["agent_id"] = agent["id"]
                st.rerun()
