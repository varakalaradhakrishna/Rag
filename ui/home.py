"""
Home Page View
Showcases the platform overview, key metrics, architectural highlights, and quick navigation.
"""

import streamlit as st
import pandas as pd
from database.database import get_database_summary, query_sales_df
from utils.helpers import format_currency, format_number, format_percentage
from ui.styles import render_kpi

def render_home():
    st.markdown("""
        <div class="hero-banner">
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800;">🛒 BBD E-Commerce Sales Intelligence & AI Data Analyst</h1>
            <p style="margin-top: 8px; font-size: 1.05rem; opacity: 0.9;">
                A comprehensive Python-based enterprise intelligence platform uniting multi-dimensional sales analytics,
                persistent cumulative data ingestion, machine learning time-series forecasting, and an evidence-grounded RAG AI Data Analyst.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    summary = get_database_summary()
    
    # KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)
    render_kpi(k1, "Total Revenue", format_currency(summary["total_revenue"]), "Historical GMV")
    render_kpi(k2, "Net Profit", format_currency(summary["total_profit"]), "Blended Net Margin")
    render_kpi(k3, "Total Orders", format_number(summary["total_records"]), "Completed Transactions")
    render_kpi(k4, "Total Datasets", str(summary["total_uploads"]), "Audited Batches")
    render_kpi(k5, "Last Data Update", summary["latest_upload"].split()[0] if summary["latest_upload"] != "N/A" else "Initial Seed", "Synced to Central DB")
    
    st.markdown("---")
    
    # Core Capabilities & Architecture Columns
    c1, c2 = st.columns([1.1, 0.9])
    
    with c1:
        st.subheader("⚡ Core Capabilities")
        st.markdown("""
        * **100% Python Architecture**: Pure Python backend and frontend with Streamlit, SQLite, Pandas, and Scikit-Learn.
        * **Cumulative Data Ingestion**: When new CSV or Excel files are uploaded, **OLD DATA + NEW DATA = COMPLETE DATA**. Duplicates are automatically detected and rejected using `Order_ID`.
        * **Full-Spectrum Business Analytics**: In-depth analysis across Sales velocity, Product margins, Customer RFM profiles, Regional penetration, Discounts, and Reverse Logistics.
        * **ML Multi-Horizon Forecasting**: Time-series models (Random Forest, Gradient Boosting, Ridge) predicting 7, 30, 60, and 90-day future demand and revenue.
        * **RAG Business Knowledge Base**: Vector database indexing official PDF/TXT business documents (return policies, pricing guides, market reports).
        * **Unified AI Data Analyst**: An intelligent agent with intent classification routing queries across SQL database facts, RAG documents, and ML forecasts without numerical hallucinations.
        """)
        
    with c2:
        st.subheader("📌 Quick Start Navigation")
        st.info("Select any module from the left sidebar to begin exploring:")
        
        q_cols = st.columns(2)
        with q_cols[0]:
            st.markdown("- **📊 Dashboard**: Executive KPI cockpit")
            st.markdown("- **📈 Sales Analytics**: Trends & channels")
            st.markdown("- **📦 Product Analytics**: Top SKUs & ratings")
            st.markdown("- **👥 Customer Analytics**: RFM loyalty")
        with q_cols[1]:
            st.markdown("- **🔮 Forecasting**: 7-90 day ML projections")
            st.markdown("- **🤖 AI Data Analyst**: Ask natural language questions")
            st.markdown("- **📤 Upload New Data**: Ingest new CSV/XLSX")
            st.markdown("- **📚 RAG Knowledge Base**: Upload PDFs/TXTs")
            
        st.caption("ℹ️ *Notice: The initial dataset contains synthetic e-commerce transactions modeled on Big Billion Days consumer patterns.*")
