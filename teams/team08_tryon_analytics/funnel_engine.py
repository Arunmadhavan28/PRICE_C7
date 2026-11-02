"""
Funnel Analytics Engine for Team 8: The Virtual Try-On Feedback Loop.
Measures conversion funnel drop-off, AR conversion lift, and statistical revenue impact.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

DEFAULT_LOGS_PATH = Path(__file__).resolve().parent / "data" / "session_logs.csv"


def load_session_logs(filepath: str = None) -> pd.DataFrame:
    """Loads and validates AR user session log CSV."""
    path = Path(filepath) if filepath else DEFAULT_LOGS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Session log file not found at {path}")
    df = pd.read_csv(path)
    required = ["Session_ID", "AR_TryOn_Used", "Time_in_AR", "Purchase_Made"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Standardize booleans
    for col in ["AR_TryOn_Used", "Purchase_Made"]:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.lower().isin(["true", "1", "yes"])
        else:
            df[col] = df[col].astype(bool)

    return df


def calculate_conversion_lift(cr_ar: float, cr_non_ar: float) -> float:
    """Calculates percentage conversion lift of AR users over Non-AR users."""
    if cr_non_ar <= 0:
        return 0.0
    return round(((cr_ar - cr_non_ar) / cr_non_ar) * 100.0, 1)


def segment_ar_vs_non_ar(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Splits session logs into AR users vs Non-AR users."""
    ar_df = df[df["AR_TryOn_Used"] == True].copy()
    non_ar_df = df[df["AR_TryOn_Used"] == False].copy()
    return ar_df, non_ar_df


def calculate_funnel_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes conversion funnel stages, conversion rates, and financial lift.
    """
    total_sessions = len(df)
    ar_df, non_ar_df = segment_ar_vs_non_ar(df)

    ar_sessions = len(ar_df)
    non_ar_sessions = len(non_ar_df)

    ar_purchases = int(ar_df["Purchase_Made"].sum())
    non_ar_purchases = int(non_ar_df["Purchase_Made"].sum())

    cr_ar = (ar_purchases / max(1, ar_sessions)) * 100.0
    cr_non_ar = (non_ar_purchases / max(1, non_ar_sessions)) * 100.0
    lift_pct = calculate_conversion_lift(cr_ar, cr_non_ar)

    # Average Order Value (AOV) for converting sessions
    aov_ar = float(ar_df[ar_df["Purchase_Made"] == True]["Cart_Value"].mean()) if ar_purchases > 0 else 0.0
    aov_non_ar = float(non_ar_df[non_ar_df["Purchase_Made"] == True]["Cart_Value"].mean()) if non_ar_purchases > 0 else 0.0

    # Total revenues
    total_rev_ar = float(ar_df["Cart_Value"].sum())
    total_rev_non_ar = float(non_ar_df["Cart_Value"].sum())

    # Average engagement time in AR (seconds)
    avg_time_ar = float(ar_df["Time_in_AR"].mean()) if ar_sessions > 0 else 0.0

    return {
        "total_sessions": total_sessions,
        "ar_sessions": ar_sessions,
        "non_ar_sessions": non_ar_sessions,
        "ar_purchases": ar_purchases,
        "non_ar_purchases": non_ar_purchases,
        "cr_ar": round(cr_ar, 1),
        "cr_non_ar": round(cr_non_ar, 1),
        "conversion_lift_pct": lift_pct,
        "aov_ar": round(aov_ar, 2),
        "aov_non_ar": round(aov_non_ar, 2),
        "total_rev_ar": round(total_rev_ar, 2),
        "total_rev_non_ar": round(total_rev_non_ar, 2),
        "avg_time_in_ar_sec": round(avg_time_ar, 1)
    }
