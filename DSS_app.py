"""
Primary Care Intelligence Hub - Landing Page
Streamlit columns approach: sidebar (HTML) + interactive main content (Streamlit native).
"""
import streamlit as st
import dataiku
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Primary Care Intelligence Hub",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================
# SESSION STATE
# =====================================================
if "nav_state" not in st.session_state:
    st.session_state["nav_state"] = "home"  # "home" | "deepdive" | brand key

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

# =====================================================
# DATA LOADING
# =====================================================
BRANDS = ['NURTEC', 'ELIQUIS', 'PREVNAR', 'COMIRNATY', 'ABRYSVO']
BRAND_COLORS = {
    'NURTEC': '#1C4FC0', 'ELIQUIS': '#41B6E6', 'PREVNAR': '#7C3AED',
    'COMIRNATY': '#10B981', 'ABRYSVO': '#F59E0B',
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
all_quarters = sorted(df['YR_QTR_TXT'].unique())
latest_qtr = all_quarters[-1] if all_quarters else 'N/A'

try:
    max_date_df = dataiku.Dataset("SQL_NPA_MAX_DATE_SF").get_dataframe()
    max_date_raw = str(max_date_df.iloc[0, 0]).split(" ")[0]
except Exception:
    max_date_raw = latest_qtr

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

# =====================================================
# GLOBAL STYLES
# =====================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"], #MainMenu, footer,
    .stApp > header { display: none !important; }
    .stApp { background: radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.08) 0%, transparent 60%), radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.07) 0%, transparent 55%), #EEF3FB !important; }
    .block-container { padding: 10px 10px 0 10px !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
    h1, h2, h3, h4 { font-family: 'Manrope', sans-serif; letter-spacing: -0.015em; color: #0A1A3D; }
    /* Sidebar nav button styling */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) .stButton > button {
        width: 100%; text-align: left; justify-content: flex-start;
        background: transparent !important; border: none !important; box-shadow: none !important;
        padding: 8px 12px !important; border-radius: 8px !important;
        font-size: 13px !important; font-weight: 500 !important; color: #475569 !important;
    }
    div[data-testid="stVerticalBlock"] > div:nth-child(1) .stButton > button:hover {
        background: rgba(28,79,192,0.06) !important; color: #1C4FC0 !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# LAYOUT: Sidebar column + Main content column
# =====================================================
sidebar_col, main_col = st.columns([1, 5], gap="small")

# --- SIDEBAR (left column) ---
with sidebar_col:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.62); backdrop-filter:saturate(180%) blur(22px); -webkit-backdrop-filter:saturate(180%) blur(22px); border:1px solid rgba(15,23,42,0.08); border-radius:18px; box-shadow:0 8px 24px rgba(15,23,42,0.07); padding:14px 16px 12px; height:calc(100vh - 30px); display:flex; flex-direction:column; overflow:hidden;">
        <div style="margin-bottom:10px;">
            <div style="font-family:'Manrope',sans-serif; font-weight:800; font-size:1.1rem; color:#0A1A3D; line-height:1.18; letter-spacing:-0.025em;">Primary Care<br>Intelligence Hub</div>
            <div style="font-size:0.7rem; color:#64748B; font-weight:500; margin-top:2px;">Pfizer Analytics</div>
        </div>
        <div style="height:1px; background:rgba(15,23,42,0.08); margin:0 0 10px;"></div>
        <div style="font-size:0.6rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#64748B; margin-bottom:6px;">Primary Care Workspace</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation buttons (Streamlit native - these actually work!)
    if st.button("📊 Deep Dive Dashboards", key="nav_deepdive", use_container_width=True):
        st.session_state["nav_state"] = "deepdive"
        st.rerun()

    if st.button("🤖 CoWork Agents", key="nav_cowork", use_container_width=True):
        st.session_state["nav_state"] = "home"
        st.rerun()

    st.markdown("""
    <div style="margin-top:auto; padding-top:16px; border-top:1px solid rgba(15,23,42,0.06); font-size:11px; color:#64748B;">
        <strong>Primary Care Analytics</strong><br>
        Team_ZS_PC_Analytics@zs.com
    </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT (right column) ---
with main_col:
    nav = st.session_state["nav_state"]

    # ===== SUMMARY SECTION (always visible on home/deepdive) =====
    if nav in ("home", "deepdive"):
        # Build brand sparkline cards
        def build_brand_card_data(df_input):
            cards = []
            for brand in BRANDS:
                bdf = df_input[df_input['BRAND'] == brand].sort_values('YR_QTR_TXT')
                if bdf.empty:
                    continue
                values = bdf['VALUE'].tolist()
                quarters = bdf['YR_QTR_TXT'].tolist()
                latest = values[-1]
                delta = latest - values[-2] if len(values) >= 2 else 0.0
                v_min, v_max = min(values), max(values)
                v_range = v_max - v_min if v_max != v_min else 1
                n = len(values)
                points = []
                for i, v in enumerate(values):
                    x = round((i / (n - 1)) * 120, 1) if n > 1 else 60
                    y = round(24 - ((v - v_min) / v_range) * 22, 1)
                    points.append(f"{x},{y}")
                polyline = " ".join(points)
                cards.append({'brand': brand, 'value': f"{latest:.1f}%", 'delta': f"{delta:+.1f}",
                              'delta_class': 'up' if delta >= 0 else 'down', 'color': BRAND_COLORS[brand],
                              'polyline': polyline, 'first_qtr': quarters[0], 'latest_qtr': quarters[-1]})
            return cards

        cards = build_brand_card_data(df)
        cards_html = ""
        for c in cards:
            cards_html += f'''<div style="background:rgba(255,255,255,0.55);backdrop-filter:blur(12px);border:1px solid rgba(15,23,42,0.06);border-radius:12px;padding:10px 14px;min-width:0;">
                <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;">
                    <span style="font-family:'Manrope',sans-serif;font-weight:700;font-size:12px;color:#0A1A3D;">{c['brand'].title()}</span>
                    <span style="font-size:13px;font-weight:700;color:#0A1A3D;">{c['value']}<span style="font-size:10px;margin-left:4px;color:{'#10B981' if c['delta_class']=='up' else '#EF4444'};font-weight:600;">{c['delta']}</span></span>
                </div>
                <svg viewBox="0 0 120 26" style="width:100%;height:22px;" preserveAspectRatio="none"><polyline points="{c['polyline']}" fill="none" stroke="{c['color']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                <div style="font-size:10px;color:#64748B;margin-top:3px;"><span style="background:#EEF3FB;padding:1px 5px;border-radius:4px;font-weight:600;font-size:9px;">NPA</span> {c['first_qtr']} → {c['latest_qtr']}</div>
            </div>'''

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.55);backdrop-filter:saturate(180%) blur(14px);border:1px solid rgba(15,23,42,0.06);border-radius:16px;padding:16px 20px;margin-bottom:12px;box-shadow:0 2px 8px rgba(15,23,42,0.04);">
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;">
                <span style="font-family:'Manrope',sans-serif;font-weight:700;font-size:14px;color:#0A1A3D;">Primary Care Brand Performance Summary</span>
                <span style="font-size:11px;color:#64748B;">QoQ TRx Market Share</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:10px;">{cards_html}</div>
            <div style="font-size:11px;color:#64748B;border-top:1px solid rgba(15,23,42,0.06);padding-top:8px;">
                <strong>NPA:</strong> Till {max_date_raw} &nbsp;|&nbsp; <strong>DDD:</strong> Till {max_date_raw} &nbsp;|&nbsp; <strong>LAAD:</strong> Till {max_date_raw} &nbsp;|&nbsp; <strong style="color:#1C4FC0;">Refreshed:</strong> {refresh_ts}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ===== HOME VIEW: Mission Statement =====
    if nav == "home":
        st.markdown("""
        <div style="text-align:center; padding:40px 20px;">
            <div style="width:80px;height:1px;background:linear-gradient(90deg,transparent,rgba(28,79,192,0.3),transparent);margin:0 auto 16px;"></div>
            <p style="font-family:'Manrope',sans-serif;font-size:18px;font-weight:600;color:#0A1A3D;line-height:1.55;max-width:520px;margin:0 auto 10px;">Your single source of truth for Primary Care brand performance analytics across NPA, DDD, and LAAD data sources.</p>
            <p style="font-size:13px;color:#64748B;max-width:480px;margin:0 auto;">Use <strong style="color:#163990;">Deep Dive Dashboards</strong> in the sidebar for detailed QoQ analysis, competitive trends, and exportable reports.</p>
            <div style="width:80px;height:1px;background:linear-gradient(90deg,transparent,rgba(28,79,192,0.3),transparent);margin:16px auto 0;"></div>
        </div>
        """, unsafe_allow_html=True)

    # ===== DEEP DIVE VIEW: Brand Selection Grid =====
    elif nav == "deepdive":
        st.markdown("""
        <div style="text-align:center;padding:10px 0 6px;">
            <div style="width:80px;height:1px;background:linear-gradient(90deg,transparent,rgba(28,79,192,0.3),transparent);margin:0 auto 10px;"></div>
            <div style="font-family:'Manrope',sans-serif;font-weight:700;font-size:15px;color:#0A1A3D;">Deep Dive Dashboards</div>
            <div style="font-size:12px;color:#64748B;margin-top:4px;">Select a brand to explore detailed QoQ analysis</div>
        </div>
        """, unsafe_allow_html=True)

        # Brand tile buttons (Streamlit native - these WORK!)
        st.markdown("""<style>
        .brand-grid .stButton > button {
            background: rgba(255,255,255,0.72) !important; backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(15,23,42,0.06) !important; border-radius: 14px !important;
            padding: 24px 16px !important; font-size: 15px !important; font-weight: 700 !important;
            color: #0A1A3D !important; font-family: 'Manrope', sans-serif !important;
            min-height: 80px !important; box-shadow: 0 2px 6px rgba(15,23,42,0.03) !important;
        }
        .brand-grid .stButton > button:hover {
            transform: translateY(-3px) !important; box-shadow: 0 8px 20px rgba(15,23,42,0.09) !important;
            border-color: rgba(28,79,192,0.3) !important; background: rgba(255,255,255,0.9) !important;
        }
        </style>""", unsafe_allow_html=True)

        st.markdown('<div class="brand-grid">', unsafe_allow_html=True)
        brand_keys = list(BRAND_CONFIG.keys())
        row1 = brand_keys[:4]
        row2 = brand_keys[4:]

        cols = st.columns(4)
        for i, bk in enumerate(row1):
            with cols[i]:
                if st.button(BRAND_CONFIG[bk]["display_name"], key=f"tile_{bk}", use_container_width=True):
                    st.session_state["nav_state"] = bk
                    st.rerun()

        cols2 = st.columns(4)
        for i, bk in enumerate(row2):
            with cols2[i]:
                if st.button(BRAND_CONFIG[bk]["display_name"], key=f"tile_{bk}", use_container_width=True):
                    st.session_state["nav_state"] = bk
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== BRAND PAGE VIEW =====
    elif nav in BRAND_CONFIG:
        from brand_pages import render_brand_page
        render_brand_page(nav, BRAND_CONFIG)
