import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── App Header ── */
    .app-header {
        background: linear-gradient(135deg, #1e3d59 0%, #2d6a9f 100%);
        color: white;
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(30,61,89,0.2);
    }
    .app-header h1 { font-size: 1.65rem; font-weight: 700; margin: 0; line-height: 1.3; }
    .app-header p  { font-size: 0.88rem; margin: 0.35rem 0 0 0; opacity: 0.82; }

    /* ── Section title ── */
    .section-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1e3d59;
        border-left: 4px solid #1e3d59;
        padding-left: 0.75rem;
        margin: 1.2rem 0 0.75rem 0;
    }

    /* ── Info box ── */
    .info-box {
        background: #eef4ff;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        border-left: 4px solid #3b82f6;
        font-size: 0.875rem;
        color: #374151;
        margin-bottom: 1rem;
        line-height: 1.55;
    }

    /* ── Result cards (individual prediction) ── */
    .result-danger {
        background: linear-gradient(135deg, #b91c1c, #ef4444);
        border-radius: 12px; padding: 1.8rem; color: white;
        text-align: center; box-shadow: 0 4px 18px rgba(185,28,28,0.3);
    }
    .result-warning {
        background: linear-gradient(135deg, #c2410c, #f97316);
        border-radius: 12px; padding: 1.8rem; color: white;
        text-align: center; box-shadow: 0 4px 18px rgba(194,65,12,0.3);
    }
    .result-safe {
        background: linear-gradient(135deg, #166534, #22c55e);
        border-radius: 12px; padding: 1.8rem; color: white;
        text-align: center; box-shadow: 0 4px 18px rgba(22,101,52,0.3);
    }
    .result-card-value { font-size: 3rem; font-weight: 700; margin: 0.4rem 0; line-height: 1; }
    .result-card-title { font-size: 1.05rem; font-weight: 600; margin: 0 0 0.4rem 0; opacity: 0.92; }
    .result-card-sub   { font-size: 0.82rem; opacity: 0.82; margin-top: 0.4rem; }

    /* ── Buttons ── */
    .stButton > button {
        background: #1e3d59 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.45rem 1.4rem !important;
        transition: background 0.2s !important;
    }
    .stButton > button:hover { background: #2d6a9f !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: #f1f5f9;
        border-radius: 8px;
        padding: 3px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #64748b;
        font-weight: 500;
        font-size: 0.875rem;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #1e3d59 !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
    }

    /* ── Sidebar ── */
    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin: 1rem 0 0.4rem 0;
    }
    .sidebar-metric {
        background: #f8fafc;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.35rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
    }
    .sidebar-metric-label { color: #64748b; }
    .sidebar-metric-value { color: #1e3d59; font-weight: 700; }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Custom footer ── */
    .custom-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.78rem;
        border-top: 1px solid #f1f5f9;
        padding-top: 1.5rem;
        margin-top: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)
