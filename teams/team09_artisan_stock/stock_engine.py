"""
Artisan Stock Planning Engine for Team 9: The Artisan Safety-Stock Planner.
Calculates Reorder Point (ROP), inventory runway, and generates automated purchase orders.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np

DEFAULT_MATERIALS_PATH = Path(__file__).resolve().parent / "data" / "artisan_materials.csv"


def load_materials_data(filepath: str = None) -> pd.DataFrame:
    """Loads and validates artisan raw materials dataset."""
    path = Path(filepath) if filepath else DEFAULT_MATERIALS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Materials file not found at {path}")
    df = pd.read_csv(path)
    required = ["Material_Name", "Current_Level", "Lead_Time_Days", "Daily_Burn_Rate", "Upcoming_Events"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    return df


def calculate_safety_stock(lead_time_days: float, daily_burn_rate: float, safety_stock_units: float = 0.0) -> float:
    """
    Standard Reorder Point Formula:
    ROP = (Lead Time Days * Daily Burn Rate) + Safety Stock Units
    """
    rop = (float(lead_time_days) * float(daily_burn_rate)) + float(safety_stock_units)
    return round(rop, 1)


def calculate_runway_days(current_level: float, daily_burn_rate: float) -> float:
    """Calculates runway days remaining before complete stockout."""
    if daily_burn_rate <= 0:
        return 999.0
    return round(float(current_level) / float(daily_burn_rate), 1)


def evaluate_material_status(row: pd.Series) -> Dict[str, Any]:
    """
    Evaluates individual material runway and triggers status:
    - CRITICAL (Red): Runway Days <= Lead Time Days (Immediate stockout risk!)
    - WARNING (Yellow): Current Level <= Reorder Point (ROP)
    - HEALTHY (Green): Current Level > ROP
    """
    lead_time = float(row["Lead_Time_Days"])
    burn_rate = float(row["Daily_Burn_Rate"])
    current = float(row["Current_Level"])
    safety = float(row.get("Safety_Stock", burn_rate * 3))

    rop = calculate_safety_stock(lead_time, burn_rate, safety)
    runway_days = calculate_runway_days(current, burn_rate)

    if runway_days <= lead_time:
        status = "CRITICAL"
        color = "#ef4444"
        urgency = "Stockout imminent before shipment arrives!"
    elif current <= rop:
        status = "WARNING"
        color = "#f59e0b"
        urgency = "Approaching reorder point."
    else:
        status = "HEALTHY"
        color = "#00e676"
        urgency = "Adequate inventory on hand."

    # Recommended replenishment order to restore 30-day runway
    target_30_day_stock = (30 * burn_rate) + safety
    recommended_order_units = max(0, int(np.ceil(target_30_day_stock - current)))

    unit_cost = float(row.get("Unit_Cost", 5.0))
    est_po_cost = round(recommended_order_units * unit_cost, 2)

    return {
        "Material_Name": row["Material_Name"],
        "Category": row.get("Category", "Artisan"),
        "Current_Level": current,
        "Lead_Time_Days": lead_time,
        "Daily_Burn_Rate": burn_rate,
        "Reorder_Point": rop,
        "Runway_Days": runway_days,
        "Status": status,
        "Status_Color": color,
        "Urgency_Note": urgency,
        "Recommended_Order_Units": recommended_order_units,
        "Unit_Cost": unit_cost,
        "Estimated_PO_Cost": est_po_cost,
        "Supplier_Contact": row.get("Supplier_Contact", "vendor@supplies.com"),
        "Upcoming_Events": row.get("Upcoming_Events", "Standard Production")
    }


def generate_purchase_order(items_to_reorder: List[Dict[str, Any]]) -> str:
    """
    Generates structured, clean Purchase Order text ready to copy or email to vendors.
    """
    if not items_to_reorder:
        return "No items currently require replenishment."

    po_id = f"PO-{datetime.now().strftime('%Y%m%d')}-001"
    date_str = datetime.now().strftime("%B %d, %Y")

    lines = [
        "=" * 68,
        f"                 PURCHASE ORDER: {po_id}",
        "=" * 68,
        f"Date: {date_str}",
        f"Order Status: APPROVED FOR TRANSMISSION",
        f"Shipment Urgency: EXPEDITE PRIORITY",
        "-" * 68,
        f"{'ITEM / MATERIAL':<34} | {'QTY':>6} | {'UNIT $':>8} | {'TOTAL $':>10}",
        "-" * 68,
    ]

    grand_total = 0.0
    for item in items_to_reorder:
        qty = item["Recommended_Order_Units"]
        unit_price = item["Unit_Cost"]
        line_total = item["Estimated_PO_Cost"]
        grand_total += line_total
        name_short = (item["Material_Name"][:32] + "..") if len(item["Material_Name"]) > 34 else item["Material_Name"]
        lines.append(f"{name_short:<34} | {qty:>6} | ${unit_price:>7.2f} | ${line_total:>9.2f}")

    lines.append("-" * 68)
    lines.append(f"{'GRAND TOTAL ESTIMATED CAPITAL:':<52} ${grand_total:>10.2f}")
    lines.append("=" * 68)
    lines.append("Supplier Delivery Notes: Please confirm lead time and dispatch tracking.")
    lines.append("Generated by: Artisan Safety-Stock Planner AI")

    return "\n".join(lines)
