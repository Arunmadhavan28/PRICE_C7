"""
Streamlit Web Application for Team 5: The Empathy Engine.
Visualizes emotional breakdowns and customer friction points from written feedback.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from empathy_engine import (
    load_reviews,
    compute_emotion_distribution,
    analyze_bulk_reviews
)

st.set_page_config(
    page_title="Empathy Engine | Retail AI",
    layout="wide"
)

st.title("The Empathy Engine: Retail Emotion Analytics")
st.caption("Quantifying Qualitative Customer Reviews into Distinct Emotional Dimensions | Target: CX and Retail Ops Directors")

# Load Default Reviews
reviews_path = Path(__file__).parent / "data" / "customer_reviews.txt"
default_reviews = load_reviews(str(reviews_path)) if reviews_path.exists() else []

# Sidebar Controls
st.sidebar.header("Customer Feedback Input")

st.sidebar.markdown(f"**Loaded Samples**: `{len(default_reviews)} customer reviews`")

custom_text = st.sidebar.text_area(
    "Paste Custom Reviews (One per line)",
    value="\n".join(default_reviews[:10]),
    height=250
)

use_all_samples = st.sidebar.checkbox("Analyze Full 30-Review Dataset", value=True)

if use_all_samples and default_reviews:
    reviews_to_analyze = default_reviews
else:
    reviews_to_analyze = [line.strip() for line in custom_text.split("\n") if line.strip()]

if not reviews_to_analyze:
    st.warning("Please provide customer reviews to analyze.")
    st.stop()

# Run Emotion Breakdown
dist_df, metrics = compute_emotion_distribution(reviews_to_analyze)
detailed_df = analyze_bulk_reviews(reviews_to_analyze)

# Metric Cards Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Reviews Analyzed", f"{metrics['total_reviews']}")
with col2:
    st.metric("Customer Joy and Satisfaction", f"{metrics['satisfaction_rate']}%", delta="Positive Sentiment")
with col3:
    st.metric("Friction Index", f"{metrics['friction_index']}%", delta="Frustration + Confusion", delta_color="inverse")
with col4:
    st.metric("Average Polarity", f"{metrics['avg_polarity']:+.2f}", delta=f"Dominant Pain: {metrics['top_friction_emotion']}")

st.markdown("---")

# Visual Charts Row
chart_col1, chart_col2 = st.columns(2)

color_map = {
    "Joy": "#00e676",
    "Satisfaction": "#3b82f6",
    "Neutral": "#94a3b8",
    "Confusion": "#f59e0b",
    "Frustration": "#ef4444"
}

with chart_col1:
    st.subheader("Emotional Share Distribution")
    fig_pie = px.pie(
        dist_df,
        values="Count",
        names="Emotion",
        color="Emotion",
        color_discrete_map=color_map,
        hole=0.45
    )
    fig_pie.update_layout(template="plotly_dark", height=380, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    st.subheader("Emotional Volume Breakdown")
    fig_bar = px.bar(
        dist_df,
        x="Emotion",
        y="Count",
        color="Emotion",
        color_discrete_map=color_map,
        text="Percentage"
    )
    fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_bar.update_layout(template="plotly_dark", height=380, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Drill-Down Review Inspector
st.subheader("Emotion Drill-Down Inspector")
selected_filter = st.selectbox(
    "Filter by Emotion Category",
    ["All Reviews", "Frustration", "Confusion", "Joy", "Satisfaction", "Neutral"]
)

if selected_filter == "All Reviews":
    filtered_df = detailed_df
else:
    filtered_df = detailed_df[detailed_df["emotion"] == selected_filter]

st.markdown(f"Displaying **{len(filtered_df)}** reviews:")

for _, row in filtered_df.iterrows():
    badge_color = color_map.get(row["emotion"], "#888")
    keywords_str = ", ".join(row["matched_keywords"]) if row["matched_keywords"] else "None"
    st.markdown(f"""
    <div style="background: #18181b; border-left: 5px solid {badge_color}; border-radius: 6px; padding: 12px; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <b style="color: {badge_color};">{row['emotion']}</b>
            <span style="color: #888; font-size: 0.8em;">Polarity: {row['polarity']:+.2f}</span>
        </div>
        <div style="font-size: 0.95em; color: #eee; margin-bottom: 6px;">"{row['review_text']}"</div>
        <div style="font-size: 0.75em; color: #aaa;">Trigger Keywords: <code>{keywords_str}</code></div>
    </div>
    """, unsafe_allow_html=True)
