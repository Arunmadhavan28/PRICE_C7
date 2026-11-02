"""
Streamlit Web Application for Team 7: Ethical AI Auditor for Retail.
Red-teaming alert dashboard detecting demographic pricing bias and privacy breaches.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from auditor import (
    load_audit_data,
    audit_privacy_breaches,
    audit_bias_correlation,
    generate_compliance_report
)

st.set_page_config(
    page_title="Ethical AI Auditor | Retail AI",
    layout="wide"
)

st.title("Ethical AI Auditor for Retail")
st.caption("AI Governance and Red-Teaming Dashboard | Target: Retail Compliance Officers and AI Ethics Teams")

# Load Audit Data
data_path = Path(__file__).parent / "data" / "audit_dataset.csv"
audit_df = load_audit_data(str(data_path))

# Run Audit
report = generate_compliance_report(audit_df)
priv = report["privacy"]
bias = report["bias"]
breaches_df, _ = audit_privacy_breaches(audit_df)

# Compliance Alert Banner
if report["risk_level"] != "COMPLIANT & AUDITED":
    st.warning(f"ALERT - {report['risk_level']}: {report['recommended_action']}")
else:
    st.success(f"STATUS - {report['risk_level']}: {report['recommended_action']}")

# Top Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Privacy Breaches", f"{priv['breach_count']} rows", delta=f"{priv['breach_rate_pct']}% of records", delta_color="inverse")
with col2:
    st.metric("Demographic Bias (r)", f"{bias['pearson_correlation']:+.3f}", delta="Price Steering Index", delta_color="inverse")
with col3:
    st.metric("Disparate Impact Ratio", f"{bias['disparate_impact_ratio']:.2f}", delta="Min/Max Zip Avg Ratio", delta_color="inverse")
with col4:
    st.metric("Audited Log Records", f"{priv['total_records']}", delta="PricingEngine_v2.1")

st.markdown("---")

# Visual Bias Correlation Scatter Plot
st.subheader("Demographic Proxy vs Recommended Price Scatter Plot")
st.caption("Detects if the AI model is steering lower-income neighborhoods toward cheap clearance and wealthy zip codes toward high-ticket items.")

plot_df = audit_df.copy()
plot_df["Opt_in_Label"] = plot_df["Opt_in_Status"].apply(lambda x: "Opted-In [PASS]" if x else "PRIVACY BREACH [FAIL]")

fig = px.scatter(
    plot_df,
    x="Customer_ZipCode",
    y="Recommended_Item_Price",
    color="Opt_in_Label",
    color_discrete_map={"Opted-In [PASS]": "#3b82f6", "PRIVACY BREACH [FAIL]": "#ef4444"},
    size="Recommended_Item_Price",
    hover_data=["Income_Bracket", "Item_Category"],
    trendline="ols"
)

fig.update_layout(
    template="plotly_dark",
    height=450,
    xaxis_type="category",
    xaxis_title="Customer Demographic Proxy (Zip Code)",
    yaxis_title="AI Recommended Product Price ($ USD)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Privacy Breach Quarantine View
st.markdown("---")
st.subheader("Quarantined Privacy Violations (Opt_in_Status == False)")
st.caption("The following users explicitly opted out or did not consent, but AI recommendations were still generated.")

if len(breaches_df) > 0:
    st.dataframe(breaches_df[["Customer_ZipCode", "Recommended_Item_Price", "Opt_in_Status", "Item_Category"]], use_container_width=True)
    if st.button("Simulate Automated GDPR Data Scrub / Quarantine"):
        st.success("Successfully quarantined non-consented logs from active training pipelines.")
else:
    st.info("No privacy violations found in active dataset.")
