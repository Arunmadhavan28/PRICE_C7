# Team 8: The Virtual Try-On Feedback Loop (AR/VR Analytics)

## Team Information
- Track: AR/VR Analytics and Funnel Conversion Optimization
- Application Name: The Virtual Try-On Feedback Loop
- Team Members:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## The Core Problem Solved
E-commerce fashion retailers invest heavily in developing Augmented Reality (AR) virtual try-on features (3D avatar fitting, eyewear, footwear tracking). However, marketing and product leaders rarely possess visibility into whether AR features genuinely increase conversion or merely serve as novelty features.

The Solution: An analytics application that ingests session-level user telemetry, computes comparative conversion funnels (AR Users vs Standard Control), and isolates the exact conversion lift and basket value created by virtual try-on engagement.

## Target End Customer
- Primary: E-commerce Product Managers, Digital Marketers, and Growth Leads.
- Secondary: Retail Tech Executives evaluating 3D/AR software vendor contracts.

---

## Technical and Data Requirements
1. Data: data/session_logs.csv containing:
   - Session_ID (Unique web session identifier)
   - AR_TryOn_Used (Boolean flag)
   - Time_in_AR (Duration in seconds spent in AR mode)
   - Purchase_Made (Boolean checkout flag)
   - Cart_Value (USD value of completed transaction)
   - Device_Type (iOS, Android, Desktop)
2. Logic (funnel_engine.py):
   - load_session_logs(filepath)
   - segment_ar_vs_non_ar(df)
   - calculate_conversion_lift(cr_ar, cr_non_ar): Lift = ((CR_AR - CR_NonAR) / CR_NonAR) * 100%.
   - calculate_funnel_metrics(df): Computes session counts, conversion rates, average order value (AOV), and incremental revenue.
3. UI / Dashboard (app.py):
   - Streamlit dashboard with Plotly Funnel visualization (go.Funnel).
   - High-level metric cards: AR Conversion Lift %, AR Conversion Rate, Non-AR Conversion Rate, AR Basket Size.
   - Comparative bar chart comparing conversion rate and average cart value.
   - Interactive slider filtering sessions by minimum time spent in AR.

---

## Execution Strategy and Prompt Log

### Prompt 1: Synthetic Telemetry Log Generation
> "Write a Python script using pandas and numpy that generates synthetic web-traffic session logs for an e-commerce store with an AR try-on feature. Include columns: Session_ID, AR_TryOn_Used (bool), Time_in_AR (seconds), Purchase_Made (bool), Cart_Value, and Device_Type. Make AR users convert at ~38% and non-AR at ~18%."

### Prompt 2: Funnel Metrics and Conversion Lift
> "Write a Python analytics function calculate_funnel_metrics that groups sessions by AR_TryOn_Used, computes conversion rates for each cohort, and calculates the percentage conversion lift with safeguards against zero division."

### Prompt 3: Plotly Funnel Chart and Dashboard
> "Create a Streamlit dashboard with 4 metric cards at the top. On the left, render a comparative conversion funnel using Plotly go.Funnel showing drop-off from Total Sessions to Purchases. On the right, display a grouped bar chart comparing conversion rate and average basket size between AR and Non-AR users."

---

## How to Run Locally

```bash
# 1. Activate your virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
streamlit run app.py
```

## How to Run Automated Unit Tests

```bash
# Run pytest for Team 8
pytest tests/test_team08.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 8
```

## Evaluation Rubric (100 Points to 25 Marks)
- Architecture (20 pts): Directory structure, app.py, funnel_engine.py, clean requirements.
- Logic and Unit Tests (30 pts): Accurate conversion rate and lift formula, zero-division guard, test suite passes.
- Interactive UI (20 pts): Plotly funnel chart, grouped bar chart, cohort filter sliders.
- Data Quality (15 pts): Complete session logs with realistic AR interaction telemetry.
- Documentation (15 pts): Complete prompt log, customer definition, run instructions.
