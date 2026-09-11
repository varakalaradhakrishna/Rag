"""
Customer Analytics & RFM Segmentation View
Analyzes repeat buyer behavior, customer lifetime value, and RFM loyalty segments.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.database import query_sales_df
from analytics.customers import get_customer_summary, get_rfm_segmentation, get_top_customers
from utils.helpers import format_currency, format_number, format_percentage
from ui.styles import render_kpi

def render_customers_view():
    st.title("👥 Customer Intelligence & RFM Segmentation")
    st.caption("Gain actionable visibility into buyer retention, purchase cadence, and customer lifetime value (CLV).")
    
    df = query_sales_df("SELECT * FROM sales")
    if df.empty:
        st.warning("No sales transactions found.")
        return
        
    summary = get_customer_summary(df)
    
    k1, k2, k3, k4 = st.columns(4)
    render_kpi(k1, "Unique Customers", format_number(summary["total_unique_customers"]), "Individual Buyers")
    render_kpi(k2, "Repeat Buyers", format_number(summary["repeat_customers"]), f"{summary['repeat_rate']:.1f}% Repeat Rate")
    render_kpi(k3, "Avg Orders / Buyer", f"{summary['avg_orders_per_customer']:.2f}", "Purchase Frequency")
    render_kpi(k4, "Avg Spend / Buyer", format_currency(summary["avg_revenue_per_customer"]), "Customer Lifetime Value")
    
    st.markdown("---")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("🎯 RFM Customer Segmentation")
        rfm_df = get_rfm_segmentation(df)
        if not rfm_df.empty:
            seg_counts = rfm_df["Segment"].value_counts().reset_index()
            seg_counts.columns = ["Segment", "Count"]
            
            fig_rfm = px.pie(
                seg_counts, names="Segment", values="Count", hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_dark"
            )
            fig_rfm.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_rfm, use_container_width=True)
            
    with c2:
        st.subheader("💎 Top 10 Customers by Lifetime Value")
        top_cust = get_top_customers(df, top_n=10)
        disp_top = top_cust[["customer_id", "orders", "total_spent", "avg_order_value", "favorite_category"]].copy()
        disp_top["total_spent"] = disp_top["total_spent"].apply(format_currency)
        disp_top["avg_order_value"] = disp_top["avg_order_value"].apply(format_currency)
        st.dataframe(disp_top, use_container_width=True)
        
    st.markdown("##### 📋 RFM Segment Definition & Action Guide")
    st.markdown("""
    * **Champions**: Highly recent, frequent buyers with top monetary spend. *Action: VIP rewards, early access to festive deals.*
    * **Loyal Customers**: Consistent buyers with steady basket value. *Action: Cross-sell related product categories.*
    * **Potential Loyalists**: Recent shoppers with high basket sizes. *Action: Loyalty program enrollment incentives.*
    * **At Risk Customers**: Historically high spenders who haven't purchased in over 45 days. *Action: Win-back personalized promo codes.*
    """)
