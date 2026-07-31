"""
Home screen for the Primary Care Intelligence Hub.
Displays hero banner with portfolio KPIs and brand/agent quick-access cards.
"""
import streamlit as st
from backend.config import BRAND_CONFIG, AGENT_CATEGORIES
from backend.data_loader import load_master_data, get_brand_summary_kpis, get_data_freshness


def render():
    """Render the Home screen."""
    # ─── Hero Banner ────────────────────────────────────────────────────
    freshness = get_data_freshness()

    st.markdown(f"""
    <div class="hero-card">
        <h2>Primary Care Portfolio Performance</h2>
        <p style="font-size:13px; color:var(--slate-600); margin-bottom:20px;">
            Comprehensive analytics across 8 brands · Data updated: {freshness}
        </p>
        <div class="kpi-grid">
            <div class="kpi-tile">
                <div class="kpi-label">Active Brands</div>
                <div class="kpi-value">8</div>
                <div class="kpi-sub">Tracked in portfolio</div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-label">Data Sources</div>
                <div class="kpi-value">3</div>
                <div class="kpi-sub">NPA · DDD · ELAAD</div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-label">Cortex Agents</div>
                <div class="kpi-value">{sum(len(c['agents']) for c in AGENT_CATEGORIES)}</div>
                <div class="kpi-sub">AI-powered analytics</div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-label">Last Refresh</div>
                <div class="kpi-value" style="font-size:16px;">{freshness}</div>
                <div class="kpi-sub">Auto-updated</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Earnings Reports Section ───────────────────────────────────────
    st.markdown('<p class="section-header">📊 Earnings Reports</p>', unsafe_allow_html=True)

    # Render brand cards in a 4-column grid
    cols = st.columns(4)
    for idx, (key, config) in enumerate(BRAND_CONFIG.items()):
        with cols[idx % 4]:
            _render_brand_card(key, config)

    # ─── Cortex Agents Section ──────────────────────────────────────────
    st.markdown('<p class="section-header">🤖 Cortex Agents</p>', unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, category in enumerate(AGENT_CATEGORIES):
        with cols[idx % 3]:
            _render_agent_category_card(category)


def _render_brand_card(key, config):
    """Render a single brand quick-access card."""
    st.markdown(f"""
    <div class="brand-card" style="--card-accent: {config['color']}; margin-bottom:16px;">
        <div class="brand-icon">{config['icon']}</div>
        <div class="brand-name">{config['display_name']}</div>
        <div class="brand-market">{config['market_display']}</div>
        <div class="brand-kpi-label">Source: {config['source']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Invisible button overlay for click navigation
    if st.button(f"View {config['display_name']}", key=f"home_brand_{key}", use_container_width=True):
        st.session_state["screen"] = key
        st.rerun()


def _render_agent_category_card(category):
    """Render a single agent category card."""
    agent_count = len(category["agents"])
    tags_html = "".join(
        f'<span class="agent-tag">{agent["tags"][0]}</span>'
        for agent in category["agents"][:3]
    )

    st.markdown(f"""
    <div class="agent-category-card" style="margin-bottom:16px;">
        <div class="category-icon">{category['icon']}</div>
        <div class="category-name">{category['name']}</div>
        <div class="category-desc">{category['description']}</div>
        <div style="margin-top:12px;">
            {tags_html}
            <span style="font-size:11px; color:var(--slate-400); margin-left:4px;">{agent_count} agents</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"Explore {category['name']}", key=f"home_agent_{category['id']}", use_container_width=True):
        st.session_state["screen"] = "agents"
        st.session_state["agent_screen"] = "ta"
        st.session_state["agent_category"] = category["id"]
        st.rerun()
