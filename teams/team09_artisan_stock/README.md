# 📦 Team 9: The Artisan Safety-Stock Planner (Inventory Optimization)

## 👥 Team Information
- **Track**: Inventory Optimization & Supply Chain Planning
- **Application Name**: The Artisan Safety-Stock Planner
- **Team Members**:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## 🎯 The Core Problem Solved
Independent retail artisans and boutique craft makers track raw production materials manually on scratch paper or fragmented spreadsheets. Consequently, they often realize too late—right before a peak holiday craft market or wholesale pop-up—that they lack the essential raw materials (wax, leather, wicks, brass hardware) required to fulfill production spikes, while supplier lead times can exceed two weeks.

**The Solution**: A visual, color-coded Kanban status-tracker that calculates daily material runway against supplier lead times using standard safety stock equations ($\text{ROP} = (\text{Lead Time} \times \text{Daily Burn}) + \text{Safety Stock}$), immediately turning cards red when runway is endangered and generating a clean, one-click purchase order for suppliers.

## 🛍️ Target End Customer
- **Primary**: Independent Artisans, Makers, Handcrafted Product Creators, and Boutique Owners.
- **Secondary**: Small-batch manufacturers managing variable raw material lead times.

---

## 📊 Technical & Data Requirements
1. **Data**: `data/artisan_materials.csv` containing:
   - `Material_Name` (e.g. Soy Wax Flakes, Brass Hooks, Veg-Tan Leather)
   - `Category` (Candles, Jewelry, Textiles, Packaging)
   - `Current_Level` (Current raw units on hand)
   - `Lead_Time_Days` (Vendor shipping & fulfillment time in days)
   - `Daily_Burn_Rate` (Units consumed per day)
   - `Safety_Stock` (Buffer inventory units)
   - `Upcoming_Events` (Holiday fairs, pop-ups)
   - `Supplier_Contact`, `Unit_Cost`
2. **Logic (`stock_engine.py`)**:
   - `load_materials_data(filepath)`
   - `calculate_safety_stock(lead_time_days, daily_burn_rate, safety_stock_units)`: Computes Reorder Point: $\text{ROP} = (\text{Lead Time} \times \text{Daily Burn}) + \text{Safety Stock}$.
   - `calculate_runway_days(current_level, daily_burn_rate)`: $\text{Runway} = \frac{\text{Current}}{\text{Burn Rate}}$.
   - `evaluate_material_status(row)`: Classifies into `CRITICAL` (Runway $\le$ Lead Time), `WARNING` (Current $\le$ ROP), or `HEALTHY`.
   - `generate_purchase_order(items_to_reorder)`: Formats consolidated PO text with quantities, unit costs, and grand totals.
3. **UI / Dashboard (`app.py`)**:
   - Visual Kanban card grid with color-coded left borders (Green, Yellow, Red).
   - Dynamic progress bars (`st.progress`) depicting runway days remaining relative to supplier lead times.
   - High-level metric cards: Total Materials, Critical Stockout Alerts, Warning Items, Replenishment Capital Needed.
   - One-click "⚡ Generate Purchase Order for Vendors" button with interactive text preview and `.txt` file download.

---

## 🤖 Vibe-Coding Execution Strategy & Prompt Log
*Students used the following curated AI prompts to build this tracker:*

### Prompt 1: Safety Stock & Runway Math
> *"Write a Python script that calculates the inventory runway days and Reorder Point (ROP = Lead Time * Daily Burn Rate + Safety Stock) for artisan materials. Return a status: 'CRITICAL' if runway <= lead time, 'WARNING' if current <= ROP, and 'HEALTHY' otherwise."*

### Prompt 2: Purchase Order Formatter
> *"Create a function `generate_purchase_order` that takes all materials in CRITICAL or WARNING status, calculates the units needed to restore a 30-day runway, and formats a clean, itemized text purchase order with PO number, date, itemized table, and grand total capital required."*

### Prompt 3: Visual Kanban Cards in Streamlit
> *"Build a Streamlit dashboard that displays the materials in a 3-column card grid. Use custom CSS cards that turn green, yellow, or red based on status. Show progress bars for runway health, and provide a prominent button at the bottom to generate and download the purchase order file."*

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
# Run pytest for Team 9
pytest tests/test_team09.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 9
```

## 🏆 Evaluation Rubric (100 Points -> 25 Marks)
- **Architecture (20 pts)**: Directory structure, `app.py`, `stock_engine.py`, clean requirements.
- **Logic & Unit Tests (30 pts)**: Accurate ROP formula, runway calculation, status thresholds, test suite passes.
- **Interactive UI (20 pts)**: Visual kanban cards, progress bars, metric cards, PO download button.
- **Data Quality (15 pts)**: Complete materials dataset with lead times, burn rates, and supplier contacts.
- **Documentation (15 pts)**: Complete prompt log, customer definition, run instructions.
