"""
Database Seed and Bootstrapper
Loads initial synthetic dataset into SQLite database if empty.
"""

import os
import sys
from pathlib import Path

# Add project root to path for standalone execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.config import SAMPLE_DATA_DIR, DATABASE_PATH
from utils.logging import logger
from data_processing.loader import load_file_to_df
from data_processing.cleaner import clean_ecommerce_data
from data_processing.feature_engineering import apply_feature_engineering
from database.database import init_db, insert_sales_records, get_database_summary

def seed_initial_data_if_empty():
    """Checks if database is empty and loads initial BBD dataset."""
    init_db()
    summary = get_database_summary()
    
    if summary["total_records"] == 0:
        initial_csv = SAMPLE_DATA_DIR / "bbd_initial_sales_dataset.csv"
        if initial_csv.exists():
            logger.info(f"Seeding database with initial dataset from {initial_csv}...")
            df_raw, msg = load_file_to_df(str(initial_csv), "bbd_initial_sales_dataset.csv")
            if df_raw is not None:
                df_clean, report = clean_ecommerce_data(df_raw)
                df_enriched = apply_feature_engineering(df_clean)
                result = insert_sales_records(df_enriched, "bbd_initial_sales_dataset.csv")
                logger.info(f"Seed complete: {result}")
                return result
        else:
            logger.warning(f"Initial sample dataset not found at {initial_csv}")
    else:
        logger.info(f"Database already contains {summary['total_records']} records. Seeding skipped.")
    return None

if __name__ == "__main__":
    seed_initial_data_if_empty()
