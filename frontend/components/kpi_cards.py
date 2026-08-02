"""
Reusable KPI card components with delta arrow support.
"""
import streamlit as st


def render_kpi_row(kpis):
    """
    Render a row of KPI tiles.

    Args:
        kpis: list of dicts with keys:
            - label: str
            - value: str
            - delta: str (optional, e.g. "+12.4%")
            - direction: str (optional, "up"/"down"/"flat")
            - vs: str (optional, e.g. "vs STLY")
            - sub: str (optional, fallback text below value)
    """
    tiles_html = ""
    for kpi in kpis:
        delta_html = ""
        if kpi.get("delta"):
            direction = kpi.get("direction", "flat")
            tri = "&#9650;" if direction == "up" else "&#9660;" if direction == "down" else ""
            vs_text = f' <span class="vs">{kpi.get("vs", "")}</span>' if kpi.get("vs") else ""
            delta_html = f'<div class="kpi-delta {direction}"><span class="tri">{tri}</span>{kpi["delta"]}{vs_text}</div>'
        elif kpi.get("sub"):
            delta_html = f'<div class="kpi-sub">{kpi["sub"]}</div>'

        tiles_html += f"""
        <div class="kpi-tile">
            <div class="kpi-label">{kpi['label']}</div>
            <div class="kpi-value">{kpi['value']}</div>
            {delta_html}
        </div>
        """

    st.markdown(f'<div class="kpi-grid">{tiles_html}</div>', unsafe_allow_html=True)


def render_single_kpi(label, value, delta=None, direction="flat", vs="", sub=""):
    """Render a single standalone KPI card."""
    delta_html = ""
    if delta:
        tri = "&#9650;" if direction == "up" else "&#9660;" if direction == "down" else ""
        vs_text = f' <span class="vs">{vs}</span>' if vs else ""
        delta_html = f'<div class="kpi-delta {direction}"><span class="tri">{tri}</span>{delta}{vs_text}</div>'
    elif sub:
        delta_html = f'<div class="kpi-sub">{sub}</div>'

    st.markdown(f"""
    <div class="kpi-tile" style="display:inline-block; min-width:160px;">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)
