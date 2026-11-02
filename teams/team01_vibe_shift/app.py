"""
Streamlit Web Application for Team 1: The 'Vibe-Shift' Trend Forecaster.
Combines historical sales velocity with external social media signals to project demand surges.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from forecaster import load_trend_data, forecast_demand

st.set_page_config(
    page_title="Trend Forecaster | Retail AI",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e24;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
    .badge-rising { color: #00ff88; font-weight: bold; }
    .badge-falling { color: #ff4d4d; font-weight: bold; }
    .mood-card {
        background: #111;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #444;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("The Trend Forecaster")
st.caption("Demand Surge Prediction Blending Sales Velocity and Cultural Signals | Target: Boutique Retail Buyers and Planners")

# Sidebar Controls
st.sidebar.header("Forecasting Parameters")

default_data_path = Path(__file__).parent / "data" / "trend_sales_data.csv"

uploaded_file = st.sidebar.file_uploader("Upload Custom CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"])
elif default_data_path.exists():
    df = load_trend_data(str(default_data_path))
else:
    st.error("Dataset not found. Please upload a CSV or generate data.")
    st.stop()

categories = sorted(df["Item_Category"].unique())
selected_category = st.sidebar.selectbox("Select Apparel Category", categories)

forecast_days = st.sidebar.slider("Forecast Horizon (Days)", min_value=7, max_value=60, value=30, step=1)
social_weight = st.sidebar.slider("Cultural Signal Weight (Social Score)", min_value=0.0, max_value=1.0, value=0.35, step=0.05)
growth_acc = st.sidebar.slider("Trend Acceleration Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# Execute Forecast
hist_df, forecast_df, metrics = forecast_demand(
    df,
    category=selected_category,
    forecast_days=forecast_days,
    social_weight=social_weight,
    growth_acceleration=growth_acc
)

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Social Media Trend Score",
        value=f"{metrics['current_social_score']:.0f} / 100",
        delta=metrics["social_trend_direction"]
    )
with col2:
    st.metric(
        label=f"{forecast_days}-Day Projected Demand",
        value=f"{metrics['total_forecasted_units']:,} units",
        delta=f"Avg {metrics['avg_daily_projected']} units/day"
    )
with col3:
    growth_rate = ((metrics['avg_daily_projected'] - metrics['historical_avg_daily']) / max(1.0, metrics['historical_avg_daily'])) * 100
    st.metric(
        label="Projected Demand Shift",
        value=f"{growth_rate:+.1f}%",
        delta="vs Historical Baseline"
    )
with col4:
    st.metric(
        label="Predicted Peak Surge Date",
        value=metrics["peak_forecast_day"],
        delta="Order Safety Stock by Day -7"
    )

st.markdown("---")

# Interactive Demand & Cultural Signal Chart
st.subheader("Demand Projection with Cultural Wave Overlay")

fig = go.Figure()

# Historical Sales
fig.add_trace(go.Scatter(
    x=hist_df["Date"],
    y=hist_df["Historical_Sales_Volume"],
    mode="lines",
    name="Historical Daily Sales",
    line=dict(color="#4a90e2", width=2)
))

# Forecast Upper & Lower Bounds (Confidence Ribbon)
fig.add_trace(go.Scatter(
    x=forecast_df["Date"].tolist() + forecast_df["Date"].tolist()[::-1],
    y=forecast_df["Upper_Bound"].tolist() + forecast_df["Lower_Bound"].tolist()[::-1],
    fill="toself",
    fillcolor="rgba(0, 230, 118, 0.15)",
    line=dict(color="rgba(255,255,255,0)"),
    hoverinfo="skip",
    showlegend=True,
    name="95% Confidence Band"
))

# Forecast Projected Demand
fig.add_trace(go.Scatter(
    x=forecast_df["Date"],
    y=forecast_df["Forecast_Demand"],
    mode="lines+markers",
    name=f"{forecast_days}-Day AI Forecast",
    line=dict(color="#00e676", width=3, dash="solid"),
    marker=dict(size=4)
))

fig.update_layout(
    title=f"Demand Trajectory for {selected_category}",
    xaxis_title="Date",
    yaxis_title="Units Sold / Forecasted",
    template="plotly_dark",
    hovermode="x unified",
    height=480,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Mood Board Image Gallery
st.markdown("---")
st.subheader("Trend Aesthetic and Visual Mood Board")
st.caption("Curated visual aesthetics and mood board signals representing the cultural shift for this trend.")

mood_boards = {
    "Streetwear Cargo Pants": [
        {"title": "Gorpcore Utilitarian", "desc": "Technical straps & tactical pocket silhouettes", "color": "#2d3748", "hex": "#4A5568", "tag": "Viral TikTok Surge"},
        {"title": "Baggy Street Fit", "desc": "Earth-toned oversized cuts with skate sneakers", "color": "#744210", "hex": "#B7791F", "tag": "High Velocity"},
        {"title": "Washed Camo", "desc": "Vintage washed textures & heavyweight canvas", "color": "#1a202c", "hex": "#2D3748", "tag": "Restock Recommended"}
    ],
    "Y2K Denim Jackets": [
        {"title": "Distressed Raw Hem", "desc": "Early 2000s cyberpop washed trucker fit", "color": "#2b6cb0", "hex": "#3182CE", "tag": "Rising Fast"},
        {"title": "Bedazzled & Patchwork", "desc": "Maximalist rhinestones with cropped waistlines", "color": "#44337a", "hex": "#6B46C1", "tag": "Microtrend"},
        {"title": "Vintage Acid Wash", "desc": "Chunky oversized layering jacket", "color": "#2c5282", "hex": "#4299E1", "tag": "Order +20%"}
    ],
    "Cottagecore Maxi Dresses": [
        {"title": "Puff Sleeve Floral", "desc": "Soft pastel meadow aesthetic in breathable cotton", "color": "#702459", "hex": "#B83280", "tag": "Seasonal Decay"},
        {"title": "Tiered Ruffle Linen", "desc": "Prairie silhouette with romantic tie details", "color": "#744210", "hex": "#D69E2E", "tag": "Markdown Target"},
        {"title": "Lace-Trimmed Apron", "desc": "Hand-stitched vintage revival piece", "color": "#285e61", "hex": "#319795", "tag": "Clear Inventory"}
    ]
}

category_moods = mood_boards.get(selected_category, [
    {"title": "Core Trend Wave", "desc": "High engagement cultural aesthetic", "color": "#2d3748", "hex": "#4A5568", "tag": "Trending"},
    {"title": "Social Micro-Surge", "desc": "Influencer lookbook discovery", "color": "#44337a", "hex": "#6B46C1", "tag": "Growing"},
    {"title": "Retail Capsule", "desc": "Recommended merchandise mix", "color": "#1a202c", "hex": "#2D3748", "tag": "Curated"}
])

mcols = st.columns(len(category_moods))
for i, mood in enumerate(category_moods):
    with mcols[i]:
        st.markdown(f"""
        <div style="background-color: {mood['color']}; border: 1px solid #555; border-radius: 12px; padding: 20px; text-align: center; color: white; min-height: 180px;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background-color: {mood['hex']}; margin: 0 auto 10px auto; border: 2px solid #fff;"></div>
            <h4 style="margin: 0 0 5px 0;">{mood['title']}</h4>
            <p style="font-size: 0.85em; color: #cbd5e0; margin-bottom: 10px;">{mood['desc']}</p>
            <span style="background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: bold;">{mood['tag']}</span>
        </div>
        """, unsafe_allow_html=True)

# Data Table Expander
with st.expander("View Forecast Data Table"):
    st.dataframe(forecast_df, use_container_width=True)
