"""
Data loading layer for Dataiku DSS datasets.
All data access is centralized here with caching.
"""
import pandas as pd
import streamlit as st
import dataiku

from backend.config import MASTER_DATASET, MAX_DATE_DATASET, BRAND_CONFIG


# ─────────────────────────────────────────────────────────────────────────────
# Core Data Loading
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_master_data():
    """Load the full earnings report master dataset."""
    dataset = dataiku.Dataset(MASTER_DATASET)
    df = dataset.get_dataframe()
    return df


@st.cache_data(ttl=3600)
def load_max_dates():
    """Load data freshness dates."""
    dataset = dataiku.Dataset(MAX_DATE_DATASET)
    df = dataset.get_dataframe()
    return df


# ─────────────────────────────────────────────────────────────────────────────
# NPA Data Extraction
# ─────────────────────────────────────────────────────────────────────────────

def get_npa_trx_data(df, brand_key, market):
    """Extract NPA TRx data for a given brand and market."""
    mask = (
        (df["DATASET"] == "NPA_TRX")
        & (df["MARKET"] == market)
    )
    brand_df = df[mask].copy()
    return brand_df


def get_npa_nbrx_data(df, brand_key, market):
    """Extract NPA NBRx data for a given brand and market."""
    mask = (
        (df["DATASET"] == "NPA_NBRX")
        & (df["MARKET"] == market)
    )
    brand_df = df[mask].copy()
    return brand_df


def get_ddd_data(df, brand_key, market):
    """Extract DDD shipment data for a given brand and market."""
    mask = (
        (df["DATASET"] == "DDD")
        & (df["MARKET"] == market)
    )
    brand_df = df[mask].copy()
    return brand_df


def get_elaad_data(df, brand_key, market):
    """Extract ELAAD claims data for a given brand and market."""
    mask = (
        (df["DATASET"] == "ELAAD")
        & (df["MARKET"] == market)
    )
    brand_df = df[mask].copy()
    return brand_df


# ─────────────────────────────────────────────────────────────────────────────
# Market Share Pivoting
# ─────────────────────────────────────────────────────────────────────────────

def pivot_market_share(df, brand_key, metric_filter="MS"):
    """
    Pivot data into time-series format for market share charts.
    Filters to rows containing the metric_filter string in METRICS column.
    Returns a pivoted DataFrame with quarters as columns and brands as rows.
    """
    ms_df = df[df["METRICS"].str.contains(metric_filter, case=False, na=False)].copy()

    if ms_df.empty:
        return pd.DataFrame()

    pivot = ms_df.pivot_table(
        index="BRAND",
        columns="YR_QTR_TXT",
        values="VALUE",
        aggfunc="first",
    )

    # Sort columns chronologically
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)
    return pivot


# ─────────────────────────────────────────────────────────────────────────────
# Summary KPIs for Home Page
# ─────────────────────────────────────────────────────────────────────────────

def get_brand_summary_kpis(df, brand_key, source):
    """
    Get the latest quarter KPI values for a brand (used on home page cards).
    Returns dict with latest_ms, latest_qtr, trend direction.
    """
    config = BRAND_CONFIG.get(brand_key.lower(), {})
    market = config.get("market", "")

    if source == "NPA":
        brand_df = get_npa_trx_data(df, brand_key, market)
    elif source == "DDD":
        brand_df = get_ddd_data(df, brand_key, market)
    elif source == "ELAAD":
        brand_df = get_elaad_data(df, brand_key, market)
    else:
        return {"latest_ms": "N/A", "latest_qtr": "N/A", "trend": "flat"}

    # Filter to brand-specific rows with market share metric
    brand_rows = brand_df[brand_df["BRAND"].str.upper() == brand_key.upper()]
    ms_rows = brand_rows[brand_rows["METRICS"].str.contains("MS|Share", case=False, na=False)]

    if ms_rows.empty:
        return {"latest_ms": "N/A", "latest_qtr": "N/A", "trend": "flat"}

    # Get latest quarter
    latest_qtr = sorted(ms_rows["YR_QTR_TXT"].unique())[-1] if not ms_rows["YR_QTR_TXT"].empty else "N/A"
    latest_val = ms_rows[ms_rows["YR_QTR_TXT"] == latest_qtr]["VALUE"].iloc[0] if latest_qtr != "N/A" else None

    # Determine trend
    qtrs = sorted(ms_rows["YR_QTR_TXT"].unique())
    if len(qtrs) >= 2:
        prev_qtr = qtrs[-2]
        prev_val = ms_rows[ms_rows["YR_QTR_TXT"] == prev_qtr]["VALUE"].iloc[0]
        if latest_val and prev_val:
            trend = "up" if latest_val > prev_val else ("down" if latest_val < prev_val else "flat")
        else:
            trend = "flat"
    else:
        trend = "flat"

    return {
        "latest_ms": f"{latest_val:.1f}%" if latest_val else "N/A",
        "latest_qtr": latest_qtr,
        "trend": trend,
    }


def get_data_freshness():
    """Get the latest data refresh date from the max dates dataset."""
    try:
        dates_df = load_max_dates()
        if not dates_df.empty:
            max_date = dates_df.iloc[0, 0]
            return str(max_date)
    except Exception:
        pass
    return "Unknown"
