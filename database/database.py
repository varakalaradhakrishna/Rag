"""
Database Connection and Persistence Manager
Handles SQLite connection, schema creation, incremental append, and duplicate rejection.
"""

import sqlite3
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from datetime import datetime
import uuid

from utils.config import DATABASE_PATH
from utils.logging import logger
from database.schema import CREATE_SALES_TABLE, CREATE_UPLOAD_HISTORY_TABLE, CREATE_INDEXES

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    target_path = str(db_path or DATABASE_PATH)
    conn = sqlite3.connect(target_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the database schema and indexes."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(CREATE_SALES_TABLE)
        cursor.execute(CREATE_UPLOAD_HISTORY_TABLE)
        for idx_sql in CREATE_INDEXES:
            cursor.execute(idx_sql)
        conn.commit()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_existing_order_ids(conn: sqlite3.Connection) -> set:
    """Returns a set of all currently stored Order_IDs to detect duplicates."""
    cursor = conn.cursor()
    cursor.execute("SELECT order_id FROM sales")
    rows = cursor.fetchall()
    return {row[0] for row in rows}

def insert_sales_records(
    df: pd.DataFrame,
    filename: str,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Inserts sales records into the database with duplicate detection.
    NEVER deletes historical data.
    Preserves: OLD DATA + NEW DATA = COMPLETE DATA.
    
    Returns report dictionary with counts of new, duplicate, and total rows.
    """
    if df is None or df.empty:
        return {
            "success": False,
            "filename": filename,
            "total_rows": 0,
            "new_rows": 0,
            "duplicate_rows": 0,
            "invalid_rows": 0,
            "message": "Empty or null DataFrame provided."
        }
    
    init_db(db_path)
    conn = get_connection(db_path)
    upload_id = f"UPL-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    total_rows = len(df)
    new_rows_count = 0
    duplicate_rows_count = 0
    
    try:
        # Normalize column names to lowercase matching schema
        df_norm = df.copy()
        df_norm.columns = [col.lower() for col in df_norm.columns]
        
        # Check existing Order_IDs in the database
        existing_ids = get_existing_order_ids(conn)
        
        # Filter out duplicates
        is_duplicate = df_norm['order_id'].astype(str).isin(existing_ids)
        duplicate_rows_count = int(is_duplicate.sum())
        
        # Keep only new records and drop any internal duplicates inside the uploaded batch
        df_new = df_norm[~is_duplicate].drop_duplicates(subset=['order_id'], keep='first')
        internal_duplicates = (total_rows - duplicate_rows_count) - len(df_new)
        duplicate_rows_count += internal_duplicates
        
        new_rows_count = len(df_new)
        
        if new_rows_count > 0:
            # Reorder or select columns that exist in schema
            expected_cols = [
                'order_id', 'order_date', 'customer_id', 'product_id', 'product_name',
                'category', 'brand', 'mrp', 'discount_percent', 'sale_price', 'quantity',
                'revenue', 'profit', 'state', 'city', 'payment_method', 'rating',
                'delivery_days', 'return_flag', 'year', 'month', 'month_name', 'week',
                'day', 'day_name', 'quarter', 'revenue_per_item', 'discount_amount',
                'profit_margin', 'order_value', 'is_returned'
            ]
            
            # Select available columns
            valid_cols = [c for c in expected_cols if c in df_new.columns]
            df_to_insert = df_new[valid_cols]
            
            df_to_insert.to_sql('sales', conn, if_exists='append', index=False)
        
        # Log to upload history
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO upload_history (upload_id, filename, upload_timestamp, total_rows, new_rows, duplicate_rows, invalid_rows, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (upload_id, filename, timestamp, total_rows, new_rows_count, duplicate_rows_count, 0, "SUCCESS")
        )
        conn.commit()
        
        logger.info(f"Ingestion successful for {filename}: {new_rows_count} new, {duplicate_rows_count} duplicates.")
        
        return {
            "success": True,
            "upload_id": upload_id,
            "filename": filename,
            "timestamp": timestamp,
            "total_rows": total_rows,
            "new_rows": new_rows_count,
            "duplicate_rows": duplicate_rows_count,
            "invalid_rows": 0,
            "message": f"Successfully ingested {new_rows_count:,} new records. Skipped {duplicate_rows_count:,} duplicates."
        }
        
    except Exception as e:
        logger.error(f"Error inserting records: {e}")
        conn.rollback()
        return {
            "success": False,
            "filename": filename,
            "total_rows": total_rows,
            "new_rows": 0,
            "duplicate_rows": 0,
            "invalid_rows": total_rows,
            "message": f"Database insertion failed: {str(e)}"
        }
    finally:
        conn.close()

def query_sales_df(sql: str, params: tuple = (), db_path: Optional[str] = None) -> pd.DataFrame:
    """Executes a SQL query and returns a pandas DataFrame."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    finally:
        conn.close()

def get_database_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Returns total records, upload count, date ranges, and latest update."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*), MIN(order_date), MAX(order_date), SUM(revenue), SUM(profit) FROM sales")
        sales_stats = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*), MAX(upload_timestamp) FROM upload_history")
        upload_stats = cursor.fetchone()
        
        total_records = sales_stats[0] if sales_stats else 0
        min_date = sales_stats[1] if sales_stats and sales_stats[1] else "N/A"
        max_date = sales_stats[2] if sales_stats and sales_stats[2] else "N/A"
        total_revenue = sales_stats[3] if sales_stats and sales_stats[3] else 0.0
        total_profit = sales_stats[4] if sales_stats and sales_stats[4] else 0.0
        
        total_uploads = upload_stats[0] if upload_stats else 0
        latest_upload = upload_stats[1] if upload_stats and upload_stats[1] else "N/A"
        
        return {
            "total_records": total_records,
            "min_date": min_date,
            "max_date": max_date,
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "total_uploads": total_uploads,
            "latest_upload": latest_upload
        }
    finally:
        conn.close()

def get_upload_history_df(db_path: Optional[str] = None) -> pd.DataFrame:
    """Fetches full upload history as DataFrame."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        df = pd.read_sql_query(
            "SELECT upload_id, filename, upload_timestamp, total_rows, new_rows, duplicate_rows, invalid_rows, status FROM upload_history ORDER BY upload_timestamp DESC",
            conn
        )
        return df
    finally:
        conn.close()
