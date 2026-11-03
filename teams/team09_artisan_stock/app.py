"""
Streamlit Web Application for Team 9: The Artisan Safety-Stock Planner.
Visual Kanban inventory tracking, Plotly runway diagnostics, and automated 1-click purchase orders.
Clean academic formatting with zero decorative unicode emojis and native theme adaptation.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from stock_engine import (
    load_materials_data,
    calculate_safety_stock,
    calculate_runway_days,
    calculate_stockout_risk_score,
    evaluate_material_status,
    simulate_event_surge,
    calculate_portfolio_summary,
    generate_purchase_order,
    generate_purchase_order_dataframe
)

# ---------------------------------------------------------
# Page Configuration (Clean Academic Header)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Artisan Safety-Stock Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Modern, Adaptive CSS (Light & Dark Mode Friendly)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Metric Card Polish - Adaptive to Light & Dark Theme */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        min-height: 110px;
    }
    div[data-testid="stMetricLabel"] > div > p {
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.85;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    div[data-testid="stMetricDelta"] > div {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
    }

    /* Tab Header Polish */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 2px solid rgba(148, 163, 184, 0.2);
        padding-bottom: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 22px;
        font-weight: 600;
        font-size: 0.95rem;
    }

    /* Universal Adaptive Kanban Card */
    .artisan-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .artisan-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    .status-badge {
        font-weight: 700;
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 14px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #ffffff !important;
        display: inline-block;
    }
    .category-pill {
        font-size: 0.8rem;
        font-weight: 500;
        opacity: 0.75;
    }
    .card-title {
        margin: 10px 0 8px 0;
        font-size: 1.1rem;
        font-weight: 700;
    }
    .card-body-text {
        font-size: 0.88rem;
        line-height: 1.6;
        margin-bottom: 12px;
        opacity: 0.9;
    }
    .card-footer-text {
        display: flex;
        justify-content: space-between;
        font-size: 0.78rem;
        font-weight: 600;
        opacity: 0.75;
        margin-bottom: 4px;
    }

    /* Information Ribbon */
    .summary-ribbon {
        background-color: var(--secondary-background-color);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 20px;
        font-size: 0.9rem;
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Ingestion
# ---------------------------------------------------------
DATA_PATH = Path(__file__).resolve().parent / "data" / "artisan_materials.csv"

try:
    raw_df = load_materials_data(str(DATA_PATH))
except Exception as err:
    st.error(f"Failed to load inventory dataset: {err}")
    st.stop()

# ---------------------------------------------------------
# Sidebar Controls & Interactive Event Simulation
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600&auto=format&fit=crop&q=60", use_container_width=True)
    st.title("Artisan Studio Controls")
    st.caption("Inventory & Supply Chain Command Center")

    st.markdown("### Demand Surge Simulator")
    st.info("Simulate upcoming craft fair pop-ups, holiday rushes, or seasonal demand spikes.")
    surge_multiplier = st.slider(
        "Event Demand Multiplier",
        min_value=1.0,
        max_value=3.0,
        value=1.0,
        step=0.25,
        help="Scales daily material consumption rate (Burn Rate) to model demand surges."
    )
    if surge_multiplier > 1.0:
        st.warning(f"Active Surge: {surge_multiplier:.2f}x Normal Consumption")

    st.markdown("---")
    st.markdown("### Filters and Search")
    categories = ["All Categories"] + sorted(list(raw_df["Category"].dropna().unique()))
    selected_category = st.selectbox("Craft Category", categories)

    status_options = ["All Statuses", "CRITICAL Only", "WARNING Only", "HEALTHY Only"]
    selected_status = st.selectbox("Stock Health Filter", status_options)

    search_query = st.text_input("Search Material by Name", placeholder="e.g. Soy Wax, Brass, Leather...")

    st.markdown("---")
    st.caption("Team 9: Inventory Optimization | Retail AI Lab")

# ---------------------------------------------------------
# Data Processing & Filtering
# ---------------------------------------------------------
evaluations = [
    evaluate_material_status(row, surge_multiplier=surge_multiplier)
    for _, row in raw_df.iterrows()
]

# Apply Filters
filtered_evals = evaluations

if selected_category != "All Categories":
    filtered_evals = [e for e in filtered_evals if e["Category"] == selected_category]

if selected_status == "CRITICAL Only":
    filtered_evals = [e for e in filtered_evals if e["Status"] == "CRITICAL"]
elif selected_status == "WARNING Only":
    filtered_evals = [e for e in filtered_evals if e["Status"] == "WARNING"]
elif selected_status == "HEALTHY Only":
    filtered_evals = [e for e in filtered_evals if e["Status"] == "HEALTHY"]

if search_query.strip():
    q = search_query.strip().lower()
    filtered_evals = [e for e in filtered_evals if q in e["Material_Name"].lower()]

# Overall Portfolio Summary
portfolio = calculate_portfolio_summary(evaluations)
items_needing_po = [e for e in evaluations if e["Status"] in ["CRITICAL", "WARNING"]]

# ---------------------------------------------------------
# Top Header Banner
# ---------------------------------------------------------
st.title("The Artisan Safety-Stock Planner")
st.markdown(
    "Visual Kanban inventory control, supplier lead-time runway analytics, and autonomous purchase order generation for boutique artisans."
)

# ---------------------------------------------------------
# 4 Spacious, Non-Truncated Executive KPI Cards
# ---------------------------------------------------------
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.metric(
        label="Materials Tracked",
        value=f"{portfolio['total_materials']} SKUs",
        delta="Active Workshop Catalog"
    )

with kpi_col2:
    crit_count = portfolio['critical_count']
    st.metric(
        label="Critical Stockouts",
        value=f"{crit_count} Alert{'s' if crit_count != 1 else ''}",
        delta="Runway <= Lead Time",
        delta_color="inverse" if crit_count > 0 else "normal"
    )

with kpi_col3:
    warn_count = portfolio['warning_count']
    st.metric(
        label="Reorder Warnings",
        value=f"{warn_count} Item{'s' if warn_count != 1 else ''}",
        delta="Stock <= Reorder Point",
        delta_color="inverse" if warn_count > 0 else "normal"
    )

with kpi_col4:
    st.metric(
        label="Replenishment Capital",
        value=f"₹{portfolio['total_po_capital']:,.2f}",
        delta="To Restore 30-Day Buffer"
    )

# Subtle secondary metrics summary ribbon
st.markdown(f"""
<div class="summary-ribbon">
    <span><b>Current Asset Value:</b> ₹{portfolio['total_asset_value']:,.2f}</span>
    <span><b>Average Studio Runway:</b> {portfolio['average_runway_days']} Days</span>
    <span><b>Active Demand Rate:</b> {surge_multiplier:.2f}x Normal Pace</span>
    <span><b>Average Portfolio Risk:</b> {portfolio['average_risk_score']}%</span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Application Tabs (Clean Academic Labels)
# ---------------------------------------------------------
tab_kanban, tab_analytics, tab_simulator, tab_po, tab_data = st.tabs([
    "Kanban Board",
    "Runway Charts",
    "What-If Simulator",
    "Purchase Orders",
    "Master Catalog"
])

# ---------------------------------------------------------
# TAB 1: Visual Kanban Grid
# ---------------------------------------------------------
with tab_kanban:
    st.subheader("Visual Material Runway Kanban")
    st.caption("Cards are color-coded by replenishment urgency relative to vendor delivery lead times.")

    if not filtered_evals:
        st.info("No materials match the selected filters. Clear the filters in the sidebar to view all items.")
    else:
        # Responsive 3-column Kanban card grid
        grid_cols = st.columns(3)
        for idx, mat in enumerate(filtered_evals):
            col = grid_cols[idx % 3]
            with col:
                status_color = mat["Status_Color"]
                runway = mat["Runway_Days"]
                lead_time = mat["Lead_Time_Days"]
                health_ratio = min(1.0, max(0.0, runway / max(1.0, lead_time * 2.5)))

                st.markdown(f"""
                <div class="artisan-card" style="border-left: 6px solid {status_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="status-badge" style="background-color: {status_color};">
                            {mat['Status']}
                        </span>
                        <span class="category-pill">
                            {mat['Category']}
                        </span>
                    </div>
                    <div class="card-title">
                        {mat['Material_Name']}
                    </div>
                    <div class="card-body-text">
                        <b>Current Stock:</b> {mat['Current_Level']} units &bull; <b>Cost:</b> ₹{mat['Unit_Cost']:.2f}<br>
                        <b>Daily Burn:</b> {mat['Daily_Burn_Rate']}/day &bull; <b>Reorder Point (ROP):</b> {mat['Reorder_Point']}<br>
                        <b>Supplier Lead Time:</b> {mat['Lead_Time_Days']} days<br>
                        <b>Runway Days Remaining:</b> <span style="color: {status_color}; font-weight: 700; font-size: 0.95rem;">{mat['Runway_Days']} days</span>
                    </div>
                    <div class="card-footer-text">
                        <span>Runway Health</span>
                        <span>Risk Score: {mat['Risk_Score']}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.progress(health_ratio)
                st.caption(f"Trigger: {mat['Upcoming_Events']} | Contact: {mat['Supplier_Contact']}")
                st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: Runway Diagnostics & Interactive Visualizations
# ---------------------------------------------------------
with tab_analytics:
    st.subheader("Supply Chain Runway Diagnostics")
    st.caption("Visual comparisons highlighting materials at risk of exhausting stock before supplier orders arrive.")

    c_chart1, c_chart2 = st.columns([3, 2])

    with c_chart1:
        # Horizon Chart: Runway Days vs Supplier Lead Time (The Danger Zone)
        chart_data = []
        for e in evaluations:
            chart_data.append({
                "Material": e["Material_Name"][:22] + (".." if len(e["Material_Name"]) > 22 else ""),
                "Runway_Days": e["Runway_Days"],
                "Lead_Time_Days": e["Lead_Time_Days"],
                "Status": e["Status"]
            })
        cdf = pd.DataFrame(chart_data)

        fig_horizon = go.Figure()
        fig_horizon.add_trace(go.Bar(
            name="Runway Days (Stock On-Hand)",
            x=cdf["Material"],
            y=cdf["Runway_Days"],
            marker_color=[
                "#ef4444" if s == "CRITICAL" else ("#f59e0b" if s == "WARNING" else "#10b981")
                for s in cdf["Status"]
            ]
        ))
        fig_horizon.add_trace(go.Scatter(
            name="Supplier Lead Time Threshold",
            x=cdf["Material"],
            y=cdf["Lead_Time_Days"],
            mode="lines+markers",
            line=dict(color="#f43f5e", width=3, dash="dash"),
            marker=dict(size=8, color="#f43f5e")
        ))
        fig_horizon.update_layout(
            title="Runway Days vs Supplier Lead Time (Items below dashed red line risk stockout)",
            xaxis_tickangle=-45,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=430,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=120)
        )
        st.plotly_chart(fig_horizon, use_container_width=True)

    with c_chart2:
        # Donut Chart: Replenishment Capital Breakdown by Craft Category
        reorder_by_cat = {}
        for e in items_needing_po:
            cat = e["Category"]
            reorder_by_cat[cat] = reorder_by_cat.get(cat, 0.0) + e["Estimated_PO_Cost"]

        if reorder_by_cat:
            cat_df = pd.DataFrame(list(reorder_by_cat.items()), columns=["Category", "Capital"])
            fig_donut = px.pie(
                cat_df,
                names="Category",
                values="Capital",
                hole=0.45,
                title="Replenishment Capital by Craft Category",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=430
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.success("All inventory levels are optimal. No replenishment capital currently needed.")

    # Scatter Bubble Chart: Burn Rate vs Current Level vs Lead Time
    st.markdown("### Stockout Vulnerability Matrix")
    st.caption("Bubble size indicates Supplier Lead Time. SKUs in the upper-left represent the highest operational replenishment priority.")

    scat_df = pd.DataFrame(evaluations)
    fig_scatter = px.scatter(
        scat_df,
        x="Current_Level",
        y="Daily_Burn_Rate",
        size="Lead_Time_Days",
        color="Status",
        hover_name="Material_Name",
        color_discrete_map={"CRITICAL": "#ef4444", "WARNING": "#f59e0b", "HEALTHY": "#10b981"},
        labels={"Current_Level": "Current Stock Level (Units)", "Daily_Burn_Rate": "Daily Burn Rate (Units/Day)"},
        title="Burn Rate vs On-Hand Inventory (Bubble Size = Supplier Lead Time Days)"
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: Interactive What-If Scenario Lab
# ---------------------------------------------------------
with tab_simulator:
    st.subheader("Interactive What-If Scenario Simulator")
    st.caption("Adjust supplier lead times, burn rates, and buffer levels to forecast inventory resilience.")

    sim_col1, sim_col2 = st.columns([1, 1])

    material_names = list(raw_df["Material_Name"].unique())
    with sim_col1:
        target_name = st.selectbox("Select Material to Simulate", material_names)
        target_row = raw_df[raw_df["Material_Name"] == target_name].iloc[0]

        st.markdown(f"**Adjusting parameters for:** `{target_name}`")
        sim_current = st.slider("Current Stock Level", 0.0, 500.0, float(target_row["Current_Level"]), 1.0)
        sim_lead = st.slider("Supplier Lead Time (Days)", 1.0, 30.0, float(target_row["Lead_Time_Days"]), 1.0)
        sim_burn = st.slider("Daily Burn Rate (Units/Day)", 0.1, 50.0, float(target_row["Daily_Burn_Rate"]), 0.5)
        sim_safety = st.slider("Safety Stock Buffer (Units)", 0.0, 150.0, float(target_row.get("Safety_Stock", 10.0)), 1.0)

    with sim_col2:
        st.markdown("**Real-Time Simulation Feedback**")
        sim_rop = calculate_safety_stock(sim_lead, sim_burn, sim_safety)
        sim_runway = calculate_runway_days(sim_current, sim_burn)
        sim_risk = calculate_stockout_risk_score(sim_current, sim_lead, sim_burn, sim_safety)

        if sim_runway <= sim_lead:
            sim_status = "CRITICAL"
            st.error(f"Simulated Inventory Status: **{sim_status}** (Stockout occurs before shipment arrives!)")
        elif sim_current <= sim_rop:
            sim_status = "WARNING"
            st.warning(f"Simulated Inventory Status: **{sim_status}** (Stock level is at or below Reorder Point)")
        else:
            sim_status = "HEALTHY"
            st.success(f"Simulated Inventory Status: **{sim_status}** (Buffer is healthy)")

        r_col1, r_col2, r_col3 = st.columns(3)
        with r_col1:
            st.metric("Simulated Runway", f"{sim_runway:.1f} Days", delta=f"Lead: {sim_lead} Days")
        with r_col2:
            st.metric("Calculated ROP", f"{sim_rop:.1f} Units", delta=f"Current: {sim_current} Units")
        with r_col3:
            st.metric("Risk Score", f"{sim_risk:.1f}%", delta="Failure Probability")

        target_restore_stock = (30 * sim_burn) + sim_safety
        units_needed = max(0, int(np.ceil(target_restore_stock - sim_current)))
        unit_price = float(target_row.get("Unit_Cost", 5.0))
        st.info(f"Recommended replenishment order to restore 30-day runway: **{units_needed} units** (₹{units_needed * unit_price:,.2f})")

# ---------------------------------------------------------
# TAB 4: Autonomous Purchase Order Studio
# ---------------------------------------------------------
with tab_po:
    st.subheader("Autonomous Purchase Order Studio")
    st.caption("Consolidates all Critical and Warning inventory items into an itemized purchase order ready for vendor transmission.")

    if not items_needing_po:
        st.success("All inventory levels are optimal. No materials currently meet the replenishment threshold.")
    else:
        st.warning(f"**[ALERT] {len(items_needing_po)} Material{'s' if len(items_needing_po) != 1 else ''}** require replenishment to prevent stockouts.")

        po_table_df = generate_purchase_order_dataframe(items_needing_po)
        st.dataframe(po_table_df, use_container_width=True)

        st.markdown("---")
        po_text = generate_purchase_order(items_needing_po)

        c_po_left, c_po_right = st.columns([1, 1])
        with c_po_left:
            st.download_button(
                label="Download Purchase Order as Plain Text (.txt)",
                data=po_text,
                file_name="artisan_purchase_order.txt",
                mime="text/plain",
                use_container_width=True
            )
        with c_po_right:
            csv_data = po_table_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Purchase Order as CSV (.csv)",
                data=csv_data,
                file_name="artisan_purchase_order.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("#### Transmission Preview")
        st.text_area("PO Plaintext Payload", value=po_text, height=260)

# ---------------------------------------------------------
# TAB 5: Inventory Master Catalog
# ---------------------------------------------------------
with tab_data:
    st.subheader("Artisan Raw Materials Master Catalog")
    st.caption("Comprehensive data view with supplier contacts, lead times, and unit pricing.")

    master_display_df = pd.DataFrame(evaluations)[[
        "Material_Name", "Category", "Current_Level", "Lead_Time_Days",
        "Daily_Burn_Rate", "Reorder_Point", "Runway_Days", "Status",
        "Unit_Cost", "Estimated_PO_Cost", "Supplier_Contact", "Upcoming_Events"
    ]]

    st.dataframe(master_display_df, use_container_width=True)

    master_csv = raw_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Export Master Catalog as CSV",
        data=master_csv,
        file_name="artisan_materials_catalog.csv",
        mime="text/csv"
    )
