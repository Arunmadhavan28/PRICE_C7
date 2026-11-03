"""
Unit tests for Team 2: The Sassy Stylist Bot.
Verifies Layer 1 Data and Math functions, Grounding Guarantee, and Stylist Engine Logic.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from stylist_engine import (
    load_catalog,
    search_catalog_by_vibe,
    recommend_outfit,
    get_sassy_stylist_response,
    calculate_vibe_similarity,
    calculate_outfit_budget_breakdown,
    filter_catalog_by_budget
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "catalog_50.json"


@pytest.fixture
def catalog():
    return load_catalog(str(DATA_PATH))


def test_catalog_volume_and_schema(catalog):
    """Verifies catalog contains 50 items and adheres to required schema."""
    assert len(catalog) >= 50
    required_keys = ["Product_Name", "Category", "Price", "Vibe_Tags", "Image_URL"]
    for item in catalog:
        for k in required_keys:
            assert k in item, f"Missing key '{k}' in item {item}"
        assert isinstance(item["Price"], (int, float))
        assert item["Price"] > 0
        assert isinstance(item["Vibe_Tags"], list)


def test_vibe_search_matching(catalog):
    """Verifies that search matches beach wedding queries appropriately."""
    results = search_catalog_by_vibe("beach wedding", catalog, top_k=3)
    assert len(results) == 3
    tags = [t.lower() for item in results for t in item.get("Vibe_Tags", [])]
    assert any("beach" in t or "wedding" in t for t in tags)


def test_grounding_guarantee(catalog):
    """Guarantees that recommended items strictly originate from the local catalog."""
    catalog_names = {item["Product_Name"] for item in catalog}
    recs = recommend_outfit("rave in berlin", catalog)
    assert len(recs) > 0
    for rec in recs:
        assert rec["Product_Name"] in catalog_names, f"Hallucinated item: {rec['Product_Name']}"


def test_stylist_response_generation(catalog):
    """Ensures stylist response produces coherent recommendations and item list."""
    response_text, items = get_sassy_stylist_response("cocktail party", catalog=catalog)
    assert len(response_text) > 20
    assert len(items) > 0
    keywords = ["curated", "outfit", "style", "selection", "catalog", "recommended", "pieces", "investment"]
    assert any(k in response_text.lower() for k in keywords)


def test_similarity_scoring_math():
    """Verifies Layer 1 mathematical similarity function properties."""
    sample_item = {
        "Product_Name": "Silk Slip Evening Dress",
        "Category": "Dresses",
        "Price": 180.0,
        "Vibe_Tags": ["cocktail", "black tie", "formal", "glam"],
        "Description": "Luxurious bias-cut silk dress ideal for formal gala evenings."
    }
    # Direct match on tag and title
    score_high = calculate_vibe_similarity("cocktail evening dress", sample_item)
    assert 0.0 <= score_high <= 1.0
    assert score_high > 0.3

    # Unrelated query should yield 0.0
    score_zero = calculate_vibe_similarity("ski mountain parka winter blizzard", sample_item)
    assert score_zero == 0.0

    # Empty query should yield 0.0
    score_empty = calculate_vibe_similarity("", sample_item)
    assert score_empty == 0.0


def test_budget_breakdown_math(catalog):
    """Verifies financial aggregation math across recommended outfits."""
    sample_outfit = catalog[:4]
    breakdown = calculate_outfit_budget_breakdown(sample_outfit)

    expected_total = round(sum(item["Price"] for item in sample_outfit), 2)
    expected_avg = round(expected_total / 4, 2)

    assert breakdown["item_count"] == 4
    assert breakdown["total_cost"] == expected_total
    assert breakdown["average_price"] == expected_avg
    assert breakdown["min_price"] == min(item["Price"] for item in sample_outfit)
    assert breakdown["max_price"] == max(item["Price"] for item in sample_outfit)
    assert sum(breakdown["category_counts"].values()) == 4


def test_filter_by_budget(catalog):
    """Verifies that budget filter strictly honors maximum price threshold."""
    budget_limit = 100.0
    filtered = filter_catalog_by_budget(catalog, max_price=budget_limit)
    assert len(filtered) > 0
    for item in filtered:
        assert item["Price"] <= budget_limit
