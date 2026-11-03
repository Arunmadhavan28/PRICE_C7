"""
Artisan Stock Planning Engine for Team 9: The Artisan Safety-Stock Planner.
Calculates Reorder Point (ROP), inventory runway, and generates automated purchase orders.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

DEFAULT_MATERIALS_PATH = Path(__file__).resolve().parent / "data" / "artisan_materials.csv"


def load_materials_data(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Loads and validates the artisan raw materials dataset.
    Ensures required schema columns exist and validates numeric data types.
    """
    path = Path(filepath) if filepath else DEFAULT_MATERIALS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Materials file not found at {path}")

    df = pd.read_csv(path)
    required = ["Material_Name", "Current_Level", "Lead_Time_Days", "Daily_Burn_Rate", "Upcoming_Events"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Ensure non-negative numerical values
    df["Current_Level"] = pd.to_numeric(df["Current_Level"], errors="coerce").fillna(0.0)
    df["Lead_Time_Days"] = pd.to_numeric(df["Lead_Time_Days"], errors="coerce").fillna(1.0)
    df["Daily_Burn_Rate"] = pd.to_numeric(df["Daily_Burn_Rate"], errors="coerce").fillna(0.1)
    if "Safety_Stock" in df.columns:
        df["Safety_Stock"] = pd.to_numeric(df["Safety_Stock"], errors="coerce").fillna(0.0)
    if "Unit_Cost" in df.columns:
        df["Unit_Cost"] = pd.to_numeric(df["Unit_Cost"], errors="coerce").fillna(1.0)

    return df


def calculate_safety_stock(lead_time_days: float, daily_burn_rate: float, safety_stock_units: float = 0.0) -> float:
    """
    Standard Reorder Point (ROP) Formula:
    ROP = (Lead Time Days * Daily Burn Rate) + Safety Stock Units
    """
    lead_time = max(0.0, float(lead_time_days))
    burn_rate = max(0.0, float(daily_burn_rate))
    safety = max(0.0, float(safety_stock_units))
    rop = (lead_time * burn_rate) + safety
    return round(rop, 1)


def calculate_runway_days(current_level: float, daily_burn_rate: float) -> float:
    """
    Calculates runway days remaining before complete stockout:
    Runway Days = Current Stock / Daily Burn Rate
    """
    current = max(0.0, float(current_level))
    burn_rate = float(daily_burn_rate)
    if burn_rate <= 0:
        return 999.0
    return round(current / burn_rate, 1)


def calculate_stockout_risk_score(
    current_level: float,
    lead_time_days: float,
    daily_burn_rate: float,
    safety_stock: float = 0.0
) -> float:
    """
    Calculates an intuitive Stockout Risk Index (0.0% to 100.0%):
    - 100% Risk: Current level is exhausted before shipment arrives.
    - 50%-99% Risk: Current level is below or near Reorder Point.
    - < 50% Risk: Buffer is comfortably above Reorder Point.
    """
    lead_time = max(0.1, float(lead_time_days))
    burn_rate = max(0.01, float(daily_burn_rate))
    current = max(0.0, float(current_level))
    runway = calculate_runway_days(current, burn_rate)

    if runway <= 0.0:
        return 100.0
    if runway <= lead_time:
        # Severe danger: stock depletes before new shipment arrives
        ratio = runway / lead_time
        return round(100.0 - (ratio * 25.0), 1)  # 75.0% - 100.0%

    rop = calculate_safety_stock(lead_time, burn_rate, safety_stock)
    if current <= rop:
        # Warning zone: between lead time and ROP
        gap = rop - current
        factor = gap / max(1.0, rop)
        return round(50.0 + (factor * 25.0), 1)  # 50.0% - 75.0%

    # Safe zone: above ROP
    excess_ratio = current / max(1.0, rop)
    risk = max(5.0, 50.0 / excess_ratio)
    return round(risk, 1)


def evaluate_material_status(row: pd.Series, surge_multiplier: float = 1.0) -> Dict[str, Any]:
    """
    Evaluates individual material runway and triggers actionable status:
    - CRITICAL (Red): Runway Days <= Lead Time Days (Immediate stockout risk!)
    - WARNING (Yellow): Current Level <= Reorder Point (ROP)
    - HEALTHY (Green): Current Level > ROP

    Supports optional surge_multiplier to model event / festival demand spikes.
    """
    lead_time = max(1.0, float(row["Lead_Time_Days"]))
    base_burn = max(0.01, float(row["Daily_Burn_Rate"]))
    burn_rate = round(base_burn * max(0.1, float(surge_multiplier)), 2)
    current = max(0.0, float(row["Current_Level"]))
    safety = float(row.get("Safety_Stock", base_burn * 3))

    rop = calculate_safety_stock(lead_time, burn_rate, safety)
    runway_days = calculate_runway_days(current, burn_rate)
    risk_score = calculate_stockout_risk_score(current, lead_time, burn_rate, safety)

    if runway_days <= lead_time:
        status = "CRITICAL"
        color = "#ef4444"
        urgency = "Stockout imminent before shipment arrives! Immediate reorder required."
    elif current <= rop:
        status = "WARNING"
        color = "#f59e0b"
        urgency = "Approaching reorder point. Schedule replenishment order."
    else:
        status = "HEALTHY"
        color = "#10b981"
        urgency = "Adequate inventory on hand. Optimal runway buffer."

    # Recommended replenishment order to restore standard 30-day runway
    target_30_day_stock = (30 * burn_rate) + safety
    recommended_order_units = max(0, int(np.ceil(target_30_day_stock - current)))

    unit_cost = float(row.get("Unit_Cost", 5.0))
    est_po_cost = round(recommended_order_units * unit_cost, 2)
    current_asset_value = round(current * unit_cost, 2)

    return {
        "Material_Name": str(row["Material_Name"]),
        "Category": str(row.get("Category", "Artisan")),
        "Current_Level": current,
        "Lead_Time_Days": lead_time,
        "Daily_Burn_Rate": burn_rate,
        "Base_Burn_Rate": base_burn,
        "Safety_Stock": safety,
        "Reorder_Point": rop,
        "Runway_Days": runway_days,
        "Risk_Score": risk_score,
        "Status": status,
        "Status_Color": color,
        "Urgency_Note": urgency,
        "Recommended_Order_Units": recommended_order_units,
        "Unit_Cost": unit_cost,
        "Estimated_PO_Cost": est_po_cost,
        "Current_Asset_Value": current_asset_value,
        "Supplier_Contact": str(row.get("Supplier_Contact", "vendor@supplies.com")),
        "Upcoming_Events": str(row.get("Upcoming_Events", "Standard Production"))
    }


def simulate_event_surge(row: pd.Series, surge_multiplier: float = 1.5) -> Dict[str, Any]:
    """
    Simulates demand surge impact for artisan markets, holiday fairs, and pop-up events.
    """
    return evaluate_material_status(row, surge_multiplier=surge_multiplier)


def calculate_portfolio_summary(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates high-level portfolio metrics for the entire artisan workshop.
    """
    if not evaluations:
        return {
            "total_materials": 0,
            "critical_count": 0,
            "warning_count": 0,
            "healthy_count": 0,
            "total_po_capital": 0.0,
            "total_asset_value": 0.0,
            "average_runway_days": 0.0,
            "average_risk_score": 0.0
        }

    critical = [e for e in evaluations if e["Status"] == "CRITICAL"]
    warning = [e for e in evaluations if e["Status"] == "WARNING"]
    healthy = [e for e in evaluations if e["Status"] == "HEALTHY"]
    reorder_items = [e for e in evaluations if e["Status"] in ["CRITICAL", "WARNING"]]

    total_po_capital = sum(e["Estimated_PO_Cost"] for e in reorder_items)
    total_asset_value = sum(e["Current_Asset_Value"] for e in evaluations)
    avg_runway = np.mean([e["Runway_Days"] for e in evaluations])
    avg_risk = np.mean([e["Risk_Score"] for e in evaluations])

    return {
        "total_materials": len(evaluations),
        "critical_count": len(critical),
        "warning_count": len(warning),
        "healthy_count": len(healthy),
        "total_po_capital": round(total_po_capital, 2),
        "total_asset_value": round(total_asset_value, 2),
        "average_runway_days": round(avg_runway, 1),
        "average_risk_score": round(avg_risk, 1)
    }


def generate_purchase_order(items_to_reorder: List[Dict[str, Any]]) -> str:
    """
    Generates structured, clean Purchase Order text ready to copy, email, or transmit to vendors.
    """
    if not items_to_reorder:
        return "No items currently require replenishment."

    po_id = f"PO-{datetime.now().strftime('%Y%m%d')}-001"
    date_str = datetime.now().strftime("%B %d, %Y")

    lines = [
        "=" * 72,
        f"                 PURCHASE ORDER: {po_id}",
        "=" * 72,
        f"Date: {date_str}",
        f"Issuing Entity: Artisan Workshop & Studio Operations",
        f"Order Status: APPROVED FOR TRANSMISSION",
        f"Shipment Urgency: EXPEDITE PRIORITY (Supply Chain Risk Protected)",
        "-" * 72,
        f"{'ITEM / MATERIAL':<36} | {'QTY':>6} | {'UNIT $':>8} | {'TOTAL $':>12}",
        "-" * 72,
    ]

    grand_total = 0.0
    for item in items_to_reorder:
        qty = item["Recommended_Order_Units"]
        unit_price = item["Unit_Cost"]
        line_total = item["Estimated_PO_Cost"]
        grand_total += line_total
        name_short = (item["Material_Name"][:34] + "..") if len(item["Material_Name"]) > 36 else item["Material_Name"]
        lines.append(f"{name_short:<36} | {qty:>6} | ${unit_price:>7.2f} | ${line_total:>11.2f}")

    lines.append("-" * 72)
    lines.append(f"{'GRAND TOTAL ESTIMATED CAPITAL:':<54} ${grand_total:>12.2f}")
    lines.append("=" * 72)
    lines.append("Supplier Delivery Instructions: Please verify lead times and provide tracking.")
    lines.append("Payment Terms: Net 30 upon delivery confirmation.")
    lines.append("Generated by: The Artisan Safety-Stock Planner AI (Team 9)")

    return "\n".join(lines)


def generate_purchase_order_dataframe(items_to_reorder: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Converts replenishment items into a structured pandas DataFrame for CSV / Excel export.
    """
    if not items_to_reorder:
        return pd.DataFrame(columns=[
            "Material_Name", "Category", "Current_Level", "Recommended_Order_Units",
            "Unit_Cost", "Estimated_PO_Cost", "Supplier_Contact", "Status"
        ])

    rows = []
    for item in items_to_reorder:
        rows.append({
            "Material_Name": item["Material_Name"],
            "Category": item["Category"],
            "Current_Level": item["Current_Level"],
            "Recommended_Order_Units": item["Recommended_Order_Units"],
            "Unit_Cost": f"${item['Unit_Cost']:.2f}",
            "Estimated_PO_Cost": f"${item['Estimated_PO_Cost']:.2f}",
            "Supplier_Contact": item["Supplier_Contact"],
            "Status": item["Status"]
        })
    return pd.DataFrame(rows)
