"""
Master Launch Hub for Retail AI Vibe-Coding Challenge.
Allows judges, instructors, and students to navigate between all 9 team applications
and run the automated evaluator directly in the browser!
"""

import sys
import subprocess
from pathlib import Path
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Retail AI Challenge | Master Hub",
    page_icon="🛍️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

st.sidebar.title("🛍️ Retail AI Challenge")
st.sidebar.caption("9 Multi-Disciplinary Tracks with Automated Evaluator")

# Navigation menu
menu_options = [
    "🏠 Challenge Overview & Scorecard",
    "Team 1: 'Vibe-Shift' Trend Forecaster",
    "Team 2: Sassy Stylist Bot",
    "Team 3: 'Happy Hour' Dynamic Pricing",
    "Team 4: Color-Palette Personal Shopper",
    "Team 5: The Empathy Engine",
    "Team 6: 'Drop Culture' Markdown Optimizer",
    "Team 7: Ethical AI Auditor",
    "Team 8: Virtual Try-On Feedback Loop",
    "Team 9: Artisan Safety-Stock Planner",
    "🧪 Run Live Autograder (100 pts -> 25 Marks)"
]

choice = st.sidebar.radio("Select View / Team App:", menu_options)

if choice == "🏠 Challenge Overview & Scorecard":
    st.title("🏆 Retail AI Vibe-Coding Challenge")
    st.markdown("""
    Welcome to the **Retail AI Vibe-Coding Challenge**! This repository hosts nine production-grade,
    modular retail AI applications built with a *vibe-coding* approach.
    
    ### 🎯 9 Specialized Team Tracks
    """)

    tracks = [
        {"Team": "Team 1", "Name": "The 'Vibe-Shift' Trend Forecaster", "Category": "Demand Forecasting", "Customer": "Boutique Retail Buyers & Inventory Planners"},
        {"Team": "Team 2", "Name": "The Sassy Stylist Bot", "Category": "Conversational AI", "Customer": "E-Commerce Fashion Shoppers (B2C)"},
        {"Team": "Team 3", "Name": "The 'Happy Hour' Dynamic Pricing Engine", "Category": "Pricing Analytics", "Customer": "Store & Revenue Managers at Cafes / Shops"},
        {"Team": "Team 4", "Name": "Color-Palette Personal Shopper", "Category": "Visual Commerce", "Customer": "Home Decor & Apparel Shoppers"},
        {"Team": "Team 5", "Name": "The Empathy Engine", "Category": "Sentiment Analysis", "Customer": "Customer Experience (CX) & Operations Directors"},
        {"Team": "Team 6", "Name": "The 'Drop Culture' Markdown Optimizer", "Category": "Clearance Analytics", "Customer": "Retail Merchandisers & Clearance Strategists"},
        {"Team": "Team 7", "Name": "Ethical AI Auditor for Retail", "Category": "Ethics & Privacy", "Customer": "Compliance Officers & AI Governance Teams"},
        {"Team": "Team 8", "Name": "The Virtual Try-On Feedback Loop", "Category": "AR/VR Analytics", "Customer": "E-Commerce Product Managers & Growth Leads"},
        {"Team": "Team 9", "Name": "The Artisan Safety-Stock Planner", "Category": "Inventory Optimization", "Customer": "Independent Artisans, Makers & Boutique Owners"}
    ]
    st.dataframe(pd.DataFrame(tracks), use_container_width=True)

    st.markdown("""
    ---
    ### 📊 Grading & Evaluation Architecture (100 Points ➔ 25 Marks)
    Each team submission is automatically evaluated across **5 Pillars**:
    - **Pillar 1: Repository Architecture (20 pts)**: Clean directory structure, `app.py`, engine file, `README.md`, dependencies.
    - **Pillar 2: Algorithmic Logic & Unit Tests (30 pts)**: Automated pytest validation of domain math & business logic.
    - **Pillar 3: Interactive UI Readiness (20 pts)**: Interactive widgets, Plotly charts, metric cards, and responsive layout.
    - **Pillar 4: Data Quality & Schema (15 pts)**: Schema conformance, realistic variations, and volume minimums.
    - **Pillar 5: Vibe-Coding Prompts & Docs (15 pts)**: Documented AI prompt logs (Cursor / ChatGPT / Claude / Gemini).
    
    > **Final Converted Mark** = `Raw Score / 4.0` (Max: **25 Marks**)
    """)

elif choice == "🧪 Run Live Autograder (100 pts -> 25 Marks)":
    st.title("🧪 Live Autograder & Diagnostic Scorecard")
    st.caption("Run the automated evaluation engine across all 9 teams or a specific team.")

    target_team = st.selectbox("Select Team to Grade", ["All 9 Teams"] + [f"Team {i}" for i in range(1, 10)])

    if st.button("🚀 Run Autograder Now", type="primary", use_container_width=True):
        with st.spinner("Executing unit tests and inspecting architecture..."):
            cmd = [sys.executable, str(BASE_DIR / "evaluator" / "autograder.py")]
            if target_team == "All 9 Teams":
                cmd.append("--all")
            else:
                team_num = target_team.split()[1]
                cmd.extend(["--team", team_num])

            res = subprocess.run(cmd, capture_output=True, text=True)
            output_md = res.stdout if res.stdout else res.stderr
            st.markdown(output_md)

# Route to Team 1
elif choice == "Team 1: 'Vibe-Shift' Trend Forecaster":
    from teams.team01_vibe_shift import app as t1_app
# Route to Team 2
elif choice == "Team 2: Sassy Stylist Bot":
    from teams.team02_sassy_stylist import app as t2_app
# Route to Team 3
elif choice == "Team 3: 'Happy Hour' Dynamic Pricing":
    from teams.team03_dynamic_pricing import app as t3_app
# Route to Team 4
elif choice == "Team 4: Color-Palette Personal Shopper":
    from teams.team04_color_shopper import app as t4_app
# Route to Team 5
elif choice == "Team 5: The Empathy Engine":
    from teams.team05_empathy_engine import app as t5_app
# Route to Team 6
elif choice == "Team 6: 'Drop Culture' Markdown Optimizer":
    from teams.team06_markdown_optimizer import app as t6_app
# Route to Team 7
elif choice == "Team 7: Ethical AI Auditor":
    from teams.team07_ethical_auditor import app as t7_app
# Route to Team 8
elif choice == "Team 8: Virtual Try-On Feedback Loop":
    from teams.team08_tryon_analytics import app as t8_app
# Route to Team 9
elif choice == "Team 9: Artisan Safety-Stock Planner":
    from teams.team09_artisan_stock import app as t9_app
