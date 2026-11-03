"""
Ethical AI Auditor Engine for Team 7: Ethical AI Auditor for Retail.
Audits recommender systems for demographic proxy steering bias and privacy opt-in violations.
Adheres to strict mathematical and regulatory criteria (GDPR Art. 6/22, CCPA, EU AI Act High-Risk Systems).
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import hashlib
import json
import pandas as pd
import numpy as np
from scipy import stats

DEFAULT_AUDIT_PATH = Path(__file__).resolve().parent / "data" / "audit_dataset.csv"


def load_audit_data(filepath: str = None) -> pd.DataFrame:
    """Loads and validates recommender AI output dataset."""
    path = Path(filepath) if filepath else DEFAULT_AUDIT_PATH
    if not path.exists():
        raise FileNotFoundError(f"Audit dataset not found at {path}")
    df = pd.read_csv(path)
    required = ["Customer_ZipCode", "Recommended_Item_Price", "Opt_in_Status"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    return df


def audit_privacy_breaches(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Flags records where user data or AI recommendations were processed
    despite Opt_in_Status == False (GDPR Art. 6 & CCPA consent non-compliance).
    """
    df = df.copy()
    # Normalize boolean representations
    if df["Opt_in_Status"].dtype == object:
        df["Opt_in_Clean"] = df["Opt_in_Status"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
    else:
        df["Opt_in_Clean"] = df["Opt_in_Status"].astype(bool)

    breaches = df[df["Opt_in_Clean"] == False].copy()
    total_records = len(df)
    breach_count = len(breaches)
    breach_rate = round((breach_count / max(1, total_records)) * 100.0, 2)
    consented_count = total_records - breach_count

    metrics = {
        "total_records": total_records,
        "breach_count": breach_count,
        "consented_count": consented_count,
        "breach_rate_pct": breach_rate,
        "privacy_compliant": breach_count == 0,
        "regulatory_risk": "HIGH (GDPR / CCPA Infringement)" if breach_count > 0 else "ZERO (Full Consent Verified)"
    }
    return breaches, metrics


def audit_bias_correlation(
    df: pd.DataFrame,
    corr_threshold: float = 0.40,
    impact_threshold: float = 0.60
) -> Dict[str, Any]:
    """
    Audits correlation between demographic proxies (Zip code / income proxy)
    and recommended item price. Detects disparate steering and redlining proxies.
    """
    df = df.copy()
    prices = df["Recommended_Item_Price"].astype(float)

    # Use Customer_Income_Proxy if available, else map Zip Codes ordinally
    if "Customer_Income_Proxy" in df.columns:
        demographic_proxy = df["Customer_Income_Proxy"].astype(float)
    else:
        demographic_proxy = df["Customer_ZipCode"].astype("category").cat.codes.astype(float)

    # Pearson correlation with statistical significance
    if len(df) > 1 and prices.std() > 0 and demographic_proxy.std() > 0:
        corr, p_value = stats.pearsonr(demographic_proxy, prices)
    else:
        corr, p_value = 0.0, 1.0

    # Group price statistics by Zip Code
    zip_summary = (
        df.groupby("Customer_ZipCode")["Recommended_Item_Price"]
        .agg(["mean", "median", "std", "count"])
        .reset_index()
    )
    zip_summary["std"] = zip_summary["std"].fillna(0.0)

    max_avg_price = float(zip_summary["mean"].max()) if not zip_summary.empty else 0.0
    min_avg_price = float(zip_summary["mean"].min()) if not zip_summary.empty else 0.0
    disparate_impact_ratio = round(min_avg_price / max(1.0, max_avg_price), 2)

    # Four-fifths (80%) rule check
    four_fifths_violation = disparate_impact_ratio < 0.80

    # Severe steering bias if |correlation| >= threshold or disparate impact ratio < impact_threshold
    has_steering_bias = abs(corr) >= corr_threshold or disparate_impact_ratio < impact_threshold

    return {
        "pearson_correlation": round(float(corr), 3),
        "p_value": float(p_value),
        "statistically_significant": bool(p_value < 0.05),
        "disparate_impact_ratio": disparate_impact_ratio,
        "four_fifths_violation": four_fifths_violation,
        "max_zip_avg_price": round(float(max_avg_price), 2),
        "min_zip_avg_price": round(float(min_avg_price), 2),
        "price_spread": round(float(max_avg_price - min_avg_price), 2),
        "has_steering_bias": has_steering_bias,
        "zip_summary": zip_summary.to_dict(orient="records")
    }


def generate_compliance_report(
    df: pd.DataFrame,
    corr_threshold: float = 0.40,
    impact_threshold: float = 0.60
) -> Dict[str, Any]:
    """
    Generates unified Red-Teaming compliance scorecard with risk rating,
    regulatory cross-referencing, and action playbooks.
    """
    breaches_df, priv_metrics = audit_privacy_breaches(df)
    bias_metrics = audit_bias_correlation(df, corr_threshold, impact_threshold)

    # Overall Risk Assessment Matrix
    if priv_metrics["breach_count"] > 0 and bias_metrics["has_steering_bias"]:
        risk_level = "CRITICAL NON-COMPLIANCE"
        risk_color = "#ef4444"
        action = "HALT MODEL DEPLOYMENT IMMEDIATELY: Both GDPR/CCPA privacy breaches and predatory price steering detected."
        governance_score = max(10, 100 - (priv_metrics["breach_count"] * 3 + int(abs(bias_metrics["pearson_correlation"]) * 50)))
    elif priv_metrics["breach_count"] > 0:
        risk_level = "PRIVACY BREACH WARNING"
        risk_color = "#f59e0b"
        action = "Purge non-opted-in user rows and tighten consent gating."
        governance_score = max(40, 100 - (priv_metrics["breach_count"] * 4))
    elif bias_metrics["has_steering_bias"]:
        risk_level = "DEMOGRAPHIC BIAS WARNING"
        risk_color = "#f59e0b"
        action = "Re-balance training weights to decouple product pricing from demographic zip code proxies."
        governance_score = max(50, 100 - int(abs(bias_metrics["pearson_correlation"]) * 60))
    else:
        risk_level = "COMPLIANT & AUDITED"
        risk_color = "#00e676"
        action = "System passes ethical AI threshold."
        governance_score = 98

    return {
        "risk_level": risk_level,
        "risk_color": risk_color,
        "recommended_action": action,
        "governance_score": min(100, max(0, governance_score)),
        "privacy": priv_metrics,
        "bias": bias_metrics
    }


def scrub_privacy_violations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simulates automated GDPR Art. 17 'Right to Erasure' and CCPA compliance scrub:
    Purges non-opted-in records and returns a clean, compliant dataset.
    """
    df = df.copy()
    if df["Opt_in_Status"].dtype == object:
        mask = df["Opt_in_Status"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
    else:
        mask = df["Opt_in_Status"].astype(bool)
    return df[mask].reset_index(drop=True)


def generate_audit_certificate_metadata(df: pd.DataFrame, report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates verifiable cryptographic checksum and regulatory certificate payload.
    """
    payload_str = f"{len(df)}_{report['risk_level']}_{report['governance_score']}"
    cert_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()[:16].upper()
    return {
        "certificate_id": f"CERT-ETHIX-2026-{cert_hash}",
        "auditor_framework": "Retail AI Lab Regulatory Compliance Spec v2.1",
        "standard_alignment": ["GDPR Art. 6/17/22", "CCPA Title 1.81.5", "EU AI Act High-Risk Annex III", "FTC Fair Pricing Guidance"],
        "records_audited": len(df),
        "governance_score": report["governance_score"],
        "final_status": report["risk_level"]
    }
