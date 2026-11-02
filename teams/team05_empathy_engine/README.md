# 💡 Team 5: The Empathy Engine (Sentiment & Emotion Analysis)

## 👥 Team Information
- **Track**: Natural Language Processing & Customer Emotion Analytics
- **Application Name**: The Empathy Engine
- **Team Members**:
  - Member 1: [Full Name (@github_handle)]
  - Member 2: [Full Name (@github_handle)]
  - Member 3: [Full Name (@github_handle)]

---

## 🎯 The Core Problem Solved
Qualitative customer feedback (hundreds of daily written reviews, return reasons, and support tickets) is notoriously difficult to measure and prioritize at scale. Operations directors often only track 1-to-5 star ratings, remaining completely blind to specific emotional friction points like broken returns, contradictory sizing charts, or delayed delivery.

**The Solution**: An NLP emotion intelligence engine that ingests qualitative feedback in bulk, categorizes each review into distinct emotional dimensions (**Joy**, **Frustration**, **Confusion**, **Satisfaction**, **Neutral**), and surfaces actionable CX health scores and pain-point drilldowns.

## 🛍️ Target End Customer
- **Primary**: Customer Experience (CX) Managers and Retail Operations Directors.
- **Secondary**: E-commerce Product Managers optimizing website checkout friction.

---

## 📊 Technical & Data Requirements
1. **Data**: `data/customer_reviews.txt` containing 30 varied, realistic customer reviews covering positive experiences, damaged items, return headaches, and confusing sizing charts.
2. **Logic (`empathy_engine.py`)**:
   - `load_reviews(filepath)`
   - `analyze_review(review_text)`: Maps text to emotions and calculates polarity scores (-1.0 to +1.0).
   - `compute_emotion_distribution(reviews_list)`: Computes percentage breakdowns and CX Friction Indices.
   - `analyze_bulk_reviews(reviews_list)`: Generates full structured analytics table.
   - Dual-engine architecture: Zero-cost emotion lexicon + Google Gemini API (free tier).
3. **UI / Dashboard (`app.py`)**:
   - Bulk text area for manual pasting or instant 30-review sample loading.
   - Plotly interactive Donut / Pie chart for emotional share and Bar chart for volume breakdown.
   - High-level metric cards: Total Reviews, Satisfaction Rate %, Friction Index %, Polarity.
   - Interactive drilldown filter allowing managers to inspect all reviews under specific emotions (e.g. Frustration).

---

## 🤖 Vibe-Coding Execution Strategy & Prompt Log
*Students used the following curated AI prompts to build this engine:*

### Prompt 1: Emotion Taxonomy & Sentiment Pipeline
> *"Write a Python module that takes a list of retail customer reviews and classifies each into one of five emotional categories: Joy, Frustration, Confusion, Satisfaction, or Neutral. Compute a polarity score from -1.0 to +1.0 and extract the trigger keywords causing the emotion."*

### Prompt 2: Plotly Donut & Bar Charts in Streamlit
> *"Create a Streamlit dashboard with a dark theme. Add a sidebar text area to paste reviews. Display 4 metric cards: Total Analyzed, Satisfaction %, Friction Index %, and Average Polarity. Plot an emotional distribution donut chart and an emotion bar chart side-by-side using Plotly Express."*

### Prompt 3: Filterable Review Drilldown
> *"Add a dropdown selector to filter reviews by emotion (e.g., 'Frustration', 'Confusion'). For each review in the filtered list, display a card with colored left border, polarity badge, quote, and detected trigger keywords."*

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
# Run pytest for Team 5
pytest tests/test_team05.py -v

# Run evaluator autograder
python ../../evaluator/autograder.py --team 5
```

## 🏆 Evaluation Rubric (100 Points -> 25 Marks)
- **Architecture (20 pts)**: Directory structure, `app.py`, `empathy_engine.py`, clean requirements.
- **Logic & Unit Tests (30 pts)**: Accurate emotion taxonomy, percentage aggregation, test suite passes.
- **Interactive UI (20 pts)**: Bulk text area, Plotly donut & bar charts, drill-down cards.
- **Data Quality (15 pts)**: 30 varied, realistic qualitative customer reviews.
- **Documentation (15 pts)**: Complete prompt log, customer definition, run instructions.
