"""
Unit tests for Team 6: The 'Drop Culture' Markdown Optimizer.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from optimizer import (
    load_aging_data,
    identify_at_risk_items,
    calculate_recommended_discount,
    project_profit_recovery
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "inventory_aging.csv"


@pytest.fixture
def aging_df():
    return load_aging_data(str(DATA_PATH))


def test_aging_data_schema(aging_df):
    """Verifies schema conformance for inventory aging data."""
    required = ["Item_SKU", "Days_on_Shelf", "Target_Sell_Through_Rate", "Actual_Sell_Through_Rate", "Cost_Basis"]
    for col in required:
        assert col in aging_df.columns
    assert len(aging_df) >= 10
    assert (aging_df["Cost_Basis"] > 0).all()


def test_identify_at_risk_items(aging_df):
    """Verifies at-risk classification flags lagging SKUs."""
    flagged = identify_at_risk_items(aging_df)
    assert "Risk_Status" in flagged.columns
    assert "Sell_Through_Lag" in flagged.columns
    # Check that high lag items are flagged as AT-RISK
    lagging_rows = flagged[flagged["Sell_Through_Lag"] > 0.10]
    assert (lagging_rows["Risk_Status"] != "ON TRACK").all()


def test_tiered_discount_tiers():
    """Validates 30% markdown for > 60 days, 15% for > 30 days, 5% for > 15 days."""
    row_60 = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 40.0, "Days_on_Shelf": 65, "Sell_Through_Lag": 0.10})
    res_60 = calculate_recommended_discount(row_60)
    assert res_60["Recommended_Discount_Pct"] >= 30.0

    row_30 = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 40.0, "Days_on_Shelf": 35, "Sell_Through_Lag": 0.10})
    res_30 = calculate_recommended_discount(row_30)
    assert res_30["Recommended_Discount_Pct"] == 15.0

    row_15 = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 40.0, "Days_on_Shelf": 20, "Sell_Through_Lag": 0.10})
    res_15 = calculate_recommended_discount(row_15)
    assert res_15["Recommended_Discount_Pct"] == 5.0


def test_cost_basis_barrier_protection():
    """Guarantees that clearance price NEVER falls below Cost_Basis."""
    # Even if days > 60 implies 30% off, cost basis of 80 on 100 retail caps discount at 20%
    high_cost_row = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 85.0, "Days_on_Shelf": 80, "Sell_Through_Lag": 0.40})
    res = calculate_recommended_discount(high_cost_row)
    assert res["Clearance_Price"] >= high_cost_row["Cost_Basis"]
    assert res["Clearance_Price"] == 85.0
    assert res["Protected_From_Breach"] is True


def test_profit_recovery_metrics(aging_df):
    """Verifies profit recovery summary calculations."""
    res_df, metrics = project_profit_recovery(aging_df)
    assert len(res_df) == len(aging_df)
    assert metrics["at_risk_sku_count"] > 0
    assert metrics["total_capital_at_risk"] > 0
    assert metrics["total_projected_profit"] >= 0
