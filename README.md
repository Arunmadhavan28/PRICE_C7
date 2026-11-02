# 🛍️ Retail AI Vibe-Coding Challenge (PRICE_C7)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/LLM-Google%20Gemini%20(Free%20Tier)-8E75C4.svg)](https://aistudio.google.com/)
[![Autograder CI](https://github.com/Arunmadhavanevr/PRICE_C7/workflows/%F0%9F%8E%93%20Retail%20AI%20Vibe-Coding%20Autograder/badge.svg)](https://github.com/Arunmadhavanevr/PRICE_C7/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Welcome to the **Retail AI Vibe-Coding Challenge**! This repository is a turnkey, production-grade educational platform hosting **nine distinct AI-driven retail applications** built with a modern **vibe-coding** paradigm.

Students fork this repository, build their assigned team application using AI-assisted coding tools (Cursor, Claude, ChatGPT, Gemini), test locally, and submit a Pull Request. An automated **GitHub Actions Autograder** grades submissions out of **100 points** and converts the score into **25 Academic Marks**.

---

## 📑 Table of Contents
- [🎯 The 9 Project Specifications Matrix](#-the-9-project-specifications-matrix)
- [🤖 The Vibe-Coding Playbook](#-the-vibe-coding-playbook)
- [📊 Evaluation Rubric (100 Points ➔ 25 Marks)](#-evaluation-rubric-100-points--25-marks)
- [🚀 Quickstart & Student Workflow](#-quickstart--student-workflow)
- [🔑 Google Gemini API Setup (100% Free)](#-google-gemini-api-setup-100-free)
- [📂 Repository Architecture](#-repository-architecture)
- [🧪 Running Automated Tests & Autograder](#-running-automated-tests--autograder)
- [🤝 Pull Request Submission Guide](#-pull-request-submission-guide)

---

## 🎯 The 9 Project Specifications Matrix

| Team | Project Name | Domain Category | Target End Customer | Key Technical Logic |
| :---: | :--- | :--- | :--- | :--- |
| **Team 1** | [The "Vibe-Shift" Trend Forecaster](teams/team01_vibe_shift/) | Demand Forecasting | Boutique Clothing Buyers & Planners | Time-series forecasting (30 days) blending sales velocity with cultural trend momentum. |
| **Team 2** | [The Sassy Stylist Bot](teams/team02_sassy_stylist/) | Conversational AI | Online Shoppers browsing fashion B2C | Grounded conversational LLM (Gemini API) adopting an opinionated fashion persona recommending strictly from local 50-item catalog. |
| **Team 3** | [The "Happy Hour" Dynamic Pricing Engine](teams/team03_dynamic_pricing/) | Pricing Analytics | Store & Revenue Managers at local cafes / shops | Real-time environmental pricing modifiers (weather, hour > 5 PM, stock surplus) with cost-basis floor protection. |
| **Team 4** | [Color-Palette Personal Shopper](teams/team04_color_shopper/) | Visual Commerce | Home Decor, Furniture & Apparel Shoppers | Dominant color extraction via quantization + 3D Euclidean distance RGB matching across catalog. |
| **Team 5** | [The Empathy Engine](teams/team05_empathy_engine/) | Sentiment Analysis | Customer Experience (CX) & Retail Ops Directors | NLP pipeline categorizing qualitative customer reviews into distinct emotions (Joy, Frustration, Confusion). |
| **Team 6** | [The "Drop Culture" Markdown Optimizer](teams/team06_markdown_optimizer/) | Clearance Analytics | Retail Merchandisers & Clearance Strategists | Identifies lagging sell-through velocity, computing minimum clearance discount while protecting cost basis. |
| **Team 7** | [Ethical AI Auditor for Retail](teams/team07_ethical_auditor/) | Ethics & Privacy | Retail Compliance Officers & AI Ethics Teams | Red-teaming auditor checking demographic zip code pricing bias ($r$) and isolating opt-in privacy violations. |
| **Team 8** | [The Virtual Try-On Feedback Loop](teams/team08_tryon_analytics/) | AR/VR Analytics | E-Commerce Product Managers & Digital Marketers | Funnel conversion analysis measuring AR vs Non-AR user behavior, basket size, and percentage conversion lift. |
| **Team 9** | [The Artisan Safety-Stock Planner](teams/team09_artisan_stock/) | Inventory Optimization | Independent Artisans, Makers & Boutique Owners | Visual Kanban calculating Reorder Point ($\text{ROP} = \text{LeadTime} \times \text{Burn} + \text{SafetyStock}$) with 1-click Purchase Order generation. |

---

## 🤖 The Vibe-Coding Playbook

*Vibe-coding* is the discipline of architecting software through strategic, high-leverage prompting of Large Language Models (LLMs) like Cursor, Claude 3.5 Sonnet, ChatGPT (GPT-4o), and Google Gemini.

### 💡 Core Rules for Effective Vibe-Coding:
1. **Never Prompt in a Vacuum**: Provide clear domain schemas, inputs, and expected outputs in your initial prompt.
2. **Break into Three Iterative Layers**:
   - **Layer 1: Data & Math**: Prompt the AI to generate synthetic data with realistic seasonality and write pure Python calculation functions.
   - **Layer 2: Test Verification**: Prompt the AI to write unit tests for edge cases (zero division, empty inputs, cost floor).
   - **Layer 3: UI & Polish**: Wire the tested functions into Streamlit widgets, Plotly graphs, and responsive layouts.
3. **Log Your Prompts**: Record every prompt in your team's `README.md` and the Pull Request description (mandatory for 15 rubric points).

---

## 📊 Evaluation Rubric (100 Points ➔ 25 Marks)

Submissions are evaluated automatically on every PR across **5 Pillars**:

$$\text{Final Grade} = \frac{\text{Raw Score (/100)}}{4.0} = \mathbf{25.0 \text{ Marks}}$$

| Pillar | Focus Area | Max Points | Diagnostic Checks |
| :---: | :--- | :---: | :--- |
| **1** | **Repository Architecture** | **20 pts** | Team folder isolation, `app.py`, engine file, `README.md`, `requirements.txt`. |
| **2** | **Algorithmic Logic & Tests** | **30 pts** | Pytest unit tests pass (100%), required math formulas, edge-case bounds. |
| **3** | **Interactive UI Readiness** | **20 pts** | Streamlit controls (sliders, selectboxes, uploaders, chat), Plotly charts, metric cards. |
| **4** | **Data Quality & Schema** | **15 pts** | Dataset exists, valid columns/keys, meets minimum volume requirements. |
| **5** | **Vibe-Coding Prompts & Docs** | **15 pts** | Documented prompt log, customer persona, local setup instructions. |
| **TOTAL** | **Full Submission** | **100 pts** | **Converted to 25.0 Marks** (Passing: $\ge$ 15.0 Marks) |

For complete scoring criteria, see [EVALUATION_RUBRIC.md](EVALUATION_RUBRIC.md).

---

## 🚀 Quickstart & Student Workflow

### 1. Clone & Set Up Environment
```bash
# Clone the repository
git clone https://github.com/Arunmadhavanevr/PRICE_C7.git
cd PRICE_C7

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Master Unified Hub
Preview all 9 team applications and run the in-browser autograder:
```bash
streamlit run app.py
```

### 3. Launch Your Team's Specific Application
```bash
cd teams/team01_vibe_shift/   # Navigate to your assigned track
streamlit run app.py
```

---

## 🔑 Google Gemini API Setup (100% Free)

Tracks utilizing Large Language Models (Team 2 Sassy Stylist & Team 5 Empathy Engine) support the **Google Gemini API** (massive context window and completely free tier with no credit card required):

1. Visit **[Google AI Studio](https://aistudio.google.com/)**.
2. Sign in with your Google account.
3. Click **Get API key** ➔ **Create API key**.
4. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
5. Paste your key:
   ```env
   GEMINI_API_KEY=AIzaSy...your_actual_key...
   ```
*(Note: If no API key is set, the applications gracefully fallback to built-in offline mock engines so you can develop and test without interruption!)*

---

## 📂 Repository Architecture

```
PRICE_C7/
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md     # Mandatory student PR template with prompt log
│   └── workflows/
│       └── autograder.yml           # Automated CI/CD evaluator posting PR scorecards
├── .env.example                     # Free Gemini API environment template
├── .gitignore                       # Clean Python, IDE, and temporary cache ignores
├── README.md                        # Master challenge guide & playbook
├── CONTRIBUTING.md                  # Step-by-step fork & PR instructions
├── GETTING_STARTED.md               # 5-minute setup guide
├── EVALUATION_RUBRIC.md             # Transparent 100 pt -> 25 mark breakdown
├── requirements.txt                 # Master dependencies
├── pyproject.toml                   # Pytest test discovery configuration
├── app.py                           # Master multi-team launcher hub
├── evaluator/                       # Automated grading engine
│   ├── autograder.py                # Grades teams locally or in CI (100 -> 25)
│   └── rubrics.py                   # Scoring criteria and schema specifications
└── teams/                           # 9 Isolated Student Tracks
    ├── team01_vibe_shift/           # Demand Forecasting
    ├── team02_sassy_stylist/        # Conversational AI (Gemini)
    ├── team03_dynamic_pricing/      # Pricing Analytics
    ├── team04_color_shopper/        # Visual Commerce
    ├── team05_empathy_engine/       # Sentiment Analysis
    ├── team06_markdown_optimizer/   # Clearance Analytics
    ├── team07_ethical_auditor/      # Ethics & Privacy
    ├── team08_tryon_analytics/      # AR/VR Analytics
    └── team09_artisan_stock/        # Inventory Optimization
```

---

## 🧪 Running Automated Tests & Autograder

Students can test their code locally before opening a Pull Request:

```bash
# Run pytest on all tracks
pytest teams/ -v

# Run pytest on your specific team (e.g. Team 1)
pytest teams/team01_vibe_shift/tests/test_team01.py -v

# Run the autograder for your team
python evaluator/autograder.py --team 1

# Run the autograder across all teams
python evaluator/autograder.py --all
```

---

## 🤝 Pull Request Submission Guide

1. **Fork** the repository to your personal GitHub account.
2. Create a feature branch: `git checkout -b team-01-vibe-shift`.
3. Work exclusively inside your designated `teams/team0X_.../` folder.
4. Run `python evaluator/autograder.py --team X` and ensure your score is **100/100 (25/25 Marks)**.
5. Push to your fork: `git push origin team-01-vibe-shift`.
6. Open a Pull Request targeting `main`. Fill in the PR template with your **Team Info**, **Screenshots**, and **Vibe-Coding Prompts**.
7. GitHub Actions will run the autograder and post your verified scorecard comment within seconds!

---

## ⚖️ License
This repository is open-sourced under the [MIT License](LICENSE). Built for AI-driven retail engineering hackathons and university labs.
