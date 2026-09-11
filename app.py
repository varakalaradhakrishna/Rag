"""
BBD E-Commerce Sales Intelligence & AI Data Analyst
Main Streamlit Application Entrypoint
Single Unified Web Application with One URL
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# Streamlit Page Configuration - Must be first Streamlit command
st.set_page_config(
    page_title="BBD E-Commerce Sales Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize seed data and RAG documents if running for the first time
from database.seed import seed_initial_data_if_empty
from rag.rag_pipeline import seed_initial_documents_if_empty
from database.database import get_database_summary
from ui.styles import apply_custom_css

# Views
from ui.home import render_home
from ui.dashboard import render_dashboard
from ui.sales_view import render_sales_view
from ui.products_view import render_products_view
from ui.customers_view import render_customers_view
from ui.regional_view import render_regional_view
from ui.discounts_view import render_discounts_view
from ui.returns_view import render_returns_view
from ui.forecasting_view import render_forecasting_view
from ui.ai_view import render_ai_view
from ui.rag_view import render_rag_view
from ui.upload_view import render_upload_view
from ui.data_management_view import render_data_management_view
from ui.about_view import render_about_view

def initialize_application():
    """Runs one-time initialization for database and RAG repository."""
    if "app_initialized" not in st.session_state:
        seed_initial_data_if_empty()
        seed_initial_documents_if_empty()
        st.session_state["app_initialized"] = True

def main():
    initialize_application()
    apply_custom_css()
    
    # Sidebar Navigation
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 12px 0 16px 0;">
            <h2 style="margin: 0; color: #3b82f6; font-size: 1.4rem; font-weight: 800;">🛒 BBD Analytics</h2>
            <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #94a3b8;">Sales Intelligence & AI Data Analyst</p>
        </div>
    """, unsafe_allow_html=True)
    
    pages = {
        "🏠 Home": render_home,
        "📊 Dashboard": render_dashboard,
        "📈 Sales Analytics": render_sales_view,
        "📦 Product Analytics": render_products_view,
        "👥 Customer Analytics": render_customers_view,
        "🌎 Regional Analytics": render_regional_view,
        "💰 Profit & Discount Analysis": render_discounts_view,
        "🔄 Returns Analysis": render_returns_view,
        "🔮 Forecasting & Prediction": render_forecasting_view,
        "🤖 AI Data Analyst": render_ai_view,
        "📚 RAG Knowledge Base": render_rag_view,
        "📤 Upload New Data": render_upload_view,
        "🗄️ Data Management": render_data_management_view,
        "ℹ️ About Project": render_about_view,
    }
    
    selected_page = st.sidebar.radio(
        "Navigation",
        list(pages.keys()),
        label_visibility="collapsed"
    )
    
    # Quick database status badge in sidebar footer
    summary = get_database_summary()
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
        <div style="background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; font-size: 0.78rem; color: #94a3b8;">
            <div>💾 <b>Active Records</b>: {summary['total_records']:,}</div>
            <div>📂 <b>Upload Batches</b>: {summary['total_uploads']}</div>
            <div>🔄 <b>Sync Status</b>: Complete</div>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.caption("Pure Python • SQLite • RAG • ML")
    
    # Render the active page
    pages[selected_page]()

if __name__ == "__main__":
    main()
