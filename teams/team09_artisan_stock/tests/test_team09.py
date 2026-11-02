"""
Unit tests for Team 9: The Artisan Safety-Stock Planner.
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
    evaluate_material_status,
    generate_purchase_order
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


def test_runway_calculation():
    """Runway Days = Current Level / Daily Burn Rate."""
    # Current = 50 units, Burn = 2.5 units/day -> Runway = 20 days
    runway = calculate_runway_days(current_level=50, daily_burn_rate=2.5)
    assert runway == 20.0


def test_status_classification():
    """Verifies critical, warning, and healthy status thresholds."""
    # Case 1: Runway <= Lead Time -> CRITICAL
    critical_row = pd.Series({
        "Material_Name": "Wax", "Current_Level": 10.0, "Lead_Time_Days": 14.0,
        "Daily_Burn_Rate": 2.0, "Safety_Stock": 5.0, "Unit_Cost": 4.0
    })
    # Runway is 10/2 = 5 days <= Lead time 14 days -> CRITICAL
    res_crit = evaluate_material_status(critical_row)
    assert res_crit["Status"] == "CRITICAL"

    # Case 2: Healthy stock
    healthy_row = pd.Series({
        "Material_Name": "Canvas", "Current_Level": 100.0, "Lead_Time_Days": 5.0,
        "Daily_Burn_Rate": 2.0, "Safety_Stock": 10.0, "Unit_Cost": 5.0
    })
    # ROP = 5*2 + 10 = 20. Current = 100 > 20 -> HEALTHY
    res_healthy = evaluate_material_status(healthy_row)
    assert res_healthy["Status"] == "HEALTHY"


def test_purchase_order_generator(materials_df):
    """Verifies purchase order generation."""
    evals = [evaluate_material_status(row) for _, row in materials_df.iterrows()]
    items_to_order = [e for e in evals if e["Status"] in ["CRITICAL", "WARNING"]]
    po_text = generate_purchase_order(items_to_order)
    assert "PURCHASE ORDER" in po_text
    assert "GRAND TOTAL" in po_text
    assert len(po_text) > 100
