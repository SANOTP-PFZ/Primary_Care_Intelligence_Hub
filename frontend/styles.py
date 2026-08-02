"""
Unified CSS for the Primary Care Intelligence Hub.
Matches the Migraine Intelligence Hub reference: grid shell with two glass panels.
"""


def get_global_css():
    """Return the complete CSS for the app."""
    return """
    <style>
    /* ═══════════════════════════════════════════════════════════════════════
       FONTS
       ═══════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* ═══════════════════════════════════════════════════════════════════════
       CSS VARIABLES
       ═══════════════════════════════════════════════════════════════════════ */
    :root {
        --navy-900: #0A1A3D;
        --navy-800: #102A5C;
        --navy-700: #163990;
        --navy-600: #1C4FC0;
        --navy-500: #3B6FD9;
        --accent: #41B6E6;

        --bg: #EEF3FB;
        --bg-2: #E3EBF7;
        --surface: #FFFFFF;
        --surface-2: #F8FAFD;
        --text: #0F172A;
        --text-muted: #64748B;
        --text-soft: #475569;
        --hairline: rgba(15,23,42,0.08);
        --hairline-2: rgba(15,23,42,0.05);
        --up: #10B981;
        --down: #EF4444;
        --flat: #94A3B8;

        --shadow-xs: 0 1px 2px rgba(15,23,42,0.04);
        --shadow-sm: 0 2px 8px rgba(15,23,42,0.05), 0 1px 2px rgba(15,23,42,0.04);
        --shadow-md: 0 6px 16px rgba(15,23,42,0.07), 0 2px 4px rgba(15,23,42,0.04);
        --shadow-lg: 0 18px 40px rgba(15,23,42,0.10), 0 6px 12px rgba(15,23,42,0.06);
        --shadow-panel: 0 8px 24px rgba(15,23,42,0.07), 0 2px 6px rgba(15,23,42,0.04);

        --ease: cubic-bezier(0.4, 0, 0.2, 1);
        --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
        --panel-radius: 18px;
        --radius: 14px;
        --radius-sm: 8px;
        --radius-lg: 16px;
        --shell-pad: 10px;
        --sidebar-w: 250px;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       HIDE ALL STREAMLIT CHROME
       ═══════════════════════════════════════════════════════════════════════ */
    .stApp > header,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    #MainMenu,
    footer {
        display: none !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       APP SHELL (grid: sidebar | main)
       ═══════════════════════════════════════════════════════════════════════ */
    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.07) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 50% 100%, rgba(124,58,237,0.04) 0%, transparent 60%),
            var(--bg) !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        color: var(--text);
        -webkit-font-smoothing: antialiased;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR - Frosted Glass Panel
       ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.62) !important;
        backdrop-filter: saturate(180%) blur(22px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(22px) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: var(--panel-radius) !important;
        box-shadow: var(--shadow-panel) !important;
        margin: var(--shell-pad) 0 var(--shell-pad) var(--shell-pad) !important;
        height: calc(100vh - 2 * var(--shell-pad)) !important;
        top: var(--shell-pad) !important;
        left: var(--shell-pad) !important;
        width: var(--sidebar-w) !important;
        min-width: var(--sidebar-w) !important;
        max-width: var(--sidebar-w) !important;
        z-index: 10 !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding: 0 !important;
        height: 100% !important;
        border-radius: var(--panel-radius) !important;
        display: flex !important;
        flex-direction: column !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background: transparent !important;
        padding: 0 !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        flex: 1 !important;
    }

    /* Remove any extra spacing Streamlit adds above first element */
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
        gap: 0 !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR NAV BUTTONS
       ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        background: transparent !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 9px 12px !important;
        margin: 2px 4px !important;
        color: var(--text-soft) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: background 0.18s var(--ease), color 0.18s var(--ease) !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(15,23,42,0.04) !important;
        color: var(--text) !important;
    }

    /* Active state via marker */
    .nav-active-marker + div .stButton > button {
        background: linear-gradient(90deg, rgba(28,79,192,0.10) 0%, rgba(28,79,192,0.04) 100%) !important;
        color: var(--navy-700) !important;
        font-weight: 600 !important;
        border-left: 3px solid var(--navy-600) !important;
    }

    .nav-active-marker { display: none; }

    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR BRAND
       ═══════════════════════════════════════════════════════════════════════ */
    .sidebar-brand {
        padding: 10px 1rem 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        flex-shrink: 0;
    }

    .sidebar-brand-logo {
        height: 28px;
        width: auto;
        object-fit: contain;
        align-self: flex-start;
    }

    .sidebar-brand-title {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        font-size: 1.1rem;
        color: var(--navy-900);
        line-height: 1.18;
        letter-spacing: -0.025em;
    }

    .sidebar-brand-subtitle {
        font-size: 0.72rem;
        color: var(--text-muted);
        font-weight: 500;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR SECTION / DIVIDER / FOOTER
       ═══════════════════════════════════════════════════════════════════════ */
    .sidebar-divider {
        height: 1px;
        background: var(--hairline);
        margin: 0 0.85rem;
    }

    .sidebar-section-header {
        font-family: 'Manrope', sans-serif !important;
        font-size: 0.62rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        color: var(--text-muted) !important;
        padding: 0.95rem 1rem 0.4rem !important;
        margin: 0 !important;
    }

    .sidebar-footer {
        padding: 0.85rem 1rem 1rem;
        font-size: 0.7rem;
        color: var(--text-muted);
        line-height: 1.55;
        border-top: 1px solid var(--hairline);
        background: linear-gradient(180deg, transparent 0%, rgba(28,79,192,0.025) 100%);
        border-radius: 0 0 var(--panel-radius) var(--panel-radius);
        margin-top: auto !important;
    }

    .sidebar-footer p {
        font-size: 0.7rem !important;
        color: var(--text-muted) !important;
        margin: 2px 0 !important;
        line-height: 1.55 !important;
    }

    .sidebar-footer strong {
        color: var(--text-soft) !important;
        font-weight: 600 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       MAIN CONTENT - Frosted Glass Panel
       ═══════════════════════════════════════════════════════════════════════ */
    section[data-testid="stMain"] {
        background: rgba(255,255,255,0.55) !important;
        backdrop-filter: saturate(180%) blur(14px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(14px) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: var(--panel-radius) !important;
        box-shadow: var(--shadow-panel) !important;
        margin: var(--shell-pad) var(--shell-pad) var(--shell-pad) 0 !important;
        min-width: 0 !important;
        overflow: hidden !important;
    }

    .block-container {
        padding: 1.2rem 1.4rem !important;
        max-width: 100% !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       HERO BANNER
       ═══════════════════════════════════════════════════════════════════════ */
    .hero-card {
        position: relative;
        background:
            radial-gradient(ellipse 90% 80% at 20% 20%, rgba(28,79,192,0.06) 0%, transparent 50%),
            radial-gradient(ellipse 60% 70% at 80% 80%, rgba(65,182,230,0.05) 0%, transparent 50%),
            linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,253,0.95) 100%);
        border-radius: var(--radius-lg);
        padding: 1.6rem 1.6rem 1.3rem;
        border: 1px solid var(--hairline-2);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
        margin-bottom: 0;
    }

    .hero-card::before {
        content: '';
        position: absolute;
        top: -1px;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--navy-600), var(--accent), var(--navy-500));
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        opacity: 0.7;
    }

    .hero-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 1.2rem;
    }

    .hero-title {
        font-family: 'Manrope', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: var(--navy-900) !important;
        letter-spacing: -0.025em !important;
        line-height: 1.15 !important;
        margin: 0 0 0.3rem 0 !important;
    }

    .hero-subtitle {
        font-size: 0.82rem;
        font-weight: 500;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .hero-subtitle .dot {
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: var(--text-muted);
        opacity: 0.5;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.68rem;
        font-weight: 600;
        color: var(--navy-700);
        background: rgba(28,79,192,0.08);
        padding: 0.3rem 0.7rem;
        border-radius: var(--radius-sm);
        flex-shrink: 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       KPI TILES
       ═══════════════════════════════════════════════════════════════════════ */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.75rem;
    }

    .kpi-tile {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(8px);
        border: 1px solid var(--hairline-2);
        border-radius: 12px;
        padding: 0.75rem 0.9rem 0.7rem;
        transition: transform 0.25s var(--ease-out), box-shadow 0.25s var(--ease);
    }

    .kpi-tile:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .kpi-tile .kpi-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        font-weight: 500;
        margin-bottom: 0.2rem;
    }

    .kpi-tile .kpi-value {
        font-family: 'Manrope', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--navy-900);
        line-height: 1.1;
        letter-spacing: -0.02em;
        font-variant-numeric: tabular-nums;
        margin-bottom: 0.25rem;
    }

    .kpi-tile .kpi-sub {
        font-size: 0.7rem;
        color: var(--text-muted);
    }

    .kpi-delta {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.7rem;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
    .kpi-delta.up { color: var(--up); }
    .kpi-delta.down { color: var(--down); }
    .kpi-delta.flat { color: var(--flat); }
    .kpi-delta .tri { font-size: 0.6rem; line-height: 1; }
    .kpi-delta .vs { color: var(--text-muted); font-weight: 500; }

    /* ═══════════════════════════════════════════════════════════════════════
       WORKSPACE DIVIDER
       ═══════════════════════════════════════════════════════════════════════ */
    .workspace-divider {
        height: 1px;
        background: var(--hairline);
        margin: 1.2rem 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SECTION HEADERS
       ═══════════════════════════════════════════════════════════════════════ */
    .section-header {
        font-family: 'Manrope', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: var(--navy-900) !important;
        letter-spacing: -0.02em !important;
        margin: 0 0 0.2rem 0 !important;
    }

    .section-desc {
        font-size: 0.84rem;
        color: var(--text-muted);
        margin-bottom: 1rem;
        max-width: 680px;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       CARDS
       ═══════════════════════════════════════════════════════════════════════ */
    .card {
        position: relative;
        display: flex;
        flex-direction: column;
        background: var(--surface);
        border-radius: var(--radius);
        padding: 1rem 1.1rem;
        min-height: 148px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease);
        cursor: pointer;
    }

    .card::after {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        background: linear-gradient(135deg, rgba(255,255,255,0) 55%, rgba(65,182,230,0.05) 80%, rgba(28,79,192,0.07) 100%);
        opacity: 0;
        transition: opacity 0.28s var(--ease);
        pointer-events: none;
    }

    .card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
    .card:hover::after { opacity: 1; }

    .card-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.6rem;
    }

    .icon-chip {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 13px;
        font-weight: 700;
    }

    .chip-blue { background: linear-gradient(135deg, #DBEAFE, #BFDBFE); color: #1D4ED8; }
    .chip-indigo { background: linear-gradient(135deg, #E0E7FF, #C7D2FE); color: #4338CA; }
    .chip-purple { background: linear-gradient(135deg, #EDE9FE, #DDD6FE); color: #6D28D9; }
    .chip-cyan { background: linear-gradient(135deg, #CFFAFE, #A5F3FC); color: #0E7490; }
    .chip-green { background: linear-gradient(135deg, #DCFCE7, #BBF7D0); color: #047857; }
    .chip-rose { background: linear-gradient(135deg, #FCE7F3, #FBCFE8); color: #BE185D; }
    .chip-amber { background: linear-gradient(135deg, #FEF3C7, #FDE68A); color: #92400E; }
    .chip-orange { background: linear-gradient(135deg, #FFEDD5, #FED7AA); color: #C2410C; }

    .card-title {
        font-family: 'Manrope', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--navy-900);
        line-height: 1.25;
        margin-bottom: 0.25rem;
    }

    .card-desc {
        font-size: 0.78rem;
        color: var(--text-muted);
        line-height: 1.5;
        flex: 1;
        margin-bottom: 0.7rem;
    }

    .dest-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.68rem;
        font-weight: 600;
        color: var(--text-soft);
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        background: rgba(15,23,42,0.05);
        align-self: flex-start;
    }

    .dest-pill .swatch { font-size: 8px; line-height: 1; }
    .dest-tableau .swatch { color: #1F77B4; }
    .dest-ppt .swatch { color: #D24726; }
    .dest-xlsx .swatch { color: #107C41; }
    .dest-agent .swatch { color: #7C3AED; }
    .dest-doc .swatch { color: #475569; }

    .badge {
        font-size: 0.6rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        background: rgba(15,23,42,0.05);
        color: var(--text-muted);
    }
    .badge.weekly { background: rgba(16,185,129,0.12); color: #047857; }
    .badge.monthly { background: rgba(59,130,246,0.12); color: #1E40AF; }

    /* ═══════════════════════════════════════════════════════════════════════
       BRAND CARDS (legacy compat)
       ═══════════════════════════════════════════════════════════════════════ */
    .brand-card {
        position: relative;
        display: flex;
        flex-direction: column;
        background: var(--surface);
        border-radius: var(--radius);
        padding: 1rem 1.1rem;
        min-height: 148px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease);
        cursor: pointer;
    }
    .brand-card::after { content: ''; position: absolute; inset: 0; border-radius: inherit; background: linear-gradient(135deg, rgba(255,255,255,0) 55%, rgba(65,182,230,0.05) 80%, rgba(28,79,192,0.07) 100%); opacity: 0; transition: opacity 0.28s var(--ease); pointer-events: none; }
    .brand-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
    .brand-card:hover::after { opacity: 1; }

    /* ═══════════════════════════════════════════════════════════════════════
       AGENT CARDS
       ═══════════════════════════════════════════════════════════════════════ */
    .agent-category-card {
        position: relative;
        display: flex;
        flex-direction: column;
        background: var(--surface);
        border-radius: var(--radius);
        padding: 1rem 1.1rem;
        min-height: 148px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease);
        cursor: pointer;
    }
    .agent-category-card::after { content: ''; position: absolute; inset: 0; border-radius: inherit; background: linear-gradient(135deg, rgba(255,255,255,0) 55%, rgba(124,58,237,0.05) 80%, rgba(28,79,192,0.07) 100%); opacity: 0; transition: opacity 0.28s var(--ease); pointer-events: none; }
    .agent-category-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
    .agent-category-card:hover::after { opacity: 1; }

    .agent-tag {
        display: inline-block;
        background: rgba(65,182,230,0.1);
        color: #0E7490;
        font-size: 10px;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: 5px;
        margin: 2px 3px 2px 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       MAIN HEADER (brand pages)
       ═══════════════════════════════════════════════════════════════════════ */
    .main-header {
        background: rgba(255,255,255,0.7);
        backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--hairline);
        border-radius: var(--radius-lg);
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: var(--shadow-sm);
    }

    .main-header h1 {
        font-family: 'Manrope', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: var(--navy-900) !important;
        margin: 0 0 0.2rem 0 !important;
        letter-spacing: -0.02em !important;
    }

    .main-header p {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin: 0;
        font-weight: 500;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       BREADCRUMBS
       ═══════════════════════════════════════════════════════════════════════ */
    .breadcrumb {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin-bottom: 1rem;
    }
    .breadcrumb a { color: var(--navy-700); text-decoration: none; font-weight: 500; }
    .breadcrumb span { margin: 0 6px; color: var(--text-muted); }

    /* ═══════════════════════════════════════════════════════════════════════
       DATA TABLES
       ═══════════════════════════════════════════════════════════════════════ */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        font-family: 'Inter', sans-serif;
    }
    .styled-table thead { background: var(--surface-2); }
    .styled-table th { padding: 0.6rem 0.75rem; text-align: left; font-weight: 600; color: var(--text-muted); border-bottom: 1px solid var(--hairline); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; }
    .styled-table td { padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--hairline-2); color: var(--text-soft); }
    .styled-table tbody tr:hover { background: rgba(28,79,192,0.03); }

    /* ═══════════════════════════════════════════════════════════════════════
       CHART CONTAINERS
       ═══════════════════════════════════════════════════════════════════════ */
    .chart-container {
        background: rgba(255,255,255,0.75);
        backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--hairline);
        border-radius: var(--radius);
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-xs);
    }

    .chart-container h3 {
        font-family: 'Manrope', sans-serif;
        font-size: 0.88rem;
        font-weight: 700;
        color: var(--navy-900);
        margin: 0 0 1rem 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       DOWNLOAD BUTTONS
       ═══════════════════════════════════════════════════════════════════════ */
    .download-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(28,79,192,0.06);
        color: var(--navy-700);
        border: 1px solid rgba(28,79,192,0.15);
        border-radius: var(--radius-sm);
        padding: 0.5rem 1rem;
        font-size: 0.82rem;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.18s var(--ease);
    }
    .download-btn:hover { background: rgba(28,79,192,0.12); border-color: rgba(28,79,192,0.3); }

    /* ═══════════════════════════════════════════════════════════════════════
       STREAMLIT ELEMENT OVERRIDES
       ═══════════════════════════════════════════════════════════════════════ */
    .stPlotlyChart { border-radius: var(--radius) !important; }

    div[data-testid="stExpander"] {
        border: 1px solid var(--hairline) !important;
        border-radius: var(--radius) !important;
        background: rgba(255,255,255,0.6) !important;
    }

    /* Card action buttons */
    .card + div .stButton > button,
    .brand-card + div .stButton > button,
    .agent-category-card + div .stButton > button {
        border: 1px solid var(--hairline) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--navy-700) !important;
        background: rgba(28,79,192,0.04) !important;
        padding: 0.4rem 0.75rem !important;
    }

    </style>
    """
