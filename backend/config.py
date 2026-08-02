"""
Brand configuration and constants for Primary Care Intelligence Hub.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Brand Configuration
# ─────────────────────────────────────────────────────────────────────────────

BRAND_CONFIG = {
    "nurtec": {
        "display_name": "Nurtec ODT",
        "brand_key": "NURTEC",
        "market": "MIGRAINE",
        "market_display": "Migraine Acute Treatment Market",
        "source": "NPA",
        "icon": "Rx",
        "color": "#41B6E6",
        "chip": "chip-blue",
    },
    "eliquis": {
        "display_name": "Eliquis",
        "brand_key": "ELIQUIS",
        "market": "ORAL ANTICOAGULANTS",
        "market_display": "Oral Anticoagulants Market",
        "source": "NPA",
        "icon": "Rx",
        "color": "#6366F1",
        "chip": "chip-indigo",
    },
    "prevnar": {
        "display_name": "Prevnar Family",
        "brand_key": "PREVNAR",
        "market": "PNEUMOCOCCAL VACCINES",
        "market_display": "Pneumococcal Vaccine Market",
        "source": "DDD",
        "icon": "Vx",
        "color": "#10B981",
        "chip": "chip-green",
    },
    "comirnaty": {
        "display_name": "Comirnaty",
        "brand_key": "COMIRNATY",
        "market": "COVID VACCINES",
        "market_display": "COVID-19 Vaccine Market",
        "source": "DDD",
        "icon": "Vx",
        "color": "#F59E0B",
        "chip": "chip-amber",
    },
    "abrysvo": {
        "display_name": "Abrysvo",
        "brand_key": "ABRYSVO",
        "market": "RSV VACCINES",
        "market_display": "RSV Vaccine Market",
        "source": "DDD",
        "icon": "Vx",
        "color": "#EC4899",
        "chip": "chip-rose",
    },
    "paxlovid": {
        "display_name": "Paxlovid",
        "brand_key": "PAXLOVID",
        "market": "COVID TREATMENTS",
        "market_display": "COVID-19 Treatment Market",
        "source": "NPA",
        "icon": "Rx",
        "color": "#8B5CF6",
        "chip": "chip-purple",
    },
    "zavzpret": {
        "display_name": "Zavzpret",
        "brand_key": "ZAVZPRET",
        "market": "MIGRAINE",
        "market_display": "Migraine Acute Treatment Market",
        "source": "ELAAD",
        "icon": "Rx",
        "color": "#14B8A6",
        "chip": "chip-cyan",
    },
    "beyfortus": {
        "display_name": "Beyfortus",
        "brand_key": "BEYFORTUS",
        "market": "RSV PREVENTION",
        "market_display": "RSV Infant Prevention Market",
        "source": "ELAAD",
        "icon": "Ab",
        "color": "#F97316",
        "chip": "chip-orange",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Dataset Names (Dataiku)
# ─────────────────────────────────────────────────────────────────────────────

MASTER_DATASET = "SQL_EARNINGS_REPORT_MASTER_DATASET_SF"
MAX_DATE_DATASET = "SQL_NPA_MAX_DATE_SF"

# ─────────────────────────────────────────────────────────────────────────────
# Agent Hub Configuration
# ─────────────────────────────────────────────────────────────────────────────

AGENT_CATEGORIES = [
    {
        "id": "npa",
        "name": "NPA Analytics",
        "description": "New Prescription Analytics for branded drugs",
        "icon": "NPA",
        "color": "#41B6E6",
        "agents": [
            {
                "id": "npa_trx",
                "name": "NPA TRx Agent",
                "description": "Total prescriptions analysis and market share trends",
                "tags": ["TRx", "Market Share", "Trends"],
            },
            {
                "id": "npa_nbrx",
                "name": "NPA NBRx Agent",
                "description": "New-to-brand prescription analytics and conversion metrics",
                "tags": ["NBRx", "New Patients", "Conversion"],
            },
        ],
    },
    {
        "id": "ddd",
        "name": "DDD Shipments",
        "description": "Dose-level distribution and shipment analytics",
        "icon": "DDD",
        "color": "#10B981",
        "agents": [
            {
                "id": "ddd_shipment",
                "name": "DDD Shipment Agent",
                "description": "Vaccine shipment tracking and channel distribution",
                "tags": ["Shipments", "Channels", "Distribution"],
            },
            {
                "id": "ddd_retail",
                "name": "DDD Retail Agent",
                "description": "Retail vs non-retail market share analysis",
                "tags": ["Retail", "Non-Retail", "OA/MA"],
            },
        ],
    },
    {
        "id": "elaad",
        "name": "ELAAD Claims",
        "description": "Claims and patient-level analytics",
        "icon": "CLM",
        "color": "#8B5CF6",
        "agents": [
            {
                "id": "elaad_claims",
                "name": "ELAAD Claims Agent",
                "description": "Claims volume analysis and patient identification",
                "tags": ["Claims", "Patients", "Volume"],
            },
            {
                "id": "elaad_weekly",
                "name": "LAAD Weekly Agent",
                "description": "Weekly claims trends and seasonal patterns",
                "tags": ["Weekly", "Trends", "Seasonal"],
            },
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Design Tokens
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    "navy_900": "#0A1A3D",
    "navy_800": "#0F2452",
    "navy_700": "#162D5A",
    "slate_50": "#F8FAFC",
    "slate_100": "#F1F5F9",
    "accent": "#41B6E6",
    "accent_dark": "#2196C3",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "border": "rgba(15,23,42,0.08)",
    "shadow": "rgba(15,23,42,0.04)",
}
