"""
Forecasting & Machine Learning Prediction View
Multi-horizon statistical & ML projections, model benchmark comparisons, and interactive actual-vs-forecast charts.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from database.database import query_sales_df
from forecasting.predict import generate_multi_horizon_forecast
from utils.helpers import format_currency, format_number, format_percentage
from ui.styles import render_kpi

def render_forecasting_view():
    st.title("🔮 Machine Learning Demand & Revenue Forecasting")
    st.caption("Statistical time-series models (Gradient Boosting, Random Forest, Ridge) predicting future business horizons.")
    
    df = query_sales_df("SELECT * FROM sales")
    if df.empty:
        st.warning("No sales transactions found in database.")
        return
        
    target_choice = st.radio(
        "Forecast Target Metric:",
        ["Revenue (₹)", "Quantity (Units Sold)"],
        horizontal=True
    )
    target_col = "revenue" if "Revenue" in target_choice else "quantity"
    
    with st.spinner("Training ML time-series models and calculating projections..."):
        fc_res = generate_multi_horizon_forecast(df, target_col=target_col)
        
    if not fc_res.get("success"):
        st.error(fc_res.get("message", "Forecasting failed."))
        return
        
    h_summaries = fc_res["horizon_summaries"]
    
    # 4 Horizon Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    
    for col, days in zip([c1, c2, c3, c4], [7, 30, 60, 90]):
        h_data = h_summaries.get(f"{days}_days", {})
        val = format_currency(h_data.get("total_forecast", 0)) if target_col == "revenue" else format_number(h_data.get("total_forecast", 0))
        pct = h_data.get("trend_change_pct", 0)
        render_kpi(col, f"Next {days} Days Projection", val, f"{pct:+.1f}% vs baseline", is_negative=(pct < 0))
        
    st.markdown("---")
    
    # Actual vs Predicted Test Set Chart + Future Forecast
    st.subheader(f"📊 Historical Trajectory & Future {target_choice} Projection")
    
    hist_daily = fc_res["historical_daily"]
    forecast_df = fc_res["forecast_df"]
    
    fig = go.Figure()
    
    # 1. Historical Actual
    fig.add_trace(go.Scatter(
        x=hist_daily["date"], y=hist_daily[target_col],
        mode="lines", name=f"Historical Actual {target_col.capitalize()}",
        line=dict(color="#3b82f6", width=2)
    ))
    
    # 2. Predicted Forecast Line
    fig.add_trace(go.Scatter(
        x=forecast_df["date"], y=forecast_df["predicted"],
        mode="lines+markers", name=f"ML Predicted Forecast ({fc_res['model_name']})",
        line=dict(color="#f59e0b", width=2.5, dash="dash")
    ))
    
    # 3. Confidence Interval Bands
    fig.add_trace(go.Scatter(
        x=list(forecast_df["date"]) + list(forecast_df["date"])[::-1],
        y=list(forecast_df["upper_bound"]) + list(forecast_df["lower_bound"])[::-1],
        fill="toself",
        fillcolor="rgba(245, 158, 11, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=True,
        name="Confidence Band (±1.2 RMSE)"
    ))
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col_eval, col_insight = st.columns([1, 1.2])
    
    with col_eval:
        st.subheader("⚙️ Model Architecture & Benchmark Scores")
        metrics = fc_res["metrics"]
        st.markdown(f"**Selected Winning Algorithm**: `{fc_res['model_name']}`")
        
        m_df = pd.DataFrame([
            {"Metric": "MAE (Mean Absolute Error)", "Score": f"{metrics['MAE']:,.2f}"},
            {"Metric": "RMSE (Root Mean Squared Error)", "Score": f"{metrics['RMSE']:,.2f}"},
            {"Metric": "MAPE (% Error)", "Score": f"{metrics['MAPE_pct']:.1f}%"},
            {"Metric": "R² Score (Coefficient of Determination)", "Score": f"{metrics['R2']:.4f}"}
        ])
        st.table(m_df)
        
    with col_insight:
        st.subheader("💡 Automated Predictive Insights")
        for ins in fc_res["insights"]:
            st.markdown(ins)
