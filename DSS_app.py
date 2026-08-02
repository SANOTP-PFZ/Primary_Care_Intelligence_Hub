"""
Primary Care Intelligence Hub - Landing Page
Sidebar-only implementation using full HTML component for pixel-perfect UI.
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

/* Brand section (top) */
.sidebar-brand {
    padding: 10px 1.2rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
}
.sidebar-brand img { height: 28px; align-self: flex-start; }
.sidebar-brand .title {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 1.22rem;
    color: var(--navy-900);
    line-height: 1.18;
    letter-spacing: -0.025em;
}
.sidebar-brand .subtitle { font-size: 0.72rem; color: var(--text-muted); font-weight: 500; }

/* Divider */
.sidebar-divider { height: 1px; background: var(--hairline); margin: 0 0.85rem; }

/* Section label */
.sidebar-section-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    padding: 0.95rem 1.15rem 0.4rem;
}

/* Nav items */
.nav { padding: 0 0.55rem; }
.nav-item {
    position: relative;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.55rem 0.7rem;
    margin: 0.08rem 0;
    border-radius: 8px;
    font-size: 0.84rem;
    font-weight: 500;
    color: var(--text-soft);
    cursor: pointer;
    transition: background 0.18s var(--ease), color 0.18s var(--ease);
    background: transparent;
    border: none;
    width: 100%;
    text-align: left;
    font-family: inherit;
}
.nav-item .nav-icon { width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); transition: color 0.18s var(--ease); flex-shrink: 0; }
.nav-item .nav-icon svg { width: 16px; height: 16px; stroke-width: 1.8; fill: none; stroke: currentColor; }
.nav-item .nav-label { flex: 1; min-width: 0; }
.nav-item:hover { background: rgba(15,23,42,0.04); color: var(--text); }
.nav-item:hover .nav-icon { color: var(--navy-700); }
.nav-item.active { background: linear-gradient(90deg, rgba(28,79,192,0.10) 0%, rgba(28,79,192,0.04) 100%); color: var(--navy-700); font-weight: 600; }
.nav-item.active .nav-icon { color: var(--navy-700); }
.nav-item.active::before { content: ''; position: absolute; left: -0.55rem; top: 6px; bottom: 6px; width: 3px; border-radius: 0 3px 3px 0; background: linear-gradient(180deg, var(--navy-600), var(--accent)); box-shadow: 0 0 8px rgba(28,79,192,0.3); }

/* Spacer pushes footer to bottom */
.sidebar-spacer { flex: 1; }

/* Footer (bottom) */
.sidebar-meta {
    padding: 0.85rem 1.15rem 1rem;
    font-size: 0.7rem;
    color: var(--text-muted);
    line-height: 1.55;
    border-top: 1px solid var(--hairline);
    background: linear-gradient(180deg, transparent 0%, rgba(28,79,192,0.025) 100%);
}
.sidebar-meta strong { color: var(--text-soft); font-weight: 600; }
.sidebar-meta .meta-row { margin-bottom: 0.2rem; }

/* MAIN PANEL */
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

/* SECTION HEADER */
.section-header {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: var(--navy-900);
    margin-bottom: 0.25rem;
}
.section-subtitle {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 500;
    margin-bottom: 1rem;
}

/* BRAND SUMMARY CONTAINER */
.brand-summary {
    background: rgba(255,255,255,0.62);
    backdrop-filter: saturate(180%) blur(22px);
    -webkit-backdrop-filter: saturate(180%) blur(22px);
    border: 1px solid var(--hairline);
    border-radius: var(--panel-radius);
    box-shadow: var(--shadow-panel);
    padding: 1.1rem;
}

/* BRAND CARDS GRID - 3 top, 2 bottom centered */
.brand-cards-top {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
}
.brand-cards-bottom {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    margin-top: 0.75rem;
    max-width: 66.66%;
    margin-left: auto;
    margin-right: auto;
}

/* INDIVIDUAL BRAND CARD */
.brand-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: saturate(160%) blur(12px);
    -webkit-backdrop-filter: saturate(160%) blur(12px);
    border: 1px solid var(--hairline);
    border-radius: 12px;
    padding: 0.75rem 0.9rem 0.55rem;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
    transition: box-shadow 0.2s var(--ease), transform 0.2s var(--ease);
}
.brand-card:hover {
    box-shadow: 0 6px 16px rgba(15,23,42,0.08);
    transform: translateY(-1px);
}
.card-top {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.35rem;
}
.brand-name {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    color: var(--navy-900);
}
.brand-metric {
    display: flex;
    align-items: center;
    gap: 0.3rem;
}
.brand-value {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 0.9rem;
    color: var(--text);
}
.brand-delta {
    font-size: 0.62rem;
    font-weight: 600;
    padding: 1px 5px;
    border-radius: 4px;
}
.brand-delta.up { color: #059669; background: rgba(16,185,129,0.1); }
.brand-delta.down { color: #DC2626; background: rgba(239,68,68,0.08); }
.brand-spark { width: 100%; }
.brand-spark svg { width: 100%; height: 28px; display: block; }
</style>
</head>
<body>
<div class="app">

<!-- SIDEBAR -->
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
        <button class="nav-item active">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg></span>
            <span class="nav-label">Deep Dive Dashboards</span>
        </button>
        <button class="nav-item">
            <span class="nav-icon"><svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="10" rx="2"/><path d="M9 16v3M15 16v3M9 6V3M15 6V3M3 11h3M18 11h3"/></svg></span>
            <span class="nav-label">CoWork Agents</span>
        </button>
    </nav>

    <div class="sidebar-spacer"></div>

    <div class="sidebar-meta">
        <div class="meta-row"><strong>Primary Care Analytics</strong></div>
        <div class="meta-row">Team_ZS_PC_Analytics@zs.com</div>
    </div>
</aside>

<!-- MAIN PANEL -->
<div class="main">
    <main class="content">
        <div class="section-header">Primary Care Brand Performance Summary</div>
        <div class="section-subtitle">TRx Market Share Trend | 2024 Q1 onwards</div>

        <div class="brand-summary">
            <!-- Top row: 3 cards -->
            <div class="brand-cards-top">
                <div class="brand-card">
                    <div class="card-top">
                        <span class="brand-name">Nurtec</span>
                        <span class="brand-metric"><span class="brand-value">4.2%</span><span class="brand-delta up">+0.3</span></span>
                    </div>
                    <div class="brand-spark"><svg viewBox="0 0 120 26" preserveAspectRatio="none"><polyline points="0,22 24,19 48,17 72,14 96,12 120,8" fill="none" stroke="#1C4FC0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
                </div>
                <div class="brand-card">
                    <div class="card-top">
                        <span class="brand-name">Eliquis</span>
                        <span class="brand-metric"><span class="brand-value">62.1%</span><span class="brand-delta up">+1.2</span></span>
                    </div>
                    <div class="brand-spark"><svg viewBox="0 0 120 26" preserveAspectRatio="none"><polyline points="0,22 24,18 48,14 72,11 96,8 120,5" fill="none" stroke="#41B6E6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
                </div>
                <div class="brand-card">
                    <div class="card-top">
                        <span class="brand-name">Prevnar</span>
                        <span class="brand-metric"><span class="brand-value">48.7%</span><span class="brand-delta down">-0.5</span></span>
                    </div>
                    <div class="brand-spark"><svg viewBox="0 0 120 26" preserveAspectRatio="none"><polyline points="0,6 24,9 48,12 72,15 96,17 120,20" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
                </div>
            </div>

            <!-- Bottom row: 2 cards centered -->
            <div class="brand-cards-bottom">
                <div class="brand-card">
                    <div class="card-top">
                        <span class="brand-name">Comirnaty</span>
                        <span class="brand-metric"><span class="brand-value">35.4%</span><span class="brand-delta down">-2.1</span></span>
                    </div>
                    <div class="brand-spark"><svg viewBox="0 0 120 26" preserveAspectRatio="none"><polyline points="0,5 24,8 48,12 72,16 96,19 120,22" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
                </div>
                <div class="brand-card">
                    <div class="card-top">
                        <span class="brand-name">Abrysvo</span>
                        <span class="brand-metric"><span class="brand-value">18.9%</span><span class="brand-delta up">+3.4</span></span>
                    </div>
                    <div class="brand-spark"><svg viewBox="0 0 120 26" preserveAspectRatio="none"><polyline points="0,24 24,20 48,15 72,11 96,7 120,3" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
                </div>
            </div>
        </div>
    </main>
</div>

</div>
</body>
</html>
"""

st.components.v1.html(html_content, height=920, scrolling=False)
