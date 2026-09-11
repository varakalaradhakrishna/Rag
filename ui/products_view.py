"""
Product Analytics View
Comprehensive analysis of catalog performers, revenue drivers, profit contributors, and worst-performing SKUs.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.database import query_sales_df
from analytics.products import get_top_products, get_worst_performing_products, get_product_rating_analysis
from utils.helpers import format_currency, format_number, format_percentage

def render_products_view():
    st.title("📦 Product Catalog Analytics")
    st.caption("Identify bestsellers, margin drivers, low-velocity SKUs, and customer review distributions.")
    
    df = query_sales_df("SELECT * FROM sales")
    if df.empty:
        st.warning("No sales transactions found.")
        return
        
    metric_choice = st.radio(
        "Rank Top Products By:",
        ["Revenue", "Profit", "Quantity", "Rating"],
        horizontal=True
    )
    
    metric_map = {"Revenue": "revenue", "Profit": "profit", "Quantity": "quantity", "Rating": "avg_rating"}
    top_df = get_top_products(df, metric=metric_map[metric_choice], top_n=12)
    
    st.subheader(f"Top 12 Products Ranked by {metric_choice}")
    
    fig_top = px.bar(
        top_df, x=metric_map[metric_choice], y="product_name", orientation="h",
        color=metric_map[metric_choice], color_continuous_scale="Purples",
        hover_data=["category", "brand", "revenue", "profit", "return_rate"],
        labels={metric_map[metric_choice]: metric_choice, "product_name": "Product"},
        template="plotly_dark"
    )
    fig_top.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_top, use_container_width=True)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("⚠️ Worst Performing SKUs (Lowest Revenue)")
        worst_df = get_worst_performing_products(df, bottom_n=8)
        disp_worst = worst_df[["product_name", "category", "brand", "revenue", "orders", "return_rate"]].copy()
        disp_worst["revenue"] = disp_worst["revenue"].apply(format_currency)
        disp_worst["orders"] = disp_worst["orders"].apply(format_number)
        disp_worst["return_rate"] = disp_worst["return_rate"].apply(format_percentage)
        st.dataframe(disp_worst, use_container_width=True)
        
    with c2:
        st.subheader("⭐ Customer Ratings Distribution")
        rating_df = get_product_rating_analysis(df)
        fig_rating = px.bar(
            rating_df, x="rating", y="orders",
            labels={"rating": "Customer Star Rating", "orders": "Order Count"},
            color="rating", color_continuous_scale="Viridis",
            template="plotly_dark"
        )
        fig_rating.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_rating, use_container_width=True)
