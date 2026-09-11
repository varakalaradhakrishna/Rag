"""
Multi-Horizon Forecasting and Business Insights Generator
Produces multi-day future projections (7, 30, 60, 90 days) and automated narrative insights.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Dict, Any, List

from forecasting.train import prepare_daily_timeseries, train_and_compare_models
from utils.helpers import format_currency, format_number, format_percentage

def generate_multi_horizon_forecast(
    df: pd.DataFrame,
    target_col: str = "revenue",
    horizons: List[int] = [7, 30, 60, 90]
) -> Dict[str, Any]:
    """
    Trains best ML model on historical daily data and iteratively forecasts future values.
    """
    daily_df = prepare_daily_timeseries(df, target_col=target_col)
    
    if daily_df.empty or len(daily_df) < 25:
        return {
            "success": False,
            "message": "Insufficient historical data to produce a reliable forecast (need at least 25 daily records)."
        }
        
    training_res = train_and_compare_models(daily_df, target_col=target_col, test_days=min(14, len(daily_df) // 4))
    
    if not training_res["success"]:
        return training_res
        
    model = training_res["best_model"]
    feature_cols = training_res["feature_cols"]
    
    # Iterative forward forecasting
    last_date = daily_df["date"].max()
    max_horizon = max(horizons)
    
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, max_horizon + 1)]
    
    # Working series starting with historical
    extended_series = daily_df[["date", target_col]].copy()
    
    predictions = []
    
    for dt in forecast_dates:
        dow = dt.dayofweek
        dom = dt.day
        mon = dt.month
        is_wknd = 1 if dow in [5, 6] else 0
        
        # Pull lags from extended series
        lag_1 = extended_series[target_col].iloc[-1]
        lag_7 = extended_series[target_col].iloc[-7] if len(extended_series) >= 7 else lag_1
        lag_14 = extended_series[target_col].iloc[-14] if len(extended_series) >= 14 else lag_7
        
        rolling_7 = extended_series[target_col].iloc[-7:].mean()
        rolling_14 = extended_series[target_col].iloc[-14:].mean()
        
        feat_vector = np.array([[dow, dom, mon, is_wknd, lag_1, lag_7, lag_14, rolling_7, rolling_14]])
        pred_val = float(max(0.0, model.predict(feat_vector)[0]))
        
        predictions.append(pred_val)
        
        # Append predicted row to extended series
        extended_series = pd.concat([
            extended_series,
            pd.DataFrame([{"date": dt, target_col: pred_val}])
        ], ignore_index=True)
        
    forecast_df = pd.DataFrame({
        "date": forecast_dates,
        "predicted": predictions
    })
    
    # Compute confidence intervals (+/- 1.5 RMSE)
    rmse = training_res["metrics"]["RMSE"]
    forecast_df["lower_bound"] = np.maximum(0, forecast_df["predicted"] - (1.2 * rmse))
    forecast_df["upper_bound"] = forecast_df["predicted"] + (1.2 * rmse)
    
    # Calculate horizon aggregates
    horizon_summaries = {}
    recent_baseline_daily = daily_df[target_col].iloc[-30:].mean() if len(daily_df) >= 30 else daily_df[target_col].mean()
    
    for h in horizons:
        sub = forecast_df.iloc[:h]
        total_pred = float(sub["predicted"].sum())
        avg_pred_daily = float(sub["predicted"].mean())
        
        pct_change = ((avg_pred_daily - recent_baseline_daily) / recent_baseline_daily * 100.0) if recent_baseline_daily > 0 else 0.0
        
        horizon_summaries[f"{h}_days"] = {
            "days": h,
            "total_forecast": round(total_pred, 2),
            "avg_daily_forecast": round(avg_pred_daily, 2),
            "trend_change_pct": round(pct_change, 2)
        }
        
    # Generate Business Insights
    insights = []
    h30 = horizon_summaries.get("30_days", {})
    if h30:
        chg = h30["trend_change_pct"]
        if chg > 5.0:
            insights.append(f"📈 **Demand Momentum**: {target_col.capitalize()} is projected to rise by **{chg:+.1f}%** over the next 30 days compared to recent daily baselines.")
        elif chg < -5.0:
            insights.append(f"📉 **Post-Sale Normalization**: {target_col.capitalize()} is projected to moderate by **{chg:+.1f}%** following peak festive sales spikes.")
        else:
            insights.append(f"⚖️ **Stable Trajectory**: {target_col.capitalize()} displays a balanced run-rate with **{chg:+.1f}%** projected variation.")
            
    insights.append(f"🤖 **Model Architecture**: Forecast generated using **{training_res['best_model_name']}** (Test RMSE: {training_res['metrics']['RMSE']:,}, R²: {training_res['metrics']['R2']}).")
    insights.append("⚠️ **Uncertainty Note**: Predictions represent statistical approximations based on historical cycles and cannot guarantee unforeseen supply or demand shocks.")
    
    return {
        "success": True,
        "target_col": target_col,
        "historical_daily": daily_df[["date", target_col]],
        "forecast_df": forecast_df,
        "horizon_summaries": horizon_summaries,
        "insights": insights,
        "model_name": training_res["best_model_name"],
        "metrics": training_res["metrics"],
        "test_comparison": training_res["test_comparison"]
    }
