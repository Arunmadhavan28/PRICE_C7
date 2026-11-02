"""
Pricing Engine for Team 3: The 'Happy Hour' Dynamic Pricing Engine.
Computes real-time price modifiers based on time of day, weather, and stock constraints.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

DEFAULT_INVENTORY_PATH = Path(__file__).resolve().parent / "data" / "inventory.json"


def load_inventory(filepath: str = None) -> List[Dict[str, Any]]:
    """Loads and validates cafe/boutique inventory."""
    path = Path(filepath) if filepath else DEFAULT_INVENTORY_PATH
    if not path.exists():
        raise FileNotFoundError(f"Inventory file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Inventory must be a list of items.")
    return data


def apply_pricing_rules(
    item_dict: Dict[str, Any],
    hour_of_day: int,
    weather: str,
    current_stock: int = None
) -> Tuple[float, List[str]]:
    """
    Evaluates rule-based logic gates to compute percentage price modifier.

    Logic Gates:
    1. Happy Hour Clearance: If Hour > 17 (5 PM) and Stock > 20 -> -15%
    2. Rain Warmth Surge: If Weather == "Raining" and Item contains "Hot" or "Coffee" or "Chai" -> +10%
    3. Heatwave Refreshment Surge: If Weather == "Heatwave" and Item contains "Cold" or "Iced" or "Nitro" -> +15%
    4. Scarcity Premium: If Stock < 5 -> +10%
    5. Early Morning Commute Rush: If 7 <= Hour <= 9 and Category == "Beverages" -> +5%

    Returns:
        (total_percentage_modifier, list_of_triggered_rule_descriptions)
    """
    stock = current_stock if current_stock is not None else item_dict.get("Current_Stock", 0)
    name = item_dict.get("Item", "")
    category = item_dict.get("Category", "")

    modifier = 0.0
    rules_triggered = []

    # Rule 1: Happy Hour Clearance (> 5 PM and surplus stock)
    if hour_of_day >= 17 and stock > 20:
        modifier -= 0.15
        rules_triggered.append("🌙 Happy Hour Surplus Clearance (-15%)")

    # Rule 2: Rain Weather Surge for Hot Comfort Items
    if weather.lower() == "raining" and any(k in name.lower() for k in ["hot", "coffee", "chai", "espresso"]):
        modifier += 0.10
        rules_triggered.append("🌧️ Rainy Day Warmth Surge (+10%)")

    # Rule 3: Heatwave Surge for Chilled Items
    if weather.lower() == "heatwave" and any(k in name.lower() for k in ["cold", "iced", "nitro", "matcha"]):
        modifier += 0.15
        rules_triggered.append("☀️ Heatwave Refreshment Surge (+15%)")

    # Rule 4: Scarcity Premium (Low stock rush)
    if 0 < stock < 5:
        modifier += 0.10
        rules_triggered.append("🔥 High-Demand Scarcity Premium (+10%)")

    # Rule 5: Morning Commute Rush (7 AM - 9 AM)
    if 7 <= hour_of_day <= 9 and category == "Beverages":
        modifier += 0.05
        rules_triggered.append("☕ Morning Rush Surge (+5%)")

    if not rules_triggered:
        rules_triggered.append("⚖️ Standard Base Rate (0%)")

    return round(modifier, 4), rules_triggered


def calculate_dynamic_price(
    item_dict: Dict[str, Any],
    hour_of_day: int,
    weather: str,
    current_stock: int = None
) -> Dict[str, Any]:
    """
    Computes final dynamic price with cost-basis guardrail.
    Guarantees: Final Price >= Cost_Price.
    """
    base_price = float(item_dict["Base_Price"])
    cost_price = float(item_dict.get("Cost_Price", base_price * 0.3))
    stock = current_stock if current_stock is not None else item_dict.get("Current_Stock", 0)

    modifier, rules = apply_pricing_rules(item_dict, hour_of_day, weather, stock)

    raw_price = base_price * (1.0 + modifier)

    # Cost-basis floor guardrail
    final_price = max(cost_price, raw_price)
    floor_hit = final_price == cost_price and raw_price < cost_price

    if floor_hit:
        rules.append("🛡️ Cost Basis Floor Guardrail Activated")

    delta_pct = ((final_price - base_price) / base_price) * 100
    margin_dollar = final_price - cost_price
    margin_pct = (margin_dollar / final_price) * 100

    return {
        "Item": item_dict["Item"],
        "Category": item_dict.get("Category", "General"),
        "Base_Price": base_price,
        "Current_Stock": stock,
        "Dynamic_Price": round(final_price, 2),
        "Price_Delta_Pct": round(delta_pct, 1),
        "Margin_Dollar": round(margin_dollar, 2),
        "Margin_Pct": round(margin_pct, 1),
        "Rules_Triggered": rules
    }
