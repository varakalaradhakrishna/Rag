"""
Returns and Reverse Logistics Analytics Module
Analyzes return frequency, category vulnerabilities, and reverse logistics revenue loss.
"""

import pandas as pd
from typing import Dict, Any

def get_return_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates overall return rate and financial loss from returned merchandise."""
    if df.empty or "return_flag" not in df.columns:
        return {
            "total_orders": 0,
            "returned_orders": 0,
            "return_rate": 0.0,
            "returned_revenue": 0.0,
            "retained_revenue": 0.0
        }
        
    total_orders = len(df)
    returned_orders = int(df["return_flag"].sum())
    return_rate = (returned_orders / total_orders * 100.0) if total_orders > 0 else 0.0
    
    returned_revenue = float(df[df["return_flag"] == 1]["revenue"].sum())
    total_revenue = float(df["revenue"].sum())
    retained_revenue = total_revenue - returned_revenue
    
    return {
        "total_orders": total_orders,
        "returned_orders": returned_orders,
        "return_rate": return_rate,
        "returned_revenue": returned_revenue,
        "retained_revenue": retained_revenue
    }

def get_returns_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Returns aggregated by product category."""
    if df.empty or "return_flag" not in df.columns:
        return pd.DataFrame()
        
    ret = df.groupby("category").agg(
        total_orders=("order_id", "count"),
        returned_orders=("return_flag", "sum"),
        returned_revenue=("revenue", lambda x: x[df.loc[x.index, "return_flag"] == 1].sum())
    ).reset_index()
    
    ret["return_rate"] = (ret["returned_orders"] / ret["total_orders"] * 100.0).round(2)
    return ret.sort_values("return_rate", ascending=False)

def get_returns_by_brand(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Returns aggregated by brand."""
    if df.empty or "return_flag" not in df.columns:
        return pd.DataFrame()
        
    ret = df.groupby("brand").agg(
        total_orders=("order_id", "count"),
        returned_orders=("return_flag", "sum"),
        total_revenue=("revenue", "sum")
    ).reset_index()
    
    # Filter brands with at least 20 orders for statistical validity
    ret_filtered = ret[ret["total_orders"] >= 20].copy()
    if ret_filtered.empty:
        ret_filtered = ret.copy()
        
    ret_filtered["return_rate"] = (ret_filtered["returned_orders"] / ret_filtered["total_orders"] * 100.0).round(2)
    return ret_filtered.sort_values("return_rate", ascending=False).head(top_n)

def get_returns_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """Returns aggregated by state."""
    if df.empty or "return_flag" not in df.columns:
        return pd.DataFrame()
        
    ret = df.groupby("state").agg(
        total_orders=("order_id", "count"),
        returned_orders=("return_flag", "sum"),
        total_revenue=("revenue", "sum")
    ).reset_index()
    
    ret["return_rate"] = (ret["returned_orders"] / ret["total_orders"] * 100.0).round(2)
    return ret.sort_values("return_rate", ascending=False)
