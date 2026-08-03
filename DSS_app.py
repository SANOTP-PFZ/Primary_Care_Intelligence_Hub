"""
Primary Care Monthly Report Dashboard - Dataiku DSS Streamlit Webapp
All data loaded dynamically from Dataiku dataset via pandas.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import dataiku

st.set_page_config(page_title="Primary Care Monthly Report Dashboard", layout="wide", initial_sidebar_state="collapsed")

# =====================================================
# CONFIGURATION
# =====================================================

DATASET_NAME = "SQL_EARNINGS_REPORT_MASTER_DATASET_SF"

BRAND_CONFIG = {
    "nurtec": {"display_name": "Nurtec", "brand_key": "NURTEC", "market": "OCGRP", "market_display": "Oral CGRP", "source": "NPA"},
    "eliquis": {"display_name": "Eliquis", "brand_key": "ELIQUIS", "market": "OAC", "market_display": "Oral Anticoagulant", "source": "NPA"},
    "prevnar": {"display_name": "Prevnar", "brand_key": "PREVNAR", "market": "PCV", "market_display": "PCV", "source": "NPA", "ddd_market": "PCV", "ddd_brand": "PREVNAR"},
    "comirnaty": {"display_name": "Comirnaty", "brand_key": "COMIRNATY", "market": "COVID_VACCINES", "market_display": "COVID Vaccines", "source": "NPA", "ddd_market": "COVID", "ddd_brand": "COMIRNATY"},
    "abrysvo": {"display_name": "Abrysvo", "brand_key": "ABRYSVO", "market": "RSV", "market_display": "RSV", "source": "NPA", "ddd_market": "RSV", "ddd_brand": "ABRYSVO"},
    "paxlovid": {"display_name": "Paxlovid", "brand_key": "PAXLOVID", "market": "COVID_ORAL", "market_display": "COVID Oral Treatment", "source": "NPA"},
    "zavzpret": {"display_name": "Zavzpret", "brand_key": "ZAVZPRET", "market": "ZAVZPRET", "market_display": "Zavzpret", "source": "NPA"},
    "beyfortus": {"display_name": "Beyfortus", "brand_key": "BEYFORTUS", "market": "BEYFORTUS", "market_display": "Beyfortus", "source": "ELAAD"},
}

CHART_COLORS = ["#1C4FC0", "#41B6E6", "#7C3AED", "#0E7490", "#D946EF", "#047857", "#EF4444", "#64748B"]

# =====================================================
# DATA LOADING
# =====================================================

@st.cache_data(ttl=3600)
def load_data():
    dataset = dataiku.Dataset(DATASET_NAME)
    return dataset.get_dataframe()


def get_npa_trx_data(df, market):
    return df[(df["DATASET"] == "NPA_TRX") & (df["MARKET"] == market)].copy()


def get_npa_nbrx_data(df, market):
    return df[(df["DATASET"] == "NPA_NBRX") & (df["MARKET"] == market)].copy()


def pivot_market_share(df_subset, metric_name):
    filtered = df_subset[df_subset["METRICS"] == metric_name]
    if filtered.empty:
        return pd.DataFrame()
    pivoted = filtered.pivot_table(index="YR_QTR_TXT", columns="BRAND", values="VALUE")
    pivoted = pivoted.sort_index()
    if len(pivoted) > 10:
        pivoted = pivoted.iloc[-10:]
    return pivoted

# =====================================================
# CSS STYLES
# =====================================================

COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
:root {
    --bg: #EEF3FB; --surface: #FFFFFF; --text-1: #0F172A; --text-2: #1C4FC0;
    --text-3: #64748B; --border: rgba(15,23,42,0.08); --border-hover: rgba(28,79,192,0.35);
    --navy-700: #163990; --navy-800: #102A5C; --navy-900: #0A1A3D;
    --shadow-sm: 0 2px 8px rgba(15,23,42,0.05), 0 1px 2px rgba(15,23,42,0.04);
    --shadow-md: 0 6px 16px rgba(15,23,42,0.07), 0 2px 4px rgba(15,23,42,0.04);
    --shadow-panel: 0 8px 24px rgba(15,23,42,0.07), 0 2px 6px rgba(15,23,42,0.04);
    --radius: 14px; --radius-lg: 18px;
    --ease: cubic-bezier(0.4,0,0.2,1); --ease-out: cubic-bezier(0.16,1,0.3,1);
}
* { box-sizing: border-box; }
#MainMenu, header, footer, [data-testid="stSidebar"] { display: none !important; visibility: hidden !important; }
.block-container { padding-top: 1rem !important; max-width: 100% !important; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.06) 0%, transparent 60%),
                radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.05) 0%, transparent 55%),
                var(--bg) !important;
}
h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -0.015em; color: var(--navy-900); }
.hub-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 24px; border-radius: var(--radius-lg);
    background: rgba(255,255,255,0.62); backdrop-filter: saturate(180%) blur(22px);
    margin-bottom: 16px; box-shadow: var(--shadow-panel); border: 1px solid var(--border);
}
.hub-title { font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 22px; color: var(--navy-900); letter-spacing: -0.025em; }
</style>
"""

HOME_BUTTON_CSS = """
<style>
.stButton > button {
    background: rgba(255,255,255,0.55) !important; backdrop-filter: saturate(180%) blur(14px) !important;
    border: 1px solid rgba(15,23,42,0.08) !important; border-radius: 18px !important;
    padding: 28px 28px !important; color: #0A1A3D !important; font-size: 18px !important;
    font-weight: 700 !important; font-family: 'Manrope', sans-serif !important;
    cursor: pointer !important; box-shadow: 0 2px 8px rgba(15,23,42,0.05) !important;
    min-height: 100px !important; transition: all 0.28s cubic-bezier(0.16,1,0.3,1) !important;
}
.stButton > button:hover {
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 18px 40px rgba(15,23,42,0.10) !important;
    background: rgba(255,255,255,0.85) !important; border-color: rgba(28,79,192,0.35) !important;
}
.stButton > button > div, .stButton > button > div > p, .stButton > button p, .stButton > button span {
    font-size: 18px !important; font-weight: 700 !important;
}
</style>
"""

# =====================================================
# HELPERS
# =====================================================

def render_ribbon(title):
    st.markdown(COMMON_CSS, unsafe_allow_html=True)
    st.markdown(f'<div class="hub-header"><span class="hub-title">{title}</span></div>', unsafe_allow_html=True)


def render_trend_chart(pivoted_df, title, brands_order=None, is_percentage=True):
    if pivoted_df.empty:
        st.info(f"No data available for: {title}")
        return
    fig = go.Figure()
    brands = brands_order if brands_order else list(pivoted_df.columns)
    for i, brand in enumerate(brands):
        if brand not in pivoted_df.columns:
            continue
        y_vals = pivoted_df[brand].tolist()
        fmt = f"<b>{brand}</b><br>%{{x}}<br>%{{y:.2f}}%<extra></extra>" if is_percentage else f"<b>{brand}</b><br>%{{x}}<br>%{{y:,.0f}}<extra></extra>"
        if i == 0:
            text_vals = [f"{v:.2f}" if pd.notna(v) else "" for v in y_vals] if is_percentage else [f"{v:,.0f}" if pd.notna(v) else "" for v in y_vals]
            fig.add_trace(go.Scatter(x=pivoted_df.index.tolist(), y=y_vals, mode="lines+markers+text", name=brand, text=text_vals, textposition="top center", textfont=dict(size=10, color=CHART_COLORS[0]), line=dict(color=CHART_COLORS[0], width=3), marker=dict(size=7), hovertemplate=fmt))
        else:
            fig.add_trace(go.Scatter(x=pivoted_df.index.tolist(), y=y_vals, mode="lines+markers", name=brand, line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2), marker=dict(size=5), hovertemplate=fmt))
    fig.update_layout(template="plotly_white", height=420, margin=dict(l=60, r=30, t=20, b=50), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(family="Inter, system-ui", size=13, color="#0F172A"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0), hovermode="x unified")
    fig.update_xaxes(showgrid=False, tickfont=dict(size=12, color="#64748B"))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(15,23,42,0.06)", ticksuffix="%" if is_percentage else "", tickfont=dict(size=12, color="#64748B"), separatethousands=True)
    try:
        st.plotly_chart(fig, use_container_width=True, theme=None)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def render_styled_table(df_to_render, title):
    if df_to_render.empty:
        return
    with st.expander(title, expanded=False):
        st.dataframe(df_to_render, use_container_width=True, hide_index=True)


# =====================================================
# BRAND PAGE RENDERER
# =====================================================

def render_brand_page(brand_key_page):
    config = BRAND_CONFIG[brand_key_page]
    brand_name = config["brand_key"]
    market = config["market"]
    display_name = config["display_name"]

    render_ribbon(f"{display_name} \u2014 Quarter on Quarter Report")

    # Back button
    if st.button("\u2190 Back to Home"):
        st.session_state["current_page"] = "home"
        st.rerun()

    df = load_data()

    # --- Get data based on source ---
    if brand_key_page == "beyfortus":
        elaad_data = df[(df["DATASET"] == "ELAAD") & (df["MARKET"] == "BEYFORTUS")]
        claims = pivot_market_share(elaad_data, "CLAIMS")
        patients = pivot_market_share(elaad_data, "PATIENTS")
        if claims.empty and patients.empty:
            st.warning(f"No data available for {display_name}.")
            return
        st.subheader("Claims Trend (LAAD)")
        render_trend_chart(claims, "Claims", [brand_name], is_percentage=False)
        st.subheader("Patients Trend (LAAD)")
        render_trend_chart(patients, "Patients", [brand_name], is_percentage=False)
        if not claims.empty:
            render_styled_table(claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), "Claims (Raw)")
        if not patients.empty:
            render_styled_table(patients.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), "Patients (Raw)")
        return

    trx_data = get_npa_trx_data(df, market)
    nbrx_data = get_npa_nbrx_data(df, market)

    if trx_data.empty and nbrx_data.empty:
        st.warning(f"No NPA data for {display_name} in market '{market}'.")
        return

    # --- Zavzpret special handler ---
    if brand_key_page == "zavzpret":
        trx_claims = pivot_market_share(trx_data, "TRX CLAIMS")
        nbrx_claims = pivot_market_share(nbrx_data, "NBRX CLAIMS")
        st.subheader("TRX Claims Trend (NPA)")
        render_trend_chart(trx_claims, "TRX Claims", [brand_name], is_percentage=False)
        st.subheader("NBRX Claims Trend (NPA)")
        render_trend_chart(nbrx_claims, "NBRX Claims", [brand_name], is_percentage=False)
        if not trx_claims.empty:
            render_styled_table(trx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), "TRX Claims (Raw)")
        if not nbrx_claims.empty:
            render_styled_table(nbrx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), "NBRX Claims (Raw)")
        return

    # --- Standard NPA brands ---
    trx_ms = pivot_market_share(trx_data, "TRX MARKET SHARE")
    nbrx_ms = pivot_market_share(nbrx_data, "NBRX MARKET SHARE")
    trx_diff = pivot_market_share(trx_data, "TRX MS DIFF VS STLY")
    nbrx_diff = pivot_market_share(nbrx_data, "NBRX MS DIFF VS STLY")
    trx_claims = pivot_market_share(trx_data, "TRX CLAIMS")
    nbrx_claims = pivot_market_share(nbrx_data, "NBRX CLAIMS")

    # KPIs
    latest_qtr = trx_ms.index[-1] if not trx_ms.empty else "N/A"
    trx_val = trx_ms.loc[latest_qtr, brand_name] if (not trx_ms.empty and brand_name in trx_ms.columns and latest_qtr in trx_ms.index) else None
    nbrx_val = nbrx_ms.loc[latest_qtr, brand_name] if (not nbrx_ms.empty and brand_name in nbrx_ms.columns and latest_qtr in nbrx_ms.index) else None
    trx_diff_val = trx_diff.loc[latest_qtr, brand_name] if (not trx_diff.empty and brand_name in trx_diff.columns and latest_qtr in trx_diff.index) else None
    nbrx_diff_val = nbrx_diff.loc[latest_qtr, brand_name] if (not nbrx_diff.empty and brand_name in nbrx_diff.columns and latest_qtr in nbrx_diff.index) else None

    col1, col2 = st.columns(2)
    with col1:
        trx_str = f"{trx_val:.2f}%" if pd.notna(trx_val) else "N/A"
        delta_str = f"{trx_diff_val:+.2f}pp vs STLY" if pd.notna(trx_diff_val) else ""
        st.metric(f"{display_name} TRX Market Share (NPA)", trx_str, delta_str)
    with col2:
        nbrx_str = f"{nbrx_val:.2f}%" if pd.notna(nbrx_val) else "N/A"
        delta_str = f"{nbrx_diff_val:+.2f}pp vs STLY" if pd.notna(nbrx_diff_val) else ""
        st.metric(f"{display_name} NBRX Market Share (NPA)", nbrx_str, delta_str)

    st.caption(f"Latest quarter: {latest_qtr}")

    # TRX Market Share Trend
    if not trx_ms.empty:
        st.subheader(f"TRX Market Share Trend \u2014 {config['market_display']} (NPA)")
        brands_order = [brand_name] + [b for b in trx_ms.columns if b != brand_name]
        render_trend_chart(trx_ms, "TRX Market Share", brands_order)

    # NBRX Market Share Trend
    if not nbrx_ms.empty:
        st.subheader(f"NBRX Market Share Trend \u2014 {config['market_display']} (NPA)")
        brands_order_nbrx = [brand_name] + [b for b in nbrx_ms.columns if b != brand_name]
        render_trend_chart(nbrx_ms, "NBRX Market Share", brands_order_nbrx)

    # DDD metrics for vaccine brands
    ddd_brands = {"abrysvo": "ABRYSVO", "comirnaty": "COMIRNATY", "prevnar": "PREVNAR"}
    ddd_market_map = {"abrysvo": "RSV", "comirnaty": "COVID", "prevnar": "PCV"}
    if brand_key_page in ddd_brands:
        ddd_brand = ddd_brands[brand_key_page]
        ddd_market = ddd_market_map[brand_key_page]
        ddd_data = df[(df["DATASET"] == "DDD") & (df["MARKET"] == ddd_market)]
        if not ddd_data.empty:
            shipment_ms = pivot_market_share(ddd_data, "OVERALL_MS")
            if not shipment_ms.empty:
                st.subheader(f"Shipment Market Share \u2014 {ddd_market} (DDD)")
                ddd_order = [ddd_brand] + [b for b in shipment_ms.columns if b != ddd_brand]
                render_trend_chart(shipment_ms, "Shipment MS", ddd_order)

            retail_ms = pivot_market_share(ddd_data, "RETAIL_MS")
            if not retail_ms.empty:
                st.subheader(f"Retail Market Share \u2014 {ddd_market} (DDD)")
                retail_order = [ddd_brand] + [b for b in retail_ms.columns if b != ddd_brand]
                render_trend_chart(retail_ms, "Retail MS", retail_order)

            non_retail_ms = pivot_market_share(ddd_data, "NON_RETAIL_MS")
            if not non_retail_ms.empty:
                st.subheader(f"Non-Retail Market Share \u2014 {ddd_market} (DDD)")
                nr_order = [ddd_brand] + [b for b in non_retail_ms.columns if b != ddd_brand]
                render_trend_chart(non_retail_ms, "Non-Retail MS", nr_order)

    # Raw data tables
    st.subheader("Raw Data Tables")
    if not trx_ms.empty:
        display_df = trx_ms.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
        render_styled_table(display_df, "TRX Market Share (NPA)")
    if not nbrx_ms.empty:
        display_df = nbrx_ms.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
        render_styled_table(display_df, "NBRX Market Share (NPA)")
    if not trx_claims.empty:
        display_df = trx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
        render_styled_table(display_df, "TRX Claims (NPA)")
    if not nbrx_claims.empty:
        display_df = nbrx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
        render_styled_table(display_df, "NBRX Claims (NPA)")

    # Download
    st.subheader("Download")
    def generate_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            if not trx_ms.empty:
                trx_ms.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="TRX Market Share", index=False)
            if not nbrx_ms.empty:
                nbrx_ms.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="NBRX Market Share", index=False)
            if not trx_claims.empty:
                trx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="TRX Claims", index=False)
            if not nbrx_claims.empty:
                nbrx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="NBRX Claims", index=False)
        return output.getvalue()

    excel_data = generate_excel()
    st.download_button(
        label="\U0001f4e5 Download Excel Report",
        data=excel_data,
        file_name=f"{display_name.lower()}_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =====================================================
# HOME PAGE
# =====================================================

def render_home():
    render_ribbon("Primary Care Monthly Report Dashboard")
    st.markdown(HOME_BUTTON_CSS, unsafe_allow_html=True)

    # Refresh timestamp
    from datetime import datetime
    try:
        max_date_df = dataiku.Dataset("SQL_NPA_MAX_DATE_SF").get_dataframe()
        max_date_raw = str(max_date_df.iloc[0, 0]).split(" ")[0]
    except Exception:
        max_date_raw = "N/A"

    try:
        import pytz
        client = dataiku.api_client()
        project = client.get_default_project()
        ds = project.get_dataset(DATASET_NAME)
        last_metrics = ds.get_last_metric_values()
        build_date_metric = last_metrics.get_metric_by_id("reporting:BUILD_START_DATE")
        build_date_val = build_date_metric.get("lastValues", [{}])[0].get("value", None) if build_date_metric else None
        if build_date_val:
            utc_time = datetime.strptime(build_date_val, "%Y-%m-%dT%H:%M:%S.%fZ")
            ist = pytz.timezone("Asia/Kolkata")
            ist_time = pytz.utc.localize(utc_time).astimezone(ist)
            refresh_ts = ist_time.strftime("%B %d, %Y at %I:%M %p IST")
        else:
            refresh_ts = max_date_raw
    except Exception:
        refresh_ts = max_date_raw

    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.55); backdrop-filter: saturate(180%) blur(14px); border-radius: 14px; padding: 16px 24px; box-shadow: 0 2px 8px rgba(15,23,42,0.05); border: 1px solid rgba(15,23,42,0.08); border-left: 4px solid #1C4FC0; margin-bottom: 20px;">
        <div style="font-size: 14px; font-weight: 700; color: #0A1A3D; margin-bottom: 8px; font-family: 'Manrope', sans-serif;">Data Summary</div>
        <span style="font-size: 13px; color: #0F172A;"><strong>NPA:</strong> Till {max_date_raw} &nbsp;|&nbsp; <strong>DDD:</strong> Till {max_date_raw} &nbsp;|&nbsp; <strong>LAAD:</strong> Till {max_date_raw} &nbsp;|&nbsp; <strong>Refreshed:</strong> {refresh_ts}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Select a brand for Deep Dive QoQ Analysis")

    brands = list(BRAND_CONFIG.keys())
    for row_start in range(0, len(brands), 4):
        row_brands = brands[row_start:row_start + 4]
        cols = st.columns(4)
        for i, brand_key in enumerate(row_brands):
            with cols[i]:
                if st.button(BRAND_CONFIG[brand_key]["display_name"], key=f'{brand_key}_btn', use_container_width=True):
                    st.session_state["current_page"] = brand_key
                    st.rerun()


# =====================================================
# ROUTING
# =====================================================

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

page = st.session_state["current_page"]

if page == "home":
    render_home()
elif page in BRAND_CONFIG:
    render_brand_page(page)
