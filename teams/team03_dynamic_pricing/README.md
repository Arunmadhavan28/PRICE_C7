# Team 3: The Dynamic Pricing Engine (Pricing Analytics)

## Team Information
- Track: Pricing Analytics and Margin Optimization
- Application Name: The Dynamic Pricing Engine
- Team Members:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## The Core Problem Solved
Static retail pricing fails to capture maximum profit during high-demand surges and fails to clear aging or perishable inventory during slow business hours. Cafes and boutique retailers leave margin on the table by charging identical prices regardless of weather, time, or stock.

The Solution: A rule-based dynamic pricing engine that computes real-time price modifiers based on environmental inputs (time of day, ambient weather, current inventory runway) with strict cost-basis guardrails to prevent margin erosion.

## Target End Customer
- Primary: Store Managers and Revenue Managers at local retail cafes, bakeries, or boutique shops.
- Secondary: Multi-location franchise operators aiming to maximize intraday profitability.

---

## Technical and Data Requirements
1. Data: data/inventory.json containing items with:
   - Item (Product Name)
   - Category (Beverages, Pastry, Food)
   - Base_Price (Standard retail price in USD)
   - Cost_Price (Absolute cost basis floor)
   - Current_Stock (Available unit count)
2. Logic (pricing_engine.py):
   - load_inventory(filepath)
   - apply_pricing_rules(item_dict, hour_of_day, weather, current_stock):
     - Clearance Rule: If Time > 17:00 and Stock > 20 -> -15% discount.
     - Rain Surge: If Weather == "Raining" and Item is Hot Beverage -> +10% surge.
     - Heatwave Surge: If Weather == "Heatwave" and Item is Cold/Iced Beverage -> +15% surge.
     - Scarcity Premium: If Stock < 5 -> +10% demand premium.
   - calculate_dynamic_price(...): Applies modifiers and strictly enforces Dynamic_Price >= Cost_Price.
3. UI / Dashboard (app.py):
   - Streamlit dashboard with sliders for time of day (0-23h), weather dropdown, and inventory multipliers.
   - Live-updating Price Board displaying Base Price, Dynamic Price, % Shift, and triggered rule badges.
   - Aggregate metric cards for revenue impact, margin pool, and discounted volume.

---

## Execution Strategy and Prompt Log

### Prompt 1: Rule-Based Pricing Engine with Guardrails
> "Write a Python pricing function that calculates dynamic prices for retail cafe items. It must take an item dict, hour of day, weather, and stock. Implement rules: if hour > 17 and stock > 20, reduce price by 15%; if weather is 'Raining' and item contains 'Hot Coffee', increase price by 10%. Crucially, add a guardrail that ensures the calculated price never falls below Cost_Price."

### Prompt 2: Interactive Streamlit Price Board
> "Build a Streamlit dashboard with UI sliders for Time of Day (0-23) and an inventory scale factor, plus a dropdown for weather conditions. Display a live-updating table showing each item's Base Price, New Price, % Change, and badges showing exactly which pricing rules fired."

### Prompt 3: Financial Metric Cards and Margin Bar Chart
> "Add 4 top-level metric cards in Streamlit showing Average Price Adjustment, Count of Discounted Items, Count of Surged Items, and Total Protected Margin Pool. Below the table, include a bar chart comparing Base Price vs Dynamic Price."

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
# Run pytest for Team 3
pytest tests/test_team03.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 3
```

## Evaluation Rubric (100 Points to 25 Marks)
- Architecture (20 pts): Directory structure, app.py, pricing_engine.py, clean requirements.
- Logic and Unit Tests (30 pts): Complete rule-based gates, weather surges, cost-price floor protection.
- Interactive UI (20 pts): Interactive sliders, weather selectbox, live-updating price board, metrics.
- Data Quality (15 pts): Complete inventory JSON with valid Base_Price, Cost_Price, and Stock.
- Documentation (15 pts): Complete prompt log, customer definition, run instructions.
