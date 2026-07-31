"""
Data transformation utilities.
"""
import pandas as pd
import base64
from io import BytesIO


def format_number(val, decimals=1, prefix="", suffix=""):
    """Format a number for display."""
    if pd.isna(val) or val is None:
        return "N/A"
    try:
        val = float(val)
        formatted = f"{val:,.{decimals}f}"
        return f"{prefix}{formatted}{suffix}"
    except (ValueError, TypeError):
        return str(val)


def format_percent(val, decimals=1):
    """Format a value as percentage."""
    return format_number(val, decimals=decimals, suffix="%")


def calculate_change(current, previous):
    """Calculate period-over-period change."""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return None
    return ((current - previous) / abs(previous)) * 100


def get_trend_arrow(trend):
    """Return an HTML arrow indicator based on trend direction."""
    if trend == "up":
        return '<span style="color:#10B981;">▲</span>'
    elif trend == "down":
        return '<span style="color:#EF4444;">▼</span>'
    return '<span style="color:#94A3B8;">─</span>'


def df_to_excel_bytes(df, sheet_name="Data"):
    """Convert a DataFrame to Excel bytes for download."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=True)
    return buffer.getvalue()


def get_download_link(data_bytes, filename, mime_type, link_text="Download"):
    """Generate a base64 download link (works in Dataiku DSS proxy)."""
    b64 = base64.b64encode(data_bytes).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}" style="color:#41B6E6; text-decoration:none; font-weight:600;">{link_text}</a>'
