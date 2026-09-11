"""
Regional and Geographic Analytics Module
Measures market penetration, state-level revenue, city orders, and regional return rates.
"""

import pandas as pd
from typing import Dict, Any

def get_state_performance(df: pd.DataFrame) -> pd.DataFrame:
    """State-wise breakdown of revenue, orders, profit, and returns."""
    if df.empty or "state" not in df.columns:
        return pd.DataFrame()
        
    states = df.groupby("state").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "count"),
        quantity=("quantity", "sum"),
        return_rate=("return_flag", lambda x: (x.sum() / len(x) * 100.0) if len(x) > 0 else 0)
    ).reset_index().sort_values("revenue", ascending=False)
    
    states["profit_margin"] = (states["profit"] / states["revenue"] * 100.0).round(2)
    states["market_share_pct"] = (states["revenue"] / states["revenue"].sum() * 100.0).round(2)
    return states

def get_city_performance(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Ranks top performing cities by revenue."""
    if df.empty or "city" not in df.columns:
        return pd.DataFrame()
        
    cities = df.groupby(["city", "state"]).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "count"),
        quantity=("quantity", "sum"),
        return_rate=("return_flag", lambda x: (x.sum() / len(x) * 100.0) if len(x) > 0 else 0)
    ).reset_index().sort_values("revenue", ascending=False).head(top_n)
    
    return cities
