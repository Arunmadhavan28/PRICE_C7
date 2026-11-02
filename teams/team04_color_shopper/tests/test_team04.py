"""
Unit tests for Team 4: Color-Palette Personal Shopper.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from PIL import Image
from color_engine import (
    hex_to_rgb,
    rgb_to_hex,
    calculate_color_distance,
    extract_dominant_colors,
    find_closest_products
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
