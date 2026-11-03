"""
The Virtual Try-On Feedback Loop
AR/VR Commerce Telemetry & Incremental Conversion Attribution Engine.

An enterprise-grade, interactive executive analytics dashboard.
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Ensure local module imports resolve regardless of current working directory
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import importlib
import funnel_engine
importlib.reload(funnel_engine)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from funnel_engine import (
    load_session_logs,
    calculate_funnel_metrics,
    calculate_device_breakdown,
    calculate_revenue_impact,
    calculate_statistical_validation,
    calculate_engagement_buckets,
    calculate_revenue_timeseries,
    generate_executive_insights,
    generate_pdf_report
)

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="The Virtual Try-On Feedback Loop | Executive Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Strict Corporate Light Theme CSS (Section 1: Colour System)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Typography & Palette */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #F7F9FC;
        color: #172B4D;
    }

    [data-testid="stHeader"] {
        background-color: rgba(247, 249, 252, 0.95);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #E2E8F0;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #172B4D !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Header Component */
    .top-header-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding-bottom: 14px;
        margin-bottom: 16px;
        border-bottom: 1px solid #E2E8F0;
    }

    .badge-data-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .tag-category {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.70rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    /* Six KPI Cards (Uniform Height & Clean Borders) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        min-height: 140px;
        box-shadow: 0 1px 3px 0 rgba(23, 43, 77, 0.04);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 6px -1px rgba(23, 43, 77, 0.06);
    }

    div[data-testid="stMetricLabel"] p {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }

    div[data-testid="stMetricValue"] div {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #172B4D !important;
        letter-spacing: -0.03em;
        line-height: 1.15;
    }

    /* Executive Synthesis Structured Cards */
    .synthesis-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px 0 rgba(23, 43, 77, 0.03);
    }

    .synthesis-card-title {
        color: #172B4D;
        font-size: 0.90rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .synthesis-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 8px;
        display: inline-block;
    }

    .takeaway-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #059669;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
        color: #64748B;
        padding: 10px 18px;
        border-radius: 6px 6px 0 0;
    }

    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom: 2px solid #2563EB !important;
        background-color: transparent !important;
    }

    hr {
        margin: 1.5rem 0;
        border: 0;
        border-top: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Ingestion
# -----------------------------------------------------------------------------
DATA_PATH = Path(__file__).resolve().parent / "data" / "session_logs.csv"

try:
    raw_df = load_session_logs(str(DATA_PATH))
except Exception as e:
    st.error(f"Failed to load session logs from {DATA_PATH}: {str(e)}")
    st.stop()

# -----------------------------------------------------------------------------
# State Management: Reset Filters (Section 3)
# -----------------------------------------------------------------------------
if "reset_trigger" not in st.session_state:
    st.session_state["reset_trigger"] = 0

def reset_all_filters():
    st.session_state["filter_device"] = "All Devices"
    st.session_state["filter_category"] = "All Categories"
    st.session_state["filter_cohort"] = "All Shoppers"
    st.session_state["filter_purchase"] = "All Sessions"
    st.session_state["filter_min_ar_time"] = 0
    if "Timestamp" in raw_df.columns and not raw_df["Timestamp"].isna().all():
        min_d = raw_df["Timestamp"].min().date()
        max_d = raw_df["Timestamp"].max().date()
        st.session_state["filter_date_range"] = (min_d, max_d)
    st.session_state["reset_trigger"] += 1

# -----------------------------------------------------------------------------
# Sidebar: Collapsible & Enterprise Filter Hierarchy (Section 3)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<span class="tag-category">Dashboard Controls</span>', unsafe_allow_html=True)
    st.markdown("### Cohort & Session Filters")
    st.caption("Apply constraints to evaluate performance across segments. All views update dynamically.")

    # 1. Device Platform Filter
    device_options = ["All Devices"] + sorted(raw_df["Device_Type"].unique().tolist())
    selected_device = st.selectbox(
        "Device Platform",
        options=device_options,
        key="filter_device",
        help="Filter sessions by client hardware and operating platform."
    )

    # 2. Product Category Filter
    category_options = ["All Categories"]
    if "Product_Category" in raw_df.columns:
        category_options += sorted(raw_df["Product_Category"].unique().tolist())
    selected_category = st.selectbox(
        "Product Category",
        options=category_options,
        key="filter_category",
        help="Filter sessions by merchandised fashion category."
    )

    # 3. Date Range Filter
    has_dates = "Timestamp" in raw_df.columns and not raw_df["Timestamp"].isna().all()
    if has_dates:
        default_min_date = raw_df["Timestamp"].min().date()
        default_max_date = raw_df["Timestamp"].max().date()
        selected_date_range = st.date_input(
            "Date Range",
            value=(default_min_date, default_max_date),
            min_value=default_min_date,
            max_value=default_max_date,
            key="filter_date_range",
            help="Filter session records within a specific calendar range."
        )
    else:
        selected_date_range = None

    # 4. Customer Cohort Filter
    selected_cohort = st.selectbox(
        "Customer Cohort",
        options=["All Shoppers", "AR Try-On Shoppers Only", "Standard / Non-AR Shoppers Only"],
        key="filter_cohort",
        help="Isolate users who engaged with the virtual try-on feature vs baseline control."
    )

    # 5. Purchase Status Filter
    selected_purchase_status = st.selectbox(
        "Purchase Status",
        options=["All Sessions", "Completed Purchases", "Abandoned Sessions"],
        key="filter_purchase",
        help="Filter sessions by checkout conversion outcome."
    )

    # 6. Minimum Time in AR Slider (0 to 300 seconds)
    min_ar_time = st.slider(
        "Minimum Time in AR (Seconds)",
        min_value=0,
        max_value=300,
        value=0,
        step=10,
        key="filter_min_ar_time",
        help="Isolate deep-engagement AR sessions. Non-AR sessions remain as baseline control."
    )

    st.markdown("---")

    # Reset Filters Button
    if st.button("Reset Filters to Default", use_container_width=True):
        reset_all_filters()
        st.rerun()

    st.markdown("### Telemetry Scope")
    st.info(
        f"**Source:** Static Benchmark Dataset\n\n"
        f"**Total Records:** {len(raw_df):,} sessions\n\n"
        f"**Historical Date Window:** Oct 1, 2026 – Oct 31, 2026"
    )

# -----------------------------------------------------------------------------
# Apply Filtering Logic Dynamically
# -----------------------------------------------------------------------------
filtered_df = raw_df.copy()

# Device
if selected_device != "All Devices":
    filtered_df = filtered_df[filtered_df["Device_Type"] == selected_device]

# Category
if selected_category != "All Categories" and "Product_Category" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Product_Category"] == selected_category]

# Date Range
if has_dates and isinstance(selected_date_range, (tuple, list)) and len(selected_date_range) == 2:
    start_d, end_d = selected_date_range
    filtered_df = filtered_df[
        (filtered_df["Timestamp"].dt.date >= start_d) & (filtered_df["Timestamp"].dt.date <= end_d)
    ]

# Cohort
if selected_cohort == "AR Try-On Shoppers Only":
    filtered_df = filtered_df[filtered_df["AR_TryOn_Used"] == True]
elif selected_cohort == "Standard / Non-AR Shoppers Only":
    filtered_df = filtered_df[filtered_df["AR_TryOn_Used"] == False]

# Purchase Status
if selected_purchase_status == "Completed Purchases":
    filtered_df = filtered_df[filtered_df["Purchase_Made"] == True]
elif selected_purchase_status == "Abandoned Sessions":
    filtered_df = filtered_df[filtered_df["Purchase_Made"] == False]

# Minimum AR Time
if min_ar_time > 0:
    filtered_df = filtered_df[
        (filtered_df["AR_TryOn_Used"] == False) | (filtered_df["Time_in_AR"] >= min_ar_time)
    ]

# Core dynamic computations
metrics = calculate_funnel_metrics(filtered_df)
revenue_impact = calculate_revenue_impact(metrics)
device_df = calculate_device_breakdown(filtered_df)
engagement_df = calculate_engagement_buckets(filtered_df)
stat_val = calculate_statistical_validation(
    metrics["ar_purchases"], metrics["ar_sessions"],
    metrics["non_ar_purchases"], metrics["non_ar_sessions"]
)
timeseries_df = calculate_revenue_timeseries(filtered_df)
insights_dict = generate_executive_insights(metrics, revenue_impact, stat_val, device_df, engagement_df)

# Filter Summary String
active_filters = []
if selected_device != "All Devices":
    active_filters.append(f"Device: {selected_device}")
if selected_category != "All Categories":
    active_filters.append(f"Category: {selected_category}")
if selected_cohort != "All Shoppers":
    active_filters.append(f"Cohort: {selected_cohort}")
if selected_purchase_status != "All Sessions":
    active_filters.append(f"Status: {selected_purchase_status}")
if min_ar_time > 0:
    active_filters.append(f"Min AR: >={min_ar_time}s")

filter_summary_str = " | ".join(active_filters) if active_filters else "All Traffic (Unfiltered Benchmark)"

# -----------------------------------------------------------------------------
# Dashboard Header (Section 2)
# -----------------------------------------------------------------------------
header_left, header_right = st.columns([2.5, 1.2])

with header_left:
    st.markdown('<span class="tag-category">Retail AI Analytics</span>', unsafe_allow_html=True)
    st.markdown("""
    <h1 style="margin: 0; font-size: 1.85rem; font-weight: 800; color: #172B4D; letter-spacing: -0.025em;">
        The Virtual Try-On Feedback Loop
    </h1>
    <p style="margin: 4px 0 0 0; font-size: 0.90rem; color: #64748B;">
        AR/VR Commerce Telemetry & Incremental Conversion Attribution Engine
    </p>
    """, unsafe_allow_html=True)

with header_right:
    st.markdown('<span class="badge-data-status">Data Status: Sample Telemetry Benchmark</span>', unsafe_allow_html=True)
    st.caption(f"Last Refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC")
    refresh_col, export_col = st.columns(2)
    with refresh_col:
        if st.button("Refresh Telemetry", use_container_width=True):
            st.rerun()
    with export_col:
        # Pre-generate PDF for quick export
        pdf_bytes = generate_pdf_report(metrics, revenue_impact, stat_val, device_df, engagement_df, filter_summary_str)
        st.download_button(
            label="Export PDF Report",
            data=pdf_bytes,
            file_name=f"virtual_tryon_report_{date.today().isoformat()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# Active Filter Indicator & Count
total_records = len(raw_df)
current_records = len(filtered_df)
pct_active = (current_records / total_records * 100.0) if total_records > 0 else 0.0

st.markdown(
    f"<div style='background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 14px; margin-top: 10px; font-size: 0.82rem; color: #475569;'>"
    f"<strong>Active Filter Scope:</strong> {filter_summary_str} &nbsp;|&nbsp; "
    f"<strong>Filtered Volume:</strong> Showing {current_records:,} of {total_records:,} sessions ({pct_active:.1f}%)"
    f"</div>",
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------------------------------------------------------
# Six KPI Cards (Section 4: KPI Cards)
# -----------------------------------------------------------------------------
kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5, kpi_c6 = st.columns(6)

with kpi_c1:
    st.metric(
        label="1. AR Conversion Rate",
        value=f"{metrics['cr_ar']:.1f}%",
        delta=f"{metrics['ar_purchases']} purchases",
        help="Percentage of sessions engaging in AR that completed a checkout: (AR Purchases / AR Sessions) * 100."
    )
    st.caption(f"{metrics['ar_sessions']} total AR sessions")

with kpi_c2:
    lift = metrics["conversion_lift_pct"]
    lift_sign = "+" if lift > 0 else ""
    st.metric(
        label="2. AR Conversion Lift",
        value=f"{lift_sign}{lift:.1f}%",
        delta=f"{stat_val['absolute_diff_pp']:+.1f} pp diff",
        help="Percentage lift in conversion rate over standard control: ((CR_AR - CR_NonAR) / CR_NonAR) * 100."
    )
    st.caption("Relative lift vs control")

with kpi_c3:
    st.metric(
        label="3. Non-AR Conversion Rate",
        value=f"{metrics['cr_non_ar']:.1f}%",
        delta=f"{metrics['non_ar_purchases']} purchases",
        help="Baseline conversion rate of standard browsing visitors: (Non-AR Purchases / Non-AR Sessions) * 100."
    )
    st.caption(f"{metrics['non_ar_sessions']} control sessions")

with kpi_c4:
    aov_diff = metrics["aov_ar"] - metrics["aov_non_ar"]
    aov_sign = "+" if aov_diff >= 0 else ""
    st.metric(
        label="4. AR Average Order Value",
        value=f"${metrics['aov_ar']:.2f}",
        delta=f"{aov_sign}${aov_diff:.2f} vs Control",
        help="Mean transaction cart value for converting AR shoppers: Total AR Cart Value / AR Purchases."
    )
    st.caption(f"Baseline: ${metrics['aov_non_ar']:.2f}")

with kpi_c5:
    inc_rev = revenue_impact["incremental_revenue"]
    st.metric(
        label="5. Estimated Incremental Rev",
        value=f"${inc_rev:,.2f}",
        delta=f"+{revenue_impact['rps_lift_pct']:.1f}% RPS Lift",
        help="Modeled incremental revenue beyond baseline: Total AR Revenue - (AR Sessions * Non-AR RPS)."
    )
    st.caption("Model-estimated revenue uplift")

with kpi_c6:
    st.metric(
        label="6. AR Adoption Rate",
        value=f"{metrics['adoption_rate_pct']:.1f}%",
        delta=f"{metrics['ar_sessions']} / {metrics['total_sessions']} users",
        help="Percentage of total store traffic that utilized virtual try-on: (AR Sessions / Total Sessions) * 100."
    )
    st.caption("Feature adoption share")

st.markdown("---")

# -----------------------------------------------------------------------------
# Base Layout Config for Plotly Charts (White Theme & High Contrast)
# -----------------------------------------------------------------------------
plotly_light_theme = dict(
    template="plotly_white",
    paper_bgcolor="rgba(255,255,255,1)",
    plot_bgcolor="rgba(255,255,255,1)",
    font=dict(family="Inter, sans-serif", color="#172B4D"),
    margin=dict(l=20, r=20, t=35, b=20)
)

# -----------------------------------------------------------------------------
# Section 5 & 6: Conversion Analytics & Separate CR / AOV Charts
# -----------------------------------------------------------------------------
sec5_col, sec6_col = st.columns([1.1, 1.0])

with sec5_col:
    st.subheader("Comparative Conversion Funnel")
    st.caption("Stage-to-stage progression from product browsing visits through completed checkout.")

    fig_funnel = go.Figure()

    # AR Funnel (Green #059669)
    fig_funnel.add_trace(go.Funnel(
        name="AR Try-On Cohort",
        y=["Session Visits", "Engaged with AR", "Completed Checkout"],
        x=[metrics["ar_sessions"], metrics["ar_sessions"], metrics["ar_purchases"]],
        textinfo="value+percent initial",
        marker=dict(color="#059669"),
        connector=dict(line=dict(color="#10B981", width=2))
    ))

    # Non-AR Funnel (Blue #2563EB)
    fig_funnel.add_trace(go.Funnel(
        name="Standard Control Cohort",
        y=["Session Visits", "Standard Browsing", "Completed Checkout"],
        x=[metrics["non_ar_sessions"], metrics["non_ar_sessions"], metrics["non_ar_purchases"]],
        textinfo="value+percent initial",
        marker=dict(color="#2563EB"),
        connector=dict(line=dict(color="#3B82F6", width=2))
    ))

    fig_funnel.update_layout(
        **plotly_light_theme,
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with sec6_col:
    # Separate Conversion Rate & AOV Charts (Section 6)
    st.subheader("Cohort Benchmarking")
    st.caption("Independent comparisons preventing mixed-axis ambiguity.")

    tab_cr, tab_aov = st.tabs(["Conversion Rate (%)", "Average Basket Value ($)"])

    with tab_cr:
        cr_chart_df = pd.DataFrame([
            {"Cohort": "AR Try-On Users", "Conversion_Rate": metrics["cr_ar"], "Label": f"{metrics['cr_ar']:.1f}%"},
            {"Cohort": "Non-AR Control", "Conversion_Rate": metrics["cr_non_ar"], "Label": f"{metrics['cr_non_ar']:.1f}%"}
        ])

        fig_cr = px.bar(
            cr_chart_df,
            x="Cohort",
            y="Conversion_Rate",
            color="Cohort",
            text="Label",
            color_discrete_map={"AR Try-On Users": "#059669", "Non-AR Control": "#2563EB"}
        )
        fig_cr.update_layout(
            **plotly_light_theme,
            height=300,
            yaxis=dict(title="Conversion Rate (%)", gridcolor="#F1F5F9"),
            xaxis=dict(title="", gridcolor="#F1F5F9"),
            showlegend=False
        )
        fig_cr.update_traces(textposition="outside")
        st.plotly_chart(fig_cr, use_container_width=True)
        st.caption(f"Difference: **{stat_val['absolute_diff_pp']:+.1f} percentage points** ({metrics['conversion_lift_pct']:+.1f}% relative lift)")

    with tab_aov:
        aov_chart_df = pd.DataFrame([
            {"Cohort": "AR Try-On Users", "AOV": metrics["aov_ar"], "Label": f"${metrics['aov_ar']:.2f}"},
            {"Cohort": "Non-AR Control", "AOV": metrics["aov_non_ar"], "Label": f"${metrics['aov_non_ar']:.2f}"}
        ])

        fig_aov = px.bar(
            aov_chart_df,
            x="Cohort",
            y="AOV",
            color="Cohort",
            text="Label",
            color_discrete_map={"AR Try-On Users": "#059669", "Non-AR Control": "#2563EB"}
        )
        fig_aov.update_layout(
            **plotly_light_theme,
            height=300,
            yaxis=dict(title="Average Order Value ($)", gridcolor="#F1F5F9"),
            xaxis=dict(title="", gridcolor="#F1F5F9"),
            showlegend=False
        )
        fig_aov.update_traces(textposition="outside")
        st.plotly_chart(fig_aov, use_container_width=True)
        st.caption(f"Difference: **+${aov_diff:.2f} per basket** ({((aov_diff / max(0.01, metrics['aov_non_ar']))*100):+.1f}% relative uplift)")

st.markdown("---")

# -----------------------------------------------------------------------------
# Deep Dive Analysis Tabs: Sections 7, 8, 9, 11
# -----------------------------------------------------------------------------
tab_device_perf, tab_financial, tab_telemetry, tab_stats = st.tabs([
    "Device Performance",
    "Financial Attribution",
    "AR Engagement Telemetry",
    "Statistical Validation"
])

# -----------------------------------------------------------------------------
# Section 7: Device Performance
# -----------------------------------------------------------------------------
with tab_device_perf:
    st.subheader("Performance by Client Environment")
    st.caption("Evaluating virtual try-on responsiveness and conversion across mobile and desktop devices.")

    if not device_df.empty:
        col_dev_l, col_dev_r = st.columns([1.1, 1.0])

        with col_dev_l:
            melted_dev = device_df.melt(
                id_vars=["Device_Type"],
                value_vars=["AR_CR_%", "Non_AR_CR_%"],
                var_name="Cohort",
                value_name="Conversion_Rate"
            )
            melted_dev["Cohort"] = melted_dev["Cohort"].map({
                "AR_CR_%": "AR Users",
                "Non_AR_CR_%": "Non-AR Control"
            })

            fig_dev_bar = px.bar(
                melted_dev,
                x="Device_Type",
                y="Conversion_Rate",
                color="Cohort",
                barmode="group",
                title="Conversion Rate by Platform",
                color_discrete_map={"AR Users": "#059669", "Non-AR Control": "#2563EB"}
            )
            fig_dev_bar.update_layout(
                **plotly_light_theme,
                height=320,
                yaxis=dict(title="Conversion Rate (%)", gridcolor="#F1F5F9"),
                xaxis=dict(title="Device Type", gridcolor="#F1F5F9")
            )
            st.plotly_chart(fig_dev_bar, use_container_width=True)

        with col_dev_r:
            st.markdown("#### Performance Matrix")
            # Highlight top performer
            best_device = device_df.sort_values("Conversion_Lift_%", ascending=False).iloc[0]["Device_Type"]
            st.markdown(
                f"<div style='background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; padding: 8px 12px; margin-bottom: 12px; font-size: 0.82rem; color: #065F46;'>"
                f"<strong>Top Performing Platform:</strong> {best_device} delivers the highest relative conversion lift in active telemetry."
                f"</div>",
                unsafe_allow_html=True
            )

            formatted_dev = device_df.rename(columns={
                "Device_Type": "Platform",
                "Total_Sessions": "Sessions",
                "AR_Sessions": "AR Visits",
                "Non_AR_Sessions": "Control Visits",
                "Adoption_Rate_%": "Adoption %",
                "AR_CR_%": "AR CR %",
                "Non_AR_CR_%": "Control CR %",
                "Conversion_Lift_%": "Lift %",
                "AR_AOV_$": "AR AOV ($)",
                "Non_AR_AOV_$": "Control AOV ($)",
                "AR_Total_Rev_$": "AR Revenue ($)",
                "Non_AR_Total_Rev_$": "Control Rev ($)"
            })

            st.dataframe(
                formatted_dev.style.format({
                    "Adoption %": "{:.1f}%",
                    "AR CR %": "{:.1f}%",
                    "Control CR %": "{:.1f}%",
                    "Lift %": "{:+.1f}%",
                    "AR AOV ($)": "${:.2f}",
                    "Control AOV ($)": "${:.2f}",
                    "AR Revenue ($)": "${:,.2f}",
                    "Control Rev ($)": "${:,.2f}"
                }),
                use_container_width=True
            )
    else:
        st.info("No device data available for current filter selection.")

# -----------------------------------------------------------------------------
# Section 8: Financial Impact & Revenue Attribution
# -----------------------------------------------------------------------------
with tab_financial:
    st.subheader("Comprehensive Financial Attribution")
    st.caption("Distinguishing observed gross transaction volume from estimated incremental revenue.")

    fin_k1, fin_k2, fin_k3, fin_k4 = st.columns(4)
    with fin_k1:
        st.metric("Total AR Gross Revenue", f"${metrics['total_rev_ar']:,.2f}")
    with fin_k2:
        st.metric("Total Non-AR Gross Revenue", f"${metrics['total_rev_non_ar']:,.2f}")
    with fin_k3:
        st.metric("Revenue Per AR Session", f"${revenue_impact['rps_ar']:.2f}")
    with fin_k4:
        st.metric(
            "Estimated Incremental Revenue",
            f"${revenue_impact['incremental_revenue']:,.2f}",
            delta=f"+{revenue_impact['rps_lift_pct']:.1f}% RPS Lift"
        )

    col_fin_pie, col_fin_rps = st.columns([1, 1])

    with col_fin_pie:
        rev_share_df = pd.DataFrame([
            {"Cohort": "AR Try-On Shoppers", "Revenue": metrics["total_rev_ar"]},
            {"Cohort": "Standard Control", "Revenue": metrics["total_rev_non_ar"]}
        ])
        fig_fin_pie = px.pie(
            rev_share_df,
            names="Cohort",
            values="Revenue",
            title="Gross Revenue Contribution Share",
            color="Cohort",
            color_discrete_map={"AR Try-On Shoppers": "#059669", "Standard Control": "#2563EB"},
            hole=0.48
        )
        fig_fin_pie.update_layout(**plotly_light_theme, height=310)
        st.plotly_chart(fig_fin_pie, use_container_width=True)

    with col_fin_rps:
        rps_df = pd.DataFrame([
            {"Cohort": "AR Try-On Users", "RPS": revenue_impact["rps_ar"]},
            {"Cohort": "Non-AR Control", "RPS": revenue_impact["rps_non_ar"]}
        ])
        fig_rps = px.bar(
            rps_df,
            x="Cohort",
            y="RPS",
            title="Revenue Per Session (RPS) Comparison ($/Session)",
            text_auto=".2f",
            color="Cohort",
            color_discrete_map={"AR Try-On Users": "#059669", "Non-AR Control": "#2563EB"}
        )
        fig_rps.update_layout(
            **plotly_light_theme,
            height=310,
            yaxis=dict(title="Revenue Per Session ($)", gridcolor="#F1F5F9"),
            xaxis=dict(title="", gridcolor="#F1F5F9"),
            showlegend=False
        )
        st.plotly_chart(fig_rps, use_container_width=True)

    # Revenue trend over time
    if not timeseries_df.empty:
        st.markdown("#### Historical Revenue Velocity Over Time")
        fig_ts = px.line(
            timeseries_df,
            x="Date",
            y="Revenue",
            color="Cohort",
            title="Daily Transaction Revenue by Cohort",
            color_discrete_map={"AR Users": "#059669", "Non-AR Users": "#2563EB"}
        )
        fig_ts.update_layout(
            **plotly_light_theme,
            height=280,
            yaxis=dict(title="Daily Revenue ($)", gridcolor="#F1F5F9"),
            xaxis=dict(title="Date", gridcolor="#F1F5F9")
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    # Methodology Documentation Note
    st.info(
        "**Financial Modeling Methodology:** "
        "Observed Revenue represents the exact total of completed transactions recorded. "
        "Estimated Incremental Revenue is modeled counterfactually as: "
        "`Incremental Revenue = Total AR Revenue - (AR Sessions * Non-AR Revenue Per Session)`. "
        "This isolates the value created beyond standard baseline conversion efficiency."
    )

# -----------------------------------------------------------------------------
# Section 9: AR Engagement Telemetry
# -----------------------------------------------------------------------------
with tab_telemetry:
    st.subheader("AR Engagement Telemetry & Duration Buckets")
    st.caption("Analyzing session duration in 3D/AR mode across discrete engagement intervals.")

    ar_sessions_df = filtered_df[filtered_df["AR_TryOn_Used"] == True]

    if not ar_sessions_df.empty:
        eng_col1, eng_col2, eng_col3 = st.columns(3)
        mean_all = ar_sessions_df["Time_in_AR"].mean()
        purch_df = ar_sessions_df[ar_sessions_df["Purchase_Made"] == True]
        aban_df = ar_sessions_df[ar_sessions_df["Purchase_Made"] == False]
        mean_purch = purch_df["Time_in_AR"].mean() if not purch_df.empty else 0.0
        mean_aban = aban_df["Time_in_AR"].mean() if not aban_df.empty else 0.0

        with eng_col1:
            st.metric("Avg AR Engagement Duration", f"{mean_all:.1f}s", help="Mean active time spent inside AR virtual try-on mode.")
        with eng_col2:
            st.metric("Avg Duration: Converting Shoppers", f"{mean_purch:.1f}s", delta=f"+{mean_purch - mean_aban:.1f}s vs Abandoners")
        with eng_col3:
            st.metric("Avg Duration: Abandoning Shoppers", f"{mean_aban:.1f}s")

        col_eng_chart, col_eng_table = st.columns([1.1, 1.0])

        with col_eng_chart:
            if not engagement_df.empty:
                fig_buckets = px.bar(
                    engagement_df,
                    x="Bucket",
                    y="Conversion_Rate_%",
                    title="Conversion Rate by Engagement Duration Interval",
                    text_auto=".1f",
                    color_discrete_sequence=["#059669"]
                )
                fig_buckets.update_layout(
                    **plotly_light_theme,
                    height=320,
                    yaxis=dict(title="Conversion Rate (%)", gridcolor="#F1F5F9"),
                    xaxis=dict(title="Engagement Duration Bucket", gridcolor="#F1F5F9")
                )
                st.plotly_chart(fig_buckets, use_container_width=True)

        with col_eng_table:
            st.markdown("#### Engagement Bucket Breakdown")
            st.dataframe(
                engagement_df.style.format({
                    "Conversion_Rate_%": "{:.1f}%",
                    "Abandonment_Rate_%": "{:.1f}%"
                }),
                use_container_width=True
            )

        st.caption(
            "Note: Engagement telemetry reflects user exploration depth. "
            "Correlation between longer AR time and conversion indicates user consideration rather than causation."
        )
    else:
        st.info("No active AR sessions in the current filter scope.")

# -----------------------------------------------------------------------------
# Section 11: Statistical Validation
# -----------------------------------------------------------------------------
with tab_stats:
    st.subheader("Statistical Validation & Causal Inference")
    st.caption("Hypothesis testing and confidence bounds for conversion rate differences.")

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("Z-Statistic", f"{stat_val['z_score']:.2f}", help="Two-proportion pooled z-test statistic.")
    with stat_col2:
        st.metric("p-value", f"{stat_val['p_value']:.4f}", help="Probability of observing this lift under the null hypothesis.")
    with stat_col3:
        sig_label = "Significant (p < 0.05)" if stat_val["is_significant"] else "Not Significant"
        st.metric("Statistical Significance", sig_label)
    with stat_col4:
        st.metric("Sample Size Evaluated", f"{stat_val['sample_size_total']:,} visits")

    st.markdown("#### 95% Confidence Interval Bounds")
    ci_col1, ci_col2 = st.columns(2)
    with ci_col1:
        st.markdown(
            f"<div style='background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px;'>"
            f"<span style='color: #059669; font-weight: 700;'>AR Cohort 95% CI</span>: "
            f"<strong>{stat_val['ci_ar'][0]:.1f}% to {stat_val['ci_ar'][1]:.1f}%</strong>"
            f"<br><span style='font-size: 0.80rem; color: #64748B;'>Estimated true conversion rate range for AR shoppers.</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    with ci_col2:
        st.markdown(
            f"<div style='background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px;'>"
            f"<span style='color: #2563EB; font-weight: 700;'>Control Cohort 95% CI</span>: "
            f"<strong>{stat_val['ci_non_ar'][0]:.1f}% to {stat_val['ci_non_ar'][1]:.1f}%</strong>"
            f"<br><span style='font-size: 0.80rem; color: #64748B;'>Estimated true conversion rate range for standard control shoppers.</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "**Methodological Advisory on Causal Limitations:** "
        "The current dataset represents observational telemetry rather than a randomized controlled trial (A/B test). "
        "Shoppers voluntarily initiated the AR feature, introducing potential self-selection bias (shoppers with higher intent or newer devices "
        "may be more likely to launch virtual try-on). While the observed difference is statistically significant (p < 0.05), "
        "business executives should validate these results with a true randomized A/B test before committing to large-scale vendor contracts."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# Section 10: Executive Synthesis and Strategic Insights
# -----------------------------------------------------------------------------
st.subheader("Executive Synthesis & Strategic Insights")
st.caption("Actionable business recommendations derived dynamically from active telemetry filters.")

# Key Takeaways (Top 3)
st.markdown("#### Key Takeaways")
for idx, item in enumerate(insights_dict["key_takeaways"], 1):
    st.markdown(
        f"<div class='takeaway-box'>"
        f"<strong>{idx}.</strong> {item}"
        f"</div>",
        unsafe_allow_html=True
    )

# Structured Insight Cards
st.markdown("#### Detailed Business Assessment")
ins_col1, ins_col2 = st.columns(2)

ins_sections = insights_dict["sections"]

with ins_col1:
    # 1. Conversion Efficiency
    ce = ins_sections["conversion_efficiency"]
    st.markdown(f"""
    <div class="synthesis-card" style="border-left: 4px solid #059669;">
        <span class="synthesis-badge" style="background-color: #ECFDF5; color: #065F46;">{ce['title']}</span>
        <div class="synthesis-card-title">Finding: {ce['finding']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Supporting Metric:</strong> {ce['metric']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Business Implication:</strong> {ce['implication']}</div>
        <div style="font-size: 0.82rem; color: #047857;"><strong>Recommended Action:</strong> {ce['action']}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Revenue Attribution
    ra = ins_sections["revenue_attribution"]
    st.markdown(f"""
    <div class="synthesis-card" style="border-left: 4px solid #2563EB;">
        <span class="synthesis-badge" style="background-color: #EFF6FF; color: #1D4ED8;">{ra['title']}</span>
        <div class="synthesis-card-title">Finding: {ra['finding']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Supporting Metric:</strong> {ra['metric']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Business Implication:</strong> {ra['implication']}</div>
        <div style="font-size: 0.82rem; color: #1D4ED8;"><strong>Recommended Action:</strong> {ra['action']}</div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Device Performance
    dp = ins_sections["device_performance"]
    st.markdown(f"""
    <div class="synthesis-card" style="border-left: 4px solid #D97706;">
        <span class="synthesis-badge" style="background-color: #FEF3C7; color: #92400E;">{dp['title']}</span>
        <div class="synthesis-card-title">Finding: {dp['finding']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Supporting Metric:</strong> {dp['metric']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Business Implication:</strong> {dp['implication']}</div>
        <div style="font-size: 0.82rem; color: #B45309;"><strong>Recommended Action:</strong> {dp['action']}</div>
    </div>
    """, unsafe_allow_html=True)

with ins_col2:
    # 4. Basket Valuation
    bv = ins_sections["basket_valuation"]
    st.markdown(f"""
    <div class="synthesis-card" style="border-left: 4px solid #16A34A;">
        <span class="synthesis-badge" style="background-color: #F0FDF4; color: #15803D;">{bv['title']}</span>
        <div class="synthesis-card-title">Finding: {bv['finding']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Supporting Metric:</strong> {bv['metric']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Business Implication:</strong> {bv['implication']}</div>
        <div style="font-size: 0.82rem; color: #15803D;"><strong>Recommended Action:</strong> {bv['action']}</div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Engagement Performance
    ep = ins_sections["engagement_performance"]
    st.markdown(f"""
    <div class="synthesis-card" style="border-left: 4px solid #7C3AED;">
        <span class="synthesis-badge" style="background-color: #F5F3FF; color: #6D28D9;">{ep['title']}</span>
        <div class="synthesis-card-title">Finding: {ep['finding']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Supporting Metric:</strong> {ep['metric']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Business Implication:</strong> {ep['implication']}</div>
        <div style="font-size: 0.82rem; color: #6D28D9;"><strong>Recommended Action:</strong> {ep['action']}</div>
    </div>
    """, unsafe_allow_html=True)

    # 6. Adoption Opportunities
    ao = ins_sections["adoption_opportunities"]
    st.markdown(f"""
    <div class="synthesis-card" style="border-left: 4px solid #0284C7;">
        <span class="synthesis-badge" style="background-color: #F0F9FF; color: #0369A1;">{ao['title']}</span>
        <div class="synthesis-card-title">Finding: {ao['finding']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Supporting Metric:</strong> {ao['metric']}</div>
        <div style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;"><strong>Business Implication:</strong> {ao['implication']}</div>
        <div style="font-size: 0.82rem; color: #0284C7;"><strong>Recommended Action:</strong> {ao['action']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# Section 12: Report Export & Raw Data Explorer
# -----------------------------------------------------------------------------
with st.expander("Raw Telemetry Explorer & Export Options"):
    st.caption("Inspect filtered session records, verify schema parameters, and download reports.")
    st.dataframe(filtered_df, use_container_width=True)

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Data (CSV)",
            data=csv_bytes,
            file_name=f"filtered_tryon_sessions_{date.today().isoformat()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_col2:
        st.download_button(
            label="Download Executive Summary (PDF)",
            data=pdf_bytes,
            file_name=f"virtual_tryon_executive_report_{date.today().isoformat()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
