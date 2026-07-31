"""
Reusable KPI card components.
"""
import streamlit as st


def render_kpi_row(kpis):
    """
    Render a row of KPI tiles.
    
    Args:
        kpis: list of dicts with keys: label, value, sub (optional)
    """
    tiles_html = ""
    for kpi in kpis:
        sub = kpi.get("sub", "")
        sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
        tiles_html += f"""
        <div class="kpi-tile">
            <div class="kpi-label">{kpi['label']}</div>
            <div class="kpi-value">{kpi['value']}</div>
            {sub_html}
        </div>
        """

    st.markdown(f'<div class="kpi-grid">{tiles_html}</div>', unsafe_allow_html=True)


def render_single_kpi(label, value, sub="", color=None):
    """Render a single standalone KPI card."""
    color_style = f"color:{color};" if color else ""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""

    st.markdown(f"""
    <div class="kpi-tile" style="display:inline-block; min-width:180px;">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="{color_style}">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)
