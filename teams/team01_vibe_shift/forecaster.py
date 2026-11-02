"""
Core Demand Forecasting Logic for Team 1: 'Vibe-Shift' Trend Forecaster.
Blends historical sales velocity with external cultural / social media trend signals.
"""

from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd


def load_trend_data(filepath: str) -> pd.DataFrame:
    """Loads and validates the historical sales & trend CSV."""
    df = pd.read_csv(filepath)
    required_cols = ["Date", "Item_Category", "Historical_Sales_Volume", "Social_Media_Trend_Score"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date").reset_index(drop=True)
    return df


def forecast_demand(
    df: pd.DataFrame,
    category: str,
    forecast_days: int = 30,
    social_weight: float = 0.35,
    growth_acceleration: float = 1.0
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Predicts the next N days of demand by combining:
    1. Historical sales velocity (rolling linear trend)
    2. Weekly seasonality patterns (weekday vs weekend uplift)
    3. Social media cultural signal momentum (trend score velocity)

    Returns:
        (historical_subset_df, forecast_df, metrics_dict)
    """
    cat_df = df[df["Item_Category"] == category].copy()
    if cat_df.empty:
        raise ValueError(f"Category '{category}' not found in dataset.")

    cat_df = cat_df.sort_values(by="Date").reset_index(drop=True)
    sales = cat_df["Historical_Sales_Volume"].values
    social = cat_df["Social_Media_Trend_Score"].values
    n = len(sales)

    # 1. Base velocity via weighted recent moving average and slope
    recent_window = min(30, n)
    recent_sales = sales[-recent_window:]
    x = np.arange(recent_window)
    slope, intercept = np.polyfit(x, recent_sales, 1)

    # 2. Cultural Signal Velocity (Social Media Trend momentum)
    recent_social = social[-14:]
    social_slope, _ = np.polyfit(np.arange(len(recent_social)), recent_social, 1)
    current_social_score = float(social[-1])
    social_momentum = (current_social_score / 50.0 - 1.0) * social_weight + (social_slope * 0.02)

    # 3. Weekly day-of-week multiplier
    cat_df["DayOfWeek"] = cat_df["Date"].dt.dayofweek
    dow_multipliers = cat_df.groupby("DayOfWeek")["Historical_Sales_Volume"].mean()
    overall_mean = max(1.0, cat_df["Historical_Sales_Volume"].mean())
    dow_factors = (dow_multipliers / overall_mean).to_dict()

    # 4. Generate future dates
    last_date = cat_df["Date"].max()
    future_dates = [last_date + timedelta(days=i + 1) for i in range(forecast_days)]

    forecast_values = []
    lower_bounds = []
    upper_bounds = []

    std_err = float(np.std(recent_sales - (slope * x + intercept)))
    std_err = max(5.0, std_err)

    for i, f_date in enumerate(future_dates):
        step = recent_window + i
        base_trend = max(1.0, slope * step + intercept)

        # Cultural multiplier compounding with growth acceleration
        cultural_lift = 1.0 + (social_momentum * (1.0 + 0.015 * i * growth_acceleration))
        cultural_lift = max(0.2, cultural_lift)

        dow_factor = dow_factors.get(f_date.weekday(), 1.0)

        projected = base_trend * cultural_lift * dow_factor
        projected = max(0.0, round(float(projected), 1))

        # Broadening confidence intervals over time
        uncertainty = std_err * np.sqrt(1 + (i / 10.0))
        lower = max(0.0, round(projected - 1.96 * uncertainty, 1))
        upper = round(projected + 1.96 * uncertainty, 1)

        forecast_values.append(projected)
        lower_bounds.append(lower)
        upper_bounds.append(upper)

    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Forecast_Demand": forecast_values,
        "Lower_Bound": lower_bounds,
        "Upper_Bound": upper_bounds,
        "Item_Category": category
    })

    metrics = {
        "current_social_score": current_social_score,
        "social_trend_direction": "Rising 🔥" if social_slope > 0.2 else ("Falling 📉" if social_slope < -0.2 else "Stable ⚖️"),
        "total_forecasted_units": int(np.sum(forecast_values)),
        "avg_daily_projected": round(float(np.mean(forecast_values)), 1),
        "peak_forecast_day": forecast_df.loc[forecast_df["Forecast_Demand"].idxmax()]["Date"].strftime("%Y-%m-%d"),
        "historical_avg_daily": round(float(cat_df["Historical_Sales_Volume"].mean()), 1)
    }

    return cat_df, forecast_df, metrics
