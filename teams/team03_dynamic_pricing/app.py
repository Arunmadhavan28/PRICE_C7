"""
Streamlit Web Application for Team 3: Dynamic Pricing Engine.
Interactive pricing dashboard with real-time environmental simulation,
financial margin analytics, and rule transparency.
Clean academic formatting with zero decorative unicode symbols.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pricing_engine import load_inventory, calculate_dynamic_price

# Page Configuration
st.set_page_config(
    page_title="Dynamic Pricing Engine | Retail AI Team 3",
    layout="wide"
)

# Application Header
st.title("'Happy Hour' Dynamic Pricing Engine")
st.caption(
    "Intraday Algorithmic Pricing Modifiers with Cost-Basis Protection | "
    "Designed for Store and Revenue Managers"
)

# Load Inventory
inventory_path = Path(__file__).parent / "data" / "inventory.json"
try:
    inventory = load_inventory(str(inventory_path))
except Exception as e:
    st.error(f"Failed to load inventory dataset: {e}")
    st.stop()

# Sidebar: Environmental Simulation Controls
st.sidebar.header("Environmental Simulation Controls")

hour = st.sidebar.slider(
    "Time of Day (24-Hour Clock)",
    min_value=0,
    max_value=23,
    value=18,
    help="7:00-9:00 triggers Morning Rush (+5% on Beverages); 17:00+ triggers Happy Hour clearance (-15% on surplus stock)."
)

weather = st.sidebar.selectbox(
    "Current Weather Condition",
    ["Sunny", "Raining", "Heatwave", "Cold Wave", "Overcast"],
    index=1,
    help="Raining boosts hot coffee/tea (+10%); Heatwave boosts iced/nitro items (+15%)."
)

stock_override = st.sidebar.slider(
    "Inventory Simulation Factor",
    min_value=0.2,
    max_value=2.0,
    value=1.0,
    step=0.1,
    help="Scales available stock across all items to simulate overstock vs scarcity rushes."
)

category_filter = st.sidebar.selectbox(
    "Filter by Category",
    ["All Categories"] + sorted(list({item.get("Category", "General") for item in inventory})),
    index=0
)

# Sidebar Clock and Context Indicator
time_band = "[Morning Rush]" if 7 <= hour <= 9 else ("[Happy Hour Clearance]" if hour >= 17 else "[Standard Operating Hours]")
st.sidebar.info(f"**Clock**: `{hour:02d}:00` ({time_band})\n\n**Weather**: `{weather}`\n\n**Inventory Factor**: `{stock_override:.1f}x`")

# Calculate Dynamic Prices across inventory using core pricing engine
results = []
for item in inventory:
    simulated_stock = max(0, int(item.get("Current_Stock", 0) * stock_override))
    calc = calculate_dynamic_price(
        item_dict=item,
        hour_of_day=hour,
        weather=weather,
        current_stock=simulated_stock
    )
    results.append(calc)

df_all = pd.DataFrame(results)

# Apply category filter
if category_filter != "All Categories":
    df_results = df_all[df_all["Category"] == category_filter].copy()
else:
    df_results = df_all.copy()

# Financial Overview Metric Cards
avg_shift = df_results["Price_Delta_Pct"].mean() if not df_results.empty else 0.0
total_margin = df_results["Margin_Dollar"].sum() if not df_results.empty else 0.0
discounted_count = int((df_results["Price_Delta_Pct"] < 0).sum())
surged_count = int((df_results["Price_Delta_Pct"] > 0).sum())
floor_guarded_count = int(df_results["Rules_Triggered"].apply(lambda rules: any("Cost Basis Floor" in r for r in rules)).sum())

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Price Adjustment", f"{avg_shift:+.1f}%", delta="Menu Shift")
with col2:
    st.metric("Discounted Items", f"{discounted_count} items", delta="Clearance Mode")
with col3:
    st.metric("Surged Items", f"{surged_count} items", delta="Demand Capture")
with col4:
    st.metric("Total Margin Pool", f"${total_margin:.2f}", delta=f"{floor_guarded_count} at Cost Floor")

st.markdown("---")

# Main Interface Tabs
tab_board, tab_explain, tab_safeguards = st.tabs([
    "Tab 1: Real-Time Price Board and Analytics",
    "Tab 2: Item Drilldown and Price Explanations",
    "Tab 3: Engine Safeguards and Export"
])

with tab_board:
    st.subheader("Live-Updating Dynamic Price Board")

    display_data = []
    for _, r in df_results.iterrows():
        display_data.append({
            "Item": r["Item"],
            "Category": r["Category"],
            "Cost Price": f"${r['Cost_Price']:.2f}",
            "Base Price": f"${r['Base_Price']:.2f}",
            "Dynamic Price": f"${r['Dynamic_Price']:.2f}",
            "Price Shift (%)": f"{r['Price_Delta_Pct']:+.1f}%",
            "Simulated Stock": r["Current_Stock"],
            "Active Pricing Rules": " | ".join(r["Rules_Triggered"])
        })

    st.dataframe(pd.DataFrame(display_data), use_container_width=True)

    # Plotly Visualization: Base vs Cost vs Recommended Dynamic Price
    st.subheader("Price Comparison and Margin Visualization")
    if not df_results.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Cost Basis Floor",
            x=df_results["Item"],
            y=df_results["Cost_Price"],
            marker_color="#94a3b8"
        ))
        fig.add_trace(go.Bar(
            name="Base Price",
            x=df_results["Item"],
            y=df_results["Base_Price"],
            marker_color="#38bdf8"
        ))
        fig.add_trace(go.Bar(
            name="Recommended Dynamic Price",
            x=df_results["Item"],
            y=df_results["Dynamic_Price"],
            marker_color="#22c55e"
        ))
        fig.update_layout(
            barmode="group",
            xaxis_tickangle=-25,
            yaxis_title="Price in USD ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=100),
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_explain:
    st.subheader("Algorithmic Transparency and Price Drivers")
    selected_item_name = st.selectbox("Select Menu Item for Deep-Dive", df_results["Item"].tolist())

    if selected_item_name:
        row = df_results[df_results["Item"] == selected_item_name].iloc[0]

        ecol1, ecol2, ecol3 = st.columns(3)
        with ecol1:
            st.metric("Base Price", f"${row['Base_Price']:.2f}")
        with ecol2:
            st.metric("Cost Basis Floor", f"${row['Cost_Price']:.2f}")
        with ecol3:
            st.metric("Final Dynamic Price", f"${row['Dynamic_Price']:.2f}", delta=f"{row['Price_Delta_Pct']:+.1f}%")

        st.markdown("#### Triggered Decision Logic")
        for rule in row["Rules_Triggered"]:
            if "Clearance" in rule:
                st.warning(f"[Clearance Applied]: {rule}")
            elif "Surge" in rule or "Premium" in rule:
                st.success(f"[Demand Modifier Applied]: {rule}")
            elif "Cost Basis Floor" in rule:
                st.error(f"[Cost-Floor Guardrail Triggered]: {rule} -- Price prevented from dropping below ${row['Cost_Price']:.2f} cost basis.")
            else:
                st.info(f"[Standard Base Rate]: {rule}")

        with st.expander("Detailed Margin Economics"):
            st.write(f"- **Gross Margin ($)**: `${row['Margin_Dollar']:.2f}`")
            st.write(f"- **Gross Margin (%)**: `{row['Margin_Pct']:.1f}%`")
            st.write(f"- **Available Stock**: `{row['Current_Stock']}` units")

with tab_safeguards:
    st.subheader("Configured Safeguards and System Health")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown("**1. Cost-Floor Protection**")
        st.caption("Guarantees that `Dynamic_Price >= Cost_Price` on all items, protecting profitability even under severe inventory liquidation.")
    with sc2:
        st.markdown("**2. Anti-Gouging Surge Ceiling**")
        st.caption("Surges are bounded by `MAX_PRICE_MULTIPLIER = 2.0x` (+100% cap) to prevent consumer backlash during extreme demand spikes.")
    with sc3:
        st.markdown("**3. Zero/Negative Stock Safety**")
        st.caption("Stock levels <= 0 do not trigger false scarcity premiums or liquidation discounts.")

    st.markdown("---")
    st.subheader("Export Recommended Menu Prices")
    csv_bytes = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Inventory and Prices (CSV)",
        data=csv_bytes,
        file_name=f"dynamic_prices_hour_{hour}_{weather.lower()}.csv",
        mime="text/csv"
    )
