#!/usr/bin/env python3
"""
Synthetic Session Data Generator for Team 8: The Virtual Try-On Feedback Loop.
Generates realistic e-commerce telemetry with AR engagement, device platform,
product category, and temporal timestamp attributes.
"""

from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def generate_session_data(
    output_path: str = "session_logs.csv",
    n_sessions: int = 300,
    seed: int = 3
) -> pd.DataFrame:
    """
    Generates realistic e-commerce session logs comparing AR try-on users vs standard shoppers.

    Parameters:
    - output_path: Destination CSV file path.
    - n_sessions: Total number of sessions to simulate (>= 250).
    - seed: Fixed random seed for exact reproducibility (seed 3 yields ~40% AR, ~38% AR CR, ~18% Non-AR CR).

    Returns:
    - pd.DataFrame containing simulated session records.
    """
    np.random.seed(seed)

    device_choices = ["iOS Mobile", "Android Mobile", "Desktop Chrome"]
    device_weights = [0.55, 0.35, 0.10]
    category_choices = ["Apparel", "Footwear", "Eyewear", "Accessories"]
    category_weights = [0.48, 0.24, 0.16, 0.12]

    ar_flags = np.random.rand(n_sessions) < 0.40
    ar_cr_flags = np.random.rand(n_sessions) < 0.38
    non_ar_cr_flags = np.random.rand(n_sessions) < 0.18
    purchase_flags = np.where(ar_flags, ar_cr_flags, non_ar_cr_flags)
    devices = np.random.choice(device_choices, size=n_sessions, p=device_weights)
    categories = np.random.choice(category_choices, size=n_sessions, p=category_weights)

    # Generate realistic timestamps across October 2026
    base_date = datetime(2026, 10, 1, 8, 0, 0)
    day_offsets = np.random.randint(0, 31, size=n_sessions)
    hour_offsets = np.random.randint(0, 15, size=n_sessions)
    minute_offsets = np.random.randint(0, 60, size=n_sessions)
    second_offsets = np.random.randint(0, 60, size=n_sessions)
    timestamps = [
        base_date + timedelta(days=int(d), hours=int(h), minutes=int(m), seconds=int(s))
        for d, h, m, s in zip(day_offsets, hour_offsets, minute_offsets, second_offsets)
    ]
    sort_idx = np.argsort(timestamps)
    timestamps = [timestamps[i].strftime("%Y-%m-%d %H:%M:%S") for i in sort_idx]

    # AR engagement duration: Gamma distribution centered ~100s (range 15s - 300s)
    raw_time_in_ar = np.where(
        ar_flags,
        np.clip(np.random.gamma(shape=3.2, scale=33, size=n_sessions).astype(int), 15, 300),
        0
    )

    # Cart values for purchasers: AR users show higher basket size due to fit confidence
    raw_cart_values = np.where(
        purchase_flags,
        np.where(
            ar_flags,
            np.round(np.random.normal(148.0, 26.0, n_sessions), 2),
            np.round(np.random.normal(108.0, 20.0, n_sessions), 2)
        ),
        0.0
    )
    raw_cart_values = np.maximum(0.0, raw_cart_values)

    # Apply chronological order
    ar_flags = ar_flags[sort_idx]
    purchase_flags = purchase_flags[sort_idx]
    devices = devices[sort_idx]
    categories = categories[sort_idx]
    time_in_ar = raw_time_in_ar[sort_idx]
    cart_values = raw_cart_values[sort_idx]

    records = []
    for i in range(n_sessions):
        records.append({
            "Session_ID": f"SES-{1000 + i}",
            "Timestamp": str(timestamps[i]),
            "Product_Category": str(categories[i]),
            "AR_TryOn_Used": bool(ar_flags[i]),
            "Time_in_AR": int(time_in_ar[i]),
            "Purchase_Made": bool(purchase_flags[i]),
            "Cart_Value": float(cart_values[i]),
            "Device_Type": str(devices[i])
        })

    df = pd.DataFrame(records)

    target_file = Path(output_path)
    target_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target_file, index=False)
    print(f"Successfully generated {len(df)} session logs at: {target_file.resolve()}")
    return df


if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    dest_path = current_dir / "session_logs.csv"
    generate_session_data(str(dest_path), n_sessions=300, seed=3)
