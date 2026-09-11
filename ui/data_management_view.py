"""
Data Management & Audit History View
Tracks database integrity, historical upload logs, and storage parameters.
"""

import streamlit as st
import pandas as pd
from database.database import get_database_summary, get_upload_history_df, get_connection
from utils.helpers import format_currency, format_number
from ui.styles import render_kpi

def render_data_management_view():
    st.title("🗄️ Database Management & Ingestion Audit")
    st.caption("Inspect central SQLite database metrics, comprehensive upload audit trails, and data schema health.")
    
    summary = get_database_summary()
    
    k1, k2, k3, k4 = st.columns(4)
    render_kpi(k1, "Total Valid Records", format_number(summary["total_records"]), "In SQLite Database")
    render_kpi(k2, "Total Ingestions", str(summary["total_uploads"]), "Audited Batches")
    render_kpi(k3, "Earliest Transaction", summary["min_date"].split()[0] if summary["min_date"] != "N/A" else "N/A", "Timeline Start")
    render_kpi(k4, "Latest Transaction", summary["max_date"].split()[0] if summary["max_date"] != "N/A" else "N/A", "Timeline End")
    
    st.markdown("---")
    
    st.subheader("📜 Complete Ingestion Audit Trail (`upload_history`)")
    hist_df = get_upload_history_df()
    
    if not hist_df.empty:
        disp_hist = hist_df.copy()
        disp_hist.columns = [
            "Upload ID", "File Name", "Timestamp", "Total Rows",
            "New Records Added", "Duplicates Skipped", "Invalid Rows", "Status"
        ]
        disp_hist["Total Rows"] = disp_hist["Total Rows"].apply(format_number)
        disp_hist["New Records Added"] = disp_hist["New Records Added"].apply(format_number)
        disp_hist["Duplicates Skipped"] = disp_hist["Duplicates Skipped"].apply(format_number)
        st.dataframe(disp_hist, use_container_width=True)
    else:
        st.info("No upload history entries recorded yet.")
        
    st.markdown("---")
    
    st.subheader("🗃️ Database Schema & Storage Specifications")
    st.markdown("""
    * **Storage Engine**: SQLite 3 with WAL (Write-Ahead Logging) compatibility.
    * **Primary Key**: `order_id` (Text GUID format enforcing record uniqueness).
    * **Indexes Applied**: `order_date`, `category`, `brand`, `state`, `customer_id`, `(year, month)`, `return_flag`.
    * **Deduplication Policy**: `Order_ID` lookup prior to ingestion. Historical transactions are permanently preserved.
    """)
    
    with st.expander("⚠️ Advanced Maintenance: Database Reset (Protected)", expanded=False):
        st.warning("Resetting the database clears transactions and restores the initial sample baseline. This action requires explicit confirmation.")
        confirm = st.checkbox("I understand and wish to re-seed the database with the initial dataset.")
        if confirm:
            if st.button("Re-Seed Database to Initial State", type="secondary"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sales")
                cursor.execute("DELETE FROM upload_history")
                conn.commit()
                conn.close()
                from database.seed import seed_initial_data_if_empty
                seed_initial_data_if_empty()
                st.success("Database successfully reset and re-seeded with initial clean records.")
                st.rerun()
