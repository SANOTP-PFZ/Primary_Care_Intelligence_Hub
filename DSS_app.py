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

if nav in ("home", "deepdive", "cowork"):
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

    # --- LEFT COLUMN: Sidebar with clickable nav ---
    with sidebar_col:
        # Determine which nav item is active
        active_nav = nav  # "home", "deepdive", or "cowork"

        # CSS: hide the real Streamlit buttons visually but keep them clickable,
        # and style the sidebar column as the glassmorphism card
        st.markdown("""
        <style>
            /* ─── SIDEBAR COLUMN → single glassmorphism card ─── */
            [data-testid="column"]:first-child {
                min-height: calc(100vh - 16px) !important;
                height: calc(100vh - 16px) !important;
                position: relative !important;
            }
            [data-testid="column"]:first-child > [data-testid="stVerticalBlockBorderWrapper"] {
                height: 100% !important;
                position: relative !important;
                background: rgba(255,255,255,0.62) !important;
                backdrop-filter: saturate(180%) blur(22px) !important;
                -webkit-backdrop-filter: saturate(180%) blur(22px) !important;
                border: 1px solid rgba(15,23,42,0.08) !important;
                border-radius: 18px !important;
                box-shadow: 0 8px 24px rgba(15,23,42,0.07), 0 2px 6px rgba(15,23,42,0.04) !important;
                overflow: hidden !important;
            }
            [data-testid="column"]:first-child [data-testid="stVerticalBlock"] {
                gap: 0 !important;
            }
            /* ─── HIDE real Streamlit buttons (invisible but clickable) ─── */
            [data-testid="column"]:first-child .stButton {
                position: absolute !important;
                opacity: 0 !important;
                pointer-events: none !important;
                height: 0 !important;
                overflow: hidden !important;
                margin: 0 !important;
                padding: 0 !important;
            }
        </style>
        """, unsafe_allow_html=True)

        # Render entire sidebar as a single HTML component (matches reference exactly)
        deepdive_active = "active" if active_nav == "deepdive" else ""
        cowork_active = "active" if active_nav == "cowork" else ""

        sidebar_html = f"""
        <style>
            .sb-root {{ display:flex; flex-direction:column; height:100%; font-family:'Inter',system-ui,-apple-system,sans-serif; -webkit-font-smoothing:antialiased; }}
            .sb-brand {{ padding:1.4rem 1.2rem 1.2rem; display:flex; flex-direction:column; gap:0.7rem; }}
            .sb-brand img {{ height:28px; align-self:flex-start; }}
            .sb-brand .sb-title {{ font-family:'Manrope',sans-serif; font-weight:800; font-size:1.22rem; color:#0A1A3D; line-height:1.18; letter-spacing:-0.025em; }}
            .sb-brand .sb-subtitle {{ font-size:0.72rem; color:#64748B; font-weight:500; margin-top:0.15rem; }}
            .sb-divider {{ height:1px; background:rgba(15,23,42,0.08); margin:0 0.85rem; }}
            .sb-section-label {{ font-family:'Manrope',sans-serif; font-size:0.62rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#64748B; padding:0.95rem 1.15rem 0.4rem; }}
            .sb-nav {{ padding:0 0.55rem; }}
            .sb-nav-item {{
                position:relative; display:flex; align-items:center; gap:0.7rem;
                padding:0.55rem 0.7rem; margin:0.08rem 0; border-radius:8px;
                font-size:0.84rem; font-weight:500; color:#475569;
                cursor:pointer; transition:background 0.18s cubic-bezier(0.4,0,0.2,1), color 0.18s cubic-bezier(0.4,0,0.2,1);
                background:transparent; border:none; width:100%; text-align:left; font-family:inherit;
            }}
            .sb-nav-item:hover {{ background:rgba(15,23,42,0.04); color:#0F172A; }}
            .sb-nav-item:hover .sb-nav-icon {{ color:#163990; }}
            .sb-nav-item:hover .sb-nav-count {{ background:rgba(15,23,42,0.09); color:#475569; }}
            .sb-nav-item .sb-nav-icon {{ width:18px; height:18px; display:flex; align-items:center; justify-content:center; color:#64748B; transition:color 0.18s cubic-bezier(0.4,0,0.2,1); flex-shrink:0; }}
            .sb-nav-item .sb-nav-icon svg {{ width:16px; height:16px; stroke-width:1.8; fill:none; stroke:currentColor; }}
            .sb-nav-item .sb-nav-label {{ flex:1; min-width:0; }}
            .sb-nav-item .sb-nav-count {{ font-size:0.66rem; font-weight:600; color:#64748B; background:rgba(15,23,42,0.06); padding:0.12rem 0.42rem; border-radius:5px; font-variant-numeric:tabular-nums; transition:background 0.18s, color 0.18s; flex-shrink:0; line-height:1.3; }}
            .sb-nav-item.active {{ background:linear-gradient(90deg, rgba(28,79,192,0.10) 0%, rgba(28,79,192,0.04) 100%); color:#163990; font-weight:600; }}
            .sb-nav-item.active .sb-nav-icon {{ color:#163990; }}
            .sb-nav-item.active .sb-nav-count {{ background:rgba(28,79,192,0.14); color:#163990; }}
            .sb-nav-item.active::before {{ content:''; position:absolute; left:-0.55rem; top:6px; bottom:6px; width:3px; border-radius:0 3px 3px 0; background:linear-gradient(180deg, #1C4FC0, #41B6E6); box-shadow:0 0 8px rgba(28,79,192,0.3); }}
            .sb-spacer {{ flex:1; }}
            .sb-meta {{ padding:0.85rem 1.15rem 1rem; font-size:0.7rem; color:#64748B; line-height:1.55; border-top:1px solid rgba(15,23,42,0.06); background:linear-gradient(180deg, transparent 0%, rgba(28,79,192,0.025) 100%); }}
            .sb-meta strong {{ color:#475569; font-weight:600; }}
            .sb-meta .sb-meta-row {{ margin-bottom:0.2rem; }}
        </style>
        <div class="sb-root">
            <div class="sb-brand">
                <img src="https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png" alt="Pfizer">
                <div>
                    <div class="sb-title">Primary Care<br>Intelligence Hub</div>
                    <div class="sb-subtitle">Pfizer Analytics</div>
                </div>
            </div>
            <div class="sb-divider"></div>
            <div class="sb-section-label">Primary Care Workspace</div>
            <nav class="sb-nav">
                <button class="sb-nav-item {deepdive_active}" id="sb-nav-deepdive">
                    <span class="sb-nav-icon"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg></span>
                    <span class="sb-nav-label">Deep-Dive Dashboards</span>
                    <span class="sb-nav-count">8</span>
                </button>
                <button class="sb-nav-item {cowork_active}" id="sb-nav-cowork">
                    <span class="sb-nav-icon"><svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="10" rx="2"/><path d="M9 16v3M15 16v3M9 6V3M15 6V3M3 11h3M18 11h3"/></svg></span>
                    <span class="sb-nav-label">CoWork Agents</span>
                    <span class="sb-nav-count">3</span>
                </button>
            </nav>
            <div class="sb-spacer"></div>
            <div class="sb-meta">
                <div class="sb-meta-row"><strong>Primary Care Analytics</strong></div>
                <div class="sb-meta-row">Team_ZS_PC_Analytics@zs.com</div>
            </div>
        </div>
        <script>
        (function() {{
            // Wire HTML nav buttons to hidden Streamlit buttons
            var col = document.currentScript.closest('[data-testid="column"]') ||
                      document.querySelector('[data-testid="column"]:first-child');
            if (!col) return;

            function clickStreamlitButton(idx) {{
                // Re-enable pointer events momentarily and click
                var stButtons = col.querySelectorAll('.stButton');
                if (stButtons[idx]) {{
                    stButtons[idx].style.pointerEvents = 'auto';
                    stButtons[idx].style.opacity = '0';
                    stButtons[idx].style.height = 'auto';
                    stButtons[idx].style.overflow = 'visible';
                    stButtons[idx].style.position = 'relative';
                    var btn = stButtons[idx].querySelector('button');
                    if (btn) btn.click();
                }}
            }}

            var navDD = document.getElementById('sb-nav-deepdive');
            var navCW = document.getElementById('sb-nav-cowork');
            if (navDD) navDD.addEventListener('click', function() {{ clickStreamlitButton(0); }});
            if (navCW) navCW.addEventListener('click', function() {{ clickStreamlitButton(1); }});
        }})();
        </script>
        """
        st.markdown(sidebar_html, unsafe_allow_html=True)

        # Hidden Streamlit buttons (invisible but functional for session state updates)
        if st.button("Deep Dive Dashboards", key="nav_deepdive"):
            st.session_state["nav_state"] = "deepdive"
            st.rerun()

        if st.button("CoWork Agents", key="nav_cowork"):
            st.session_state["nav_state"] = "cowork"
            st.rerun()

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

        # Separator
        st.markdown("""
        <div style="text-align:center; padding:0.15rem 0 0.5rem;">
            <div style="width:80px; height:1px; background:linear-gradient(90deg,transparent,rgba(28,79,192,0.3),transparent); margin:0 auto;"></div>
        </div>
        """, unsafe_allow_html=True)

        # Conditional: Mission text (home) vs Brand tiles (deepdive) vs CoWork (cowork)
        if nav == "home":
            st.markdown("""
            <div style="text-align:center; padding:0.6rem 0 0;">
                <div style="font-family:'Manrope',sans-serif; font-weight:800; font-size:18px; color:#0A1A3D; letter-spacing:-0.02em; margin-bottom:0.5rem;">Welcome to the Primary Care Intelligence Hub</div>
                <div style="font-size:13px; color:#475569; line-height:1.7; max-width:580px; margin:0 auto;">
                    Empowering Pfizer's Primary Care business with real-time market intelligence, competitive analytics, and actionable insights across our key therapeutic brands. This platform consolidates NPA, DDD, and LAAD data sources into unified quarterly performance views.
                </div>
                <div style="margin-top:0.8rem; font-size:12px; color:#64748B;">
                    Select <strong style="color:#1C4FC0;">Deep Dive Dashboards</strong> or <strong style="color:#1C4FC0;">CoWork Agents</strong> in the sidebar to get started.
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif nav == "deepdive":
            # Deep Dive header + brand tiles
            st.markdown("""
            <div style="text-align:center; padding:0.1rem 0 0.6rem;">
                <div style="font-family:'Manrope',sans-serif; font-weight:700; font-size:15px; color:#0A1A3D; letter-spacing:-0.01em;">Deep Dive Dashboards</div>
                <div style="font-size:12px; color:#64748B; font-weight:400; margin-top:0.15rem;">Select a brand to explore detailed QoQ analysis, competitive trends, and exportable reports</div>
            </div>
            """, unsafe_allow_html=True)

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

        elif nav == "cowork":
            # CoWork Agents — Coming Soon placeholder
            st.markdown("""
            <div style="text-align:center; padding:2.5rem 0 0;">
                <div style="display:inline-flex; align-items:center; justify-content:center; width:64px; height:64px; border-radius:16px; background:rgba(28,79,192,0.06); margin-bottom:1rem;">
                    <span style="font-size:28px;">🤖</span>
                </div>
                <div style="font-family:'Manrope',sans-serif; font-weight:800; font-size:18px; color:#0A1A3D; letter-spacing:-0.02em; margin-bottom:0.5rem;">CoWork Agents</div>
                <div style="font-size:13px; color:#475569; line-height:1.7; max-width:480px; margin:0 auto;">
                    AI-powered analytical agents are being developed to assist with market insights, competitive intelligence, and automated reporting.
                </div>
                <div style="margin-top:1.2rem; display:inline-block; padding:6px 16px; border-radius:8px; background:rgba(28,79,192,0.06); border:1px solid rgba(28,79,192,0.12);">
                    <span style="font-family:'Manrope',sans-serif; font-size:12px; font-weight:700; color:#1C4FC0; letter-spacing:0.02em;">Coming Soon</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    # === RENDER BRAND PAGE ===
    import plotly.graph_objects as go
    from io import BytesIO
    from brand_pages import render_brand_page
    render_brand_page(nav, BRAND_CONFIG)
