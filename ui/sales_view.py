"""
Sales Analytics View
Deep-dive temporal and channel performance across monthly runs, brands, and categories.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.database import query_sales_df
from analytics.sales import (
    get_daily_sales_trend,
    get_monthly_sales_summary,
    get_category_sales,
    get_brand_sales,
    get_payment_method_distribution
)
from utils.helpers import format_currency, format_number, format_percentage

def render_sales_view():
    st.title("📈 In-Depth Sales & Channel Analytics")
    st.caption("Detailed breakdown of revenue velocity, monthly growth, brand rankings, and transaction frequency.")
    
    df = query_sales_df("SELECT * FROM sales")
    if df.empty:
        st.warning("No sales transactions found.")
        return
        
    tab1, tab2, tab3 = st.tabs(["📅 Monthly Performance", "🏷️ Brand & Category Share", "💳 Payment Methods"])
    
    with tab1:
        st.subheader("Monthly Revenue, Profit & Margin Dynamics")
        monthly_df = get_monthly_sales_summary(df)
        
        if not monthly_df.empty:
            fig_monthly = go.Figure()
            fig_monthly.add_trace(go.Bar(
                x=monthly_df["month_name"] + " " + monthly_df["year"].astype(str),
                y=monthly_df["revenue"],
                name="Gross Revenue",
                marker_color="#3b82f6"
            ))
            fig_monthly.add_trace(go.Bar(
                x=monthly_df["month_name"] + " " + monthly_df["year"].astype(str),
                y=monthly_df["profit"],
                name="Net Profit",
                marker_color="#10b981"
            ))
            fig_monthly.add_trace(go.Scatter(
                x=monthly_df["month_name"] + " " + monthly_df["year"].astype(str),
                y=monthly_df["profit_margin"],
                name="Profit Margin (%)",
                yaxis="y2",
                mode="lines+markers",
                marker=dict(size=8, color="#f59e0b")
            ))
            fig_monthly.update_layout(
                yaxis=dict(title="Amount (₹)"),
                yaxis2=dict(title="Margin (%)", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                barmode="group",
                template="plotly_dark",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # Formatted Monthly Data Table
            st.markdown("##### Detailed Monthly Performance Ledger")
            display_m = monthly_df.copy()
            display_m["revenue"] = display_m["revenue"].apply(format_currency)
            display_m["profit"] = display_m["profit"].apply(format_currency)
            display_m["orders"] = display_m["orders"].apply(format_number)
            display_m["units_sold"] = display_m["units_sold"].apply(format_number)
            display_m["profit_margin"] = display_m["profit_margin"].apply(format_percentage)
            display_m["avg_discount"] = display_m["avg_discount"].apply(format_percentage)
            st.dataframe(display_m, use_container_width=True)
            
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Top 12 Brands by Gross Revenue")
            brand_df = get_brand_sales(df, top_n=12)
            fig_brand = px.bar(
                brand_df, x="revenue", y="brand", orientation="h",
                color="revenue", color_continuous_scale="Tealgrn",
                labels={"revenue": "Revenue (₹)", "brand": "Brand"},
                template="plotly_dark"
            )
            fig_brand.update_layout(margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_brand, use_container_width=True)
            
        with c2:
            st.subheader("Category Volume vs Value Matrix")
            cat_df = get_category_sales(df)
            fig_scatter = px.scatter(
                cat_df, x="units_sold", y="revenue", size="profit", color="category",
                hover_name="category", text="category",
                labels={"units_sold": "Units Sold", "revenue": "Total Revenue (₹)"},
                template="plotly_dark"
            )
            fig_scatter.update_traces(textposition='top center')
            fig_scatter.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_scatter, use_container_width=True)
            
    with tab3:
        st.subheader("Payment Method Analytics")
        pm_df = get_payment_method_distribution(df)
        col1, col2 = st.columns([1, 1.2])
        with col1:
            fig_donut = px.pie(
                pm_df, names="payment_method", values="revenue", hole=0.5,
                color_discrete_sequence=px.colors.sequential.Electric,
                template="plotly_dark"
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)
        with col2:
            st.markdown("##### Payment Gateway Metrics")
            disp_pm = pm_df.copy()
            disp_pm["revenue"] = disp_pm["revenue"].apply(format_currency)
            disp_pm["orders"] = disp_pm["orders"].apply(format_number)
            disp_pm["share_percent"] = disp_pm["share_percent"].apply(format_percentage)
            st.dataframe(disp_pm, use_container_width=True)
