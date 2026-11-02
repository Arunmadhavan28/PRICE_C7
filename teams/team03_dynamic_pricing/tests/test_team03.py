"""
Unit tests for Team 3: The 'Happy Hour' Dynamic Pricing Engine.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from pricing_engine import load_inventory, apply_pricing_rules, calculate_dynamic_price

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "inventory.json"


@pytest.fixture
def inventory():
    return load_inventory(str(DATA_PATH))


def test_inventory_schema(inventory):
    """Verifies inventory dataset structure."""
    assert len(inventory) >= 5
    for item in inventory:
        assert "Item" in item
        assert "Base_Price" in item
        assert "Current_Stock" in item
        assert item["Base_Price"] > 0


def test_happy_hour_rule():
    """Time > 5 PM (17:00) and Stock > 20 reduces price by 15%."""
    mock_item = {"Item": "Croissant", "Base_Price": 10.0, "Cost_Price": 3.0, "Current_Stock": 25}
    mod, rules = apply_pricing_rules(mock_item, hour_of_day=18, weather="Sunny", current_stock=25)
    assert mod == -0.15
    assert any("Happy Hour" in r for r in rules)

    result = calculate_dynamic_price(mock_item, hour_of_day=18, weather="Sunny", current_stock=25)
    assert result["Dynamic_Price"] == 8.50


def test_weather_rain_surge():
    """Weather == 'Raining' and Item contains 'Hot Coffee' increases price by 10%."""
    mock_item = {"Item": "Hot Coffee", "Base_Price": 10.0, "Cost_Price": 2.0, "Current_Stock": 10}
    mod, rules = apply_pricing_rules(mock_item, hour_of_day=12, weather="Raining", current_stock=10)
    assert mod == 0.10
    assert any("Rainy Day" in r for r in rules)

    result = calculate_dynamic_price(mock_item, hour_of_day=12, weather="Raining", current_stock=10)
    assert result["Dynamic_Price"] == 11.00


def test_heatwave_cold_surge():
    """Weather == 'Heatwave' and Item contains 'Cold Brew' increases price by 15%."""
    mock_item = {"Item": "Cold Brew Nitro", "Base_Price": 10.0, "Cost_Price": 2.0, "Current_Stock": 10}
    mod, rules = apply_pricing_rules(mock_item, hour_of_day=14, weather="Heatwave", current_stock=10)
    assert mod == 0.15
    result = calculate_dynamic_price(mock_item, hour_of_day=14, weather="Heatwave", current_stock=10)
    assert result["Dynamic_Price"] == 11.50


def test_cost_basis_guardrail():
    """Guarantees price never drops below Cost_Price even with extreme discounts."""
    mock_item = {"Item": "Surplus Pastry", "Base_Price": 5.0, "Cost_Price": 4.80, "Current_Stock": 100}
    # -15% on 5.0 would be 4.25, which is lower than Cost_Price 4.80
    result = calculate_dynamic_price(mock_item, hour_of_day=19, weather="Sunny", current_stock=100)
    assert result["Dynamic_Price"] >= mock_item["Cost_Price"]
    assert result["Dynamic_Price"] == 4.80
