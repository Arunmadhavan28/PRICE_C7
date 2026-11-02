#!/usr/bin/env python3
"""
Generates synthetic fashion retail sales and cultural trend data.
Includes seasonality, viral social media bursts, and trend decay.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_mock_trend_data(output_path="trend_sales_data.csv", n_days=180):
    np.random.seed(42)
    start_date = datetime.now() - timedelta(days=n_days)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]

    categories = [
        {"name": "Streetwear Cargo Pants", "base_vol": 120, "trend_phase": "peak", "volatility": 15},
        {"name": "Y2K Denim Jackets", "base_vol": 85, "trend_phase": "rising", "volatility": 12},
        {"name": "Cottagecore Maxi Dresses", "base_vol": 60, "trend_phase": "falling", "volatility": 8},
        {"name": "Minimalist Linen Shirts", "base_vol": 110, "trend_phase": "stable", "volatility": 10},
        {"name": "Cyberpunk Metallic Vests", "base_vol": 35, "trend_phase": "viral_surge", "volatility": 25}
    ]

    records = []
    for cat in categories:
        for idx, d in enumerate(dates):
            t = idx / n_days
            # Seasonal / trend wave
            if cat["trend_phase"] == "rising":
                trend_factor = 1.0 + 1.2 * t
                social_score = min(100, int(45 + 50 * t + np.random.normal(0, 5)))
            elif cat["trend_phase"] == "falling":
                trend_factor = max(0.2, 1.8 - 1.4 * t)
                social_score = max(10, int(90 - 75 * t + np.random.normal(0, 4)))
            elif cat["trend_phase"] == "viral_surge":
                # Spike between day 100 and 150
                spike = 3.0 * np.exp(-((idx - 120) ** 2) / 300)
                trend_factor = 0.8 + spike
                social_score = min(100, int(30 + 65 * spike/3.0 + np.random.normal(0, 6)))
            elif cat["trend_phase"] == "peak":
                trend_factor = 1.4 + 0.2 * np.sin(2 * np.pi * t * 3)
                social_score = min(100, int(75 + 15 * np.sin(2 * np.pi * t * 3) + np.random.normal(0, 4)))
            else:
                trend_factor = 1.0 + 0.1 * np.sin(2 * np.pi * t * 2)
                social_score = int(50 + 10 * np.random.normal(0, 3))

            weekly_lift = 1.25 if d.weekday() in [4, 5, 6] else 0.95
            sales = max(5, int(cat["base_vol"] * trend_factor * weekly_lift + np.random.normal(0, cat["volatility"])))

            records.append({
                "Date": d.strftime("%Y-%m-%d"),
                "Item_Category": cat["name"],
                "Historical_Sales_Volume": sales,
                "Social_Media_Trend_Score": max(1, min(100, social_score))
            })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows across {len(categories)} categories at {output_path}")
    return df

if __name__ == "__main__":
    generate_mock_trend_data("trend_sales_data.csv")
