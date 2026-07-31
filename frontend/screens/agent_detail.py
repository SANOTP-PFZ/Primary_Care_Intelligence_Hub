"""
Agent detail page - shows a single agent's interface/information.
"""
import streamlit as st
from backend.config import AGENT_CATEGORIES


def render():
    """Render the agent detail page."""
    agent_id = st.session_state.get("agent_id")

    # Find the agent in our config
    agent = None
    parent_category = None
    for category in AGENT_CATEGORIES:
        for a in category["agents"]:
            if a["id"] == agent_id:
                agent = a
                parent_category = category
                break
        if agent:
            break

    if not agent:
        st.warning("Agent not found.")
        if st.button("← Back to Agent Hub"):
            st.session_state["agent_screen"] = "landing"
            st.rerun()
        return

    # Breadcrumb
    st.markdown(f"""
    <div class="breadcrumb">
        <a href="#" onclick="return false;">Agent Hub</a>
        <span>›</span>
        <a href="#" onclick="return false;">{parent_category['name']}</a>
        <span>›</span>
        <strong>{agent['name']}</strong>
    </div>
    """, unsafe_allow_html=True)

    # Back button
    if st.button("← Back to Agents", key="back_to_agents"):
        st.session_state["agent_screen"] = "ta"
        st.rerun()

    # Agent header
    tags_html = "".join(f'<span class="agent-tag">{tag}</span>' for tag in agent["tags"])

    st.markdown(f"""
    <div class="hero-card">
        <h2>{agent['name']}</h2>
        <p style="font-size:14px; color:var(--slate-600); margin-bottom:16px;">{agent['description']}</p>
        <div>{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # Agent interaction area
    st.markdown('<p class="section-header">💬 Ask this Agent</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <p style="font-size:13px; color:var(--slate-600); margin-bottom:12px;">
            This agent is powered by Snowflake Cortex. Ask questions about your data in natural language.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Chat-style input
    user_query = st.text_input(
        "Ask a question...",
        placeholder="e.g., What is the TRx market share trend for Nurtec?",
        key="agent_query_input"
    )

    if user_query:
        with st.spinner("Agent is thinking..."):
            # Placeholder for Cortex agent integration
            st.markdown(f"""
            <div class="glass-card" style="margin-top:16px; border-left:3px solid var(--accent);">
                <p style="font-size:12px; color:var(--accent); font-weight:600; margin-bottom:8px;">Agent Response</p>
                <p style="font-size:14px; color:var(--slate-800);">
                    This is a placeholder for the Cortex agent response. 
                    In production, this will connect to Snowflake Cortex for AI-powered analytics.
                </p>
                <p style="font-size:12px; color:var(--slate-400); margin-top:12px;">
                    Query: "{user_query}"
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Agent capabilities
    st.markdown('<p class="section-header">📋 Capabilities</p>', unsafe_allow_html=True)

    capabilities = {
        "npa_trx": ["TRx market share analysis", "Quarter-over-quarter trends", "Competitive landscape", "Brand performance vs market"],
        "npa_nbrx": ["NBRx new patient metrics", "Conversion rate analysis", "New-to-brand trends", "Share of new starts"],
        "ddd_shipment": ["Shipment volume tracking", "Channel distribution analysis", "Retail vs non-retail split", "Regional patterns"],
        "ddd_retail": ["Retail market share", "Non-retail market share", "OA/MA splits", "Channel contribution trends"],
        "elaad_claims": ["Claims volume analysis", "Patient identification", "Prescriber patterns", "Geographic distribution"],
        "elaad_weekly": ["Weekly trend analysis", "Seasonal pattern detection", "Year-over-year comparisons", "Anomaly identification"],
    }

    agent_caps = capabilities.get(agent_id, ["General data analysis", "Trend identification", "Comparative analytics"])

    for cap in agent_caps:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            <span style="color:var(--success); font-size:14px;">✓</span>
            <span style="font-size:13px; color:var(--slate-800);">{cap}</span>
        </div>
        """, unsafe_allow_html=True)
