"""
Core Demand Forecasting Logic for Team 1: 'Vibe-Shift' Trend Forecaster.
Blends historical sales velocity with external cultural / social media trend signals.
"""

from datetime import datetime, timedelta
import io
from pathlib import Path
from typing import Tuple, Dict, Any, Union
import numpy as np
import pandas as pd


def load_trend_data(filepath_or_buffer: Union[str, Path, io.IOBase]) -> pd.DataFrame:
    """
    Loads, cleans, and validates the historical sales & trend CSV.
    Supports file path strings, pathlib.Path, or in-memory file buffers (e.g. Streamlit uploaders).

    Raises:
        ValueError: If required columns are missing, data is empty, or dates are invalid.
    """
    if isinstance(filepath_or_buffer, (str, Path)):
        p = Path(filepath_or_buffer)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {filepath_or_buffer}")
        if p.stat().st_size == 0:
            raise ValueError(f"Data file is empty: {filepath_or_buffer}")

    df = pd.read_csv(filepath_or_buffer)

    if df.empty:
        raise ValueError("The provided dataset contains zero rows.")

    required_cols = ["Date", "Item_Category", "Historical_Sales_Volume", "Social_Media_Trend_Score"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")

    # Parse and validate dates
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if df["Date"].isnull().any():
        invalid_count = int(df["Date"].isnull().sum())
        raise ValueError(f"Dataset contains {invalid_count} row(s) with invalid or unparseable dates.")

    # Validate and clean numeric fields
    df["Historical_Sales_Volume"] = pd.to_numeric(df["Historical_Sales_Volume"], errors="coerce").astype(float).fillna(0.0)
    df["Historical_Sales_Volume"] = df["Historical_Sales_Volume"].clip(lower=0.0)

    df["Social_Media_Trend_Score"] = pd.to_numeric(df["Social_Media_Trend_Score"], errors="coerce").astype(float).fillna(50.0)
    df["Social_Media_Trend_Score"] = df["Social_Media_Trend_Score"].clip(0.0, 100.0)

    df["Item_Category"] = df["Item_Category"].astype(str).str.strip()

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

    Args:
        df: Historical DataFrame with required columns.
        category: The apparel item category to forecast.
        forecast_days: Number of days into the future to project (must be > 0).
        social_weight: Sensitivity weight [0.0 - 1.0] for social media momentum.
        growth_acceleration: Cultural multiplier compounding factor.

    Returns:
        (historical_subset_df, forecast_df, metrics_dict)
    """
    if forecast_days <= 0:
        raise ValueError(f"forecast_days must be a positive integer, got {forecast_days}")

    social_weight = max(0.0, min(1.0, float(social_weight)))
    growth_acceleration = max(0.1, float(growth_acceleration))

    cat_df = df[df["Item_Category"] == category].copy()
    if cat_df.empty:
        raise ValueError(f"Category '{category}' not found in dataset.")

    cat_df = cat_df.sort_values(by="Date").reset_index(drop=True)
    sales = cat_df["Historical_Sales_Volume"].to_numpy(dtype=float)
    social = cat_df["Social_Media_Trend_Score"].to_numpy(dtype=float)
    n = len(sales)

    # 1. Base velocity via weighted recent moving average and slope
    if n >= 2:
        recent_window = min(30, n)
        recent_sales = sales[-recent_window:]
        x = np.arange(recent_window)
        poly = np.polyfit(x, recent_sales, 1)
        slope, intercept = float(poly[0]), float(poly[1])
        residuals = recent_sales - (slope * x + intercept)
        std_err = float(np.std(residuals))
        std_err = max(5.0, std_err)
    else:
        recent_window = max(1, n)
        slope = 0.0
        intercept = float(sales[0]) if n > 0 else 10.0
        std_err = 5.0

    # 2. Cultural Signal Velocity (Social Media Trend momentum)
    if len(social) >= 2:
        recent_social_len = min(14, len(social))
        recent_social = social[-recent_social_len:]
        poly_social = np.polyfit(np.arange(recent_social_len), recent_social, 1)
        social_slope = float(poly_social[0])
    else:
        social_slope = 0.0

    current_social_score = float(social[-1]) if len(social) > 0 else 50.0
    social_momentum = (current_social_score / 50.0 - 1.0) * social_weight + (social_slope * 0.02)

    # 3. Weekly day-of-week multiplier
    cat_df["DayOfWeek"] = cat_df["Date"].dt.dayofweek
    dow_multipliers = cat_df.groupby("DayOfWeek")["Historical_Sales_Volume"].mean()
    overall_mean = max(1.0, float(cat_df["Historical_Sales_Volume"].mean()))
    dow_factors = (dow_multipliers / overall_mean).to_dict()

    # 4. Generate future dates
    last_date = cat_df["Date"].max()
    future_dates = [last_date + timedelta(days=i + 1) for i in range(forecast_days)]

    forecast_values = []
    lower_bounds = []
    upper_bounds = []

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
        upper = max(projected, round(projected + 1.96 * uncertainty, 1))

        # Enforce invariant: 0 <= lower <= projected <= upper
        lower = min(lower, projected)
        upper = max(upper, projected)

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

    # Buyer inventory metrics
    total_forecasted = int(np.sum(forecast_values))
    avg_projected = round(float(np.mean(forecast_values)), 1)
    hist_avg = round(float(cat_df["Historical_Sales_Volume"].mean()), 1)
    max_idx = int(forecast_df["Forecast_Demand"].idxmax())
    peak_date_str = forecast_df.loc[max_idx]["Date"].strftime("%Y-%m-%d")

    # Recommended safety stock: 1-week lead time buffer at 95% service level
    safety_stock = int(np.ceil(1.65 * std_err * np.sqrt(7)))
    reorder_point = int(np.ceil(avg_projected * 7 + safety_stock))

    # Trend velocity percentage
    start_social = float(social[-min(14, len(social))]) if len(social) > 0 else current_social_score
    trend_velocity_pct = round(((current_social_score - start_social) / max(1.0, start_social)) * 100, 1)

    # Risk level classification
    cv = std_err / max(1.0, hist_avg)
    risk_level = "High" if cv > 0.35 else ("Moderate" if cv > 0.20 else "Low")

    metrics = {
        "current_social_score": current_social_score,
        "social_trend_direction": "Rising" if social_slope > 0.2 else ("Falling" if social_slope < -0.2 else "Stable"),
        "total_forecasted_units": total_forecasted,
        "avg_daily_projected": avg_projected,
        "peak_forecast_day": peak_date_str,
        "historical_avg_daily": hist_avg,
        "safety_stock_recommendation": safety_stock,
        "reorder_point_recommendation": reorder_point,
        "trend_velocity_pct": trend_velocity_pct,
        "forecast_volatility_risk": risk_level
    }

    return cat_df, forecast_df, metrics

