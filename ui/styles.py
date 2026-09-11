"""
UI Styling & Custom CSS Injector
Provides executive-grade styling for KPI cards, metric indicators, badges, and layout aesthetics.
"""

import streamlit as st

def apply_custom_css():
    """Injects custom CSS to modernize the Streamlit interface."""
    st.markdown("""
        <style>
        /* Main background & fonts */
        .main {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        }
        
        /* Metric card styling */
        .kpi-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px 20px;
            color: #f8fafc;
            margin-bottom: 14px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            border-color: #3b82f6;
        }
        .kpi-title {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 6px;
            font-weight: 600;
        }
        .kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.2;
        }
        .kpi-sub {
            font-size: 0.78rem;
            color: #10b981;
            margin-top: 6px;
            display: flex;
            align-items: center;
        }
        .kpi-sub.negative {
            color: #ef4444;
        }
        
        /* Badges */
        .badge-sql {
            background-color: #0284c7;
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-rag {
            background-color: #7c3aed;
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-forecast {
            background-color: #ea580c;
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-hybrid {
            background-color: #059669;
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        /* Banner */
        .hero-banner {
            background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #1d4ed8;
            color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

def render_kpi(col, title: str, value: str, subtext: str = "", is_negative: bool = False):
    """Renders a custom HTML KPI metric card in a Streamlit column."""
    sub_class = "negative" if is_negative else ""
    col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {f'<div class="kpi-sub {sub_class}">{subtext}</div>' if subtext else ''}
        </div>
    """, unsafe_allow_html=True)
