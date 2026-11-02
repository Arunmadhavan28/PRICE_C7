# ⚡ 5-Minute Quickstart Guide

Get up and running with the **Retail AI Vibe-Coding Challenge** in under five minutes.

---

## 💻 Prerequisites
- **Python 3.10, 3.11, or 3.12** installed on your system.
- **Git** configured with your GitHub account.
- An AI code assistant (Cursor, VS Code with GitHub Copilot / Gemini Code Assist, ChatGPT, or Claude).

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Arunmadhavanevr/PRICE_C7.git
cd PRICE_C7
```

### 2. Create Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔑 Set Up Free Google Gemini API (Zero Cost)
The conversational and emotion intelligence tracks (Team 2 & Team 5) feature Google Gemini API integration.
1. Visit **[Google AI Studio](https://aistudio.google.com/)**.
2. Sign in with any standard Google account.
3. Click **Get API key** ➔ **Create API key** (free tier has massive context and zero billing setup).
4. Configure your `.env` file:
   ```bash
   cp .env.example .env
   ```
5. Open `.env` and set:
   ```env
   GEMINI_API_KEY=AIzaSy...your_actual_key...
   ```
*(Note: If you don't configure an API key, all apps will automatically fall back to their built-in offline rules and run seamlessly!)*

---

## 🎮 Launch the Master Dashboard
You can preview all 9 team applications from the root launcher:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to test the apps or run the live autograder!

---

## 🧪 Run Tests & Pre-Submission Autograder
```bash
# Run all unit tests
pytest teams/ -v

# Run the autograder on your team (e.g., Team 1)
python evaluator/autograder.py --team 1

# Run the autograder across all teams
python evaluator/autograder.py --all
```
