"""
Executive Dashboard View
Interactive cross-filtered command center featuring high-impact KPI cards and Plotly visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.database import query_sales_df
from analytics.sales import get_overall_kpis, get_daily_sales_trend, get_category_sales
from utils.helpers import format_currency, format_number, format_percentage
from ui.styles import render_kpi

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Renders dashboard filter controls in an expander and returns filtered subset."""
    with st.expander("🔍 Interactive Data Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        # Category Filter
        categories = ["All Categories"] + sorted(list(df["category"].dropna().unique()))
        selected_cat = col1.selectbox("Category", categories)
        
        # Brand Filter
        brands = ["All Brands"] + sorted(list(df["brand"].dropna().unique()))
        selected_brand = col2.selectbox("Brand", brands)
        
        # State Filter
        states = ["All States"] + sorted(list(df["state"].dropna().unique()))
        selected_state = col3.selectbox("State", states)
        
        # Payment Method
        payments = ["All Payment Methods"] + sorted(list(df["payment_method"].dropna().unique()))
        selected_pm = col4.selectbox("Payment Method", payments)
        
        col5, col6 = st.columns([1, 1])
        # Return status
        return_options = ["All Orders", "Delivered / Retained Only", "Returned Only"]
        selected_return = col5.selectbox("Return Status", return_options)
        
        # Date range
        df["date_only"] = pd.to_datetime(df["order_date"]).dt.date
        min_dt, max_dt = df["date_only"].min(), df["date_only"].max()
        selected_dates = col6.date_input("Order Date Range", value=(min_dt, max_dt), min_value=min_dt, max_value=max_dt)
        
    filtered = df.copy()
    if selected_cat != "All Categories":
        filtered = filtered[filtered["category"] == selected_cat]
    if selected_brand != "All Brands":
        filtered = filtered[filtered["brand"] == selected_brand]
    if selected_state != "All States":
        filtered = filtered[filtered["state"] == selected_state]
    if selected_pm != "All Payment Methods":
        filtered = filtered[filtered["payment_method"] == selected_pm]
    if selected_return == "Delivered / Retained Only":
        filtered = filtered[filtered["return_flag"] == 0]
    elif selected_return == "Returned Only":
        filtered = filtered[filtered["return_flag"] == 1]
        
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        s_start, s_end = selected_dates
        filtered = filtered[(filtered["date_only"] >= s_start) & (filtered["date_only"] <= s_end)]
        
    return filtered

def render_dashboard():
    st.title("📊 Executive Sales Intelligence Dashboard")
    st.caption("Live cross-filtered performance cockpit powered by SQLite and Plotly.")
    
    df = query_sales_df("SELECT * FROM sales")
    if df.empty:
        st.warning("No sales transactions available in database. Please seed or upload data.")
        return
        
    filtered_df = filter_dataframe(df)
    kpis = get_overall_kpis(filtered_df)
    
    # 8 KPI Cards in two rows of 4
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    render_kpi(r1c1, "Total Revenue", format_currency(kpis["total_revenue"]), f"{format_percentage(kpis['profit_margin'])} Margin")
    render_kpi(r1c2, "Total Profit", format_currency(kpis["total_profit"]), "Net Earnings")
    render_kpi(r1c3, "Total Orders", format_number(kpis["total_orders"]), "Completed Baskets")
    render_kpi(r1c4, "Total Units Sold", format_number(kpis["total_quantity"]), "Items Dispatched")
    
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    render_kpi(r2c1, "Avg Order Value (AOV)", format_currency(kpis["avg_order_value"]), "Per Order")
    render_kpi(r2c2, "Average Discount", format_percentage(kpis["avg_discount"]), "Off MRP")
    render_kpi(r2c3, "Return Rate", format_percentage(kpis["return_rate"]), "Reverse Logistics", is_negative=(kpis["return_rate"] > 10.0))
    render_kpi(r2c4, "Average Rating", f"★ {kpis['avg_rating']:.2f} / 5.0", "Customer Satisfaction")
    
    st.markdown("---")
    
    # Charts Row 1: Daily Revenue Trend + Category Revenue Breakdown
    c1, c2 = st.columns([1.2, 0.8])
    
    with c1:
        st.subheader("📈 Daily Revenue & Profit Velocity")
        trend_df = get_daily_sales_trend(filtered_df)
        if not trend_df.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=trend_df["date"], y=trend_df["revenue"],
                mode="lines+markers", name="Revenue",
                line=dict(color="#3b82f6", width=2.5),
                fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.1)"
            ))
            fig_trend.add_trace(go.Scatter(
                x=trend_df["date"], y=trend_df["profit"],
                mode="lines", name="Profit",
                line=dict(color="#10b981", width=2, dash="dot")
            ))
            fig_trend.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified",
                template="plotly_dark"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
    with c2:
        st.subheader("📦 Revenue by Category")
        cat_df = get_category_sales(filtered_df)
        if not cat_df.empty:
            fig_cat = px.pie(
                cat_df, names="category", values="revenue",
                hole=0.45, color_discrete_sequence=px.colors.qualitative.Bold,
                template="plotly_dark"
            )
            fig_cat.update_traces(textposition='inside', textinfo='percent+label')
            fig_cat.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_cat, use_container_width=True)
            
    # Charts Row 2: State-wise Revenue + Payment Method Share
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("🌎 Regional Revenue Performance")
        state_df = filtered_df.groupby("state")["revenue"].sum().reset_index().sort_values("revenue", ascending=True)
        fig_state = px.bar(
            state_df.tail(10), x="revenue", y="state", orientation="h",
            labels={"revenue": "Revenue (₹)", "state": "State"},
            color="revenue", color_continuous_scale="Blues",
            template="plotly_dark"
        )
        fig_state.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_state, use_container_width=True)
        
    with c4:
        st.subheader("💳 Payment Methods Mix")
        pm_df = filtered_df.groupby("payment_method")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
        fig_pm = px.bar(
            pm_df, x="payment_method", y="revenue",
            labels={"revenue": "Revenue (₹)", "payment_method": "Payment Method"},
            color="payment_method", color_discrete_sequence=px.colors.qualitative.Prism,
            template="plotly_dark"
        )
        fig_pm.update_layout(showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_pm, use_container_width=True)
