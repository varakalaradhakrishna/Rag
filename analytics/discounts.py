"""
Profit & Discount Analytics Module
Analyzes promotional elasticity, discount buckets, and margin erosion.
"""

import pandas as pd
import numpy as np

def get_discount_bucket_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups orders into discount tiers to analyze volume vs profitability.
    """
    if df.empty or "discount_percent" not in df.columns:
        return pd.DataFrame()
        
    bins = [0, 10, 20, 30, 40, 60, 100]
    labels = ["0-10%", "10-20%", "20-30%", "30-40%", "40-60%", "60%+"]
    
    df_temp = df.copy()
    df_temp["discount_bucket"] = pd.cut(
        df_temp["discount_percent"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )
    
    tier_summary = df_temp.groupby("discount_bucket", observed=False).agg(
        orders=("order_id", "count"),
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        units_sold=("quantity", "sum"),
        avg_discount=("discount_percent", "mean"),
        return_rate=("return_flag", lambda x: (x.sum() / len(x) * 100.0) if len(x) > 0 else 0)
    ).reset_index()
    
    tier_summary["profit_margin"] = (
        tier_summary["profit"] / tier_summary["revenue"].replace(0, np.nan) * 100.0
    ).fillna(0.0).round(2)
    
    return tier_summary

def get_category_discount_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Computes average discount, revenue, and margin by category."""
    if df.empty:
        return pd.DataFrame()
        
    matrix = df.groupby("category").agg(
        avg_discount=("discount_percent", "mean"),
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "count")
    ).reset_index()
    
    matrix["profit_margin"] = (matrix["profit"] / matrix["revenue"] * 100.0).round(2)
    return matrix.sort_values("avg_discount", ascending=False)
