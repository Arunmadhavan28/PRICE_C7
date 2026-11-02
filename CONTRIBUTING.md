# Student Contribution and Pull Request Submission Guide

Follow this guide to set up your repository, develop your team application, test locally, and submit your Pull Request for grading.

---

## Step-by-Step Student Workflow

### Step 1: Fork the Repository
1. Navigate to the main repository: https://github.com/Arunmadhavan28/PRICE_C7
2. Click the Fork button in the top-right corner.
3. Create the fork under your personal GitHub account.

### Step 2: Clone Your Fork Locally
```bash
# Clone your fork (replace YOUR_USERNAME with your GitHub handle)
git clone https://github.com/YOUR_USERNAME/PRICE_C7.git
cd PRICE_C7

# Create a dedicated feature branch for your team
git checkout -b team-01-submission
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
Work inside your assigned team folder:
```
teams/
  team01_vibe_shift/         # Team 1: Demand Forecasting
  team02_sassy_stylist/      # Team 2: Conversational AI
  team03_dynamic_pricing/    # Team 3: Pricing Analytics
  team04_color_shopper/      # Team 4: Visual Commerce
  team05_empathy_engine/     # Team 5: Sentiment Analysis
  team06_markdown_optimizer/ # Team 6: Clearance Analytics
  team07_ethical_auditor/    # Team 7: Ethics & Privacy
  team08_tryon_analytics/    # Team 8: AR/VR Analytics
  team09_artisan_stock/      # Team 9: Inventory Optimization
```

Rule: Keep all changes isolated inside your assigned team folder.

---

### Step 5: Develop Your Solution
1. Open the project in your editor.
2. Read your track README.md for problem statements, formulas, and prompt guidelines.
3. Test your Streamlit app locally:
   ```bash
   cd teams/team0X_your_team/
   streamlit run app.py
   ```

---

### Step 6: Verify with Automated Unit Tests and Autograder
Before submitting your PR, verify that you achieve 100/100 points (25/25 Marks):

```bash
# 1. Run unit tests for your team
pytest teams/team01_vibe_shift/tests/test_team01.py -v

# 2. Run the local autograder
python evaluator/autograder.py --team 1
```

If any check reports [FAIL], review the diagnostic message and address the issue.

---

### Step 7: Commit, Push, and Open a Pull Request
```bash
# Stage your changes
git add teams/team0X_your_team/

# Commit with a clear message
git commit -m "feat(team01): completed trend forecaster and prompt log"

# Push to your fork
git push origin team-01-submission
```

### Step 8: Open the Pull Request on GitHub
1. Go to your fork on GitHub and click "Compare & pull request".
2. Target the base repository: Arunmadhavan28/PRICE_C7 (branch: main).
3. Fill out the Pull Request Template.
4. Submit the PR.

---

## Autonomous Grading, Review, and Auto-Merge
Once your PR is submitted:
- The Retail AI Autograder workflow runs automatically.
- A bot comment will appear on your PR with your detailed diagnostic scorecard (100 raw points converted to 25.0 academic marks).
- If your score is 100/100 (25.0/25 marks), the bot automatically submits an official GitHub approval review and executes an autonomous squash merge into `main`.
- Once merged, consult the [Submission and Grading Guide](SUBMISSION_AND_GRADING_GUIDE.md) for the exact notification checklist and message template to claim your marks with ARUNMADHAVAN.
- If your score is less than 100, make the necessary corrections and push additional commits to your branch. The autograder updates automatically.
