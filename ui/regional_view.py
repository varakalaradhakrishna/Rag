"""
Regional Analytics View
State and city-level performance, market share concentration, and regional return rates.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.database import query_sales_df
from analytics.regional import get_state_performance, get_city_performance
from utils.helpers import format_currency, format_number, format_percentage

def render_regional_view():
    st.title("🌎 Regional & City-Level Intelligence")
    st.caption("Measure geographic market penetration, regional profitability, and metropolitan delivery dynamics.")
    
    df = query_sales_df("SELECT * FROM sales")
    if df.empty:
        st.warning("No sales transactions found.")
        return
        
    state_df = get_state_performance(df)
    
    c1, c2 = st.columns([1.2, 0.8])
    
    with c1:
        st.subheader("State-Wise Revenue & Margin")
        fig_state = px.bar(
            state_df, x="state", y="revenue",
            color="profit_margin", color_continuous_scale="Viridis",
            labels={"revenue": "Total Revenue (₹)", "state": "State", "profit_margin": "Margin (%)"},
            template="plotly_dark"
        )
        fig_state.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_state, use_container_width=True)
        
    with c2:
        st.subheader("Regional Return Rate Ranking")
        state_ret = state_df.sort_values("return_rate", ascending=True)
        fig_ret = px.bar(
            state_ret, x="return_rate", y="state", orientation="h",
            color="return_rate", color_continuous_scale="Reds",
            labels={"return_rate": "Return Rate (%)", "state": "State"},
            template="plotly_dark"
        )
        fig_ret.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_ret, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("🏙️ Top 15 Performing Cities")
    city_df = get_city_performance(df, top_n=15)
    
    disp_city = city_df.copy()
    disp_city["revenue"] = disp_city["revenue"].apply(format_currency)
    disp_city["profit"] = disp_city["profit"].apply(format_currency)
    disp_city["orders"] = disp_city["orders"].apply(format_number)
    disp_city["quantity"] = disp_city["quantity"].apply(format_number)
    disp_city["return_rate"] = disp_city["return_rate"].apply(format_percentage)
    
    st.dataframe(disp_city, use_container_width=True)
