"""
Unified CSS for the Primary Care Intelligence Hub.
Glassmorphism design system aligned with the Migraine Intelligence Hub reference.
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
       CSS VARIABLES (matched to reference)
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
    }

    /* ═══════════════════════════════════════════════════════════════════════
       GLOBAL RESET
       ═══════════════════════════════════════════════════════════════════════ */
    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 0% 0%, rgba(28,79,192,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 70% 50% at 100% 0%, rgba(65,182,230,0.07) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 50% 100%, rgba(124,58,237,0.04) 0%, transparent 60%),
            var(--bg) !important;
        font-family: 'Inter', system-ui, -apple-system, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif !important;
        color: var(--text);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .stApp > header { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Remove top padding from main block so hero is top-aligned */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR STYLING (Frosted Glass Containerized Panel)
       ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.62) !important;
        backdrop-filter: saturate(180%) blur(22px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(22px) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: var(--panel-radius) !important;
        box-shadow: var(--shadow-panel) !important;
        margin: 10px !important;
        height: calc(100vh - 20px) !important;
        top: 10px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        border-radius: var(--panel-radius) !important;
        padding: 0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background: transparent !important;
        padding: 0 8px !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        background: transparent !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 9px 12px !important;
        margin: 1px 0 !important;
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

    /* Active nav item - gradient background + left border indicator */
    .nav-active + div .stButton > button,
    .nav-active > div .stButton > button,
    [data-testid="stSidebar"] .nav-active + div button {
        background: linear-gradient(90deg, rgba(28,79,192,0.10) 0%, rgba(28,79,192,0.04) 100%) !important;
        color: var(--navy-700) !important;
        font-weight: 600 !important;
        border-left: 3px solid transparent !important;
        border-image: linear-gradient(180deg, var(--navy-600), var(--accent)) 1 !important;
        box-shadow: 0 0 8px rgba(28,79,192,0.06) !important;
    }

    /* ─── Sidebar Brand (Containerized Button-style Title) ─── */
    .sidebar-brand {
        padding: 16px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(255,255,255,0.7);
        border: 1px solid var(--hairline);
        border-radius: 10px;
        margin: 12px 8px 8px;
        box-shadow: var(--shadow-xs);
        transition: box-shadow 0.18s var(--ease);
    }

    .sidebar-brand:hover {
        box-shadow: var(--shadow-sm);
    }

    .sidebar-brand-logo {
        height: 24px;
        width: auto;
        object-fit: contain;
        flex-shrink: 0;
    }

    .sidebar-brand-text {
        flex: 1;
        min-width: 0;
    }

    .sidebar-brand-title {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        font-size: 13px;
        color: var(--navy-900);
        line-height: 1.2;
        letter-spacing: -0.02em;
    }

    .sidebar-brand-subtitle {
        font-size: 10.5px;
        color: var(--text-muted);
        font-weight: 500;
        margin-top: 2px;
    }

    /* Collapse button styling - aligns with Streamlit's sidebar arrows */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
        top: 16px !important;
        right: 12px !important;
    }

    /* ─── Sidebar Section Headers ─── */
    .sidebar-section-header {
        font-family: 'Manrope', sans-serif !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.4px !important;
        color: var(--text-muted) !important;
        padding: 14px 12px 6px 12px !important;
        margin: 0 !important;
    }

    /* ─── Sidebar Divider ─── */
    .sidebar-divider {
        height: 1px;
        background: var(--hairline);
        margin: 4px 12px;
    }

    /* ─── Sidebar Spacer ─── */
    .sidebar-spacer {
        flex: 1;
        min-height: 40px;
    }

    /* ─── Sidebar Footer ─── */
    .sidebar-footer {
        padding: 12px 16px 16px;
        border-top: 1px solid var(--hairline);
        background: linear-gradient(180deg, transparent 0%, rgba(28,79,192,0.025) 100%);
        border-radius: 0 0 var(--panel-radius) var(--panel-radius);
    }

    .sidebar-footer p {
        font-size: 11px !important;
        color: var(--text-muted) !important;
        margin: 2px 0 !important;
        line-height: 1.55 !important;
    }

    .sidebar-footer strong {
        color: var(--text-soft) !important;
        font-weight: 600 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       MAIN CONTENT AREA (Glass Panel)
       ═══════════════════════════════════════════════════════════════════════ */
    section[data-testid="stMain"] {
        background: rgba(255,255,255,0.55) !important;
        backdrop-filter: saturate(180%) blur(14px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(14px) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: var(--panel-radius) !important;
        box-shadow: var(--shadow-panel) !important;
        margin: 10px 10px 10px 0 !important;
        overflow: hidden !important;
    }

    section[data-testid="stMain"] > div {
        max-width: 100%;
    }

    .main-header {
        background: rgba(255,255,255,0.7);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--hairline);
        border-radius: var(--radius-lg);
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-sm);
    }

    .main-header h1 {
        font-family: 'Manrope', sans-serif !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        color: var(--navy-900) !important;
        margin: 0 0 4px 0 !important;
        letter-spacing: -0.02em !important;
    }

    .main-header p {
        font-size: 13px;
        color: var(--text-muted);
        margin: 0;
        font-weight: 500;
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
        padding: 24px 24px 20px;
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
        margin-bottom: 20px;
    }

    .hero-title {
        font-family: 'Manrope', sans-serif !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        color: var(--navy-900) !important;
        letter-spacing: -0.025em !important;
        line-height: 1.15 !important;
        margin: 0 0 6px 0 !important;
    }

    .hero-subtitle {
        font-size: 13px;
        font-weight: 500;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 8px;
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
        gap: 6px;
        font-size: 11px;
        font-weight: 600;
        color: var(--navy-700);
        background: rgba(28,79,192,0.08);
        padding: 5px 12px;
        border-radius: var(--radius-sm);
        flex-shrink: 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       KPI TILES (Hero)
       ═══════════════════════════════════════════════════════════════════════ */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 12px;
    }

    .kpi-tile {
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(8px);
        border: 1px solid var(--hairline-2);
        border-radius: 12px;
        padding: 14px 16px 12px;
        transition: transform 0.25s var(--ease-out), box-shadow 0.25s var(--ease);
    }

    .kpi-tile:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .kpi-tile .kpi-label {
        font-size: 11px;
        color: var(--text-muted);
        font-weight: 500;
        margin-bottom: 4px;
    }

    .kpi-tile .kpi-value {
        font-family: 'Manrope', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: var(--navy-900);
        line-height: 1.1;
        letter-spacing: -0.02em;
        font-variant-numeric: tabular-nums;
        margin-bottom: 5px;
    }

    .kpi-tile .kpi-sub {
        font-size: 12px;
        color: var(--text-muted);
        margin-top: 2px;
    }

    .kpi-delta {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11.5px;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
    .kpi-delta.up { color: var(--up); }
    .kpi-delta.down { color: var(--down); }
    .kpi-delta.flat { color: var(--flat); }
    .kpi-delta .tri { font-size: 10px; line-height: 1; }
    .kpi-delta .vs { color: var(--text-muted); font-weight: 500; }

    /* ═══════════════════════════════════════════════════════════════════════
       GLASSMORPHISM CARDS
       ═══════════════════════════════════════════════════════════════════════ */
    .glass-card {
        background: rgba(255,255,255,0.75);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--hairline);
        border-radius: var(--radius);
        padding: 24px;
        box-shadow: var(--shadow-sm);
        transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease);
    }

    .glass-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-3px);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       BRAND / CONTENT CARDS (with icon chips + destination pills)
       ═══════════════════════════════════════════════════════════════════════ */
    .card {
        position: relative;
        display: flex;
        flex-direction: column;
        background: var(--surface);
        border-radius: var(--radius);
        padding: 18px 20px;
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

    .card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }

    .card:hover::after {
        opacity: 1;
    }

    .card-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }

    .icon-chip {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 18px;
    }

    .chip-blue { background: linear-gradient(135deg, #DBEAFE, #BFDBFE); }
    .chip-indigo { background: linear-gradient(135deg, #E0E7FF, #C7D2FE); }
    .chip-purple { background: linear-gradient(135deg, #EDE9FE, #DDD6FE); }
    .chip-cyan { background: linear-gradient(135deg, #CFFAFE, #A5F3FC); }
    .chip-green { background: linear-gradient(135deg, #DCFCE7, #BBF7D0); }
    .chip-rose { background: linear-gradient(135deg, #FCE7F3, #FBCFE8); }
    .chip-amber { background: linear-gradient(135deg, #FEF3C7, #FDE68A); }
    .chip-orange { background: linear-gradient(135deg, #FFEDD5, #FED7AA); }

    .card-title {
        font-family: 'Manrope', sans-serif;
        font-size: 15px;
        font-weight: 700;
        color: var(--navy-900);
        line-height: 1.25;
        margin-bottom: 5px;
    }

    .card-desc {
        font-size: 12.5px;
        color: var(--text-muted);
        line-height: 1.5;
        flex: 1;
        margin-bottom: 12px;
    }

    .dest-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        font-weight: 600;
        color: var(--text-soft);
        padding: 3px 9px;
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
        font-size: 9.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 3px 8px;
        border-radius: 5px;
        background: rgba(15,23,42,0.05);
        color: var(--text-muted);
    }
    .badge.weekly { background: rgba(16,185,129,0.12); color: #047857; }
    .badge.monthly { background: rgba(59,130,246,0.12); color: #1E40AF; }

    /* Legacy brand-card (backwards compat) */
    .brand-card {
        position: relative;
        display: flex;
        flex-direction: column;
        background: var(--surface);
        border-radius: var(--radius);
        padding: 18px 20px;
        min-height: 148px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease);
        cursor: pointer;
    }

    .brand-card::after {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        background: linear-gradient(135deg, rgba(255,255,255,0) 55%, rgba(65,182,230,0.05) 80%, rgba(28,79,192,0.07) 100%);
        opacity: 0;
        transition: opacity 0.28s var(--ease);
        pointer-events: none;
    }

    .brand-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }

    .brand-card:hover::after {
        opacity: 1;
    }

    .brand-card .brand-icon {
        font-size: 18px;
        margin-bottom: 10px;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #DBEAFE, #BFDBFE);
    }

    .brand-card .brand-name {
        font-family: 'Manrope', sans-serif;
        font-size: 15px;
        font-weight: 700;
        color: var(--navy-900);
        margin-bottom: 4px;
    }

    .brand-card .brand-market {
        font-size: 12px;
        color: var(--text-muted);
        margin-bottom: 12px;
        line-height: 1.5;
        flex: 1;
    }

    .brand-card .brand-kpi {
        font-family: 'Manrope', sans-serif;
        font-size: 18px;
        font-weight: 800;
        color: var(--navy-900);
    }

    .brand-card .brand-kpi-label {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        font-weight: 600;
        color: var(--text-soft);
        padding: 3px 9px;
        border-radius: 6px;
        background: rgba(15,23,42,0.05);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       AGENT CARDS
       ═══════════════════════════════════════════════════════════════════════ */
    .agent-category-card {
        position: relative;
        display: flex;
        flex-direction: column;
        background: var(--surface);
        border-radius: var(--radius);
        padding: 18px 20px;
        min-height: 148px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        transition: transform 0.28s var(--ease-out), box-shadow 0.28s var(--ease);
        cursor: pointer;
    }

    .agent-category-card::after {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        background: linear-gradient(135deg, rgba(255,255,255,0) 55%, rgba(124,58,237,0.05) 80%, rgba(28,79,192,0.07) 100%);
        opacity: 0;
        transition: opacity 0.28s var(--ease);
        pointer-events: none;
    }

    .agent-category-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }

    .agent-category-card:hover::after {
        opacity: 1;
    }

    .agent-category-card .category-icon {
        font-size: 18px;
        margin-bottom: 10px;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #EDE9FE, #DDD6FE);
    }

    .agent-category-card .category-name {
        font-family: 'Manrope', sans-serif;
        font-size: 15px;
        font-weight: 700;
        color: var(--navy-900);
        margin-bottom: 5px;
    }

    .agent-category-card .category-desc {
        font-size: 12.5px;
        color: var(--text-muted);
        line-height: 1.5;
        flex: 1;
    }

    .agent-tag {
        display: inline-block;
        background: rgba(65,182,230,0.1);
        color: #0E7490;
        font-size: 10.5px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 5px;
        margin: 2px 4px 2px 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SECTION HEADERS
       ═══════════════════════════════════════════════════════════════════════ */
    .section-header {
        font-family: 'Manrope', sans-serif !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        color: var(--navy-900) !important;
        letter-spacing: -0.02em !important;
        margin: 28px 0 6px 0 !important;
    }

    .section-desc {
        font-size: 13px;
        color: var(--text-muted);
        margin-bottom: 16px;
        max-width: 680px;
    }

    .workspace-divider {
        height: 1px;
        background: var(--hairline);
        margin: 20px 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       BREADCRUMBS
       ═══════════════════════════════════════════════════════════════════════ */
    .breadcrumb {
        font-size: 13px;
        color: var(--text-muted);
        margin-bottom: 16px;
    }

    .breadcrumb a {
        color: var(--navy-700);
        text-decoration: none;
        font-weight: 500;
    }

    .breadcrumb span {
        margin: 0 6px;
        color: var(--text-muted);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       DATA TABLES
       ═══════════════════════════════════════════════════════════════════════ */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        font-family: 'Inter', sans-serif;
    }

    .styled-table thead {
        background: var(--surface-2);
    }

    .styled-table th {
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
        color: var(--text-muted);
        border-bottom: 1px solid var(--hairline);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .styled-table td {
        padding: 10px 12px;
        border-bottom: 1px solid var(--hairline-2);
        color: var(--text-soft);
    }

    .styled-table tbody tr:hover {
        background: rgba(28,79,192,0.03);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       CHART CONTAINERS
       ═══════════════════════════════════════════════════════════════════════ */
    .chart-container {
        background: rgba(255,255,255,0.75);
        backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--hairline);
        border-radius: var(--radius);
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-xs);
    }

    .chart-container h3 {
        font-family: 'Manrope', sans-serif;
        font-size: 14px;
        font-weight: 700;
        color: var(--navy-900);
        margin: 0 0 16px 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       DOWNLOAD BUTTONS
       ═══════════════════════════════════════════════════════════════════════ */
    .download-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(28,79,192,0.06);
        color: var(--navy-700);
        border: 1px solid rgba(28,79,192,0.15);
        border-radius: var(--radius-sm);
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.18s var(--ease);
    }

    .download-btn:hover {
        background: rgba(28,79,192,0.12);
        border-color: rgba(28,79,192,0.3);
        box-shadow: var(--shadow-xs);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       STREAMLIT OVERRIDES
       ═══════════════════════════════════════════════════════════════════════ */
    .stPlotlyChart {
        border-radius: var(--radius) !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--hairline) !important;
        border-radius: var(--radius) !important;
        background: rgba(255,255,255,0.6) !important;
    }

    /* Hide Streamlit button borders in card areas */
    .brand-card + div .stButton > button,
    .agent-category-card + div .stButton > button {
        border: 1px solid var(--hairline) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--navy-700) !important;
        background: rgba(28,79,192,0.04) !important;
        padding: 6px 12px !important;
        margin-top: -8px !important;
    }

    .brand-card + div .stButton > button:hover,
    .agent-category-card + div .stButton > button:hover {
        background: rgba(28,79,192,0.10) !important;
        border-color: rgba(28,79,192,0.25) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       UTILITY
       ═══════════════════════════════════════════════════════════════════════ */
    .mt-4 { margin-top: 16px; }
    .mt-6 { margin-top: 24px; }
    .mb-4 { margin-bottom: 16px; }
    .mb-6 { margin-bottom: 24px; }

    </style>
    """
