# Retail AI Lab (PRICE_C7)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/LLM-Google%20Gemini%20(Free%20Tier)-8E75C4.svg)](https://aistudio.google.com/)
[![Autograder CI](https://github.com/Arunmadhavan28/PRICE_C7/workflows/Retail%20AI%20Autograder/badge.svg)](https://github.com/Arunmadhavan28/PRICE_C7/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Retail AI Lab is an educational engineering repository hosting nine modular retail AI applications. 

Students fork this repository, build their assigned team application, test locally, and submit a Pull Request. An automated GitHub Actions Autograder evaluates submissions across five standard pillars out of 100 points and converts the score into 25 academic marks.

---

## Table of Contents
- [Project Specifications Matrix](#project-specifications-matrix)
- [Development Strategy](#development-strategy)
- [Evaluation Rubric (100 Points to 25 Marks)](#evaluation-rubric-100-points-to-25-marks)
- [Quickstart and Student Workflow](#quickstart-and-student-workflow)
- [Google Gemini API Setup (Free Tier)](#google-gemini-api-setup-free-tier)
- [Repository Architecture](#repository-architecture)
- [Running Automated Tests and Autograder](#running-automated-tests-and-autograder)
- [Pull Request Submission Guide](#pull-request-submission-guide)

---

## Project Specifications Matrix

| Team | Project Name | Domain Category | Target End Customer | Key Technical Logic |
| :---: | :--- | :--- | :--- | :--- |
| **Team 1** | [The 'Vibe-Shift' Trend Forecaster](teams/team01_vibe_shift/) | Demand Forecasting | Boutique Clothing Buyers and Planners | Time-series forecasting (30 days) blending sales velocity with cultural trend momentum. |
| **Team 2** | [The Sassy Stylist Bot](teams/team02_sassy_stylist/) | Conversational AI | Online Shoppers browsing fashion storefronts | Grounded conversational assistant using Gemini API strictly constrained to local 50-item catalog. |
| **Team 3** | [The 'Happy Hour' Dynamic Pricing Engine](teams/team03_dynamic_pricing/) | Pricing Analytics | Store and Revenue Managers at local cafes / shops | Real-time environmental pricing modifiers (weather, hour > 17:00, stock surplus) with cost-basis floor protection. |
| **Team 4** | [Color-Palette Personal Shopper](teams/team04_color_shopper/) | Visual Commerce | Home Decor, Furniture and Apparel Shoppers | Dominant color extraction via quantization and 3D Euclidean distance RGB matching across product catalog. |
| **Team 5** | [The Empathy Engine](teams/team05_empathy_engine/) | Sentiment Analysis | Customer Experience (CX) and Retail Ops Directors | NLP pipeline categorizing qualitative customer reviews into distinct emotions (Joy, Frustration, Confusion). |
| **Team 6** | [The 'Drop Culture' Markdown Optimizer](teams/team06_markdown_optimizer/) | Clearance Analytics | Retail Merchandisers and Clearance Strategists | Identifies lagging sell-through velocity, computing minimum clearance discount while protecting cost basis. |
| **Team 7** | [Ethical AI Auditor for Retail](teams/team07_ethical_auditor/) | Ethics & Privacy | Retail Compliance Officers and AI Governance Teams | Red-teaming auditor checking demographic zip code pricing bias (Pearson r) and isolating opt-in privacy violations. |
| **Team 8** | [The Virtual Try-On Feedback Loop](teams/team08_tryon_analytics/) | AR/VR Analytics | E-Commerce Product Managers and Digital Marketers | Funnel conversion analysis measuring AR vs Non-AR user behavior, basket size, and conversion lift percentage. |
| **Team 9** | [The Artisan Safety-Stock Planner](teams/team09_artisan_stock/) | Inventory Optimization | Independent Artisans, Makers and Boutique Owners | Visual Kanban calculating Reorder Point (ROP = LeadTime * Burn + SafetyStock) with automated Purchase Order generation. |

---

## Development Strategy

Students use modern AI-assisted workflows (Cursor, Claude, ChatGPT, Gemini) to accelerate implementation:
1. Provide clear schemas, inputs, and expected outputs in prompts.
2. Separate work into three layers:
   - Layer 1: Data and Math functions in dedicated core engine files.
   - Layer 2: Automated test verification via pytest.
   - Layer 3: Interactive UI using Streamlit and Plotly.
3. Record prompts in the team README.md and the Pull Request description.

---

## Evaluation Rubric (100 Points to 25 Marks)

Submissions are evaluated automatically on every Pull Request across 5 Pillars:

$$\text{Final Grade} = \frac{\text{Raw Score (/100)}}{4.0} = 25.0 \text{ Marks}$$

| Pillar | Focus Area | Max Points | Diagnostic Checks |
| :---: | :--- | :---: | :--- |
| **1** | **Repository Architecture** | **20 pts** | Team folder isolation, app.py, engine file, README.md, requirements.txt. |
| **2** | **Algorithmic Logic and Tests** | **30 pts** | Pytest unit tests pass (100%), required formulas, edge-case bounds. |
| **3** | **Interactive UI Readiness** | **20 pts** | Streamlit controls (sliders, selectboxes, uploaders, chat), Plotly charts, metric cards. |
| **4** | **Data Quality and Schema** | **15 pts** | Dataset exists, valid columns/keys, meets minimum volume requirements. |
| **5** | **Prompt Documentation** | **15 pts** | Documented prompt log, customer persona, local setup instructions. |
| **TOTAL** | **Full Submission** | **100 pts** | Converted to 25.0 Marks (Passing: >= 15.0 Marks) |

See [EVALUATION_RUBRIC.md](EVALUATION_RUBRIC.md) for details.

---

## Quickstart and Student Workflow

### 1. Clone and Set Up Environment
```bash
git clone https://github.com/Arunmadhavan28/PRICE_C7.git
cd PRICE_C7

python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Launch the Master Hub
Preview all nine team applications and run the in-browser autograder:
```bash
streamlit run app.py
```

### 3. Launch a Specific Team Application
```bash
cd teams/team01_vibe_shift/
streamlit run app.py
```

---

## Google Gemini API Setup (Free Tier)

Tracks using language models (Team 2 and Team 5) support Google Gemini API:
1. Visit Google AI Studio at https://aistudio.google.com/
2. Sign in with your Google account.
3. Generate an API key.
4. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
5. Add your key:
   ```env
   GEMINI_API_KEY=your_key_here
   ```
Note: If no API key is configured, applications automatically use offline fallback logic.

---

## Repository Architecture

```
PRICE_C7/
  .github/
    PULL_REQUEST_TEMPLATE.md
    workflows/
      autograder.yml
  .env.example
  .gitignore
  README.md
  CONTRIBUTING.md
  GETTING_STARTED.md
  EVALUATION_RUBRIC.md
  requirements.txt
  pyproject.toml
  app.py
  evaluator/
    autograder.py
    rubrics.py
  teams/
    team01_vibe_shift/
    team02_sassy_stylist/
    team03_dynamic_pricing/
    team04_color_shopper/
    team05_empathy_engine/
    team06_markdown_optimizer/
    team07_ethical_auditor/
    team08_tryon_analytics/
    team09_artisan_stock/
```

---

## Running Automated Tests and Autograder

```bash
# Run pytest on all tracks
pytest teams/ -v

# Run pytest on a specific team (e.g. Team 1)
pytest teams/team01_vibe_shift/tests/test_team01.py -v

# Run the autograder for a specific team
python evaluator/autograder.py --team 1

# Run the autograder across all teams
python evaluator/autograder.py --all
```

---

## Pull Request Submission and Autonomous Grading

This repository features a 100% autonomous evaluation, PR review, and auto-merge system.

For step-by-step instructions, expected bot scorecard comments, and the exact protocol for when to claim full credit:
- See the complete [Submission, Grading, and Completion Guide](SUBMISSION_AND_GRADING_GUIDE.md).
- See the [Contributing Guide](CONTRIBUTING.md).

### Quick Summary of the Submission Workflow:
1. Fork the repository to your personal GitHub account.
2. Create a feature branch: `git checkout -b team-01-submission`.
3. Work inside your designated `teams/team0X_.../` folder.
4. Verify locally: `python evaluator/autograder.py --team X` (must report 100/100 points, 25.0/25 marks).
5. Push to your fork: `git push origin team-01-submission`.
6. Open a Pull Request targeting `main`.
7. Within 60 seconds, the Retail AI Autograder bot runs automatically, posts your scorecard comment, officially reviews (`APPROVE`), and squash-merges your PR into `main`.
8. Once the PR is merged, follow the checklist in [SUBMISSION_AND_GRADING_GUIDE.md](SUBMISSION_AND_GRADING_GUIDE.md) to notify ARUNMADHAVAN and record your 25 marks.

---

## License
MIT License.
