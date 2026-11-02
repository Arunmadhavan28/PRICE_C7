"""
Streamlit Web Application for Team 6: The 'Drop Culture' Markdown Optimizer.
Clearance analytics identifying lagging sell-through and protecting cost basis.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from optimizer import load_aging_data, project_profit_recovery

st.set_page_config(
    page_title="Markdown Optimizer | Retail AI",
    page_icon="🏷️",
    layout="wide"
)

st.title("🏷️ The 'Drop Culture' Markdown Optimizer")
st.caption("Clearance Analytics Computing Minimum Velocity Markdowns Without Breaching Cost Basis | Target: Retail Merchandisers")

# Load Inventory Aging Data
data_path = Path(__file__).parent / "data" / "inventory_aging.csv"
raw_df = load_aging_data(str(data_path))

# Run Calculation
optimized_df, metrics = project_profit_recovery(raw_df)

# Sidebar Filter & Settings
st.sidebar.header("🎯 Markdown Controls")
st.sidebar.markdown(f"**Total Tracked SKUs**: `{metrics['total_sku_count']}`")
st.sidebar.markdown(f"**At-Risk Lagging SKUs**: `{metrics['at_risk_sku_count']}`")

aging_threshold = st.sidebar.slider("Highlight Aging Threshold (Days on Shelf)", min_value=15, max_value=90, value=30)
filter_category = st.sidebar.selectbox("Filter Category", ["All Categories"] + sorted(raw_df["Category"].unique().tolist()))

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("SKUs At Risk", f"{metrics['at_risk_sku_count']} / {metrics['total_sku_count']}", delta="Lagging Target", delta_color="inverse")
with col2:
    st.metric("Capital at Dead Stock Risk", f"${metrics['total_capital_at_risk']:,.2f}", delta="Cost Basis Value", delta_color="inverse")
with col3:
    st.metric("Projected Clearance Revenue", f"${metrics['total_projected_revenue']:,.2f}", delta="Capital Liberated")
with col4:
    st.metric("Projected Net Profit Recovery", f"${metrics['total_projected_profit']:,.2f}", delta=f"Avg Discount {metrics['avg_clearance_discount']}%")

st.markdown("---")

# Data Table with Risk Highlighting
st.subheader("📋 Inventory Aging & Clearance Matrix")

def color_risk(val):
    if val == "CRITICAL AT-RISK":
        return "background-color: #7f1d1d; color: white; font-weight: bold;"
    elif val == "AT-RISK":
        return "background-color: #78350f; color: white; font-weight: bold;"
    return "background-color: #064e3b; color: white;"

display_df = optimized_df.copy()
if filter_category != "All Categories":
    display_df = display_df[display_df["Category"] == filter_category]

styled_table = display_df[[
    "Item_SKU", "Item_Name", "Category", "Days_on_Shelf",
    "Target_Sell_Through_Rate", "Actual_Sell_Through_Rate",
    "Retail_Price", "Cost_Basis", "Recommended_Discount_Pct",
    "Clearance_Price", "Risk_Status"
]].style.map(color_risk, subset=["Risk_Status"])

st.dataframe(styled_table, use_container_width=True)

# Interactive Chart: Price vs Cost Floor
st.markdown("---")
st.subheader("📊 Clearance Pricing Floor Protection Analysis")
st.caption("Visualizing retail price vs recommended clearance price vs unbreakable cost basis floor.")

fig = go.Figure()
fig.add_trace(go.Bar(
    x=display_df["Item_SKU"],
    y=display_df["Retail_Price"],
    name="Original Retail Price",
    marker_color="#3b82f6"
))
fig.add_trace(go.Bar(
    x=display_df["Item_SKU"],
    y=display_df["Clearance_Price"],
    name="Recommended Clearance Price",
    marker_color="#f59e0b"
))
fig.add_trace(go.Bar(
    x=display_df["Item_SKU"],
    y=display_df["Cost_Basis"],
    name="Cost Basis Floor (Min Limit)",
    marker_color="#ef4444"
))

fig.update_layout(
    barmode="group",
    template="plotly_dark",
    height=420,
    xaxis_title="Item SKU",
    yaxis_title="Price ($ USD)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Export Button
csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Export Clearance Markdown File for POS Upload",
    data=csv_data,
    file_name="clearance_markdown_approved.csv",
    mime="text/csv",
    use_container_width=True
)
