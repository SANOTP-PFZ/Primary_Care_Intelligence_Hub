"""
Primary Care Intelligence Hub - Dataiku DSS Streamlit Webapp
Renders the full UI as an HTML component for pixel-perfect layout control.
"""
import streamlit as st

st.set_page_config(
    page_title="Primary Care Intelligence Hub",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit chrome
st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"], #MainMenu, footer,
    .stApp > header { display: none !important; }
    .stApp { background: transparent !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewBlockContainer"] { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
    --navy-900: #0A1A3D;
    --navy-800: #102A5C;
    --navy-700: #163990;
    --navy-600: #1C4FC0;
    --navy-500: #3B6FD9;
    --accent: #41B6E6;
    --bg: #EEF3FB;
    --surface: #FFFFFF;
    --text: #0F172A;
    --text-muted: #64748B;
    --text-soft: #475569;
    --hairline: rgba(15,23,42,0.08);
    --shadow-panel: 0 8px 24px rgba(15,23,42,0.07), 0 2px 6px rgba(15,23,42,0.04);
    --ease: cubic-bezier(0.4, 0, 0.2, 1);
    --sidebar-w: 232px;
    --shell-pad: 10px;
    --panel-radius: 18px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { height: 100%; }
body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background:
        radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.07) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 50% 100%, rgba(124,58,237,0.04) 0%, transparent 60%),
        var(--bg);
    color: var(--text);
    line-height: 1.5;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
    overflow: hidden;
}
h1, h2, h3, h4 { font-family: 'Manrope', 'Inter', system-ui, sans-serif; letter-spacing: -0.015em; }

/* APP SHELL */
.app { height: 100vh; display: grid; grid-template-columns: var(--sidebar-w) 1fr; gap: var(--shell-pad); padding: var(--shell-pad); overflow: hidden; }

/* SIDEBAR */
.sidebar {
    background: rgba(255,255,255,0.62);
    backdrop-filter: saturate(180%) blur(22px);
    -webkit-backdrop-filter: saturate(180%) blur(22px);
    border: 1px solid var(--hairline);
    border-radius: var(--panel-radius);
    box-shadow: var(--shadow-panel);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.sidebar-brand { padding: 1.4rem 1.2rem 1.2rem; display: flex; flex-direction: column; gap: 0.7rem; }
.sidebar-brand img { height: 28px; align-self: flex-start; }
.sidebar-brand .title { font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 1.22rem; color: var(--navy-900); line-height: 1.18; letter-spacing: -0.025em; }
.sidebar-brand .subtitle { font-size: 0.72rem; color: var(--text-muted); font-weight: 500; }
.sidebar-divider { height: 1px; background: var(--hairline); margin: 0 0.85rem; }
.sidebar-section-label { font-family: 'Manrope', sans-serif; font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text-muted); padding: 0.95rem 1.15rem 0.4rem; }

.nav { padding: 0 0.55rem; }
.nav-item {
    position: relative; display: flex; align-items: center; gap: 0.7rem;
    padding: 0.55rem 0.7rem; margin: 0.08rem 0; border-radius: 8px;
    font-size: 0.84rem; font-weight: 500; color: var(--text-soft);
    cursor: pointer; transition: background 0.18s var(--ease), color 0.18s var(--ease);
    background: transparent; border: none; width: 100%; text-align: left; font-family: inherit;
}
.nav-item .nav-icon { width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); transition: color 0.18s var(--ease); flex-shrink: 0; }
.nav-item .nav-icon svg { width: 16px; height: 16px; stroke-width: 1.8; fill: none; stroke: currentColor; }
.nav-item .nav-label { flex: 1; min-width: 0; }
.nav-item .nav-count { font-size: 0.66rem; font-weight: 600; color: var(--text-muted); background: rgba(15,23,42,0.06); padding: 0.12rem 0.42rem; border-radius: 5px; font-variant-numeric: tabular-nums; flex-shrink: 0; line-height: 1.3; }
.nav-item:hover { background: rgba(15,23,42,0.04); color: var(--text); }
.nav-item:hover .nav-icon { color: var(--navy-700); }
.nav-item.active { background: linear-gradient(90deg, rgba(28,79,192,0.10) 0%, rgba(28,79,192,0.04) 100%); color: var(--navy-700); font-weight: 600; }
.nav-item.active .nav-icon { color: var(--navy-700); }
.nav-item.active .nav-count { background: rgba(28,79,192,0.14); color: var(--navy-700); }
.nav-item.active::before { content: ''; position: absolute; left: -0.55rem; top: 6px; bottom: 6px; width: 3px; border-radius: 0 3px 3px 0; background: linear-gradient(180deg, var(--navy-600), var(--accent)); box-shadow: 0 0 8px rgba(28,79,192,0.3); }

.sidebar-spacer { flex: 1; }
.sidebar-meta { padding: 0.85rem 1.15rem 1rem; font-size: 0.7rem; color: var(--text-muted); line-height: 1.55; border-top: 1px solid var(--hairline); background: linear-gradient(180deg, transparent 0%, rgba(28,79,192,0.025) 100%); }
.sidebar-meta strong { color: var(--text-soft); font-weight: 600; }
.sidebar-meta .meta-row { margin-bottom: 0.2rem; }

/* MAIN */
.main {
    background: rgba(255,255,255,0.55);
    backdrop-filter: saturate(180%) blur(14px);
    -webkit-backdrop-filter: saturate(180%) blur(14px);
    border: 1px solid var(--hairline);
    border-radius: var(--panel-radius);
    box-shadow: var(--shadow-panel);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0;
}
.content { flex: 1; min-height: 0; overflow-y: auto; padding: 1.4rem; }
.content::-webkit-scrollbar { width: 6px; }
.content::-webkit-scrollbar-track { background: transparent; }
.content::-webkit-scrollbar-thumb { background: rgba(15,23,42,0.14); border-radius: 3px; }
</style>
</head>
<body>
<div class="app">

<aside class="sidebar">
    <div class="sidebar-brand">
        <img src="https://cdn.pfizer.com/pfizercom/2022-10/Pfizer_Logo_Color_CMYK.png" alt="Pfizer">
        <div>
            <div class="title">Primary Care<br>Intelligence Hub</div>
            <div class="subtitle">Pfizer Analytics</div>
        </div>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section-label">Primary Care Workspace</div>
    <nav class="nav">
        <button class="nav-item active" data-target="dashboards">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg></span>
            <span class="nav-label">Deep Dive Dashboards</span>
            <span class="nav-count">8</span>
        </button>
        <button class="nav-item" data-target="agents">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="10" rx="2"/><path d="M9 16v3M15 16v3M9 6V3M15 6V3M3 11h3M18 11h3"/></svg></span>
            <span class="nav-label">CoWork Agents</span>
            <span class="nav-count">6</span>
        </button>
    </nav>
    <div class="sidebar-spacer"></div>
    <div class="sidebar-meta">
        <div class="meta-row"><strong>Primary Care Analytics</strong></div>
        <div class="meta-row">Team_ZS_PC_Analytics@zs.com</div>
    </div>
</aside>

<div class="main">
    <main class="content">
        <p style="color: var(--text-muted); font-size: 0.9rem;">Main content area — ready for next phase.</p>
    </main>
</div>

</div>
</body>
</html>
"""

st.components.v1.html(html_content, height=920, scrolling=False)
