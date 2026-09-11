"""
Time-Series Feature Extraction and Model Training Module
Trains and compares multiple ML models (Random Forest, Gradient Boosting, Ridge Regression).
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from forecasting.evaluation import evaluate_forecast_predictions
from utils.logging import logger

def prepare_daily_timeseries(df: pd.DataFrame, target_col: str = "revenue") -> pd.DataFrame:
    """
    Transforms raw transactional data into a continuous daily time-series with engineered features.
    """
    if df.empty or "order_date" not in df.columns or target_col not in df.columns:
        return pd.DataFrame()
        
    df_temp = df.copy()
    df_temp["date"] = pd.to_datetime(df_temp["order_date"]).dt.date
    
    daily = df_temp.groupby("date").agg({target_col: "sum"}).reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)
    
    # Fill any missing calendar dates with 0 or forward rolling median
    if len(daily) > 1:
        full_idx = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
        daily = daily.set_index("date").reindex(full_idx, fill_value=0.0).rename_axis("date").reset_index()
        
    # Feature Engineering for Time Series
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["day_of_month"] = daily["date"].dt.day
    daily["month"] = daily["date"].dt.month
    daily["is_weekend"] = daily["day_of_week"].isin([5, 6]).astype(int)
    
    # Lag and Rolling window features
    daily["lag_1"] = daily[target_col].shift(1)
    daily["lag_7"] = daily[target_col].shift(7)
    daily["lag_14"] = daily[target_col].shift(14)
    daily["rolling_mean_7"] = daily[target_col].shift(1).rolling(window=7, min_periods=1).mean()
    daily["rolling_mean_14"] = daily[target_col].shift(1).rolling(window=14, min_periods=1).mean()
    
    # Drop rows where lag_14 is NaN
    daily_features = daily.dropna().reset_index(drop=True)
    return daily_features

def train_and_compare_models(
    daily_df: pd.DataFrame,
    target_col: str = "revenue",
    test_days: int = 14
) -> Dict[str, Any]:
    """
    Trains and compares Random Forest, Gradient Boosting, and Ridge Regression.
    Returns comparison table, best model, evaluation metrics, and test predictions.
    """
    if len(daily_df) < (test_days + 15):
        return {
            "success": False,
            "message": f"Insufficient historical days ({len(daily_df)} available). Need at least {test_days + 15} daily records."
        }
        
    feature_cols = [
        "day_of_week", "day_of_month", "month", "is_weekend",
        "lag_1", "lag_7", "lag_14", "rolling_mean_7", "rolling_mean_14"
    ]
    
    X = daily_df[feature_cols].values
    y = daily_df[target_col].values
    
    # Train / Test split by time sequence
    train_size = len(daily_df) - test_days
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    test_dates = daily_df["date"].iloc[train_size:].values
    
    models = {
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "Ridge Regression": Ridge(alpha=1.0)
    }
    
    results = {}
    best_model_name = None
    best_rmse = float("inf")
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_pred = np.maximum(0, y_pred)  # Non-negative predictions
        
        metrics = evaluate_forecast_predictions(y_test, y_pred)
        results[name] = {
            "model": model,
            "metrics": metrics,
            "y_pred": y_pred
        }
        
        if metrics["RMSE"] < best_rmse:
            best_rmse = metrics["RMSE"]
            best_model_name = name
            
    # Retrain best model on full dataset
    best_model = models[best_model_name]
    best_model.fit(X, y)
    
    # Format actual vs predicted for test set
    test_comparison = pd.DataFrame({
        "date": test_dates,
        "actual": y_test,
        "predicted": results[best_model_name]["y_pred"]
    })
    
    return {
        "success": True,
        "best_model_name": best_model_name,
        "best_model": best_model,
        "all_results": results,
        "metrics": results[best_model_name]["metrics"],
        "test_comparison": test_comparison,
        "training_days": train_size,
        "test_days": test_days,
        "feature_cols": feature_cols
    }
