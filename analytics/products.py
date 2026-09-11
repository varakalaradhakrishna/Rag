"""
Product Analytics Module
Examines product performance, velocity, margins, ratings, and return rates.
"""

import pandas as pd
from typing import Dict, Any

def get_top_products(df: pd.DataFrame, metric: str = "revenue", top_n: int = 15) -> pd.DataFrame:
    """
    Ranks products by specified metric (revenue, profit, quantity, rating).
    """
    if df.empty:
        return pd.DataFrame()
        
    metric_col = metric.lower()
    
    prod = df.groupby(["product_id", "product_name", "category", "brand"]).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        quantity=("quantity", "sum"),
        orders=("order_id", "count"),
        avg_price=("sale_price", "mean"),
        avg_rating=("rating", "mean"),
        return_rate=("return_flag", lambda x: (x.sum() / len(x) * 100.0) if len(x) > 0 else 0)
    ).reset_index()
    
    prod["profit_margin"] = (prod["profit"] / prod["revenue"] * 100.0).round(2)
    
    if metric_col in prod.columns:
        prod = prod.sort_values(metric_col, ascending=False).head(top_n)
    else:
        prod = prod.sort_values("revenue", ascending=False).head(top_n)
        
    return prod

def get_worst_performing_products(df: pd.DataFrame, bottom_n: int = 10) -> pd.DataFrame:
    """Finds lowest revenue products."""
    if df.empty:
        return pd.DataFrame()
        
    prod = df.groupby(["product_id", "product_name", "category", "brand"]).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        quantity=("quantity", "sum"),
        orders=("order_id", "count"),
        avg_rating=("rating", "mean"),
        return_rate=("return_flag", lambda x: (x.sum() / len(x) * 100.0) if len(x) > 0 else 0)
    ).reset_index().sort_values("revenue", ascending=True).head(bottom_n)
    
    return prod

def get_product_rating_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyzes distribution of product customer review ratings."""
    if df.empty:
        return pd.DataFrame()
        
    rating_dist = df.groupby("rating").agg(
        orders=("order_id", "count"),
        revenue=("revenue", "sum"),
        return_rate=("return_flag", lambda x: (x.sum() / len(x) * 100.0) if len(x) > 0 else 0)
    ).reset_index().sort_values("rating")
    
    return rating_dist
