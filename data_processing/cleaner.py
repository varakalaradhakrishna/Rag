"""
Data Cleaning and Sanitization Engine
Performs robust, transparent data cleaning, type conversions, and boundary enforcement.
Generates an explicit Data Cleaning & Quality Audit Report.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from utils.logging import logger

def clean_ecommerce_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw e-commerce DataFrame.
    
    Returns:
        (df_cleaned, cleaning_report)
    """
    total_raw_rows = len(df_raw)
    
    # 1. Normalize Column Names (standardize to PascalCase or TitleCase to match expected)
    df = df_raw.copy()
    col_dict = {col.lower(): col for col in df.columns}
    
    # Standard name mapping
    standard_cols = {
        "order_id": "Order_ID",
        "order_date": "Order_Date",
        "customer_id": "Customer_ID",
        "product_id": "Product_ID",
        "product_name": "Product_Name",
        "category": "Category",
        "brand": "Brand",
        "mrp": "MRP",
        "discount_percent": "Discount_Percent",
        "sale_price": "Sale_Price",
        "quantity": "Quantity",
        "revenue": "Revenue",
        "profit": "Profit",
        "state": "State",
        "city": "City",
        "payment_method": "Payment_Method",
        "rating": "Rating",
        "delivery_days": "Delivery_Days",
        "return_flag": "Return_Flag"
    }
    
    rename_map = {}
    for lower_name, std_name in standard_cols.items():
        if lower_name in col_dict:
            rename_map[col_dict[lower_name]] = std_name
            
    df = df.rename(columns=rename_map)
    
    # Track statistics
    invalid_rows_count = 0
    issues_found = []
    
    # 2. String Cleaning: Trim extra whitespace and normalize text
    string_cols = ["Order_ID", "Customer_ID", "Product_ID", "Product_Name", "Category", "Brand", "State", "City", "Payment_Method"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # Replace 'nan', 'none', 'null' with empty string or default
            df[col] = df[col].replace(['nan', 'None', 'null', 'NULL', 'NaN'], '')
            
    # Check empty Order_IDs or Product_Names
    if "Order_ID" in df.columns:
        empty_orders = df["Order_ID"] == ""
        if empty_orders.sum() > 0:
            issues_found.append(f"{empty_orders.sum()} rows missing Order_ID (dropped)")
            df = df[~empty_orders]
            
    # 3. Duplicate Detection within dataset
    initial_valid = len(df)
    df_dedup = df.drop_duplicates(subset=["Order_ID"], keep="first")
    internal_duplicates = initial_valid - len(df_dedup)
    if internal_duplicates > 0:
        issues_found.append(f"{internal_duplicates} internal duplicate Order_IDs detected")
    df = df_dedup
    
    # 4. Date Parsing
    if "Order_Date" in df.columns:
        df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
        invalid_dates = df["Order_Date"].isna()
        if invalid_dates.sum() > 0:
            issues_found.append(f"{invalid_dates.sum()} rows had unparseable Order_Date (filled with forward fill or now)")
            df["Order_Date"] = df["Order_Date"].ffill().bfill().fillna(pd.Timestamp.now())
        df["Order_Date"] = df["Order_Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
    # 5. Numeric Casting & Range Sanitization
    numeric_configs = {
        "MRP": (0.0, 1_000_000.0, 999.0),
        "Discount_Percent": (0.0, 99.0, 10.0),
        "Sale_Price": (0.0, 1_000_000.0, 899.0),
        "Quantity": (1, 100, 1),
        "Revenue": (0.0, 10_000_000.0, 899.0),
        "Profit": (-500_000.0, 500_000.0, 50.0),
        "Rating": (1.0, 5.0, 4.0),
        "Delivery_Days": (1, 30, 3),
        "Return_Flag": (0, 1, 0)
    }
    
    for col, (min_val, max_val, default_val) in numeric_configs.items():
        if col in df.columns:
            # Coerce to numeric
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # Count invalid
            nan_count = df[col].isna().sum()
            out_of_bounds = ((df[col] < min_val) | (df[col] > max_val)).sum()
            
            if nan_count > 0 or out_of_bounds > 0:
                issues_found.append(f"{col}: {nan_count} missing/non-numeric, {out_of_bounds} out-of-bounds sanitized")
                
            # Fill NaN with default
            df[col] = df[col].fillna(default_val)
            
            # Clip bounds
            df[col] = df[col].clip(lower=min_val, upper=max_val)
            
            # Integer conversion where appropriate
            if col in ["Quantity", "Delivery_Days", "Return_Flag"]:
                df[col] = df[col].astype(int)
            else:
                df[col] = df[col].round(2)
                
    # 6. Recalculate Revenue & Profit consistency if discrepancy detected
    if "Sale_Price" in df.columns and "Quantity" in df.columns and "Revenue" in df.columns:
        expected_revenue = (df["Sale_Price"] * df["Quantity"]).round(2)
        revenue_diff = (df["Revenue"] - expected_revenue).abs() > 1.0
        if revenue_diff.sum() > 0:
            issues_found.append(f"{revenue_diff.sum()} rows had revenue inconsistencies, synced to Sale_Price * Quantity")
            df.loc[revenue_diff, "Revenue"] = expected_revenue[revenue_diff]
            
    clean_rows_count = len(df)
    invalid_rows_count = total_raw_rows - clean_rows_count - internal_duplicates
    
    report = {
        "total_raw_rows": total_raw_rows,
        "valid_rows": initial_valid,
        "duplicate_rows": internal_duplicates,
        "invalid_rows": max(0, invalid_rows_count),
        "clean_rows": clean_rows_count,
        "issues_addressed": issues_found,
        "status": "CLEAN" if len(issues_found) == 0 else "SANITIZED_WITH_REPAIRS"
    }
    
    logger.info(f"Data cleaned. Total: {total_raw_rows}, Cleaned: {clean_rows_count}, Issues: {len(issues_found)}")
    return df, report
