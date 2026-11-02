#!/usr/bin/env python3
"""
Generates synthetic web-traffic and AR virtual try-on session logs.
"""

import numpy as np
import pandas as pd

def generate_session_data(output_path="session_logs.csv", n_sessions=250):
    np.random.seed(42)

    records = []
    for i in range(n_sessions):
        session_id = f"SES-{1000 + i}"
        # 40% of sessions engage with AR Try-On
        ar_used = bool(np.random.rand() < 0.40)

        if ar_used:
            time_in_ar = int(np.random.gamma(shape=3.0, scale=35))  # avg ~105 seconds
            # AR users convert at 38%
            purchase_made = bool(np.random.rand() < 0.38)
            cart_value = round(float(np.random.normal(145, 30)), 2) if purchase_made else 0.0
        else:
            time_in_ar = 0
            # Non-AR users convert at 18%
            purchase_made = bool(np.random.rand() < 0.18)
            cart_value = round(float(np.random.normal(110, 25)), 2) if purchase_made else 0.0

        records.append({
            "Session_ID": session_id,
            "AR_TryOn_Used": ar_used,
            "Time_in_AR": time_in_ar,
            "Purchase_Made": purchase_made,
            "Cart_Value": max(0.0, cart_value),
            "Device_Type": np.random.choice(["iOS Mobile", "Android Mobile", "Desktop Chrome"], p=[0.55, 0.35, 0.10])
        })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} session logs at {output_path}")
    return df

if __name__ == "__main__":
    generate_session_data("session_logs.csv")
