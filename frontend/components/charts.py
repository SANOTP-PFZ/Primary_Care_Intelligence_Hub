"""
Reusable chart components.
"""
import plotly.graph_objects as go
import streamlit as st


def create_line_chart(pivot_df, title, primary_brand=None, primary_color="#41B6E6", height=350):
    """
    Create a styled line chart from pivot data.
    
    Args:
        pivot_df: DataFrame with brands as index, quarters as columns
        title: Chart title
        primary_brand: Brand key to highlight
        primary_color: Color for the primary brand line
        height: Chart height in pixels
    """
    fig = go.Figure()

    for brand_name in pivot_df.index:
        is_primary = primary_brand and brand_name.upper() == primary_brand.upper()

        fig.add_trace(go.Scatter(
            x=list(pivot_df.columns),
            y=pivot_df.loc[brand_name].values,
            name=brand_name,
            mode="lines+markers",
            line=dict(
                width=3 if is_primary else 1.5,
                color=primary_color if is_primary else "#94A3B8",
            ),
            marker=dict(size=6 if is_primary else 4),
            opacity=1.0 if is_primary else 0.4,
        ))

    fig.update_layout(
        title=None,
        height=height,
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

    return fig


def render_chart_in_container(fig, title):
    """Render a Plotly chart inside a styled glass container."""
    st.markdown(f'<div class="chart-container"><h3>{title}</h3></div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, theme=None)
