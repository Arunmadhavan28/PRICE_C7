"""
Pricing Engine for Team 3: The 'Happy Hour' Dynamic Pricing Engine.
Computes real-time price modifiers based on time of day, weather, and stock constraints.

Design Principles:
- Deterministic: Identical inputs always produce identical pricing recommendations.
- Guardrail-Enforced: Final recommended selling price never falls below product cost basis.
- Resilient: Handles malformed, null, negative, or boundary inputs gracefully.
- Transparent: Returns granular audit trail of all triggered pricing rules.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

DEFAULT_INVENTORY_PATH = Path(__file__).resolve().parent / "data" / "inventory.json"

# Pricing boundary safeguards
MAX_PRICE_MULTIPLIER = 2.0  # Guardrail: Maximum surge ceiling (+100% of base price)
DEFAULT_COST_MARGIN_RATIO = 0.30  # Standard cafe industry assumption: 30% cost basis


def load_inventory(filepath: str = None) -> List[Dict[str, Any]]:
    """
    Loads and validates cafe/boutique inventory from a JSON file.

    Args:
        filepath: Optional path to JSON file. Defaults to data/inventory.json.

    Returns:
        List of item dictionaries validated against schema.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file is not valid JSON or root is not a list.
    """
    path = Path(filepath) if filepath else DEFAULT_INVENTORY_PATH
    if not path.exists():
        raise FileNotFoundError(f"Inventory file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON in inventory file: {e}")

    if not isinstance(data, list):
        raise ValueError("Inventory must be a list of item objects.")

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
    1. Happy Hour Clearance: If Hour >= 17 (5 PM) and Stock > 20 -> -15% discount
    2. Rain Warmth Surge: If Weather == "Raining" and Item contains "hot", "coffee", "chai", "espresso" -> +10% surge
    3. Heatwave Refreshment Surge: If Weather == "Heatwave" and Item contains "cold", "iced", "nitro", "matcha" -> +15% surge
    4. Scarcity Premium: If 0 < Stock < 5 -> +10% demand premium
    5. Early Morning Commute Rush: If 7 <= Hour <= 9 and Category == "Beverages" -> +5% morning rush surge

    Safeguards & Normalization:
    - Hour is normalized to 0-23 range.
    - Weather string is trimmed and case-insensitive.
    - Stock is safely cast to integer (negative stock does not trigger scarcity or clearance).

    Returns:
        (total_percentage_modifier, list_of_triggered_rule_descriptions)
    """
    if not isinstance(item_dict, dict):
        item_dict = {}

    # Safe stock resolution
    raw_stock = current_stock if current_stock is not None else item_dict.get("Current_Stock", 0)
    try:
        stock = int(raw_stock)
    except (ValueError, TypeError):
        stock = 0

    # Safe hour resolution (clamp to 0-23)
    try:
        hour = int(hour_of_day)
        hour = max(0, min(23, hour))
    except (ValueError, TypeError):
        hour = 12

    # Safe weather string resolution
    weather_clean = str(weather).strip().lower() if weather is not None else ""

    name = str(item_dict.get("Item", "")).lower()
    category = str(item_dict.get("Category", ""))

    modifier = 0.0
    rules_triggered: List[str] = []

    # Rule 1: Happy Hour Clearance (>= 5 PM and surplus inventory)
    if hour >= 17 and stock > 20:
        modifier -= 0.15
        rules_triggered.append("Happy Hour Surplus Clearance (-15%)")

    # Rule 2: Rain Weather Surge for Hot Comfort Items
    if weather_clean == "raining" and any(k in name for k in ["hot", "coffee", "chai", "espresso"]):
        modifier += 0.10
        rules_triggered.append("Rainy Day Warmth Surge (+10%)")

    # Rule 3: Heatwave Surge for Chilled Items
    if weather_clean == "heatwave" and any(k in name for k in ["cold", "iced", "nitro", "matcha"]):
        modifier += 0.15
        rules_triggered.append("Heatwave Refreshment Surge (+15%)")

    # Rule 4: Scarcity Premium (Low stock rush; strictly positive stock below 5 units)
    if 0 < stock < 5:
        modifier += 0.10
        rules_triggered.append("High-Demand Scarcity Premium (+10%)")

    # Rule 5: Morning Commute Rush (7 AM - 9 AM for Beverages)
    if 7 <= hour <= 9 and category == "Beverages":
        modifier += 0.05
        rules_triggered.append("Morning Rush Surge (+5%)")

    if not rules_triggered:
        rules_triggered.append("Standard Base Rate (0%)")

    return round(modifier, 4), rules_triggered


def calculate_dynamic_price(
    item_dict: Dict[str, Any],
    hour_of_day: int,
    weather: str,
    current_stock: int = None
) -> Dict[str, Any]:
    """
    Computes final dynamic price with cost-basis floor and surge ceiling guardrails.

    Guarantees:
    - Cost Floor: Final Price >= Cost_Price (prevents margin erosion).
    - Ceiling Bound: Raw Price <= Base_Price * MAX_PRICE_MULTIPLIER.
    - Zero/Negative Base Price handled safely without division errors.
    - Deterministic numerical calculations.

    Returns:
        Dict with keys:
            Item, Category, Base_Price, Cost_Price, Current_Stock,
            Dynamic_Price, Price_Delta_Pct, Margin_Dollar, Margin_Pct,
            Rules_Triggered
    """
    if not isinstance(item_dict, dict):
        item_dict = {}

    # Safe Base Price parsing
    raw_base = item_dict.get("Base_Price", 0.0)
    try:
        base_price = max(0.0, float(raw_base))
    except (ValueError, TypeError):
        base_price = 0.0

    # Safe Cost Price parsing (default assumption: 30% cost ratio if omitted)
    raw_cost = item_dict.get("Cost_Price")
    if raw_cost is not None:
        try:
            cost_price = max(0.0, float(raw_cost))
        except (ValueError, TypeError):
            cost_price = round(base_price * DEFAULT_COST_MARGIN_RATIO, 2)
    else:
        cost_price = round(base_price * DEFAULT_COST_MARGIN_RATIO, 2)

    # Safe Stock resolution
    raw_stock = current_stock if current_stock is not None else item_dict.get("Current_Stock", 0)
    try:
        stock = int(raw_stock)
    except (ValueError, TypeError):
        stock = 0

    # Calculate modifiers and rules
    modifier, rules = apply_pricing_rules(
        item_dict=item_dict,
        hour_of_day=hour_of_day,
        weather=weather,
        current_stock=stock
    )

    # Compute raw price with surge ceiling safeguard
    raw_price = base_price * (1.0 + modifier)
    max_price_ceiling = base_price * MAX_PRICE_MULTIPLIER
    if raw_price > max_price_ceiling:
        raw_price = max_price_ceiling
        rules.append(f"Price Ceiling Guardrail Enforced (+{int((MAX_PRICE_MULTIPLIER-1)*100)}% Max)")

    # Cost-basis floor guardrail enforcement
    final_price = max(cost_price, raw_price)
    floor_hit = final_price == cost_price and raw_price < cost_price

    if floor_hit:
        rules.append("Cost Basis Floor Guardrail Activated")

    # Financial metric calculations with zero-division protection
    delta_pct = ((final_price - base_price) / base_price * 100) if base_price > 0 else 0.0
    margin_dollar = final_price - cost_price
    margin_pct = (margin_dollar / final_price * 100) if final_price > 0 else 0.0

    return {
        "Item": item_dict.get("Item", "Unknown Item"),
        "Category": item_dict.get("Category", "General"),
        "Base_Price": base_price,
        "Cost_Price": cost_price,
        "Current_Stock": stock,
        "Dynamic_Price": round(final_price, 2),
        "Price_Delta_Pct": round(delta_pct, 1),
        "Margin_Dollar": round(margin_dollar, 2),
        "Margin_Pct": round(margin_pct, 1),
        "Rules_Triggered": rules
    }
