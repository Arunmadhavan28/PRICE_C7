"""
Unit tests for Team 5: The Empathy Engine.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from empathy_engine import (
    load_reviews,
    analyze_review,
    compute_emotion_distribution,
    analyze_bulk_reviews
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "customer_reviews.txt"


@pytest.fixture
def reviews():
    return load_reviews(str(DATA_PATH))


def test_reviews_volume(reviews):
    """Verifies at least 20 raw customer reviews are loaded."""
    assert len(reviews) >= 20
    assert all(len(r.strip()) > 10 for r in reviews)


def test_emotion_classification():
    """Validates accurate classification across key emotion categories."""
    joy_review = "I am absolutely thrilled and love this luxurious handbag, sheer perfection!"
    res_joy = analyze_review(joy_review)
    assert res_joy["emotion"] == "Joy"
    assert res_joy["polarity"] > 0

    frust_review = "The zipper broke on day one and customer support ignored me, total disaster!"
    res_frust = analyze_review(frust_review)
    assert res_frust["emotion"] == "Frustration"
    assert res_frust["polarity"] < 0

    conf_review = "I am puzzled by this sizing chart, it makes no sense and contradictory info everywhere."
    res_conf = analyze_review(conf_review)
    assert res_conf["emotion"] == "Confusion"


def test_distribution_sum_and_metrics(reviews):
    """Verifies that distribution percentages sum to 100%."""
    dist_df, metrics = compute_emotion_distribution(reviews)
    assert len(dist_df) > 0
    total_pct = dist_df["Percentage"].sum()
    assert 99.0 <= total_pct <= 101.0
    assert "satisfaction_rate" in metrics
    assert "friction_index" in metrics
    assert -1.0 <= metrics["avg_polarity"] <= 1.0


def test_bulk_dataframe_schema(reviews):
    """Checks DataFrame output from bulk analysis."""
    df = analyze_bulk_reviews(reviews[:5])
    assert len(df) == 5
    for col in ["review_text", "emotion", "polarity", "matched_keywords"]:
        assert col in df.columns
