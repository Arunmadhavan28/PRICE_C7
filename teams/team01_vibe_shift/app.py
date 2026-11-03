"""
Streamlit Web Application for Team 1: The 'Vibe-Shift' Trend Forecaster.
Combines historical sales velocity with external social media signals to project demand surges.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from forecaster import load_trend_data, forecast_demand

try:
    st.set_page_config(
        page_title="Trend Forecaster | Retail AI",
        page_icon=None,
        layout="wide"
    )
except Exception:
    # Page config can only be set once; guard when imported from master hub
    pass

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
if uploaded_file is not None:
    try:
        df = load_trend_data(uploaded_file)
        st.sidebar.success(f"Custom CSV loaded ({len(df)} rows)")
    except Exception as err:
        st.sidebar.error(f"Error parsing custom CSV: {err}")
        st.info("Falling back to default historical trend dataset.")
        df = load_trend_data(str(default_data_path))
elif default_data_path.exists():
    df = load_trend_data(str(default_data_path))
else:
    st.error("Dataset not found. Please upload a valid trend sales CSV.")
    st.stop()


categories = sorted(df["Item_Category"].unique())
selected_category = st.sidebar.selectbox("Select Apparel Category", categories)

forecast_days = st.sidebar.slider("Forecast Horizon (Days)", min_value=7, max_value=60, value=30, step=1)
social_weight = st.sidebar.slider("Cultural Signal Weight (Social Score)", min_value=0.0, max_value=1.0, value=0.35, step=0.05)
growth_acc = st.sidebar.slider("Trend Acceleration Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# Scenario Simulation Controls in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("What-If Cultural Scenario")
simulated_spike = st.sidebar.slider("Simulate Viral Signal Shift (%)", min_value=-50, max_value=50, value=0, step=5)

# Adjust DataFrame copy if scenario simulation active
sim_df = df.copy()
sim_df["Social_Media_Trend_Score"] = sim_df["Social_Media_Trend_Score"].astype(float)
if simulated_spike != 0:
    mask = sim_df["Item_Category"] == selected_category
    factor = 1.0 + (simulated_spike / 100.0)
    sim_df.loc[mask, "Social_Media_Trend_Score"] = (sim_df.loc[mask, "Social_Media_Trend_Score"] * factor).clip(0.0, 100.0)

# Execute Forecast
hist_df, forecast_df, metrics = forecast_demand(
    sim_df,
    category=selected_category,
    forecast_days=forecast_days,
    social_weight=social_weight,
    growth_acceleration=growth_acc
)

# Top KPI Summary Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Social Trend Momentum",
        value=f"{metrics['current_social_score']:.0f} / 100",
        delta=f"{metrics['social_trend_direction']} ({metrics['trend_velocity_pct']:+.1f}% 14d)"
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
        label="Demand Shift vs Baseline",
        value=f"{growth_rate:+.1f}%",
        delta=f"Hist Avg {metrics['historical_avg_daily']} units"
    )
with col4:
    st.metric(
        label="Peak Surge Date",
        value=metrics["peak_forecast_day"],
        delta=f"Safety Buffer: {metrics['safety_stock_recommendation']} units"
    )

st.markdown("---")

# Tabbed Layout
tab_forecast, tab_inventory, tab_mood, tab_diagnostics = st.tabs([
    "Tab 1: Demand Trajectory & Forecast",
    "Tab 2: Buyer Replenishment Plan",
    "Tab 3: Cultural Aesthetic & Mood Board",
    "Tab 4: Seasonality & Diagnostics"
])

# -------------------------------------------------------------
# TAB 1: Demand Trajectory with Dual-Axis Cultural Overlay
# -------------------------------------------------------------
with tab_forecast:
    st.subheader(f"Demand Projection with Cultural Wave Overlay — {selected_category}")
    if simulated_spike != 0:
        st.info(f"[Simulation Active] Simulated Scenario Active: {simulated_spike:+d}% shift applied to social media trend signals.")

    # Create Dual-Axis Plotly Chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Historical Sales Volume (Primary Y)
    fig.add_trace(go.Scatter(
        x=hist_df["Date"],
        y=hist_df["Historical_Sales_Volume"],
        mode="lines",
        name="Historical Daily Sales",
        line=dict(color="#4a90e2", width=2)
    ), secondary_y=False)

    # 2. Confidence Ribbon (Primary Y)
    fig.add_trace(go.Scatter(
        x=forecast_df["Date"].tolist() + forecast_df["Date"].tolist()[::-1],
        y=forecast_df["Upper_Bound"].tolist() + forecast_df["Lower_Bound"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(0, 230, 118, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=True,
        name="95% Confidence Band"
    ), secondary_y=False)

    # 3. Forecast Projected Demand (Primary Y)
    fig.add_trace(go.Scatter(
        x=forecast_df["Date"],
        y=forecast_df["Forecast_Demand"],
        mode="lines+markers",
        name=f"{forecast_days}-Day AI Forecast",
        line=dict(color="#00e676", width=3, dash="solid"),
        marker=dict(size=4)
    ), secondary_y=False)

    # 4. Social Media Trend Score (Secondary Y - Cultural Wave Overlay)
    fig.add_trace(go.Scatter(
        x=hist_df["Date"],
        y=hist_df["Social_Media_Trend_Score"],
        mode="lines",
        name="Cultural Signal Score (0-100)",
        line=dict(color="#d946ef", width=1.5, dash="dot"),
        opacity=0.75
    ), secondary_y=True)

    fig.update_layout(
        title=f"Dual-Axis Trajectory: Sales Demand & Cultural Momentum for {selected_category}",
        xaxis_title="Timeline",
        template="plotly_dark",
        hovermode="x unified",
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="Units Sold / Forecasted", secondary_y=False)
    fig.update_yaxes(title_text="Social Trend Score (0-100)", secondary_y=True, range=[0, 110])

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: Boutique Buyer Replenishment Plan
# -------------------------------------------------------------
with tab_inventory:
    st.subheader("Boutique Buyer Inventory Replenishment Plan")
    st.caption("Actionable procurement recommendations calculated from projected velocity, lead times, and confidence spreads.")

    bcol1, bcol2, bcol3, bcol4 = st.columns(4)
    with bcol1:
        st.metric("Recommended Safety Stock Buffer", f"{metrics['safety_stock_recommendation']} units", "Lead Time: 7 Days")
    with bcol2:
        st.metric("Suggested Reorder Point (ROP)", f"{metrics['reorder_point_recommendation']} units", "Replenish Threshold")
    with bcol3:
        st.metric("Forecast Volatility Risk", metrics["forecast_volatility_risk"], "Based on Sales Variance")
    with bcol4:
        st.metric("Total Procurement Need", f"{metrics['total_forecasted_units']} units", f"Across {forecast_days} Days")

    st.markdown("#### Recommended Buyer Actions")
    st.markdown(f"""
    - **Procurement Timing**: Place replenishment orders by **{metrics['peak_forecast_day']} minus 7 days** to avoid stockouts during the anticipated demand surge.
    - **Inventory Allocation**: Maintain at least **{metrics['safety_stock_recommendation']} units** of buffer stock for *{selected_category}* to absorb unexpected viral micro-spikes.
    - **Trend Volatility Assessment**: Risk level is classified as **{metrics['forecast_volatility_risk']}**. {'Increase purchase buffer by +10% to prevent missed sales.' if metrics['forecast_volatility_risk'] == 'High' else 'Standard replenishment schedule recommended.'}
    """)

    st.markdown("#### Forecast Data Table")
    st.dataframe(forecast_df, use_container_width=True)

    csv_data = forecast_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Forecast & Purchase Order (CSV)",
        data=csv_data,
        file_name=f"forecast_{selected_category.lower().replace(' ', '_')}_{forecast_days}d.csv",
        mime="text/csv"
    )

# -------------------------------------------------------------
# TAB 3: Cultural Aesthetic & Mood Board Gallery
# -------------------------------------------------------------
with tab_mood:
    st.subheader("Trend Aesthetic Signals & Visual Mood Board")
    st.caption("Curated visual aesthetics representing the cultural movement driving demand in this category.")

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
        ],
        "Minimalist Linen Shirts": [
            {"title": "Neutral Coastal Fit", "desc": "Breathable unbleached flax weave with relaxed lapels", "color": "#4a5568", "hex": "#718096", "tag": "Stable Evergreen"},
            {"title": "Earthy Olive Drape", "desc": "Mediterranean washed earth tones for effortless layering", "color": "#2f855a", "hex": "#38A169", "tag": "Warm Season Lift"},
            {"title": "Raw Hem Tunic", "desc": "Understated quiet luxury capsule staple", "color": "#744210", "hex": "#D69E2E", "tag": "Steady Repeat Orders"}
        ],
        "Cyberpunk Metallic Vests": [
            {"title": "Neon Chrome Techwear", "desc": "Reflective iridescent fabrics with modular zip pouches", "color": "#44337a", "hex": "#805AD5", "tag": "Viral Micro-Surge"},
            {"title": "Matte Armor Harness", "desc": "Industrial nylon webbed strapping with gunmetal hardware", "color": "#1a202c", "hex": "#4A5568", "tag": "Festival Peak"},
            {"title": "Holographic Foil Shell", "desc": "Ultraviolet reactive weather-resistant shell", "color": "#171923", "hex": "#D53F8C", "tag": "Short Spike Horizon"}
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
            # Generate SVG visual badge and render with st.image
            clean_title = mood['title'].replace("&", "and")
            clean_tag = mood['tag'].replace("&", "and")
            svg_data = f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110"><rect width="300" height="110" rx="10" fill="{mood["color"]}"/><circle cx="45" cy="55" r="24" fill="{mood["hex"]}" stroke="#ffffff" stroke-width="2"/><text x="85" y="48" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="14">{clean_title}</text><text x="85" y="72" fill="#cbd5e0" font-family="sans-serif" font-size="11">{clean_tag}</text></svg>'
            st.image(svg_data, caption=f"Aesthetic Signal: {mood['title']}", use_container_width=True)
            st.markdown(f"""
            <div style="background-color: {mood['color']}; border: 1px solid #444; border-radius: 8px; padding: 12px; margin-top: -10px; color: white;">
                <p style="font-size: 0.85em; color: #cbd5e0; margin: 0 0 8px 0;">{mood['desc']}</p>
                <span style="background: rgba(255,255,255,0.15); padding: 3px 8px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">{mood['tag']}</span>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 4: Seasonality & Diagnostics
# -------------------------------------------------------------
with tab_diagnostics:
    st.subheader(f"Historical Demand Diagnostics & Seasonality — {selected_category}")

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    cat_df = hist_df.copy()
    cat_df["DayOfWeek"] = cat_df["Date"].dt.dayofweek
    dow_stats = cat_df.groupby("DayOfWeek")["Historical_Sales_Volume"].agg(["mean", "std", "count"]).reset_index()
    dow_stats["DayName"] = dow_stats["DayOfWeek"].apply(lambda d: day_names[d])

    fig_dow = go.Figure()
    fig_dow.add_trace(go.Bar(
        x=dow_stats["DayName"],
        y=dow_stats["mean"],
        error_y=dict(type="data", array=dow_stats["std"].fillna(0)),
        marker_color="#3b82f6",
        name="Avg Daily Units"
    ))
    fig_dow.update_layout(
        title=f"Weekly Day-of-Week Seasonality Lift for {selected_category}",
        xaxis_title="Day of Week",
        yaxis_title="Average Units Sold",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig_dow, use_container_width=True)

    with st.expander("View Full Historical Dataset Summary"):
        st.dataframe(cat_df.describe(), use_container_width=True)

