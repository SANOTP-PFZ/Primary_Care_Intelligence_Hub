"""
Brand Deep Dive Pages - Renders brand-specific QoQ analysis views.
Uses same dataset (SQL_EARNINGS_REPORT_MASTER_DATASET_SF) and same glassmorphism
design system as the landing page.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import base64
import dataiku

DATASET_NAME = "SQL_EARNINGS_REPORT_MASTER_DATASET_SF"
CHART_COLORS = ["#1C4FC0", "#41B6E6", "#7C3AED", "#0E7490", "#D946EF", "#047857", "#EF4444", "#64748B"]

# Pfizer logo (same as in DSS_app.py — small inline version)
PFIZER_LOGO_URL = "https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png"

# =====================================================
# BRAND PAGE CSS — matches landing page glassmorphism
# =====================================================

BRAND_PAGE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #EEF3FB;
        --surface: #FFFFFF;
        --text-1: #0F172A;
        --text-2: #1C4FC0;
        --text-3: #64748B;
        --border: rgba(15, 23, 42, 0.08);
        --border-hover: rgba(28, 79, 192, 0.35);
        --navy-700: #163990;
        --navy-800: #102A5C;
        --navy-900: #0A1A3D;
        --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
        --shadow-sm: 0 2px 8px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.04);
        --shadow-md: 0 6px 16px rgba(15, 23, 42, 0.07), 0 2px 4px rgba(15, 23, 42, 0.04);
        --shadow-panel: 0 8px 24px rgba(15, 23, 42, 0.07), 0 2px 6px rgba(15, 23, 42, 0.04);
        --radius: 14px;
        --radius-lg: 18px;
        --ease: cubic-bezier(0.4, 0, 0.2, 1);
        --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    }

    * { box-sizing: border-box; }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] { display: none !important; }

    .block-container { padding-top: 1rem !important; max-width: 100% !important; padding-left: 3rem !important; padding-right: 3rem !important; }
    html, body, [class*="css"] { font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--text-1) !important; -webkit-font-smoothing: antialiased; }
    h1, h2, h3, h4 { font-family: 'Manrope', 'Inter', system-ui, sans-serif; letter-spacing: -0.015em; }

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background:
            radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.06) 0%, transparent 60%),
            radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.05) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 50% 100%, rgba(124,58,237,0.03) 0%, transparent 60%),
            var(--bg) !important;
        color: var(--text-1);
    }

    [data-testid="stMarkdownContainer"] p { color: var(--text-1); }

    /* Expanders — glassmorphism */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.55) !important;
        backdrop-filter: saturate(180%) blur(14px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(14px) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow-xs) !important;
        transition: box-shadow 0.18s var(--ease), border-color 0.18s var(--ease) !important;
    }
    [data-testid="stExpander"]:hover { box-shadow: var(--shadow-sm) !important; border-color: var(--border-hover) !important; }
    [data-testid="stExpander"] summary { color: var(--text-2) !important; background: transparent !important; font-weight: 600 !important; }
    [data-testid="stExpander"] summary span { color: var(--text-2) !important; }
    [data-testid="stExpander"] summary:hover span { color: var(--navy-700) !important; }

    /* Chart containers — curved edges with glass border */
    [data-testid="stPlotlyChart"] {
        border-radius: 16px !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        background: rgba(255, 255, 255, 0.55) !important;
        backdrop-filter: saturate(180%) blur(14px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(14px) !important;
        padding: 12px !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        overflow: hidden !important;
        transition: box-shadow 0.18s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stPlotlyChart"]:hover {
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.07), 0 2px 4px rgba(15, 23, 42, 0.04) !important;
        border-color: rgba(28, 79, 192, 0.2) !important;
    }

    /* Back button — small pill, NOT large brand-card style */
    div[data-testid="stButton"]:first-of-type button {
        min-height: auto !important;
        padding: 8px 20px !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        background: rgba(255,255,255,0.7) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-2) !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-xs) !important;
        transition: all 0.18s var(--ease) !important;
        transform: none !important;
    }
    div[data-testid="stButton"]:first-of-type button:hover {
        background: #FFFFFF !important;
        border-color: var(--border-hover) !important;
        box-shadow: var(--shadow-sm) !important;
        color: var(--navy-700) !important;
        transform: none !important;
    }
</style>
"""


# =====================================================
# DATA LOADING
# =====================================================

@st.cache_data(ttl=3600)
def load_full_data():
    return dataiku.Dataset(DATASET_NAME).get_dataframe()


def get_npa_trx_data(df, market):
    return df[(df["DATASET"] == "NPA_TRX") & (df["MARKET"] == market)].copy()


def get_npa_nbrx_data(df, market):
    return df[(df["DATASET"] == "NPA_NBRX") & (df["MARKET"] == market)].copy()


def pivot_metric(df_subset, metric_name):
    """Pivot data to get brand x quarter matrix for a given metric."""
    filtered = df_subset[df_subset["METRICS"] == metric_name]
    if filtered.empty:
        return pd.DataFrame()
    pivoted = filtered.pivot_table(index="YR_QTR_TXT", columns="BRAND", values="VALUE")
    pivoted = pivoted.sort_index()
    if len(pivoted) > 10:
        pivoted = pivoted.iloc[-10:]
    return pivoted


# =====================================================
# UI HELPERS
# =====================================================

def inject_css():
    """Inject brand page CSS (call once at top of render)."""
    st.markdown(BRAND_PAGE_CSS, unsafe_allow_html=True)


def render_header(title):
    """Render glassmorphism floating header bar."""
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; padding:14px 24px; border-radius:18px; background:rgba(255,255,255,0.62); backdrop-filter:saturate(180%) blur(22px); -webkit-backdrop-filter:saturate(180%) blur(22px); margin:0.5rem 0 12px 0; box-shadow:0 8px 24px rgba(15,23,42,0.07),0 2px 6px rgba(15,23,42,0.04); border:1px solid rgba(15,23,42,0.08);">
        <div style="display:flex; align-items:center; gap:12px;">
            <img src="{PFIZER_LOGO_URL}" style="height:28px; max-width:120px; object-fit:contain;" />
            <span style="font-family:'Manrope',sans-serif; font-weight:800; font-size:22px; color:#0A1A3D; letter-spacing:-0.025em;">{title}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_back_button():
    """Render back button (pill style via CSS)."""
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("\u2190 Back to Home", key="back_btn"):
        st.session_state["nav_state"] = "home"
        st.rerun()


def render_kpi_cards(cards):
    """Render KPI cards with glassmorphism. cards = list of dicts with label, value, delta_html, period."""
    html = '<div style="display:flex; gap:18px; padding:12px 0 16px;">'
    for card in cards:
        html += f"""
        <div style="background:rgba(255,255,255,0.55); backdrop-filter:saturate(180%) blur(14px); -webkit-backdrop-filter:saturate(180%) blur(14px); border:1px solid rgba(15,23,42,0.08); border-radius:18px; padding:22px 28px; flex:1; box-shadow:0 2px 8px rgba(15,23,42,0.05),0 1px 2px rgba(15,23,42,0.04); transition:transform 0.28s cubic-bezier(0.16,1,0.3,1), box-shadow 0.28s cubic-bezier(0.4,0,0.2,1); position:relative; overflow:hidden;">
            <div style="color:#64748B; font-size:12px; font-weight:500; margin-bottom:6px;">{card['label']}</div>
            <div style="color:#0A1A3D; font-family:'Manrope',sans-serif; font-size:32px; font-weight:700; font-variant-numeric:tabular-nums; line-height:1.1; letter-spacing:-0.02em;">{card['value']} {card.get('delta_html', '')}</div>
            <div style="color:#64748B; font-size:11px; font-weight:500; margin-top:8px;">{card.get('period', '')}</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_section_title(title, source_tag=""):
    """Render a styled section title with spacing below."""
    tag_html = f' <span style="font-size:13px; color:#1C4FC0; font-weight:500;">({source_tag})</span>' if source_tag else ""
    st.markdown(f'<div style="padding:20px 0 12px; color:#0A1A3D; font-family:\'Manrope\',sans-serif; font-size:18px; font-weight:700; letter-spacing:-0.015em;">{title}{tag_html}</div>', unsafe_allow_html=True)


def format_delta_html(val, suffix="pp vs STLY"):
    """Format a delta value as colored HTML."""
    if pd.isna(val):
        return ""
    sign = "+" if val >= 0 else ""
    color = "#10B981" if val >= 0 else "#EF4444"
    arrow = "&#9650;" if val >= 0 else "&#9660;"
    return f'<span style="font-size:18px; color:{color}; font-weight:600;">{arrow} {sign}{val:.2f}{suffix}</span>'


def render_trend_chart(pivoted_df, brands_order=None, is_percentage=True):
    """Render a Plotly line chart."""
    if pivoted_df.empty:
        st.info("No data available.")
        return
    fig = go.Figure()
    brands = brands_order if brands_order else list(pivoted_df.columns)
    for i, brand in enumerate(brands):
        if brand not in pivoted_df.columns:
            continue
        y_vals = pivoted_df[brand].tolist()
        hover = f"<b>{brand}</b><br>%{{x}}<br>%{{y:.2f}}%<extra></extra>" if is_percentage else f"<b>{brand}</b><br>%{{x}}<br>%{{y:,.0f}}<extra></extra>"
        if i == 0:
            text_vals = [f"{v:.2f}" if pd.notna(v) else "" for v in y_vals] if is_percentage else [f"{v:,.0f}" if pd.notna(v) else "" for v in y_vals]
            fig.add_trace(go.Scatter(x=pivoted_df.index.tolist(), y=y_vals, mode="lines+markers+text", name=brand, text=text_vals, textposition="top center", textfont=dict(size=10, color=CHART_COLORS[0]), line=dict(color=CHART_COLORS[0], width=3), marker=dict(size=7), hovertemplate=hover))
        else:
            fig.add_trace(go.Scatter(x=pivoted_df.index.tolist(), y=y_vals, mode="lines+markers", name=brand, line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2), marker=dict(size=5), hovertemplate=hover))
    fig.update_layout(template="plotly_white", height=420, margin=dict(l=60, r=30, t=20, b=50), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(family="Inter, system-ui, sans-serif", size=13, color="#0F172A"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12, color="#64748B")), hovermode="x unified")
    fig.update_xaxes(showgrid=False, tickfont=dict(size=12, color="#64748B"), linecolor="rgba(15,23,42,0.08)", tickcolor="rgba(15,23,42,0.08)", ticks="outside", title_text="")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(15,23,42,0.06)", ticksuffix="%" if is_percentage else "", tickfont=dict(size=12, color="#64748B"), linecolor="rgba(15,23,42,0.08)", tickcolor="rgba(15,23,42,0.08)", ticks="outside", title_text="", separatethousands=True)
    try:
        st.plotly_chart(fig, use_container_width=True, theme=None)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def render_styled_table(df_to_render, title, expanded=False):
    """Render a DataFrame as a styled HTML table inside an expander."""
    if df_to_render.empty:
        return
    with st.expander(title, expanded=expanded):
        html = '<table style="width:100%; border-collapse:collapse; font-family:Inter,system-ui,sans-serif; margin:10px 0;">'
        html += '<thead><tr>'
        for col in df_to_render.columns:
            html += f'<th style="background:#102A5C; color:#FFFFFF; padding:10px 14px; text-align:center; font-size:12px; font-weight:600; letter-spacing:0.03em;">{col}</th>'
        html += '</tr></thead><tbody>'
        for idx, row in df_to_render.iterrows():
            bg = "#F8FAFD" if idx % 2 == 0 else "#FFFFFF"
            html += f'<tr style="background:{bg};">'
            for j, val in enumerate(row):
                align = "center"
                font_weight = "600" if j == 0 else "400"
                html += f'<td style="padding:9px 14px; text-align:{align}; font-size:12px; color:#0F172A; font-weight:{font_weight}; border-bottom:1px solid rgba(15,23,42,0.06);">{val}</td>'
            html += '</tr>'
        html += '</tbody></table>'
        st.markdown(html, unsafe_allow_html=True)


def render_download_link(data, file_name, label, mime):
    """Render a base64 HTML download link with pill styling."""
    if data is None:
        return
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:{mime};base64,{b64}" download="{file_name}" style="display:inline-flex;align-items:center;gap:0.4rem;padding:8px 20px;border-radius:999px;background:rgba(255,255,255,0.7);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid rgba(15,23,42,0.08);color:#1C4FC0;font-size:0.82rem;font-weight:600;text-decoration:none;font-family:Inter,system-ui,sans-serif;transition:all 0.18s cubic-bezier(0.4,0,0.2,1);box-shadow:0 1px 2px rgba(15,23,42,0.04);" onmouseover="this.style.background=\'#FFFFFF\';this.style.boxShadow=\'0 2px 8px rgba(15,23,42,0.05)\';this.style.borderColor=\'rgba(28,79,192,0.35)\';this.style.transform=\'translateY(-1px)\';" onmouseout="this.style.background=\'rgba(255,255,255,0.7)\';this.style.boxShadow=\'0 1px 2px rgba(15,23,42,0.04)\';this.style.borderColor=\'rgba(15,23,42,0.08)\';this.style.transform=\'none\';">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)


def render_footer():
    """No-op — footer removed to avoid hiding download links."""
    pass


# =====================================================
# MAIN BRAND PAGE RENDERER
# =====================================================

def render_brand_page(brand_key, brand_config):
    """Main entry point: renders the brand deep dive page."""
    config = brand_config[brand_key]
    brand_name = config["brand_key"]
    market = config["market"]
    display_name = config["display_name"]

    # Inject CSS + Header + Back button
    inject_css()
    render_header(f"{display_name} Quarter on Quarter Report")
    render_back_button()

    # Load data
    df = load_full_data()

    # === BEYFORTUS (LAAD source) ===
    if brand_key == "beyfortus":
        elaad_data = df[(df["DATASET"] == "ELAAD") & (df["MARKET"] == "BEYFORTUS")]
        if elaad_data.empty:
            st.warning("No LAAD data available for Beyfortus.")
            render_footer()
            return
        claims = pivot_metric(elaad_data, "CLAIMS")
        patients = pivot_metric(elaad_data, "PATIENTS")
        claims_growth = pivot_metric(elaad_data, "CLAIMS GROWTH PCT STLY")
        patients_growth = pivot_metric(elaad_data, "PATIENTS GROWTH PCT STLY")

        latest_qtr = claims.index[-1] if not claims.empty else (patients.index[-1] if not patients.empty else "N/A")
        claims_val = claims.loc[latest_qtr, brand_name] if (not claims.empty and brand_name in claims.columns) else None
        patients_val = patients.loc[latest_qtr, brand_name] if (not patients.empty and brand_name in patients.columns) else None
        cg = claims_growth.loc[latest_qtr, brand_name] if (not claims_growth.empty and brand_name in claims_growth.columns and latest_qtr in claims_growth.index) else None
        pg = patients_growth.loc[latest_qtr, brand_name] if (not patients_growth.empty and brand_name in patients_growth.columns and latest_qtr in patients_growth.index) else None

        render_kpi_cards([
            {"label": f"{display_name} Claims (LAAD)", "value": f"{claims_val:,.0f}" if pd.notna(claims_val) else "N/A", "delta_html": format_delta_html(cg, "% vs STLY"), "period": f"Latest: {latest_qtr}"},
            {"label": f"{display_name} Patients (LAAD)", "value": f"{patients_val:,.0f}" if pd.notna(patients_val) else "N/A", "delta_html": format_delta_html(pg, "% vs STLY"), "period": f"Latest: {latest_qtr}"},
        ])

        if not claims.empty:
            render_section_title("Claims Trend", "LAAD")
            render_trend_chart(claims, [brand_name], is_percentage=False)
        if not patients.empty:
            render_section_title("Patients Trend", "LAAD")
            render_trend_chart(patients, [brand_name], is_percentage=False)

        # Raw tables
        render_section_title("Raw Data Tables")
        if not claims.empty:
            display_df = claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
            for col in display_df.columns[1:]:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
            render_styled_table(display_df, "Claims (LAAD)")
        if not patients.empty:
            display_df = patients.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
            for col in display_df.columns[1:]:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
            render_styled_table(display_df, "Patients (LAAD)")

        # Download
        render_section_title("Download Reports")
        def gen_excel_bey():
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                if not claims.empty:
                    claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="Claims", index=False)
                if not patients.empty:
                    patients.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="Patients", index=False)
            return output.getvalue()
        render_download_link(gen_excel_bey(), "beyfortus_report.xlsx", "\U0001f4e5 Download Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        render_footer()
        return

    # === ZAVZPRET (Claims only, no market share) ===
    if brand_key == "zavzpret":
        trx_data = get_npa_trx_data(df, market)
        nbrx_data = get_npa_nbrx_data(df, market)
        trx_claims = pivot_metric(trx_data, "TRX CLAIMS")
        nbrx_claims = pivot_metric(nbrx_data, "NBRX CLAIMS")
        trx_growth = pivot_metric(trx_data, "TRX CLAIMS GROWTH PCT")
        nbrx_growth = pivot_metric(nbrx_data, "NBRX CLAIMS GROWTH PCT")

        if trx_claims.empty and nbrx_claims.empty:
            st.warning("No NPA data available for Zavzpret.")
            render_footer()
            return

        latest_qtr = trx_claims.index[-1] if not trx_claims.empty else nbrx_claims.index[-1]
        tc = trx_claims.loc[latest_qtr, brand_name] if (not trx_claims.empty and brand_name in trx_claims.columns) else None
        nc = nbrx_claims.loc[latest_qtr, brand_name] if (not nbrx_claims.empty and brand_name in nbrx_claims.columns) else None
        tg = trx_growth.loc[latest_qtr, brand_name] if (not trx_growth.empty and brand_name in trx_growth.columns and latest_qtr in trx_growth.index) else None
        ng = nbrx_growth.loc[latest_qtr, brand_name] if (not nbrx_growth.empty and brand_name in nbrx_growth.columns and latest_qtr in nbrx_growth.index) else None

        render_kpi_cards([
            {"label": f"{display_name} TRX Claims (NPA)", "value": f"{tc:,.0f}" if pd.notna(tc) else "N/A", "delta_html": format_delta_html(tg, "% vs STLY"), "period": f"Latest: {latest_qtr}"},
            {"label": f"{display_name} NBRX Claims (NPA)", "value": f"{nc:,.0f}" if pd.notna(nc) else "N/A", "delta_html": format_delta_html(ng, "% vs STLY"), "period": f"Latest: {latest_qtr}"},
        ])

        if not trx_claims.empty:
            render_section_title("TRX Claims Trend", "NPA")
            render_trend_chart(trx_claims, [brand_name], is_percentage=False)
        if not nbrx_claims.empty:
            render_section_title("NBRX Claims Trend", "NPA")
            render_trend_chart(nbrx_claims, [brand_name], is_percentage=False)

        render_section_title("Raw Data Tables")
        if not trx_claims.empty:
            display_df = trx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
            for col in display_df.columns[1:]:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
            render_styled_table(display_df, "TRX Claims (NPA)")
        if not nbrx_claims.empty:
            display_df = nbrx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
            for col in display_df.columns[1:]:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
            render_styled_table(display_df, "NBRX Claims (NPA)")

        render_section_title("Download Reports")
        def gen_excel_zav():
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                if not trx_claims.empty:
                    trx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="TRX Claims", index=False)
                if not nbrx_claims.empty:
                    nbrx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="NBRX Claims", index=False)
            return output.getvalue()
        render_download_link(gen_excel_zav(), "zavzpret_report.xlsx", "\U0001f4e5 Download Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        render_footer()
        return

    # === STANDARD NPA BRANDS (Nurtec, Eliquis, Prevnar, Comirnaty, Abrysvo, Paxlovid) ===
    trx_data = get_npa_trx_data(df, market)
    nbrx_data = get_npa_nbrx_data(df, market)

    if trx_data.empty and nbrx_data.empty:
        st.warning(f"No NPA data for {display_name} in market '{market}'.")
        render_footer()
        return

    trx_ms = pivot_metric(trx_data, "TRX MARKET SHARE")
    nbrx_ms = pivot_metric(nbrx_data, "NBRX MARKET SHARE")
    trx_diff = pivot_metric(trx_data, "TRX MS DIFF VS STLY")
    nbrx_diff = pivot_metric(nbrx_data, "NBRX MS DIFF VS STLY")
    trx_claims = pivot_metric(trx_data, "TRX CLAIMS")
    nbrx_claims = pivot_metric(nbrx_data, "NBRX CLAIMS")

    # --- KPIs ---
    latest_qtr = trx_ms.index[-1] if not trx_ms.empty else (nbrx_ms.index[-1] if not nbrx_ms.empty else "N/A")
    trx_val = trx_ms.loc[latest_qtr, brand_name] if (not trx_ms.empty and brand_name in trx_ms.columns) else None
    nbrx_val = nbrx_ms.loc[latest_qtr, brand_name] if (not nbrx_ms.empty and brand_name in nbrx_ms.columns) else None
    trx_diff_val = trx_diff.loc[latest_qtr, brand_name] if (not trx_diff.empty and brand_name in trx_diff.columns and latest_qtr in trx_diff.index) else None
    nbrx_diff_val = nbrx_diff.loc[latest_qtr, brand_name] if (not nbrx_diff.empty and brand_name in nbrx_diff.columns and latest_qtr in nbrx_diff.index) else None

    render_kpi_cards([
        {"label": f"{display_name} TRX Market Share (NPA)", "value": f"{trx_val:.2f}%" if pd.notna(trx_val) else "N/A", "delta_html": format_delta_html(trx_diff_val), "period": f"Latest: {latest_qtr}"},
        {"label": f"{display_name} NBRX Market Share (NPA)", "value": f"{nbrx_val:.2f}%" if pd.notna(nbrx_val) else "N/A", "delta_html": format_delta_html(nbrx_diff_val), "period": f"Latest: {latest_qtr}"},
    ])

    # --- TRX Market Share Trend ---
    if not trx_ms.empty:
        render_section_title(f"TRX Market Share Trend \u2014 {config['market_display']} Market", "NPA")
        order = [brand_name] + [b for b in trx_ms.columns if b != brand_name]
        render_trend_chart(trx_ms, order)

    # --- NBRX Market Share Trend ---
    if not nbrx_ms.empty:
        render_section_title(f"NBRX Market Share Trend \u2014 {config['market_display']} Market", "NPA")
        order = [brand_name] + [b for b in nbrx_ms.columns if b != brand_name]
        render_trend_chart(nbrx_ms, order)

    # --- DDD Metrics (Prevnar, Comirnaty, Abrysvo only) ---
    if "ddd_market" in config:
        ddd_market = config["ddd_market"]
        ddd_data = df[(df["DATASET"] == "DDD") & (df["MARKET"] == ddd_market)]
        if not ddd_data.empty:
            shipment_ms = pivot_metric(ddd_data, "OVERALL_MS")
            if not shipment_ms.empty:
                render_section_title(f"Shipment Market Share \u2014 {ddd_market} Market", "DDD")
                order = [brand_name] + [b for b in shipment_ms.columns if b != brand_name]
                render_trend_chart(shipment_ms, order)

            retail_ms = pivot_metric(ddd_data, "RETAIL_MS")
            if not retail_ms.empty:
                render_section_title(f"Retail Market Share \u2014 {ddd_market} Market", "DDD")
                order = [brand_name] + [b for b in retail_ms.columns if b != brand_name]
                render_trend_chart(retail_ms, order)

            non_retail_ms = pivot_metric(ddd_data, "NON_RETAIL_MS")
            if not non_retail_ms.empty:
                render_section_title(f"Non-Retail Market Share \u2014 {ddd_market} Market", "DDD")
                order = [brand_name] + [b for b in non_retail_ms.columns if b != brand_name]
                render_trend_chart(non_retail_ms, order)

            # --- Channel Contribution Pie + Trend (all DDD brands) ---
            retail_contrib = pivot_metric(ddd_data, "RETAIL_CONTRIBUTION")
            non_retail_contrib = pivot_metric(ddd_data, "NON_RETAIL_CONTRIBUTION")

            if (not retail_contrib.empty and brand_name in retail_contrib.columns) or \
               (not non_retail_contrib.empty and brand_name in non_retail_contrib.columns):
                render_section_title(f"{display_name} Channel Contribution", "DDD")
                latest_c_qtr = retail_contrib.index[-1] if not retail_contrib.empty else non_retail_contrib.index[-1]
                r_val = retail_contrib.loc[latest_c_qtr, brand_name] if (not retail_contrib.empty and brand_name in retail_contrib.columns) else 0
                nr_val = non_retail_contrib.loc[latest_c_qtr, brand_name] if (not non_retail_contrib.empty and brand_name in non_retail_contrib.columns) else 0

                col_pie, col_trend = st.columns([1, 2])
                with col_pie:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=["Retail", "Non-Retail"],
                        values=[r_val if pd.notna(r_val) else 0, nr_val if pd.notna(nr_val) else 0],
                        marker=dict(colors=["#1C4FC0", "#F8971D"], line=dict(color="#FFFFFF", width=2)),
                        textinfo="text",
                        text=[f"Retail<br>{r_val:.1f}%" if pd.notna(r_val) else "Retail<br>N/A", f"Non-Retail<br>{nr_val:.1f}%" if pd.notna(nr_val) else "Non-Retail<br>N/A"],
                        textposition="outside", textfont=dict(size=12, color="#0F172A"),
                        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
                        hole=0.4, pull=[0.03, 0.03]
                    )])
                    fig_pie.update_layout(template="plotly_white", height=350, margin=dict(l=30, r=30, t=40, b=30), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", title=dict(text=f"Latest: {latest_c_qtr}", font=dict(size=13, color="#1C4FC0")), showlegend=False)
                    try:
                        st.plotly_chart(fig_pie, use_container_width=True, theme=None)
                    except TypeError:
                        st.plotly_chart(fig_pie, use_container_width=True)

                with col_trend:
                    fig_ct = go.Figure()
                    if not retail_contrib.empty and brand_name in retail_contrib.columns:
                        fig_ct.add_trace(go.Scatter(x=retail_contrib.index.tolist(), y=retail_contrib[brand_name].tolist(), mode="lines+markers", name="Retail", line=dict(color="#1C4FC0", width=3), marker=dict(size=7), hovertemplate="<b>Retail</b><br>%{x}<br>%{y:.1f}%<extra></extra>"))
                    if not non_retail_contrib.empty and brand_name in non_retail_contrib.columns:
                        fig_ct.add_trace(go.Scatter(x=non_retail_contrib.index.tolist(), y=non_retail_contrib[brand_name].tolist(), mode="lines+markers", name="Non-Retail", line=dict(color="#F8971D", width=3), marker=dict(size=7), hovertemplate="<b>Non-Retail</b><br>%{x}<br>%{y:.1f}%<extra></extra>"))
                    fig_ct.update_layout(template="plotly_white", height=350, margin=dict(l=60, r=30, t=20, b=50), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(family="Inter, system-ui, sans-serif", size=13, color="#0F172A"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12, color="#64748B")), hovermode="x unified")
                    fig_ct.update_xaxes(showgrid=False, tickfont=dict(size=12, color="#64748B"), linecolor="rgba(15,23,42,0.08)", ticks="outside")
                    fig_ct.update_yaxes(showgrid=True, gridcolor="rgba(15,23,42,0.06)", ticksuffix="%", tickfont=dict(size=12, color="#64748B"), linecolor="rgba(15,23,42,0.08)", ticks="outside")
                    try:
                        st.plotly_chart(fig_ct, use_container_width=True, theme=None)
                    except TypeError:
                        st.plotly_chart(fig_ct, use_container_width=True)

            # --- Abrysvo-specific: OA MS + OA vs MA Contribution ---
            if brand_key == "abrysvo":
                oa_ms = pivot_metric(ddd_data, "OA_MS")
                if not oa_ms.empty:
                    render_section_title("OA Market Share \u2014 RSV Market", "DDD")
                    order = [brand_name] + [b for b in oa_ms.columns if b != brand_name]
                    render_trend_chart(oa_ms, order)

                oa_contrib = pivot_metric(ddd_data, "OA_CONTRIBUTION")
                ma_contrib = pivot_metric(ddd_data, "MA_CONTRIBUTION")
                if (not oa_contrib.empty and brand_name in oa_contrib.columns) or \
                   (not ma_contrib.empty and brand_name in ma_contrib.columns):
                    render_section_title(f"{display_name} OA vs MA Contribution", "DDD")
                    latest_oa_qtr = oa_contrib.index[-1] if not oa_contrib.empty else ma_contrib.index[-1]
                    oa_val = oa_contrib.loc[latest_oa_qtr, brand_name] if (not oa_contrib.empty and brand_name in oa_contrib.columns) else 0
                    ma_val = ma_contrib.loc[latest_oa_qtr, brand_name] if (not ma_contrib.empty and brand_name in ma_contrib.columns) else 0

                    col_pie2, col_trend2 = st.columns([1, 2])
                    with col_pie2:
                        fig_pie2 = go.Figure(data=[go.Pie(
                            labels=["OA", "MA"],
                            values=[oa_val if pd.notna(oa_val) else 0, ma_val if pd.notna(ma_val) else 0],
                            marker=dict(colors=["#1C4FC0", "#10B981"], line=dict(color="#FFFFFF", width=2)),
                            textinfo="text",
                            text=[f"OA<br>{oa_val:.1f}%" if pd.notna(oa_val) else "OA<br>N/A", f"MA<br>{ma_val:.1f}%" if pd.notna(ma_val) else "MA<br>N/A"],
                            textposition="outside", textfont=dict(size=12, color="#0F172A"),
                            hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
                            hole=0.4, pull=[0.03, 0.03]
                        )])
                        fig_pie2.update_layout(template="plotly_white", height=350, margin=dict(l=30, r=30, t=40, b=30), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", title=dict(text=f"Latest: {latest_oa_qtr}", font=dict(size=13, color="#1C4FC0")), showlegend=False)
                        try:
                            st.plotly_chart(fig_pie2, use_container_width=True, theme=None)
                        except TypeError:
                            st.plotly_chart(fig_pie2, use_container_width=True)

                    with col_trend2:
                        fig_oa = go.Figure()
                        if not oa_contrib.empty and brand_name in oa_contrib.columns:
                            fig_oa.add_trace(go.Scatter(x=oa_contrib.index.tolist(), y=oa_contrib[brand_name].tolist(), mode="lines+markers", name="OA Contribution", line=dict(color="#1C4FC0", width=3), marker=dict(size=7), hovertemplate="<b>OA</b><br>%{x}<br>%{y:.1f}%<extra></extra>"))
                        if not ma_contrib.empty and brand_name in ma_contrib.columns:
                            fig_oa.add_trace(go.Scatter(x=ma_contrib.index.tolist(), y=ma_contrib[brand_name].tolist(), mode="lines+markers", name="MA Contribution", line=dict(color="#10B981", width=3), marker=dict(size=7), hovertemplate="<b>MA</b><br>%{x}<br>%{y:.1f}%<extra></extra>"))
                        fig_oa.update_layout(template="plotly_white", height=350, margin=dict(l=60, r=30, t=20, b=50), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(family="Inter, system-ui, sans-serif", size=13, color="#0F172A"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12, color="#64748B")), hovermode="x unified")
                        fig_oa.update_xaxes(showgrid=False, tickfont=dict(size=12, color="#64748B"), linecolor="rgba(15,23,42,0.08)", ticks="outside")
                        fig_oa.update_yaxes(showgrid=True, gridcolor="rgba(15,23,42,0.06)", ticksuffix="%", tickfont=dict(size=12, color="#64748B"), linecolor="rgba(15,23,42,0.08)", ticks="outside")
                        try:
                            st.plotly_chart(fig_oa, use_container_width=True, theme=None)
                        except TypeError:
                            st.plotly_chart(fig_oa, use_container_width=True)

            # --- Prevnar-specific: Peds + Adult MS ---
            if brand_key == "prevnar":
                ped_ms = pivot_metric(ddd_data, "PED_MS")
                if not ped_ms.empty:
                    ped_brands = [b for b in ["PREVNAR", "VAXNEUVANCE"] if b in ped_ms.columns]
                    ped_ms_filtered = ped_ms[ped_brands]
                    ped_ms_filtered = ped_ms_filtered[ped_ms_filtered.index >= "2024Q1"]
                    if not ped_ms_filtered.empty:
                        render_section_title("Peds Market Share Trend \u2014 PCV Market", "DDD")
                        render_trend_chart(ped_ms_filtered, ped_brands)

                adult_ms = pivot_metric(ddd_data, "ADULT_MS")
                if not adult_ms.empty:
                    adult_brands = [b for b in ["PREVNAR", "VAXNEUVANCE", "CAPVAXIVE"] if b in adult_ms.columns]
                    adult_ms_filtered = adult_ms[adult_brands]
                    adult_ms_filtered = adult_ms_filtered[adult_ms_filtered.index >= "2024Q1"]
                    if not adult_ms_filtered.empty:
                        render_section_title("Adult Market Share Trend \u2014 PCV Market", "DDD")
                        render_trend_chart(adult_ms_filtered, adult_brands)

    # --- Section 1: QoQ Market Share Differences ---
    render_section_title("QoQ Market Share Differences")

    # Fetch additional metrics for this section
    trx_pq_ms = pivot_metric(trx_data, "TRX PQ MARKET SHARE")
    trx_ms_diff_pq = pivot_metric(trx_data, "TRX MS DIFF VS PQ")
    nbrx_pq_ms = pivot_metric(nbrx_data, "NBRX PQ MARKET SHARE")
    nbrx_ms_diff_pq = pivot_metric(nbrx_data, "NBRX MS DIFF VS PQ")

    if not trx_ms.empty and brand_name in trx_ms.columns:
        ms_trx_table = pd.DataFrame({"Quarter": trx_ms.index})
        ms_trx_table[f"{display_name} MS"] = trx_ms[brand_name].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-").values
        ms_trx_table["PQ MS"] = trx_pq_ms[brand_name].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-").values if (not trx_pq_ms.empty and brand_name in trx_pq_ms.columns) else "-"
        ms_trx_table["MS Diff vs STLY"] = trx_diff[brand_name].apply(lambda x: f"{x:+.2f}" if pd.notna(x) else "-").values if (not trx_diff.empty and brand_name in trx_diff.columns) else "-"
        ms_trx_table["MS Diff vs PQ"] = trx_ms_diff_pq[brand_name].apply(lambda x: f"{x:+.2f}" if pd.notna(x) else "-").values if (not trx_ms_diff_pq.empty and brand_name in trx_ms_diff_pq.columns) else "-"
        render_styled_table(ms_trx_table, f"TRX Market Share Difference \u2014 {display_name} (NPA)")

    if not nbrx_ms.empty and brand_name in nbrx_ms.columns:
        ms_nbrx_table = pd.DataFrame({"Quarter": nbrx_ms.index})
        ms_nbrx_table[f"{display_name} MS"] = nbrx_ms[brand_name].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-").values
        ms_nbrx_table["PQ MS"] = nbrx_pq_ms[brand_name].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-").values if (not nbrx_pq_ms.empty and brand_name in nbrx_pq_ms.columns) else "-"
        ms_nbrx_table["MS Diff vs STLY"] = nbrx_diff[brand_name].apply(lambda x: f"{x:+.2f}" if pd.notna(x) else "-").values if (not nbrx_diff.empty and brand_name in nbrx_diff.columns) else "-"
        ms_nbrx_table["MS Diff vs PQ"] = nbrx_ms_diff_pq[brand_name].apply(lambda x: f"{x:+.2f}" if pd.notna(x) else "-").values if (not nbrx_ms_diff_pq.empty and brand_name in nbrx_ms_diff_pq.columns) else "-"
        render_styled_table(ms_nbrx_table, f"NBRX Market Share Difference \u2014 {display_name} (NPA)")

    # --- Section 2: QoQ Growth Summaries ---
    render_section_title("QoQ Growth Summaries")

    # Fetch growth metrics (brand + market total)
    brand_market_data = df[df["BRAND"].isin([brand_name, market])].copy()
    trx_qoq_growth = pivot_metric(brand_market_data[(brand_market_data["DATASET"] == "NPA_TRX") & (brand_market_data["MARKET"] == market)], "TRX QOQ GROWTH PCT") if not brand_market_data.empty else pd.DataFrame()
    trx_stly_growth = pivot_metric(brand_market_data[(brand_market_data["DATASET"] == "NPA_TRX") & (brand_market_data["MARKET"] == market)], "TRX STLY GROWTH PCT") if not brand_market_data.empty else pd.DataFrame()
    nbrx_qoq_growth = pivot_metric(brand_market_data[(brand_market_data["DATASET"] == "NPA_NBRX") & (brand_market_data["MARKET"] == market)], "NBRX QOQ GROWTH PCT") if not brand_market_data.empty else pd.DataFrame()
    nbrx_stly_growth = pivot_metric(brand_market_data[(brand_market_data["DATASET"] == "NPA_NBRX") & (brand_market_data["MARKET"] == market)], "NBRX STLY GROWTH PCT") if not brand_market_data.empty else pd.DataFrame()

    def fmt_growth(val):
        if pd.isna(val):
            return "-"
        sign = "+" if val >= 0 else ""
        return f"{sign}{val:.2f}%"

    if not trx_claims.empty:
        gs_trx = pd.DataFrame({"Quarter": trx_claims.index})
        if brand_name in trx_claims.columns:
            gs_trx[f"{display_name} TRX Claims"] = trx_claims[brand_name].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-").values
            gs_trx[f"{display_name} PQ Growth %"] = trx_qoq_growth[brand_name].reindex(trx_claims.index).apply(fmt_growth).values if (not trx_qoq_growth.empty and brand_name in trx_qoq_growth.columns) else "-"
            gs_trx[f"{display_name} STLY Growth %"] = trx_stly_growth[brand_name].reindex(trx_claims.index).apply(fmt_growth).values if (not trx_stly_growth.empty and brand_name in trx_stly_growth.columns) else "-"
        if market in trx_claims.columns:
            gs_trx[f"{market} TRX Claims"] = trx_claims[market].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-").values
            gs_trx[f"{market} PQ Growth %"] = trx_qoq_growth[market].reindex(trx_claims.index).apply(fmt_growth).values if (not trx_qoq_growth.empty and market in trx_qoq_growth.columns) else "-"
            gs_trx[f"{market} STLY Growth %"] = trx_stly_growth[market].reindex(trx_claims.index).apply(fmt_growth).values if (not trx_stly_growth.empty and market in trx_stly_growth.columns) else "-"
        render_styled_table(gs_trx, "TRX Growth Summary (NPA)")

    if not nbrx_claims.empty:
        gs_nbrx = pd.DataFrame({"Quarter": nbrx_claims.index})
        if brand_name in nbrx_claims.columns:
            gs_nbrx[f"{display_name} NBRX Claims"] = nbrx_claims[brand_name].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-").values
            gs_nbrx[f"{display_name} PQ Growth %"] = nbrx_qoq_growth[brand_name].reindex(nbrx_claims.index).apply(fmt_growth).values if (not nbrx_qoq_growth.empty and brand_name in nbrx_qoq_growth.columns) else "-"
            gs_nbrx[f"{display_name} STLY Growth %"] = nbrx_stly_growth[brand_name].reindex(nbrx_claims.index).apply(fmt_growth).values if (not nbrx_stly_growth.empty and brand_name in nbrx_stly_growth.columns) else "-"
        if market in nbrx_claims.columns:
            gs_nbrx[f"{market} NBRX Claims"] = nbrx_claims[market].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-").values
            gs_nbrx[f"{market} PQ Growth %"] = nbrx_qoq_growth[market].reindex(nbrx_claims.index).apply(fmt_growth).values if (not nbrx_qoq_growth.empty and market in nbrx_qoq_growth.columns) else "-"
            gs_nbrx[f"{market} STLY Growth %"] = nbrx_stly_growth[market].reindex(nbrx_claims.index).apply(fmt_growth).values if (not nbrx_stly_growth.empty and market in nbrx_stly_growth.columns) else "-"
        render_styled_table(gs_nbrx, "NBRX Growth Summary (NPA)")

    # --- Section 3: Raw Data Tables ---
    render_section_title("Raw Data Tables")
    if not trx_ms.empty:
        display_df = trx_ms.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
        for col in display_df.columns[1:]:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
        render_styled_table(display_df, "TRX Market Share (NPA)")

    if not nbrx_ms.empty:
        display_df = nbrx_ms.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
        for col in display_df.columns[1:]:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
        render_styled_table(display_df, "NBRX Market Share (NPA)")

    if not trx_claims.empty:
        display_df = trx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
        for col in display_df.columns[1:]:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
        render_styled_table(display_df, "TRX Claims (NPA)")

    if not nbrx_claims.empty:
        display_df = nbrx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"})
        for col in display_df.columns[1:]:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
        render_styled_table(display_df, "NBRX Claims (NPA)")

    # --- Download ---
    render_section_title("Download Reports")

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
            if not trx_diff.empty:
                trx_diff.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="TRX MS Diff vs STLY", index=False)
            if not nbrx_diff.empty:
                nbrx_diff.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}).to_excel(writer, sheet_name="NBRX MS Diff vs STLY", index=False)
        return output.getvalue()

    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 3])
    with col_dl1:
        render_download_link(generate_excel(), f"{display_name.lower()}_report.xlsx", "\U0001f4e5 Download Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col_dl2:
        # PDF generation
        def generate_pdf():
            try:
                from reportlab.lib.pagesizes import letter, landscape
                from reportlab.lib.units import inch
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

                output = BytesIO()
                doc = SimpleDocTemplate(output, pagesize=landscape(letter), leftMargin=40, rightMargin=40, topMargin=30, bottomMargin=30)
                elements = []
                styles = getSampleStyleSheet()

                title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#1C4FC0"), spaceAfter=6)
                heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#1C4FC0"), spaceBefore=16, spaceAfter=8)
                kpi_style = ParagraphStyle("KPI", parent=styles["Normal"], fontSize=12, textColor=colors.HexColor("#1C4FC0"), spaceAfter=4)

                table_style_rl = TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1C4FC0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D8E0")),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F8")]),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 1), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                ])

                elements.append(Paragraph(f"{display_name} \u2014 {config['market_display']} Market Report", title_style))
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<b>Latest Quarter:</b> {latest_qtr}", kpi_style))
                trx_v_str = f"{trx_val:.2f}%" if pd.notna(trx_val) else "N/A"
                nbrx_v_str = f"{nbrx_val:.2f}%" if pd.notna(nbrx_val) else "N/A"
                trx_d_str = f" ({trx_diff_val:+.2f}pp vs STLY)" if pd.notna(trx_diff_val) else ""
                nbrx_d_str = f" ({nbrx_diff_val:+.2f}pp vs STLY)" if pd.notna(nbrx_diff_val) else ""
                elements.append(Paragraph(f"<b>{display_name} TRX Market Share (NPA):</b> {trx_v_str}{trx_d_str}", kpi_style))
                elements.append(Paragraph(f"<b>{display_name} NBRX Market Share (NPA):</b> {nbrx_v_str}{nbrx_d_str}", kpi_style))
                elements.append(Spacer(1, 14))

                if not trx_ms.empty:
                    elements.append(Paragraph("TRX Market Share (%)", heading_style))
                    header = ["Quarter"] + list(trx_ms.columns)
                    table_data = [header]
                    for qtr in trx_ms.index:
                        table_data.append([qtr] + [f"{v:.2f}" if pd.notna(v) else "-" for v in trx_ms.loc[qtr]])
                    t = Table(table_data, colWidths=[1.2*inch] + [1.3*inch]*min(len(trx_ms.columns), 6))
                    t.setStyle(table_style_rl)
                    elements.append(t)
                    elements.append(Spacer(1, 10))

                if not nbrx_ms.empty:
                    elements.append(Paragraph("NBRX Market Share (%)", heading_style))
                    header = ["Quarter"] + list(nbrx_ms.columns)
                    table_data = [header]
                    for qtr in nbrx_ms.index:
                        table_data.append([qtr] + [f"{v:.2f}" if pd.notna(v) else "-" for v in nbrx_ms.loc[qtr]])
                    t = Table(table_data, colWidths=[1.2*inch] + [1.3*inch]*min(len(nbrx_ms.columns), 6))
                    t.setStyle(table_style_rl)
                    elements.append(t)
                    elements.append(Spacer(1, 10))

                if not trx_claims.empty:
                    elements.append(Paragraph("TRX Claims", heading_style))
                    header = ["Quarter"] + list(trx_claims.columns)
                    table_data = [header]
                    for qtr in trx_claims.index:
                        table_data.append([qtr] + [f"{v:,.0f}" if pd.notna(v) else "-" for v in trx_claims.loc[qtr]])
                    t = Table(table_data, colWidths=[1.2*inch] + [1.3*inch]*min(len(trx_claims.columns), 6))
                    t.setStyle(table_style_rl)
                    elements.append(t)
                    elements.append(Spacer(1, 10))

                if not nbrx_claims.empty:
                    elements.append(Paragraph("NBRX Claims", heading_style))
                    header = ["Quarter"] + list(nbrx_claims.columns)
                    table_data = [header]
                    for qtr in nbrx_claims.index:
                        table_data.append([qtr] + [f"{v:,.0f}" if pd.notna(v) else "-" for v in nbrx_claims.loc[qtr]])
                    t = Table(table_data, colWidths=[1.2*inch] + [1.3*inch]*min(len(nbrx_claims.columns), 6))
                    t.setStyle(table_style_rl)
                    elements.append(t)

                doc.build(elements)
                return output.getvalue()
            except Exception:
                return None

        pdf_data = generate_pdf()
        if pdf_data:
            render_download_link(pdf_data, f"{display_name.lower()}_report.pdf", "\U0001f4c4 Download PDF", "application/pdf")

    render_footer()
