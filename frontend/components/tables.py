"""
Styled table rendering components.
"""
import streamlit as st
import pandas as pd


def render_styled_table(df, max_rows=20, format_pct=True):
    """
    Render a DataFrame as a styled HTML table.
    
    Args:
        df: DataFrame to render
        max_rows: Max rows to display
        format_pct: Whether to format values as percentages
    """
    if df.empty:
        st.info("No data available.")
        return

    display_df = df.head(max_rows)

    # Build HTML table
    headers = "".join(f"<th>{col}</th>" for col in display_df.columns)
    rows = ""
    for _, row in display_df.iterrows():
        cells = ""
        for val in row:
            if format_pct and isinstance(val, (int, float)):
                cells += f"<td>{val:.1f}%</td>"
            else:
                cells += f"<td>{val}</td>"
        rows += f"<tr>{cells}</tr>"

    # Add index as first column
    index_header = f"<th>{display_df.index.name or 'Brand'}</th>"
    index_rows = ""
    for idx_val, row in display_df.iterrows():
        cells = f"<td><strong>{idx_val}</strong></td>"
        for val in row:
            if format_pct and isinstance(val, (int, float)):
                cells += f"<td>{val:.1f}%</td>"
            else:
                cells += f"<td>{val}</td>"
        index_rows += f"<tr>{cells}</tr>"

    st.markdown(f"""
    <div style="overflow-x:auto; margin-bottom:16px;">
        <table class="styled-table">
            <thead><tr>{index_header}{headers}</tr></thead>
            <tbody>{index_rows}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    if len(df) > max_rows:
        st.caption(f"Showing {max_rows} of {len(df)} rows")
