"""
Profit & Discount Analysis View
Examines the relationship between discount depth, order volume, and net profit margin erosion.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.database import query_sales_df
from analytics.discounts import get_discount_bucket_analysis, get_category_discount_matrix
from utils.helpers import format_currency, format_number, format_percentage

def render_discounts_view():
    st.title("💰 Profit & Discount Elasticity Analysis")
    st.caption("Investigate how promotional price drops impact unit volume, basket conversion, and bottom-line margins.")
    
    df = query_sales_df("SELECT * FROM sales")
    if df.empty:
        st.warning("No sales transactions found.")
        return
        
    tier_df = get_discount_bucket_analysis(df)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Revenue vs Profit Margin by Discount Tier")
        fig_tier = px.bar(
            tier_df, x="discount_bucket", y="revenue",
            color="profit_margin", color_continuous_scale="RdYlGn",
            labels={"discount_bucket": "Discount Range", "revenue": "Total Revenue (₹)", "profit_margin": "Margin (%)"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_tier, use_container_width=True)
        
    with c2:
        st.subheader("Category Discount vs Margin Matrix")
        cat_matrix = get_category_discount_matrix(df)
        fig_matrix = px.scatter(
            cat_matrix, x="avg_discount", y="profit_margin", size="revenue", color="category",
            hover_name="category", text="category",
            labels={"avg_discount": "Average Discount (%)", "profit_margin": "Profit Margin (%)"},
            template="plotly_dark"
        )
        fig_matrix.update_traces(textposition='top center')
        st.plotly_chart(fig_matrix, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("📊 Discount Tier Breakdown Table")
    disp_tier = tier_df.copy()
    disp_tier["revenue"] = disp_tier["revenue"].apply(format_currency)
    disp_tier["profit"] = disp_tier["profit"].apply(format_currency)
    disp_tier["orders"] = disp_tier["orders"].apply(format_number)
    disp_tier["units_sold"] = disp_tier["units_sold"].apply(format_number)
    disp_tier["profit_margin"] = disp_tier["profit_margin"].apply(format_percentage)
    disp_tier["avg_discount"] = disp_tier["avg_discount"].apply(format_percentage)
    disp_tier["return_rate"] = disp_tier["return_rate"].apply(format_percentage)
    
    st.dataframe(disp_tier, use_container_width=True)
