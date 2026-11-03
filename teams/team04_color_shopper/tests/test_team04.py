"""
Unit tests for Team 4: Color-Palette Personal Shopper.
"""

import sys
from pathlib import Path
from io import BytesIO
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
import numpy as np
from PIL import Image
from color_engine import (
    hex_to_rgb,
    rgb_to_hex,
    calculate_color_distance,
    extract_dominant_colors,
    find_closest_products,
    validate_catalog_dataframe,
    get_color_harmony
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "catalog.csv"


@pytest.fixture
def catalog_df():
    return pd.read_csv(DATA_PATH)


def test_hex_rgb_conversions():
    """Validates bidirectional conversion between hex and RGB."""
    rgb = hex_to_rgb("#C85A32")
    assert rgb == (200, 90, 50)
    assert rgb_to_hex(200, 90, 50) == "#C85A32"

    with pytest.raises(ValueError):
        hex_to_rgb("invalid_hex")


def test_euclidean_color_distance():
    """Verifies 3D Euclidean distance in RGB color space."""
    black = (0, 0, 0)
    white = (255, 255, 255)
    identical = calculate_color_distance(black, black)
    assert identical == 0.0

    max_dist = calculate_color_distance(black, white)
    assert 441.0 < max_dist < 442.0  # sqrt(3 * 255^2) ≈ 441.67


def test_dominant_color_extractor():
    """Extracts palette from a synthesized test image."""
    img = Image.new("RGB", (100, 100), color=(200, 90, 50))
    palette = extract_dominant_colors(img, num_colors=2)
    assert len(palette) > 0
    assert "hex" in palette[0]
    assert palette[0]["hex"] == "#C85A32"


def test_catalog_schema_and_closest_match(catalog_df):
    """Verifies catalog schema and closest match ranking."""
    required = ["Product_Name", "Hex_Color_Code", "Image_URL"]
    for col in required:
        assert col in catalog_df.columns
    assert len(catalog_df) >= 10

    # Search for terracotta chair's exact color
    matches = find_closest_products("#C85A32", catalog_df, top_n=3)
    assert len(matches) == 3
    # Top match should be the exact chair with distance 0.0
    assert matches[0]["Distance"] == 0.0
    assert matches[0]["Match_Confidence"] == 100.0
    assert matches[0]["Product_Name"] == "Terracotta Velvet Accent Chair"


# ==============================================================================
# Additional Comprehensive Validation Tests (Team 4 Robustness)
# ==============================================================================

def test_hex_conversions_extended():
    """Validates 3-digit shorthand, whitespace trimming, and malformed inputs."""
    # 3-digit shorthand
    assert hex_to_rgb("#FFF") == (255, 255, 255)
    assert hex_to_rgb("FFF") == (255, 255, 255)
    assert hex_to_rgb("#000") == (0, 0, 0)
    assert hex_to_rgb("F50") == (255, 85, 0)

    # Whitespace and case-insensitivity
    assert hex_to_rgb("  #c85a32  ") == (200, 90, 50)
    assert hex_to_rgb("c85a32") == (200, 90, 50)

    # Malformed inputs must raise ValueError
    with pytest.raises(ValueError):
        hex_to_rgb("#GGGGGG")
    with pytest.raises(ValueError):
        hex_to_rgb("#12345")  # 5 digits
    with pytest.raises(ValueError):
        hex_to_rgb("#1234567")  # 7 digits
    with pytest.raises(ValueError):
        hex_to_rgb("")
    with pytest.raises(ValueError):
        hex_to_rgb(None)  # non-string


def test_rgb_to_hex_validation():
    """Validates RGB channel bounds and type checking."""
    assert rgb_to_hex(0, 0, 0) == "#000000"
    assert rgb_to_hex(255, 255, 255) == "#FFFFFF"

    # Out of bounds
    with pytest.raises(ValueError):
        rgb_to_hex(-1, 50, 50)
    with pytest.raises(ValueError):
        rgb_to_hex(256, 50, 50)
    with pytest.raises(ValueError):
        rgb_to_hex(50, 300, 50)
    with pytest.raises(ValueError):
        rgb_to_hex("red", 50, 50)


def test_calculate_color_distance_extended():
    """Verifies known distances, commutativity, and input bounds."""
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    # sqrt(255^2 + 255^2) ≈ 360.62
    dist_rg = calculate_color_distance(red, green)
    assert abs(dist_rg - 360.62) < 0.1

    # Commutative property
    assert calculate_color_distance(red, blue) == calculate_color_distance(blue, red)

    # Invalid input shapes
    with pytest.raises(ValueError):
        calculate_color_distance((255, 0), (0, 0, 0))
    with pytest.raises(ValueError):
        calculate_color_distance((255, 0, 0), (300, 0, 0))


def test_catalog_validation_and_imputation():
    """Validates schema checking, auto-imputation of missing RGB, and bad row handling."""
    # Empty DataFrame
    with pytest.raises(ValueError):
        validate_catalog_dataframe(pd.DataFrame())

    # Missing required column
    incomplete_df = pd.DataFrame({
        "Product_Name": ["Test Chair"],
        "Hex_Color_Code": ["#C85A32"]
        # Image_URL missing
    })
    with pytest.raises(ValueError):
        validate_catalog_dataframe(incomplete_df)

    # Impute missing RGB_R/G/B columns from Hex_Color_Code
    catalog_no_rgb = pd.DataFrame({
        "Product_Name": ["Navy Pillow"],
        "Category": ["Decor"],
        "Hex_Color_Code": ["#1E293B"],
        "Price": [45.0],
        "Image_URL": ["https://example.com/pillow.jpg"]
    })
    validated = validate_catalog_dataframe(catalog_no_rgb)
    assert "RGB_R" in validated.columns
    assert validated.iloc[0]["RGB_R"] == 30
    assert validated.iloc[0]["RGB_G"] == 41
    assert validated.iloc[0]["RGB_B"] == 59


def test_find_closest_products_filtering(catalog_df):
    """Tests category, min/max price filtering and empty result handling."""
    # Category filter
    rugs = find_closest_products("#DDAA33", catalog_df, top_n=5, category="Rugs")
    assert len(rugs) > 0
    for item in rugs:
        assert item["Category"] == "Rugs"

    # Price range filter ($40 to $100)
    mid_price = find_closest_products("#8FA382", catalog_df, top_n=10, min_price=40.0, max_price=100.0)
    assert len(mid_price) > 0
    for item in mid_price:
        assert 40.0 <= item["Price"] <= 100.0

    # Filter with no matching items returns empty list
    no_matches = find_closest_products("#C85A32", catalog_df, category="NonExistentCategory")
    assert no_matches == []

    # top_n <= 0 returns empty list
    assert find_closest_products("#C85A32", catalog_df, top_n=0) == []


def test_image_extraction_edge_cases():
    """Tests dominant color extraction on transparent images, small images, and corrupt inputs."""
    # 1x1 small image
    tiny = Image.new("RGB", (1, 1), color=(100, 150, 200))
    pal_tiny = extract_dominant_colors(tiny, num_colors=1)
    assert len(pal_tiny) == 1
    assert pal_tiny[0]["hex"] == "#6496C8"

    # Transparent RGBA image composited over white background
    transparent_img = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
    pal_trans = extract_dominant_colors(transparent_img, num_colors=1)
    # Fully transparent over white should yield white, NOT black
    assert pal_trans[0]["hex"] == "#FFFFFF"

    # Empty bytes input
    with pytest.raises(ValueError):
        extract_dominant_colors(b"")

    # num_colors < 1
    with pytest.raises(ValueError):
        extract_dominant_colors(tiny, num_colors=0)


def test_color_harmony_deterministic():
    """Verifies deterministic color harmony calculations (complementary, analogous, warm/cool)."""
    harmony = get_color_harmony("#C85A32")
    assert harmony["base_hex"] == "#C85A32"
    assert harmony["temperature"] == "Warm"
    assert len(harmony["analogous"]) == 2
    assert len(harmony["triadic"]) == 2
    assert "styling_tip" in harmony

    # Test cool color
    cool_harmony = get_color_harmony("#1E293B")
    assert cool_harmony["temperature"] == "Cool"
