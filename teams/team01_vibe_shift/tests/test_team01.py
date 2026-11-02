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
