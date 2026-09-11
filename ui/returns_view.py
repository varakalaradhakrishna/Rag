"""
Returns & Reverse Logistics View
Detailed breakdown of return rates, reversed GMV loss, and category vulnerability.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.database import query_sales_df
from analytics.returns import get_return_summary, get_returns_by_category, get_returns_by_brand, get_returns_by_state
from utils.helpers import format_currency, format_number, format_percentage
from ui.styles import render_kpi

def render_returns_view():
    st.title("🔄 Returns & Reverse Logistics Intelligence")
    st.caption("Track returned order rates, reversed merchandise loss, and category vulnerability hotspots.")
    
    df = query_sales_df("SELECT * FROM sales")
    if df.empty:
        st.warning("No sales transactions found.")
        return
        
    ret_summary = get_return_summary(df)
    
    k1, k2, k3, k4 = st.columns(4)
    render_kpi(k1, "Overall Return Rate", format_percentage(ret_summary["return_rate"]), "Portfolio Benchmark", is_negative=(ret_summary["return_rate"] > 8.0))
    render_kpi(k2, "Returned Orders", format_number(ret_summary["returned_orders"]), "Units Reversed")
    render_kpi(k3, "Returned GMV Loss", format_currency(ret_summary["returned_revenue"]), "Reversed Gross Revenue", is_negative=True)
    render_kpi(k4, "Net Retained GMV", format_currency(ret_summary["retained_revenue"]), "Realized Net Revenue")
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Return Rates by Category")
        cat_ret = get_returns_by_category(df)
        fig_cat = px.bar(
            cat_ret, x="return_rate", y="category", orientation="h",
            color="return_rate", color_continuous_scale="Reds",
            labels={"return_rate": "Return Rate (%)", "category": "Category"},
            template="plotly_dark"
        )
        fig_cat.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with c2:
        st.subheader("Return Rates Across Top Brands")
        brand_ret = get_returns_by_brand(df, top_n=10)
        fig_brand = px.bar(
            brand_ret, x="return_rate", y="brand", orientation="h",
            color="return_rate", color_continuous_scale="OrRd",
            labels={"return_rate": "Return Rate (%)", "brand": "Brand"},
            template="plotly_dark"
        )
        fig_brand.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_brand, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("📋 State-Level Return Rate Leaderboard")
    state_ret = get_returns_by_state(df)
    disp_state = state_ret.copy()
    disp_state["total_revenue"] = disp_state["total_revenue"].apply(format_currency)
    disp_state["total_orders"] = disp_state["total_orders"].apply(format_number)
    disp_state["returned_orders"] = disp_state["returned_orders"].apply(format_number)
    disp_state["return_rate"] = disp_state["return_rate"].apply(format_percentage)
    st.dataframe(disp_state, use_container_width=True)
