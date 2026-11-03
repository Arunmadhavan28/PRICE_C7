"""
Unit tests for Team 3: The 'Happy Hour' Dynamic Pricing Engine.
Covers core rubric specifications, edge cases, safeguards, and determinism.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from pricing_engine import (
    load_inventory,
    apply_pricing_rules,
    calculate_dynamic_price,
    MAX_PRICE_MULTIPLIER,
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "inventory.json"


@pytest.fixture
def inventory():
    return load_inventory(str(DATA_PATH))


# ==============================================================================
# Baseline Evaluator Tests (Preserved)
# ==============================================================================

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
    assert any("Cost Basis Floor" in r for r in result["Rules_Triggered"])


# ==============================================================================
# Comprehensive Edge-Case and Boundary Tests
# ==============================================================================

def test_scarcity_premium_rule():
    """Stock between 1 and 4 units (0 < Stock < 5) triggers +10% Scarcity Premium."""
    mock_item = {"Item": "Artisanal Muffin", "Base_Price": 4.0, "Cost_Price": 1.0, "Current_Stock": 3}
    mod, rules = apply_pricing_rules(mock_item, hour_of_day=12, weather="Sunny", current_stock=3)
    assert mod == 0.10
    assert any("Scarcity Premium" in r for r in rules)

    result = calculate_dynamic_price(mock_item, hour_of_day=12, weather="Sunny", current_stock=3)
    assert result["Dynamic_Price"] == 4.40


def test_morning_rush_rule():
    """Morning Commute Rush (7 AM - 9 AM) adds +5% surge for Beverages only."""
    beverage_item = {"Item": "Flat White", "Category": "Beverages", "Base_Price": 5.0, "Cost_Price": 1.5, "Current_Stock": 15}
    pastry_item = {"Item": "Pain au Chocolat", "Category": "Pastry", "Base_Price": 4.0, "Cost_Price": 1.2, "Current_Stock": 15}

    # At 8 AM, beverage gets +5%
    mod_bev, rules_bev = apply_pricing_rules(beverage_item, hour_of_day=8, weather="Clear", current_stock=15)
    assert mod_bev == 0.05
    assert any("Morning Rush" in r for r in rules_bev)

    # At 8 AM, pastry does NOT get morning rush
    mod_pas, rules_pas = apply_pricing_rules(pastry_item, hour_of_day=8, weather="Clear", current_stock=15)
    assert mod_pas == 0.00
    assert "Standard Base Rate (0%)" in rules_pas


def test_combined_rules_stacking():
    """Evaluates multiple simultaneous rules: Happy Hour Clearance (-15%) + Rain Surge (+10%)."""
    mock_item = {
        "Item": "Hot Spiced Chai",
        "Category": "Beverages",
        "Base_Price": 10.0,
        "Cost_Price": 2.0,
        "Current_Stock": 30
    }
    # 18:00 (>= 17) and Stock 30 (> 20) -> -15%
    # Weather 'Raining' and Item has 'Hot' -> +10%
    # Net modifier: -15% + 10% = -5% (-0.05)
    mod, rules = apply_pricing_rules(mock_item, hour_of_day=18, weather="Raining", current_stock=30)
    assert mod == -0.05
    assert len(rules) == 2
    assert any("Happy Hour" in r for r in rules)
    assert any("Rainy Day" in r for r in rules)

    result = calculate_dynamic_price(mock_item, hour_of_day=18, weather="Raining", current_stock=30)
    assert result["Dynamic_Price"] == 9.50


def test_zero_and_negative_inventory():
    """Zero and negative inventory must not trigger scarcity surges or clearance discounts."""
    mock_zero = {"Item": "Latte", "Base_Price": 5.0, "Cost_Price": 1.5, "Current_Stock": 0}
    mock_neg = {"Item": "Latte", "Base_Price": 5.0, "Cost_Price": 1.5, "Current_Stock": -5}

    # Stock 0: 0 < stock < 5 is False; stock > 20 is False
    mod_0, rules_0 = apply_pricing_rules(mock_zero, hour_of_day=19, weather="Sunny", current_stock=0)
    assert mod_0 == 0.0
    assert "Standard Base Rate (0%)" in rules_0

    # Negative stock: Handled safely without triggering rules
    mod_neg, rules_neg = apply_pricing_rules(mock_neg, hour_of_day=19, weather="Sunny", current_stock=-5)
    assert mod_neg == 0.0


def test_boundary_hours():
    """Tests boundary clock transitions (hour 16 vs 17 for happy hour; hours 6, 7, 9, 10 for rush)."""
    bev = {"Item": "Latte", "Category": "Beverages", "Base_Price": 5.0, "Current_Stock": 25}

    # Happy Hour boundary: 16:00 is normal; 17:00 triggers clearance
    mod_16, _ = apply_pricing_rules(bev, hour_of_day=16, weather="Sunny", current_stock=25)
    mod_17, _ = apply_pricing_rules(bev, hour_of_day=17, weather="Sunny", current_stock=25)
    assert mod_16 == 0.0
    assert mod_17 == -0.15

    # Morning rush boundary: 6:00 (no rush), 7:00 (rush), 9:00 (rush), 10:00 (no rush)
    mod_6, _ = apply_pricing_rules(bev, hour_of_day=6, weather="Sunny", current_stock=10)
    mod_7, _ = apply_pricing_rules(bev, hour_of_day=7, weather="Sunny", current_stock=10)
    mod_9, _ = apply_pricing_rules(bev, hour_of_day=9, weather="Sunny", current_stock=10)
    mod_10, _ = apply_pricing_rules(bev, hour_of_day=10, weather="Sunny", current_stock=10)
    assert mod_6 == 0.0
    assert mod_7 == 0.05
    assert mod_9 == 0.05
    assert mod_10 == 0.0


def test_deterministic_output():
    """Verifies that calling calculate_dynamic_price repeatedly yields identical outputs."""
    item = {"Item": "Cold Brew Nitro", "Base_Price": 6.0, "Cost_Price": 1.8, "Current_Stock": 15}
    results = [calculate_dynamic_price(item, hour_of_day=14, weather="Heatwave", current_stock=15) for _ in range(50)]
    first = results[0]
    for r in results[1:]:
        assert r == first


def test_extreme_and_malformed_inputs():
    """Safely handles missing fields, None inputs, and malformed data types."""
    # None item dictionary
    res_none = calculate_dynamic_price(None, hour_of_day=12, weather="Sunny")
    assert isinstance(res_none, dict)
    assert res_none["Dynamic_Price"] >= 0.0

    # Malformed data types
    malformed = {
        "Item": "Quirk Item",
        "Base_Price": "invalid_number",
        "Cost_Price": None,
        "Current_Stock": "ten"
    }
    res_malformed = calculate_dynamic_price(malformed, hour_of_day=99, weather=None, current_stock="bogus")
    assert isinstance(res_malformed, dict)
    assert res_malformed["Dynamic_Price"] == 0.0

    # Negative base price clamped safely
    neg_item = {"Item": "Glitch", "Base_Price": -10.0, "Cost_Price": -2.0}
    res_neg = calculate_dynamic_price(neg_item, hour_of_day=12, weather="Sunny")
    assert res_neg["Base_Price"] == 0.0
    assert res_neg["Dynamic_Price"] >= 0.0


def test_price_ceiling_guardrail():
    """Ensures dynamic price never exceeds the safety ceiling (MAX_PRICE_MULTIPLIER * Base_Price)."""
    item = {"Item": "Hot Specialty Coffee", "Category": "Beverages", "Base_Price": 10.0, "Cost_Price": 2.0, "Current_Stock": 3}
    # Hour 8 (+5% rush), Raining (+10% rain), Stock 3 (+10% scarcity) -> +25% raw price = 12.50
    res = calculate_dynamic_price(item, hour_of_day=8, weather="Raining", current_stock=3)
    assert res["Dynamic_Price"] <= item["Base_Price"] * MAX_PRICE_MULTIPLIER


def test_margin_and_delta_calculations():
    """Verifies precision and accuracy of dollar and percentage margin outputs."""
    item = {"Item": "Bagel", "Base_Price": 4.0, "Cost_Price": 1.0, "Current_Stock": 10}
    res = calculate_dynamic_price(item, hour_of_day=12, weather="Sunny", current_stock=10)
    assert res["Dynamic_Price"] == 4.00
    assert res["Price_Delta_Pct"] == 0.0
    assert res["Margin_Dollar"] == 3.00
    assert res["Margin_Pct"] == 75.0


def test_load_inventory_file_not_found():
    """load_inventory must raise FileNotFoundError for nonexistent paths."""
    with pytest.raises(FileNotFoundError):
        load_inventory("non_existent_inventory_path.json")
