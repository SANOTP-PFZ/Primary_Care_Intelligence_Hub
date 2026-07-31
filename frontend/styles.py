"""
Unified CSS for the Primary Care Intelligence Hub.
Glassmorphism design system matching the Migraine Intelligence Hub aesthetic.
"""


def get_global_css():
    """Return the complete CSS for the app."""
    return """
    <style>
    /* ═══════════════════════════════════════════════════════════════════════
       FONTS
       ═══════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* ═══════════════════════════════════════════════════════════════════════
       CSS VARIABLES
       ═══════════════════════════════════════════════════════════════════════ */
    :root {
        --navy-900: #0A1A3D;
        --navy-800: #0F2452;
        --navy-700: #162D5A;
        --slate-50: #F8FAFC;
        --slate-100: #F1F5F9;
        --slate-200: #E2E8F0;
        --slate-400: #94A3B8;
        --slate-600: #475569;
        --slate-800: #1E293B;
        --accent: #41B6E6;
        --accent-dark: #2196C3;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --border: rgba(15,23,42,0.08);
        --shadow-sm: 0 1px 3px rgba(15,23,42,0.04);
        --shadow-md: 0 4px 12px rgba(15,23,42,0.06);
        --shadow-lg: 0 8px 24px rgba(15,23,42,0.08);
        --radius: 12px;
        --radius-sm: 8px;
        --radius-lg: 16px;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       GLOBAL RESET
       ═══════════════════════════════════════════════════════════════════════ */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 50%, #F0F9FF 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .stApp > header { display: none !important; }

    /* Hide default Streamlit hamburger menu */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR STYLING (Glassmorphism)
       ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--navy-900) 0%, var(--navy-800) 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
        box-shadow: 4px 0 24px rgba(10,26,61,0.3) !important;
    }

    [data-testid="stSidebar"] * {
        color: rgba(255,255,255,0.85) !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        background: transparent !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 10px 16px !important;
        margin: 2px 0 !important;
        color: rgba(255,255,255,0.7) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
    }

    /* Active nav item */
    [data-testid="stSidebar"] .nav-active > button {
        background: rgba(65,182,230,0.15) !important;
        color: #41B6E6 !important;
        border-left: 3px solid #41B6E6 !important;
        font-weight: 600 !important;
    }

    /* Sidebar section headers */
    .sidebar-section-header {
        font-family: 'Manrope', sans-serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        color: rgba(255,255,255,0.4) !important;
        padding: 20px 16px 8px 16px !important;
        margin: 0 !important;
    }

    /* Sidebar logo area */
    .sidebar-logo {
        padding: 24px 20px 16px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 16px;
    }

    .sidebar-logo h2 {
        font-family: 'Manrope', sans-serif !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 8px 0 4px 0 !important;
        line-height: 1.3 !important;
    }

    .sidebar-logo p {
        font-size: 11px !important;
        color: rgba(255,255,255,0.5) !important;
        margin: 0 !important;
    }

    /* Sidebar footer */
    .sidebar-footer {
        padding: 16px 20px;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin-top: auto;
    }

    .sidebar-footer p {
        font-size: 11px !important;
        color: rgba(255,255,255,0.4) !important;
        margin: 2px 0 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       MAIN CONTENT AREA
       ═══════════════════════════════════════════════════════════════════════ */
    .main-header {
        background: rgba(255,255,255,0.7);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-sm);
    }

    .main-header h1 {
        font-family: 'Manrope', sans-serif !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        color: var(--navy-900) !important;
        margin: 0 0 4px 0 !important;
    }

    .main-header p {
        font-size: 14px;
        color: var(--slate-600);
        margin: 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       GLASSMORPHISM CARDS
       ═══════════════════════════════════════════════════════════════════════ */
    .glass-card {
        background: rgba(255,255,255,0.75);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 24px;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
        border-color: rgba(65,182,230,0.2);
    }

    /* Hero Card (top of home page) */
    .hero-card {
        background: rgba(255,255,255,0.8);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 32px;
        margin-bottom: 28px;
        box-shadow: var(--shadow-md);
        border-top: 3px solid;
        border-image: linear-gradient(90deg, var(--accent), #6366F1, #EC4899) 1;
    }

    .hero-card h2 {
        font-family: 'Manrope', sans-serif !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        color: var(--navy-900) !important;
        margin: 0 0 20px 0 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       KPI TILES
       ═══════════════════════════════════════════════════════════════════════ */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
    }

    .kpi-tile {
        background: rgba(255,255,255,0.6);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 16px 20px;
        text-align: center;
    }

    .kpi-tile .kpi-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--slate-400);
        margin-bottom: 6px;
    }

    .kpi-tile .kpi-value {
        font-family: 'Manrope', sans-serif;
        font-size: 22px;
        font-weight: 800;
        color: var(--navy-900);
    }

    .kpi-tile .kpi-sub {
        font-size: 12px;
        color: var(--slate-600);
        margin-top: 4px;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       BRAND CARDS (Home page grid)
       ═══════════════════════════════════════════════════════════════════════ */
    .brand-card {
        background: rgba(255,255,255,0.75);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .brand-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--card-accent, var(--accent));
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .brand-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-3px);
        border-color: rgba(65,182,230,0.2);
    }

    .brand-card:hover::before {
        opacity: 1;
    }

    .brand-card .brand-icon {
        font-size: 28px;
        margin-bottom: 12px;
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
        color: var(--slate-400);
        margin-bottom: 12px;
    }

    .brand-card .brand-kpi {
        font-family: 'Manrope', sans-serif;
        font-size: 18px;
        font-weight: 800;
        color: var(--navy-900);
    }

    .brand-card .brand-kpi-label {
        font-size: 11px;
        color: var(--slate-400);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       AGENT CARDS
       ═══════════════════════════════════════════════════════════════════════ */
    .agent-category-card {
        background: rgba(255,255,255,0.75);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 24px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .agent-category-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-3px);
    }

    .agent-category-card .category-icon {
        font-size: 32px;
        margin-bottom: 12px;
    }

    .agent-category-card .category-name {
        font-family: 'Manrope', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: var(--navy-900);
        margin-bottom: 6px;
    }

    .agent-category-card .category-desc {
        font-size: 13px;
        color: var(--slate-600);
        line-height: 1.5;
    }

    .agent-tag {
        display: inline-block;
        background: rgba(65,182,230,0.1);
        color: var(--accent-dark);
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        margin: 2px 4px 2px 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SECTION HEADERS
       ═══════════════════════════════════════════════════════════════════════ */
    .section-header {
        font-family: 'Manrope', sans-serif !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        color: var(--navy-900) !important;
        margin: 28px 0 16px 0 !important;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       BREADCRUMBS
       ═══════════════════════════════════════════════════════════════════════ */
    .breadcrumb {
        font-size: 13px;
        color: var(--slate-400);
        margin-bottom: 16px;
    }

    .breadcrumb a {
        color: var(--accent);
        text-decoration: none;
        font-weight: 500;
    }

    .breadcrumb span {
        margin: 0 6px;
        color: var(--slate-400);
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
        background: var(--slate-50);
    }

    .styled-table th {
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
        color: var(--slate-600);
        border-bottom: 2px solid var(--border);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .styled-table td {
        padding: 10px 12px;
        border-bottom: 1px solid var(--border);
        color: var(--slate-800);
    }

    .styled-table tbody tr:hover {
        background: rgba(65,182,230,0.04);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       CHART CONTAINERS
       ═══════════════════════════════════════════════════════════════════════ */
    .chart-container {
        background: rgba(255,255,255,0.75);
        backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 20px;
        margin-bottom: 20px;
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
        background: rgba(65,182,230,0.1);
        color: var(--accent-dark);
        border: 1px solid rgba(65,182,230,0.2);
        border-radius: var(--radius-sm);
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
    }

    .download-btn:hover {
        background: rgba(65,182,230,0.2);
        border-color: var(--accent);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       RESPONSIVE / UTILITY
       ═══════════════════════════════════════════════════════════════════════ */
    .mt-4 { margin-top: 16px; }
    .mt-6 { margin-top: 24px; }
    .mb-4 { margin-bottom: 16px; }
    .mb-6 { margin-bottom: 24px; }

    /* Streamlit element overrides */
    .stPlotlyChart {
        border-radius: var(--radius) !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        background: rgba(255,255,255,0.6) !important;
    }

    </style>
    """
