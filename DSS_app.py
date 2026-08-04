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
    cards = []
    for brand in BRANDS:
        bdf = df[df['BRAND'] == brand].sort_values('YR_QTR_TXT')
        if bdf.empty:
            continue
        values = bdf['VALUE'].tolist()
        quarters = bdf['YR_QTR_TXT'].tolist()
        latest = values[-1]
        delta = latest - values[-2] if len(values) >= 2 else 0.0
        cards.append({
            'brand': brand,
            'value': f"{latest:.1f}%",
            'delta': f"{delta:+.1f}",
            'delta_class': 'up' if delta >= 0 else 'down',
            'color': BRAND_COLORS[brand],
            'prior_qtr': quarters[-2] if len(quarters) >= 2 else '',
            'latest_qtr': quarters[-1] if quarters else '',
        })
    return cards


brand_cards = build_brand_card_data(df)

# =====================================================
# BRAND CONFIG
# =====================================================
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

BRANDS_LIST = [
    ("Nurtec", "nurtec", "Oral CGRP market analytics"),
    ("Eliquis", "eliquis", "Oral Anticoagulant market analytics"),
    ("Prevnar", "prevnar", "PCV market analytics"),
    ("Comirnaty", "comirnaty", "COVID Vaccines market analytics"),
    ("Abrysvo", "abrysvo", "RSV market analytics"),
    ("Paxlovid", "paxlovid", "COVID Oral Treatment analytics"),
    ("Zavzpret", "zavzpret", "Zavzpret market analytics"),
    ("Beyfortus", "beyfortus", "Beyfortus market analytics"),
]

# =====================================================
# ROUTING — query param based
# =====================================================
brand_param = st.query_params.get("brand", None)

if brand_param and brand_param in BRAND_CONFIG:
    # === RENDER BRAND PAGE ===
    from brand_pages import render_brand_page
    render_brand_page(brand_param, BRAND_CONFIG)
else:
    # === RENDER LANDING PAGE as single HTML component ===
    st.markdown("""
    <style>
    [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
    [data-testid="stSidebar"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapseButton"],
    #MainMenu,footer,.stApp>header{display:none!important}
    .block-container{padding:0!important;max-width:100%!important}
    [data-testid="stAppViewBlockContainer"]{padding:0!important}
    [data-testid="stMainBlockContainer"]{padding:0!important}
    [data-testid="stVerticalBlock"]{gap:0!important}
    .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{overflow:hidden!important}
    </style>
    """, unsafe_allow_html=True)

    # Build hero KPI cards HTML
    hero_kpis_html = ""
    for c in brand_cards:
        delta_class = "up" if c['delta_class'] == 'up' else "down"
        tri = "&#9650;" if delta_class == "up" else "&#9660;"
        hero_kpis_html += f'''<div class="hero-kpi"><div class="kpi-label">{c['brand'].title()} TRx Mkt Share</div><div class="kpi-period">{c['latest_qtr']}</div><div class="kpi-value">{c['value']}</div><div class="kpi-delta {delta_class}"><span class="tri">{tri}</span>{c['delta']}pp <span class="vs">vs {c['prior_qtr']}</span></div></div>'''

    # Build brand cards HTML for dashboard section
    brand_cards_grid = ""
    for name, key, desc in BRANDS_LIST:
        brand_cards_grid += f'''<div class="card" onclick="window.open(window.parent.location.origin + window.parent.location.pathname + '?brand={key}', '_blank')"><div class="card-top"><span class="icon-chip chip-s1"><svg viewBox="0 0 24 24"><path d="M3 12h4l3-9 4 18 3-9h4" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></span></div><div class="card-title">{name}</div></div>'''

    landing_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
    --navy-900:#0A1A3D;--navy-700:#163990;--navy-600:#1C4FC0;--accent:#41B6E6;
    --bg:#EEF3FB;--surface:#FFFFFF;--text:#0F172A;--text-muted:#64748B;--text-soft:#475569;
    --hairline:rgba(15,23,42,0.08);--hairline-2:rgba(15,23,42,0.05);
    --up:#10B981;--down:#EF4444;
    --shadow-sm:0 2px 8px rgba(15,23,42,0.05),0 1px 2px rgba(15,23,42,0.04);
    --shadow-md:0 6px 16px rgba(15,23,42,0.07),0 2px 4px rgba(15,23,42,0.04);
    --shadow-lg:0 18px 40px rgba(15,23,42,0.10),0 6px 12px rgba(15,23,42,0.06);
    --shadow-panel:0 8px 24px rgba(15,23,42,0.07),0 2px 6px rgba(15,23,42,0.04);
    --ease:cubic-bezier(0.4,0,0.2,1);--ease-out:cubic-bezier(0.16,1,0.3,1);
    --sidebar-w:232px;--shell-pad:10px;--panel-radius:18px;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%}}
body{{font-family:'Inter',system-ui,sans-serif;background:radial-gradient(ellipse 80% 60% at 0% 0%,rgba(28,79,192,0.08) 0%,transparent 60%),radial-gradient(ellipse 70% 50% at 100% 0%,rgba(65,182,230,0.07) 0%,transparent 55%),radial-gradient(ellipse 60% 50% at 50% 100%,rgba(124,58,237,0.04) 0%,transparent 60%),var(--bg);color:var(--text);line-height:1.5;font-size:14px;-webkit-font-smoothing:antialiased;overflow:hidden}}
h1,h2,h3,h4{{font-family:'Manrope','Inter',system-ui,sans-serif;letter-spacing:-0.015em}}
.app{{height:100vh;display:grid;grid-template-columns:var(--sidebar-w) 1fr;gap:var(--shell-pad);padding:var(--shell-pad);overflow:hidden}}
.sidebar{{position:relative;background:rgba(255,255,255,0.62);backdrop-filter:saturate(180%) blur(22px);-webkit-backdrop-filter:saturate(180%) blur(22px);border:1px solid var(--hairline);border-radius:var(--panel-radius);box-shadow:var(--shadow-panel);display:flex;flex-direction:column;overflow:hidden}}
.sidebar-brand{{padding:1.4rem 1.2rem 1.2rem;display:flex;flex-direction:column;gap:0.7rem}}
.sidebar-brand img{{height:28px;align-self:flex-start}}
.sidebar-brand .title{{font-family:'Manrope',sans-serif;font-weight:800;font-size:1.22rem;color:var(--navy-900);line-height:1.18;letter-spacing:-0.025em}}
.sidebar-brand .subtitle{{font-size:0.72rem;color:var(--text-muted);font-weight:500}}
.sidebar-divider{{height:1px;background:var(--hairline);margin:0 0.85rem}}
.sidebar-section-label{{font-family:'Manrope',sans-serif;font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:var(--text-muted);padding:0.95rem 1.15rem 0.4rem}}
.nav{{padding:0 0.55rem}}
.nav-item{{position:relative;display:flex;align-items:center;gap:0.7rem;padding:0.55rem 0.7rem;margin:0.08rem 0;border-radius:8px;font-size:0.84rem;font-weight:500;color:var(--text-soft);cursor:pointer;transition:background 0.18s var(--ease),color 0.18s var(--ease);background:transparent;border:none;width:100%;text-align:left;font-family:inherit}}
.nav-item .nav-icon{{width:18px;height:18px;display:flex;align-items:center;justify-content:center;color:var(--text-muted);transition:color 0.18s var(--ease);flex-shrink:0}}
.nav-item .nav-icon svg{{width:16px;height:16px;stroke-width:1.8;fill:none;stroke:currentColor}}
.nav-item .nav-label{{flex:1;min-width:0}}
.nav-item .nav-count{{font-size:0.66rem;font-weight:600;color:var(--text-muted);background:rgba(15,23,42,0.06);padding:0.12rem 0.42rem;border-radius:5px;font-variant-numeric:tabular-nums;flex-shrink:0;line-height:1.3}}
.nav-item:hover{{background:rgba(15,23,42,0.04);color:var(--text)}}
.nav-item:hover .nav-icon{{color:var(--navy-700)}}
.nav-item.active{{background:linear-gradient(90deg,rgba(28,79,192,0.10) 0%,rgba(28,79,192,0.04) 100%);color:var(--navy-700);font-weight:600}}
.nav-item.active .nav-icon{{color:var(--navy-700)}}
.nav-item.active .nav-count{{background:rgba(28,79,192,0.14);color:var(--navy-700)}}
.nav-item.active::before{{content:'';position:absolute;left:-0.55rem;top:6px;bottom:6px;width:3px;border-radius:0 3px 3px 0;background:linear-gradient(180deg,var(--navy-600),var(--accent));box-shadow:0 0 8px rgba(28,79,192,0.3)}}
.sidebar-spacer{{flex:1}}
.sidebar-meta{{padding:0.85rem 1.15rem 1rem;font-size:0.7rem;color:var(--text-muted);line-height:1.55;border-top:1px solid var(--hairline);background:linear-gradient(180deg,transparent 0%,rgba(28,79,192,0.025) 100%)}}
.sidebar-meta strong{{color:var(--text-soft);font-weight:600}}
.sidebar-meta .meta-row{{margin-bottom:0.2rem}}
.main{{background:rgba(255,255,255,0.55);backdrop-filter:saturate(180%) blur(14px);-webkit-backdrop-filter:saturate(180%) blur(14px);border:1px solid var(--hairline);border-radius:var(--panel-radius);box-shadow:var(--shadow-panel);display:flex;flex-direction:column;overflow:hidden;min-width:0}}
.content{{flex:1;min-height:0;overflow-y:auto;padding:1.4rem}}
.content::-webkit-scrollbar{{width:6px}}
.content::-webkit-scrollbar-thumb{{background:rgba(15,23,42,0.14);border-radius:3px}}
.section{{display:none;opacity:0;transform:translateY(4px);transition:opacity 0.22s var(--ease),transform 0.22s var(--ease-out)}}
.section.is-active{{display:block}}
.section.is-visible{{opacity:1;transform:translateY(0)}}
.section-head{{margin-bottom:1rem}}
.section-head h2{{font-size:1.35rem;font-weight:700;color:var(--navy-900);letter-spacing:-0.02em;margin-bottom:0.2rem}}
.section-head p{{font-size:0.84rem;color:var(--text-muted);max-width:680px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}
.card{{position:relative;display:flex;flex-direction:column;background:var(--surface);border-radius:14px;padding:1.15rem 1.2rem;min-height:148px;overflow:hidden;box-shadow:var(--shadow-sm);transition:transform 0.28s var(--ease-out),box-shadow 0.28s var(--ease);cursor:pointer}}
.card::after{{content:'';position:absolute;inset:0;border-radius:inherit;background:linear-gradient(135deg,rgba(255,255,255,0) 55%,rgba(65,182,230,0.05) 80%,rgba(28,79,192,0.07) 100%);opacity:0;transition:opacity 0.28s var(--ease);pointer-events:none}}
.card:hover{{transform:translateY(-3px);box-shadow:var(--shadow-lg)}}
.card:hover::after{{opacity:1}}
.card-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:0.7rem}}
.icon-chip{{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.icon-chip svg{{width:19px;height:19px;stroke-width:1.8;fill:none}}
.chip-s1{{background:linear-gradient(135deg,#DBEAFE,#BFDBFE)}}
.chip-s1 svg{{stroke:#1D4ED8}}
.chip-s3{{background:linear-gradient(135deg,#EDE9FE,#DDD6FE)}}
.chip-s3 svg{{stroke:#6D28D9}}
.card-title{{font-family:'Manrope',sans-serif;font-size:1.02rem;font-weight:700;color:var(--navy-900);line-height:1.25;margin-bottom:0.3rem}}
.card-desc{{font-size:0.8rem;color:var(--text-muted);line-height:1.5;flex:1;margin-bottom:0.85rem}}
.dest-pill{{display:inline-flex;align-items:center;gap:0.35rem;font-size:0.7rem;font-weight:600;color:var(--text-soft);padding:0.22rem 0.55rem;border-radius:6px;background:rgba(15,23,42,0.05);align-self:flex-start}}
.hero{{position:relative;background:radial-gradient(ellipse 90% 80% at 20% 20%,rgba(28,79,192,0.06) 0%,transparent 50%),radial-gradient(ellipse 60% 70% at 80% 80%,rgba(65,182,230,0.05) 0%,transparent 50%),linear-gradient(135deg,rgba(255,255,255,0.9) 0%,rgba(248,250,253,0.95) 100%);border-radius:16px;padding:2rem 2rem 1.6rem;border:1px solid var(--hairline-2);box-shadow:var(--shadow-sm);overflow:hidden}}
.hero::before{{content:'';position:absolute;top:-1px;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--navy-600),var(--accent),#3B6FD9);border-radius:16px 16px 0 0;opacity:0.7}}
.hero-header{{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1.5rem}}
.hero-title{{font-family:'Manrope',sans-serif;font-size:1.65rem;font-weight:800;color:var(--navy-900);letter-spacing:-0.025em;line-height:1.15;margin-bottom:0.35rem}}
.hero-subtitle{{font-size:0.82rem;font-weight:500;color:var(--text-muted);display:flex;align-items:center;gap:0.5rem}}
.hero-subtitle .dot{{width:4px;height:4px;border-radius:50%;background:var(--text-muted);opacity:0.5}}
.hero-kpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:0.75rem}}
.hero-kpi{{background:rgba(255,255,255,0.75);backdrop-filter:blur(8px);border:1px solid var(--hairline-2);border-radius:12px;padding:0.85rem 1rem 0.8rem;transition:transform 0.25s var(--ease-out),box-shadow 0.25s var(--ease)}}
.hero-kpi:hover{{transform:translateY(-2px);box-shadow:var(--shadow-md)}}
.hero-kpi .kpi-label{{font-size:0.7rem;color:var(--text-muted);font-weight:500;margin-bottom:0.25rem}}
.hero-kpi .kpi-value{{font-family:'Manrope',sans-serif;font-size:1.5rem;font-weight:700;color:var(--navy-900);line-height:1.1;letter-spacing:-0.02em;font-variant-numeric:tabular-nums;margin-bottom:0.3rem}}
.hero-kpi .kpi-delta{{display:inline-flex;align-items:center;gap:0.25rem;font-size:0.7rem;font-weight:600;font-variant-numeric:tabular-nums}}
.hero-kpi .kpi-delta.up{{color:var(--up)}}
.hero-kpi .kpi-delta.down{{color:var(--down)}}
.hero-kpi .kpi-delta .tri{{font-size:0.65rem;line-height:1}}
.hero-kpi .kpi-delta .vs{{color:var(--text-muted);font-weight:500}}
.hero-kpi .kpi-period{{font-size:0.62rem;color:var(--text-muted);font-weight:500;margin-bottom:0.15rem;opacity:0.8}}
.workspace-divider{{height:1px;background:var(--hairline);margin:1.4rem 0}}
.dropdown-wrap{{position:relative}}
.icon-btn{{display:inline-flex;align-items:center;gap:0.4rem;padding:0.4rem 0.7rem;border-radius:7px;background:rgba(255,255,255,0.7);border:1px solid var(--hairline);color:var(--text-soft);font-size:0.75rem;font-weight:500;cursor:pointer;font-family:inherit;transition:all 0.18s var(--ease)}}
.icon-btn:hover{{background:#fff;color:var(--navy-700);border-color:rgba(28,79,192,0.25)}}
.icon-btn svg{{width:13px;height:13px;stroke-width:1.8;fill:none;stroke:currentColor}}
.dropdown{{position:absolute;top:calc(100% + 6px);right:0;background:rgba(255,255,255,0.96);backdrop-filter:saturate(180%) blur(20px);border:1px solid var(--hairline);border-radius:12px;box-shadow:var(--shadow-lg);min-width:320px;padding:0.45rem 0;opacity:0;visibility:hidden;transform:translateY(-6px) scale(0.98);transform-origin:top right;transition:opacity 0.2s var(--ease),transform 0.2s var(--ease),visibility 0.2s;z-index:200}}
.dropdown.show{{opacity:1;visibility:visible;transform:translateY(0) scale(1)}}
.dropdown-header{{font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--text-muted);padding:0.5rem 0.95rem 0.35rem}}
.dropdown-item{{display:flex;align-items:center;justify-content:space-between;padding:0.45rem 0.95rem;font-size:0.78rem}}
.dropdown-item:hover{{background:rgba(15,23,42,0.04)}}
.dropdown-item .src{{font-weight:500}}
.dropdown-item .date{{font-size:0.7rem;color:var(--text-muted);font-variant-numeric:tabular-nums;white-space:nowrap}}
.section-head-row{{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-bottom:0.2rem}}
</style>
</head>
<body>
<div class="app">
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
    <nav class="nav" id="sidebarNav">
        <button class="nav-item active" data-target="dashboards">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg></span>
            <span class="nav-label">Deep-Dive Dashboards</span>
            <span class="nav-count">8</span>
        </button>
        <button class="nav-item" data-target="agents">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="10" rx="2"/><path d="M9 16v3M15 16v3M9 6V3M15 6V3M3 11h3M18 11h3"/></svg></span>
            <span class="nav-label">CoWork Agents</span>
            <span class="nav-count">3</span>
        </button>
    </nav>
    <div class="sidebar-spacer"></div>
    <div class="sidebar-meta">
        <div class="meta-row"><strong>Primary Care Analytics</strong></div>
        <div class="meta-row">Team_ZS_PC_Analytics@zs.com</div>
        <div class="meta-row">Data till {max_date_raw}</div>
    </div>
</aside>
<div class="main">
<main class="content">
    <div class="hero">
        <div class="hero-header">
            <div>
                <h1 class="hero-title">Primary Care Performance Summary</h1>
                <div class="hero-subtitle"><span>QoQ TRx Market Share</span><span class="dot"></span><span>NPA Data</span></div>
            </div>
            <div class="dropdown-wrap">
                <button class="icon-btn" onclick="toggleDropdown(event)"><svg viewBox="0 0 24 24"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>Data Availability<svg viewBox="0 0 24 24" style="width:11px;height:11px;"><path d="M6 9l6 6 6-6"/></svg></button>
                <div class="dropdown" id="dataDropdown">
                    <div class="dropdown-header">Last refresh by source</div>
                    <div class="dropdown-item"><span class="src">NPA</span><span class="date">{max_date_raw}</span></div>
                    <div class="dropdown-item"><span class="src">DDD</span><span class="date">{max_date_raw}</span></div>
                    <div class="dropdown-item"><span class="src">LAAD</span><span class="date">{max_date_raw}</span></div>
                    <div class="dropdown-item"><span class="src">Refreshed</span><span class="date">{refresh_ts}</span></div>
                </div>
            </div>
        </div>
        <div class="hero-kpis">
            {hero_kpis_html}
        </div>
    </div>
    <div class="workspace-divider"></div>

    <!-- DASHBOARDS SECTION -->
    <section class="section is-active is-visible" id="dashboards">
        <div class="section-head">
            <div class="section-head-row"><h2>Deep-Dive Dashboards</h2></div>
            <p>Select a brand to explore detailed QoQ analysis, competitive trends, and exportable reports.</p>
        </div>
        <div class="grid">
            {brand_cards_grid}
        </div>
    </section>

    <!-- AGENTS SECTION -->
    <section class="section" id="agents">
        <div class="section-head"><h2>CoWork Agents</h2><p>AI-powered analytical agents for automated insights and conversational data exploration.</p></div>
        <div style="text-align:center;padding:3rem 0;">
            <div style="display:inline-flex;align-items:center;justify-content:center;width:64px;height:64px;border-radius:16px;background:rgba(28,79,192,0.06);margin-bottom:1rem;">
                <span style="font-size:28px;">&#129302;</span>
            </div>
            <div style="font-family:'Manrope',sans-serif;font-weight:800;font-size:18px;color:var(--navy-900);margin-bottom:0.5rem;">CoWork Agents</div>
            <div style="font-size:13px;color:var(--text-muted);line-height:1.7;max-width:480px;margin:0 auto;">AI-powered analytical agents are being developed to assist with market insights, competitive intelligence, and automated reporting.</div>
            <div style="margin-top:1.2rem;display:inline-block;padding:6px 16px;border-radius:8px;background:rgba(28,79,192,0.06);border:1px solid rgba(28,79,192,0.12);">
                <span style="font-family:'Manrope',sans-serif;font-size:12px;font-weight:700;color:var(--navy-600);letter-spacing:0.02em;">Coming Soon</span>
            </div>
        </div>
    </section>
</main>
</div>
</div>
<script>
(function() {{
    'use strict';
    window.toggleDropdown = function(ev) {{
        ev.stopPropagation();
        document.getElementById('dataDropdown').classList.toggle('show');
    }};
    document.addEventListener('click', function(e) {{
        if (!e.target.closest('.dropdown-wrap')) document.querySelectorAll('.dropdown.show').forEach(function(d){{d.classList.remove('show')}});
    }});
    var nav = document.getElementById('sidebarNav');
    var items = nav.querySelectorAll('.nav-item');
    var sections = {{}};
    items.forEach(function(it){{ sections[it.dataset.target] = document.getElementById(it.dataset.target); }});
    var switching = false;
    function showSection(id) {{
        if (switching) return;
        var current = document.querySelector('.section.is-active');
        var next = sections[id];
        if (!next || next === current) return;
        switching = true;
        if (current) current.classList.remove('is-visible');
        setTimeout(function() {{
            if (current) current.classList.remove('is-active');
            document.querySelector('.content').scrollTop = 0;
            next.classList.add('is-active');
            void next.offsetWidth;
            next.classList.add('is-visible');
            switching = false;
        }}, 220);
    }}
    items.forEach(function(item) {{
        item.addEventListener('click', function(e) {{
            e.preventDefault();
            items.forEach(function(i){{ i.classList.remove('active'); }});
            item.classList.add('active');
            showSection(item.dataset.target);
        }});
    }});
}})();
</script>
</body>
</html>"""

    st.components.v1.html(landing_html, height=920, scrolling=False)
