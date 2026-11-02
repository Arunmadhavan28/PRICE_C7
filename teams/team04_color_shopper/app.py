"""
Streamlit Web Application for Team 4: Color-Palette Personal Shopper.
Extracts dominant colors from uploaded photos and discovers matched catalog products.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
from PIL import Image
from color_engine import (
    extract_dominant_colors,
    find_closest_products,
    hex_to_rgb
)

st.set_page_config(
    page_title="Color-Palette Shopper | Retail AI",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Color-Palette Personal Shopper")
st.caption("Visual Commerce Engine Matching Real-World Spaces & Wardrobes to Catalog Products | Target: Home Decor & Apparel Shoppers")

# Load Catalog
catalog_path = Path(__file__).parent / "data" / "catalog.csv"
catalog_df = pd.read_csv(catalog_path)

# Sidebar Controls
st.sidebar.header("📸 Image & Palette Inputs")

sample_dir = Path(__file__).parent / "data" / "sample_images"
sample_files = list(sample_dir.glob("*.png")) if sample_dir.exists() else []
sample_names = ["Upload Custom Photo"] + [f.name for f in sample_files]

selected_source = st.sidebar.selectbox("Choose Image Source", sample_names)
uploaded_file = st.sidebar.file_uploader("Or Upload Room / Outfit Photo", type=["jpg", "jpeg", "png"])

manual_hex = st.sidebar.color_picker("Or Pick Exact Hex Shade", "#C85A32")
top_n = st.sidebar.slider("Number of Matches to Show", min_value=2, max_value=8, value=4)

# Determine active image
active_image = None
if uploaded_file is not None:
    active_image = Image.open(uploaded_file)
elif selected_source != "Upload Custom Photo" and sample_dir.exists():
    active_image = Image.open(sample_dir / selected_source)
elif sample_files:
    active_image = Image.open(sample_files[0])

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("🖼️ Selected Visual Space")
    if active_image:
        st.image(active_image, caption="Active Image for Color Extraction", use_container_width=True)
        with st.spinner("Extracting dominant color swatches..."):
            palette = extract_dominant_colors(active_image, num_colors=3)
    else:
        st.info("No image selected. Using manual color picker.")
        palette = [{"hex": manual_hex, "rgb": hex_to_rgb(manual_hex), "share_pct": 100.0}]

    st.markdown("#### 🎨 Extracted Dominant Palette")
    pal_cols = st.columns(len(palette))
    selected_swatch = palette[0]["hex"]

    for i, col_data in enumerate(palette):
        with pal_cols[i]:
            st.markdown(f"""
            <div style="background-color: {col_data['hex']}; width: 100%; height: 60px; border-radius: 8px; border: 2px solid #555; margin-bottom: 5px;"></div>
            <div style="text-align: center; font-size: 0.85em;">
                <b>{col_data['hex']}</b><br>
                <span style="color: #888;">{col_data['share_pct']}% share</span>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("🛍️ Closest Matching Catalog Pieces")
    st.caption(f"Ranked via 3D Euclidean Color Distance against **{palette[0]['hex']}**")

    matched_products = find_closest_products(palette[0]["hex"], catalog_df, top_n=top_n)

    grid_cols = st.columns(2)
    for idx, prod in enumerate(matched_products):
        with grid_cols[idx % 2]:
            st.markdown(f"""
            <div style="background: #18181b; border: 1px solid #333; border-radius: 10px; padding: 12px; margin-bottom: 15px;">
                <img src="{prod['Image_URL']}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 6px; margin-bottom: 8px;">
                <h4 style="margin: 0 0 4px 0; font-size: 1.0em;">{prod['Product_Name']}</h4>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="color: #00e676; font-weight: bold; font-size: 1.1em;">${prod['Price']:.2f}</span>
                    <span style="background: {prod['Hex_Color_Code']}; width: 22px; height: 22px; border-radius: 50%; border: 1px solid #fff; display: inline-block;"></span>
                </div>
                <div style="font-size: 0.8em; color: #aaa;">Match Score: <b>{prod['Match_Confidence']}%</b> (Dist: {prod['Distance']:.1f})</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Add to Mood Board 🛒", key=f"match_{idx}")

with st.expander("🔍 View Complete Catalog Dataset"):
    st.dataframe(catalog_df, use_container_width=True)
