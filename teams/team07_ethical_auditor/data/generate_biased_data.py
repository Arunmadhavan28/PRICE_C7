#!/usr/bin/env python3
"""
Generates synthetic AI recommendation audit logs.
Includes intentional demographic steering bias and privacy opt-in violations.
"""

import numpy as np
import pandas as pd

def generate_audit_dataset(output_path="audit_dataset.csv", n_records=120):
    np.random.seed(42)

    # 4 Zip codes representing different demographic income bands
    zip_profiles = [
        {"zip": 90210, "income_k": 180, "bias_price_mean": 240, "std": 45, "opt_in_prob": 0.88},
        {"zip": 10021, "income_k": 210, "bias_price_mean": 280, "std": 50, "opt_in_prob": 0.90},
        {"zip": 30310, "income_k": 45, "bias_price_mean": 55, "std": 15, "opt_in_prob": 0.72},
        {"zip": 48206, "income_k": 38, "bias_price_mean": 42, "std": 12, "opt_in_prob": 0.68}
    ]

    records = []
    for i in range(n_records):
        prof = np.random.choice(zip_profiles)
        price = max(15.0, round(float(np.random.normal(prof["bias_price_mean"], prof["std"])), 2))
        opt_in = bool(np.random.rand() < prof["opt_in_prob"])

        # Intentional synthetic privacy violation: 15% of records have opt_in == False but still received recommendations
        records.append({
            "Customer_ZipCode": prof["zip"],
            "Income_Bracket": f"${prof['income_k']}k Avg",
            "Customer_Income_Proxy": prof["income_k"],
            "Recommended_Item_Price": price,
            "Opt_in_Status": opt_in,
            "Item_Category": np.random.choice(["Apparel", "Footwear", "Accessories", "Luxury Goods"]),
            "Recommendation_Algorithm": "PricingEngine_v2.1"
        })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} audit logs at {output_path}")
    return df

if __name__ == "__main__":
    generate_audit_dataset("audit_dataset.csv")
