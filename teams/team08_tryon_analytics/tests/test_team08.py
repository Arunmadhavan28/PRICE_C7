"""
Unit tests for Team 8: The Virtual Try-On Feedback Loop.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from funnel_engine import (
    load_session_logs,
    calculate_funnel_metrics,
    calculate_conversion_lift,
    segment_ar_vs_non_ar
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "session_logs.csv"


@pytest.fixture
def logs_df():
    return load_session_logs(str(DATA_PATH))


def test_session_logs_schema(logs_df):
    """Verifies schema conformance for user session logs."""
    required = ["Session_ID", "AR_TryOn_Used", "Time_in_AR", "Purchase_Made"]
    for col in required:
        assert col in logs_df.columns
    assert len(logs_df) >= 50
    assert logs_df["AR_TryOn_Used"].dtype == bool
    assert logs_df["Purchase_Made"].dtype == bool


def test_ar_cohort_segmentation(logs_df):
    """Verifies clean separation into AR and Non-AR subsets."""
    ar_df, non_ar_df = segment_ar_vs_non_ar(logs_df)
    assert len(ar_df) + len(non_ar_df) == len(logs_df)
    assert (ar_df["AR_TryOn_Used"] == True).all()
    assert (non_ar_df["AR_TryOn_Used"] == False).all()


def test_conversion_lift_calculation():
    """Validates mathematical accuracy of conversion lift formula."""
    # 30% vs 20% -> 50% lift
    lift = calculate_conversion_lift(30.0, 20.0)
    assert lift == 50.0

    # Safeguard against zero division
    zero_lift = calculate_conversion_lift(10.0, 0.0)
    assert zero_lift == 0.0


def test_funnel_metrics_generation(logs_df):
    """Verifies calculation of full conversion funnel metrics."""
    metrics = calculate_funnel_metrics(logs_df)
    assert "cr_ar" in metrics
    assert "cr_non_ar" in metrics
    assert "conversion_lift_pct" in metrics
    assert "aov_ar" in metrics
    assert metrics["ar_sessions"] > 0
    assert metrics["non_ar_sessions"] > 0
