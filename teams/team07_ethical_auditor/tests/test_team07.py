"""
Unit tests for Team 7: Ethical AI Auditor for Retail.
Evaluates algorithmic precision, schema validity, disparate impact math,
and GDPR/CCPA privacy quarantine logic.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from auditor import (
    load_audit_data,
    audit_privacy_breaches,
    audit_bias_correlation,
    generate_compliance_report,
    scrub_privacy_violations,
    generate_audit_certificate_metadata
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "audit_dataset.csv"


@pytest.fixture
def audit_df():
    return load_audit_data(str(DATA_PATH))


def test_audit_data_schema(audit_df):
    """Verifies schema conformance for audit log dataset."""
    required = ["Customer_ZipCode", "Recommended_Item_Price", "Opt_in_Status"]
    for col in required:
        assert col in audit_df.columns
    assert len(audit_df) >= 25
    assert (audit_df["Recommended_Item_Price"] > 0).all()


def test_privacy_breach_detection(audit_df):
    """Detects and isolates records processed without user opt-in."""
    breaches, metrics = audit_privacy_breaches(audit_df)
    assert "breach_count" in metrics
    assert "breach_rate_pct" in metrics
    # Every row in breaches must have Opt_in_Clean == False
    assert (breaches["Opt_in_Clean"] == False).all()
    assert metrics["breach_count"] == len(breaches)
    assert metrics["consented_count"] + metrics["breach_count"] == metrics["total_records"]


def test_bias_correlation_calculation(audit_df):
    """Verifies demographic proxy price correlation calculation."""
    bias = audit_bias_correlation(audit_df)
    assert "pearson_correlation" in bias
    assert -1.0 <= bias["pearson_correlation"] <= 1.0
    assert "disparate_impact_ratio" in bias
    assert bias["disparate_impact_ratio"] > 0
    assert "statistically_significant" in bias
    assert "price_spread" in bias
    assert bias["price_spread"] >= 0


def test_compliance_report_generation(audit_df):
    """Ensures compliance report outputs full risk assessment."""
    report = generate_compliance_report(audit_df)
    assert "risk_level" in report
    assert "recommended_action" in report
    assert "governance_score" in report
    assert 0 <= report["governance_score"] <= 100
    assert report["risk_level"] in [
        "CRITICAL NON-COMPLIANCE",
        "PRIVACY BREACH WARNING",
        "DEMOGRAPHIC BIAS WARNING",
        "COMPLIANT & AUDITED"
    ]


def test_scrub_privacy_violations(audit_df):
    """Verifies GDPR Art. 17 data purge returns 100% consented dataset."""
    clean_df = scrub_privacy_violations(audit_df)
    assert len(clean_df) > 0
    assert len(clean_df) <= len(audit_df)
    _, metrics = audit_privacy_breaches(clean_df)
    assert metrics["breach_count"] == 0
    assert metrics["privacy_compliant"] is True


def test_audit_certificate_generation(audit_df):
    """Verifies cryptographic compliance certificate generation."""
    report = generate_compliance_report(audit_df)
    cert = generate_audit_certificate_metadata(audit_df, report)
    assert "certificate_id" in cert
    assert cert["certificate_id"].startswith("CERT-ETHIX-2026-")
    assert "standard_alignment" in cert
    assert len(cert["standard_alignment"]) >= 3
    assert cert["records_audited"] == len(audit_df)
