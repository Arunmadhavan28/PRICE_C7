"""
Streamlit Chat Application for Team 2: The Sassy Stylist Bot.
Conversational fashion styling powered by Gemini API / Offline Engine.
Includes Layer 3 Interactive UI using Streamlit and Plotly visualizations.
"""

import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from stylist_engine import (
    load_catalog,
    get_sassy_stylist_response,
    calculate_outfit_budget_breakdown,
    FALLBACK_API_KEY
)

st.set_page_config(
    page_title="The Sassy Stylist Bot | Retail AI",
    page_icon="👗",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .chat-badge {
        background-color: #ec4899;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75em;
        font-weight: bold;
    }
    .product-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Load catalog data
catalog_path = Path(__file__).parent / "data" / "catalog_50.json"
catalog = load_catalog(str(catalog_path))
df_catalog = pd.DataFrame(catalog)

# Sidebar Configuration
st.sidebar.title("✨ Sassy Stylist Studio")
st.sidebar.caption("Team 2: Grounded Conversational Fashion Engine")

# Catalog Key Metrics in Sidebar
st.sidebar.markdown("### Catalog Snapshot")
col_s1, col_s2 = st.sidebar.columns(2)
col_s1.metric("Active Pieces", f"{len(catalog)}")
col_s2.metric("Avg Price", f"${df_catalog['Price'].mean():.1f}")

api_key_input = st.sidebar.text_input(
    "Google Gemini API Key",
    value=os.getenv("GEMINI_API_KEY", ""),
    type="password",
    help="Free tier Gemini API key from Google AI Studio. Built-in offline fallback is active automatically."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌟 Quick Occasion Prompts")
quick_prompts = [
    "What to wear to a beach wedding in Amalfi?",
    "Evening formal cocktail party in Manhattan",
    "Casual chic Friday at a creative studio",
    "First date at a moody candlelit bistro"
]

for qp in quick_prompts:
    if st.sidebar.button(qp, use_container_width=True):
        st.session_state["pending_prompt"] = qp

# Main Header
st.title("👗 The Sassy Stylist Bot")
st.caption("AI-powered styling with unapologetic attitude — 100% grounded in our boutique catalog without hallucination.")

# Navigation Tabs
tab_chat, tab_analytics, tab_guide = st.tabs(["💬 Stylist Chat", "📊 Catalog & Style Analytics", "ℹ️ Grounding Guide"])

with tab_guide:
    st.info("💡 **Grounded Styling Guarantee**: Every single piece recommended is verified against our local 50-item catalog. No phantom items, no broken links, zero hallucinations.")
    with st.expander("Explore Team 2 Architecture & Methodology"):
        st.markdown("""
        - **Layer 1: Data & Math Core Engine**: Implements normalized Jaccard-based vibe similarity and outfit financial aggregation.
        - **Layer 2: Automated Pytest Verification**: 100% test suite pass rate verifying grounding, schemas, and arithmetic correctness.
        - **Layer 3: Interactive UI**: Built with Streamlit chat widgets and Plotly analytics dashboards.
        """)

with tab_analytics:
    st.subheader("Boutique Catalog Analytics")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Items", f"{len(df_catalog)}")
    col_m2.metric("Categories", f"{df_catalog['Category'].nunique()}")
    col_m3.metric("Min Price", f"${df_catalog['Price'].min():.2f}")
    col_m4.metric("Max Price", f"${df_catalog['Price'].max():.2f}")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cat_counts = df_catalog["Category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Item Count"]
        fig_donut = px.pie(
            cat_counts,
            names="Category",
            values="Item Count",
            title="Catalog Category Distribution",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_c2:
        fig_bar = px.bar(
            df_catalog.groupby("Category")["Price"].mean().reset_index(),
            x="Category",
            y="Price",
            title="Average Price by Fashion Category ($)",
            color="Price",
            color_continuous_scale="Viridis",
            labels={"Price": "Avg Price ($)"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with tab_chat:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Darling, welcome to my studio! Tell me where you are going or what aesthetic you want, and let me rescue you from a fashion disaster with our verified catalog.",
                "recommendations": []
            }
        ]

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            recs = msg.get("recommendations", [])
            if recs:
                st.markdown("#### Curated Outfit Selection:")
                cols = st.columns(len(recs))
                for i, item in enumerate(recs):
                    with cols[i]:
                        img_url = item.get("Image_URL", "https://via.placeholder.com/300")
                        st.image(img_url, use_container_width=True)
                        st.markdown(f"**{item['Product_Name']}**")
                        st.markdown(f"`${item['Price']:.2f}` | *{item['Category']}*")
                        tags_str = " ".join([f"`#{t}`" for t in item.get("Vibe_Tags", [])[:2]])
                        st.markdown(tags_str)
                        st.button(f"Add to Bag", key=f"btn_{msg['content'][:8]}_{i}")

                # Plotly outfit price comparison
                outfit_metrics = calculate_outfit_budget_breakdown(recs)
                rec_df = pd.DataFrame(recs)
                fig_outfit = px.bar(
                    rec_df,
                    x="Product_Name",
                    y="Price",
                    color="Category",
                    title=f"Curated Outfit Financial Summary (Total: ${outfit_metrics['total_cost']:.2f})",
                    labels={"Price": "Price ($)", "Product_Name": "Item"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_outfit.update_layout(xaxis_tickangle=-25, margin=dict(b=80))
                st.plotly_chart(fig_outfit, use_container_width=True)

    # Chat Input Handling
    prompt = st.chat_input("Ask Vivian for outfit advice (e.g., 'What should I wear to a rooftop summer party?')...")

    if "pending_prompt" in st.session_state and st.session_state["pending_prompt"]:
        prompt = st.session_state["pending_prompt"]
        st.session_state["pending_prompt"] = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "recommendations": []})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Vivian is inspecting the catalog and judging your aesthetic..."):
                response_text, rec_items = get_sassy_stylist_response(
                    user_query=prompt,
                    chat_history=st.session_state.messages,
                    catalog=catalog,
                    api_key=api_key_input
                )
                st.markdown(response_text)

                if rec_items:
                    st.markdown("#### Curated Outfit Selection:")
                    cols = st.columns(len(rec_items))
                    for i, item in enumerate(rec_items):
                        with cols[i]:
                            st.image(item["Image_URL"], use_container_width=True)
                            st.markdown(f"**{item['Product_Name']}**")
                            st.markdown(f"`${item['Price']:.2f}` | *{item['Category']}*")
                            tags_str = " ".join([f"`#{t}`" for t in item.get("Vibe_Tags", [])[:2]])
                            st.markdown(tags_str)

                    # Plotly chart for current recommendation
                    outfit_metrics = calculate_outfit_budget_breakdown(rec_items)
                    rec_df = pd.DataFrame(rec_items)
                    fig_outfit = px.bar(
                        rec_df,
                        x="Product_Name",
                        y="Price",
                        color="Category",
                        title=f"Curated Outfit Financial Summary (Total: ${outfit_metrics['total_cost']:.2f})",
                        labels={"Price": "Price ($)", "Product_Name": "Item"},
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_outfit.update_layout(xaxis_tickangle=-25, margin=dict(b=80))
                    st.plotly_chart(fig_outfit, use_container_width=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "recommendations": rec_items
        })
