"""
Clearance Markdown Engine for Team 6: The 'Drop Culture' Markdown Optimizer.
Identifies lag in sell-through rates and computes optimal markdown discounts without breaching cost basis.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

DEFAULT_AGING_PATH = Path(__file__).resolve().parent / "data" / "inventory_aging.csv"


def load_aging_data(filepath: str = None) -> pd.DataFrame:
    """Loads and validates inventory aging dataset."""
    path = Path(filepath) if filepath else DEFAULT_AGING_PATH
    if not path.exists():
        raise FileNotFoundError(f"Inventory aging file not found at {path}")
    df = pd.read_csv(path)
    required = ["Item_SKU", "Days_on_Shelf", "Target_Sell_Through_Rate", "Actual_Sell_Through_Rate", "Cost_Basis"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column {col} in aging data")
    return df


def identify_at_risk_items(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies inventory items where actual sell-through is lagging behind target.
    Flags severity: 'CRITICAL', 'AT RISK', or 'ON TRACK'.
    """
    df = df.copy()
    df["Sell_Through_Lag"] = round(df["Target_Sell_Through_Rate"] - df["Actual_Sell_Through_Rate"], 3)

    def classify_risk(row):
        lag = row["Sell_Through_Lag"]
        days = row["Days_on_Shelf"]
        if lag > 0.35 or (lag > 0.20 and days > 60):
            return "CRITICAL AT-RISK"
        elif lag > 0.05:
            return "AT-RISK"
        else:
            return "ON TRACK"

    df["Risk_Status"] = df.apply(classify_risk, axis=1)
    return df


def calculate_recommended_discount(row: pd.Series) -> Dict[str, Any]:
    """
    Calculates the minimum clearance discount percentage based on aging tiers:
    - Days on Shelf > 60: 30% discount
    - Days on Shelf > 30: 15% discount
    - Days on Shelf > 15: 5% discount
    - Otherwise: 0%

    Strict Constraint: Discounted Price cannot fall below Cost_Basis!
    Max allowable discount % = (Retail_Price - Cost_Basis) / Retail_Price
    """
    retail_price = float(row.get("Retail_Price", 100.0))
    cost_basis = float(row["Cost_Basis"])
    days = int(row["Days_on_Shelf"])
    if "Sell_Through_Lag" in row:
        lag = float(row["Sell_Through_Lag"])
    elif "Target_Sell_Through_Rate" in row and "Actual_Sell_Through_Rate" in row:
        lag = float(row["Target_Sell_Through_Rate"] - row["Actual_Sell_Through_Rate"])
    else:
        lag = 0.0

    # Base tiered discount
    if days > 60:
        base_disc = 0.30
    elif days > 30:
        base_disc = 0.15
    elif days > 15:
        base_disc = 0.05
    else:
        base_disc = 0.0

    # Amplify if extreme sell-through lag
    if lag > 0.30:
        base_disc += 0.05

    # Maximum discount allowed before hitting cost basis
    max_safe_discount = max(0.0, (retail_price - cost_basis) / retail_price)
    effective_discount = min(base_disc, max_safe_discount)

    new_price = round(retail_price * (1.0 - effective_discount), 2)
    new_price = max(cost_basis, new_price)  # Strict cost basis floor

    actual_disc_pct = round(((retail_price - new_price) / retail_price) * 100, 1)

    return {
        "Recommended_Discount_Pct": actual_disc_pct,
        "Original_Price": retail_price,
        "Clearance_Price": new_price,
        "Cost_Basis": cost_basis,
        "Margin_Dollars": round(new_price - cost_basis, 2),
        "Protected_From_Breach": new_price >= cost_basis
    }


def project_profit_recovery(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Applies recommended discounts across all at-risk items and calculates
    projected inventory capital recovery vs dead stock loss.
    """
    df_flagged = identify_at_risk_items(df)
    results = []

    for _, row in df_flagged.iterrows():
        disc_info = calculate_recommended_discount(row)
        units = row.get("Current_Units", 50)
        potential_loss = row["Cost_Basis"] * units
        projected_revenue = disc_info["Clearance_Price"] * units
        projected_profit = disc_info["Margin_Dollars"] * units

        row_dict = row.to_dict()
        row_dict.update({
            "Recommended_Discount_Pct": disc_info["Recommended_Discount_Pct"],
            "Clearance_Price": disc_info["Clearance_Price"],
            "Margin_Dollars": disc_info["Margin_Dollars"],
            "Projected_Revenue": round(projected_revenue, 2),
            "Projected_Profit": round(projected_profit, 2),
            "Dead_Stock_Risk_Capital": round(potential_loss, 2)
        })
        results.append(row_dict)

    res_df = pd.DataFrame(results)

    at_risk_sub = res_df[res_df["Risk_Status"] != "ON TRACK"]

    summary_metrics = {
        "total_sku_count": len(res_df),
        "at_risk_sku_count": len(at_risk_sub),
        "total_capital_at_risk": round(float(at_risk_sub["Dead_Stock_Risk_Capital"].sum()), 2),
        "total_projected_revenue": round(float(at_risk_sub["Projected_Revenue"].sum()), 2),
        "total_projected_profit": round(float(at_risk_sub["Projected_Profit"].sum()), 2),
        "avg_clearance_discount": round(float(at_risk_sub["Recommended_Discount_Pct"].mean()), 1)
    }

    return res_df, summary_metrics
