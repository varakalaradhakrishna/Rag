"""
Sales Analytics Module
Aggregates sales trends across temporal horizons, categories, brands, and payment modes.
"""

import pandas as pd
from typing import Dict, Any, Optional

def get_overall_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates top-level KPI summary cards."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "total_orders": 0,
            "total_quantity": 0,
            "avg_order_value": 0.0,
            "avg_discount": 0.0,
            "return_rate": 0.0,
            "avg_rating": 0.0,
            "profit_margin": 0.0
        }
        
    total_orders = len(df)
    total_revenue = float(df["revenue"].sum())
    total_profit = float(df["profit"].sum())
    total_quantity = int(df["quantity"].sum())
    avg_order_value = float(df["revenue"].mean()) if total_orders > 0 else 0.0
    avg_discount = float(df["discount_percent"].mean()) if total_orders > 0 else 0.0
    
    returned_count = int(df["return_flag"].sum())
    return_rate = (returned_count / total_orders * 100.0) if total_orders > 0 else 0.0
    avg_rating = float(df["rating"].mean()) if total_orders > 0 else 0.0
    profit_margin = (total_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0
    
    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "avg_order_value": avg_order_value,
        "avg_discount": avg_discount,
        "return_rate": return_rate,
        "avg_rating": avg_rating,
        "profit_margin": profit_margin
    }

def get_daily_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates revenue, profit, and order count by day."""
    if df.empty or "order_date" not in df.columns:
        return pd.DataFrame()
        
    df_temp = df.copy()
    df_temp["date"] = pd.to_datetime(df_temp["order_date"]).dt.date
    
    trend = df_temp.groupby("date").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "count"),
        quantity=("quantity", "sum")
    ).reset_index().sort_values("date")
    
    trend["date"] = pd.to_datetime(trend["date"])
    return trend

def get_monthly_sales_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates monthly performance with profit margins."""
    if df.empty:
        return pd.DataFrame()
        
    summary = df.groupby(["year", "month", "month_name"]).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "count"),
        quantity=("quantity", "sum"),
        avg_discount=("discount_percent", "mean")
    ).reset_index().sort_values(["year", "month"])
    
    summary["profit_margin"] = (summary["profit"] / summary["revenue"] * 100.0).round(2)
    return summary

def get_category_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Category breakdown sorted by total revenue."""
    if df.empty:
        return pd.DataFrame()
        
    cat = df.groupby("category").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "count"),
        quantity=("quantity", "sum"),
        avg_discount=("discount_percent", "mean"),
        return_rate=("return_flag", lambda x: (x.sum() / len(x) * 100.0) if len(x) > 0 else 0)
    ).reset_index().sort_values("revenue", ascending=False)
    
    cat["profit_margin"] = (cat["profit"] / cat["revenue"] * 100.0).round(2)
    return cat

def get_brand_sales(df: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    """Top brands by sales revenue."""
    if df.empty:
        return pd.DataFrame()
        
    brands = df.groupby("brand").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "count"),
        quantity=("quantity", "sum")
    ).reset_index().sort_values("revenue", ascending=False).head(top_n)
    
    return brands

def get_payment_method_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Distribution of sales across payment methods."""
    if df.empty:
        return pd.DataFrame()
        
    pm = df.groupby("payment_method").agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "count")
    ).reset_index().sort_values("revenue", ascending=False)
    
    pm["share_percent"] = (pm["revenue"] / pm["revenue"].sum() * 100.0).round(1)
    return pm
