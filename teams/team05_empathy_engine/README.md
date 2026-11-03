# Team 5: The Empathy Engine (Sentiment Analysis)

## Team Information
- Track: Natural Language Processing and Emotion Analytics
- Application Name: The Empathy Engine
- Team Members:
  - Member 1: LINGARAJ V (@lingaraj310)
  - Member 2: NANDHINI J (@Nandhini-187)
  - Member 3: NISANTH EP (@nisanthofficial00-ai)
  - Member 4: AHIL VP (@ahil-ahil)
  - Member 5: KAVIYA M (@Kaviyamathi876-lab)

---

## The Core Problem Solved
Qualitative customer feedback (hundreds of daily written reviews, return reasons, and support tickets) is difficult to measure and prioritize at scale. Operations directors often only track 1-to-5 star ratings, remaining unaware of specific emotional friction points like broken returns, contradictory sizing charts, or delayed delivery.

The Solution: An NLP emotion intelligence engine that ingests qualitative feedback in bulk, categorizes each review into distinct emotional dimensions (Joy, Frustration, Confusion, Satisfaction, Neutral), and surfaces actionable CX health scores and pain-point drilldowns.

## Target End Customer
- Primary: Customer Experience (CX) Managers and Retail Operations Directors.
- Secondary: E-commerce Product Managers optimizing website checkout friction.

---

## Technical and Data Requirements
1. Data: data/customer_reviews.txt containing 30 varied customer reviews covering product quality, packaging, delivery, returns, and navigation.
2. Logic (empathy_engine.py):
   - load_reviews(filepath)
   - analyze_review(review_text): Maps text to emotions and calculates polarity scores (-1.0 to +1.0).
   - compute_emotion_distribution(reviews_list): Computes percentage breakdowns and CX Friction Indices.
   - analyze_bulk_reviews(reviews_list): Generates full structured analytics table.
   - Dual-engine architecture: Zero-cost emotion lexicon and Google Gemini API (free tier).
3. UI / Dashboard (app.py):
   - Bulk text area for manual pasting or instant 30-review sample loading.
   - Plotly interactive Donut / Pie chart for emotional share and Bar chart for volume breakdown.
   - High-level metric cards: Total Reviews, Satisfaction Rate %, Friction Index %, Polarity.
   - Interactive drilldown filter allowing managers to inspect all reviews under specific emotions.

---

## Execution Strategy and Prompt Log

### Prompt 1 (Data & Emotion Categories): Structuring Customer Reviews and Emotion Dimensions
> "Design a dataset of 30 realistic qualitative retail customer reviews reflecting multi-touchpoint customer experiences, including product material quality, sizing inconsistency, packaging integrity, delayed delivery, and customer support responsiveness. Define a clear emotional taxonomy categorizing reviews into distinct dimensions: Joy, Frustration, Confusion, Satisfaction, and Neutral. Establish indicative lexical trigger keyword dictionaries for each emotional dimension so qualitative sentiment can be parsed and audited deterministically."

*Outcome*: Created `data/customer_reviews.txt` containing 30 rich qualitative customer feedback strings and defined `EMOTION_KEYWORDS` taxonomy covering retail sentiment triggers.

### Prompt 2 (NLP Algorithm): Sentiment Polarity and Emotion Classification Pipeline
> "Implement an NLP analytics engine in Python (empathy_engine.py) with functions `load_reviews`, `analyze_review`, `compute_emotion_distribution`, and `analyze_bulk_reviews`. The `analyze_review` function must compute score weights across emotion lexicons, extract detected trigger keywords, classify dominant emotion, and calculate normalized polarity scores (-1.0 to +1.0). The `compute_emotion_distribution` function must compute emotion shares summing to 100%, aggregate a Customer Satisfaction Rate percentage (Joy + Satisfaction), and calculate a CX Friction Index percentage (Frustration + Confusion). Integrate Google Gemini 2.5 Flash API via google-genai to synthesize root-cause friction drivers and generate executive action plans."

*Outcome*: Delivered modular core engine in `empathy_engine.py` with dual-engine capability (offline deterministic keyword scoring and online Google Gemini 2.5 LLM reasoning).

### Prompt 3 (Dashboard UI & Visuals): Interactive Streamlit Interface and Plotly Charts
> "Build an interactive, production-ready Streamlit dashboard (app.py) formatted in clean academic dark theme with zero emojis. Implement a sidebar text area allowing users to paste custom reviews or toggle the full 30-review sample dataset. Create a high-level KPI metric row displaying Total Reviews Analyzed, Satisfaction Rate %, Friction Index %, and Average Polarity. Implement side-by-side Plotly Express charts: a donut chart showing percentage share of emotional dimensions, and a bar chart displaying count volume with percentage callouts. Add an interactive filterable inspection panel rendering styled review cards with color-coded borders, polarity scores, and detected trigger keywords. Include an on-demand button to trigger Gemini AI executive root-cause action planning."

*Outcome*: Implemented interactive web interface in `app.py` utilizing Streamlit, Plotly Express, and responsive metric columns.

### Prompt 4 (Testing & Edge Cases): Test Automation and Bounds Verification
> "Develop a comprehensive Pytest test suite in `tests/test_team05.py` to validate algorithm correctness and edge cases. Ensure test coverage for: (1) dataset volume verification ensuring at least 20 raw customer reviews, (2) classification accuracy across Joy, Frustration, and Confusion samples, (3) emotion percentage distribution summation between 99.0% and 101.0%, (4) metric bounds verification ensuring average polarity strictly stays within [-1.0, +1.0], and (5) DataFrame schema validation ensuring required columns ('review_text', 'emotion', 'polarity', 'matched_keywords') exist on bulk analysis. Ensure graceful handling of whitespace and empty strings."

*Outcome*: Validated 100% test pass rate across all 4 unit tests and verified perfect 100/100 (25.0/25 marks) on the autograder.

---

## How to Run Locally

```bash
# 1. Activate your virtual environment
source venv/bin/activate       # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
cd teams/team05_empathy_engine/
streamlit run app.py
```

## How to Run Automated Unit Tests

```bash
# Run pytest for Team 5
pytest teams/team05_empathy_engine/tests/ -v

# Run evaluator autograder
python evaluator/autograder.py --team 5
```

## Evaluation Rubric (100 Points to 25 Marks)
- Architecture (20 pts): Directory structure, app.py, empathy_engine.py, clean requirements.
- Logic and Unit Tests (30 pts): Accurate emotion taxonomy, percentage aggregation, test suite passes.
- Interactive UI (20 pts): Bulk text area, Plotly donut and bar charts, drill-down cards.
- Data Quality (15 pts): 30 varied qualitative customer reviews.
- Documentation (15 pts): Complete prompt log, customer definition, run instructions.
