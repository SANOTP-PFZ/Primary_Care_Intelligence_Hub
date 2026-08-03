"""
Brand Deep Dive Pages - Renders brand-specific QoQ analysis views.
Uses same dataset (SQL_EARNINGS_REPORT_MASTER_DATASET_SF) and same data structure
as the reference Monthly Report Dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import dataiku

DATASET_NAME = "SQL_EARNINGS_REPORT_MASTER_DATASET_SF"
CHART_COLORS = ["#1C4FC0", "#41B6E6", "#7C3AED", "#0E7490", "#D946EF", "#047857", "#EF4444", "#64748B"]


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


def render_trend_chart(pivoted_df, brands_order=None, is_percentage=True):
    """Render a Plotly line chart from a pivoted DataFrame."""
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
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=60, r=30, t=20, b=50), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font=dict(family="Inter, system-ui", size=12), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0), hovermode="x unified")
    fig.update_xaxes(showgrid=False, tickfont=dict(size=11, color="#64748B"))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(15,23,42,0.06)", ticksuffix="%" if is_percentage else "", tickfont=dict(size=11, color="#64748B"), separatethousands=True)
    try:
        st.plotly_chart(fig, use_container_width=True, theme=None)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def render_brand_page(brand_key, brand_config):
    """Main entry point: renders the brand deep dive page."""
    config = brand_config[brand_key]
    brand_name = config["brand_key"]
    market = config["market"]
    display_name = config["display_name"]

    # Header + back button
    if st.button("\u2190 Back to Deep Dive", key="back_btn"):
        st.session_state["nav_state"] = "deepdive"
        st.rerun()
    st.markdown(f"### {display_name} \u2014 Quarter on Quarter Report")

    # Load data
    df = load_full_data()

    # === BEYFORTUS (LAAD source) ===
    if brand_key == "beyfortus":
        elaad_data = df[(df["DATASET"] == "ELAAD") & (df["MARKET"] == "BEYFORTUS")]
        if elaad_data.empty:
            st.warning("No LAAD data available for Beyfortus.")
            return
        claims = pivot_metric(elaad_data, "CLAIMS")
        patients = pivot_metric(elaad_data, "PATIENTS")
        if not claims.empty:
            st.subheader("Claims Trend (LAAD)")
            render_trend_chart(claims, [brand_name], is_percentage=False)
        if not patients.empty:
            st.subheader("Patients Trend (LAAD)")
            render_trend_chart(patients, [brand_name], is_percentage=False)
        # Raw tables
        if not claims.empty:
            with st.expander("Claims Data"):
                st.dataframe(claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), use_container_width=True, hide_index=True)
        if not patients.empty:
            with st.expander("Patients Data"):
                st.dataframe(patients.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), use_container_width=True, hide_index=True)
        return

    # === ZAVZPRET (Claims only, no market share) ===
    if brand_key == "zavzpret":
        trx_data = get_npa_trx_data(df, market)
        nbrx_data = get_npa_nbrx_data(df, market)
        trx_claims = pivot_metric(trx_data, "TRX CLAIMS")
        nbrx_claims = pivot_metric(nbrx_data, "NBRX CLAIMS")
        if not trx_claims.empty:
            st.subheader("TRX Claims Trend (NPA)")
            render_trend_chart(trx_claims, [brand_name], is_percentage=False)
        if not nbrx_claims.empty:
            st.subheader("NBRX Claims Trend (NPA)")
            render_trend_chart(nbrx_claims, [brand_name], is_percentage=False)
        # Raw tables
        if not trx_claims.empty:
            with st.expander("TRX Claims Data"):
                st.dataframe(trx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), use_container_width=True, hide_index=True)
        if not nbrx_claims.empty:
            with st.expander("NBRX Claims Data"):
                st.dataframe(nbrx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), use_container_width=True, hide_index=True)
        return

    # === STANDARD NPA BRANDS (Nurtec, Eliquis, Prevnar, Comirnaty, Abrysvo, Paxlovid) ===
    trx_data = get_npa_trx_data(df, market)
    nbrx_data = get_npa_nbrx_data(df, market)

    if trx_data.empty and nbrx_data.empty:
        st.warning(f"No NPA data for {display_name} in market '{market}'.")
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

    col1, col2 = st.columns(2)
    with col1:
        trx_str = f"{trx_val:.2f}%" if pd.notna(trx_val) else "N/A"
        delta = f"{trx_diff_val:+.2f}pp vs STLY" if pd.notna(trx_diff_val) else ""
        st.metric(f"{display_name} TRX Market Share (NPA)", trx_str, delta)
    with col2:
        nbrx_str = f"{nbrx_val:.2f}%" if pd.notna(nbrx_val) else "N/A"
        delta = f"{nbrx_diff_val:+.2f}pp vs STLY" if pd.notna(nbrx_diff_val) else ""
        st.metric(f"{display_name} NBRX Market Share (NPA)", nbrx_str, delta)
    st.caption(f"Latest quarter: {latest_qtr}")

    # --- TRX Market Share Trend ---
    if not trx_ms.empty:
        st.subheader(f"TRX Market Share \u2014 {config['market_display']} (NPA)")
        order = [brand_name] + [b for b in trx_ms.columns if b != brand_name]
        render_trend_chart(trx_ms, order)

    # --- NBRX Market Share Trend ---
    if not nbrx_ms.empty:
        st.subheader(f"NBRX Market Share \u2014 {config['market_display']} (NPA)")
        order = [brand_name] + [b for b in nbrx_ms.columns if b != brand_name]
        render_trend_chart(nbrx_ms, order)

    # --- DDD Metrics (Prevnar, Comirnaty, Abrysvo only) ---
    if "ddd_market" in config:
        ddd_market = config["ddd_market"]
        ddd_data = df[(df["DATASET"] == "DDD") & (df["MARKET"] == ddd_market)]
        if not ddd_data.empty:
            st.markdown("---")
            st.subheader(f"DDD Shipment Data \u2014 {ddd_market}")

            shipment_ms = pivot_metric(ddd_data, "OVERALL_MS")
            if not shipment_ms.empty:
                st.markdown(f"**Overall Shipment Market Share**")
                order = [brand_name] + [b for b in shipment_ms.columns if b != brand_name]
                render_trend_chart(shipment_ms, order)

            retail_ms = pivot_metric(ddd_data, "RETAIL_MS")
            if not retail_ms.empty:
                st.markdown(f"**Retail Market Share**")
                order = [brand_name] + [b for b in retail_ms.columns if b != brand_name]
                render_trend_chart(retail_ms, order)

            non_retail_ms = pivot_metric(ddd_data, "NON_RETAIL_MS")
            if not non_retail_ms.empty:
                st.markdown(f"**Non-Retail Market Share**")
                order = [brand_name] + [b for b in non_retail_ms.columns if b != brand_name]
                render_trend_chart(non_retail_ms, order)

    # --- Raw Data Tables ---
    st.markdown("---")
    st.subheader("Data Tables")
    if not trx_ms.empty:
        with st.expander("TRX Market Share (%)"):
            st.dataframe(trx_ms.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), use_container_width=True, hide_index=True)
    if not nbrx_ms.empty:
        with st.expander("NBRX Market Share (%)"):
            st.dataframe(nbrx_ms.round(2).reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), use_container_width=True, hide_index=True)
    if not trx_claims.empty:
        with st.expander("TRX Claims"):
            st.dataframe(trx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), use_container_width=True, hide_index=True)
    if not nbrx_claims.empty:
        with st.expander("NBRX Claims"):
            st.dataframe(nbrx_claims.reset_index().rename(columns={"YR_QTR_TXT": "Quarter"}), use_container_width=True, hide_index=True)

    # --- Excel Download ---
    st.markdown("---")
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

    st.download_button(
        label="\U0001f4e5 Download Excel Report",
        data=generate_excel(),
        file_name=f"{display_name.lower()}_qoq_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
