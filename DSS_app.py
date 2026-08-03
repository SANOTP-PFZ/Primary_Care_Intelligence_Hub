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

# Compute refresh timestamp (from dataset build metrics, converted UTC → IST)
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
                    <div class="card-footer"><span class="card-source">NPA</span> {c['first_qtr']} → {c['latest_qtr']}</div>
                </div>''')
    return "\n".join(html_cards)


brand_cards_html = render_brand_cards_html(brand_cards)

# Hide all Streamlit chrome
st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"], #MainMenu, footer,
    .stApp > header { display: none !important; }
    .stApp { background: transparent !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewBlockContainer"] { padding: 0 !important; }
    [data-testid="stMainBlockContainer"] { padding: 0 8px !important; }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }
</style>
""", unsafe_allow_html=True)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
    --navy-900: #0A1A3D;
    --navy-800: #102A5C;
    --navy-700: #163990;
    --navy-600: #1C4FC0;
    --navy-500: #3B6FD9;
    --accent: #41B6E6;
    --bg: #EEF3FB;
    --surface: #FFFFFF;
    --text: #0F172A;
    --text-muted: #64748B;
    --text-soft: #475569;
    --hairline: rgba(15,23,42,0.08);
    --shadow-panel: 0 8px 24px rgba(15,23,42,0.07), 0 2px 6px rgba(15,23,42,0.04);
    --ease: cubic-bezier(0.4, 0, 0.2, 1);
    --sidebar-w: 232px;
    --shell-pad: 10px;
    --panel-radius: 18px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { height: 100%; }
body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background:
        radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.07) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 50% 100%, rgba(124,58,237,0.04) 0%, transparent 60%),
        var(--bg);
    color: var(--text);
    line-height: 1.5;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
    overflow: hidden;
}
h1, h2, h3, h4 { font-family: 'Manrope', 'Inter', system-ui, sans-serif; letter-spacing: -0.015em; }

/* APP SHELL */
.app { height: 100vh; display: grid; grid-template-columns: var(--sidebar-w) 1fr; gap: var(--shell-pad); padding: var(--shell-pad); overflow: hidden; }

/* SIDEBAR */
.sidebar {
    background: rgba(255,255,255,0.62);
    backdrop-filter: saturate(180%) blur(22px);
    -webkit-backdrop-filter: saturate(180%) blur(22px);
    border: 1px solid var(--hairline);
    border-radius: var(--panel-radius);
    box-shadow: var(--shadow-panel);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Brand section (top) */
.sidebar-brand {
    padding: 10px 1.2rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.sidebar-brand img { height: 28px; align-self: flex-start; }
.sidebar-brand .title {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 1.22rem;
    color: var(--navy-900);
    line-height: 1.18;
    letter-spacing: -0.025em;
}
.sidebar-brand .subtitle { font-size: 0.72rem; color: var(--text-muted); font-weight: 500; }

/* Divider */
.sidebar-divider { height: 1px; background: var(--hairline); margin: 0 0.85rem; }

/* Section label */
.sidebar-section-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    padding: 0.95rem 1.15rem 0.4rem;
}

/* Nav items */
.nav { padding: 0 0.55rem; }
.nav-item {
    position: relative;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.55rem 0.7rem;
    margin: 0.08rem 0;
    border-radius: 8px;
    font-size: 0.84rem;
    font-weight: 500;
    color: var(--text-soft);
    cursor: pointer;
    transition: background 0.18s var(--ease), color 0.18s var(--ease);
    background: transparent;
    border: none;
    width: 100%;
    text-align: left;
    font-family: inherit;
}
.nav-item .nav-icon { width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); transition: color 0.18s var(--ease); flex-shrink: 0; }
.nav-item .nav-icon svg { width: 16px; height: 16px; stroke-width: 1.8; fill: none; stroke: currentColor; }
.nav-item .nav-label { flex: 1; min-width: 0; }
.nav-item:hover { background: rgba(15,23,42,0.04); color: var(--text); }
.nav-item:hover .nav-icon { color: var(--navy-700); }
.nav-item.active { background: linear-gradient(90deg, rgba(28,79,192,0.10) 0%, rgba(28,79,192,0.04) 100%); color: var(--navy-700); font-weight: 600; }
.nav-item.active .nav-icon { color: var(--navy-700); }
.nav-item.active::before { content: ''; position: absolute; left: -0.55rem; top: 6px; bottom: 6px; width: 3px; border-radius: 0 3px 3px 0; background: linear-gradient(180deg, var(--navy-600), var(--accent)); box-shadow: 0 0 8px rgba(28,79,192,0.3); }

/* Spacer pushes footer to bottom */
.sidebar-spacer { flex: 1; }

/* Footer (bottom) */
.sidebar-meta {
    padding: 0.85rem 1.15rem 1rem;
    font-size: 0.7rem;
    color: var(--text-muted);
    line-height: 1.55;
    border-top: 1px solid var(--hairline);
    background: linear-gradient(180deg, transparent 0%, rgba(28,79,192,0.025) 100%);
}
.sidebar-meta strong { color: var(--text-soft); font-weight: 600; }
.sidebar-meta .meta-row { margin-bottom: 0.2rem; }

/* MAIN PANEL */
.main {
    background: rgba(255,255,255,0.55);
    backdrop-filter: saturate(180%) blur(14px);
    -webkit-backdrop-filter: saturate(180%) blur(14px);
    border: 1px solid var(--hairline);
    border-radius: var(--panel-radius);
    box-shadow: var(--shadow-panel);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0;
}
.content { flex: 1; min-height: 0; overflow: hidden; padding: 1.2rem; display: flex; flex-direction: column; }

/* SECTION HEADER */
.section-header {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 17.5px;
    color: var(--navy-900);
    margin-bottom: 0.25rem;
}
.section-subtitle {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 500;
    margin-bottom: 1rem;
}

/* BRAND SUMMARY CONTAINER */
.brand-summary {
    background: rgba(255,255,255,0.62);
    backdrop-filter: saturate(180%) blur(22px);
    -webkit-backdrop-filter: saturate(180%) blur(22px);
    border: 1px solid var(--hairline);
    border-radius: var(--panel-radius);
    box-shadow: var(--shadow-panel);
    padding: 1.1rem;
}

/* BRAND CARDS GRID - single row */
.brand-cards {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem;
}

/* INDIVIDUAL BRAND CARD - compact squarish */
.brand-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: saturate(160%) blur(12px);
    -webkit-backdrop-filter: saturate(160%) blur(12px);
    border: 1px solid var(--hairline);
    border-radius: 16px;
    padding: 0.7rem 0.75rem 0.5rem;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
    transition: box-shadow 0.2s var(--ease), transform 0.2s var(--ease);
    aspect-ratio: 1.4 / 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.brand-card:hover {
    box-shadow: 0 6px 16px rgba(15,23,42,0.08);
    transform: translateY(-1px);
}
.card-top {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.35rem;
}
.brand-name {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: var(--navy-900);
}
.brand-metric {
    display: flex;
    align-items: center;
    gap: 0.3rem;
}
.brand-value {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 16px;
    color: var(--text);
}
.brand-delta {
    font-size: 11px;
    font-weight: 600;
    padding: 1px 5px;
    border-radius: 4px;
}
.brand-delta.up { color: #059669; background: rgba(16,185,129,0.1); }
.brand-delta.down { color: #DC2626; background: rgba(239,68,68,0.08); }
.brand-spark { width: 100%; }
.brand-spark svg { width: 100%; height: 28px; display: block; }
.card-footer {
    font-size: 10.5px;
    color: var(--text-muted);
    font-weight: 500;
    text-align: center;
    margin-top: 0.25rem;
    letter-spacing: 0.02em;
}
.card-source {
    display: inline-block;
    background: rgba(28,79,192,0.08);
    color: var(--navy-700);
    font-size: 9.5px;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 3px;
    letter-spacing: 0.05em;
    margin-right: 3px;
}

/* DATA FRESHNESS STRIP */
.data-freshness {
    margin-top: 0.85rem;
    padding: 0.6rem 0.9rem;
    border-radius: 10px;
    background: rgba(28,79,192,0.03);
    border: 1px solid rgba(28,79,192,0.08);
    display: flex;
    gap: 1.8rem;
    align-items: center;
    flex-wrap: wrap;
}
.data-freshness-label {
    font-family: 'Manrope', sans-serif;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--navy-700);
}
.data-freshness-item {
    font-size: 12px;
    color: var(--text-soft);
    font-weight: 500;
}
.data-freshness-item strong {
    color: var(--navy-900);
    font-weight: 600;
}
.data-freshness-divider {
    width: 1px;
    height: 14px;
    background: rgba(28,79,192,0.2);
}
.data-refreshed {
    margin-left: auto;
    color: var(--text-muted);
}

/* MISSION STATEMENT */
.hub-mission {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 0.6rem 3rem;
}
.mission-divider {
    width: 80px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(28,79,192,0.3), transparent);
    margin: 0 auto 0.8rem;
}
.mission-text {
    font-family: 'Manrope', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: var(--navy-900);
    line-height: 1.55;
    margin-bottom: 0.6rem;
    letter-spacing: -0.01em;
    max-width: 520px;
}
.mission-sub {
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 400;
    line-height: 1.55;
    margin-bottom: 1.2rem;
    max-width: 480px;
}
.mission-sub strong {
    color: var(--navy-700);
    font-weight: 600;
}

/* DEEP DIVE BRAND SELECTION */
.deep-dive-section {
    padding: 0.8rem 0 0;
    flex: 1;
    display: flex;
    flex-direction: column;
}
.deep-dive-section .mission-divider {
    margin: 0 auto 1rem;
}
.deep-dive-header {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 15.5px;
    color: var(--navy-900);
    margin-bottom: 0.25rem;
    text-align: center;
    letter-spacing: -0.01em;
}
.deep-dive-subtitle {
    font-size: 12.5px;
    color: var(--text-muted);
    text-align: center;
    margin-bottom: 1rem;
    font-weight: 400;
}
.deep-dive-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: 1fr 1fr;
    gap: 0.9rem;
    padding: 0 0.3rem;
    flex: 1;
}
.deep-dive-tile {
    background: rgba(255,255,255,0.72);
    backdrop-filter: saturate(160%) blur(12px);
    -webkit-backdrop-filter: saturate(160%) blur(12px);
    border: 1px solid var(--hairline);
    border-radius: 14px;
    padding: 1.5rem 1.2rem;
    text-align: center;
    cursor: pointer;
    transition: transform 0.22s var(--ease), box-shadow 0.22s var(--ease), border-color 0.18s var(--ease);
    box-shadow: 0 2px 6px rgba(15,23,42,0.03);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 80px;
}
.deep-dive-tile:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(15,23,42,0.09);
    border-color: rgba(28,79,192,0.3);
}
.deep-dive-tile .tile-name {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 15px;
    color: var(--navy-900);
}
</style>
</head>
<body>
<div class="app">

<!-- SIDEBAR -->
<aside class="sidebar">
    <div class="sidebar-brand">
        <img src="https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png" alt="Pfizer">
        <div>
            <div class="title">Primary Care<br>Intelligence Hub</div>
            <div class="subtitle">Pfizer Analytics</div>
        </div>
    </div>

    <div class="sidebar-divider"></div>

    <div class="sidebar-section-label">Primary Care Workspace</div>
    <nav class="nav">
        <button class="nav-item" id="nav-deepdive" onclick="activateDeepDive()">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg></span>
            <span class="nav-label">Deep Dive Dashboards</span>
        </button>
        <button class="nav-item" id="nav-cowork" onclick="activateCowork()">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="10" rx="2"/><path d="M9 16v3M15 16v3M9 6V3M15 6V3M3 11h3M18 11h3"/></svg></span>
            <span class="nav-label">CoWork Agents</span>
        </button>
    </nav>

    <div class="sidebar-spacer"></div>

    <div class="sidebar-meta">
        <div class="meta-row"><strong>Primary Care Analytics</strong></div>
        <div class="meta-row">Team_ZS_PC_Analytics@zs.com</div>
    </div>
</aside>

<!-- MAIN PANEL -->
<div class="main">
    <main class="content">
        <div class="brand-summary">
            <div class="section-header">Primary Care Brand Performance Summary</div>
            <div class="section-subtitle">QoQ TRx Market Share Trends</div>

            <div class="brand-cards">
__BRAND_CARDS__
            </div>

            <div class="data-freshness">
                <span class="data-freshness-label">Data Availability</span>
                <span class="data-freshness-item"><strong>NPA:</strong> Till __MAX_DATE__</span>
                <span class="data-freshness-item"><strong>DDD:</strong> Till __MAX_DATE__</span>
                <span class="data-freshness-item"><strong>LAAD:</strong> Till __MAX_DATE__</span>
                <span class="data-freshness-divider"></span>
                <span class="data-freshness-item data-refreshed"><strong>Refreshed:</strong> __REFRESH_TS__</span>
            </div>
        </div>

        <!-- MISSION STATEMENT (visible by default) -->
        <div class="hub-mission" id="mission-section">
            <div class="mission-divider"></div>
            <p class="mission-text">Your single source of truth for Primary Care brand performance analytics across NPA, DDD, and LAAD data sources.</p>
            <p class="mission-sub">Use <strong>Deep Dive Dashboards</strong> in the sidebar for detailed QoQ analysis, competitive trends, and exportable reports.</p>
            <div class="mission-divider"></div>
        </div>

        <!-- Deep dive brand tiles are rendered natively by Streamlit below the iframe -->
    </main>
</div>

</div>

<script>
// Sidebar nav interactions (visual only — deep dive tiles rendered natively by Streamlit)
function clearActive() {
    document.querySelectorAll('.nav-item').forEach(function(item) {
        item.classList.remove('active');
    });
}
function activateDeepDive() {
    clearActive();
    document.getElementById('nav-deepdive').classList.add('active');
    document.getElementById('mission-section').style.display = 'none';
}
function activateCowork() {
    clearActive();
    document.getElementById('nav-cowork').classList.add('active');
    document.getElementById('mission-section').style.display = 'flex';
}
</script>
</body>
</html>
"""

html_content = html_content.replace("__BRAND_CARDS__", brand_cards_html)
html_content = html_content.replace("__MAX_DATE__", max_date_raw)
html_content = html_content.replace("__REFRESH_TS__", refresh_ts)

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
    # === RENDER ORIGINAL LANDING PAGE (iframe: sidebar + summary cards + mission) ===
    st.components.v1.html(html_content, height=520, scrolling=False)

    # === DEEP DIVE BRAND TILES (native Streamlit buttons, styled to match iframe design) ===
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Container to visually continue the landing page panel */
    .deep-dive-container {
        background: rgba(255,255,255,0.55);
        backdrop-filter: saturate(180%) blur(14px);
        -webkit-backdrop-filter: saturate(180%) blur(14px);
        border: 1px solid rgba(15,23,42,0.08);
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(15,23,42,0.07), 0 2px 6px rgba(15,23,42,0.04);
        padding: 1.2rem 1.4rem;
        margin: -8px 10px 20px 10px;
    }
    .deep-dive-container .dd-divider {
        width: 80px;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(28,79,192,0.3), transparent);
        margin: 0 auto 0.9rem;
    }
    .deep-dive-container .dd-header {
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
        font-size: 15.5px;
        color: #0A1A3D;
        margin-bottom: 0.25rem;
        text-align: center;
        letter-spacing: -0.01em;
    }
    .deep-dive-container .dd-subtitle {
        font-size: 12.5px;
        color: #64748B;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 400;
    }

    /* Style the Streamlit buttons to match the deep-dive tiles exactly */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: rgba(255,255,255,0.72) !important;
        backdrop-filter: saturate(160%) blur(12px) !important;
        -webkit-backdrop-filter: saturate(160%) blur(12px) !important;
        border: 1px solid rgba(15,23,42,0.08) !important;
        border-radius: 14px !important;
        padding: 1.3rem 1rem !important;
        color: #0A1A3D !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        font-family: 'Manrope', 'Inter', system-ui, sans-serif !important;
        cursor: pointer !important;
        transition: transform 0.22s cubic-bezier(0.4,0,0.2,1), box-shadow 0.22s cubic-bezier(0.4,0,0.2,1), border-color 0.18s cubic-bezier(0.4,0,0.2,1) !important;
        box-shadow: 0 2px 6px rgba(15,23,42,0.03) !important;
        min-height: 70px !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(15,23,42,0.09) !important;
        border-color: rgba(28,79,192,0.3) !important;
        background: rgba(255,255,255,0.92) !important;
    }
    </style>
    <div class="deep-dive-container">
        <div class="dd-divider"></div>
        <div class="dd-header">Deep Dive Dashboards</div>
        <div class="dd-subtitle">Select a brand to explore detailed QoQ analysis, competitive trends, and exportable reports</div>
    </div>
    """, unsafe_allow_html=True)

    brands_list = [
        ("Nurtec", "nurtec"), ("Eliquis", "eliquis"), ("Prevnar", "prevnar"), ("Comirnaty", "comirnaty"),
        ("Abrysvo", "abrysvo"), ("Paxlovid", "paxlovid"), ("Zavzpret", "zavzpret"), ("Beyfortus", "beyfortus"),
    ]

    # Row 1: first 4 brands
    cols1 = st.columns(4, gap="small")
    for i, (name, key) in enumerate(brands_list[:4]):
        with cols1[i]:
            if st.button(name, key=f"brand_btn_{key}", use_container_width=True):
                st.session_state["nav_state"] = key
                st.rerun()

    # Row 2: last 4 brands
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
