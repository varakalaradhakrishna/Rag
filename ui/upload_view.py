"""
New Data Ingestion & Deduplication View
Upload CSV/XLSX datasets with comprehensive validation, duplicate auditing, and cumulative persistence.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from data_processing.loader import load_file_to_df
from data_processing.validator import validate_dataset_structure
from data_processing.cleaner import clean_ecommerce_data
from data_processing.feature_engineering import apply_feature_engineering
from database.database import insert_sales_records, get_connection, get_existing_order_ids
from utils.config import SAMPLE_DATA_DIR
from utils.helpers import format_currency, format_number, format_percentage

def render_upload_view():
    st.title("📤 Upload New Sales Dataset")
    st.caption("Expand historical intelligence with new transaction batches (.csv, .xlsx). Strict deduplication guarantees zero data loss.")
    
    # Downloadable Sample Files for Testing Ingestion
    with st.expander("📥 Need Test Files? Download Verified Demo Batches", expanded=False):
        st.markdown("Download pre-generated test batches to test incremental upload and deduplication:")
        d_col1, d_col2 = st.columns(2)
        
        batch2_path = SAMPLE_DATA_DIR / "bbd_batch2_october_sales.csv"
        if batch2_path.exists():
            with open(batch2_path, "rb") as f:
                d_col1.download_button(
                    label="📄 Download Batch 2 (3,000 New CSV Records)",
                    data=f.read(),
                    file_name="bbd_batch2_october_sales.csv",
                    mime="text/csv"
                )
                
        batch3_path = SAMPLE_DATA_DIR / "bbd_batch3_with_duplicates.xlsx"
        if batch3_path.exists():
            with open(batch3_path, "rb") as f:
                d_col2.download_button(
                    label="📊 Download Batch 3 (1,500 XLSX - 500 Duplicates)",
                    data=f.read(),
                    file_name="bbd_batch3_with_duplicates.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file to upload",
        type=["csv", "xlsx", "xls"]
    )
    
    if uploaded_file is not None:
        filename = uploaded_file.name
        
        # Step 1: File Loading
        with st.spinner(f"Reading {filename}..."):
            df_raw, load_msg = load_file_to_df(uploaded_file, filename)
            
        if df_raw is None:
            st.error(load_msg)
            return
            
        st.success(f"File loaded successfully: **{format_number(len(df_raw))}** raw rows.")
        
        # Step 2: Schema Validation
        val_report = validate_dataset_structure(df_raw)
        
        if not val_report["is_valid"]:
            st.error(f"❌ Schema validation failed! Missing required columns: `{', '.join(val_report['missing_columns'])}`")
            return
            
        # Step 3: Data Cleaning & Feature Engineering
        with st.spinner("Sanitizing data and engineering analytical features..."):
            df_clean, clean_report = clean_ecommerce_data(df_raw)
            df_enriched = apply_feature_engineering(df_clean)
            
        # Step 4: Duplicate Detection against Database
        conn = get_connection()
        existing_ids = get_existing_order_ids(conn)
        conn.close()
        
        new_ids = df_enriched["Order_ID"].astype(str)
        is_dup = new_ids.isin(existing_ids)
        external_dup_count = int(is_dup.sum())
        new_records_count = len(df_enriched) - external_dup_count
        
        st.subheader("📋 Dataset Ingestion & Validation Audit")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows in File", format_number(clean_report["total_raw_rows"]))
        c2.metric("New Unique Records", format_number(new_records_count))
        c3.metric("Duplicates to Skip", format_number(external_dup_count + clean_report["duplicate_rows"]))
        c4.metric("Sanitized / Clean Rows", format_number(len(df_enriched)))
        
        if clean_report["issues_addressed"]:
            with st.expander("🛠️ Data Quality Adjustments Made", expanded=False):
                for issue in clean_report["issues_addressed"]:
                    st.markdown(f"- {issue}")
                    
        # Summary Preview
        st.markdown("##### 🔍 Batch Summary Preview")
        dt_col = pd.to_datetime(df_enriched["Order_Date"], errors="coerce")
        min_date = dt_col.min().strftime("%Y-%m-%d") if not dt_col.isna().all() else "N/A"
        max_date = dt_col.max().strftime("%Y-%m-%d") if not dt_col.isna().all() else "N/A"
        
        p1, p2, p3 = st.columns(3)
        p1.write(f"**Date Range**: {min_date} to {max_date}")
        p1.write(f"**Total Batch Revenue**: {format_currency(df_enriched['Revenue'].sum())}")
        p2.write(f"**Categories Count**: {df_enriched['Category'].nunique()} categories")
        p2.write(f"**Geographic Reach**: {df_enriched['State'].nunique()} states")
        p3.write(f"**Top Category**: {df_enriched['Category'].mode()[0] if not df_enriched.empty else 'N/A'}")
        p3.write(f"**Top Payment Mode**: {df_enriched['Payment_Method'].mode()[0] if not df_enriched.empty else 'N/A'}")
        
        st.markdown("##### 📄 Data Sample Preview")
        st.dataframe(df_enriched.head(5), use_container_width=True)
        
        st.markdown("---")
        
        # User Confirmation Button
        if new_records_count > 0:
            if st.button("✅ Confirm & Append to Historical Database", type="primary"):
                with st.spinner("Inserting new records and updating database indexes..."):
                    res = insert_sales_records(df_enriched, filename)
                    
                if res["success"]:
                    st.success(f"🎉 **Ingestion Successful!** Added **{format_number(res['new_rows'])}** new records. Skipped **{format_number(res['duplicate_rows'])}** duplicates.")
                    st.info("The central SQLite database, analytics dashboards, forecasting models, and AI analyst have automatically incorporated this new data.")
                    st.balloons()
                else:
                    st.error(f"Error during ingestion: {res['message']}")
        else:
            st.warning("⚠️ All records in this file already exist in the database. No new records to insert.")
