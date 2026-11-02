"""
Streamlit Web Application for Team 3: Dynamic Pricing Engine.
Interactive price board with sliders for time, weather, and inventory.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
from pricing_engine import load_inventory, calculate_dynamic_price

st.set_page_config(
    page_title="Dynamic Pricing Engine | Retail AI",
    layout="wide"
)

st.title("Dynamic Pricing Engine")
st.caption("Real-Time Algorithmic Pricing Modifiers for Cafes and Retailers | Target: Store and Revenue Managers")

# Load Inventory
inventory_path = Path(__file__).parent / "data" / "inventory.json"
inventory = load_inventory(str(inventory_path))

# Sidebar Controls
st.sidebar.header("Environmental Simulation Controls")

hour = st.sidebar.slider(
    "Time of Day (24-Hour Clock)",
    min_value=0,
    max_value=23,
    value=18,
    help="17:00+ triggers Happy Hour clearance discounts on surplus stock."
)

weather = st.sidebar.selectbox(
    "Current Weather Condition",
    ["Sunny", "Raining", "Heatwave", "Cold Wave", "Overcast"],
    index=1,
    help="Raining boosts hot coffee/tea; Heatwave boosts iced/nitro items."
)

stock_override = st.sidebar.slider(
    "Inventory Simulation Factor",
    min_value=0.2,
    max_value=2.0,
    value=1.0,
    step=0.1,
    help="Adjusts all stock levels simultaneously to test scarcity vs overstock."
)

st.sidebar.markdown(f"**Current Clock**: `{hour:02d}:00` | **Weather**: `{weather}`")

# Calculate Dynamic Prices across inventory
results = []
for item in inventory:
    simulated_stock = max(1, int(item["Current_Stock"] * stock_override))
    calc = calculate_dynamic_price(item, hour_of_day=hour, weather=weather, current_stock=simulated_stock)
    results.append(calc)

df_results = pd.DataFrame(results)

# Top Metrics Row
avg_shift = df_results["Price_Delta_Pct"].mean()
total_margin = df_results["Margin_Dollar"].sum()
discounted_count = (df_results["Price_Delta_Pct"] < 0).sum()
surged_count = (df_results["Price_Delta_Pct"] > 0).sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Price Adjustment", f"{avg_shift:+.1f}%", delta="Across Menu")
with col2:
    st.metric("Discounted Items", f"{discounted_count} items", delta="Clearance Mode")
with col3:
    st.metric("Surged Items", f"{surged_count} items", delta="Demand Capture")
with col4:
    st.metric("Total Margin Pool", f"${total_margin:.2f}", delta="Protected Cost Floor")

st.markdown("---")

# Live-Updating Price Board
st.subheader("Real-Time Dynamic Price Board")

display_data = []
for _, r in df_results.iterrows():
    rules_text = " | ".join(r["Rules_Triggered"])
    price_tag = f"${r['Dynamic_Price']:.2f}"
    delta_tag = f"{r['Price_Delta_Pct']:+.1f}%"
    display_data.append({
        "Item": r["Item"],
        "Category": r["Category"],
        "Base Price": f"${r['Base_Price']:.2f}",
        "Dynamic Price": price_tag,
        "Shift (%)": delta_tag,
        "Simulated Stock": r["Current_Stock"],
        "Active Pricing Rules": rules_text
    })

st.dataframe(pd.DataFrame(display_data), use_container_width=True)

# Visual Comparison of Margin and Base vs Dynamic
with st.expander("Price Delta Comparison View"):
    chart_df = df_results[["Item", "Base_Price", "Dynamic_Price"]].set_index("Item")
    st.bar_chart(chart_df)
