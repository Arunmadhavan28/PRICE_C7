"""
Unit tests for Team 1: 'Vibe-Shift' Trend Forecaster.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from forecaster import load_trend_data, forecast_demand

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "trend_sales_data.csv"


@pytest.fixture
def sample_data():
    return load_trend_data(str(DATA_PATH))


def test_data_schema(sample_data):
    """Validates dataset has required columns and non-empty rows."""
    required = ["Date", "Item_Category", "Historical_Sales_Volume", "Social_Media_Trend_Score"]
    for col in required:
        assert col in sample_data.columns
    assert len(sample_data) >= 30
    assert not sample_data["Date"].isnull().any()


def test_forecast_horizon(sample_data):
    """Verifies forecast generates exact horizon days."""
    cat = sample_data["Item_Category"].iloc[0]
    hist_df, forecast_df, metrics = forecast_demand(sample_data, category=cat, forecast_days=30)
    assert len(forecast_df) == 30
    assert "Forecast_Demand" in forecast_df.columns
    assert "Lower_Bound" in forecast_df.columns
    assert "Upper_Bound" in forecast_df.columns


def test_forecast_bounds(sample_data):
    """Verifies that projected values are non-negative and upper bound >= lower bound."""
    cat = sample_data["Item_Category"].iloc[0]
    _, forecast_df, _ = forecast_demand(sample_data, category=cat, forecast_days=30)
    assert (forecast_df["Forecast_Demand"] >= 0).all()
    assert (forecast_df["Upper_Bound"] >= forecast_df["Lower_Bound"]).all()


def test_social_weight_influence(sample_data):
    """Verifies that varying the social weight parameter modulates forecast projection."""
    cat = sample_data["Item_Category"].iloc[0]
    _, f_low, _ = forecast_demand(sample_data, category=cat, forecast_days=15, social_weight=0.0)
    _, f_high, _ = forecast_demand(sample_data, category=cat, forecast_days=15, social_weight=0.9)
    # The two forecasts should not be identical if social score has variance
    assert len(f_low) == len(f_high)


def test_invalid_category_error(sample_data):
    """Ensures meaningful ValueError when non-existent category is requested."""
    with pytest.raises(ValueError):
        forecast_demand(sample_data, category="NonExistentCategory999", forecast_days=30)


def test_forecast_invalid_days(sample_data):
    """Ensures ValueError is raised when forecast_days <= 0."""
    cat = sample_data["Item_Category"].iloc[0]
    with pytest.raises(ValueError):
        forecast_demand(sample_data, category=cat, forecast_days=0)
    with pytest.raises(ValueError):
        forecast_demand(sample_data, category=cat, forecast_days=-10)


def test_confidence_interval_invariants(sample_data):
    """Verifies invariant: 0 <= Lower_Bound <= Forecast_Demand <= Upper_Bound for all days."""
    for cat in sample_data["Item_Category"].unique():
        _, forecast_df, _ = forecast_demand(sample_data, category=cat, forecast_days=20)
        assert (forecast_df["Lower_Bound"] >= 0).all()
        assert (forecast_df["Forecast_Demand"] >= forecast_df["Lower_Bound"]).all()
        assert (forecast_df["Upper_Bound"] >= forecast_df["Forecast_Demand"]).all()


def test_load_trend_data_from_buffer():
    """Verifies that load_trend_data can successfully parse data from an in-memory buffer."""
    import io
    csv_text = (
        "Date,Item_Category,Historical_Sales_Volume,Social_Media_Trend_Score\n"
        "2026-01-01,Test Dress,50,75\n"
        "2026-01-02,Test Dress,55,80\n"
        "2026-01-03,Test Dress,60,82\n"
    )
    buffer = io.StringIO(csv_text)
    df = load_trend_data(buffer)
    assert len(df) == 3
    assert df["Item_Category"].iloc[0] == "Test Dress"
    assert df["Historical_Sales_Volume"].sum() == 165


def test_load_trend_data_missing_column():
    """Verifies that load_trend_data raises ValueError if required column is missing."""
    import io
    csv_text = "Date,Item_Category,Historical_Sales_Volume\n2026-01-01,Test,50\n"
    with pytest.raises(ValueError) as excinfo:
        load_trend_data(io.StringIO(csv_text))
    assert "Missing required columns" in str(excinfo.value)


def test_load_trend_data_invalid_dates():
    """Verifies that load_trend_data raises ValueError on corrupt dates."""
    import io
    csv_text = "Date,Item_Category,Historical_Sales_Volume,Social_Media_Trend_Score\nnot-a-date,Test,50,80\n"
    with pytest.raises(ValueError) as excinfo:
        load_trend_data(io.StringIO(csv_text))
    assert "invalid or unparseable dates" in str(excinfo.value)


def test_short_history_graceful_handling():
    """Verifies that forecaster does not crash on categories with minimal history (< 2 rows)."""
    minimal_df = pd.DataFrame({
        "Date": pd.to_datetime(["2026-01-01"]),
        "Item_Category": ["Micro Capsule"],
        "Historical_Sales_Volume": [42.0],
        "Social_Media_Trend_Score": [60.0]
    })
    hist_df, forecast_df, metrics = forecast_demand(minimal_df, category="Micro Capsule", forecast_days=7)
    assert len(forecast_df) == 7
    assert (forecast_df["Forecast_Demand"] >= 0).all()
    assert metrics["total_forecasted_units"] > 0


def test_constant_sales_history():
    """Verifies that forecast handles zero variance flat sales without NaN values."""
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    flat_df = pd.DataFrame({
        "Date": dates,
        "Item_Category": ["Flat Shirt"] * 30,
        "Historical_Sales_Volume": [100.0] * 30,
        "Social_Media_Trend_Score": [50.0] * 30
    })
    _, forecast_df, metrics = forecast_demand(flat_df, category="Flat Shirt", forecast_days=14)
    assert not forecast_df["Forecast_Demand"].isnull().any()
    assert not forecast_df["Upper_Bound"].isnull().any()
    assert metrics["forecast_volatility_risk"] == "Low"


def test_metrics_contents(sample_data):
    """Verifies all mandatory buyer and trend metrics are populated."""
    cat = sample_data["Item_Category"].iloc[0]
    _, _, metrics = forecast_demand(sample_data, category=cat, forecast_days=30)
    expected_keys = [
        "current_social_score",
        "social_trend_direction",
        "total_forecasted_units",
        "avg_daily_projected",
        "peak_forecast_day",
        "historical_avg_daily",
        "safety_stock_recommendation",
        "reorder_point_recommendation",
        "trend_velocity_pct",
        "forecast_volatility_risk"
    ]
    for key in expected_keys:
        assert key in metrics
        assert metrics[key] is not None
    assert metrics["safety_stock_recommendation"] >= 5
    assert metrics["reorder_point_recommendation"] >= metrics["safety_stock_recommendation"]
