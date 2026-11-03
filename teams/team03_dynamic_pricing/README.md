# Team 3: The 'Happy Hour' Dynamic Pricing Engine (Pricing Analytics)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Visualization-Plotly-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/pytest-15%2F15%20passed-brightgreen.svg)](tests/test_team03.py)
[![Evaluation](https://img.shields.io/badge/Autograder-100%2F100-success.svg)](../../evaluator/autograder.py)

---

## 1. Project Overview & Team Information

- **Track**: Pricing Analytics and Margin Optimization
- **Application Name**: The 'Happy Hour' Dynamic Pricing Engine
- **Target Category**: Retail AI Lab (PRICE_C7) — Team 3
- **Team Members**:
  - Lead Engineer & Pricing Analyst: Hariharan R (@hariwhatever)
  - Core Contributor: Pricing Strategy & AI Systems Developer

---

## 2. Business Problem & Opportunity

Static retail pricing fails to capture maximum profit during intraday demand surges and fails to clear aging or perishable inventory during slow business hours. Local cafes, artisan bakeries, and boutique retailers leave significant operating margin on the table by charging uniform prices regardless of:
1. **Time of day** (e.g., peak morning commute vs late afternoon slowdown).
2. **Ambient weather conditions** (e.g., cold rain driving hot beverage cravings; heatwaves spiking iced beverage velocity).
3. **Inventory shelf runway** (e.g., unsold perishable pastries approaching closing hours).

### The Solution
The **'Happy Hour' Dynamic Pricing Engine** introduces rule-based, deterministic real-time price modifiers driven by ambient environment and inventory data. Crucially, the engine incorporates an impenetrable **cost-basis floor guardrail** (`Dynamic_Price >= Cost_Price`), ensuring inventory clearance never translates into margin-dilutive or negative-profit transactions.

---

## 3. Target Customer Persona

### Primary Persona: Store & Revenue Manager (Cafe & Boutique Retail)
- **Role**: Store Operations & Revenue Manager at independent specialty cafes and quick-service bakeries.
- **Key Responsibilities**: Maximizing daily gross margin, minimizing end-of-day pastry and dairy write-offs, maintaining customer loyalty and fair pricing perception.
- **Pain Points**:
  - High end-of-day perishable waste (15–25% of fresh croissants and artisan bread discarded daily).
  - Uncaptured surge demand on rainy mornings when foot traffic is willing to pay a premium for warm comfort beverages.
  - Manual, clumsy discount sticker tagging that confuses staff and erodes brand value.
- **How This Engine Helps**: Automates menu price recommendations on electronic price tags or point-of-sale displays while guaranteeing gross margins remain strictly positive.

### Secondary Persona: Multi-Unit Franchise Operator
- **Role**: Regional Operations Director managing 5–20 retail coffee kiosks.
- **Goal**: Centrally coordinate automated happy hour clearance and weather-responsive menu adjustments without risking below-cost promotions.

---

## 4. Pricing Methodology & Rules

The dynamic pricing engine applies five transparent, deterministic logic gates:

| # | Pricing Gate | Trigger Condition | Modifier | Strategic Rationale |
|---|---|---|:---:|---|
| 1 | **Happy Hour Clearance** | $\text{Hour} \ge 17$ (5 PM) **AND** $\text{Stock} > 20$ | **$-15\%$** | Clears surplus perishable stock before store closing; prevents write-offs. |
| 2 | **Rain Warmth Surge** | $\text{Weather} = \text{"Raining"}$ **AND** Item $\in \{\text{Hot}, \text{Coffee}, \text{Chai}, \text{Espresso}\}$ | **$+10\%$** | Captures willingness-to-pay for comfort beverages during adverse rain. |
| 3 | **Heatwave Refreshment Surge** | $\text{Weather} = \text{"Heatwave"}$ **AND** Item $\in \{\text{Cold}, \text{Iced}, \text{Nitro}, \text{Matcha}\}$ | **$+15\%$** | Capitalizes on high hydration demand during hot weather. |
| 4 | **Scarcity Demand Premium** | $0 < \text{Stock} < 5$ units | **$+10\%$** | Captures scarcity value as inventory nears exhaustion. |
| 5 | **Morning Commute Rush** | $7 \le \text{Hour} \le 9$ (7–9 AM) **AND** Category $= \text{"Beverages"}$ | **$+5\%$** | Captures peak morning commuter demand velocity. |

If no rules are triggered, the engine assigns the **Standard Base Rate ($0\%$)**. When multiple rules trigger simultaneously (e.g., Rain Surge during Happy Hour), modifiers stack additively.

---

## 5. Mathematical Formulation

Let:
- $P_{\text{base}} \in \mathbb{R}^+$ be the standard retail price.
- $P_{\text{cost}} \in \mathbb{R}^+$ be the absolute cost basis floor ($P_{\text{cost}} \le P_{\text{base}}$).
- $S \in \mathbb{Z}$ be the current inventory stock level.
- $H \in [0, 23]$ be the hour of the day.
- $W$ be the ambient weather string.
- $M_{\text{max}} = 2.0$ be the maximum surge multiplier (surge ceiling).

### Net Modifier Formulation
$$\Delta_{\text{net}} = \sum_{k=1}^{5} m_k$$

Where:
$$m_1 = -0.15 \quad \text{if } H \ge 17 \land S > 20 \text{, else } 0$$
$$m_2 = +0.10 \quad \text{if } \text{lower}(W) = \text{"raining"} \land \text{is\_hot}(Item) \text{, else } 0$$
$$m_3 = +0.15 \quad \text{if } \text{lower}(W) = \text{"heatwave"} \land \text{is\_cold}(Item) \text{, else } 0$$
$$m_4 = +0.10 \quad \text{if } 0 < S < 5 \text{, else } 0$$
$$m_5 = +0.05 \quad \text{if } 7 \le H \le 9 \land \text{Category} = \text{"Beverages"} \text{, else } 0$$

### Raw Selling Price
$$P_{\text{raw}} = \min\left(P_{\text{base}} \cdot (1 + \Delta_{\text{net}}), \; P_{\text{base}} \cdot M_{\text{max}}\right)$$

### Cost-Basis Floor Guardrail Enforcement
$$P_{\text{final}} = \max\left(P_{\text{cost}}, \; P_{\text{raw}}\right)$$

### Financial Margin Metrics
$$\text{Margin}_{\$} = P_{\text{final}} - P_{\text{cost}}$$
$$\text{Margin}_{\%} = \begin{cases} \left(\frac{\text{Margin}_{\$}}{P_{\text{final}}}\right) \times 100 & \text{if } P_{\text{final}} > 0 \\ 0.0 & \text{otherwise} \end{cases}$$
$$\Delta_{\text{price}\%} = \begin{cases} \left(\frac{P_{\text{final}} - P_{\text{base}}}{P_{\text{base}}}\right) \times 100 & \text{if } P_{\text{base}} > 0 \\ 0.0 & \text{otherwise} \end{cases}$$

---

## 6. Safeguards and Guardrails

1. **Absolute Cost Floor Guarantee**:
   The engine strictly enforces $P_{\text{final}} \ge P_{\text{cost}}$. If aggressive clearance would push a price below the item's direct cost, the price is clamped directly at $P_{\text{cost}}$ and the audit log records: `Cost Basis Floor Guardrail Activated`.
2. **Anti-Gouging Ceiling Guardrail**:
   Surges cannot exceed $2.0 \times P_{\text{base}}$ (+100% price surge cap), protecting consumer trust and preventing algorithm runaways.
3. **Zero & Negative Stock Safety**:
   If stock $S \le 0$, the item is considered depleted. It will **not** trigger scarcity premiums ($0 < S < 5$) or surplus clearance ($S > 20$).
4. **Input Sanitization**:
   Handles `None`, empty dicts, missing keys, malformed numeric strings, and out-of-range hours gracefully without crashing.
5. **Full Determinism**:
   Calculations are pure functions with zero random seeds or stochastic drift. Identical inputs always yield identical pricing and margin outputs.

---

## 7. Dataset Schema & Description

The catalog is stored at `data/inventory.json` and consists of 8 representative items spanning Beverages, Pastry, and Food:

| Column / Key | Data Type | Description | Sample Value |
|---|:---:|---|---|
| `Item` | `string` | Unique product name including temperature descriptors | `"Hot Coffee (Artisanal Drip)"` |
| `Category` | `string` | Merchandising department | `"Beverages"` |
| `Base_Price` | `float` | Standard baseline retail price in USD | `4.50` |
| `Cost_Price` | `float` | Absolute unit cost basis floor in USD | `1.20` |
| `Current_Stock` | `integer` | Current available inventory on shelf | `35` |

---

## 8. Installation & Setup Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### Linux / macOS Setup
```bash
git clone https://github.com/hariwhatever/PRICE_C7.git
cd PRICE_C7

python3 -m venv venv
source venv/bin/activate

pip install -r teams/team03_dynamic_pricing/requirements.txt
```

### Windows PowerShell Setup
```powershell
# Clone and enter directory
git clone https://github.com/hariwhatever/PRICE_C7.git
cd PRICE_C7

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r teams/team03_dynamic_pricing/requirements.txt
```

---

## 9. Execution Instructions

### Running the Team 3 Streamlit Dashboard
```powershell
# From repo root:
streamlit run teams/team03_dynamic_pricing/app.py

# Or from team directory:
cd teams/team03_dynamic_pricing
streamlit run app.py
```

### Running Automated Pytest Tests
```powershell
# Run Team 3 test suite (15 unit tests)
python -m pytest teams/team03_dynamic_pricing/tests/test_team03.py -v
```

### Running the Evaluator Autograder
```powershell
# Run autograder for Team 3
python evaluator/autograder.py --team 3
```

---

## 10. Test Coverage Summary

The expanded test suite in [`tests/test_team03.py`](tests/test_team03.py) covers 15 distinct test cases:

1. `test_inventory_schema`: Verifies $\ge 5$ items, required keys, positive base price.
2. `test_happy_hour_rule`: Verifies 18:00, stock 25 produces $-15\%$ discount.
3. `test_weather_rain_surge`: Verifies Raining + Hot Coffee produces $+10\%$ surge.
4. `test_heatwave_cold_surge`: Verifies Heatwave + Cold Brew produces $+15\%$ surge.
5. `test_cost_basis_guardrail`: Verifies cost-basis floor clamp when raw discount falls below cost.
6. `test_scarcity_premium_rule`: Verifies $0 < \text{stock} < 5$ produces $+10\%$ surge.
7. `test_morning_rush_rule`: Verifies 7–9 AM produces $+5\%$ surge on Beverages only.
8. `test_combined_rules_stacking`: Verifies simultaneous Rain Surge (+10%) and Happy Hour (-15%) yields net $-5\%$.
9. `test_zero_and_negative_inventory`: Verifies stock $\le 0$ does not trigger invalid rules.
10. `test_boundary_hours`: Verifies clock transitions at 6h, 7h, 9h, 10h, 16h, 17h.
11. `test_deterministic_output`: Verifies 50 consecutive runs yield identical numerical results.
12. `test_extreme_and_malformed_inputs`: Verifies safe execution with `None`, string inputs, negative base prices.
13. `test_price_ceiling_guardrail`: Verifies maximum surge ceiling cap ($2.0\times$).
14. `test_margin_and_delta_calculations`: Verifies dollar and percentage margin formulas.
15. `test_load_inventory_file_not_found`: Verifies `FileNotFoundError` handling for missing files.

---

## 11. Assumptions & Limitations

### Assumptions
- **Cost Margin Baseline**: When `Cost_Price` is omitted in an input item, the engine conservatively assumes a 30% food & beverage cost ratio ($0.30 \times P_{\text{base}}$).
- **Keyword Matching**: Beverage classification relies on semantic keywords (`hot`, `coffee`, `chai`, `espresso`, `cold`, `iced`, `nitro`, `matcha`) reflecting real-world cafe menu naming conventions.
- **Hour Resolution**: Intraday pricing operates at discrete 1-hour intervals (0–23).

### Limitations
- **Customer Price Sensitivity**: Does not currently calibrate price elasticity of demand via econometric regression models.
- **Competitor Parity**: Does not scrape competitor menu boards in real time.
- **Omnichannel Sync**: Assumes in-store POS and electronic menu boards sync instantly.

---

## 12. Execution Strategy & AI Prompt Log

Development followed a structured vibe-coding workflow with Claude / Gemini:

### Prompt 1: Core Mathematical Formulation & Guardrails
> *"Implement a robust, deterministic Python dynamic pricing engine for a retail cafe catalog. It must accept an item dictionary, hour of day (0-23), weather condition, and inventory stock. Implement five rules: Happy hour clearance (-15%), rainy warmth surge (+10%), heatwave chilled beverage surge (+15%), scarcity premium (+10%), and morning commute rush (+5%). Crucially, include an absolute cost-floor safeguard that guarantees the recommended price never falls below Cost_Price."*

### Prompt 2: Comprehensive Test Suite & Edge Cases
> *"Write a comprehensive pytest test suite for the dynamic pricing engine. Preserve the existing evaluator baseline tests exactly, then add tests for scarcity premiums, morning rush, combined rule stacking, boundary clock hours, zero and negative stock, extreme/malformed inputs, deterministic reproducibility, and price ceiling limits."*

### Prompt 3: Rich Interactive Streamlit & Plotly Dashboard
> *"Build a Streamlit dashboard with environmental simulation sliders for hour of day, weather, and stock scaling. Include 4 top-level financial KPI cards, a real-time price board dataframe, an interactive Plotly grouped bar chart comparing Base Price vs Cost Floor vs Dynamic Price, an item-level price driver drilldown tab, and CSV export."*

### Prompt 4: Academic Evaluation Rubric Alignment
> *"Verify the implementation against evaluator/autograder.py and rubrics.py to guarantee 100/100 raw points and 25.0/25 academic marks. Ensure directory isolation, valid Python AST parsing for all 3 key functions, interactive widget detection, data schema validation, and complete documentation."*
