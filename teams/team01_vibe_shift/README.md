# 🔮 Team 1: The "Vibe-Shift" Trend Forecaster (Demand Forecasting)

## 👥 Team Information
- **Track**: Demand Forecasting & Cultural Signal Analytics
- **Application Name**: The "Vibe-Shift" Trend Forecaster
- **Team Members**:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## 🎯 The Core Problem Solved
Traditional retail demand forecasting relies solely on historical sales, missing fast-moving social media trends and cultural micro-surges. This leads to stockouts of trending viral items and overstock of rapidly fading fads. 

**The Solution**: This application predicts upcoming demand surges by combining historical sales velocity with external cultural signals (TikTok/Instagram sentiment scores and trend momentum), enabling boutique buyers to order inventory before a trend peaks.

## 🛍️ Target End Customer
- **Primary**: Retail Buyers and Inventory Planners at boutique clothing stores.
- **Secondary**: E-commerce merchandisers managing short product lifecycles.

---

## 📊 Technical & Data Requirements
1. **Data**: A mock CSV dataset containing columns for:
   - `Date` (YYYY-MM-DD)
   - `Item_Category` (e.g., Streetwear Cargo Pants, Y2K Denim Jackets, Cottagecore Maxi Dresses)
   - `Historical_Sales_Volume` (daily units sold)
   - `Social_Media_Trend_Score` (0–100 normalized cultural momentum score)
2. **Logic (`forecaster.py`)**:
   - `load_trend_data(filepath)`
   - `forecast_demand(df, category, forecast_days, social_weight)`: Implements predictive time-series projection combining moving average velocity with social score acceleration and confidence bands.
3. **UI / Dashboard (`app.py`)**:
   - Streamlit dashboard with category dropdown and forecast horizon slider.
   - Interactive Plotly line charts displaying historical sales vs projected 30-day demand with 95% confidence intervals.
   - "Mood Board" aesthetic cards showcasing visual signals of the forecasted trend.

---

## 🤖 Vibe-Coding Execution Strategy & Prompt Log
*Students used the following curated AI prompts to build this application:*

### Prompt 1: Synthetic Seasonal Data Generation
> *"Write a Python script using pandas and numpy that generates a realistic CSV dataset with columns: Date, Item_Category, Historical_Sales_Volume, and Social_Media_Trend_Score. Simulate 180 days across 5 apparel categories with weekly seasonality and viral social media spikes."*

### Prompt 2: Trend Forecasting Algorithm
> *"Write a Python function `forecast_demand` that takes historical sales and a social media trend score. Fit a trend line on recent sales, calculate day-of-week multipliers, and amplify the 30-day projection based on social media momentum with upper and lower confidence intervals."*

### Prompt 3: Streamlit & Plotly Dashboard
> *"Create a Streamlit dashboard with a dark theme. Add a sidebar to select categories and forecast horizon. Display 4 metric cards (Social Trend Score, 30-day Projected Demand, Growth Shift, Peak Date). Plot historical sales and the 30-day forecast with a shaded confidence ribbon using Plotly graph_objects. Add a visual mood board gallery at the bottom."*

---

## 🚀 How to Run Locally

```bash
# 1. Activate your virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
streamlit run app.py
```

## 🧪 How to Run Automated Unit Tests

```bash
# Run pytest for Team 1
pytest tests/test_team01.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 1
```

## 🏆 Evaluation Rubric (100 Points -> 25 Marks)
- **Architecture (20 pts)**: Directory structure, `app.py`, `forecaster.py`, clean requirements.
- **Logic & Unit Tests (30 pts)**: Accurate time-series forecasting, confidence bounds, test suite passes.
- **Interactive UI (20 pts)**: Plotly demand visualization, metric cards, visual mood board.
- **Data Quality (15 pts)**: 900+ rows of realistic seasonal data with social trend scores.
- **Documentation (15 pts)**: Complete prompt log, customer definition, run instructions.
