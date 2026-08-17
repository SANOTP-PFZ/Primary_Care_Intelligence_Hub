"""
Primary Care OE Maximization Intelligence Hub - Landing Page
"""
import streamlit as st
import dataiku
import pandas as pd

st.set_page_config(
    page_title="Primary Care OE Maximization Intelligence Hub",
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
    ("Nurtec", "nurtec", ["NPA"]),
    ("Eliquis", "eliquis", ["NPA"]),
    ("Prevnar", "prevnar", ["NPA", "DDD"]),
    ("Comirnaty", "comirnaty", ["NPA", "DDD"]),
    ("Abrysvo", "abrysvo", ["NPA", "DDD"]),
    ("Paxlovid", "paxlovid", ["NPA"]),
    ("Zavzpret", "zavzpret", ["NPA"]),
    ("Beyfortus", "beyfortus", ["LAAD"]),
]

# =====================================================
# ROUTING — query param based
# =====================================================
brand_param = st.query_params.get("brand", None)
agents_param = st.query_params.get("agents", None)

if brand_param and brand_param in BRAND_CONFIG:
    # === RENDER BRAND PAGE ===
    from brand_pages import render_brand_page
    render_brand_page(brand_param, BRAND_CONFIG)
elif agents_param in ("ta", "tad"):
    # === RENDER AGENTS PAGE in new tab ===
    st.markdown("""
    <style>
    [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
    [data-testid="stSidebar"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapseButton"],
    #MainMenu,footer,.stApp>header{display:none!important}
    .block-container{padding:0!important;max-width:100%!important}
    [data-testid="stAppViewBlockContainer"]{padding:0!important}
    [data-testid="stMainBlockContainer"]{padding:0!important}
    [data-testid="stVerticalBlock"]{gap:0!important}
    </style>
    """, unsafe_allow_html=True)

    if agents_param == "ta":
        agents_page_title = "Therapy Area Agents"
        agents_page_desc = "Ask technical and business questions across all available data sources for your therapy area."
        agents_page_cards = """
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_PCV_VACCINE_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Pneumococcal (PCV)</div><div class="ta-card-desc">Conversational querying across all Pneumococcal data sources.</div></a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_RSV_VACCINE_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Respiratory Syncytial Virus (RSV)</div><div class="ta-card-desc">Conversational querying across all RSV data sources.</div></a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_FLU_VACCINE_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Flu</div><div class="ta-card-desc">Conversational querying across all Flu data sources.</div></a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OAC_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Oral Anticoagulant (OAC)</div><div class="ta-card-desc">Conversational querying across all OAC data sources.</div></a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_COVID_VACCINE_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">COVID</div><div class="ta-card-desc">Conversational querying across all COVID data sources.</div></a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_MIGRAINE_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Migraine (OCGRP)</div><div class="ta-card-desc">Conversational querying across all Migraine data sources.</div></a>
"""
    else:
        agents_page_title = "Therapy Area + Data Source Agents"
        agents_page_desc = "Query specific data sources scoped to a therapy area."
        agents_page_cards = """
                <a class="ta-agent-card" data-source="cdc" data-market="vaccines" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_CDC_PROVIDER_DOSES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">CDC Provider</div><div class="ta-card-desc">CDC provider-level administration data for vaccines.</div><div class="ta-card-chip">CDC</div></a>
                <a class="ta-agent-card" data-source="cdc" data-market="vaccines" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_CDC_BULK_SHIPMENTS" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">CDC Bulk</div><div class="ta-card-desc">CDC bulk dose distribution data for vaccines.</div><div class="ta-card-chip">CDC</div></a>
                <a class="ta-agent-card" data-source="ddd" data-market="vaccines" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_DDD_VACCINES_WEEKLY" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">DDD Vaccines</div><div class="ta-card-desc">DDD weekly demand and shipment insights for vaccines.</div><div class="ta-card-chip">DDD</div></a>
                <a class="ta-agent-card" data-source="ddd" data-market="oac" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=DDD_SALES_WEEKLY" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">DDD IM</div><div class="ta-card-desc">DDD weekly demand and shipment for Internal Medicine.</div><div class="ta-card-chip">DDD</div></a>
                <a class="ta-agent-card" data-source="867" data-market="vaccines" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_867_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">867 Vaccines</div><div class="ta-card-desc">867 EDI channel distribution data for vaccines.</div><div class="ta-card-chip">867</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="covid" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=ELAAD_COVID_MARKET_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD COVID</div><div class="ta-card-desc">eLAAD claims-based tracking for COVID vaccines.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="rsv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_ELAAD_RSV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD RSV</div><div class="ta-card-desc">eLAAD claims-based insights for RSV vaccines.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="flu" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_ELAAD_FLU_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD Flu</div><div class="ta-card-desc">eLAAD claims-based insights for Flu vaccines.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="pcv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_ELAAD_PCV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD PCV</div><div class="ta-card-desc">eLAAD claims-based insights for PCV.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="oac" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_ELAAD_OAC" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD OAC</div><div class="ta-card-desc">eLAAD claims-based tracking for OAC.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="covid" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_COVID_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum COVID</div><div class="ta-card-desc">Optum claims-based analytics for COVID vaccines.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="rsv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_RSV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum RSV</div><div class="ta-card-desc">Optum claims-based analytics for RSV vaccines.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="flu" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_FLU_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum Flu</div><div class="ta-card-desc">Optum claims-based analytics for Flu vaccines.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="pcv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_PCV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum PCV</div><div class="ta-card-desc">Optum claims-based analytics for PCV.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="oac" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_OAC" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum OAC</div><div class="ta-card-desc">Optum claims-based analytics for OAC.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="hv" data-market="covid" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_HV_COVID_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Health Verity COVID</div><div class="ta-card-desc">HealthVerity claims analytics for COVID vaccines.</div><div class="ta-card-chip">HV</div></a>
                <a class="ta-agent-card" data-source="hv" data-market="rsv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_HV_RSV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Health Verity RSV</div><div class="ta-card-desc">HealthVerity claims analytics for RSV vaccines.</div><div class="ta-card-chip">HV</div></a>
                <a class="ta-agent-card" data-source="hv" data-market="flu" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_HV_FLU_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Health Verity Flu</div><div class="ta-card-desc">HealthVerity claims analytics for Flu vaccines.</div><div class="ta-card-chip">HV</div></a>
                <a class="ta-agent-card" data-source="hv" data-market="pcv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_HV_PCV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Health Verity PCV</div><div class="ta-card-desc">HealthVerity claims analytics for PCV.</div><div class="ta-card-chip">HV</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="migraine" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USMIGRAINEIISRPTETL&agent=MIGRAINE_LAAD_W_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Migraine LAAD</div><div class="ta-card-desc">LAAD weekly monitoring for Migraine portfolio.</div><div class="ta-card-chip">LAAD</div></a>
                <a class="ta-agent-card" data-source="npa" data-market="migraine" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=MIGRAINEDEEPDIVEDUPLICATE&agent=MIGRAINE_NPA_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Migraine NPA</div><div class="ta-card-desc">NPA prescription data insights for Migraine.</div><div class="ta-card-chip">NPA</div></a>
                <a class="ta-agent-card" data-source="forsyth" data-market="migraine" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_FORSYTH_MIGRAINE" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Forsyth Migraine</div><div class="ta-card-desc">Forsyth market research for Migraine.</div><div class="ta-card-chip">Forsyth</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="migraine" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USMIGRAINEIISRPTETL&agent=MIGRAINE_ELAAD_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Migraine eLAAD</div><div class="ta-card-desc">Monthly eLAAD aggregation for Migraine.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="npa" data-market="all" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USPRIMARYCAREADHOCANALYTICSPARTC&agent=PC_NPA_TRX_ALL_BRANDS" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">NPA TRx</div><div class="ta-card-desc">NPA TRx performance tracking across all brands.</div><div class="ta-card-chip">NPA</div></a>
                <a class="ta-agent-card" data-source="npa" data-market="all" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USPRIMARYCAREADHOCANALYTICSPARTC&agent=PC_NPA_NBRX_ALL_BRANDS" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">NPA NBRx</div><div class="ta-card-desc">NPA NBRx acquisition trends across all brands.</div><div class="ta-card-chip">NPA</div></a>
                <a class="ta-agent-card" data-source="copay" data-market="all" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_COPAY_REDEMPTION_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">CoPay</div><div class="ta-card-desc">Copay and voucher program claim-level data.</div><div class="ta-card-chip">CoPay</div></a>
"""

    # Build filter bar HTML (only for TAD)
    filter_bar_html = ""
    flowchart_html_escaped = ""
    if agents_param == "tad":
        # Static supply chain flowchart (SVG embedded directly)
        flowchart_html_escaped = """
            <div style="margin-bottom:1.2rem;border:1px solid rgba(15,23,42,0.08);border-radius:14px;padding:1.2rem 1rem 0.8rem;background:rgba(255,255,255,0.7);">
                <div style="font-size:13px;font-weight:700;color:#1f2a44;margin-bottom:4px;">Pharmaceutical Supply Chain</div>
                <div style="font-size:11px;color:#5a6478;margin-bottom:10px;">Medicine moves right along the chain, money flows back left, and rebates close the loop.</div>
                <div style="overflow-x:auto;padding-bottom:6px;">
                    <svg viewBox="0 0 1392 200" style="display:block;width:100%;min-width:940px;height:auto;" role="img">
                        <defs>
                            <linearGradient id="cardShine" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#fbfcff"/></linearGradient>
                            <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#26386b" flood-opacity="0.10"/></filter>
                            <marker id="arrMed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#2f6fd0"/></marker>
                            <marker id="arrMoney" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#3f8f3f"/></marker>
                            <marker id="arrRet" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#d98a2b"/></marker>
                        </defs>
                        <path d="M162,111 L227,111" fill="none" stroke="#2f6fd0" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMed)"/>
                        <path d="M227,129 L162,129" fill="none" stroke="#3f8f3f" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMoney)"/>
                        <path d="M362,111 L427,111" fill="none" stroke="#2f6fd0" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMed)"/>
                        <path d="M427,129 L362,129" fill="none" stroke="#3f8f3f" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMoney)"/>
                        <path d="M562,111 L627,111" fill="none" stroke="#2f6fd0" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMed)"/>
                        <path d="M627,129 L562,129" fill="none" stroke="#3f8f3f" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMoney)"/>
                        <path d="M762,120 L827,120" fill="none" stroke="#3f8f3f" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMoney)"/>
                        <path d="M962,120 L1027,120" fill="none" stroke="#3f8f3f" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMoney)"/>
                        <path d="M1162,120 L1227,120" fill="none" stroke="#3f8f3f" stroke-width="2" stroke-opacity=".42" marker-end="url(#arrMoney)"/>
                        <path d="M430,84 C 414,58 378,58 363,84" fill="none" stroke="#d98a2b" stroke-width="2" stroke-opacity=".65" stroke-dasharray="5 4" marker-end="url(#arrRet)"/>
                        <g fill="#4a5468" font-size="11" text-anchor="middle">
                            <text x="196" y="60" fill="#2f6fd0">medicine &#8594;</text>
                            <text x="196" y="74" fill="#3f8f3f">money &#8592;</text>
                            <text x="396" y="50" font-size="10.5" fill="#d98a2b">Returns</text>
                            <text x="796" y="66">Premiums</text>
                            <text x="996" y="66">Payments &amp; rebates</text>
                            <text x="1196" y="66">Rebates</text>
                        </g>
                        <g><rect x="30" y="82" width="132" height="72" rx="12" fill="url(#cardShine)" stroke="#e3e8f2" filter="url(#soft)"/><text x="42" y="100" font-size="9.5" font-weight="700" letter-spacing=".08em" fill="#8b93a6">01</text><text x="96" y="119" text-anchor="middle" font-size="13.5" font-weight="700">Manufacturer</text><text x="96" y="133" text-anchor="middle" font-size="10" fill="#5a6478">e.g. Pfizer</text></g>
                        <g><rect x="230" y="82" width="132" height="72" rx="12" fill="url(#cardShine)" stroke="#e3e8f2" filter="url(#soft)"/><text x="242" y="100" font-size="9.5" font-weight="700" letter-spacing=".08em" fill="#8b93a6">02</text><text x="296" y="119" text-anchor="middle" font-size="13.5" font-weight="700">Wholesaler</text><text x="296" y="133" text-anchor="middle" font-size="10" fill="#5a6478">Distributes</text><rect x="234" y="164" width="124" height="18" rx="9" fill="#eef0fc" stroke="#d7dbf6"/><text x="296" y="176.5" text-anchor="middle" font-size="9.5" fill="#6a5fd0">DDD &#183; 867</text></g>
                        <g><rect x="430" y="82" width="132" height="72" rx="12" fill="url(#cardShine)" stroke="#e3e8f2" filter="url(#soft)"/><text x="442" y="100" font-size="9.5" font-weight="700" letter-spacing=".08em" fill="#8b93a6">03</text><text x="496" y="119" text-anchor="middle" font-size="13.5" font-weight="700">Pharmacy</text><text x="496" y="133" text-anchor="middle" font-size="10" fill="#5a6478">Dispenses</text><rect x="408" y="164" width="176" height="18" rx="9" fill="#eef0fc" stroke="#d7dbf6"/><text x="496" y="176.5" text-anchor="middle" font-size="9" fill="#6a5fd0">ELAAD &#183; Optum &#183; Health Verity</text></g>
                        <g><rect x="630" y="82" width="132" height="72" rx="12" fill="url(#cardShine)" stroke="#e3e8f2" filter="url(#soft)"/><text x="642" y="100" font-size="9.5" font-weight="700" letter-spacing=".08em" fill="#8b93a6">04</text><text x="696" y="119" text-anchor="middle" font-size="13.5" font-weight="700">Patient</text><text x="696" y="133" text-anchor="middle" font-size="10" fill="#5a6478">Fills prescription</text><rect x="654" y="164" width="84" height="18" rx="9" fill="#eef0fc" stroke="#d7dbf6"/><text x="696" y="176.5" text-anchor="middle" font-size="9.5" fill="#6a5fd0">CDC</text></g>
                        <g><rect x="830" y="82" width="132" height="72" rx="12" fill="url(#cardShine)" stroke="#e3e8f2" filter="url(#soft)"/><text x="842" y="100" font-size="9.5" font-weight="700" letter-spacing=".08em" fill="#8b93a6">05</text><text x="896" y="119" text-anchor="middle" font-size="13.5" font-weight="700">Health plan</text><text x="896" y="133" text-anchor="middle" font-size="10" fill="#5a6478">Insurer</text></g>
                        <g><rect x="1030" y="82" width="132" height="72" rx="12" fill="url(#cardShine)" stroke="#e3e8f2" filter="url(#soft)"/><text x="1042" y="100" font-size="9.5" font-weight="700" letter-spacing=".08em" fill="#8b93a6">06</text><text x="1096" y="119" text-anchor="middle" font-size="13.5" font-weight="700">PBM</text><text x="1096" y="133" text-anchor="middle" font-size="10" fill="#5a6478">Manages benefits</text><rect x="1044" y="164" width="104" height="18" rx="9" fill="#f1f2f6" stroke="#d6dae4" stroke-dasharray="4 3"/><text x="1096" y="176.5" text-anchor="middle" font-size="9" fill="#98a0b3">Network contract</text></g>
                        <g><rect x="1230" y="82" width="132" height="72" rx="12" fill="#f4f6fb" stroke="#cfd6e6" stroke-dasharray="5 4"/><text x="1296" y="119" text-anchor="middle" font-size="12.5" font-weight="700" fill="#98a0b3">Manufacturer</text><text x="1296" y="134" text-anchor="middle" font-size="9" fill="#98a0b3">loop closes &#8635;</text></g>
                    </svg>
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;margin:8px 2px 0;font-size:11.5px;color:#5a6478;">
                    <span style="display:flex;align-items:center;gap:8px;"><span style="width:26px;border-top:3px solid #2f6fd0;border-radius:2px;"></span>Flow of medicine</span>
                    <span style="display:flex;align-items:center;gap:8px;"><span style="width:26px;border-top:3px solid #3f8f3f;border-radius:2px;"></span>Flow of money</span>
                    <span style="display:flex;align-items:center;gap:8px;"><span style="width:26px;border-top:3px dashed #d98a2b;border-radius:2px;"></span>Returns</span>
                    <span style="display:flex;align-items:center;gap:8px;"><span style="width:30px;height:16px;border-radius:8px;background:#eef0fc;border:1px solid #d7dbf6;display:inline-block;"></span>Data sources</span>
                </div>
            </div>"""

        filter_bar_html = """
            <div class="filter-bar">
                <div class="filter-group">
                    <span class="filter-group-label">Source:</span>
                    <button class="filter-chip active" onclick="filterTAD(this,'source','all')">All</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','cdc')">CDC</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','ddd')">DDD</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','867')">867</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','elaad')">eLAAD</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','optum')">Optum</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','hv')">Health Verity</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','npa')">NPA</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','forsyth')">Forsyth</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','copay')">CoPay</button>
                </div>
                <div class="filter-group">
                    <span class="filter-group-label">Market:</span>
                    <button class="filter-chip active" onclick="filterTAD(this,'market','all')">All</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','covid')">COVID</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','rsv')">RSV</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','flu')">Flu</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','pcv')">PCV</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','oac')">OAC</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','migraine')">Migraine</button>
                </div>
            </div>"""

    agents_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--navy-900:#0A1A3D;--navy-700:#163990;--navy-600:#1C4FC0;--accent:#41B6E6;--bg:#EEF3FB;--surface:#FFFFFF;--text:#0F172A;--text-muted:#64748B;--text-soft:#475569;--hairline:rgba(15,23,42,0.08);--shadow-sm:0 2px 8px rgba(15,23,42,0.05),0 1px 2px rgba(15,23,42,0.04);--shadow-lg:0 18px 40px rgba(15,23,42,0.10),0 6px 12px rgba(15,23,42,0.06);--ease:cubic-bezier(0.4,0,0.2,1);--ease-out:cubic-bezier(0.16,1,0.3,1)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',system-ui,sans-serif;background:radial-gradient(ellipse 80% 60% at 0% 0%,rgba(28,79,192,0.08) 0%,transparent 60%),radial-gradient(ellipse 70% 50% at 100% 0%,rgba(65,182,230,0.07) 0%,transparent 55%),var(--bg);color:var(--text);padding:2rem 3rem;-webkit-font-smoothing:antialiased}}
h1{{font-family:'Manrope',sans-serif;font-weight:800;font-size:1.6rem;color:var(--navy-900);letter-spacing:-0.025em;margin-bottom:0.3rem}}
.subtitle{{font-size:0.84rem;color:var(--text-muted);margin-bottom:1.2rem}}
.warning{{background:rgba(255,200,50,0.08);border:1px solid rgba(200,150,0,0.15);border-radius:10px;padding:0.7rem 1rem;margin-bottom:1.2rem;font-size:0.78rem;color:var(--text-soft);display:flex;align-items:center;gap:0.5rem}}
.agent-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}
.ta-agent-card{{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;background:var(--surface);border:1px solid var(--hairline);border-radius:14px;padding:1.2rem 1rem;min-height:150px;box-shadow:var(--shadow-sm);transition:transform 0.28s var(--ease-out),box-shadow 0.28s var(--ease),border-color 0.18s var(--ease);text-align:center;text-decoration:none;cursor:pointer;overflow:hidden}}
.ta-agent-card::after{{content:'';position:absolute;inset:0;border-radius:inherit;background:linear-gradient(135deg,rgba(255,255,255,0) 55%,rgba(65,182,230,0.05) 80%,rgba(28,79,192,0.07) 100%);opacity:0;transition:opacity 0.28s var(--ease);pointer-events:none}}
.ta-agent-card:hover{{transform:translateY(-3px);box-shadow:var(--shadow-lg);border-color:rgba(28,79,192,0.2)}}
.ta-agent-card:hover::after{{opacity:1}}
.ta-card-icon{{width:36px;height:36px;border-radius:10px;background:rgba(65,182,230,0.10);display:flex;align-items:center;justify-content:center}}
.ta-card-icon svg{{width:18px;height:18px;stroke:var(--accent)}}
.ta-card-title{{font-family:'Manrope',sans-serif;font-size:0.92rem;font-weight:700;color:var(--navy-900);line-height:1.25;margin-top:4px}}
.ta-card-desc{{font-size:0.72rem;color:var(--text-muted);line-height:1.45}}
.ta-card-chip{{font-size:0.62rem;color:var(--text-muted);display:flex;align-items:center;gap:5px;margin-top:auto;padding-top:0.4rem}}
.ta-card-chip::before{{content:'';width:7px;height:7px;border-radius:2px;background:var(--accent);display:inline-block}}
.filter-bar{{display:flex;flex-direction:column;gap:0.6rem;padding:0.7rem 0.9rem;background:rgba(255,255,255,0.6);border:1px solid var(--hairline);border-radius:10px;margin-bottom:1rem}}
.filter-group{{display:flex;align-items:center;gap:0.35rem;flex-wrap:wrap}}
.filter-group-label{{font-size:0.62rem;font-weight:600;color:var(--text-muted);margin-right:0.2rem}}
.filter-chip{{font-size:0.7rem;font-weight:500;padding:0.25rem 0.6rem;border-radius:6px;border:1px solid var(--hairline);background:rgba(255,255,255,0.7);color:var(--text-soft);cursor:pointer;font-family:inherit;transition:all 0.15s var(--ease)}}
.filter-chip:hover{{background:#fff;border-color:rgba(28,79,192,0.25);color:var(--navy-700)}}
.filter-chip.active{{background:linear-gradient(90deg,var(--navy-700),var(--accent));color:#fff;border-color:transparent;box-shadow:0 2px 8px rgba(22,57,144,0.2)}}
</style></head><body>
<h1>{agents_page_title}</h1>
<div class="subtitle">{agents_page_desc}</div>
<div class="warning"><span style="font-size:1rem;">&#9888;</span>Answers from these agents are produced by AI and may be incomplete or inaccurate. For complex or business-critical outputs, please verify with the relevant ZS team to validate the underlying logic and code before making decisions.</div>
{flowchart_html_escaped}
{filter_bar_html}
<div class="agent-grid" id="tad-agent-grid">
{agents_page_cards}
</div>
<script>
var tadSourceFilter='all',tadMarketFilter='all';
function filterTAD(btn,type,value){{
    if(type==='source')tadSourceFilter=value;
    if(type==='market')tadMarketFilter=value;
    btn.parentElement.querySelectorAll('.filter-chip').forEach(function(c){{c.classList.remove('active')}});
    btn.classList.add('active');
    document.querySelectorAll('#tad-agent-grid .ta-agent-card').forEach(function(card){{
        var src=card.getAttribute('data-source'),mkt=card.getAttribute('data-market');
        var showSrc=(tadSourceFilter==='all'||src===tadSourceFilter);
        var showMkt=(tadMarketFilter==='all'||mkt===tadMarketFilter||mkt==='all'||mkt==='vaccines');
        card.style.display=(showSrc&&showMkt)?'':'none';
    }});
}}
</script>
</body></html>"""
    st.components.v1.html(agents_html, height=900, scrolling=True)
else:
    # === RENDER LANDING PAGE as single HTML component ===
    st.markdown("""
    <style>
    [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
    [data-testid="stSidebar"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapseButton"],
    #MainMenu,footer,.stApp>header{display:none!important}
    .block-container{padding:0!important;max-width:100%!important;margin:0!important;height:100%!important}
    [data-testid="stAppViewBlockContainer"]{padding:0!important;margin:0!important}
    [data-testid="stMainBlockContainer"]{padding:0!important;margin:0!important}
    [data-testid="stVerticalBlock"]{gap:0!important;height:100%!important}
    .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{overflow:hidden!important;height:100vh!important}
    </style>
    """, unsafe_allow_html=True)

    # Build hero KPI cards HTML
    hero_kpis_html = ""
    for c in brand_cards:
        delta_class = "up" if c['delta_class'] == 'up' else "down"
        tri = "&#9650;" if delta_class == "up" else "&#9660;"
        hero_kpis_html += f'''<div class="hero-kpi"><div class="kpi-label">{c['brand'].title()} TRx Mkt Share</div><div class="kpi-value">{c['value']}</div><div class="kpi-delta {delta_class}"><span class="tri">{tri}</span>{c['delta']}pp <span class="vs">vs {c['prior_qtr']}</span></div></div>'''

    # Build brand cards HTML for dashboard section
    brand_cards_grid = ""
    for name, key, sources in BRANDS_LIST:
        chips_html = ''.join(f'<span class="source-chip">{s}</span>' for s in sources)
        brand_cards_grid += f'''<div class="card" onclick="window.open(window.parent.location.origin + window.parent.location.pathname + '?brand={key}', '_blank')"><div class="card-top"><span class="icon-chip chip-s1"><svg viewBox="0 0 24 24"><path d="M3 12h4l3-9 4 18 3-9h4" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></span></div><div class="card-title">{name}</div><div class="card-sources">{chips_html}</div></div>'''

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
.sidebar{{position:sticky;top:var(--shell-pad);height:calc(100vh - 2*var(--shell-pad));background:rgba(255,255,255,0.62);backdrop-filter:saturate(180%) blur(22px);-webkit-backdrop-filter:saturate(180%) blur(22px);border:1px solid var(--hairline);border-radius:var(--panel-radius);box-shadow:var(--shadow-panel);display:flex;flex-direction:column;overflow:hidden}}
.sidebar-brand{{padding:1rem 1.2rem 0.8rem;display:flex;flex-direction:column;gap:0.5rem}}
.sidebar-brand img{{height:28px;align-self:flex-start}}
.sidebar-brand .title{{font-family:'Manrope',sans-serif;font-weight:800;font-size:1.22rem;color:var(--navy-900);line-height:1.18;letter-spacing:-0.025em}}
.sidebar-brand .subtitle{{font-size:0.72rem;color:var(--text-muted);font-weight:500}}
.sidebar-divider{{height:1px;background:var(--hairline);margin:0 0.85rem}}
.sidebar-section-label{{font-family:'Manrope',sans-serif;font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:var(--text-muted);padding:0.7rem 1.15rem 0.3rem}}
.nav{{padding:0 0.55rem}}
.nav-item{{position:relative;display:flex;align-items:center;gap:0.7rem;padding:0.45rem 0.7rem;margin:0.05rem 0;border-radius:8px;font-size:0.84rem;font-weight:500;color:var(--text-soft);cursor:pointer;transition:background 0.18s var(--ease),color 0.18s var(--ease);background:transparent;border:none;width:100%;text-align:left;font-family:inherit}}
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
.sidebar-nav-scroll{{flex:1;min-height:0;overflow-y:auto}}
.sidebar-nav-scroll::-webkit-scrollbar{{width:4px}}
.sidebar-nav-scroll::-webkit-scrollbar-thumb{{background:rgba(15,23,42,0.10);border-radius:2px}}
.sidebar-meta{{padding:0.6rem 1.15rem 0.7rem;font-size:0.7rem;color:var(--text-muted);line-height:1.45;border-top:1px solid var(--hairline);background:linear-gradient(180deg,transparent 0%,rgba(28,79,192,0.025) 100%)}}
.sidebar-meta strong{{color:var(--text-soft);font-weight:600}}
.sidebar-meta .meta-row{{margin-bottom:0.2rem}}
.main{{background:rgba(255,255,255,0.55);backdrop-filter:saturate(180%) blur(14px);-webkit-backdrop-filter:saturate(180%) blur(14px);border:1px solid var(--hairline);border-radius:var(--panel-radius);box-shadow:var(--shadow-panel);display:flex;flex-direction:column;overflow:hidden;min-width:0;min-height:0}}
.content{{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:1.4rem;display:flex;flex-direction:column}}
.content::-webkit-scrollbar{{width:6px}}
.content::-webkit-scrollbar-thumb{{background:rgba(15,23,42,0.14);border-radius:3px}}
.section{{display:none;opacity:0;transform:translateY(4px);transition:opacity 0.22s var(--ease),transform 0.22s var(--ease-out)}}
.section.is-active{{display:flex;flex-direction:column;flex:1;min-height:0}}
.section.is-visible{{opacity:1;transform:translateY(0)}}
.section-head{{margin-bottom:1rem}}
.section-head h2{{font-size:1.35rem;font-weight:700;color:var(--navy-900);letter-spacing:-0.02em;margin-bottom:0.2rem}}
.section-head p{{font-size:0.84rem;color:var(--text-muted);max-width:680px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}
.grid-4{{gap:1.4rem}}
.grid-4 .card{{min-height:180px;padding:1.5rem 1.4rem;justify-content:center;align-items:center;text-align:center}}
.grid-4 .card .card-top{{justify-content:center;margin-bottom:1rem}}
.grid-4 .card .card-title{{font-size:1.15rem;margin-bottom:0}}
.grid-4 .card .icon-chip{{width:44px;height:44px;border-radius:12px}}
.grid-4 .card .icon-chip svg{{width:22px;height:22px}}
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
.card-sources{{display:flex;gap:0.35rem;flex-wrap:wrap;margin-top:auto}}
.source-chip{{font-size:0.62rem;font-weight:600;color:var(--navy-700);background:rgba(28,79,192,0.08);padding:0.15rem 0.45rem;border-radius:4px;letter-spacing:0.03em}}
.agent-categories{{display:grid;grid-template-columns:repeat(2,1fr);gap:1.2rem;margin-top:0.5rem}}
.agent-cat-card{{position:relative;background:var(--surface);border:1px solid var(--hairline);border-radius:14px;padding:1.5rem 1.4rem;cursor:pointer;transition:transform 0.28s var(--ease-out),box-shadow 0.28s var(--ease),border-color 0.18s var(--ease);box-shadow:var(--shadow-sm)}}
.agent-cat-card:hover{{transform:translateY(-3px);box-shadow:var(--shadow-lg);border-color:rgba(28,79,192,0.2)}}
.agent-cat-card.selected{{border-color:var(--navy-600);box-shadow:0 0 0 2px rgba(28,79,192,0.12),var(--shadow-md)}}
.agent-cat-card.selected::before{{content:'';position:absolute;top:-1px;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--navy-600),var(--accent));border-radius:14px 14px 0 0}}
.agent-cat-icon{{width:42px;height:42px;border-radius:11px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#EDE9FE,#DDD6FE);margin-bottom:0.9rem}}
.agent-cat-icon svg{{width:20px;height:20px;stroke:#6D28D9}}
.agent-cat-title{{font-family:'Manrope',sans-serif;font-size:1.05rem;font-weight:700;color:var(--navy-900);margin-bottom:0.35rem}}
.agent-cat-desc{{font-size:0.8rem;color:var(--text-muted);line-height:1.55}}
.agent-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}
.ta-agent-card{{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;background:var(--surface);border:1px solid var(--hairline);border-radius:14px;padding:1.2rem 1rem;min-height:150px;box-shadow:var(--shadow-sm);transition:transform 0.28s var(--ease-out),box-shadow 0.28s var(--ease),border-color 0.18s var(--ease);text-align:center;text-decoration:none;cursor:pointer;overflow:hidden}}
.ta-agent-card::after{{content:'';position:absolute;inset:0;border-radius:inherit;background:linear-gradient(135deg,rgba(255,255,255,0) 55%,rgba(65,182,230,0.05) 80%,rgba(28,79,192,0.07) 100%);opacity:0;transition:opacity 0.28s var(--ease);pointer-events:none}}
.ta-agent-card:hover{{transform:translateY(-3px);box-shadow:var(--shadow-lg);border-color:rgba(28,79,192,0.2)}}
.ta-agent-card:hover::after{{opacity:1}}
.ta-card-icon{{width:36px;height:36px;border-radius:10px;background:rgba(65,182,230,0.10);display:flex;align-items:center;justify-content:center}}
.ta-card-icon svg{{width:18px;height:18px;stroke:var(--accent)}}
.ta-card-title{{font-family:'Manrope',sans-serif;font-size:0.92rem;font-weight:700;color:var(--navy-900);line-height:1.25;margin-top:4px}}
.ta-card-desc{{font-size:0.72rem;color:var(--text-muted);line-height:1.45}}
.ta-card-chip{{font-size:0.62rem;color:var(--text-muted);display:flex;align-items:center;gap:5px;margin-top:auto;padding-top:0.4rem}}
.ta-card-chip::before{{content:'';width:7px;height:7px;border-radius:2px;background:var(--accent);display:inline-block}}
.tad-group-label{{font-family:'Manrope',sans-serif;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--text-muted);padding:1.2rem 0 0.5rem;border-bottom:1px solid var(--hairline);margin-bottom:0.8rem}}
.back-to-cats{{display:inline-flex;align-items:center;gap:0.3rem;padding:0.4rem 0.8rem;border-radius:8px;background:rgba(255,255,255,0.7);border:1px solid var(--hairline);color:var(--text-soft);font-size:0.75rem;font-weight:500;cursor:pointer;font-family:inherit;transition:all 0.18s var(--ease);flex-shrink:0}}
.back-to-cats:hover{{background:#fff;color:var(--navy-700);border-color:rgba(28,79,192,0.25)}}
.tab-bar{{display:flex;gap:0.4rem;margin-bottom:1rem;border-bottom:1px solid var(--hairline);padding-bottom:0.5rem}}
.tab-btn{{font-size:0.78rem;font-weight:500;padding:0.4rem 0.9rem;border-radius:7px;border:1px solid var(--hairline);background:rgba(255,255,255,0.7);color:var(--text-soft);cursor:pointer;font-family:inherit;transition:all 0.15s var(--ease)}}
.tab-btn:hover{{background:#fff;border-color:rgba(28,79,192,0.25);color:var(--navy-700)}}
.tab-btn.active{{background:linear-gradient(90deg,var(--navy-700),var(--accent));color:#fff;border-color:transparent;box-shadow:0 2px 8px rgba(22,57,144,0.2)}}
.ds-table-wrap{{overflow-x:auto;border:1px solid var(--hairline);border-radius:10px;background:var(--surface)}}
.ds-table{{width:100%;border-collapse:collapse;font-size:0.78rem}}
.ds-table th{{text-align:left;padding:0.6rem 0.8rem;background:rgba(28,79,192,0.04);color:var(--navy-700);font-weight:600;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.04em;border-bottom:1px solid var(--hairline)}}
.ds-table td{{padding:0.55rem 0.8rem;border-bottom:1px solid rgba(15,23,42,0.04);color:var(--text-soft);vertical-align:top;line-height:1.5}}
.ds-table tr:last-child td{{border-bottom:none}}
.ds-table tr:hover td{{background:rgba(28,79,192,0.02)}}
.ds-collapse{{border:1px solid var(--hairline);border-radius:10px;margin-bottom:0.8rem;background:var(--surface);overflow:hidden}}
.ds-collapse summary{{padding:0.75rem 1rem;font-family:'Manrope',sans-serif;font-weight:600;font-size:0.85rem;color:var(--navy-700);cursor:pointer;list-style:none;display:flex;align-items:center;gap:0.5rem;transition:background 0.15s var(--ease)}}
.ds-collapse summary:hover{{background:rgba(28,79,192,0.03)}}
.ds-collapse summary::before{{content:'';display:none}}
.ds-collapse[open] summary::before{{transform:rotate(90deg)}}
.ds-collapse summary::-webkit-details-marker{{display:none}}
.ds-collapse .ds-table-wrap{{border:none;border-radius:0;border-top:1px solid var(--hairline)}}
.ds-card{{border:1px solid var(--hairline);border-radius:8px;margin-bottom:0.6rem;background:rgba(255,255,255,0.8);transition:box-shadow 0.18s var(--ease),border-color 0.18s var(--ease)}}
.ds-card:hover{{box-shadow:var(--shadow-sm);border-color:rgba(28,79,192,0.15)}}
.ds-card summary{{padding:0.6rem 0.9rem;font-family:'Manrope',sans-serif;font-weight:600;font-size:0.82rem;color:var(--navy-900);cursor:pointer;list-style:none;display:flex;align-items:center;gap:0.4rem}}
.ds-card summary::before{{content:'';display:none}}
.ds-card[open] summary::before{{transform:rotate(90deg)}}
.ds-card summary::-webkit-details-marker{{display:none}}
.ds-card-body{{padding:0.7rem 0.9rem;border-top:1px solid var(--hairline);font-size:0.78rem;color:var(--text-soft);line-height:1.6}}
.ds-field{{margin-bottom:0.45rem}}
.ds-label{{font-weight:600;color:var(--navy-700);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.03em;margin-right:0.3rem}}
.ds-section{{margin-bottom:0.7rem}}
.ds-section:last-child{{margin-bottom:0}}
.ds-section-title{{display:block;font-weight:700;color:var(--navy-700);font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.25rem}}
.ds-code{{display:block;font-family:'JetBrains Mono','Fira Code',monospace;font-size:0.72rem;background:rgba(15,23,42,0.04);border:1px solid var(--hairline);border-radius:5px;padding:0.35rem 0.6rem;color:var(--navy-900);word-break:break-all;margin-top:0.15rem}}
.ds-list{{margin:0.2rem 0 0 1.1rem;padding:0;font-size:0.78rem;line-height:1.7}}
.ds-list li{{margin-bottom:0.15rem;color:var(--text-soft)}}
.ds-collapse-btn{{display:none;margin-top:0.6rem;padding:0.3rem 0.7rem;font-size:0.7rem;font-weight:600;color:var(--navy-700);background:rgba(28,79,192,0.06);border:1px solid rgba(28,79,192,0.15);border-radius:5px;cursor:pointer;font-family:inherit;transition:all 0.15s var(--ease)}}
.ds-collapse-btn:hover{{background:rgba(28,79,192,0.12);border-color:rgba(28,79,192,0.25)}}
.ds-card[open] .ds-collapse-btn{{display:inline-block}}
.filter-bar{{display:flex;flex-direction:column;gap:0.6rem;padding:0.7rem 0.9rem;background:rgba(255,255,255,0.6);border:1px solid var(--hairline);border-radius:10px;margin-bottom:1rem}}
.filter-label{{font-size:0.7rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.08em}}
.filter-group{{display:flex;align-items:center;gap:0.35rem;flex-wrap:wrap}}
.filter-group-label{{font-size:0.62rem;font-weight:600;color:var(--text-muted);margin-right:0.2rem}}
.filter-chip{{font-size:0.7rem;font-weight:500;padding:0.25rem 0.6rem;border-radius:6px;border:1px solid var(--hairline);background:rgba(255,255,255,0.7);color:var(--text-soft);cursor:pointer;font-family:inherit;transition:all 0.15s var(--ease)}}
.filter-chip:hover{{background:#fff;border-color:rgba(28,79,192,0.25);color:var(--navy-700)}}
.filter-chip.active{{background:linear-gradient(90deg,var(--navy-700),var(--accent));color:#fff;border-color:transparent;box-shadow:0 2px 8px rgba(22,57,144,0.2)}}
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
            <div class="title">Primary Care OE<br>Maximization<br>Intelligence Hub</div>
            <div class="subtitle">Pfizer Analytics</div>
        </div>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-nav-scroll">
    <div class="sidebar-section-label">Primary Care Workspace</div>
    <nav class="nav" id="sidebarNav">
        <button class="nav-item" data-target="dashboards">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg></span>
            <span class="nav-label">Deep-Dive Dashboards</span>
            <span class="nav-count">8</span>
        </button>
        <button class="nav-item" data-target="agents">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="10" rx="2"/><path d="M9 16v3M15 16v3M9 6V3M15 6V3M3 11h3M18 11h3"/></svg></span>
            <span class="nav-label">CoWork Agents</span>
            <span class="nav-count">32</span>
        </button>
        <button class="nav-item" data-target="tools">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></span>
            <span class="nav-label">Analytical Tools</span>
        </button>
    </nav>
    <div class="sidebar-divider" style="margin-top:0.6rem;"></div>
    <div class="sidebar-section-label">Knowledge Center</div>
    <nav class="nav">
        <button class="nav-item" data-target="datadict">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 016.5 17H20" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></span>
            <span class="nav-label">Data Dictionary</span>
        </button>
        <button class="nav-item" data-target="brandinfo">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 16v-4M12 8h.01" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></span>
            <span class="nav-label">Data Source Guide</span>
        </button>
        <button class="nav-item" data-target="links">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></span>
            <span class="nav-label">Relevant Links</span>
        </button>
    </nav>
    </div>
    <div class="sidebar-meta">
        <div class="meta-row"><strong>Primary Care Analytics</strong></div>
        <div class="meta-row">Last refreshed on {max_date_raw}</div>
    </div>
</aside>
<div class="main">
<main class="content">
    <div class="hero">
        <div class="hero-header">
            <div>
                <h1 class="hero-title">Primary Care Performance Summary</h1>
                <div class="hero-subtitle"><span>QoQ TRx Market Share</span><span class="dot"></span><span>{latest_qtr}</span></div>
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

    <!-- HOME SECTION (default) -->
    <section class="section is-active is-visible" id="home">
        <div style="position:relative;background:radial-gradient(ellipse 90% 80% at 20% 20%,rgba(28,79,192,0.06) 0%,transparent 50%),radial-gradient(ellipse 60% 70% at 80% 80%,rgba(65,182,230,0.05) 0%,transparent 50%),linear-gradient(135deg,rgba(255,255,255,0.9) 0%,rgba(248,250,253,0.95) 100%);border-radius:16px;padding:2.5rem 2rem;border:1px solid rgba(15,23,42,0.05);box-shadow:0 2px 8px rgba(15,23,42,0.05),0 1px 2px rgba(15,23,42,0.04);overflow:hidden;text-align:center;flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;">
            <div style="position:absolute;top:-1px;left:0;right:0;height:3px;background:linear-gradient(90deg,#1C4FC0,#41B6E6,#3B6FD9);border-radius:16px 16px 0 0;opacity:0.7;"></div>
            <div style="display:inline-flex;align-items:center;justify-content:center;width:56px;height:56px;border-radius:14px;background:rgba(28,79,192,0.06);margin-bottom:1.2rem;">
                <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#1C4FC0" stroke-width="1.8"><path d="M3 12h4l3-9 4 18 3-9h4"/></svg>
            </div>
            <div style="font-family:'Manrope',sans-serif;font-weight:800;font-size:1.65rem;color:var(--navy-900);letter-spacing:-0.025em;margin-bottom:0.8rem;line-height:1.2;">Welcome to the Primary Care OE<br>Maximization Intelligence Hub</div>
            <div style="font-size:0.92rem;color:var(--text-muted);line-height:1.85;margin-bottom:1.5rem;max-width:640px;margin-left:auto;margin-right:auto;">
                Empowering Pfizer's Primary Care business with real-time market intelligence, competitive analytics, and actionable insights across our key therapeutic brands. This platform consolidates NPA, DDD, and LAAD data sources into unified quarterly performance views — enabling faster decisions and deeper market understanding.
            </div>
            <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
                <div style="background:rgba(255,255,255,0.75);backdrop-filter:blur(8px);border:1px solid rgba(15,23,42,0.05);border-radius:12px;padding:1rem 1.4rem;text-align:center;min-width:160px;">
                    <div style="font-family:'Manrope',sans-serif;font-size:1.4rem;font-weight:700;color:var(--navy-900);">8</div>
                    <div style="font-size:0.72rem;color:var(--text-muted);font-weight:500;margin-top:0.2rem;">Brand Dashboards</div>
                </div>
                <div style="background:rgba(255,255,255,0.75);backdrop-filter:blur(8px);border:1px solid rgba(15,23,42,0.05);border-radius:12px;padding:1rem 1.4rem;text-align:center;min-width:160px;">
                    <div style="font-family:'Manrope',sans-serif;font-size:1.4rem;font-weight:700;color:var(--navy-900);">32</div>
                    <div style="font-size:0.72rem;color:var(--text-muted);font-weight:500;margin-top:0.2rem;">AI Agents</div>
                </div>
                <div style="background:rgba(255,255,255,0.75);backdrop-filter:blur(8px);border:1px solid rgba(15,23,42,0.05);border-radius:12px;padding:1rem 1.4rem;text-align:center;min-width:160px;">
                    <div style="font-family:'Manrope',sans-serif;font-size:1.4rem;font-weight:700;color:var(--navy-900);">5</div>
                    <div style="font-size:0.72rem;color:var(--text-muted);font-weight:500;margin-top:0.2rem;">Data Sources</div>
                </div>
            </div>
            <div style="margin-top:1.5rem;font-size:0.78rem;color:var(--text-muted);">
                Select <strong style="color:var(--navy-600);">Deep-Dive Dashboards</strong> or <strong style="color:var(--navy-600);">CoWork Agents</strong> from the sidebar to get started.
            </div>
        </div>
    </section>

    <!-- ANALYTICAL TOOLS SECTION -->
    <section class="section" id="tools">
        <div class="section-head"><h2>Analytical Tools</h2><p>Advanced analytical tools and utilities for the Primary Care team.</p></div>
        <div class="grid" style="grid-template-columns:repeat(2,1fr);">
            <div class="card" style="min-height:180px;padding:1.5rem 1.4rem;justify-content:center;align-items:center;text-align:center;cursor:default;opacity:0.85;">
                <div class="card-top" style="justify-content:center;margin-bottom:1rem;"><span class="icon-chip chip-s3" style="width:44px;height:44px;border-radius:12px;"><svg viewBox="0 0 24 24" style="width:22px;height:22px;"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></span></div>
                <div class="card-title" style="font-size:1.05rem;margin-bottom:0.4rem;">Rebate Decision Agent</div>
                <div class="card-desc" style="font-size:0.78rem;color:var(--text-muted);line-height:1.5;">AI-powered rebate scenario modeling and decision support for Primary Care brands.</div>
                <div style="margin-top:0.6rem;display:inline-block;padding:4px 12px;border-radius:6px;background:rgba(28,79,192,0.06);border:1px solid rgba(28,79,192,0.12);"><span style="font-size:11px;font-weight:700;color:var(--navy-600);letter-spacing:0.02em;">Coming Soon</span></div>
            </div>
            <a class="card" href="https://dss-amer-design.pfizer.com:10000/webapps/USPRIMARYCAREADHOCANALYTICSPARTC/a1g5PlB/" target="_blank" rel="noopener" style="min-height:180px;padding:1.5rem 1.4rem;justify-content:center;align-items:center;text-align:center;text-decoration:none;">
                <div class="card-top" style="justify-content:center;margin-bottom:1rem;"><span class="icon-chip chip-s1" style="width:44px;height:44px;border-radius:12px;"><svg viewBox="0 0 24 24" style="width:22px;height:22px;"><path d="M3 3v18h18M7 16l4-4 4 4 5-5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></span></div>
                <div class="card-title" style="font-size:1.05rem;margin-bottom:0.4rem;">Nurtec Waterfall Model</div>
                <div class="card-desc" style="font-size:0.78rem;color:var(--text-muted);line-height:1.5;">Waterfall analysis for Nurtec prescription volume drivers and market share changes.</div>
            </a>
        </div>
    </section>

    <!-- DATA DICTIONARY SECTION -->
    <section class="section" id="datadict">
        <div class="section-head"><h2>Data Dictionary</h2><p>Definitions, metric calculations, and data source documentation.</p></div>
        <div class="grid" style="grid-template-columns:repeat(4,1fr);">
            <a class="card" href="https://pfizer.sharepoint.com/:f:/r/sites/EnterpriseDataSolutions1/Document%20Library/Supportive%20Docs/Real%20World%20Data/RWD%20Assets/FORSYTH%20HEALTH?d=w83554f015e7d4d9a938cf8e9a6b73941&csf=1&web=1&e=7wJ1Jr" target="_blank" rel="noopener" style="min-height:120px;align-items:center;text-align:center;justify-content:center;text-decoration:none;">
                <div class="card-title" style="margin-bottom:0.5rem;">Forsyth Health</div>
                <div style="display:inline-flex;align-items:center;gap:0.3rem;font-size:0.68rem;font-weight:600;color:var(--text-muted);padding:0.2rem 0.5rem;border-radius:5px;background:rgba(15,23,42,0.05);"><span style="color:#107C41;">&#9632;</span>SharePoint</div>
            </a>
            <a class="card" href="https://pfizer.sharepoint.com/:f:/r/sites/EnterpriseDataSolutions1/Document%20Library/Supportive%20Docs/Real%20World%20Data/RWD%20Assets/Optum?d=w90b265f9d75d4154861837bb625bf70a&csf=1&web=1&e=Rbq5fl" target="_blank" rel="noopener" style="min-height:120px;align-items:center;text-align:center;justify-content:center;text-decoration:none;">
                <div class="card-title" style="margin-bottom:0.5rem;">Optum</div>
                <div style="display:inline-flex;align-items:center;gap:0.3rem;font-size:0.68rem;font-weight:600;color:var(--text-muted);padding:0.2rem 0.5rem;border-radius:5px;background:rgba(15,23,42,0.05);"><span style="color:#107C41;">&#9632;</span>SharePoint</div>
            </a>
            <a class="card" href="https://pfizer.sharepoint.com/:f:/r/sites/EnterpriseDataSolutions1/Document%20Library/Supportive%20Docs/Real%20World%20Data/RWD%20Assets/HealthVerity%20(Supportive%20Docs)?d=w3354ff0025714b8592ae1735e84849a4&csf=1&web=1&e=TgXlS0" target="_blank" rel="noopener" style="min-height:120px;align-items:center;text-align:center;justify-content:center;text-decoration:none;">
                <div class="card-title" style="margin-bottom:0.5rem;">Health Verity</div>
                <div style="display:inline-flex;align-items:center;gap:0.3rem;font-size:0.68rem;font-weight:600;color:var(--text-muted);padding:0.2rem 0.5rem;border-radius:5px;background:rgba(15,23,42,0.05);"><span style="color:#107C41;">&#9632;</span>SharePoint</div>
            </a>
            <a class="card" href="https://pfizer.sharepoint.com/sites/PrimaryCareAnalytics2/Shared%20Documents/Forms/AllItems.aspx?d=w1a42c10e30284ebf8fe540238ffe3dd8&csf=1&web=1&e=l3nuL5&TeamsCID=e88163fa%2D055f%2D490c%2Db640%2D9897e1c27616&CID=e64aa16a%2D712b%2D42c9%2D8172%2Debee31c59efd&FolderCTID=0x01200071B2656EA41C1847B975D59494D59567&id=%2Fsites%2FPrimaryCareAnalytics2%2FShared%20Documents%2FGeneral%2FData%20Dictionaries" target="_blank" rel="noopener" style="min-height:120px;align-items:center;text-align:center;justify-content:center;text-decoration:none;">
                <div class="card-title" style="margin-bottom:0.5rem;">eLAAD</div>
                <div style="display:inline-flex;align-items:center;gap:0.3rem;font-size:0.68rem;font-weight:600;color:var(--text-muted);padding:0.2rem 0.5rem;border-radius:5px;background:rgba(15,23,42,0.05);"><span style="color:#107C41;">&#9632;</span>SharePoint</div>
            </a>
        </div>
    </section>

    <!-- DATA SOURCE GUIDE SECTION -->
    <section class="section" id="brandinfo">
        <div class="section-head"><h2>Data Source Guide</h2><p>Dataset reference for Primary Care Vaccines OE — tables, brands covered, and data caveats.</p></div>
        <div style="background:rgba(28,79,192,0.04);border:1px solid rgba(28,79,192,0.12);border-radius:8px;padding:0.6rem 1rem;margin-bottom:1.2rem;font-size:0.78rem;color:var(--text-soft);display:flex;align-items:center;gap:0.5rem;">
            <span style="font-size:1rem;">&#128221;</span>
            Notes from the team&#8217;s hands-on experience with all these data sources.
        </div>

        <details class="ds-collapse">
            <summary>Shipments (DDD / 867 / 852 / 844)</summary>
            <div style="padding:0.8rem;">
                <details class="ds-card">
                    <summary>DDD &mdash; FCT_DDD_WK_VX</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>FCT_DDD_WK_VX</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>PFE Vaccines</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_BA_PROD_DB"."BA_US_CORE_VACCINES"."FCT_DDD_WK_VX"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>All account level information already present</li>
                                <li>Competitor info available</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Retail / Non-Retail ratio</li>
                                <li>Chain level doses for non-retail setting</li>
                                <li>Weekly / monthly shipments</li>
                                <li>MA / OA split for Abrysvo</li>
                                <li>Adult / Peds split for Prevnar</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Can&#8217;t perform retail chain-level analytics &mdash; data captured at ZIP level</li>
                                <li>Kaiser shipments under-represented</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>DDD &mdash; DDD_FCT_SLS_M</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>DDD_FCT_SLS_M</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>PFE Vaccines including orals (Nurtec, Paxlovid, Eliquis)</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DDD_FCT_SLS_M"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>PFZ_CUST_ID here is actually OutletID &mdash; map using DIM_ACCT_IDN_HCOS_DDD to get HCOS_PFZ_CUST_ID</li>
                                <li>Competitor info available</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Weekly / monthly level shipments for brands</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Only non-retail coverage of Nurtec, Paxlovid, and Eliquis</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>867 &mdash; FCT_IND_867</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>FCT_IND_867</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>PFE Vaccines</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_BA_PROD_DB"."BA_US_CORE_VACCINES"."FCT_IND_867"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>All account level information already present</li>
                                <li>No competitor info</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Chain / Account level shipments</li>
                                <li>Retail / Non-Retail ratio</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>867 &mdash; EDI_867_TRD_INSGT_EXTRT_VW</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>EDI_867_TRD_INSGT_EXTRT_VW</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>PFE Vaccines including orals (Nurtec, Paxlovid)</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"MARM_TRDINSIGHTP_DB"."INSIGHT_RPT"."EDI_867_TRD_INSGT_EXTRT_VW"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Map EDI_867_CUST_KEY using DIM_CUST_EXTL_ID &#8594; REL_CUST_LINKGS &#8594; HCOS_DIM_BUS to get account info</li>
                                <li>For retail/non-retail split use BUSS CHANNEL DESC</li>
                                <li>No competitor info</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Chain / Account level shipments</li>
                                <li>Retail / Non-Retail ratio</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>For retail, ~50% doses don&#8217;t get a mapping for PFZ_CUST_ID (blinded data)</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>852 &mdash; EDI_852_TRD_INSGT_FCT</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>EDI_852_TRD_INSGT_FCT</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>PFE Vaccines including orals (Nurtec, Paxlovid)</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."EDI_852_TRD_INSGT_FCT"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>sum("OH_QTY") gives WEEKLY_INVENTORY</li>
                                <li>sum("OMIT_QTY" + "WD_QTY") gives TOTAL_WITHDRAWL_QTY</li>
                                <li>sum("PFE_SHIP_QTY") gives SHIPPED_QUANTITY</li>
                                <li>No competitor info</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Inventory and withdrawal rates over time</li>
                                <li>Stocking analysis</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>844 &mdash; FCT_IND_844 / FCT_CUST_END</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>FCT_IND_844</div>
                            <div>FCT_CUST_END</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>PFE Vaccines</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_BA_PROD_DB"."BA_US_CORE_VACCINES"."FCT_IND_844"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">"COMM_US_BA_PROD_DB"."BA_US_CORE_VACCINES"."FCT_CUST_END"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Filter FCT_CUST_END for SRC_TYP_CD = '844' to get 844 shipments</li>
                                <li>No competitor info</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Weekly / monthly level shipments for brands</li>
                                <li>MA / OA split for Abrysvo</li>
                            </ul>
                        </div>
                    </div>
                </details>
            </div>
        </details>

        <details class="ds-collapse">
            <summary>Admins (ELAAD / LAAD / Optum / HV / Forsyth / NPA / CDS)</summary>
            <div style="padding:0.8rem;">
                <details class="ds-card">
                    <summary>ELAAD</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>ELAAD_FACT_MX</div>
                            <div>ELAAD_FACT_RX</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>All brands</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_DMART_ELAAD"."ELAAD_FACT_RX"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Join ELAAD_DIM_PROVIDER to get PFZ_CUST_ID</li>
                                <li>Join ELAAD_DIM_PLAN to get PFZ_PLAN_ID</li>
                                <li>Filter CLAIM_STATUS_CODE IN ('F','S') for any analysis &mdash; other statuses skew the numbers</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Weekly / monthly administrations</li>
                                <li>Vaccination rates</li>
                                <li>HCP, specialty, and payer-level cuts</li>
                                <li>Fill rates, Rx per patient, Pills per Rx</li>
                                <li>Market share</li>
                                <li>Plan-level analysis</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Diagnosis capture is low &mdash; don&#8217;t rely on this source for Dx-driven analyses</li>
                                <li>To roll up to account level, you&#8217;ll need to layer in HCP affiliations</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Weekly LAAD</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>LAAD_FCT_PX_W</div>
                            <div>LAAD_FCT_RX_W</div>
                            <div>LAAD_FCT_DX_W</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>PCV, Covid, Flu, Eliquis</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."LAAD_FCT_RX_W"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Has RSV info, but Pfizer stopped buying for RSV in 2025 season</li>
                                <li>Similar column structure as ELAAD</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Weekly / monthly administrations</li>
                                <li>Vaccination rates</li>
                                <li>HCP, specialty, and payer-level cuts</li>
                                <li>Fill rates, Rx per patient, Pills per Rx</li>
                                <li>Market share</li>
                                <li>Plan-level analysis</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Low diagnosis capture</li>
                                <li>To roll up to account level, layer in HCP affiliations</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Migraine LAAD</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>LAAD_MIG_FCT_MX_W</div>
                            <div>LAAD_MIG_FCT_RX_W</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>Migraine brands</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."LAAD_MIG_FCT_RX_W"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Best for analysis requiring most recent data</li>
                                <li>Similar column structure as ELAAD</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Weekly / monthly administrations</li>
                                <li>HCP, specialty, and payer-level cuts</li>
                                <li>Fill rates, Rx per patient, Pills per Rx</li>
                                <li>Market share</li>
                                <li>Plan-level analysis</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Low diagnosis capture</li>
                                <li>To roll up to account level, layer in HCP affiliations</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Optum</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>RX</div>
                            <div>MEDICAL_PROC</div>
                            <div>MEDICAL_DIAG</div>
                            <div>CONFINEMENT</div>
                            <div>MEDICAL</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>All brands</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"RWD_PROD"."OPTUMDOD_MTHLY"."RX"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Use MEMBER_ENROLLMENT to get patient info (YOB, gender)</li>
                                <li>Better diagnosis capture than LAAD</li>
                                <li>Better for patient journey assessment</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>UMC &mdash; Risk / No-risk split of patients</li>
                                <li>Vaccination rates</li>
                                <li>Historical analysis (LAAD only has data post 2019)</li>
                                <li>Market share</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Low data coverage &mdash; only one payer (UHG)</li>
                                <li>No HCP info available</li>
                                <li>Cannot do payer-level analysis (only Commercial and Medicare)</li>
                                <li>All claims are paid claims</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Health Verity (HV)</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>PHARMACY_CLAIMS</div>
                            <div>EVENTS</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>All brands</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"RWD_PROD"."HV_RX_PHARMACY"."PHARMACY_CLAIMS"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Only retail admins</li>
                                <li>Events table only has admins for C19 market (CVS and Walgreens)</li>
                                <li>Use LOGICAL_DELETE_REASON IS NULL for PD claims</li>
                                <li>Use CONSOLIDATED_ENROLLMENT for patient YOB/age</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Chain level admins</li>
                                <li>Market share</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Chain-level coverage not accurate (e.g., Albertsons appears highest but CVS/Walgreens are higher per RWD)</li>
                                <li>Payer info largely &#8220;Unknown&#8221;</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Forsyth</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>FH_COM_104_MIGRAINE_RX_PAID</div>
                            <div>FH_COM_104_MIGRAINE_RX_REVERSAL</div>
                            <div>FH_COM_104_MIGRAINE_RX_REJECT</div>
                            <div>FH_COM_104_MIGRAINE_MEDICAL_CLAIMS</div>
                            <div>FH_COM_104_MIGRAINE_PRESCRIBING_ATTEMPT</div>
                            <div>FH_COM_104_MIGRAINE_PHARMACY</div>
                            <div>FH_COM_104_MIGRAINE_PATIENT_DIAGNOSIS</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>Migraine brands</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"RWD_PROD"."FORSYTH_MIGRAINE_ONC"."FH_COM_104_MIGRAINE_RX_PAID"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Better coverage for Diagnosis</li>
                                <li>Prior Authorization &mdash; detailed info of each PA attempt</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Low data coverage &mdash; only one payer (ESI)</li>
                                <li>HCP info not present in Diagnosis table</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>NPA</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>Flatfile (received via email)</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>All brands</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Has weekly TRx and NBRx</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Weekly admins</li>
                                <li>Market share</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Only has retail information</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Rapid NPA</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>Flatfile (received via email)</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>PCV, RSV, Covid</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Has weekly TRx</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Weekly admins</li>
                                <li>Market share</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Only has retail information</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Firstlook</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>Flatfile (received via email)</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>Oral CGRP (Nurtec, Ubrelvy, Qulipta) and Zavzpret</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Already has monthly and quarterly TRx and NBRx rolled up data</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Weekly / monthly / quarterly admins</li>
                                <li>Market share</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Only has retail information</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>CDS</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>MDCR_PARTB_PROD_ORG_IND_MTH</div>
                            <div>MDCR_PARTB_PROD_CHAIN</div>
                            <div>MDCR_PARTD_PROD_CHAIN_ST</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Brands Covered</span>
                            <div>Covid, PCV, and Flu vaccines</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_BA_PROD_DB"."BA_US_CORE_VACCINES"."MDCR_PARTB_PROD_CHAIN"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>EVENT_CNT is claims</li>
                                <li>BENE_CNT is patients</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">What You Can Answer</span>
                            <ul class="ds-list">
                                <li>Account / Chain level admins</li>
                                <li>Referral information</li>
                                <li>Retail / Non-Retail ratio</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Coverage drops at granular levels (accounts with no info get removed)</li>
                                <li>Medicare only (60+ age population)</li>
                            </ul>
                        </div>
                    </div>
                </details>
            </div>
        </details>

        <details class="ds-collapse">
            <summary>Dimension Tables</summary>
            <div style="padding:0.8rem;">
                <details class="ds-card">
                    <summary>Miscellaneous</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>DIM_PROD</div>
                            <div>DIM_TIME</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_PROD"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_TIME"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>DIM_PROD &mdash; Product names using NDC</li>
                                <li>DIM_TIME &mdash; Time-related granularities</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>HCP / Account</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>BAC_DIM_CUST_VX</div>
                            <div>DIM_CUST</div>
                            <div>DIM_CUST_ADDR_BEST_CALL</div>
                            <div>DIM_CUST_EXTL_ID</div>
                            <div>BAC_HCP_PRIM_AFFLN</div>
                            <div>HCOS_DIM_BUS</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_BA_PROD_DB"."BA_US_CORE_VACCINES"."BAC_DIM_CUST_VX"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_CUST"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_CUST_ADDR_BEST_CALL"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_CUST_EXTL_ID"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">"COMM_US_BA_PROD_DB"."BA_US_CORE_VACCINES"."BAC_HCP_PRIM_AFFLN"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."HCOS_DIM_BUS"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>BAC_DIM_CUST_VX &mdash; Processed dataset with all info for an account</li>
                                <li>DIM_CUST &mdash; Use CUST_TYPE_CD to segregate between account and HCP</li>
                                <li>DIM_CUST_ADDR_BEST_CALL &mdash; HCP state and ZIP</li>
                                <li>DIM_CUST_EXTL_ID &mdash; NPI to CUST_ID mapping (used in HV analysis for Pharmacy_NPI)</li>
                                <li>BAC_HCP_PRIM_AFFLN &mdash; Identifies which account a particular HCP is affiliated with</li>
                                <li>HCOS_DIM_BUS &mdash; Cot classification, Cot specialty</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>DDD</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>DIM_ACCT_IDN_HCOS_DDD</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_ACCT_IDN_HCOS_DDD"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Maps DDD Outlet ID to PFZ_CUST_ID</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>ELAAD</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>ELAAD_DIM_PATIENT_DEMOGRAPHIC</div>
                            <div>ELAAD_DIM_PRODUCT</div>
                            <div>ELAAD_DIM_PLAN</div>
                            <div>ELAAD_DIM_PROVIDER</div>
                            <div>ELAAD_DIM_REJECT</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_DMART_ELAAD"."ELAAD_DIM_PROVIDER"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>ELAAD_DIM_PATIENT_DEMOGRAPHIC &mdash; Patient&#8217;s YOB and gender</li>
                                <li>ELAAD_DIM_PRODUCT &mdash; Product names using NDC</li>
                                <li>ELAAD_DIM_PLAN &mdash; Get PFZ_PLAN_ID</li>
                                <li>ELAAD_DIM_PROVIDER &mdash; Get PFZ_CUST_ID</li>
                                <li>ELAAD_DIM_REJECT &mdash; Get rejection reason</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Plan / Payer</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>DIM_CUST_PLAN_HIERY</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_CUST_PLAN_HIERY"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Plan / MCO / Payer information</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Optum</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>MEMBER_ENROLLMENT</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"RWD_PROD"."OPTUMDOD_MTHLY"."MEMBER_ENROLLMENT"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Patient&#8217;s YOB and gender</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Geography</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>DIM_ZIP</div>
                            <div>DIM_ST</div>
                            <div>ZIP2MSA</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_ZIP"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">"COMM_US_PUB_PROD_DB"."BI_US_RNA"."DIM_ST"</code>
                            <code class="ds-code" style="margin-top:0.3rem;">COMM_US_BA_PROD_DB.CDW_US_ASB_GBA_DB.ZIP2MSA</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>DIM_ZIP &mdash; ZIP5, MSA, County</li>
                                <li>DIM_ST &mdash; State Code, State Description</li>
                                <li>ZIP2MSA &mdash; Zip to MSA, DMA, Lat, Long</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Health Verity (HV)</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>CONSOLIDATED_ENROLLMENT</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"RWD_PROD"."HV_RX_PHARMACY"."CONSOLIDATED_ENROLLMENT"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Patient&#8217;s YOB and gender</li>
                            </ul>
                        </div>
                    </div>
                </details>
            </div>
        </details>

        <details class="ds-collapse">
            <summary>Alignment / Calls</summary>
            <div style="padding:0.8rem;">
                <details class="ds-card">
                    <summary>IMAP</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>IMAP_TARGET_LIST</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">"VAW_AMER_DESIGN"."PRIMARYCARECEPDRIVERANALYTICS"."IMAP_TARGET_LIST"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>HSS target list of accounts</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Dart V (HSS Calls)</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">Tables</span>
                            <div>BA_VACC_FCT_CALLS</div>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Reference It</span>
                            <code class="ds-code">COMM_US_PUB_PROD_DB."BI_US_DMART_VACCINES"."BA_VACC_FCT_CALLS"</code>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>HSS calls to HCPs/accounts</li>
                                <li>Calls to HCPs are summed up at account level (also present in fact table)</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Sem 360 (HSS Calls with Priority)</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>HSS calls to HCPs/accounts with priority information</li>
                                <li>Calls to HCPs are summed up at account level (also present in fact table)</li>
                            </ul>
                        </div>
                    </div>
                </details>
                <details class="ds-card">
                    <summary>Valkyrie (VAM Goals/Meetings)</summary>
                    <div class="ds-card-body">
                        <div class="ds-section"><span class="ds-section-title">How to Use It</span>
                            <ul class="ds-list">
                                <li>Goals and meetings for VAM</li>
                            </ul>
                        </div>
                        <div class="ds-section"><span class="ds-section-title">Important Considerations</span>
                            <ul class="ds-list">
                                <li>Meeting agenda information is missing</li>
                            </ul>
                        </div>
                    </div>
                </details>
            </div>
        </details>
    </section>

    <!-- RELEVANT LINKS SECTION -->
    <section class="section" id="links">
        <div class="section-head"><h2>Relevant Links</h2><p>Quick access to frequently used tools, portals, and resources.</p></div>
        <div class="grid" style="grid-template-columns:repeat(2,1fr);">
            <a class="card" href="https://pfizer.sharepoint.com/sites/EnterpriseDataSolutions1/Document%20Library/Forms/AllItems.aspx?id=%2Fsites%2FEnterpriseDataSolutions1%2FDocument%20Library%2FSupportive%20Docs%2FReal%20World%20Data%2FRWD%20Assets&viewid=00000000%2D0000%2D0000%2D0000%2D000000000000" target="_blank" rel="noopener" style="min-height:100px;justify-content:center;text-decoration:none;">
                <div class="card-title" style="margin-bottom:0.4rem;">Real World Data Assets</div>
                <div class="card-desc" style="margin-bottom:0;">SharePoint location with data dictionaries and training materials for all data assets that Pfizer has access to.</div>
            </a>
            <a class="card" href="https://pfizer.sharepoint.com/sites/VacceleratorSite/_layouts/15/AccessDenied.aspx?allowautoredirecttosource=true" target="_blank" rel="noopener" style="min-height:100px;justify-content:center;text-decoration:none;">
                <div class="card-title" style="margin-bottom:0.4rem;">Vaccelerator Home Page</div>
                <div class="card-desc" style="margin-bottom:0;">Understand all things BA_US_CORE_VACCINES — the central hub for vaccines data and analytics.</div>
            </a>
        </div>
    </section>

    <!-- DASHBOARDS SECTION -->
    <section class="section" id="dashboards">
        <div class="section-head">
            <div class="section-head-row"><h2>Deep-Dive Dashboards</h2></div>
            <p>Select a brand to explore detailed QoQ analysis, competitive trends, and exportable reports.</p>
        </div>
        <div class="grid grid-4">
            {brand_cards_grid}
        </div>
    </section>

    <!-- AGENTS SECTION -->
    <section class="section" id="agents">
        <div class="section-head"><h2>CoWork Agents</h2><p>AI-powered analytical agents for conversational data exploration and automated insights.</p></div>
        <div style="background:rgba(255,200,50,0.08);border:1px solid rgba(200,150,0,0.15);border-radius:10px;padding:0.7rem 1rem;margin-bottom:1.2rem;font-size:0.78rem;color:var(--text-soft);display:flex;align-items:center;gap:0.5rem;">
            <span style="font-size:1rem;">&#9888;</span>
            Answers from these agents are produced by AI and may be incomplete or inaccurate. For complex or business-critical outputs, please verify with the relevant ZS team to validate the underlying logic and code before making decisions.
        </div>
        <div class="agent-categories" id="agent-cat-container" style="min-height:260px;">
            <div class="agent-cat-card" id="cat-ta" onclick="showAgentPanel('ta')" style="min-height:240px;display:flex;flex-direction:column;justify-content:center;">
                <div class="agent-cat-icon" style="width:52px;height:52px;border-radius:14px;margin-bottom:1.2rem;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="width:24px;height:24px;"><circle cx="12" cy="12" r="9"/><path d="M12 8v4l2.5 2.5"/></svg></div>
                <div class="agent-cat-title" style="font-size:1.2rem;margin-bottom:0.5rem;">Therapy Area Agents</div>
                <div class="agent-cat-desc" style="font-size:0.86rem;line-height:1.65;">Ask technical and business questions across all available data sources for your therapy area.</div>
                <div style="margin-top:1.2rem;display:flex;align-items:center;gap:0.5rem;">
                    <span style="font-size:0.72rem;font-weight:600;color:var(--navy-700);background:rgba(28,79,192,0.08);padding:0.2rem 0.6rem;border-radius:5px;">6 Agents</span>
                    <span style="font-size:0.72rem;color:var(--text-muted);">PCV &middot; RSV &middot; Flu &middot; OAC &middot; COVID &middot; Migraine</span>
                </div>
            </div>
            <div class="agent-cat-card" id="cat-tad" onclick="showAgentPanel('tad')" style="min-height:240px;display:flex;flex-direction:column;justify-content:center;">
                <div class="agent-cat-icon" style="width:52px;height:52px;border-radius:14px;margin-bottom:1.2rem;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="width:24px;height:24px;"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg></div>
                <div class="agent-cat-title" style="font-size:1.2rem;margin-bottom:0.5rem;">Therapy Area + Data Source Agents</div>
                <div class="agent-cat-desc" style="font-size:0.86rem;line-height:1.65;">Query specific data sources — NPA, DDD, LAAD, CDC, Optum, HealthVerity — scoped to a therapy area.</div>
                <div style="margin-top:1.2rem;display:flex;align-items:center;gap:0.5rem;">
                    <span style="font-size:0.72rem;font-weight:600;color:var(--navy-700);background:rgba(28,79,192,0.08);padding:0.2rem 0.6rem;border-radius:5px;">26 Agents</span>
                    <span style="font-size:0.72rem;color:var(--text-muted);">10 Sources &middot; 6 Markets</span>
                </div>
            </div>
        </div>

        <!-- TA Agents Grid -->
        <div id="agents-ta" style="display:none;padding-top:1.2rem;">
            <button class="back-to-cats" onclick="hideAgentPanels()" style="margin-bottom:0.8rem;">&#8592; Back to Home</button>
            <div style="margin-bottom:1rem;">
                <div class="sub-panel-title" style="font-size:1.3rem;margin-bottom:0.15rem;background:linear-gradient(90deg,var(--navy-900),var(--navy-600));-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Therapy Area Agents</div>
                <div class="sub-panel-desc" style="margin-bottom:0;">Ask technical and business questions across all available data sources for your therapy area.</div>
            </div>
            <div class="agent-grid">
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_PCV_VACCINE_AGENT" target="_blank" rel="noopener">
                    <div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div>
                    <div class="ta-card-title">Pneumococcal (PCV)</div>
                    <div class="ta-card-desc">Conversational querying across all Pneumococcal data sources.</div>
                </a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_RSV_VACCINE_AGENT" target="_blank" rel="noopener">
                    <div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div>
                    <div class="ta-card-title">Respiratory Syncytial Virus (RSV)</div>
                    <div class="ta-card-desc">Conversational querying across all RSV data sources.</div>
                </a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_FLU_VACCINE_AGENT" target="_blank" rel="noopener">
                    <div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div>
                    <div class="ta-card-title">Flu</div>
                    <div class="ta-card-desc">Conversational querying across all Flu data sources.</div>
                </a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OAC_AGENT" target="_blank" rel="noopener">
                    <div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div>
                    <div class="ta-card-title">Oral Anticoagulant (OAC)</div>
                    <div class="ta-card-desc">Conversational querying across all OAC data sources.</div>
                </a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_COVID_VACCINE_AGENT" target="_blank" rel="noopener">
                    <div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div>
                    <div class="ta-card-title">COVID</div>
                    <div class="ta-card-desc">Conversational querying across all COVID data sources.</div>
                </a>
                <a class="ta-agent-card" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_MIGRAINE_AGENT" target="_blank" rel="noopener">
                    <div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div>
                    <div class="ta-card-title">Migraine (OCGRP)</div>
                    <div class="ta-card-desc">Conversational querying across all Migraine data sources.</div>
                </a>
            </div>
        </div>

        <!-- TAD Agents Grid -->
        <div id="agents-tad" style="display:none;padding-top:1.2rem;">
            <button class="back-to-cats" onclick="hideAgentPanels()" style="margin-bottom:0.8rem;">&#8592; Back to Home</button>
            <div style="margin-bottom:1rem;">
                <div class="sub-panel-title" style="font-size:1.3rem;margin-bottom:0.15rem;background:linear-gradient(90deg,var(--navy-900),var(--navy-600));-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Therapy Area + Data Source Agents</div>
                <div class="sub-panel-desc" style="margin-bottom:0;">Query specific data sources scoped to a therapy area.</div>
            </div>
            <div class="filter-bar">
                <div class="filter-group">
                    <span class="filter-group-label">Source:</span>
                    <button class="filter-chip active" onclick="filterTAD(this,'source','all')">All</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','cdc')">CDC</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','ddd')">DDD</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','867')">867</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','elaad')">eLAAD</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','optum')">Optum</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','hv')">Health Verity</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','npa')">NPA</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','forsyth')">Forsyth</button>
                    <button class="filter-chip" onclick="filterTAD(this,'source','copay')">CoPay</button>
                </div>
                <div class="filter-group">
                    <span class="filter-group-label">Market:</span>
                    <button class="filter-chip active" onclick="filterTAD(this,'market','all')">All</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','covid')">COVID</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','rsv')">RSV</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','flu')">Flu</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','pcv')">PCV</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','oac')">OAC</button>
                    <button class="filter-chip" onclick="filterTAD(this,'market','migraine')">Migraine</button>
                </div>
            </div>
            <div class="agent-grid" id="tad-agent-grid">
                <a class="ta-agent-card" data-source="cdc" data-market="vaccines" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_CDC_PROVIDER_DOSES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">CDC Provider</div><div class="ta-card-desc">CDC provider-level administration data for vaccines.</div><div class="ta-card-chip">CDC</div></a>
                <a class="ta-agent-card" data-source="cdc" data-market="vaccines" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_CDC_BULK_SHIPMENTS" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">CDC Bulk</div><div class="ta-card-desc">CDC bulk dose distribution data for vaccines.</div><div class="ta-card-chip">CDC</div></a>
                <a class="ta-agent-card" data-source="ddd" data-market="vaccines" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_DDD_VACCINES_WEEKLY" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">DDD Vaccines</div><div class="ta-card-desc">DDD weekly demand and shipment insights for vaccines.</div><div class="ta-card-chip">DDD</div></a>
                <a class="ta-agent-card" data-source="ddd" data-market="oac" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=DDD_SALES_WEEKLY" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">DDD IM</div><div class="ta-card-desc">DDD weekly demand and shipment for Internal Medicine.</div><div class="ta-card-chip">DDD</div></a>
                <a class="ta-agent-card" data-source="867" data-market="vaccines" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_867_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">867 Vaccines</div><div class="ta-card-desc">867 EDI channel distribution data for vaccines.</div><div class="ta-card-chip">867</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="covid" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=ELAAD_COVID_MARKET_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD COVID</div><div class="ta-card-desc">eLAAD claims-based tracking for COVID vaccines.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="rsv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_ELAAD_RSV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD RSV</div><div class="ta-card-desc">eLAAD claims-based insights for RSV vaccines.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="flu" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_ELAAD_FLU_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD Flu</div><div class="ta-card-desc">eLAAD claims-based insights for Flu vaccines.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="pcv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_ELAAD_PCV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD PCV</div><div class="ta-card-desc">eLAAD claims-based insights for PCV.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="oac" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_ELAAD_OAC" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">eLAAD OAC</div><div class="ta-card-desc">eLAAD claims-based tracking for OAC.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="covid" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_COVID_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum COVID</div><div class="ta-card-desc">Optum claims-based analytics for COVID vaccines.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="rsv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_RSV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum RSV</div><div class="ta-card-desc">Optum claims-based analytics for RSV vaccines.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="flu" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_FLU_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum Flu</div><div class="ta-card-desc">Optum claims-based analytics for Flu vaccines.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="pcv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_PCV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum PCV</div><div class="ta-card-desc">Optum claims-based analytics for PCV.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="optum" data-market="oac" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_OPTUM_OAC" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Optum OAC</div><div class="ta-card-desc">Optum claims-based analytics for OAC.</div><div class="ta-card-chip">Optum</div></a>
                <a class="ta-agent-card" data-source="hv" data-market="covid" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_HV_COVID_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Health Verity COVID</div><div class="ta-card-desc">HealthVerity claims analytics for COVID vaccines.</div><div class="ta-card-chip">HV</div></a>
                <a class="ta-agent-card" data-source="hv" data-market="rsv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_HV_RSV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Health Verity RSV</div><div class="ta-card-desc">HealthVerity claims analytics for RSV vaccines.</div><div class="ta-card-chip">HV</div></a>
                <a class="ta-agent-card" data-source="hv" data-market="flu" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_HV_FLU_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Health Verity Flu</div><div class="ta-card-desc">HealthVerity claims analytics for Flu vaccines.</div><div class="ta-card-chip">HV</div></a>
                <a class="ta-agent-card" data-source="hv" data-market="pcv" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_HV_PCV_VACCINES" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Health Verity PCV</div><div class="ta-card-desc">HealthVerity claims analytics for PCV.</div><div class="ta-card-chip">HV</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="migraine" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USMIGRAINEIISRPTETL&agent=MIGRAINE_LAAD_W_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Migraine LAAD</div><div class="ta-card-desc">LAAD weekly monitoring for Migraine portfolio.</div><div class="ta-card-chip">LAAD</div></a>
                <a class="ta-agent-card" data-source="npa" data-market="migraine" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=MIGRAINEDEEPDIVEDUPLICATE&agent=MIGRAINE_NPA_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Migraine NPA</div><div class="ta-card-desc">NPA prescription data insights for Migraine.</div><div class="ta-card-chip">NPA</div></a>
                <a class="ta-agent-card" data-source="forsyth" data-market="migraine" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_FORSYTH_MIGRAINE" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Forsyth Migraine</div><div class="ta-card-desc">Forsyth market research for Migraine.</div><div class="ta-card-chip">Forsyth</div></a>
                <a class="ta-agent-card" data-source="elaad" data-market="migraine" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USMIGRAINEIISRPTETL&agent=MIGRAINE_ELAAD_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">Migraine eLAAD</div><div class="ta-card-desc">Monthly eLAAD aggregation for Migraine.</div><div class="ta-card-chip">eLAAD</div></a>
                <a class="ta-agent-card" data-source="npa" data-market="all" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USPRIMARYCAREADHOCANALYTICSPARTC&agent=PC_NPA_TRX_ALL_BRANDS" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">NPA TRx</div><div class="ta-card-desc">NPA TRx performance tracking across all brands.</div><div class="ta-card-chip">NPA</div></a>
                <a class="ta-agent-card" data-source="npa" data-market="all" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USPRIMARYCAREADHOCANALYTICSPARTC&agent=PC_NPA_NBRX_ALL_BRANDS" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">NPA NBRx</div><div class="ta-card-desc">NPA NBRx acquisition trends across all brands.</div><div class="ta-card-chip">NPA</div></a>
                <a class="ta-agent-card" data-source="copay" data-market="all" href="https://app.us-east-1.privatelink.snowflakecomputing.com/pfe/amerprod01/#/ai/chat/new?db=VAW_AMER_DESIGN&schema=USIMVACCINESSDL&agent=PC_COPAY_REDEMPTION_AGENT" target="_blank" rel="noopener"><div class="ta-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="6" y="4" width="12" height="7" rx="2"/><path d="M9 11v4M15 11v4M8 18h8M12 15v3"/></svg></div><div class="ta-card-title">CoPay</div><div class="ta-card-desc">Copay and voucher program claim-level data.</div><div class="ta-card-chip">CoPay</div></a>
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


    // Agent panel switching
    window.showAgentPanel = function(panel) {{
        document.getElementById('agents-ta').style.display = (panel === 'ta') ? 'block' : 'none';
        document.getElementById('agents-tad').style.display = (panel === 'tad') ? 'block' : 'none';
        document.getElementById('agent-cat-container').style.display = 'none';
        document.getElementById('cat-ta').classList.toggle('selected', panel === 'ta');
        document.getElementById('cat-tad').classList.toggle('selected', panel === 'tad');
        // Hide hero and divider
        document.querySelector('.hero').style.display = 'none';
        document.querySelector('.workspace-divider').style.display = 'none';
        document.querySelector('.section-head').style.display = 'none';
        document.querySelector('#agents > div:nth-child(2)').style.display = 'none';
    }};
    window.hideAgentPanels = function() {{
        document.getElementById('agents-ta').style.display = 'none';
        document.getElementById('agents-tad').style.display = 'none';
        document.getElementById('agent-cat-container').style.display = 'grid';
        document.getElementById('cat-ta').classList.remove('selected');
        document.getElementById('cat-tad').classList.remove('selected');
        // Restore hero and divider
        document.querySelector('.hero').style.display = '';
        document.querySelector('.workspace-divider').style.display = '';
        document.querySelector('#agents .section-head').style.display = '';
        document.querySelector('#agents > div:nth-child(2)').style.display = '';
    }};

    // TAD filter logic
    var tadSourceFilter = 'all';
    var tadMarketFilter = 'all';
    window.filterTAD = function(btn, type, value) {{
        if (type === 'source') tadSourceFilter = value;
        if (type === 'market') tadMarketFilter = value;
        // Update active chip in the correct group
        var group = btn.parentElement;
        group.querySelectorAll('.filter-chip').forEach(function(c){{ c.classList.remove('active'); }});
        btn.classList.add('active');
        // Filter cards
        var cards = document.querySelectorAll('#tad-agent-grid .ta-agent-card');
        cards.forEach(function(card) {{
            var src = card.getAttribute('data-source');
            var mkt = card.getAttribute('data-market');
            var showSrc = (tadSourceFilter === 'all' || src === tadSourceFilter);
            var showMkt = (tadMarketFilter === 'all' || mkt === tadMarketFilter || mkt === 'all' || mkt === 'vaccines');
            card.style.display = (showSrc && showMkt) ? '' : 'none';
        }});
    }};
    var nav = document.getElementById('sidebarNav');
    var allNavItems = document.querySelectorAll('.nav .nav-item');
    var items = nav.querySelectorAll('.nav-item');
    var sections = {{'home': document.getElementById('home'), 'tools': document.getElementById('tools'), 'datadict': document.getElementById('datadict'), 'brandinfo': document.getElementById('brandinfo'), 'links': document.getElementById('links')}};
    allNavItems.forEach(function(it){{ if(it.dataset.target) sections[it.dataset.target] = document.getElementById(it.dataset.target); }});
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
    allNavItems.forEach(function(item) {{
        item.addEventListener('click', function(e) {{
            e.preventDefault();
            allNavItems.forEach(function(i){{ i.classList.remove('active'); }});
            item.classList.add('active');
            showSection(item.dataset.target);
            // Reset agent panels when navigating away
            if (item.dataset.target !== 'agents') hideAgentPanels();
        }});
    }});
    // DS card collapse buttons
    document.querySelectorAll('.ds-card-body').forEach(function(body) {{
        var btn = document.createElement('button');
        btn.className = 'ds-collapse-btn';
        btn.textContent = '\u2191 Collapse';
        btn.addEventListener('click', function(e) {{
            e.stopPropagation();
            var card = body.closest('details.ds-card');
            if (card) card.removeAttribute('open');
        }});
        body.appendChild(btn);
    }});
}})();
</script>
</body>
</html>"""

    st.components.v1.html(landing_html, height=960, scrolling=True)
