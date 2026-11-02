# 🏷️ Team 6: The "Drop Culture" Markdown Optimizer (Clearance Analytics)

## 👥 Team Information
- **Track**: Clearance Analytics & Sell-Through Optimization
- **Application Name**: The "Drop Culture" Markdown Optimizer
- **Team Members**:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## 🎯 The Core Problem Solved
Marking down underperforming inventory too early needlessly sacrifices healthy gross margin dollars. Conversely, marking down slow-moving stock too late results in dead stock write-offs and congested warehouse shelves. Retail merchandisers struggle to calculate the precise mathematical discount needed to clear stock at target velocity.

**The Solution**: An algorithmic calculation engine that monitors actual vs target sell-through velocity, flags lagging SKUs, and calculates the optimal minimum markdown tier while strictly guaranteeing that the clearance price never falls below the item's cost basis.

## 🛍️ Target End Customer
- **Primary**: Retail Merchandisers, Inventory Planners, and Clearance Strategists.
- **Secondary**: Fashion brand operations directors managing seasonal liquidation.

---

## 📊 Technical & Data Requirements
1. **Data**: `data/inventory_aging.csv` tracking:
   - `Item_SKU` (e.g. `SKU-FL-101`)
   - `Item_Name`, `Category`
   - `Days_on_Shelf` (Aging count in days)
   - `Target_Sell_Through_Rate` (Expected velocity, e.g. 0.80)
   - `Actual_Sell_Through_Rate` (Observed velocity, e.g. 0.35)
   - `Retail_Price`
   - `Cost_Basis` (Absolute floor below which company loses money)
   - `Current_Units`
2. **Logic (`optimizer.py`)**:
   - `load_aging_data(filepath)`
   - `identify_at_risk_items(df)`: Flags items where `Actual < Target`.
   - `calculate_recommended_discount(row)`:
     - Tier 1: > 60 days on shelf -> 30% markdown
     - Tier 2: > 30 days on shelf -> 15% markdown
     - Tier 3: > 15 days on shelf -> 5% markdown
     - *Hard Barrier*: Clearance Price $\ge$ Cost_Basis (cap discount at `(Retail - Cost) / Retail`).
   - `project_profit_recovery(df)`: Computes liberated capital, total margin preserved, and dead-stock loss prevented.
3. **UI / Dashboard (`app.py`)**:
   - Streamlit interface with color-coded risk table (red for critical, yellow for warning).
   - High-level metric cards: SKUs at Risk, Dead Stock Risk Capital, Projected Clearance Revenue, Projected Profit Recovery.
   - Plotly bar chart comparing Retail Price vs Clearance Price vs Cost Basis Floor.
   - One-click CSV export for POS clearance batch upload.

---

## 🤖 Vibe-Coding Execution Strategy & Prompt Log
*Students used the following curated AI prompts to build this engine:*

### Prompt 1: Sell-Through Filtering & Cost Barrier Logic
> *"Write a Python script using pandas that filters a DataFrame of retail inventory aging. Flag items where Actual_Sell_Through_Rate is lagging behind Target_Sell_Through_Rate. Apply tiered discount logic: 10% off for 15+ days, 15% off for 30+ days, 30% off for 60+ days. Most importantly, ensure the clearance price never falls below Cost_Basis."*

### Prompt 2: Profit Recovery Projections
> *"Create a function `project_profit_recovery` that calculates the total capital at risk of dead-stock loss, the projected revenue if cleared at the recommended discount, and the preserved gross margin dollars across all at-risk SKUs."*

### Prompt 3: Streamlit Clearance Control Center
> *"Build a Streamlit dashboard with 4 metric cards at the top. Style the DataFrame so that 'CRITICAL AT-RISK' items are highlighted in red. Add a Plotly grouped bar chart comparing Retail Price, Clearance Price, and Cost Basis Floor, and provide a download button to export the approved clearance file."*

---

## 🚀 How to Run Locally

```bash
# 1. Activate your virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
streamlit run app.py
```

## 🧪 How to Run Automated Unit Tests

```bash
# Run pytest for Team 6
pytest tests/test_team06.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 6
```

## 🏆 Evaluation Rubric (100 Points -> 25 Marks)
- **Architecture (20 pts)**: Directory structure, `app.py`, `optimizer.py`, clean requirements.
- **Logic & Unit Tests (30 pts)**: Accurate sell-through lag detection, tiered discount rule, cost floor guarantee.
- **Interactive UI (20 pts)**: Color-coded data table, metrics, Plotly chart, CSV download button.
- **Data Quality (15 pts)**: Realistic aging CSV with SKU, days on shelf, sell-through rates, cost basis.
- **Documentation (15 pts)**: Complete prompt log, customer definition, run instructions.
