"""
Primary Care Intelligence Hub - Dataiku DSS Streamlit Webapp
Main entry point with routing, session state management, and CSS injection.

Deployment: This file should be set as the Streamlit script in your Dataiku DSS webapp.
"""
import streamlit as st

# ─── Page Config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Primary Care Intelligence Hub",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Ensure project root is on sys.path (needed for Dataiku DSS exec-based loading) ──
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path("/home/dataiku/lib/project/project-python-libs/USPRIMARYCAREADHOCANALYTICSPARTC/Webapp/Primary_Care_Intelligence_Hub"))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ─── Imports ────────────────────────────────────────────────────────────────
from frontend.styles import get_global_css
from frontend.sidebar import render_sidebar
from frontend.screens import home, brand_page, agent_landing, agent_ta_grid, agent_tad_grid, agent_detail
from backend.config import BRAND_CONFIG

# ─── CSS Injection ──────────────────────────────────────────────────────────
st.markdown(get_global_css(), unsafe_allow_html=True)

# ─── Initialize Session State ───────────────────────────────────────────────
if "screen" not in st.session_state:
    st.session_state["screen"] = "home"

if "agent_screen" not in st.session_state:
    st.session_state["agent_screen"] = "landing"

# ─── Render Persistent Sidebar ──────────────────────────────────────────────
current_screen = render_sidebar()

# ─── Main Content Routing ───────────────────────────────────────────────────
if current_screen == "home":
    home.render()

elif current_screen in BRAND_CONFIG:
    brand_page.render(current_screen)

elif current_screen == "agents":
    # Sub-routing within the Agent Hub
    agent_screen = st.session_state.get("agent_screen", "landing")

    if agent_screen == "landing":
        agent_landing.render()
    elif agent_screen == "ta":
        agent_ta_grid.render()
    elif agent_screen == "tad":
        agent_tad_grid.render()
    elif agent_screen == "detail":
        agent_detail.render()
    else:
        agent_landing.render()

else:
    # Fallback to home
    home.render()
