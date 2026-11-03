"""
Unit tests for Team 9: The Artisan Safety-Stock Planner.
Verifies ROP mathematical correctness, runway calculations, status classification,
risk index scoring, event surge simulations, and automated purchase order generation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from stock_engine import (
    load_materials_data,
    calculate_safety_stock,
    calculate_runway_days,
    calculate_stockout_risk_score,
    evaluate_material_status,
    simulate_event_surge,
    calculate_portfolio_summary,
    generate_purchase_order,
    generate_purchase_order_dataframe
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "artisan_materials.csv"


@pytest.fixture
def materials_df():
    return load_materials_data(str(DATA_PATH))


def test_materials_schema(materials_df):
    """Verifies schema conformance for artisan materials data."""
    required = ["Material_Name", "Current_Level", "Lead_Time_Days", "Daily_Burn_Rate", "Upcoming_Events"]
    for col in required:
        assert col in materials_df.columns
    assert len(materials_df) >= 8
    assert (materials_df["Current_Level"] >= 0).all()
    assert (materials_df["Daily_Burn_Rate"] > 0).all()


def test_reorder_point_formula():
    """ROP = (Lead Time * Daily Burn Rate) + Safety Stock."""
    # Lead time = 10 days, burn rate = 5 units/day, safety stock = 20 units -> ROP = 50 + 20 = 70
    rop = calculate_safety_stock(lead_time_days=10, daily_burn_rate=5, safety_stock_units=20)
    assert rop == 70.0

    # Zero safety stock
    rop_zero_safety = calculate_safety_stock(lead_time_days=7, daily_burn_rate=3, safety_stock_units=0)
    assert rop_zero_safety == 21.0


def test_runway_calculation():
    """Runway Days = Current Level / Daily Burn Rate."""
    # Current = 50 units, Burn = 2.5 units/day -> Runway = 20 days
    runway = calculate_runway_days(current_level=50, daily_burn_rate=2.5)
    assert runway == 20.0

    # Edge case: zero burn rate produces safe long runway
    runway_zero = calculate_runway_days(current_level=50, daily_burn_rate=0.0)
    assert runway_zero == 999.0


def test_status_classification():
    """Verifies critical, warning, and healthy status thresholds."""
    # Case 1: Runway <= Lead Time -> CRITICAL
    critical_row = pd.Series({
        "Material_Name": "Soy Wax", "Current_Level": 10.0, "Lead_Time_Days": 14.0,
        "Daily_Burn_Rate": 2.0, "Safety_Stock": 5.0, "Unit_Cost": 4.0
    })
    # Runway is 10/2 = 5 days <= Lead time 14 days -> CRITICAL
    res_crit = evaluate_material_status(critical_row)
    assert res_crit["Status"] == "CRITICAL"
    assert res_crit["Risk_Score"] >= 75.0

    # Case 2: Warning (Current <= ROP, but Runway > Lead Time)
    warning_row = pd.Series({
        "Material_Name": "Brass Hooks", "Current_Level": 25.0, "Lead_Time_Days": 4.0,
        "Daily_Burn_Rate": 5.0, "Safety_Stock": 10.0, "Unit_Cost": 0.35
    })
    # Runway = 25/5 = 5 days > Lead Time 4 days.
    # ROP = 4*5 + 10 = 30 units. Current 25 <= ROP 30 -> WARNING
    res_warn = evaluate_material_status(warning_row)
    assert res_warn["Status"] == "WARNING"

    # Case 3: Healthy stock
    healthy_row = pd.Series({
        "Material_Name": "Canvas", "Current_Level": 100.0, "Lead_Time_Days": 5.0,
        "Daily_Burn_Rate": 2.0, "Safety_Stock": 10.0, "Unit_Cost": 5.0
    })
    # ROP = 5*2 + 10 = 20. Current = 100 > 20 -> HEALTHY
    res_healthy = evaluate_material_status(healthy_row)
    assert res_healthy["Status"] == "HEALTHY"
    assert res_healthy["Risk_Score"] < 50.0


def test_event_surge_simulation():
    """Simulates demand surge multiplier for holiday markets."""
    baseline_row = pd.Series({
        "Material_Name": "Leather", "Current_Level": 30.0, "Lead_Time_Days": 7.0,
        "Daily_Burn_Rate": 2.0, "Safety_Stock": 10.0, "Unit_Cost": 12.0
    })
    base_eval = evaluate_material_status(baseline_row, surge_multiplier=1.0)
    surge_eval = simulate_event_surge(baseline_row, surge_multiplier=2.0)

    # Surge doubles burn rate, decreases runway
    assert surge_eval["Daily_Burn_Rate"] == 4.0
    assert surge_eval["Runway_Days"] < base_eval["Runway_Days"]
    assert surge_eval["Reorder_Point"] > base_eval["Reorder_Point"]


def test_portfolio_summary(materials_df):
    """Verifies aggregate portfolio analytics."""
    evals = [evaluate_material_status(row) for _, row in materials_df.iterrows()]
    summary = calculate_portfolio_summary(evals)

    assert summary["total_materials"] == len(materials_df)
    assert summary["total_po_capital"] >= 0.0
    assert summary["total_asset_value"] > 0.0
    assert summary["average_runway_days"] > 0.0


def test_purchase_order_generator(materials_df):
    """Verifies plain text and tabular purchase order generation."""
    evals = [evaluate_material_status(row) for _, row in materials_df.iterrows()]
    items_to_order = [e for e in evals if e["Status"] in ["CRITICAL", "WARNING"]]
    po_text = generate_purchase_order(items_to_order)

    assert "PURCHASE ORDER" in po_text
    assert "GRAND TOTAL" in po_text
    assert len(po_text) > 100

    # Empty order check
    assert "No items currently require replenishment" in generate_purchase_order([])

    # DataFrame generator check
    po_df = generate_purchase_order_dataframe(items_to_order)
    assert isinstance(po_df, pd.DataFrame)
    assert len(po_df) == len(items_to_order)
    assert "Material_Name" in po_df.columns
