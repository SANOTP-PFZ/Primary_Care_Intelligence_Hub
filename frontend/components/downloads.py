"""
Download generation components (Excel, PDF).
"""
import streamlit as st
import pandas as pd
from io import BytesIO
import base64


def render_excel_download(df, filename, sheet_name="Data", button_label="📥 Download Excel"):
    """Render an Excel download link for a DataFrame."""
    if df is None or df.empty:
        return

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=True)

    b64 = base64.b64encode(buffer.getvalue()).decode()
    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    st.markdown(f"""
    <a href="data:{mime};base64,{b64}" download="{filename}" class="download-btn">
        {button_label}
    </a>
    """, unsafe_allow_html=True)


def render_csv_download(df, filename, button_label="📥 Download CSV"):
    """Render a CSV download link for a DataFrame."""
    if df is None or df.empty:
        return

    csv_bytes = df.to_csv(index=True).encode()
    b64 = base64.b64encode(csv_bytes).decode()

    st.markdown(f"""
    <a href="data:text/csv;base64,{b64}" download="{filename}" class="download-btn">
        {button_label}
    </a>
    """, unsafe_allow_html=True)
