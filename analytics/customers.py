"""
Customer Analytics and RFM Segmentation Module
Analyzes retention, purchase frequency, customer lifetime value, and RFM profiles.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def get_customer_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes high-level customer retention and value metrics."""
    if df.empty or "customer_id" not in df.columns:
        return {
            "total_unique_customers": 0,
            "repeat_customers": 0,
            "repeat_rate": 0.0,
            "avg_orders_per_customer": 0.0,
            "avg_revenue_per_customer": 0.0
        }
        
    cust_orders = df.groupby("customer_id")["order_id"].count()
    total_unique = len(cust_orders)
    repeat_count = int((cust_orders > 1).sum())
    repeat_rate = (repeat_count / total_unique * 100.0) if total_unique > 0 else 0.0
    avg_orders = float(cust_orders.mean()) if total_unique > 0 else 0.0
    
    total_rev = float(df["revenue"].sum())
    avg_rev = (total_rev / total_unique) if total_unique > 0 else 0.0
    
    return {
        "total_unique_customers": total_unique,
        "repeat_customers": repeat_count,
        "repeat_rate": repeat_rate,
        "avg_orders_per_customer": avg_orders,
        "avg_revenue_per_customer": avg_rev
    }

def get_rfm_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs RFM (Recency, Frequency, Monetary) customer segmentation.
    """
    if df.empty or "customer_id" not in df.columns:
        return pd.DataFrame()
        
    max_date = pd.to_datetime(df["order_date"]).max()
    
    rfm = df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (max_date - pd.to_datetime(x).max()).days),
        frequency=("order_id", "count"),
        monetary=("revenue", "sum"),
        profit=("profit", "sum")
    ).reset_index()
    
    # Quantile binning for RFM scoring (1-4 scale)
    try:
        # For recency, lower is better (inverted score)
        rfm["R_Score"] = pd.qcut(rfm["recency"].rank(method='first'), q=4, labels=[4, 3, 2, 1]).astype(int)
        rfm["F_Score"] = pd.qcut(rfm["frequency"].rank(method='first'), q=4, labels=[1, 2, 3, 4]).astype(int)
        rfm["M_Score"] = pd.qcut(rfm["monetary"].rank(method='first'), q=4, labels=[1, 2, 3, 4]).astype(int)
    except Exception:
        # Fallback if insufficient variance
        rfm["R_Score"] = 2
        rfm["F_Score"] = 2
        rfm["M_Score"] = 2
        
    rfm["RFM_Score"] = (rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"])
    
    def assign_segment(row):
        score = row["RFM_Score"]
        r = row["R_Score"]
        f = row["F_Score"]
        if score >= 10:
            return "Champions (High Value, Active)"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 3 and f < 3:
            return "Potential Loyalists"
        elif r < 2 and f >= 3:
            return "At Risk Customers"
        else:
            return "Hibernating / Needs Attention"
            
    rfm["Segment"] = rfm.apply(assign_segment, axis=1)
    return rfm

def get_top_customers(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Ranks top customers by total monetary spend."""
    if df.empty:
        return pd.DataFrame()
        
    cust = df.groupby("customer_id").agg(
        orders=("order_id", "count"),
        total_spent=("revenue", "sum"),
        total_profit=("profit", "sum"),
        avg_order_value=("revenue", "mean"),
        favorite_category=("category", lambda x: x.mode()[0] if not x.empty else "N/A")
    ).reset_index().sort_values("total_spent", ascending=False).head(top_n)
    
    return cust
