"""
Primary Care Intelligence Hub - Landing Page
"""
import streamlit as st
import dataiku
import pandas as pd

st.set_page_config(
    page_title="Primary Care Intelligence Hub",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- DATA LOADING ---
BRANDS = ['NURTEC', 'ELIQUIS', 'PREVNAR', 'COMIRNATY', 'ABRYSVO']
BRAND_COLORS = {
    'NURTEC': '#1C4FC0',
    'ELIQUIS': '#41B6E6',
    'PREVNAR': '#7C3AED',
    'COMIRNATY': '#10B981',
    'ABRYSVO': '#F59E0B',
}

@st.cache_data(ttl=3600)
def load_brand_data():
    df = dataiku.Dataset("SQL_EARNINGS_REPORT_MASTER_DATASET_SF").get_dataframe()
    df = df[
        (df['DATASET'] == 'NPA_TRX') &
        (df['METRICS'] == 'TRX MARKET SHARE') &
        (df['BRAND'].isin(BRANDS)) &
        (df['YR_QTR_TXT'] >= '2024')
    ].sort_values(['BRAND', 'YR_QTR_TXT'])
    return df

df = load_brand_data()

# Compute date range for display
all_quarters = sorted(df['YR_QTR_TXT'].unique())
first_qtr = all_quarters[0] if all_quarters else '2024Q1'
latest_qtr = all_quarters[-1] if all_quarters else 'N/A'

# Load max date for data freshness
try:
    max_date_df = dataiku.Dataset("SQL_NPA_MAX_DATE_SF").get_dataframe()
    max_date_raw = str(max_date_df.iloc[0, 0]).split(" ")[0]
except Exception:
    max_date_raw = latest_qtr

# Compute refresh timestamp (from dataset build metrics, converted UTC -> IST)
from datetime import datetime
try:
    import pytz
    client = dataiku.api_client()
    project = client.get_default_project()
    ds = project.get_dataset("SQL_EARNINGS_REPORT_MASTER_DATASET_SF")
    last_metrics = ds.get_last_metric_values()
    build_date_metric = last_metrics.get_metric_by_id("reporting:BUILD_START_DATE")
    build_date_val = build_date_metric.get("lastValues", [{}])[0].get("value", None) if build_date_metric else None

    if build_date_val:
        utc_time = datetime.strptime(build_date_val, "%Y-%m-%dT%H:%M:%S.%fZ")
        ist = pytz.timezone("Asia/Kolkata")
        ist_time = pytz.utc.localize(utc_time).astimezone(ist)
        refresh_ts = ist_time.strftime("%B %d, %Y at %I:%M %p IST")
    else:
        refresh_ts = max_date_raw if max_date_raw != "N/A" else "N/A"
except Exception:
    refresh_ts = max_date_raw if max_date_raw != "N/A" else "N/A"


def build_brand_card_data(df):
    """For each brand: latest value, QoQ delta, SVG sparkline points, and date range."""
    cards = []
    for brand in BRANDS:
        bdf = df[df['BRAND'] == brand].sort_values('YR_QTR_TXT')
        if bdf.empty:
            continue
        values = bdf['VALUE'].tolist()
        quarters = bdf['YR_QTR_TXT'].tolist()
        latest = values[-1]
        delta = latest - values[-2] if len(values) >= 2 else 0.0

        # Generate SVG polyline points (normalize values to 2-24 y-range, 26px height)
        v_min, v_max = min(values), max(values)
        v_range = v_max - v_min if v_max != v_min else 1
        n = len(values)
        points = []
        for i, v in enumerate(values):
            x = round((i / (n - 1)) * 120, 1) if n > 1 else 60
            y = round(24 - ((v - v_min) / v_range) * 22, 1)
            points.append(f"{x},{y}")
        polyline = " ".join(points)

        cards.append({
            'brand': brand,
            'value': f"{latest:.1f}%",
            'delta': f"{delta:+.1f}",
            'delta_class': 'up' if delta >= 0 else 'down',
            'color': BRAND_COLORS[brand],
            'polyline': polyline,
            'first_qtr': quarters[0] if quarters else '',
            'latest_qtr': quarters[-1] if quarters else '',
        })
    return cards


brand_cards = build_brand_card_data(df)


def render_brand_cards_html(cards):
    """Generate HTML for brand cards."""
    html_cards = []
    for c in cards:
        html_cards.append(f'''
                <div class="brand-card">
                    <div class="card-top">
                        <span class="brand-name">{c['brand'].title()}</span>
                        <span class="brand-metric"><span class="brand-value">{c['value']}</span><span class="brand-delta {c['delta_class']}">{c['delta']}</span></span>
                    </div>
                    <div class="brand-spark"><svg viewBox="0 0 120 26" preserveAspectRatio="none"><polyline points="{c['polyline']}" fill="none" stroke="{c['color']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
                    <div class="card-footer"><span class="card-source">NPA</span> {c['first_qtr']} &rarr; {c['latest_qtr']}</div>
                </div>''')
    return "\n".join(html_cards)


brand_cards_html = render_brand_cards_html(brand_cards)

# =====================================================
# GLOBAL CSS — hide chrome, lock viewport, style buttons
# =====================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Hide all Streamlit chrome */
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"], #MainMenu, footer,
    .stApp > header { display: none !important; }

    /* Overflow is controlled per-page — see routing section below */

    /* Layout spacing */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewBlockContainer"] { padding: 0 !important; }
    [data-testid="stMainBlockContainer"] { padding: 8px 10px !important; }
    [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
    [data-testid="stHorizontalBlock"] { gap: 10px !important; align-items: stretch !important; }

    /* Background gradient */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background:
            radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.07) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 50% 100%, rgba(124,58,237,0.04) 0%, transparent 60%),
            #EEF3FB !important;
    }

    /* Brand tile button styling — target ALL buttons in the right column */
    [data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"] .stButton > button {
        background: rgba(255,255,255,0.72) !important;
        backdrop-filter: saturate(160%) blur(12px) !important;
        -webkit-backdrop-filter: saturate(160%) blur(12px) !important;
        border: 1px solid rgba(15,23,42,0.08) !important;
        border-radius: 16px !important;
        padding: 1.2rem 0.9rem !important;
        color: #0A1A3D !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        font-family: 'Manrope', 'Inter', system-ui, sans-serif !important;
        cursor: pointer !important;
        transition: transform 0.22s cubic-bezier(0.4,0,0.2,1), box-shadow 0.22s cubic-bezier(0.4,0,0.2,1), border-color 0.18s cubic-bezier(0.4,0,0.2,1) !important;
        box-shadow: 0 2px 8px rgba(15,23,42,0.04) !important;
        min-height: 76px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"] .stButton > button:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 0 8px 22px rgba(15,23,42,0.09) !important;
        border-color: rgba(28,79,192,0.3) !important;
        background: rgba(255,255,255,0.94) !important;
    }

    /* Brand card styles for summary section */
    .brand-card { background:rgba(255,255,255,0.72); backdrop-filter:saturate(160%) blur(12px); -webkit-backdrop-filter:saturate(160%) blur(12px); border:1px solid rgba(15,23,42,0.08); border-radius:16px; padding:0.7rem 0.75rem 0.5rem; box-shadow:0 2px 8px rgba(15,23,42,0.03); aspect-ratio:1.4/1; display:flex; flex-direction:column; justify-content:space-between; }
    .card-top { display:flex; align-items:baseline; justify-content:space-between; margin-bottom:0.35rem; }
    .brand-name { font-family:'Manrope',sans-serif; font-weight:700; font-size:14px; color:#0A1A3D; }
    .brand-metric { display:flex; align-items:center; gap:0.3rem; }
    .brand-value { font-family:'Manrope',sans-serif; font-weight:800; font-size:16px; color:#0F172A; }
    .brand-delta { font-size:11px; font-weight:600; padding:1px 5px; border-radius:4px; }
    .brand-delta.up { color:#059669; background:rgba(16,185,129,0.1); }
    .brand-delta.down { color:#DC2626; background:rgba(239,68,68,0.08); }
    .brand-spark { width:100%; }
    .brand-spark svg { width:100%; height:28px; display:block; }
    .card-footer { font-size:10.5px; color:#64748B; font-weight:500; text-align:center; margin-top:0.25rem; letter-spacing:0.02em; }
    .card-source { display:inline-block; background:rgba(28,79,192,0.08); color:#163990; font-size:9.5px; font-weight:700; padding:1px 5px; border-radius:3px; letter-spacing:0.05em; margin-right:3px; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE + ROUTING
# =====================================================
if "nav_state" not in st.session_state:
    st.session_state["nav_state"] = "home"

BRAND_CONFIG = {
    "nurtec": {"display_name": "Nurtec", "brand_key": "NURTEC", "market": "OCGRP", "market_display": "Oral CGRP"},
    "eliquis": {"display_name": "Eliquis", "brand_key": "ELIQUIS", "market": "OAC", "market_display": "Oral Anticoagulant"},
    "prevnar": {"display_name": "Prevnar", "brand_key": "PREVNAR", "market": "PCV", "market_display": "PCV", "ddd_market": "PCV"},
    "comirnaty": {"display_name": "Comirnaty", "brand_key": "COMIRNATY", "market": "COVID_VACCINES", "market_display": "COVID Vaccines", "ddd_market": "COVID"},
    "abrysvo": {"display_name": "Abrysvo", "brand_key": "ABRYSVO", "market": "RSV", "market_display": "RSV", "ddd_market": "RSV"},
    "paxlovid": {"display_name": "Paxlovid", "brand_key": "PAXLOVID", "market": "COVID_ORAL", "market_display": "COVID Oral Treatment"},
    "zavzpret": {"display_name": "Zavzpret", "brand_key": "ZAVZPRET", "market": "ZAVZPRET", "market_display": "Zavzpret"},
    "beyfortus": {"display_name": "Beyfortus", "brand_key": "BEYFORTUS", "market": "BEYFORTUS", "market_display": "Beyfortus"},
}

nav = st.session_state["nav_state"]

if nav in ("home", "deepdive"):
    # =========================================================
    # LANDING PAGE — Two-column layout (sidebar | main content)
    # Everything fits in viewport, no scrolling
    # =========================================================

    # Lock viewport for landing page only
    st.markdown("""
    <style>
        .stApp { overflow: hidden !important; }
        [data-testid="stMain"] { overflow: hidden !important; }
        [data-testid="stMainBlockContainer"] { overflow: hidden !important; max-height: 100vh !important; }
    </style>
    """, unsafe_allow_html=True)

    sidebar_col, main_col = st.columns([232, 900], gap="small")

    # --- LEFT COLUMN: Sidebar with real nav buttons ---
    with sidebar_col:
        # CSS to style sidebar buttons as nav items (override the brand-tile button styles)
        deepdive_active = "background: linear-gradient(90deg,rgba(28,79,192,0.10) 0%,rgba(28,79,192,0.04) 100%) !important; color: #163990 !important; font-weight: 600 !important; border-left: 3px solid #1C4FC0 !important; border-radius: 0 8px 8px 0 !important;" if nav == "deepdive" else ""
        st.markdown(f"""
        <style>
            /* Sidebar nav buttons — override brand tile styles for first column */
            [data-testid="column"]:first-child .stButton > button {{
                background: transparent !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 0.5rem 0.7rem !important;
                color: #475569 !important;
                font-size: 0.84rem !important;
                font-weight: 500 !important;
                font-family: 'Inter', sans-serif !important;
                min-height: auto !important;
                height: auto !important;
                width: 100% !important;
                text-align: left !important;
                justify-content: flex-start !important;
                box-shadow: none !important;
                transform: none !important;
                aspect-ratio: unset !important;
                cursor: pointer !important;
            }}
            [data-testid="column"]:first-child .stButton > button:hover {{
                background: rgba(28,79,192,0.06) !important;
                color: #163990 !important;
                transform: none !important;
                box-shadow: none !important;
            }}
            /* Active state for Deep Dive button */
            [data-testid="column"]:first-child .stButton:first-of-type > button {{
                {deepdive_active}
            }}
        </style>
        """, unsafe_allow_html=True)

        # Sidebar top: Logo + Title + Divider + Label
        st.markdown("""
        <div style="background:rgba(255,255,255,0.62); backdrop-filter:saturate(180%) blur(22px); -webkit-backdrop-filter:saturate(180%) blur(22px); border:1px solid rgba(15,23,42,0.08); border-radius:18px; box-shadow:0 8px 24px rgba(15,23,42,0.07),0 2px 6px rgba(15,23,42,0.04); padding:14px 1.2rem 0.6rem; margin-bottom:0;">
            <div style="display:flex; flex-direction:column; gap:0.5rem; margin-bottom:0.8rem;">
                <img src="https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png" style="height:28px; align-self:flex-start;" />
                <div style="font-family:'Manrope',sans-serif; font-weight:800; font-size:1.2rem; color:#0A1A3D; line-height:1.18; letter-spacing:-0.025em;">Primary Care<br>Intelligence Hub</div>
                <div style="font-size:0.72rem; color:#64748B; font-weight:500;">Pfizer Analytics</div>
            </div>
            <div style="height:1px; background:rgba(15,23,42,0.08); margin:0 -0.3rem 0.6rem;"></div>
            <div style="font-family:'Manrope',sans-serif; font-size:0.62rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#64748B; margin-bottom:0.3rem;">Primary Care Workspace</div>
        </div>
        """, unsafe_allow_html=True)

        # Real navigation buttons
        if st.button("📊  Deep Dive Dashboards", key="nav_deepdive"):
            st.session_state["nav_state"] = "deepdive"
            st.rerun()

        if st.button("🤖  CoWork Agents", key="nav_cowork"):
            pass  # Placeholder for future feature

        # Sidebar footer
        st.markdown("""
        <div style="margin-top:auto; padding:0.85rem 1.15rem 1rem; font-size:0.7rem; color:#64748B; line-height:1.55; border-top:1px solid rgba(15,23,42,0.08); background:linear-gradient(180deg,transparent 0%,rgba(28,79,192,0.025) 100%); border-radius:0 0 18px 18px;">
            <div style="margin-bottom:0.2rem;"><strong style="color:#475569;font-weight:600;">Primary Care Analytics</strong></div>
            <div>Team_ZS_PC_Analytics@zs.com</div>
        </div>
        """, unsafe_allow_html=True)

    # --- RIGHT COLUMN: Summary + Brand Tiles ---
    with main_col:
        # Summary section rendered as a small component (SVGs need an iframe to render)
        summary_html = f"""
        <html>
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family:'Inter',system-ui,sans-serif; background:transparent; -webkit-font-smoothing:antialiased; }}
            .summary-panel {{ background:rgba(255,255,255,0.55); backdrop-filter:saturate(180%) blur(14px); -webkit-backdrop-filter:saturate(180%) blur(14px); border:1px solid rgba(15,23,42,0.08); border-radius:18px; box-shadow:0 8px 24px rgba(15,23,42,0.07),0 2px 6px rgba(15,23,42,0.04); padding:1.8rem 1.5rem; }}
            .section-header {{ font-family:'Manrope',sans-serif; font-weight:700; font-size:19px; color:#0A1A3D; margin-bottom:0.35rem; }}
            .section-subtitle {{ font-size:0.78rem; color:#64748B; font-weight:500; margin-bottom:1.1rem; }}
            .brand-cards {{ display:grid; grid-template-columns:repeat(5,1fr); gap:0.8rem; }}
            .brand-card {{ background:rgba(255,255,255,0.72); backdrop-filter:saturate(160%) blur(12px); -webkit-backdrop-filter:saturate(160%) blur(12px); border:1px solid rgba(15,23,42,0.08); border-radius:16px; padding:1rem 0.85rem 0.7rem; box-shadow:0 2px 8px rgba(15,23,42,0.03); min-height:168px; display:flex; flex-direction:column; justify-content:space-between; }}
            .card-top {{ display:flex; align-items:baseline; justify-content:space-between; margin-bottom:0.35rem; }}
            .brand-name {{ font-family:'Manrope',sans-serif; font-weight:700; font-size:14px; color:#0A1A3D; }}
            .brand-metric {{ display:flex; align-items:center; gap:0.3rem; }}
            .brand-value {{ font-family:'Manrope',sans-serif; font-weight:800; font-size:16px; color:#0F172A; }}
            .brand-delta {{ font-size:11px; font-weight:600; padding:1px 5px; border-radius:4px; }}
            .brand-delta.up {{ color:#059669; background:rgba(16,185,129,0.1); }}
            .brand-delta.down {{ color:#DC2626; background:rgba(239,68,68,0.08); }}
            .brand-spark {{ width:100%; }}
            .brand-spark svg {{ width:100%; height:28px; display:block; }}
            .card-footer {{ font-size:10.5px; color:#64748B; font-weight:500; text-align:center; margin-top:0.25rem; letter-spacing:0.02em; }}
            .card-source {{ display:inline-block; background:rgba(28,79,192,0.08); color:#163990; font-size:9.5px; font-weight:700; padding:1px 5px; border-radius:3px; letter-spacing:0.05em; margin-right:3px; }}
            .data-freshness {{ margin-top:1.2rem; padding:0.6rem 0.9rem; border-radius:10px; background:rgba(28,79,192,0.03); border:1px solid rgba(28,79,192,0.08); display:flex; gap:1.5rem; align-items:center; flex-wrap:wrap; font-size:11.5px; }}
            .data-freshness-label {{ font-family:'Manrope',sans-serif; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#163990; }}
            .data-freshness-item {{ color:#475569; font-weight:500; }}
            .data-freshness-item strong {{ color:#0A1A3D; font-weight:600; }}
            .data-freshness-divider {{ width:1px; height:12px; background:rgba(28,79,192,0.2); }}
            .data-refreshed {{ margin-left:auto; color:#64748B; }}
        </style>
        </head>
        <body>
        <div class="summary-panel">
            <div class="section-header">Primary Care Brand Performance Summary</div>
            <div class="section-subtitle">QoQ TRx Market Share Trends</div>
            <div class="brand-cards">
                {brand_cards_html}
            </div>
            <div class="data-freshness">
                <span class="data-freshness-label">Data Availability</span>
                <span class="data-freshness-item"><strong>NPA:</strong> Till {max_date_raw}</span>
                <span class="data-freshness-item"><strong>DDD:</strong> Till {max_date_raw}</span>
                <span class="data-freshness-item"><strong>LAAD:</strong> Till {max_date_raw}</span>
                <span class="data-freshness-divider"></span>
                <span class="data-freshness-item data-refreshed"><strong>Refreshed:</strong> {refresh_ts}</span>
            </div>
        </div>
        </body>
        </html>
        """
        st.components.v1.html(summary_html, height=430, scrolling=False)

        # Separator line
        st.markdown("""
        <div style="text-align:center; padding:0.15rem 0 0.5rem;">
            <div style="width:80px; height:1px; background:linear-gradient(90deg,transparent,rgba(28,79,192,0.3),transparent); margin:0 auto;"></div>
        </div>
        """, unsafe_allow_html=True)

        # --- Conditional: Mission Text (home) vs Brand Tiles (deepdive) ---
        if nav == "home":
            st.markdown("""
            <div style="text-align:center; padding:0.5rem 0 0;">
                <div style="font-family:'Manrope',sans-serif; font-weight:800; font-size:18px; color:#0A1A3D; letter-spacing:-0.02em; margin-bottom:0.5rem;">Welcome to the Primary Care Intelligence Hub</div>
                <div style="font-size:13px; color:#475569; line-height:1.7; max-width:580px; margin:0 auto;">
                    Empowering Pfizer's Primary Care business with real-time market intelligence, competitive analytics, and actionable insights across our key therapeutic brands. This platform consolidates NPA, DDD, and LAAD data sources into unified quarterly performance views.
                </div>
                <div style="margin-top:0.8rem; font-size:12px; color:#64748B;">
                    Select <strong style="color:#1C4FC0;">Deep Dive Dashboards</strong> in the sidebar to explore brand-level QoQ analysis.
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif nav == "deepdive":
            st.markdown("""
            <div style="text-align:center; padding:0.3rem 0 0.6rem;">
                <div style="font-family:'Manrope',sans-serif; font-weight:700; font-size:15px; color:#0A1A3D; letter-spacing:-0.01em;">Deep Dive Dashboards</div>
                <div style="font-size:12px; color:#64748B; font-weight:400; margin-top:0.15rem;">Select a brand to explore detailed QoQ analysis, competitive trends, and exportable reports</div>
            </div>
            """, unsafe_allow_html=True)

            # Brand tile buttons
            brands_list = [
                ("Nurtec", "nurtec"), ("Eliquis", "eliquis"), ("Prevnar", "prevnar"), ("Comirnaty", "comirnaty"),
                ("Abrysvo", "abrysvo"), ("Paxlovid", "paxlovid"), ("Zavzpret", "zavzpret"), ("Beyfortus", "beyfortus"),
            ]

            cols1 = st.columns(4, gap="small")
            for i, (name, key) in enumerate(brands_list[:4]):
                with cols1[i]:
                    if st.button(name, key=f"brand_btn_{key}", use_container_width=True):
                        st.session_state["nav_state"] = key
                        st.rerun()

            cols2 = st.columns(4, gap="small")
            for i, (name, key) in enumerate(brands_list[4:]):
                with cols2[i]:
                    if st.button(name, key=f"brand_btn_{key}", use_container_width=True):
                        st.session_state["nav_state"] = key
                        st.rerun()

else:
    # === RENDER BRAND PAGE ===
    import plotly.graph_objects as go
    from io import BytesIO
    from brand_pages import render_brand_page
    render_brand_page(nav, BRAND_CONFIG)
