# Retail AI Lab Evaluation Rubric and Grading Guide

This document defines the automated and qualitative grading system for all nine student tracks in the Retail AI Lab.

Submissions are evaluated on a 100-Point Raw Score Scale, which is automatically converted into 25 Final Academic Marks.

$$\text{Final Marks} = \frac{\text{Raw Score}}{4.0} \quad (\text{Max: } 25.0 \text{ Marks})$$

---

## Evaluation Pillars Overview

```
+-------------------------------------------------------------+---------+
| Evaluation Pillar                                           | Points  |
+-------------------------------------------------------------+---------+
| 1. Repository Architecture and File Cleanliness             | 20 pts  |
| 2. Core Algorithmic Logic and Automated Unit Tests          | 30 pts  |
| 3. Interactive UI and Dashboard Readiness                   | 20 pts  |
| 4. Data Quality and Schema Conformance                      | 15 pts  |
| 5. Prompt Documentation and Execution Strategy              | 15 pts  |
+-------------------------------------------------------------+---------+
| TOTAL RAW SCORE                                             | 100 pts |
| CONVERTED FINAL GRADE (Raw / 4)                             | 25.0 M  |
+-------------------------------------------------------------+---------+
```

---

### Pillar 1: Repository Architecture and File Cleanliness (20 Points)
- Directory Structure (4 pts): Submission lives strictly inside the designated `teams/team0X_.../` folder.
- Application Entry Point (4 pts): `app.py` is present and directly executable via `streamlit run app.py`.
- Modular Core Engine (4 pts): Domain algorithms and formulas are separated into a dedicated engine module.
- Team README (4 pts): Self-contained `README.md` populated with team members and problem definition.
- Dependency Isolation (4 pts): Clean, non-conflicting `requirements.txt`.

### Pillar 2: Algorithmic Logic and Automated Unit Tests (30 Points)
- Key Function Signatures (10 pts): All mandatory domain functions are implemented with clean types and signatures.
- Automated Pytest Suite (20 pts): Automated test execution in `tests/test_team0X.py`:
  - 100% test pass rate = 20 pts
  - Partial test pass = Proportional credit
  - Mathematical correctness: ROP formula, Euclidean distance, time-series projection, Pearson correlation, conversion lift, cost-basis floor.

### Pillar 3: Interactive UI and Dashboard Readiness (20 Points)
- Python Syntax Integrity (5 pts): `app.py` compiles and runs without syntax errors.
- Interactive Widgets and Controls (10 pts):
  - Inputs: Sliders, dropdowns, file uploaders, chat input, or text areas.
  - Outputs: Interactive Plotly line/funnel/scatter charts, status alerts, or metric cards.
- User Guidance and Layout (5 pts): Streamlit layout formatting (`st.columns`, `st.sidebar`, `st.expander`, `st.metric`).

### Pillar 4: Data Quality and Schema Conformance (15 Points)
- File Format and Integrity (5 pts): Valid CSV, JSON, or TXT file located in `data/`.
- Column / Key Requirements (5 pts): All specified fields are present and properly typed.
- Volume and Variation (5 pts): Meets minimum item/row count.

### Pillar 5: Prompt Documentation and Execution Strategy (15 Points)
- Project Problem Statement (5 pts): Target customer and business problem clearly explained.
- Prompt Log (5 pts): Detailed record of prompts used during development.
- Local Reproduction Guide (5 pts): Clear commands to install, run, and test the app.

---

## Conversion Table: 100 Points to 25 Marks

| Raw Score (/100) | Converted Mark (/25) | Performance Tier | Status |
| :---: | :---: | :---: | :---: |
| 95 - 100 | 23.8 - 25.0 | Exemplary (Production-Ready) | PASS |
| 85 - 94 | 21.3 - 23.5 | Proficient (High Quality) | PASS |
| 70 - 84 | 17.5 - 21.0 | Competent (Minor Gaps) | PASS |
| 60 - 69 | 15.0 - 17.3 | Minimum Passing Threshold | PASS (Review Required) |
| < 60 | < 15.0 | Incomplete / Logic Errors | NEEDS REVISION |

---

## Automated Scoring via GitHub Actions
Every time a team opens or updates a Pull Request:
1. GitHub Actions triggers `.github/workflows/autograder.yml`.
2. The autograder identifies which team folder was modified.
3. Tests and code inspection run automatically.
4. The bot posts a formatted diagnostic report directly as a Pull Request comment and writes the score to the Job Summary.
5. Students can review diagnostic checks and push corrections immediately.
