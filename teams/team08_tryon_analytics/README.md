# The Virtual Try-On Feedback Loop (AR/VR Analytics)

**Track:** AR/VR Commerce Telemetry & Incremental Conversion Attribution Engine  
**Team:** Team 8  
**Application Name:** The Virtual Try-On Feedback Loop  

### Team Information
- **Team Members:**
  - Member 1: Pranetha S C (@pranethasc)
  - Member 2: Jency Soundarya (@jencysoundarya-boop)

---

## 1. Executive Summary & Problem Statement

E-commerce fashion and apparel retailers invest heavily in Augmented Reality (AR) and Virtual Reality (VR) virtual try-on features (3D avatar fittings, eyewear mirrors, footwear scale checkers). However, retail executives and board members face a critical business dilemma:

> **"Does the Virtual Try-On feature genuinely drive incremental conversion and basket valuation, or is it an expensive novelty feature?"**

**The Virtual Try-On Feedback Loop** is an enterprise-grade analytics application that ingests session-level customer telemetry to benchmark **AR Try-On users** against a baseline of **Standard / Non-AR users**. The platform isolates conversion efficiency, basket valuation (AOV), Revenue Per Session (RPS), and statistical significance to support data-driven capital allocation decisions.

---

## 2. Key Features

- **Six Core KPI Scorecards**:
  1. **AR Conversion Rate**: Percentage of AR-engaged sessions that completed a purchase.
  2. **AR Conversion Lift**: Relative conversion lift percentage over standard browsing control.
  3. **Non-AR Conversion Rate**: Baseline conversion rate of standard visitors.
  4. **AR Average Order Value (AOV)**: Mean transaction value of converting AR shoppers.
  5. **Estimated Incremental Revenue**: Counterfactually modeled revenue uplift beyond control RPS.
  6. **AR Adoption Rate**: Share of total store traffic utilizing the 3D try-on tool.
- **Comparative Conversion Funnel**: Multi-stage funnel visualization (`Session Visits → Feature Engagement → Completed Checkout`) with exact counts and drop-off percentages.
- **Independent Cohort Benchmarking**: Separate, unmixed-axis charts for Conversion Rate (%) and Average Basket Value ($).
- **Client Environment Breakdown**: Granular performance matrix across iOS Mobile, Android Mobile, and Desktop Chrome with best-performing platform callout.
- **Financial Attribution & Revenue Velocity**: Observed gross transaction volume vs counterfactual incremental revenue, revenue share donut chart, Revenue Per Session (RPS) comparisons, and historical revenue trends.
- **AR Engagement Telemetry**: Duration distribution and conversion/abandonment rates across 5 discrete buckets (`0–30s`, `30–60s`, `60–90s`, `90–120s`, `Above 120s`).
- **Statistical Significance Validation**: Two-proportion pooled z-test ($z$-score, $p$-value), 95% Confidence Intervals for both cohorts, sample sizes, and absolute percentage-point difference ($\Delta\text{pp}$).
- **Executive Synthesis & Strategic Recommendations**: Actionable insights across Conversion Efficiency, Basket Valuation, Revenue Attribution, Engagement Performance, Device Performance, and Adoption Opportunities, plus Top 3 Key Takeaways.
- **Methodological Advisory**: Clear observational guidance detailing self-selection bias and recommending randomized controlled A/B testing before vendor contract finalization.
- **Dual Export Functionality**: Download filtered underlying analytics data (CSV) and executive PDF reports with one click.

---

## 3. Strict Colour System

| Role | Colour Hex | Application |
| :--- | :--- | :--- |
| **AR Try-On Cohort** | `#059669` | Green for all AR traces, bars, and metrics |
| **Standard Control Cohort** | `#2563EB` | Blue for all Non-AR traces, bars, and metrics |
| **Dashboard Background** | `#F7F9FC` | Clean enterprise light surface |
| **Card Background** | `#FFFFFF` | Elevated white card containers |
| **Headings & Primary Text** | `#172B4D` | Deep high-contrast charcoal |
| **Secondary & Muted Text**| `#64748B` | Refined slate subtitles and labels |
| **Borders & Dividers** | `#E2E8F0` | Subtle clean borders |
| **Positive / Lift** | `#16A34A` | Upward variance badges and indicators |
| **Advisory / Warning** | `#D97706` | Methodological caution banners |
| **Negative / Drop-off** | `#DC2626` | Abandonment indicators |

---

## 4. Repository Architecture

```
project/
│
├── app.py                      # Enterprise Streamlit analytics dashboard
├── funnel_engine.py            # Analytics computation, statistical testing & PDF engine
├── requirements.txt            # Dependency definitions
├── README.md                   # Complete architectural documentation
│
├── data/
│   ├── generate_session_data.py # Reproducible synthetic telemetry generator
│   └── session_logs.csv        # 300 e-commerce session logs (seed=3)
│
└── tests/
    └── test_team08.py          # Pytest test suite (15 unit tests)
```

---

## 5. Dataset Schema

The telemetry dataset (`data/session_logs.csv`) contains 300 session records generated via fixed random seed (`seed=3`):

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `Session_ID` | String | Unique web visitor session identifier (`SES-1000` to `SES-1299`) |
| `Timestamp` | Datetime | Session datetime timestamp (Oct 1, 2026 – Oct 31, 2026) |
| `Product_Category` | String | Merchandised category (`Apparel`, `Footwear`, `Eyewear`, `Accessories`) |
| `AR_TryOn_Used` | Boolean | True if shopper engaged with virtual try-on; False otherwise |
| `Time_in_AR` | Integer | Active duration in AR mode in seconds (`0` for Non-AR) |
| `Purchase_Made` | Boolean | True if session resulted in a completed checkout |
| `Cart_Value` | Float | Transaction dollar value in USD (`0.0` if abandoned) |
| `Device_Type` | String | Client hardware (`iOS Mobile`, `Android Mobile`, `Desktop Chrome`) |

---

## 6. Analytics Methodology & Mathematical Formulas

### Conversion Rate (CR)
$$\text{CR} = \left( \frac{\text{Purchases}}{\text{Sessions}} \right) \times 100$$

### Conversion Lift %
$$\text{Conversion Lift \%} = \left( \frac{\text{CR}_{\text{AR}} - \text{CR}_{\text{Non-AR}}}{\text{CR}_{\text{Non-AR}}} \right) \times 100$$
*(Safeguard: Returns `0.0` if baseline conversion $\le 0$.)*

### Average Order Value (AOV)
$$\text{AOV} = \frac{\sum \text{Cart Value of Converting Sessions}}{\text{Completed Purchases}}$$

### Revenue Per Session (RPS)
$$\text{RPS} = \frac{\text{Total Cohort Revenue}}{\text{Total Cohort Sessions}}$$

### Estimated Incremental Revenue
$$\text{Incremental Revenue} = \text{Total AR Revenue} - (\text{AR Sessions} \times \text{Non-AR RPS})$$

### Two-Proportion Pooled Z-Test
$$p_{\text{pooled}} = \frac{x_{\text{AR}} + x_{\text{Non-AR}}}{n_{\text{AR}} + n_{\text{Non-AR}}}$$
$$SE = \sqrt{p_{\text{pooled}}(1 - p_{\text{pooled}})\left(\frac{1}{n_{\text{AR}}} + \frac{1}{n_{\text{Non-AR}}}\right)}$$
$$z = \frac{\hat{p}_{\text{AR}} - \hat{p}_{\text{Non-AR}}}{SE}, \quad p\text{-value} = 2 \times (1 - \Phi(|z|))$$

---

## 7. How to Run Locally

### Installation
```bash
pip install -r requirements.txt
```

### Launch Streamlit Dashboard
```bash
streamlit run app.py
```
*Access the dashboard at `http://localhost:8501`.*

### Run Automated Unit Tests
```bash
pytest tests/test_team08.py -v
```

### Run Course Autograder
```bash
python ../../evaluator/autograder.py --team 8
```

---

## 8. Verification Results

### Unit Tests
```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.2.0, pluggy-1.7.0
collected 15 items

tests/test_team08.py::test_csv_schema_and_required_columns PASSED        [  6%]
tests/test_team08.py::test_boolean_data_types PASSED                     [ 13%]
tests/test_team08.py::test_minimum_number_of_sessions PASSED             [ 20%]
tests/test_team08.py::test_ar_vs_non_ar_segmentation PASSED              [ 26%]
tests/test_team08.py::test_conversion_lift_calculation PASSED            [ 33%]
tests/test_team08.py::test_zero_division_protection PASSED               [ 40%]
tests/test_team08.py::test_funnel_metrics_generation PASSED              [ 46%]
tests/test_team08.py::test_aov_calculation PASSED                        [ 53%]
tests/test_team08.py::test_revenue_calculation PASSED                    [ 60%]
tests/test_team08.py::test_statistical_validation PASSED                 [ 66%]
tests/test_team08.py::test_engagement_buckets PASSED                     [ 73%]
tests/test_team08.py::test_pdf_report_generation PASSED                  [ 80%]
tests/test_team08.py::test_empty_dataset_handling PASSED                 [ 86%]
tests/test_team08.py::test_missing_file_handling PASSED                  [ 93%]
tests/test_team08.py::test_missing_required_columns PASSED               [100%]

============================= 15 passed in 2.51s =============================
```

### Autograder Scorecard
```text
# Retail AI Lab Evaluation Scorecard

| Team | Application Name | Raw Score (/100) | Final Marks (/25) | Status |
| :--- | :--- | :---: | :---: | :---: |
| Team 8 | The Virtual Try-On Feedback Loop | 100/100 | 25.0/25 | PASS |

| Evaluation Pillar | Score | Max Points | Status |
| :--- | :---: | :---: | :--- |
| 1. Repository Architecture | 20 | 20 | [PASS] |
| 2. Algorithmic Logic and Unit Tests | 30 | 30 | [PASS] |
| 3. Interactive UI and Dashboard | 20 | 20 | [PASS] |
| 4. Data Quality and Schema | 15 | 15 | [PASS] |
| 5. Prompt Documentation | 15 | 15 | [PASS] |
```
