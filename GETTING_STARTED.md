# Quickstart Guide

Set up and run the Retail AI Lab in under five minutes.

---

## Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your system.
- Git configured with your GitHub account.
- An editor or IDE of your choice.

---

## Setup Instructions

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

## Google Gemini API Setup (Free Tier)
Tracks utilizing language models (Team 2 and Team 5) support Google Gemini API integration:
1. Visit Google AI Studio at https://aistudio.google.com/
2. Sign in with a standard Google account.
3. Click "Get API key" -> "Create API key".
4. Configure your .env file:
   ```bash
   cp .env.example .env
   ```
5. Open .env and add:
   ```env
   GEMINI_API_KEY=your_key_here
   ```
Note: If no API key is provided, all applications use built-in offline rules and run normally.

---

## Launch the Master Dashboard
Preview all team applications from the root launcher:
```bash
streamlit run app.py
```
Open your browser at http://localhost:8501.

---

## Run Tests and Pre-Submission Autograder
```bash
# Run all unit tests
pytest teams/ -v

# Run the autograder on your team (e.g., Team 1)
python evaluator/autograder.py --team 1

# Run the autograder across all teams
python evaluator/autograder.py --all
```
