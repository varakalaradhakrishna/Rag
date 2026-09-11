"""
Feature Engineering Engine
Computes derived temporal, financial, and behavioral analytical features.
"""

import pandas as pd
import numpy as np

def apply_feature_engineering(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches dataset with time-based attributes and business KPIs.
    """
    df = df_in.copy()
    
    # 1. Temporal Features
    if "Order_Date" in df.columns:
        dt = pd.to_datetime(df["Order_Date"], errors="coerce")
        df["Year"] = dt.dt.year.fillna(2025).astype(int)
        df["Month"] = dt.dt.month.fillna(1).astype(int)
        df["Month_Name"] = dt.dt.strftime("%B").fillna("Unknown")
        df["Week"] = dt.dt.isocalendar().week.fillna(1).astype(int)
        df["Day"] = dt.dt.day.fillna(1).astype(int)
        df["Day_Name"] = dt.dt.strftime("%A").fillna("Unknown")
        df["Quarter"] = dt.dt.quarter.fillna(1).astype(int)
    else:
        for col in ["Year", "Month", "Week", "Day", "Quarter"]:
            df[col] = 1
        df["Month_Name"] = "Unknown"
        df["Day_Name"] = "Unknown"
        
    # 2. Financial Metrics
    # Revenue Per Item = Revenue / Quantity (safe division)
    qty = df["Quantity"].replace(0, 1) if "Quantity" in df.columns else 1
    rev = df["Revenue"] if "Revenue" in df.columns else 0.0
    df["Revenue_Per_Item"] = (rev / qty).round(2)
    
    # Discount Amount = (MRP * Discount_Percent / 100) * Quantity
    mrp = df["MRP"] if "MRP" in df.columns else 0.0
    disc_pct = df["Discount_Percent"] if "Discount_Percent" in df.columns else 0.0
    df["Discount_Amount"] = ((mrp * disc_pct / 100.0) * qty).round(2)
    
    # Profit Margin = (Profit / Revenue) * 100
    profit = df["Profit"] if "Profit" in df.columns else 0.0
    safe_rev = rev.replace(0, np.nan)
    df["Profit_Margin"] = ((profit / safe_rev) * 100.0).fillna(0.0).round(2)
    
    # Order Value = Revenue
    df["Order_Value"] = rev.round(2)
    
    # Is_Returned = Return_Flag
    if "Return_Flag" in df.columns:
        df["Is_Returned"] = df["Return_Flag"].astype(int)
    else:
        df["Is_Returned"] = 0
        
    return df
