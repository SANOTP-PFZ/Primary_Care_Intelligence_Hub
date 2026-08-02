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

/* MAIN PANEL HEADER */
.section-header {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--navy-900);
    margin-bottom: 0.3rem;
}
.section-subtitle {
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 500;
    margin-bottom: 1.2rem;
}

/* CHART CARDS GRID */
.chart-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.9rem;
}
.chart-grid .chart-card:nth-child(n+4) {
    grid-column: span 1;
}
.chart-grid-bottom {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.9rem;
    margin-top: 0.9rem;
    max-width: 66.66%;
    margin-left: auto;
    margin-right: auto;
}
.chart-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: saturate(160%) blur(12px);
    -webkit-backdrop-filter: saturate(160%) blur(12px);
    border: 1px solid var(--hairline);
    border-radius: 12px;
    padding: 1rem 1rem 0.6rem;
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    transition: box-shadow 0.2s var(--ease), transform 0.2s var(--ease);
}
.chart-card:hover {
    box-shadow: 0 6px 16px rgba(15,23,42,0.08);
    transform: translateY(-1px);
}
.card-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}
.card-brand {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 0.82rem;
    color: var(--navy-900);
}
.card-value {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 1.05rem;
    color: var(--text);
}
.card-delta {
    font-size: 0.68rem;
    font-weight: 600;
    margin-left: 0.4rem;
}
.card-delta.up { color: #10B981; }
.card-delta.down { color: #EF4444; }
.chart-canvas { width: 100%; height: 90px; }
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
        <div class="section-subtitle">TRx Trend | 2024 Q1 onwards (dummy data)</div>

        <!-- Top row: 3 cards -->
        <div class="chart-grid">
            <div class="chart-card">
                <div class="card-header">
                    <span class="card-brand">Nurtec</span>
                    <span><span class="card-value">4.2%</span><span class="card-delta up">+0.3</span></span>
                </div>
                <canvas class="chart-canvas" id="chart-nurtec"></canvas>
            </div>
            <div class="chart-card">
                <div class="card-header">
                    <span class="card-brand">Eliquis</span>
                    <span><span class="card-value">62.1%</span><span class="card-delta up">+1.2</span></span>
                </div>
                <canvas class="chart-canvas" id="chart-eliquis"></canvas>
            </div>
            <div class="chart-card">
                <div class="card-header">
                    <span class="card-brand">Prevnar</span>
                    <span><span class="card-value">48.7%</span><span class="card-delta down">-0.5</span></span>
                </div>
                <canvas class="chart-canvas" id="chart-prevnar"></canvas>
            </div>
        </div>

        <!-- Bottom row: 2 cards centered -->
        <div class="chart-grid-bottom">
            <div class="chart-card">
                <div class="card-header">
                    <span class="card-brand">Comirnaty</span>
                    <span><span class="card-value">35.4%</span><span class="card-delta down">-2.1</span></span>
                </div>
                <canvas class="chart-canvas" id="chart-comirnaty"></canvas>
            </div>
            <div class="chart-card">
                <div class="card-header">
                    <span class="card-brand">Abrysvo</span>
                    <span><span class="card-value">18.9%</span><span class="card-delta up">+3.4</span></span>
                </div>
                <canvas class="chart-canvas" id="chart-abrysvo"></canvas>
            </div>
        </div>
    </main>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
const labels = ['2024 Q1','2024 Q2','2024 Q3','2024 Q4','2025 Q1','2025 Q2'];

const brandData = {
    nurtec:    { data: [3.1, 3.4, 3.6, 3.8, 3.9, 4.2], color: '#1C4FC0' },
    eliquis:   { data: [58.2, 59.1, 60.0, 60.8, 61.5, 62.1], color: '#41B6E6' },
    prevnar:   { data: [51.2, 50.8, 50.1, 49.5, 49.1, 48.7], color: '#7C3AED' },
    comirnaty: { data: [42.0, 40.5, 38.8, 37.2, 36.1, 35.4], color: '#10B981' },
    abrysvo:   { data: [8.2, 10.5, 13.1, 15.5, 17.2, 18.9], color: '#F59E0B' }
};

function createChart(canvasId, brand) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const d = brandData[brand];
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: d.data,
                borderColor: d.color,
                backgroundColor: d.color + '18',
                borderWidth: 2.2,
                tension: 0.35,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 4,
                pointHoverBackgroundColor: d.color
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0F172A',
                    titleFont: { family: 'Inter', size: 11 },
                    bodyFont: { family: 'Inter', size: 11 },
                    padding: 8,
                    cornerRadius: 6,
                    callbacks: { label: function(ctx) { return ctx.parsed.y.toFixed(1) + '%'; } }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: { display: false },
                    ticks: { font: { family: 'Inter', size: 9 }, color: '#94A3B8', maxRotation: 0 }
                },
                y: {
                    display: true,
                    grid: { color: 'rgba(15,23,42,0.04)', drawBorder: false },
                    ticks: { font: { family: 'Inter', size: 9 }, color: '#94A3B8', callback: function(v) { return v + '%'; } }
                }
            }
        }
    });
}

createChart('chart-nurtec', 'nurtec');
createChart('chart-eliquis', 'eliquis');
createChart('chart-prevnar', 'prevnar');
createChart('chart-comirnaty', 'comirnaty');
createChart('chart-abrysvo', 'abrysvo');
</script>

</div>
</body>
</html>
"""

st.components.v1.html(html_content, height=920, scrolling=False)
