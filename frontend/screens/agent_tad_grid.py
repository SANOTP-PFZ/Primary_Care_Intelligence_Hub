"""
Agent TAD grid - subcategory/drill-down level (if needed).
Currently passes through to agent detail since our structure is category → agent.
"""
import streamlit as st
from frontend.screens.agent_ta_grid import render as render_ta_grid


def render():
    """For the current config, TAD grid is the same as TA grid."""
    render_ta_grid()
