"""
Comprehensive Unit Test Suite for Team 8: The Virtual Try-On Feedback Loop (AR/VR Analytics).

Covers all required test specifications:
1. CSV schema
2. Required columns
3. Boolean data types
4. Minimum number of sessions (>= 250)
5. AR vs Non-AR segmentation
6. Conversion lift calculation
7. Zero-division protection
8. Funnel metric generation
9. AOV calculation
10. Revenue calculation
11. Statistical significance testing
12. AR engagement duration buckets
13. Executive PDF generation
Plus error handling and edge cases.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

# Add the team root directory to sys.path
TEAM_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TEAM_DIR))

from funnel_engine import (
    load_session_logs,
    calculate_funnel_metrics,
    calculate_conversion_lift,
    segment_ar_vs_non_ar,
    calculate_statistical_validation,
    calculate_engagement_buckets,
    generate_pdf_report,
    calculate_revenue_impact,
    calculate_device_breakdown,
    REQUIRED_COLUMNS
)

DATA_PATH = TEAM_DIR / "data" / "session_logs.csv"


@pytest.fixture
def logs_df():
    """Fixture providing loaded and validated session telemetry."""
    return load_session_logs(str(DATA_PATH))


# 1. Test CSV Schema & 2. Required Columns
def test_csv_schema_and_required_columns(logs_df):
    """
    1. CSV schema validation
    2. Required columns validation
    Verifies that all core required columns exist in the loaded dataset.
    """
    for col in REQUIRED_COLUMNS:
        assert col in logs_df.columns, f"Required column '{col}' is missing from session logs."
    assert "Cart_Value" in logs_df.columns, "Column 'Cart_Value' should be present."
    assert "Device_Type" in logs_df.columns, "Column 'Device_Type' should be present."


# 3. Test Boolean Data Types
def test_boolean_data_types(logs_df):
    """
    3. Boolean data types validation
    Verifies that AR_TryOn_Used and Purchase_Made are standardized to boolean type.
    """
    assert logs_df["AR_TryOn_Used"].dtype == bool, "AR_TryOn_Used must be of boolean dtype."
    assert logs_df["Purchase_Made"].dtype == bool, "Purchase_Made must be of boolean dtype."


# 4. Test Minimum Number of Sessions
def test_minimum_number_of_sessions(logs_df):
    """
    4. Minimum number of sessions validation
    Verifies that session logs contain at least 250 realistic session records.
    """
    assert len(logs_df) >= 250, f"Expected >= 250 sessions, but found {len(logs_df)}."


# 5. Test AR vs Non-AR Segmentation
def test_ar_vs_non_ar_segmentation(logs_df):
    """
    5. AR vs Non-AR segmentation validation
    Verifies clean partition into mutually exclusive AR and Non-AR subsets.
    """
    ar_df, non_ar_df = segment_ar_vs_non_ar(logs_df)
    assert len(ar_df) + len(non_ar_df) == len(logs_df), "Segmentation must account for 100% of rows."
    assert (ar_df["AR_TryOn_Used"] == True).all(), "All rows in ar_df must have AR_TryOn_Used == True."
    assert (non_ar_df["AR_TryOn_Used"] == False).all(), "All rows in non_ar_df must have AR_TryOn_Used == False."
    assert (non_ar_df["Time_in_AR"] == 0).all(), "Non-AR users must have Time_in_AR equal to 0."
    assert (ar_df["Time_in_AR"] > 0).all(), "AR users must have Time_in_AR > 0."


# 6. Test Conversion Lift Calculation
def test_conversion_lift_calculation():
    """
    6. Conversion lift calculation validation
    Validates formula: ((AR Conversion Rate - Non-AR Conversion Rate) / Non-AR Conversion Rate) * 100.
    """
    # 30.0% AR vs 20.0% Non-AR -> ((30 - 20) / 20) * 100 = 50.0%
    lift = calculate_conversion_lift(30.0, 20.0)
    assert lift == 50.0, f"Expected 50.0, got {lift}"

    # Standard case: 38.0% AR vs 19.0% Non-AR -> 100.0% lift
    assert calculate_conversion_lift(38.0, 19.0) == 100.0


# 7. Test Zero-Division Protection
def test_zero_division_protection():
    """
    7. Zero-division protection validation
    Verifies that when Non-AR baseline conversion is 0.0 or negative,
    the function returns 0.0 rather than raising ZeroDivisionError.
    """
    assert calculate_conversion_lift(10.0, 0.0) == 0.0, "calculate_conversion_lift(10.0, 0.0) must return 0.0"
    assert calculate_conversion_lift(0.0, 0.0) == 0.0
    assert calculate_conversion_lift(25.0, -5.0) == 0.0


# 8. Test Funnel Metric Generation
def test_funnel_metrics_generation(logs_df):
    """
    8. Funnel metric generation validation
    Verifies that calculate_funnel_metrics produces all required keys with valid values.
    """
    metrics = calculate_funnel_metrics(logs_df)
    expected_keys = [
        "total_sessions", "ar_sessions", "non_ar_sessions",
        "ar_purchases", "non_ar_purchases", "cr_ar", "cr_non_ar",
        "conversion_lift_pct", "aov_ar", "aov_non_ar",
        "total_rev_ar", "total_rev_non_ar", "avg_time_in_ar_sec"
    ]
    for key in expected_keys:
        assert key in metrics, f"Metric '{key}' missing from calculate_funnel_metrics result."

    assert metrics["total_sessions"] == len(logs_df)
    assert metrics["ar_sessions"] + metrics["non_ar_sessions"] == metrics["total_sessions"]
    assert metrics["ar_sessions"] > 0
    assert metrics["non_ar_sessions"] > 0
    assert 0.0 <= metrics["cr_ar"] <= 100.0
    assert 0.0 <= metrics["cr_non_ar"] <= 100.0
    assert metrics["avg_time_in_ar_sec"] > 0.0


# 9. Test AOV (Average Order Value) Calculation
def test_aov_calculation():
    """
    9. AOV calculation validation
    Verifies that Average Order Value is correctly computed as mean Cart_Value of purchasing sessions.
    """
    sample_df = pd.DataFrame([
        {"Session_ID": "S1", "AR_TryOn_Used": True, "Time_in_AR": 60, "Purchase_Made": True, "Cart_Value": 100.0},
        {"Session_ID": "S2", "AR_TryOn_Used": True, "Time_in_AR": 90, "Purchase_Made": True, "Cart_Value": 200.0},
        {"Session_ID": "S3", "AR_TryOn_Used": True, "Time_in_AR": 45, "Purchase_Made": False, "Cart_Value": 0.0},
        {"Session_ID": "S4", "AR_TryOn_Used": False, "Time_in_AR": 0, "Purchase_Made": True, "Cart_Value": 50.0},
        {"Session_ID": "S5", "AR_TryOn_Used": False, "Time_in_AR": 0, "Purchase_Made": False, "Cart_Value": 0.0},
    ])
    metrics = calculate_funnel_metrics(sample_df)
    assert metrics["aov_ar"] == 150.00
    assert metrics["aov_non_ar"] == 50.00


# 10. Test Revenue Calculation
def test_revenue_calculation():
    """
    10. Revenue calculation validation
    Verifies total revenue accumulation for AR and Non-AR purchasing cohorts.
    """
    sample_df = pd.DataFrame([
        {"Session_ID": "S1", "AR_TryOn_Used": True, "Time_in_AR": 60, "Purchase_Made": True, "Cart_Value": 120.50},
        {"Session_ID": "S2", "AR_TryOn_Used": True, "Time_in_AR": 80, "Purchase_Made": True, "Cart_Value": 79.50},
        {"Session_ID": "S3", "AR_TryOn_Used": False, "Time_in_AR": 0, "Purchase_Made": True, "Cart_Value": 60.00},
        {"Session_ID": "S4", "AR_TryOn_Used": False, "Time_in_AR": 0, "Purchase_Made": False, "Cart_Value": 0.0},
    ])
    metrics = calculate_funnel_metrics(sample_df)
    assert metrics["total_rev_ar"] == 200.00
    assert metrics["total_rev_non_ar"] == 60.00


# 11. Test Statistical Significance Testing
def test_statistical_validation():
    """
    11. Statistical validation
    Verifies two-proportion pooled z-test, confidence intervals, and p-value generation.
    """
    stat = calculate_statistical_validation(ar_purchases=45, ar_sessions=119, non_ar_purchases=33, non_ar_sessions=181)
    assert "z_score" in stat
    assert "p_value" in stat
    assert "is_significant" in stat
    assert stat["z_score"] > 3.0
    assert stat["p_value"] < 0.01
    assert stat["is_significant"] == True
    assert stat["ci_ar"][0] > 0
    assert stat["ci_non_ar"][0] > 0


# 12. Test AR Engagement Duration Buckets
def test_engagement_buckets(logs_df):
    """
    12. Engagement buckets validation
    Verifies computation of 5 duration buckets (0-30s, 30-60s, 60-90s, 90-120s, Above 120s).
    """
    buckets_df = calculate_engagement_buckets(logs_df)
    assert len(buckets_df) == 5
    assert set(buckets_df["Bucket"].tolist()) == {"0–30s", "30–60s", "60–90s", "90–120s", "Above 120s"}
    assert buckets_df["Sessions"].sum() == (logs_df["AR_TryOn_Used"] == True).sum()


# 13. Test Executive PDF Generation
def test_pdf_report_generation(logs_df):
    """
    13. PDF report generation validation
    Verifies that generate_pdf_report produces valid PDF bytes.
    """
    m = calculate_funnel_metrics(logs_df)
    rev = calculate_revenue_impact(m)
    stat = calculate_statistical_validation(m["ar_purchases"], m["ar_sessions"], m["non_ar_purchases"], m["non_ar_sessions"])
    dev = calculate_device_breakdown(logs_df)
    eng = calculate_engagement_buckets(logs_df)

    pdf_bytes = generate_pdf_report(m, rev, stat, dev, eng)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 200
    assert pdf_bytes.startswith(b"%PDF")


# 14. Edge Case: Empty Dataset Handling
def test_empty_dataset_handling():
    """
    Edge case: Empty DataFrame handling.
    """
    empty_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    metrics = calculate_funnel_metrics(empty_df)
    assert metrics["total_sessions"] == 0
    assert metrics["cr_ar"] == 0.0
    assert metrics["cr_non_ar"] == 0.0
    assert metrics["conversion_lift_pct"] == 0.0
    assert metrics["total_rev_ar"] == 0.0


# 15. Edge Case: Missing File Handling
def test_missing_file_handling():
    """
    Edge case: Non-existent file.
    """
    with pytest.raises(FileNotFoundError):
        load_session_logs("data/non_existent_file_12345.csv")


# 16. Edge Case: Missing Required Columns
def test_missing_required_columns():
    """
    Edge case: Missing columns in CSV.
    """
    invalid_df = pd.DataFrame({"Some_Column": [1, 2, 3]})
    temp_path = TEAM_DIR / "data" / "temp_invalid.csv"
    try:
        invalid_df.to_csv(temp_path, index=False)
        with pytest.raises(ValueError, match="Missing required columns"):
            load_session_logs(str(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()
