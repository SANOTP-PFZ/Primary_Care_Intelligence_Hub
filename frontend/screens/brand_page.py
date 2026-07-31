"""
Brand page renderer for earnings report data.
Handles NPA (TRx/NBRx), DDD, and ELAAD brand pages with charts, tables, and downloads.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from backend.config import BRAND_CONFIG
from backend.data_loader import load_master_data, get_npa_trx_data, get_npa_nbrx_data, get_ddd_data, get_elaad_data, pivot_market_share
from backend.utils import format_percent, df_to_excel_bytes, get_download_link


def render(brand_key):
    """Render the full brand page for the given brand key."""
    config = BRAND_CONFIG.get(brand_key)
    if not config:
        st.error(f"Unknown brand: {brand_key}")
        return

    # ─── Breadcrumb ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="breadcrumb">
        <a href="#" onclick="return false;">Home</a>
        <span>›</span>
        Earnings Reports
        <span>›</span>
        <strong>{config['display_name']}</strong>
    </div>
    """, unsafe_allow_html=True)

    # ─── Page Header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="main-header">
        <h1>{config['icon']} {config['display_name']}</h1>
        <p>{config['market_display']} · Source: {config['source']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ─── Load Data ──────────────────────────────────────────────────────
    df = load_master_data()
    brand = config["brand_key"]
    market = config["market"]
    source = config["source"]

    # Route to the appropriate renderer based on data source
    if source == "NPA":
        _render_npa_brand(df, brand, market, config)
    elif source == "DDD":
        _render_ddd_brand(df, brand, market, config)
    elif source == "ELAAD":
        _render_elaad_brand(df, brand, market, config)


def _render_npa_brand(df, brand_key, market, config):
    """Render NPA-based brand page (TRx + NBRx market share)."""
    # ── TRx Section ─────────────────────────────────────────────────────
    st.markdown('<p class="section-header">TRx Market Share</p>', unsafe_allow_html=True)

    trx_df = get_npa_trx_data(df, brand_key, market)
    trx_pivot = pivot_market_share(trx_df, brand_key, "TRx MS")

    if not trx_pivot.empty:
        # KPI: Latest quarter market share
        _render_latest_kpi(trx_pivot, brand_key, "TRx Market Share")

        # Trend chart
        _render_trend_chart(trx_pivot, f"{config['display_name']} - TRx Market Share Trend", config["color"])

        # Data table
        with st.expander("📋 TRx Market Share Data", expanded=False):
            st.dataframe(trx_pivot.style.format("{:.1f}%"), use_container_width=True)
    else:
        st.info("No TRx market share data available for this brand.")

    # ── NBRx Section ────────────────────────────────────────────────────
    st.markdown('<p class="section-header">NBRx Market Share</p>', unsafe_allow_html=True)

    nbrx_df = get_npa_nbrx_data(df, brand_key, market)
    nbrx_pivot = pivot_market_share(nbrx_df, brand_key, "NBRx MS")

    if not nbrx_pivot.empty:
        _render_latest_kpi(nbrx_pivot, brand_key, "NBRx Market Share")
        _render_trend_chart(nbrx_pivot, f"{config['display_name']} - NBRx Market Share Trend", config["color"])

        with st.expander("📋 NBRx Market Share Data", expanded=False):
            st.dataframe(nbrx_pivot.style.format("{:.1f}%"), use_container_width=True)
    else:
        st.info("No NBRx market share data available for this brand.")

    # ── Downloads ───────────────────────────────────────────────────────
    _render_downloads(trx_pivot, nbrx_pivot, config)


def _render_ddd_brand(df, brand_key, market, config):
    """Render DDD-based brand page (shipment/retail/non-retail MS)."""
    st.markdown('<p class="section-header">Shipment Market Share</p>', unsafe_allow_html=True)

    ddd_df = get_ddd_data(df, brand_key, market)
    shipment_pivot = pivot_market_share(ddd_df, brand_key, "Shipment MS")

    if not shipment_pivot.empty:
        _render_latest_kpi(shipment_pivot, brand_key, "Shipment MS")
        _render_trend_chart(shipment_pivot, f"{config['display_name']} - Shipment Market Share", config["color"])

        with st.expander("📋 Shipment Market Share Data", expanded=False):
            st.dataframe(shipment_pivot.style.format("{:.1f}%"), use_container_width=True)
    else:
        st.info("No shipment market share data available.")

    # Retail vs Non-Retail
    st.markdown('<p class="section-header">Retail vs Non-Retail</p>', unsafe_allow_html=True)

    retail_pivot = pivot_market_share(ddd_df, brand_key, "Retail MS")
    nonretail_pivot = pivot_market_share(ddd_df, brand_key, "Non-Retail MS")

    col1, col2 = st.columns(2)
    with col1:
        if not retail_pivot.empty:
            _render_trend_chart(retail_pivot, "Retail Market Share", "#10B981")
        else:
            st.info("No retail data available.")
    with col2:
        if not nonretail_pivot.empty:
            _render_trend_chart(nonretail_pivot, "Non-Retail Market Share", "#6366F1")
        else:
            st.info("No non-retail data available.")

    # Downloads
    _render_downloads(shipment_pivot, retail_pivot, config)


def _render_elaad_brand(df, brand_key, market, config):
    """Render ELAAD-based brand page (claims/patients)."""
    st.markdown('<p class="section-header">Claims & Patient Analytics</p>', unsafe_allow_html=True)

    elaad_df = get_elaad_data(df, brand_key, market)
    claims_pivot = pivot_market_share(elaad_df, brand_key, "Claims")

    if not claims_pivot.empty:
        _render_latest_kpi(claims_pivot, brand_key, "Claims Volume")
        _render_trend_chart(claims_pivot, f"{config['display_name']} - Claims Trend", config["color"])

        with st.expander("📋 Claims Data", expanded=False):
            st.dataframe(claims_pivot, use_container_width=True)
    else:
        st.info("No ELAAD claims data available for this brand.")

    # Patient data
    patients_pivot = pivot_market_share(elaad_df, brand_key, "Patient")
    if not patients_pivot.empty:
        st.markdown('<p class="section-header">Patient Volume</p>', unsafe_allow_html=True)
        _render_trend_chart(patients_pivot, f"{config['display_name']} - Patient Volume Trend", config["color"])

    # Downloads
    _render_downloads(claims_pivot, patients_pivot, config)


# ─────────────────────────────────────────────────────────────────────────────
# Shared sub-components
# ─────────────────────────────────────────────────────────────────────────────

def _render_latest_kpi(pivot_df, brand_key, metric_name):
    """Show the latest quarter KPI value for the brand."""
    if pivot_df.empty:
        return

    # Find the brand row (case-insensitive match)
    brand_row = pivot_df[pivot_df.index.str.upper() == brand_key.upper()]
    if brand_row.empty:
        return

    latest_col = pivot_df.columns[-1]
    latest_val = brand_row.iloc[0][latest_col]

    prev_col = pivot_df.columns[-2] if len(pivot_df.columns) >= 2 else None
    prev_val = brand_row.iloc[0][prev_col] if prev_col else None

    # Calculate change
    change_html = ""
    if prev_val and latest_val:
        try:
            change = float(latest_val) - float(prev_val)
            color = "var(--success)" if change >= 0 else "var(--danger)"
            arrow = "▲" if change >= 0 else "▼"
            change_html = f'<span style="color:{color}; font-size:13px; font-weight:600;">{arrow} {abs(change):.1f}pp vs prior</span>'
        except (ValueError, TypeError):
            pass

    st.markdown(f"""
    <div class="kpi-grid" style="margin-bottom:20px;">
        <div class="kpi-tile">
            <div class="kpi-label">{metric_name}</div>
            <div class="kpi-value">{format_percent(latest_val)}</div>
            <div class="kpi-sub">{latest_col} {change_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_trend_chart(pivot_df, title, color):
    """Render a Plotly line chart of the pivot data."""
    fig = go.Figure()

    for brand_name in pivot_df.index:
        row = pivot_df.loc[brand_name]
        is_primary = brand_name.upper() in [b["brand_key"] for b in BRAND_CONFIG.values()]

        fig.add_trace(go.Scatter(
            x=list(pivot_df.columns),
            y=row.values,
            name=brand_name,
            mode="lines+markers",
            line=dict(
                width=3 if is_primary else 1.5,
                color=color if is_primary else "#94A3B8",
            ),
            marker=dict(size=6 if is_primary else 4),
            opacity=1.0 if is_primary else 0.5,
        ))

    fig.update_layout(
        title=None,
        height=350,
        margin=dict(l=20, r=20, t=10, b=40),
        font=dict(family="Inter, sans-serif", size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        xaxis=dict(gridcolor="rgba(15,23,42,0.06)", showline=False),
        yaxis=dict(gridcolor="rgba(15,23,42,0.06)", showline=False, ticksuffix="%"),
    )

    st.markdown(f"""
    <div class="chart-container">
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True, theme=None)


def _render_downloads(primary_df, secondary_df, config):
    """Render Excel download links for the brand data."""
    st.markdown('<p class="section-header">📥 Downloads</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if primary_df is not None and not primary_df.empty:
            excel_bytes = df_to_excel_bytes(primary_df, sheet_name=config["display_name"])
            link = get_download_link(
                excel_bytes,
                f"{config['display_name']}_data.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "📥 Download Primary Data (Excel)"
            )
            st.markdown(link, unsafe_allow_html=True)

    with col2:
        if secondary_df is not None and not secondary_df.empty:
            excel_bytes = df_to_excel_bytes(secondary_df, sheet_name="Secondary")
            link = get_download_link(
                excel_bytes,
                f"{config['display_name']}_secondary.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "📥 Download Secondary Data (Excel)"
            )
            st.markdown(link, unsafe_allow_html=True)
