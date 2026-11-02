"""
Streamlit Web Application for Team 8: The Virtual Try-On Feedback Loop.
Funnel visualization and conversion lift analytics for AR virtual try-on.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from funnel_engine import load_session_logs, calculate_funnel_metrics

st.set_page_config(
    page_title="AR Try-On Analytics | Retail AI",
    page_icon="👓",
    layout="wide"
)

st.title("👓 The Virtual Try-On Feedback Loop")
st.caption("Measuring the Direct Business Impact & Funnel Lift of AR Experiences | Target: E-commerce Product Managers")

# Load Session Logs
data_path = Path(__file__).parent / "data" / "session_logs.csv"
logs_df = load_session_logs(str(data_path))

# Sidebar Controls
st.sidebar.header("🎯 Cohort & Device Filters")
devices = ["All Devices"] + sorted(logs_df["Device_Type"].unique().tolist())
selected_device = st.sidebar.selectbox("Device Segment", devices)

min_ar_time = st.sidebar.slider(
    "Filter by Min Time in AR (Seconds)",
    min_value=0,
    max_value=180,
    value=0,
    step=10,
    help="Isolate deep-engagement AR sessions to measure intent."
)

filtered_df = logs_df.copy()
if selected_device != "All Devices":
    filtered_df = filtered_df[filtered_df["Device_Type"] == selected_device]

if min_ar_time > 0:
    filtered_df = filtered_df[(filtered_df["AR_TryOn_Used"] == False) | (filtered_df["Time_in_AR"] >= min_ar_time)]

# Compute Metrics
metrics = calculate_funnel_metrics(filtered_df)

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "AR Conversion Lift",
        f"{metrics['conversion_lift_pct']:+.1f}%",
        delta="AR Users vs Control"
    )
with col2:
    st.metric(
        "AR Conversion Rate",
        f"{metrics['cr_ar']}%",
        delta=f"{metrics['ar_purchases']} purchases"
    )
with col3:
    st.metric(
        "Non-AR Conversion Rate",
        f"{metrics['cr_non_ar']}%",
        delta=f"{metrics['non_ar_purchases']} purchases"
    )
with col4:
    st.metric(
        "AR Avg Order Value",
        f"${metrics['aov_ar']:.2f}",
        delta=f"vs ${metrics['aov_non_ar']:.2f} Non-AR"
    )

st.markdown("---")

# Visual Funnel Charts
col_funnel, col_bar = st.columns([1.2, 1])

with col_funnel:
    st.subheader("🔻 Comparative Conversion Funnel")
    fig_funnel = go.Figure()

    # AR Funnel
    fig_funnel.add_trace(go.Funnel(
        name="Engaged with AR Try-On",
        y=["Total Sessions", "Engaged with AR", "Completed Checkout"],
        x=[metrics["ar_sessions"], metrics["ar_sessions"], metrics["ar_purchases"]],
        textinfo="value+percent initial",
        marker=dict(color="#00e676")
    ))

    # Non-AR Funnel
    fig_funnel.add_trace(go.Funnel(
        name="Standard Browsing (No AR)",
        y=["Total Sessions", "Engaged with AR", "Completed Checkout"],
        x=[metrics["non_ar_sessions"], 0, metrics["non_ar_purchases"]],
        textinfo="value+percent initial",
        marker=dict(color="#3b82f6")
    ))

    fig_funnel.update_layout(
        template="plotly_dark",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_bar:
    st.subheader("📊 Conversion Rate & Basket Size Comparison")
    comp_df = pd.DataFrame([
        {"Cohort": "AR Users", "Metric": "Conversion Rate (%)", "Value": metrics["cr_ar"]},
        {"Cohort": "Non-AR Users", "Metric": "Conversion Rate (%)", "Value": metrics["cr_non_ar"]},
        {"Cohort": "AR Users", "Metric": "Avg Basket Size ($)", "Value": metrics["aov_ar"]},
        {"Cohort": "Non-AR Users", "Metric": "Avg Basket Size ($)", "Value": metrics["aov_non_ar"]}
    ])
    fig_comp = px.bar(
        comp_df,
        x="Metric",
        y="Value",
        color="Cohort",
        barmode="group",
        color_discrete_map={"AR Users": "#00e676", "Non-AR Users": "#3b82f6"}
    )
    fig_comp.update_layout(template="plotly_dark", height=420)
    st.plotly_chart(fig_comp, use_container_width=True)

# Data Table Expander
with st.expander("🔍 View Raw User Session Logs"):
    st.dataframe(filtered_df, use_container_width=True)
