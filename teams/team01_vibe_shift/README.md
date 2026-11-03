# Team 1: The 'Vibe-Shift' Trend Forecaster (Demand Forecasting)

## Team Information
- Track: Demand Forecasting and Cultural Signal Analytics
- Application Name: The 'Vibe-Shift' Trend Forecaster
- Team Members:
  - Lead Developer / ML Engineer: Lakshana G S ([@lakshana-gs](https://github.com/lakshana-gs))

---

## The Core Problem Solved
Traditional retail demand forecasting relies purely on lagging historical sales numbers, completely missing fast-moving viral social trends and cultural micro-surges. This results in:
1. Catastrophic stockouts of trending viral apparel items before peak margin can be captured.
2. Costly overstocking of rapidly fading fashion fads that require steep markdown liquidations.

**The Solution:** This application predicts upcoming 7-to-60 day demand surges by blending historical sales velocity (rolling linear regression) with external cultural trend signals (social media sentiment score velocity and acceleration multipliers), weekly seasonality factors, and broadening confidence ribbons. It equips boutique retail buyers and inventory planners with actionable reorder timing, safety buffer quantities, and risk volatility metrics before a trend peaks.

## Target End Customer
- **Primary:** Boutique Retail Clothing Buyers and Inventory Planners seeking pre-surge inventory replenishment recommendations.
- **Secondary:** E-Commerce Fashion Merchandisers managing short trend lifecycles and micro-capsule collections.

---

## Algorithmic Architecture and Mathematical Formulation

The core forecasting engine in `forecaster.py` computes projected daily demand as:

$$\text{ProjectedDemand}_t = \max\left(0, \; \text{BaseTrend}_t \times \text{CulturalLift}_t \times \text{SeasonalityFactor}_{\text{DoW}}\right)$$

Where:
1. **Base Trend ($\text{BaseTrend}_t$):**
   $$\text{BaseTrend}_t = \max\left(1.0, \; \text{slope} \cdot (W + t) + \text{intercept}\right)$$
   Fitted via first-degree polynomial regression on the recent sales window ($W = \min(30, n)$).
2. **Cultural Lift ($\text{CulturalLift}_t$):**
   $$\text{SocialMomentum} = \left(\frac{\text{Score}_{\text{current}}}{50} - 1.0\right) \times w_{\text{social}} + (\text{slope}_{\text{social}} \times 0.02)$$
   $$\text{CulturalLift}_t = \max\left(0.2, \; 1.0 + \text{SocialMomentum} \cdot (1.0 + 0.015 \cdot t \cdot \alpha)\right)$$
   where $\alpha$ is the trend acceleration multiplier and $w_{\text{social}}$ is the cultural signal weight.
3. **Weekly Seasonality ($\text{SeasonalityFactor}_{\text{DoW}}$):**
   $$\text{SeasonalityFactor}_{\text{DoW}} = \frac{\overline{\text{Sales}}_{\text{DoW}}}{\overline{\text{Sales}}_{\text{overall}}}$$
4. **95% Confidence Bounds:**
   $$\text{Uncertainty}_t = \sigma_{\text{residuals}} \cdot \sqrt{1 + \frac{t}{10}}$$
   $$\text{LowerBound}_t = \max(0.0, \; \text{ProjectedDemand}_t - 1.96 \cdot \text{Uncertainty}_t)$$
   $$\text{UpperBound}_t = \max(\text{ProjectedDemand}_t, \; \text{ProjectedDemand}_t + 1.96 \cdot \text{Uncertainty}_t)$$
   Strictly enforced invariant: $0 \le \text{LowerBound}_t \le \text{ProjectedDemand}_t \le \text{UpperBound}_t$.
5. **Buyer Replenishment Analytics:**
   $$\text{SafetyStock} = \lceil 1.65 \cdot \sigma_{\text{residuals}} \cdot \sqrt{\text{LeadTime}_{\text{days}}} \rceil$$
   $$\text{ReorderPoint} = \lceil \overline{\text{ProjectedDaily}} \cdot \text{LeadTime}_{\text{days}} + \text{SafetyStock} \rceil$$

---

## Technical and Data Requirements
1. **Dataset (`data/trend_sales_data.csv`):** 900 records across 5 apparel categories over 180 days:
   - `Date` (YYYY-MM-DD format)
   - `Item_Category` (e.g. Streetwear Cargo Pants, Y2K Denim Jackets, Cottagecore Maxi Dresses, Minimalist Linen Shirts, Cyberpunk Metallic Vests)
   - `Historical_Sales_Volume` (daily units sold)
   - `Social_Media_Trend_Score` (0-100 cultural momentum index)
2. **Core Logic (`forecaster.py`):**
   - `load_trend_data(filepath_or_buffer)`: Robust CSV validator supporting file paths and uploaded buffers.
   - `forecast_demand(df, category, forecast_days, social_weight, growth_acceleration)`: Hardened time-series projection with buyer procurement metrics.
3. **Interactive UI (`app.py`):**
   - Streamlit dashboard with category dropdown, forecast horizon slider, sensitivity sliders, and custom CSV uploader.
   - Dual-axis interactive Plotly chart overlaying unit sales with the cultural social momentum wave.
   - What-If scenario simulation slider for viral micro-surges.
   - Tabbed layout: Forecast Trajectory, Buyer Replenishment Plan, Visual Mood Board (with SVG badges), and Seasonality Diagnostics.
   - CSV export download button for buyer purchase orders.


---

## Execution Strategy and Prompt Log

### Phase 1: Synthetic Seasonal Data Generation
> **Prompt:** "Write a Python script using pandas and numpy that generates a realistic CSV dataset with columns: Date, Item_Category, Historical_Sales_Volume, and Social_Media_Trend_Score. Simulate 180 days across 5 apparel categories with weekly seasonality, viral social media bursts, and trend decay patterns. Ensure non-empty data without nulls."

### Phase 2: Core Trend Forecasting Algorithm & Mathematical Invariants
> **Prompt:** "Write a Python function `forecast_demand` that blends historical sales velocity with external social media trend momentum. Implement a linear trend fit on recent sales, calculate weekly day-of-week multipliers, and amplify projections based on cultural score velocity. Broaden confidence intervals over the forecast horizon using standard error ($1.96 \cdot \sigma \sqrt{1 + t/10}$). Enforce strict monotonicity invariants: $0 \le \text{Lower\_Bound} \le \text{Forecast\_Demand} \le \text{Upper\_Bound}$. Compute safety stock and reorder point recommendations for buyers."

### Phase 3: Interactive Streamlit Dashboard with Dual-Axis Cultural Overlay
> **Prompt:** "Build a Streamlit web application (`app.py`) for boutique apparel buyers. Create a dual-axis interactive Plotly chart showing historical sales and projected demand on the primary y-axis, and social media trend score on the secondary y-axis. Structure the interface into four tabs: 1) Demand Trajectory with What-If Scenario simulation slider, 2) Buyer Replenishment Plan with procurement recommendations and CSV download button, 3) Cultural Aesthetic Mood Board with visual SVG badges rendered via st.image, and 4) Seasonality Diagnostics with day-of-week breakdown."

### Phase 4: Defensive Error Handling & Edge-Case Test Suite
> **Prompt:** "Harden `forecaster.py` and write comprehensive pytest unit tests in `tests/test_team01.py`. Support both file path strings and in-memory IO buffers in `load_trend_data`. Add defensive checks for zero or negative forecast days, missing columns, corrupted dates, single-item historical slices, and zero-variance constant sales. Verify all 10 buyer metric keys are populated."

### Phase 5: Autonomous Autograder & CI/CD Verification
> **Prompt:** "Run `python evaluator/autograder.py --team 1` and `pytest teams/team01_vibe_shift/tests/test_team01.py -v`. Verify that all 5 pillars achieve full points (100/100 raw score, 25.0/25 academic marks). Ensure complete file isolation inside `teams/team01_vibe_shift/`."


---

## How to Run Locally

```bash
# 1. Activate your virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
streamlit run app.py
```

## How to Run Automated Unit Tests

```bash
# Run pytest for Team 1
pytest tests/test_team01.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 1
```

## Evaluation Rubric (100 Points to 25 Marks)
- Architecture (20 pts): Directory structure, app.py, forecaster.py, clean requirements.
- Logic and Unit Tests (30 pts): Accurate time-series forecasting, confidence bounds, test suite passes.
- Interactive UI (20 pts): Plotly demand visualization, metric cards, visual mood board.
- Data Quality (15 pts): 900+ rows of realistic seasonal data with social trend scores.
- Documentation (15 pts): Complete prompt log, customer definition, run instructions.
