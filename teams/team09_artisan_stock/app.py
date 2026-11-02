"""
Streamlit Web Application for Team 9: The Artisan Safety-Stock Planner.
Visual kanban dashboard tracking runway days with 1-click purchase order generation.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
from stock_engine import (
    load_materials_data,
    evaluate_material_status,
    generate_purchase_order
)

st.set_page_config(
    page_title="Artisan Stock Planner | Retail AI",
    page_icon="📦",
    layout="wide"
)

st.title("📦 The Artisan Safety-Stock Planner")
st.caption("Visual Kanban Inventory Tracking & Automated Purchase Orders | Target: Independent Makers & Artisans")

# Load Raw Materials Data
data_path = Path(__file__).parent / "data" / "artisan_materials.csv"
materials_df = load_materials_data(str(data_path))

# Process all materials
evaluations = [evaluate_material_status(row) for _, row in materials_df.iterrows()]

# Summary Counts
critical_items = [e for e in evaluations if e["Status"] == "CRITICAL"]
warning_items = [e for e in evaluations if e["Status"] == "WARNING"]
healthy_items = [e for e in evaluations if e["Status"] == "HEALTHY"]
items_needing_po = [e for e in evaluations if e["Status"] in ["CRITICAL", "WARNING"]]
total_po_capital = sum(e["Estimated_PO_Cost"] for e in items_needing_po)

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Materials Tracked", f"{len(evaluations)} items", delta="Boutique Workshop")
with col2:
    st.metric("Critical Stockouts (Red)", f"{len(critical_items)} alerts", delta="Lead Time Exceeded", delta_color="inverse")
with col3:
    st.metric("Warning Reorder (Yellow)", f"{len(warning_items)} items", delta="Approaching ROP", delta_color="inverse")
with col4:
    st.metric("Total Replenishment Capital", f"${total_po_capital:,.2f}", delta="For 30-Day Runway")

st.markdown("---")

# Kanban Grid Layout
st.subheader("📋 Visual Material Runway Grid")
st.caption("Cards automatically transition from Green ➔ Yellow ➔ Red as runway days drop below supplier lead times.")

# Display in a 3-column responsive grid
grid_cols = st.columns(3)
for idx, mat in enumerate(evaluations):
    col = grid_cols[idx % 3]
    with col:
        badge_color = mat["Status_Color"]
        progress_val = min(1.0, max(0.0, mat["Runway_Days"] / max(1.0, mat["Lead_Time_Days"] * 2.5)))

        st.markdown(f"""
        <div style="background: #18181b; border-left: 6px solid {badge_color}; border-radius: 8px; padding: 14px; margin-bottom: 12px; border-top: 1px solid #333; border-right: 1px solid #333; border-bottom: 1px solid #333;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="background: {badge_color}; color: #000; font-weight: bold; font-size: 0.75em; padding: 2px 8px; border-radius: 10px;">{mat['Status']}</span>
                <span style="font-size: 0.8em; color: #888;">{mat['Category']}</span>
            </div>
            <h4 style="margin: 0 0 6px 0; font-size: 1.0em;">{mat['Material_Name']}</h4>
            <div style="font-size: 0.85em; color: #cbd5e0; margin-bottom: 8px;">
                Current Stock: <b>{mat['Current_Level']}</b> | Burn Rate: <b>{mat['Daily_Burn_Rate']}/day</b><br>
                Supplier Lead Time: <b>{mat['Lead_Time_Days']} days</b><br>
                Runway Remaining: <b style="color: {badge_color};">{mat['Runway_Days']} days</b>
            </div>
            <div style="font-size: 0.75em; color: #aaa; margin-bottom: 4px;">Runway Health Index:</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progress_val)
        st.caption(f"Upcoming Trigger: {mat['Upcoming_Events']}")

# Purchase Order Generator
st.markdown("---")
st.subheader("📝 One-Click Automated Purchase Order Generator")
st.caption("Consolidates all Critical and Warning inventory items into an itemized purchase order for vendors.")

if st.button("⚡ Generate Purchase Order for Vendors", type="primary", use_container_width=True):
    po_text = generate_purchase_order(items_needing_po)
    st.text_area("Purchase Order Transmission Preview", value=po_text, height=260)
    st.download_button(
        label="📥 Download Purchase Order as Plain Text (.txt)",
        data=po_text,
        file_name="purchase_order_artisan.txt",
        mime="text/plain",
        use_container_width=True
    )
