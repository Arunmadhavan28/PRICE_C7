# 🤝 Student Contribution & Pull Request Submission Guide

Welcome to the **Retail AI Vibe-Coding Challenge**! Follow this step-by-step guide to set up your repository, develop your team's application, test locally, and submit your Pull Request for grading.

---

## 🧭 Step-by-Step Student Workflow

### Step 1: Fork the Repository
1. Navigate to the main repository: [https://github.com/Arunmadhavanevr/PRICE_C7](https://github.com/Arunmadhavanevr/PRICE_C7)
2. Click the **Fork** button in the top-right corner.
3. Create the fork under your personal GitHub account.

### Step 2: Clone Your Fork Locally
```bash
# Clone your fork (replace YOUR_USERNAME with your GitHub handle)
git clone https://github.com/YOUR_USERNAME/PRICE_C7.git
cd PRICE_C7

# Create a dedicated feature branch for your team
git checkout -b team-01-vibe-shift   # Replace with your team number
```

### Step 3: Set Up Your Python Environment
```bash
# Create and activate a virtual environment (Python 3.10+ recommended)
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install master dependencies
pip install -r requirements.txt

# (Optional) Copy environment template for free Gemini API key
cp .env.example .env
```

### Step 4: Locate Your Assigned Track
Work exclusively inside your assigned team folder:
```
teams/
├── team01_vibe_shift/         # Team 1: Demand Forecasting
├── team02_sassy_stylist/       # Team 2: Conversational AI
├── team03_dynamic_pricing/     # Team 3: Pricing Analytics
├── team04_color_shopper/       # Team 4: Visual Commerce
├── team05_empathy_engine/      # Team 5: Sentiment Analysis
├── team06_markdown_optimizer/  # Team 6: Clearance Analytics
├── team07_ethical_auditor/     # Team 7: Ethics & Privacy
├── team08_tryon_analytics/     # Team 8: AR/VR Analytics
└── team09_artisan_stock/       # Team 9: Inventory Optimization
```

> **Rules of Engagement**: Do not modify other team folders! Keep your work contained within your assigned folder.

---

### Step 5: Vibe-Code Your Solution
1. Open the folder in **Cursor**, **VS Code**, or your preferred AI-augmented editor.
2. Read your track's `README.md` for specific problem statements, formulas, and prompt playbooks.
3. Prompt your AI assistant (Cursor, Claude, ChatGPT, Gemini) using the prompt strategies provided in the team README.
4. Test your Streamlit app locally:
   ```bash
   cd teams/team0X_your_team/
   streamlit run app.py
   ```

---

### Step 6: Verify with Automated Unit Tests & Autograder
Before submitting your PR, verify that you achieve **100/100 points (25/25 Marks)**:

```bash
# 1. Run unit tests for your team
pytest teams/team01_vibe_shift/tests/test_team01.py -v

# 2. Run the local autograder
python evaluator/autograder.py --team 1
```

If you see any ❌ marks, inspect the diagnostic output and fix the corresponding issue!

---

### Step 7: Commit, Push, and Open a Pull Request
```bash
# Stage your changes
git add teams/team0X_your_team/

# Commit with a clear message
git commit -m "feat(team01): completed vibe-shift demand forecaster and tests"

# Push to your fork
git push origin team-01-vibe-shift
```

### Step 8: Open the Pull Request on GitHub
1. Go to your fork on GitHub and click **Compare & pull request**.
2. Target the base repository: `Arunmadhavanevr/PRICE_C7` (branch: `main`).
3. Fill out the **Pull Request Template**:
   - Team Number and Members
   - Brief Problem & Solution summary
   - Vibe-Coding Prompt Log (the exact prompts you gave your AI)
   - Screenshots of your working Streamlit application
4. Submit the PR!

---

## 🤖 GitHub Actions Automatic Grading
Once your PR is submitted:
- The **Retail AI Autograder** workflow will automatically launch.
- Within 60 seconds, a bot comment will appear on your PR with your **Scorecard** (out of 100 points and 25 marks).
- If you need to make corrections, simply push additional commits to your branch—the autograder will re-run automatically!
