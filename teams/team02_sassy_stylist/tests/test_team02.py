"""
Unit tests for Team 2: The Sassy Stylist Bot.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from stylist_engine import (
    load_catalog,
    search_catalog_by_vibe,
    recommend_outfit,
    get_sassy_stylist_response
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
    # At least one returned item should have beach wedding tag
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
    keywords = ["curated", "outfit", "style", "selection", "catalog", "recommended"]
    assert any(k in response_text.lower() for k in keywords)
