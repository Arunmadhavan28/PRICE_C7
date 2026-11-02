"""
Color Matching Engine for Team 4: Color-Palette Personal Shopper.
Extracts dominant colors from images and performs Euclidean distance matching against product catalog.
"""

from io import BytesIO
from typing import List, Tuple, Dict, Any, Union
import numpy as np
import pandas as pd
from PIL import Image

MAX_RGB_DISTANCE = np.sqrt(255**2 + 255**2 + 255**2)  # ~441.67


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Converts a hex color string (e.g., '#C85A32' or 'C85A32') to (R, G, B) tuple."""
    hex_clean = hex_code.lstrip("#")
    if len(hex_clean) != 6:
        raise ValueError(f"Invalid hex color code: {hex_code}")
    return tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converts an (R, G, B) integer tuple to standard '#RRGGBB' hex string."""
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"


def calculate_color_distance(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """Calculates 3D Euclidean distance between two colors in RGB space."""
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    dist = np.sqrt((float(r1) - float(r2))**2 + (float(g1) - float(g2))**2 + (float(b1) - float(b2))**2)
    return round(float(dist), 2)


def extract_dominant_colors(image_source: Union[str, bytes, BytesIO], num_colors: int = 3) -> List[Dict[str, Any]]:
    """
    Extracts dominant color palette from an image using color quantization.
    Returns list of dicts with 'hex', 'rgb', and 'share_pct'.
    """
    if isinstance(image_source, Image.Image):
        img = image_source.copy()
    elif isinstance(image_source, (bytes, bytearray)):
        img = Image.open(BytesIO(image_source))
    elif isinstance(image_source, BytesIO):
        img = Image.open(image_source)
    else:
        img = Image.open(str(image_source))

    # Convert to RGB and resize for speed
    img = img.convert("RGB")
    img = img.resize((150, 150))

    # Quantize to dominant colors
    quantized = img.quantize(colors=num_colors, method=Image.Quantize.FASTOCTREE)
    palette = quantized.getpalette()[:num_colors * 3]

    color_counts = quantized.getcolors()
    total_pixels = sum(count for count, _ in color_counts)

    results = []
    # Sort by pixel frequency descending
    color_counts.sort(key=lambda x: x[0], reverse=True)

    for count, color_idx in color_counts[:num_colors]:
        idx = color_idx * 3
        r, g, b = palette[idx], palette[idx + 1], palette[idx + 2]
        hex_val = rgb_to_hex(r, g, b)
        share = round((count / total_pixels) * 100, 1)
        results.append({
            "hex": hex_val,
            "rgb": (r, g, b),
            "share_pct": share
        })

    return results


def find_closest_products(
    target_color: Union[str, Tuple[int, int, int]],
    catalog_df: pd.DataFrame,
    top_n: int = 4
) -> List[Dict[str, Any]]:
    """
    Finds the top N closest matching catalog products to a given hex or RGB color.
    Calculates match confidence percentage (0-100%).
    """
    if isinstance(target_color, str):
        target_rgb = hex_to_rgb(target_color)
    else:
        target_rgb = target_color

    matches = []
    for _, row in catalog_df.iterrows():
        prod_rgb = (int(row["RGB_R"]), int(row["RGB_G"]), int(row["RGB_B"]))
        distance = calculate_color_distance(target_rgb, prod_rgb)
        confidence = max(0.0, round((1.0 - (distance / MAX_RGB_DISTANCE)) * 100.0, 1))

        matches.append({
            "Product_Name": row["Product_Name"],
            "Category": row.get("Category", "Catalog"),
            "Hex_Color_Code": row["Hex_Color_Code"],
            "Price": float(row["Price"]),
            "Image_URL": row["Image_URL"],
            "Distance": distance,
            "Match_Confidence": confidence
        })

    matches.sort(key=lambda x: x["Distance"])
    return matches[:top_n]
