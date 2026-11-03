"""
Color Matching Engine for Team 4: Color-Palette Personal Shopper.
Extracts dominant colors from images and performs Euclidean distance matching against product catalog.
"""

from io import BytesIO
from typing import List, Tuple, Dict, Any, Union, Optional
import colorsys
import numpy as np
import pandas as pd
from PIL import Image

MAX_RGB_DISTANCE = float(np.sqrt(255**2 + 255**2 + 255**2))  # ~441.67


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """
    Converts a hex color string (e.g., '#C85A32', 'C85A32', or 3-digit shorthand '#FFF')
    to an (R, G, B) integer tuple.
    Raises ValueError on invalid formats, non-hex characters, or empty strings.
    """
    if not isinstance(hex_code, str):
        raise ValueError(f"Hex color code must be a string, got {type(hex_code).__name__}")

    hex_clean = hex_code.strip()
    if hex_clean.startswith("#"):
        hex_clean = hex_clean[1:]

    # Support standard 3-digit shorthand (e.g., 'F50' -> 'FF5500')
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)

    if len(hex_clean) != 6:
        raise ValueError(f"Invalid hex color code: '{hex_code}' (expected 3 or 6 hex digits)")

    try:
        return tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError(f"Invalid hex color code: '{hex_code}' (contains non-hexadecimal characters)")


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Converts an (R, G, B) integer tuple to a standard '#RRGGBB' uppercase hex string.
    Validates that channel values are integers in the range [0, 255].
    """
    for channel, name in ((r, "R"), (g, "G"), (b, "B")):
        if not isinstance(channel, (int, float, np.integer, np.floating)) or np.isnan(channel):
            raise ValueError(f"RGB channel {name} must be numeric, got {channel}")
        if not (0 <= channel <= 255):
            raise ValueError(f"RGB channel {name} must be between 0 and 255, got {channel}")
    return f"#{int(round(r)):02X}{int(round(g)):02X}{int(round(b)):02X}"


def calculate_color_distance(
    rgb1: Union[Tuple[int, int, int], List[int]],
    rgb2: Union[Tuple[int, int, int], List[int]]
) -> float:
    """
    Calculates the 3D Euclidean distance between two colors in RGB space:
    sqrt((R1-R2)^2 + (G1-G2)^2 + (B1-B2)^2)
    Returns rounded distance float (0.0 to ~441.67).
    """
    if len(rgb1) != 3 or len(rgb2) != 3:
        raise ValueError(f"RGB tuples must have exactly 3 channels: rgb1={rgb1}, rgb2={rgb2}")

    r1, g1, b1 = (float(c) for c in rgb1)
    r2, g2, b2 = (float(c) for c in rgb2)

    for c, name in ((r1, "r1"), (g1, "g1"), (b1, "b1"), (r2, "r2"), (g2, "g2"), (b2, "b2")):
        if not (0.0 <= c <= 255.0):
            raise ValueError(f"RGB channel {name} value {c} out of range [0, 255]")

    dist = np.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
    return round(float(dist), 2)


def validate_catalog_dataframe(catalog_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates catalog schema, imputes missing RGB channels from Hex_Color_Code,
    validates prices, and filters out malformed rows.
    Required columns: Product_Name, Hex_Color_Code, Image_URL.
    """
    if catalog_df is None or not isinstance(catalog_df, pd.DataFrame):
        raise ValueError("Catalog must be a valid pandas DataFrame")
    if catalog_df.empty:
        raise ValueError("Catalog DataFrame is empty")

    required_cols = ["Product_Name", "Hex_Color_Code", "Image_URL"]
    missing = [col for col in required_cols if col not in catalog_df.columns]
    if missing:
        raise ValueError(f"Catalog DataFrame missing required columns: {missing}")

    df = catalog_df.copy()

    # Clean and sanitize required string fields
    df["Product_Name"] = df["Product_Name"].astype(str).str.strip()
    df["Hex_Color_Code"] = df["Hex_Color_Code"].astype(str).str.strip()
    df["Image_URL"] = df["Image_URL"].astype(str).str.strip()

    # Filter out empty product names or hex codes
    df = df[df["Product_Name"].str.len() > 0]
    df = df[df["Hex_Color_Code"].str.len() > 0]

    has_rgb = all(col in df.columns for col in ("RGB_R", "RGB_G", "RGB_B"))
    valid_rows = []

    for _, row in df.iterrows():
        try:
            hex_rgb = hex_to_rgb(row["Hex_Color_Code"])
        except ValueError:
            continue  # Discard rows with invalid hex codes

        if has_rgb:
            try:
                r, g, b = int(row["RGB_R"]), int(row["RGB_G"]), int(row["RGB_B"])
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    r, g, b = hex_rgb
            except (ValueError, TypeError):
                r, g, b = hex_rgb
        else:
            r, g, b = hex_rgb

        row_dict = row.to_dict()
        row_dict["RGB_R"] = r
        row_dict["RGB_G"] = g
        row_dict["RGB_B"] = b

        # Normalize Category
        if "Category" not in row_dict or pd.isna(row_dict["Category"]):
            row_dict["Category"] = "General"
        else:
            row_dict["Category"] = str(row_dict["Category"]).strip()

        # Normalize Price
        if "Price" in row_dict:
            try:
                p = float(row_dict["Price"])
                row_dict["Price"] = max(0.0, p)
            except (ValueError, TypeError):
                row_dict["Price"] = 0.0
        else:
            row_dict["Price"] = 0.0

        valid_rows.append(row_dict)

    if not valid_rows:
        raise ValueError("No valid product rows remaining after catalog validation")

    return pd.DataFrame(valid_rows)


def extract_dominant_colors(
    image_source: Union[str, bytes, bytearray, BytesIO, Image.Image],
    num_colors: int = 3
) -> List[Dict[str, Any]]:
    """
    Extracts dominant color palette from an image using color quantization.
    Handles transparency, empty/corrupt files, and returns list of dicts with 'hex', 'rgb', and 'share_pct'.
    """
    if num_colors < 1:
        raise ValueError(f"num_colors must be at least 1, got {num_colors}")

    if isinstance(image_source, Image.Image):
        img = image_source.copy()
    elif isinstance(image_source, (bytes, bytearray)):
        if len(image_source) == 0:
            raise ValueError("Cannot extract colors from empty bytes")
        try:
            img = Image.open(BytesIO(image_source))
        except Exception as e:
            raise ValueError(f"Failed to open image from bytes: {e}")
    elif isinstance(image_source, BytesIO):
        image_source.seek(0)
        try:
            img = Image.open(image_source)
        except Exception as e:
            raise ValueError(f"Failed to open image from BytesIO: {e}")
    else:
        try:
            img = Image.open(str(image_source))
        except Exception as e:
            raise ValueError(f"Failed to open image from path '{image_source}': {e}")

    # Handle alpha/transparency: composite onto white background so alpha does not become false black
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img_rgba = img.convert("RGBA")
        bg = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
        bg.paste(img_rgba, (0, 0), img_rgba)
        img = bg.convert("RGB")
    else:
        img = img.convert("RGB")

    # Resize for speed and normalization
    img = img.resize((150, 150))

    # Quantize to dominant colors
    quantized = img.quantize(colors=num_colors, method=Image.Quantize.FASTOCTREE)
    palette = quantized.getpalette() or []
    palette = palette[:num_colors * 3]

    # Safe getcolors with maxcolors covering all 150*150 pixels
    color_counts = quantized.getcolors(maxcolors=150 * 150)
    if not color_counts:
        r, g, b = img.getpixel((75, 75))
        return [{
            "hex": rgb_to_hex(r, g, b),
            "rgb": (r, g, b),
            "share_pct": 100.0
        }]

    total_pixels = sum(count for count, _ in color_counts)
    if total_pixels == 0:
        total_pixels = 1

    # Sort by pixel frequency descending
    color_counts.sort(key=lambda x: x[0], reverse=True)

    results = []
    for count, color_idx in color_counts[:num_colors]:
        idx = color_idx * 3
        if idx + 2 < len(palette):
            r, g, b = palette[idx], palette[idx + 1], palette[idx + 2]
        else:
            r, g, b = (128, 128, 128)
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
    top_n: int = 4,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Finds the top N closest matching catalog products to a given hex or RGB color.
    Supports optional category and price range filtering.
    Calculates match confidence percentage (0-100%).
    """
    if top_n <= 0:
        return []

    if isinstance(target_color, str):
        target_rgb = hex_to_rgb(target_color)
    else:
        if len(target_color) != 3:
            raise ValueError("target_color tuple must have 3 RGB elements")
        target_rgb = (int(target_color[0]), int(target_color[1]), int(target_color[2]))

    valid_df = validate_catalog_dataframe(catalog_df)

    # Optional category filter
    if category and category.strip().lower() != "all":
        valid_df = valid_df[valid_df["Category"].str.lower() == category.strip().lower()]

    # Optional price bounds filter
    if min_price is not None:
        valid_df = valid_df[valid_df["Price"] >= float(min_price)]
    if max_price is not None:
        valid_df = valid_df[valid_df["Price"] <= float(max_price)]

    if valid_df.empty:
        return []

    matches = []
    for _, row in valid_df.iterrows():
        prod_rgb = (int(row["RGB_R"]), int(row["RGB_G"]), int(row["RGB_B"]))
        distance = calculate_color_distance(target_rgb, prod_rgb)
        confidence = max(0.0, round((1.0 - (distance / MAX_RGB_DISTANCE)) * 100.0, 1))

        matches.append({
            "Product_Name": str(row["Product_Name"]),
            "Category": str(row.get("Category", "Catalog")),
            "Hex_Color_Code": str(row["Hex_Color_Code"]),
            "Price": float(row["Price"]),
            "Image_URL": str(row["Image_URL"]),
            "Distance": distance,
            "Match_Confidence": float(confidence)
        })

    matches.sort(key=lambda x: x["Distance"])
    return matches[:top_n]


def get_color_harmony(hex_code: str) -> Dict[str, Any]:
    """
    Calculates deterministic color harmony schemes (complementary, analogous, triadic)
    and styling temperature for visual commerce recommendations.
    Uses standard HSV/color-wheel geometry without external API calls.
    """
    r, g, b = hex_to_rgb(hex_code)
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    def hsv_to_hex(hue: float, sat: float, val: float) -> str:
        nr, ng, nb = colorsys.hsv_to_rgb(hue % 1.0, max(0.0, min(1.0, sat)), max(0.0, min(1.0, val)))
        return rgb_to_hex(int(round(nr * 255)), int(round(ng * 255)), int(round(nb * 255)))

    # Complementary (180 deg)
    comp_hex = hsv_to_hex(h + 0.5, s, v)

    # Analogous (+30 deg and -30 deg)
    analogous_1 = hsv_to_hex(h + (30.0 / 360.0), s, v)
    analogous_2 = hsv_to_hex(h - (30.0 / 360.0), s, v)

    # Triadic (+120 deg and +240 deg)
    triad_1 = hsv_to_hex(h + (120.0 / 360.0), s, v)
    triad_2 = hsv_to_hex(h + (240.0 / 360.0), s, v)

    # Color temperature classification
    hue_degrees = h * 360.0
    is_warm = (hue_degrees <= 90.0) or (hue_degrees >= 300.0)
    temperature = "Warm" if is_warm else "Cool"

    if is_warm:
        style_tip = (
            f"This warm shade ({hex_code.upper()}) brings inviting coziness. "
            f"Pair it with its cool complementary accent ({comp_hex}) for striking contrast, "
            f"or keep it cohesive with adjacent warm tones ({analogous_1}, {analogous_2})."
        )
    else:
        style_tip = (
            f"This cool tone ({hex_code.upper()}) evokes calm and modern refinement. "
            f"Introduce a warm complementary accent ({comp_hex}) to add dynamic balance, "
            f"or soften with adjacent harmonious hues ({analogous_1}, {analogous_2})."
        )

    return {
        "base_hex": hex_code.upper(),
        "temperature": temperature,
        "complementary": comp_hex,
        "analogous": [analogous_1, analogous_2],
        "triadic": [triad_1, triad_2],
        "styling_tip": style_tip
    }
