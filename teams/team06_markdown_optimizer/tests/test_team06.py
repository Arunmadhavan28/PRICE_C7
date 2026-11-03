"""
Unit tests for Team 6: The 'Drop Culture' Markdown Optimizer.
Verifies algorithmic logic, schema conformance, tiered discounts, and strict cost-basis protection.
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
    project_profit_recovery,
    simulate_markdown_pacing,
    calculate_category_summary,
    export_pos_markdown_batch
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
    assert (aging_df["Days_on_Shelf"] >= 0).all()


def test_identify_at_risk_items(aging_df):
    """Verifies at-risk classification flags lagging SKUs."""
    flagged = identify_at_risk_items(aging_df)
    assert "Risk_Status" in flagged.columns
    assert "Sell_Through_Lag" in flagged.columns
    assert "Aging_Tier" in flagged.columns

    # Check that high lag items are flagged as AT-RISK or CRITICAL AT-RISK
    lagging_rows = flagged[flagged["Sell_Through_Lag"] > 0.10]
    assert (lagging_rows["Risk_Status"] != "ON TRACK").all()

    # Check critical condition (lag > 0.35 or lag > 0.20 and days > 60)
    critical_rows = flagged[(flagged["Sell_Through_Lag"] > 0.35) | ((flagged["Sell_Through_Lag"] > 0.20) & (flagged["Days_on_Shelf"] > 60))]
    assert (critical_rows["Risk_Status"] == "CRITICAL AT-RISK").all()


def test_tiered_discount_tiers():
    """Validates 30% markdown for > 60 days, 15% for > 30 days, 5% for > 15 days, 0% for <= 15 days."""
    row_60 = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 40.0, "Days_on_Shelf": 65, "Sell_Through_Lag": 0.10})
    res_60 = calculate_recommended_discount(row_60)
    assert res_60["Recommended_Discount_Pct"] >= 30.0

    row_30 = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 40.0, "Days_on_Shelf": 35, "Sell_Through_Lag": 0.10})
    res_30 = calculate_recommended_discount(row_30)
    assert res_30["Recommended_Discount_Pct"] == 15.0

    row_15 = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 40.0, "Days_on_Shelf": 20, "Sell_Through_Lag": 0.10})
    res_15 = calculate_recommended_discount(row_15)
    assert res_15["Recommended_Discount_Pct"] == 5.0

    row_fresh = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 40.0, "Days_on_Shelf": 10, "Sell_Through_Lag": 0.02})
    res_fresh = calculate_recommended_discount(row_fresh)
    assert res_fresh["Recommended_Discount_Pct"] == 0.0
    assert res_fresh["Clearance_Price"] == 100.0


def test_cost_basis_barrier_protection():
    """Guarantees that clearance price NEVER falls below Cost_Basis under any condition."""
    # Even if days > 60 implies 30% off, cost basis of 85 on 100 retail caps discount at 15%
    high_cost_row = pd.Series({"Retail_Price": 100.0, "Cost_Basis": 85.0, "Days_on_Shelf": 80, "Sell_Through_Lag": 0.40})
    res = calculate_recommended_discount(high_cost_row)
    assert res["Clearance_Price"] >= high_cost_row["Cost_Basis"]
    assert res["Clearance_Price"] == 85.0
    assert res["Protected_From_Breach"] is True
    assert res["Margin_Dollars"] >= 0.0


def test_extreme_tight_margin_protection():
    """Checks an item where retail price is identical to cost basis (0% room for discount)."""
    tight_row = pd.Series({"Retail_Price": 50.0, "Cost_Basis": 50.0, "Days_on_Shelf": 90, "Sell_Through_Lag": 0.50})
    res = calculate_recommended_discount(tight_row)
    assert res["Clearance_Price"] == 50.0
    assert res["Recommended_Discount_Pct"] == 0.0
    assert res["Protected_From_Breach"] is True


def test_profit_recovery_metrics(aging_df):
    """Verifies profit recovery summary calculations."""
    res_df, metrics = project_profit_recovery(aging_df)
    assert len(res_df) == len(aging_df)
    assert metrics["at_risk_sku_count"] > 0
    assert metrics["total_capital_at_risk"] > 0
    assert metrics["total_projected_profit"] >= 0
    assert metrics["total_projected_revenue"] >= metrics["total_capital_at_risk"]
    assert metrics["total_sku_count"] == len(aging_df)
    assert "avg_clearance_discount" in metrics


def test_simulate_markdown_pacing():
    """Verifies multi-week progressive liquidation schedule."""
    sample_row = pd.Series({"Retail_Price": 120.0, "Cost_Basis": 45.0, "Current_Units": 80})
    pacing = simulate_markdown_pacing(sample_row, weeks=4)
    assert len(pacing) == 4
    assert list(pacing["Week"]) == ["Week 1", "Week 2", "Week 3", "Week 4"]
    # Verify progressive clearance discounts
    assert (pacing["Clearance_Price"] >= 45.0).all()
    assert (pacing["Remaining_Units"].iloc[-1] <= pacing["Remaining_Units"].iloc[0])


def test_category_summary(aging_df):
    """Verifies category aggregation calculations."""
    res_df, _ = project_profit_recovery(aging_df)
    cat_summary = calculate_category_summary(res_df)
    assert not cat_summary.empty
    assert "Category" in cat_summary.columns
    assert "Capital_At_Risk" in cat_summary.columns
    assert cat_summary["Total_SKUs"].sum() == len(aging_df)


def test_export_pos_markdown_batch(aging_df):
    """Verifies POS batch export structure."""
    res_df, _ = project_profit_recovery(aging_df)
    pos_batch = export_pos_markdown_batch(res_df)
    assert not pos_batch.empty
    assert "POS_ITEM_SKU" in pos_batch.columns
    assert "CLEARANCE_PRICE" in pos_batch.columns
    assert "ACTION" in pos_batch.columns
    assert (pos_batch["COST_FLOOR_PROTECTED"] == "YES").all()


def test_custom_tier_overrides():
    """Verifies custom tier discount percentages and cost buffer parameters."""
    row = pd.Series({"Retail_Price": 200.0, "Cost_Basis": 80.0, "Days_on_Shelf": 40, "Sell_Through_Lag": 0.05})
    custom_tiers = {"tier_60": 0.40, "tier_30": 0.25, "tier_15": 0.10}
    res = calculate_recommended_discount(row, tier_overrides=custom_tiers, cost_buffer_pct=0.10)
    assert res["Recommended_Discount_Pct"] == 25.0
    assert res["Clearance_Price"] == 150.0
    assert res["Clearance_Price"] >= 80.0 * 1.10
