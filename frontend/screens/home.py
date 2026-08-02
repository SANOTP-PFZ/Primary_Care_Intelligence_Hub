"""
Home screen for the Primary Care Intelligence Hub.
Displays hero banner with portfolio KPIs and brand/agent quick-access cards.
"""
import streamlit as st
from backend.config import BRAND_CONFIG, AGENT_CATEGORIES
from backend.data_loader import load_master_data, get_brand_summary_kpis, get_data_freshness


AGENT_CHIP_COLORS = {
    "npa": "chip-blue",
    "ddd": "chip-green",
    "elaad": "chip-purple",
}


def render():
    """Render the Home screen."""
    freshness = get_data_freshness()

    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-header">
            <div>
                <h2 class="hero-title">Primary Care Portfolio Performance</h2>
                <div class="hero-subtitle">
                    <span>Pfizer Analytics</span>
                    <span class="dot"></span>
                    <span>8 Brands Tracked</span>
                </div>
            </div>
            <span class="hero-badge">Executive KPIs</span>
        </div>
        <div class="kpi-grid">
            <div class="kpi-tile">
                <div class="kpi-label">Active Brands</div>
                <div class="kpi-value">8</div>
                <div class="kpi-delta flat"><span class="vs">In portfolio</span></div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-label">Data Sources</div>
                <div class="kpi-value">3</div>
                <div class="kpi-delta flat"><span class="vs">NPA / DDD / ELAAD</span></div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-label">Cortex Agents</div>
                <div class="kpi-value">{sum(len(c['agents']) for c in AGENT_CATEGORIES)}</div>
                <div class="kpi-delta up"><span class="tri">&#9650;</span>AI-powered</div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-label">Last Refresh</div>
                <div class="kpi-value" style="font-size:16px;">{freshness}</div>
                <div class="kpi-delta flat"><span class="vs">Auto-updated</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Divider ─────────────────────────────────────────────────────────
    st.markdown('<div class="workspace-divider"></div>', unsafe_allow_html=True)

    # ─── Earnings Reports Section ───────────────────────────────────────
    st.markdown('<p class="section-header">Earnings Reports</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Interactive analytics across patient funnel, volume, and financial performance by brand.</p>', unsafe_allow_html=True)

    cols = st.columns(4)
    for idx, (key, config) in enumerate(BRAND_CONFIG.items()):
        with cols[idx % 4]:
            _render_brand_card(key, config)

    # ─── Cortex Agents Section ──────────────────────────────────────────
    st.markdown('<div class="workspace-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-header">Cortex Agents</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">AI-powered analytical agents for automated insights and conversational data exploration.</p>', unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, category in enumerate(AGENT_CATEGORIES):
        with cols[idx % 3]:
            _render_agent_category_card(category)


def _render_brand_card(key, config):
    """Render a single brand quick-access card."""
    chip_class = config.get("chip", "chip-blue")

    st.markdown(f"""
    <div class="card" style="margin-bottom:12px;">
        <div class="card-top">
            <span class="icon-chip {chip_class}">{config['icon']}</span>
            <span class="badge weekly">{config['source']}</span>
        </div>
        <div class="card-title">{config['display_name']}</div>
        <div class="card-desc">{config['market_display']}</div>
        <span class="dest-pill"><span class="swatch">&#9632;</span>{config['source']}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"View {config['display_name']}", key=f"home_brand_{key}", use_container_width=True):
        st.session_state["screen"] = key
        st.rerun()


def _render_agent_category_card(category):
    """Render a single agent category card."""
    agent_count = len(category["agents"])
    chip_class = AGENT_CHIP_COLORS.get(category["id"], "chip-purple")

    st.markdown(f"""
    <div class="card" style="margin-bottom:12px;">
        <div class="card-top">
            <span class="icon-chip {chip_class}">{category['icon']}</span>
            <span class="badge monthly">{agent_count} agents</span>
        </div>
        <div class="card-title">{category['name']}</div>
        <div class="card-desc">{category['description']}</div>
        <span class="dest-pill dest-agent"><span class="swatch">&#9632;</span>Cortex Agent</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"Explore {category['name']}", key=f"home_agent_{category['id']}", use_container_width=True):
        st.session_state["screen"] = "agents"
        st.session_state["agent_screen"] = "ta"
        st.session_state["agent_category"] = category["id"]
        st.rerun()
