# 🛡️ Team 7: Ethical AI Auditor for Retail (Ethics & Privacy)

## 👥 Team Information
- **Track**: AI Ethics, Bias Detection & Regulatory Compliance
- **Application Name**: Ethical AI Auditor for Retail
- **Team Members**:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## 🎯 The Core Problem Solved
Retail AI recommendation models can inadvertently learn harmful demographic biases—such as steering lower-income zip codes exclusively toward low-end clearance items while showing premium luxury goods only to affluent areas. Furthermore, processing user profiles without verified opt-in consent violates GDPR, CCPA, and emerging global AI governance standards, creating severe regulatory fines and brand risk.

**The Solution**: A red-teaming compliance auditor that continuously inspects model output logs, calculates demographic proxy price correlation ($r$), detects disparate impact ratios, and immediately isolates records processed without user consent (`Opt_in_Status == False`).

## 🛍️ Target End Customer
- **Primary**: Retail Compliance Officers, AI Governance Teams, and Legal Counsel.
- **Secondary**: Lead Data Scientists validating recommendation systems before production release.

---

## 📊 Technical & Data Requirements
1. **Data**: `data/audit_dataset.csv` containing:
   - `Customer_ZipCode` (Demographic proxy)
   - `Income_Bracket` & `Customer_Income_Proxy`
   - `Recommended_Item_Price` (AI output)
   - `Opt_in_Status` (Boolean user consent flag)
   - `Item_Category`
   - `Recommendation_Algorithm`
2. **Logic (`auditor.py`)**:
   - `load_audit_data(filepath)`
   - `audit_privacy_breaches(df)`: Isolates non-opted-in rows and calculates breach rates.
   - `audit_bias_correlation(df)`: Computes Pearson correlation $r$ and disparate impact ratio between low-income and high-income zip codes.
   - `generate_compliance_report(df)`: Assigns overall risk rating (`CRITICAL NON-COMPLIANCE`, `PRIVACY BREACH WARNING`, `COMPLIANT`).
3. **UI / Dashboard (`app.py`)**:
   - Red-Teaming alert banner with flashing warning status.
   - High-level metric cards: Privacy Breaches Count, Demographic Bias $r$, Disparate Impact Ratio, Log Volume.
   - Plotly interactive scatter plot showing Zip Code vs Recommended Price with OLS regression trendline.
   - Quarantined table view of non-consented rows with simulated one-click data scrub.

---

## 🤖 Vibe-Coding Execution Strategy & Prompt Log
*Students used the following curated AI prompts to build this auditor:*

### Prompt 1: Biased Synthetic Audit Dataset
> *"Write a Python script that generates a synthetic dataset representing retail AI recommendations across 4 zip codes with varying average incomes. Intentionally simulate demographic steering bias where higher-income zip codes receive significantly higher-priced recommendations, and 15% of records have Opt_in_Status=False."*

### Prompt 2: Privacy Breach & Pearson Correlation Auditor
> *"Write a Python module that takes the audit dataset, flags any record where Opt_in_Status is False, computes the Pearson correlation between customer zip income and recommended price, and calculates the disparate impact ratio."*

### Prompt 3: Red-Teaming Streamlit Dashboard
> *"Build a Streamlit governance dashboard. If privacy breaches or high correlation (>0.4) exist, display a prominent warning banner. Render 4 metric cards, a Plotly scatter plot with regression trendline, and an expandable data table of quarantined records."*

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
# Run pytest for Team 7
pytest tests/test_team07.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 7
```

## 🏆 Evaluation Rubric (100 Points -> 25 Marks)
- **Architecture (20 pts)**: Directory structure, `app.py`, `auditor.py`, clean requirements.
- **Logic & Unit Tests (30 pts)**: Accurate privacy breach isolation, Pearson correlation, test suite passes.
- **Interactive UI (20 pts)**: Red-teaming warning banner, Plotly scatter plot, metrics, quarantined table.
- **Data Quality (15 pts)**: Realistic synthetic dataset with demographic proxies and opt-in flags.
- **Documentation (15 pts)**: Complete prompt log, customer definition, run instructions.
