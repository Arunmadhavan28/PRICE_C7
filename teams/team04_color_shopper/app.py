"""
Streamlit Web Application for Team 4: Color-Palette Personal Shopper.
Extracts dominant colors from uploaded photos and discovers matched catalog products.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from PIL import Image

# Ensure local imports work both standalone and when imported by the root hub
BASE_TEAM_DIR = Path(__file__).resolve().parent
if str(BASE_TEAM_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_TEAM_DIR))

try:
    from color_engine import (
        extract_dominant_colors,
        find_closest_products,
        hex_to_rgb,
        rgb_to_hex,
        calculate_color_distance,
        validate_catalog_dataframe,
        get_color_harmony
    )
except ImportError:
    from teams.team04_color_shopper.color_engine import (
        extract_dominant_colors,
        find_closest_products,
        hex_to_rgb,
        rgb_to_hex,
        calculate_color_distance,
        validate_catalog_dataframe,
        get_color_harmony
    )

# Page configuration guarded against duplicate calls when loaded in multi-app hubs
try:
    st.set_page_config(
        page_title="Color-Palette Shopper | Retail AI",
        layout="wide"
    )
except Exception:
    pass

# Initialize session state for Mood Board
if "mood_board" not in st.session_state:
    st.session_state["mood_board"] = []

st.title("Color-Palette Personal Shopper")
st.caption("Visual Commerce Engine Matching Real-World Spaces to Catalog Products | Target: Home Decor, Furniture & Apparel Shoppers")

# ------------------------------------------------------------------------------
# 1. Load and Validate Product Catalog
# ------------------------------------------------------------------------------
catalog_path = BASE_TEAM_DIR / "data" / "catalog.csv"
catalog_loaded = False
catalog_df = pd.DataFrame()

try:
    raw_df = pd.read_csv(catalog_path)
    catalog_df = validate_catalog_dataframe(raw_df)
    catalog_loaded = True
except Exception as e:
    st.error(f"Catalog Error: Unable to load or validate product catalog at `{catalog_path}`. Details: {e}")

# ------------------------------------------------------------------------------
# 2. Sidebar Controls: Image Selection & Filtering
# ------------------------------------------------------------------------------
st.sidebar.header("1. Visual Space Input")

sample_dir = BASE_TEAM_DIR / "data" / "sample_images"
sample_files = sorted(list(sample_dir.glob("*.png"))) if sample_dir.exists() else []
sample_options = ["Upload Custom Photo"] + [f.name for f in sample_files]

selected_source = st.sidebar.selectbox("Choose Image Source", sample_options)
uploaded_file = st.sidebar.file_uploader(
    "Upload Room / Outfit Photo",
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload an image of your room, furniture, or wardrobe."
)

st.sidebar.markdown("---")
st.sidebar.header("2. Catalog Filters")

if catalog_loaded and not catalog_df.empty:
    categories = sorted(list(catalog_df["Category"].dropna().unique()))
    category_options = ["All Categories"] + categories
    selected_category = st.sidebar.selectbox("Filter by Category", category_options)

    min_catalog_price = float(catalog_df["Price"].min())
    max_catalog_price = float(catalog_df["Price"].max())
    if min_catalog_price == max_catalog_price:
        max_catalog_price += 10.0

    price_range = st.sidebar.slider(
        "Price Range ($)",
        min_value=0.0,
        max_value=max_catalog_price,
        value=(0.0, max_catalog_price),
        step=5.0
    )
else:
    selected_category = "All Categories"
    price_range = (0.0, 1000.0)

top_n = st.sidebar.slider("Number of Matches to Show", min_value=1, max_value=8, value=4)
manual_hex = st.sidebar.color_picker("Manual Shade Override", "#C85A32")

# ------------------------------------------------------------------------------
# 3. Active Image Resolution & Dominant Palette Extraction
# ------------------------------------------------------------------------------
active_image = None
image_error = None

if uploaded_file is not None:
    try:
        active_image = Image.open(uploaded_file)
    except Exception as e:
        image_error = f"Uploaded file could not be read as a valid image: {e}"
elif selected_source != "Upload Custom Photo" and sample_dir.exists():
    try:
        active_image = Image.open(sample_dir / selected_source)
    except Exception as e:
        image_error = f"Error opening sample image `{selected_source}`: {e}"
elif sample_files:
    try:
        active_image = Image.open(sample_files[0])
    except Exception:
        active_image = None

col_left, col_right = st.columns([1, 1.3], gap="large")

with col_left:
    st.subheader("Selected Visual Space")

    if image_error:
        st.error(image_error)

    if active_image is not None:
        st.image(active_image, caption="Active Space for Palette Extraction", use_container_width=True)
        with st.spinner("Extracting dominant color swatches..."):
            try:
                palette = extract_dominant_colors(active_image, num_colors=3)
            except Exception as e:
                st.warning(f"Color extraction fallback: {e}")
                palette = [{"hex": manual_hex, "rgb": hex_to_rgb(manual_hex), "share_pct": 100.0}]
    else:
        st.info("No photo selected. Using manual shade input.")
        palette = [{"hex": manual_hex, "rgb": hex_to_rgb(manual_hex), "share_pct": 100.0}]

    st.markdown("#### Extracted Dominant Palette")
    st.caption("Click any swatch below to select it as the target color for product discovery.")

    # Swatch Selector
    swatch_options = [f"{sw['hex']} ({sw['share_pct']}% share)" for sw in palette]
    selected_swatch_label = st.radio(
        "Choose Target Swatch to Match",
        options=swatch_options,
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    # Resolve selected target hex
    chosen_index = swatch_options.index(selected_swatch_label) if selected_swatch_label in swatch_options else 0
    target_hex = palette[chosen_index]["hex"]

    # Visual Swatch Cards Display
    pal_cols = st.columns(len(palette))
    for i, col_data in enumerate(palette):
        is_selected = (col_data["hex"] == target_hex)
        border_style = "3px solid #00e676" if is_selected else "1px solid #666"
        with pal_cols[i]:
            st.markdown(f"""
            <div style="background-color: {col_data['hex']}; width: 100%; height: 50px; border-radius: 8px; border: {border_style}; margin-bottom: 4px;"></div>
            <div style="text-align: center; font-size: 0.85em; font-family: monospace;">
                <b>{col_data['hex']}</b><br>
                <span style="color: #888;">{col_data['share_pct']}%</span>
            </div>
            """, unsafe_allow_html=True)

    # Harmony Analysis for target color
    harmony_data = get_color_harmony(target_hex)

# ------------------------------------------------------------------------------
# 4. Product Matching & Results Display
# ------------------------------------------------------------------------------
with col_right:
    # Summary Metrics Row
    metric_c1, metric_c2, metric_c3 = st.columns(3)
    metric_c1.metric("Target Shade", target_hex)
    metric_c2.metric("Tone Temperature", harmony_data["temperature"])

    # Query closest products with active filters
    cat_filter = None if selected_category == "All Categories" else selected_category
    matched_products = []

    if catalog_loaded and not catalog_df.empty:
        matched_products = find_closest_products(
            target_color=target_hex,
            catalog_df=catalog_df,
            top_n=top_n,
            category=cat_filter,
            min_price=price_range[0],
            max_price=price_range[1]
        )

    best_confidence = f"{matched_products[0]['Match_Confidence']}%" if matched_products else "N/A"
    metric_c3.metric("Top Match Confidence", best_confidence)

    # Tabbed Interface for Results, Harmony, and Mood Board
    tab_catalog, tab_harmony, tab_moodboard = st.tabs([
        "Coordinated Products",
        "Color Harmony & Styling",
        f"Mood Board ({len(st.session_state['mood_board'])})"
    ])

    with tab_catalog:
        st.subheader("Closest Matching Catalog Pieces")
        st.caption(f"Ranked via 3D Euclidean Color Distance against **{target_hex}** | Category: *{selected_category}* | Price: *${price_range[0]:.0f} - ${price_range[1]:.0f}*")

        if not catalog_loaded or catalog_df.empty:
            st.error("Catalog dataset is currently unavailable.")
        elif not matched_products:
            st.warning(
                f"No catalog products matched target shade **{target_hex}** with current filters "
                f"(Category: '{selected_category}', Price: ${price_range[0]:.0f} - ${price_range[1]:.0f}). "
                "Try widening your price range or selecting 'All Categories'."
            )
        else:
            grid_cols = st.columns(2)
            for idx, prod in enumerate(matched_products):
                with grid_cols[idx % 2]:
                    st.markdown(f"""
                    <div style="background: #18181b; border: 1px solid #333; border-radius: 10px; padding: 12px; margin-bottom: 10px;">
                        <img src="{prod['Image_URL']}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 6px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <h4 style="margin: 0 0 4px 0; font-size: 0.95em; color: #fff;">{prod['Product_Name']}</h4>
                        </div>
                        <span style="font-size: 0.75em; background: #27272a; color: #a1a1aa; padding: 2px 6px; border-radius: 4px;">{prod['Category']}</span>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0 6px 0;">
                            <span style="color: #00e676; font-weight: bold; font-size: 1.1em;">${prod['Price']:.2f}</span>
                            <span style="background: {prod['Hex_Color_Code']}; width: 20px; height: 20px; border-radius: 50%; border: 1px solid #fff; display: inline-block;"></span>
                        </div>
                        <div style="font-size: 0.8em; color: #aaa;">
                            Confidence: <b>{prod['Match_Confidence']}%</b> &bull; Dist: <code>{prod['Distance']:.1f}</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_key = f"save_{prod['Product_Name']}_{idx}"
                    already_saved = any(item["Product_Name"] == prod["Product_Name"] for item in st.session_state["mood_board"])

                    if already_saved:
                        st.button("Saved in Mood Board", key=btn_key, disabled=True)
                    else:
                        if st.button("Save to Mood Board", key=btn_key):
                            st.session_state["mood_board"].append(prod)
                            st.rerun()

    with tab_harmony:
        st.subheader("Color Harmony Guidance")
        st.info(harmony_data["styling_tip"])

        h_col1, h_col2, h_col3 = st.columns(3)
        with h_col1:
            st.markdown(f"**Complementary Accent**<br><code>{harmony_data['complementary']}</code>", unsafe_allow_html=True)
            st.markdown(f'<div style="background-color: {harmony_data["complementary"]}; height: 45px; border-radius: 6px; border: 1px solid #666;"></div>', unsafe_allow_html=True)
        with h_col2:
            st.markdown(f"**Analogous Hues**<br><code>{harmony_data['analogous'][0]}</code>, <code>{harmony_data['analogous'][1]}</code>", unsafe_allow_html=True)
            st.markdown(f'''
            <div style="display: flex; gap: 4px;">
                <div style="background-color: {harmony_data["analogous"][0]}; flex: 1; height: 45px; border-radius: 6px; border: 1px solid #666;"></div>
                <div style="background-color: {harmony_data["analogous"][1]}; flex: 1; height: 45px; border-radius: 6px; border: 1px solid #666;"></div>
            </div>
            ''', unsafe_allow_html=True)
        with h_col3:
            st.markdown(f"**Triadic Accents**<br><code>{harmony_data['triadic'][0]}</code>, <code>{harmony_data['triadic'][1]}</code>", unsafe_allow_html=True)
            st.markdown(f'''
            <div style="display: flex; gap: 4px;">
                <div style="background-color: {harmony_data["triadic"][0]}; flex: 1; height: 45px; border-radius: 6px; border: 1px solid #666;"></div>
                <div style="background-color: {harmony_data["triadic"][1]}; flex: 1; height: 45px; border-radius: 6px; border: 1px solid #666;"></div>
            </div>
            ''', unsafe_allow_html=True)

    with tab_moodboard:
        st.subheader("Your Curated Mood Board")
        if not st.session_state["mood_board"]:
            st.info("Your Mood Board is empty. Click 'Save to Mood Board' on any matching catalog item to curate your personal collection.")
        else:
            mb_cols = st.columns(3)
            for m_idx, m_item in enumerate(st.session_state["mood_board"]):
                with mb_cols[m_idx % 3]:
                    st.markdown(f"""
                    <div style="background: #1e1e24; border: 1px solid #444; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                        <img src="{m_item['Image_URL']}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 4px; margin-bottom: 6px;">
                        <b style="font-size: 0.9em; color: #fff;">{m_item['Product_Name']}</b><br>
                        <span style="color: #00e676; font-weight: bold;">${m_item['Price']:.2f}</span>
                        <span style="background: {m_item['Hex_Color_Code']}; width: 14px; height: 14px; border-radius: 50%; display: inline-block; float: right; border: 1px solid #fff;"></span>
                    </div>
                    """, unsafe_allow_html=True)
            if st.button("Clear Mood Board"):
                st.session_state["mood_board"] = []
                st.rerun()

# ------------------------------------------------------------------------------
# 5. Raw Catalog Dataset Viewer
# ------------------------------------------------------------------------------
with st.expander("View Complete Catalog Dataset"):
    if catalog_loaded and not catalog_df.empty:
        st.dataframe(catalog_df, use_container_width=True)
    else:
        st.write("No catalog data available.")
