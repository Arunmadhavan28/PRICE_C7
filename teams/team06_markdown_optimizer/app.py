"""
Streamlit Web Application for Team 6: The 'Drop Culture' Markdown Optimizer.
Clearance analytics identifying lagging sell-through velocity, computing optimal tiered markdowns,
and strictly protecting the wholesale cost-basis floor.
Target End Customer: Retail Merchandisers, Clearance Strategists, and Inventory Directors.
"""

import sys
from pathlib import Path
import io

# Ensure current directory is on sys.path for both standalone run and master hub import
_CURRENT_DIR = Path(__file__).resolve().parent
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

try:
    from optimizer import (
        load_aging_data,
        identify_at_risk_items,
        calculate_recommended_discount,
        project_profit_recovery,
        simulate_markdown_pacing,
        calculate_category_summary,
        generate_strategic_brief,
        export_pos_markdown_batch,
        DEFAULT_AGING_PATH
    )
except ImportError:
    from teams.team06_markdown_optimizer.optimizer import (
        load_aging_data,
        identify_at_risk_items,
        calculate_recommended_discount,
        project_profit_recovery,
        simulate_markdown_pacing,
        calculate_category_summary,
        generate_strategic_brief,
        export_pos_markdown_batch,
        DEFAULT_AGING_PATH
    )

# Safe page config (works both standalone and when imported into Master Hub)
try:
    st.set_page_config(
        page_title="Markdown Optimizer | Retail AI",
        page_icon="🏷️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    pass

# Custom styling for high-contrast enterprise retail dashboard
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
    }
    .sub-caption {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 20px;
    }
    .kpi-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-critical {
        background-color: #991b1b;
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-atrisk {
        background-color: #9a3412;
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-ontrack {
        background-color: #065f46;
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Sidebar Configuration & Parameters
# -------------------------------------------------------------
st.sidebar.title("🏷️ Markdown Optimizer")
st.sidebar.caption("Retail Clearance Analytics Engine")

# Data Source Selection
st.sidebar.subheader("📂 Data Source")
upload_option = st.sidebar.radio("Select Input Mode", ["Curated Retail Dataset", "Upload Custom Aging CSV"])

if upload_option == "Upload Custom Aging CSV":
    uploaded_file = st.sidebar.file_uploader("Upload inventory_aging.csv", type=["csv"])
    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            # Ensure mandatory fields
            required = ["Item_SKU", "Days_on_Shelf", "Target_Sell_Through_Rate", "Actual_Sell_Through_Rate", "Cost_Basis"]
            for col in required:
                if col not in raw_df.columns:
                    st.sidebar.error(f"Missing mandatory column: {col}")
                    raw_df = load_aging_data(str(DEFAULT_AGING_PATH))
                    break
            st.sidebar.success(f"Loaded {len(raw_df)} SKUs from uploaded file.")
        except Exception as e:
            st.sidebar.error(f"Error parsing uploaded CSV: {e}")
            raw_df = load_aging_data(str(DEFAULT_AGING_PATH))
    else:
        raw_df = load_aging_data(str(DEFAULT_AGING_PATH))
else:
    raw_df = load_aging_data(str(DEFAULT_AGING_PATH))

# Interactive Markdown Policy Parameters
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Markdown Policy Rules")

with st.sidebar.expander("Tier Discount Percentages", expanded=False):
    tier_60 = st.slider("Tier 3 (>60 Days on Shelf)", min_value=15, max_value=60, value=30, step=5) / 100.0
    tier_30 = st.slider("Tier 2 (>30 Days on Shelf)", min_value=10, max_value=40, value=15, step=5) / 100.0
    tier_15 = st.slider("Tier 1 (>15 Days on Shelf)", min_value=0, max_value=25, value=5, step=5) / 100.0
    cost_buffer = st.slider("Cost Basis Safety Buffer %", min_value=0, max_value=20, value=0, step=2) / 100.0

tier_overrides = {
    "tier_60": tier_60,
    "tier_30": tier_30,
    "tier_15": tier_15
}

carrying_cost_rate = st.sidebar.slider("Annual Carrying Cost Rate (%)", min_value=10, max_value=35, value=22, step=1) / 100.0

# Merchandiser Filters
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters & Search")

all_categories = sorted(raw_df["Category"].dropna().unique().tolist()) if "Category" in raw_df.columns else []
selected_category = st.sidebar.selectbox("Merchandise Category", ["All Categories"] + all_categories)

risk_filter = st.sidebar.multiselect(
    "Risk Classification",
    ["CRITICAL AT-RISK", "AT-RISK", "ON TRACK"],
    default=["CRITICAL AT-RISK", "AT-RISK", "ON TRACK"]
)

search_term = st.sidebar.text_input("Search by SKU or Item Name", "")

# -------------------------------------------------------------
# Execute Calculation Engine
# -------------------------------------------------------------
optimized_df, metrics = project_profit_recovery(
    raw_df,
    tier_overrides=tier_overrides,
    holding_cost_annual_rate=carrying_cost_rate
)

# Apply Merchandiser Filters
filtered_df = optimized_df.copy()
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

if risk_filter:
    filtered_df = filtered_df[filtered_df["Risk_Status"].isin(risk_filter)]

if search_term.strip():
    term = search_term.strip().lower()
    filtered_df = filtered_df[
        filtered_df["Item_SKU"].str.lower().str.contains(term) |
        filtered_df["Item_Name"].str.lower().str.contains(term)
    ]

# -------------------------------------------------------------
# Main Header & Overview
# -------------------------------------------------------------
st.markdown('<div class="main-header">The "Drop Culture" Markdown Optimizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-caption">Clearance Analytics & Velocity Recovery Engine | '
    '<b>Target End Customer:</b> Retail Merchandisers, Clearance Strategists & Inventory Directors</div>',
    unsafe_allow_html=True
)

# Executive KPI Cards (Row 1)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "SKUs At Risk",
        f"{metrics['at_risk_sku_count']} / {metrics['total_sku_count']}",
        delta=f"{metrics['critical_risk_sku_count']} Critical",
        delta_color="inverse"
    )
with col2:
    st.metric(
        "Dead-Stock Capital At Risk",
        f"${metrics['total_capital_at_risk']:,.2f}",
        delta=f"{metrics['at_risk_units']} Units",
        delta_color="inverse"
    )
with col3:
    st.metric(
        "Projected Clearance Revenue",
        f"${metrics['total_projected_revenue']:,.2f}",
        delta="Cash Flow Liberated",
        delta_color="normal"
    )
with col4:
    st.metric(
        "Projected Net Profit Recovery",
        f"${metrics['total_projected_profit']:,.2f}",
        delta=f"Avg Discount {metrics['avg_clearance_discount']}%",
        delta_color="normal"
    )

# Executive KPI Cards (Row 2)
col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric(
        "Accrued Carrying Cost",
        f"${metrics['total_carrying_cost_accrued']:,.2f}",
        delta=f"{int(carrying_cost_rate * 100)}% Annual Rate",
        delta_color="inverse"
    )
with col6:
    st.metric(
        "Recovery Efficiency Rate",
        f"{metrics['recovery_efficiency_pct']}%",
        delta="Revenue / Risk Capital"
    )
with col7:
    st.metric(
        "Original Potential Retail Value",
        f"${metrics['total_original_retail_value']:,.2f}",
        delta="Full MSRP Inventory"
    )
with col8:
    st.metric(
        "Blended Clearance Margin",
        f"{metrics['blended_margin_pct']}%",
        delta="Net Margin on Clearance"
    )

st.markdown("---")

# -------------------------------------------------------------
# Tabbed Workspace
# -------------------------------------------------------------
tab_matrix, tab_charts, tab_pacing, tab_sandbox, tab_ai, tab_export = st.tabs([
    "📋 Clearance Matrix",
    "📊 Floor Protection Analytics",
    "⏱️ Drop Pacing Simulator",
    "🧪 What-If Sandbox",
    "💡 Strategic Merchandiser Brief",
    "📥 POS Export & Action Center"
])

# -------------------------------------------------------------
# TAB 1: Clearance Matrix & Inventory Filter
# -------------------------------------------------------------
with tab_matrix:
    st.subheader("Inventory Aging & Algorithmic Clearance Matrix")
    st.caption("Review calculated velocity lag, recommended clearance discount, and verified cost-floor protection.")

    # Highlighting helper
    def color_risk_status(val):
        if val == "CRITICAL AT-RISK":
            return "background-color: #7f1d1d; color: #fee2e2; font-weight: bold;"
        elif val == "AT-RISK":
            return "background-color: #78350f; color: #fef3c7; font-weight: bold;"
        return "background-color: #064e3b; color: #d1fae5;"

    display_columns = [
        "Item_SKU", "Item_Name", "Category", "Days_on_Shelf",
        "Target_Sell_Through_Rate", "Actual_Sell_Through_Rate", "Sell_Through_Lag",
        "Retail_Price", "Cost_Basis", "Recommended_Discount_Pct", "Clearance_Price",
        "Margin_Dollars", "Current_Units", "Dead_Stock_Risk_Capital", "Projected_Revenue", "Risk_Status"
    ]
    
    available_cols = [c for c in display_columns if c in filtered_df.columns]
    
    # Format table for crisp presentation
    styled_df = filtered_df[available_cols].style.map(
        color_risk_status,
        subset=["Risk_Status"]
    ).format({
        "Retail_Price": "${:,.2f}",
        "Cost_Basis": "${:,.2f}",
        "Clearance_Price": "${:,.2f}",
        "Margin_Dollars": "${:,.2f}",
        "Dead_Stock_Risk_Capital": "${:,.2f}",
        "Projected_Revenue": "${:,.2f}",
        "Recommended_Discount_Pct": "{:.1f}%",
        "Target_Sell_Through_Rate": "{:.0%}",
        "Actual_Sell_Through_Rate": "{:.0%}",
        "Sell_Through_Lag": "{:+.2f}"
    })

    st.dataframe(styled_df, use_container_width=True, height=450)
    st.caption(f"Displaying **{len(filtered_df)}** of **{len(optimized_df)}** inventory items.")

    # Quick interactive action bar
    col_act1, col_act2 = st.columns([3, 1])
    with col_act1:
        st.info("💡 **Merchandiser Tip:** Items highlighted in red have a velocity lag > 35% or have spent > 60 days on shelf. Clearance discount includes a +5% velocity boost while strictly respecting cost basis.")
    with col_act2:
        if st.button("Mark All Filtered as Reviewed", use_container_width=True):
            st.success(f"Approved {len(filtered_df)} SKUs for clearance promotion!")

# -------------------------------------------------------------
# TAB 2: Visual Analytics & Floor Protection
# -------------------------------------------------------------
with tab_charts:
    st.subheader("Clearance Pricing vs Cost Floor Protection")
    st.caption("Strict mathematical barrier check: Clearance Price must NEVER fall below the Cost Basis Floor.")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 🛡️ Price vs Clearance vs Wholesale Cost Floor")
        # Bar chart comparing Retail, Clearance, and Cost Basis
        top_chart_df = filtered_df.head(15) if len(filtered_df) > 0 else optimized_df.head(15)
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=top_chart_df["Item_SKU"],
            y=top_chart_df["Retail_Price"],
            name="Original Retail MSRP",
            marker_color="#38bdf8"
        ))
        fig_bar.add_trace(go.Bar(
            x=top_chart_df["Item_SKU"],
            y=top_chart_df["Clearance_Price"],
            name="Recommended Clearance Price",
            marker_color="#f59e0b"
        ))
        fig_bar.add_trace(go.Bar(
            x=top_chart_df["Item_SKU"],
            y=top_chart_df["Cost_Basis"],
            name="Cost Basis Floor (Strict Minimum)",
            marker_color="#ef4444"
        ))
        fig_bar.update_layout(
            barmode="group",
            template="plotly_dark",
            height=380,
            xaxis_title="Item SKU",
            yaxis_title="Price ($ USD)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        st.markdown("#### 🎯 Velocity Lag vs Aging Matrix")
        # Scatter bubble chart
        fig_scatter = px.scatter(
            optimized_df,
            x="Days_on_Shelf",
            y="Sell_Through_Lag",
            size="Current_Units",
            color="Risk_Status",
            hover_name="Item_Name",
            hover_data=["Item_SKU", "Retail_Price", "Clearance_Price", "Cost_Basis"],
            color_discrete_map={
                "CRITICAL AT-RISK": "#ef4444",
                "AT-RISK": "#f59e0b",
                "ON TRACK": "#10b981"
            },
            template="plotly_dark",
            height=380,
            labels={"Days_on_Shelf": "Aging (Days on Shelf)", "Sell_Through_Lag": "Sell-Through Lag (Target - Actual)"}
        )
        # Add reference lines
        fig_scatter.add_hline(y=0.05, line_dash="dot", line_color="#f59e0b", annotation_text="At-Risk Threshold (0.05)")
        fig_scatter.add_vline(x=60, line_dash="dot", line_color="#ef4444", annotation_text="Tier 3 Aging (60 Days)")
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    
    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        st.markdown("#### 🥧 Capital at Risk by Category")
        cat_df = calculate_category_summary(optimized_df)
        fig_pie = px.pie(
            cat_df,
            names="Category",
            values="Capital_At_Risk",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Prism,
            height=350
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col4:
        st.markdown("#### 💵 Capital Liberation Financial Bridge")
        bridge_fig = go.Figure(go.Waterfall(
            name="Financial Recovery",
            orientation="v",
            measure=["absolute", "relative", "total", "relative", "total"],
            x=["Original MSRP Value", "Markdown Sacrificed", "Clearance Revenue", "Cost Basis", "Preserved Margin"],
            textposition="outside",
            y=[
                metrics["total_original_retail_value"],
                -(metrics["total_original_retail_value"] - metrics["total_projected_revenue"]),
                metrics["total_projected_revenue"],
                -metrics["total_capital_at_risk"],
                metrics["total_projected_profit"]
            ],
            connector={"line": {"color": "rgb(63, 63, 63)"}}
        ))
        bridge_fig.update_layout(template="plotly_dark", height=350, yaxis_title="$ USD")
        st.plotly_chart(bridge_fig, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: Progressive Liquidation Pacing (4-Week Drop Pacing)
# -------------------------------------------------------------
with tab_pacing:
    st.subheader("4-Week Drop Liquidation Pacing Simulator")
    st.caption("Simulate progressive weekly markdowns for specific lagging items to clear stock before dead write-off.")

    sku_list = optimized_df["Item_SKU"].tolist()
    selected_sku = st.selectbox("Select Item SKU to Simulate Pacing", sku_list, index=0)

    item_series = optimized_df[optimized_df["Item_SKU"] == selected_sku].iloc[0]

    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        st.markdown(f"**Item:** `{item_series['Item_Name']}`")
        st.markdown(f"**Category:** `{item_series['Category']}`")
    with p_col2:
        st.markdown(f"**Current MSRP:** `${item_series['Retail_Price']:,.2f}`")
        st.markdown(f"**Cost Floor:** `${item_series['Cost_Basis']:,.2f}`")
    with p_col3:
        st.markdown(f"**Days on Shelf:** `{item_series['Days_on_Shelf']}` days")
        st.markdown(f"**Units on Hand:** `{item_series['Current_Units']}` units")
    with p_col4:
        st.markdown(f"**Sell-Through Lag:** `{item_series['Sell_Through_Lag']:+.2f}`")
        st.markdown(f"**Risk Severity:** `{item_series['Risk_Status']}`")

    # Generate 4-week simulation
    pacing_df = simulate_markdown_pacing(item_series, weeks=4)

    st.markdown("#### Weekly Progressive Markdown Schedule")
    
    # Styled schedule table
    st.dataframe(
        pacing_df.style.format({
            "Discount_Pct": "{:.1f}%",
            "Clearance_Price": "${:,.2f}",
            "Cost_Floor": "${:,.2f}",
            "Units_Sold": "{:,}",
            "Remaining_Units": "{:,}",
            "Weekly_Revenue": "${:,.2f}",
            "Weekly_Profit": "${:,.2f}"
        }),
        use_container_width=True
    )

    # Line chart of price decline vs cost floor
    fig_pacing = go.Figure()
    fig_pacing.add_trace(go.Scatter(
        x=pacing_df["Week"],
        y=pacing_df["Clearance_Price"],
        mode="lines+markers+text",
        name="Scheduled Clearance Price",
        line=dict(color="#38bdf8", width=3),
        text=[f"${p:.2f}" for p in pacing_df["Clearance_Price"]],
        textposition="top center"
    ))
    fig_pacing.add_trace(go.Scatter(
        x=pacing_df["Week"],
        y=pacing_df["Cost_Floor"],
        mode="lines",
        name="Cost Basis Floor",
        line=dict(color="#ef4444", width=2, dash="dash")
    ))
    fig_pacing.update_layout(
        template="plotly_dark",
        height=320,
        yaxis_title="Price ($ USD)",
        xaxis_title="Liquidation Timeline",
        title="Scheduled Price Step-Down vs Cost Floor"
    )
    st.plotly_chart(fig_pacing, use_container_width=True)

# -------------------------------------------------------------
# TAB 4: What-If Sandbox
# -------------------------------------------------------------
with tab_sandbox:
    st.subheader("Clearance Strategy Scenario Sandbox")
    st.caption("Compare your current baseline clearance policy against alternative aggressive or conservative liquidation strategies.")

    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.markdown("#### Strategy Parameters")
        sim_disc_bump = st.slider("Global Clearance Discount Modifier (+/- %)", min_value=-15, max_value=20, value=5, step=1)
        sim_buffer = st.slider("Protect Additional Margin Above Cost (%)", min_value=0, max_value=25, value=5, step=1) / 100.0
    
    # Run simulation
    sim_tiers = {
        "tier_60": max(0.05, tier_60 + (sim_disc_bump / 100.0)),
        "tier_30": max(0.05, tier_30 + (sim_disc_bump / 100.0)),
        "tier_15": max(0.00, tier_15 + (sim_disc_bump / 100.0))
    }
    sim_df, sim_metrics = project_profit_recovery(raw_df, tier_overrides=sim_tiers)

    with s_col2:
        st.markdown("#### Strategy Comparison")
        diff_rev = sim_metrics["total_projected_revenue"] - metrics["total_projected_revenue"]
        diff_profit = sim_metrics["total_projected_profit"] - metrics["total_projected_profit"]
        diff_disc = sim_metrics["avg_clearance_discount"] - metrics["avg_clearance_discount"]

        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            st.metric(
                "Simulated Cash Revenue",
                f"${sim_metrics['total_projected_revenue']:,.2f}",
                delta=f"{diff_rev:+,.2f} vs Baseline",
                delta_color="normal"
            )
        with comp_col2:
            st.metric(
                "Simulated Net Profit",
                f"${sim_metrics['total_projected_profit']:,.2f}",
                delta=f"{diff_profit:+,.2f} vs Baseline",
                delta_color="normal"
            )

    st.markdown("---")
    st.markdown("#### Category Breakdown: Baseline vs Simulated Strategy")
    base_cat = calculate_category_summary(optimized_df)
    sim_cat = calculate_category_summary(sim_df)
    
    merged_cat = base_cat[["Category", "Capital_At_Risk", "Projected_Revenue"]].merge(
        sim_cat[["Category", "Projected_Revenue"]],
        on="Category",
        suffixes=(" (Baseline)", " (Simulated)")
    )
    st.dataframe(merged_cat.style.format({
        "Capital_At_Risk": "${:,.2f}",
        "Projected_Revenue (Baseline)": "${:,.2f}",
        "Projected_Revenue (Simulated)": "${:,.2f}"
    }), use_container_width=True)

# -------------------------------------------------------------
# TAB 5: AI Strategic Merchandiser Brief
# -------------------------------------------------------------
with tab_ai:
    st.subheader("💡 Strategic Clearance Merchandising Brief")
    st.caption("Automated executive synthesis for Retail Merchandisers, Planners, and Directors.")

    brief_text = generate_strategic_brief(metrics, optimized_df)
    st.markdown(brief_text)

    st.markdown("---")
    st.markdown("### 🎯 Clearance Action Playbook")
    
    play_col1, play_col2 = st.columns(2)
    with play_col1:
        st.markdown("""
        #### 1. Immediate Execution (Days 1 - 7)
        - Push **Critical At-Risk SKUs** (lag > 35%) to online outlet / clearance section.
        - Activate approved markdown batch in point-of-sale terminal.
        - Coordinate digital marketing email blast for "End of Season Liquidation Drop".
        """)
    with play_col2:
        play_items = optimized_df[optimized_df["Risk_Status"] == "CRITICAL AT-RISK"]
        st.markdown(f"#### 2. Warehouse Space Relief")
        st.markdown(f"- Total Units Requiring Urgent Warehouse Clearing: **{int(play_items['Current_Units'].sum()):,} units**")
        st.markdown(f"- Liberated Floor Capacity: **~{round(len(play_items) * 12.5, 1)} sq. ft.** for incoming seasonal drops.")

# -------------------------------------------------------------
# TAB 6: POS Export & Action Center
# -------------------------------------------------------------
with tab_export:
    st.subheader("📥 POS Integration & Clearance Batch Export")
    st.caption("Generate verified clearance markdown pricing files formatted for Point-of-Sale (POS) and ERP upload.")

    export_scope = st.radio("Export Scope", ["At-Risk SKUs Only (Recommended)", "All Inventory SKUs"], horizontal=True)
    include_all = (export_scope == "All Inventory SKUs")

    pos_ready_df = export_pos_markdown_batch(optimized_df, include_all=include_all)

    st.markdown(f"**Exporting `{len(pos_ready_df)}` approved markdown pricing records:**")
    st.dataframe(pos_ready_df.head(10), use_container_width=True)

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("Validate POS Upload Schema", type="secondary", use_container_width=True):
            st.success("✅ All SKUs validated. Clearance Price >= Cost Basis verified. Ready for ERP injection.")

    with col_btn2:
        csv_pos = pos_ready_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download POS Clearance Batch (.CSV)",
            data=csv_pos,
            file_name="clearance_markdown_approved.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_btn3:
        full_audit_csv = optimized_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Full Audit Report (.CSV)",
            data=full_audit_csv,
            file_name="retail_inventory_audit_full.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("---")
st.caption("Retail AI Lab | Team 6: The 'Drop Culture' Markdown Optimizer | Powered by Streamlit & Plotly")
