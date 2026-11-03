#!/usr/bin/env python3
"""
Autograder and Evaluator for Retail AI Lab.
Calculates raw score (out of 100) and converts it to academic grade (out of 25).

Usage:
  python evaluator/autograder.py --team 1
  python evaluator/autograder.py --all
  python evaluator/autograder.py --detect
"""

import os
import sys
import json
import ast
import argparse
import subprocess
from pathlib import Path
import pandas as pd

from rubrics import TEAM_SPECS

BASE_DIR = Path(__file__).resolve().parent.parent
TEAMS_DIR = BASE_DIR / "teams"


def evaluate_team(team_id: int) -> dict:
    spec = TEAM_SPECS.get(team_id)
    if not spec:
        return {"error": f"Unknown team ID: {team_id}"}

    team_folder = TEAMS_DIR / spec["folder"]
    report = {
        "team_id": team_id,
        "name": spec["name"],
        "category": spec["category"],
        "folder": str(team_folder.relative_to(BASE_DIR)),
        "categories": {},
        "raw_score": 0,
        "final_marks": 0.0,
        "feedback": [],
        "passed": False
    }

    # ---------------------------------------------------------
    # Pillar 1: Architecture and File Structure (Max: 20 pts)
    # ---------------------------------------------------------
    arch_score = 0
    arch_checks = []

    if team_folder.exists() and team_folder.is_dir():
        arch_score += 4
        arch_checks.append("[PASS] Team directory exists")
    else:
        arch_checks.append("[FAIL] Team directory missing")

    app_py = team_folder / "app.py"
    if app_py.exists():
        arch_score += 4
        arch_checks.append("[PASS] app.py present")
    else:
        arch_checks.append("[FAIL] app.py missing")

    engine_file = team_folder / spec["engine_file"]
    if engine_file.exists():
        arch_score += 4
        arch_checks.append(f"[PASS] Core engine ({spec['engine_file']}) present")
    else:
        arch_checks.append(f"[FAIL] Core engine ({spec['engine_file']}) missing")

    readme_file = team_folder / "README.md"
    if readme_file.exists():
        arch_score += 4
        arch_checks.append("[PASS] Team README.md present")
    else:
        arch_checks.append("[FAIL] Team README.md missing")

    req_file = team_folder / "requirements.txt"
    if req_file.exists():
        arch_score += 4
        arch_checks.append("[PASS] requirements.txt present")
    else:
        arch_checks.append("[FAIL] requirements.txt missing")

    report["categories"]["architecture"] = {
        "score": min(arch_score, 20),
        "max": 20,
        "checks": arch_checks
    }

    # ---------------------------------------------------------
    # Pillar 2: Algorithmic Logic and Unit Tests (Max: 30 pts)
    # ---------------------------------------------------------
    logic_score = 0
    logic_checks = []

    # Check function AST definitions in engine file
    if engine_file.exists():
        try:
            with open(engine_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            defined_funcs = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
            matched_funcs = [fn for fn in spec["key_functions"] if fn in defined_funcs]
            if len(matched_funcs) >= len(spec["key_functions"]):
                logic_score += 10
                logic_checks.append(f"[PASS] Found all key functions: {', '.join(matched_funcs)}")
            elif matched_funcs:
                pts = int(10 * (len(matched_funcs) / len(spec["key_functions"])))
                logic_score += pts
                logic_checks.append(f"[WARN] Partial key functions found: {', '.join(matched_funcs)} (+{pts} pts)")
            else:
                logic_checks.append(f"[FAIL] Expected functions {spec['key_functions']} not found in {spec['engine_file']}")
        except Exception as e:
            logic_checks.append(f"[FAIL] Syntax error parsing {spec['engine_file']}: {str(e)}")
    else:
        logic_checks.append("[FAIL] Engine file missing, skipping AST checks")

    # Run automated pytest test suite for this team
    test_folder = team_folder / "tests"
    test_files = list(test_folder.glob("test_*.py")) if test_folder.exists() else []

    if test_files:
        try:
            pytest_cmd = [
                sys.executable, "-m", "pytest",
                str(test_files[0]),
                "-q", "--no-header", "--tb=line"
            ]
            res = subprocess.run(pytest_cmd, capture_output=True, text=True, timeout=45)
            if res.returncode == 0:
                logic_score += 20
                logic_checks.append("[PASS] All automated unit tests passed successfully (+20 pts)")
            else:
                output_lines = res.stdout + res.stderr
                logic_checks.append(f"[WARN] Some unit tests failed:\n{output_lines[:300]}")
                if "passed" in output_lines:
                    logic_score += 10
                    logic_checks.append("[WARN] Partial test credit awarded (+10 pts)")
        except Exception as e:
            logic_checks.append(f"[FAIL] Test runner error: {str(e)}")
    else:
        logic_checks.append("[FAIL] No test suite found in tests/ directory")

    report["categories"]["logic_and_tests"] = {
        "score": min(logic_score, 30),
        "max": 30,
        "checks": logic_checks
    }

    # ---------------------------------------------------------
    # Pillar 3: Interactive UI and Dashboard Readiness (Max: 20 pts)
    # ---------------------------------------------------------
    ui_score = 0
    ui_checks = []

    if app_py.exists():
        try:
            with open(app_py, "r", encoding="utf-8") as f:
                app_content = f.read()

            ast.parse(app_content)
            ui_score += 5
            ui_checks.append("[PASS] app.py syntax is valid Python")

            found_ui = []
            for elem in spec["ui_elements"]:
                clean_name = elem.replace("st.", "")
                if elem in app_content or f"st.sidebar.{clean_name}" in app_content or clean_name in app_content:
                    found_ui.append(elem)
            if len(found_ui) >= 3:
                ui_score += 10
                ui_checks.append(f"[PASS] Rich interactive UI detected: {', '.join(found_ui)}")
            elif found_ui:
                ui_score += 5
                ui_checks.append(f"[WARN] Basic UI elements detected: {', '.join(found_ui)}")
            else:
                ui_checks.append("[FAIL] Expected interactive widgets not found in app.py")

            if any(term in app_content for term in ["st.sidebar", "st.expander", "st.info", "st.metric", "st.tabs"]):
                ui_score += 5
                ui_checks.append("[PASS] User guidance / tabs / metric cards detected (+5 pts)")
            else:
                ui_checks.append("[WARN] Consider adding st.sidebar, tabs, or metrics for better UX")
        except SyntaxError as e:
            ui_checks.append(f"[FAIL] Syntax error in app.py: {str(e)}")
    else:
        ui_checks.append("[FAIL] app.py missing")

    report["categories"]["ui_readiness"] = {
        "score": min(ui_score, 20),
        "max": 20,
        "checks": ui_checks
    }

    # ---------------------------------------------------------
    # Pillar 4: Data Schema and Quality Conformance (Max: 15 pts)
    # ---------------------------------------------------------
    data_score = 0
    data_checks = []

    for rel_path in spec.get("data_files", []):
        data_path = team_folder / rel_path
        if not data_path.exists():
            data_checks.append(f"[FAIL] Required data file missing: {rel_path}")
            continue

        if data_path.stat().st_size == 0:
            data_checks.append(f"[FAIL] Data file {rel_path} is empty")
            continue

        if rel_path.endswith(".csv"):
            try:
                df = pd.read_csv(data_path)
                data_score += 5
                data_checks.append(f"[PASS] Valid CSV parsed: {rel_path} ({len(df)} rows)")

                required_cols = spec.get("required_columns", [])
                missing_cols = [col for col in required_cols if col not in df.columns]
                if not missing_cols:
                    data_score += 5
                    data_checks.append(f"[PASS] All required columns present: {required_cols}")
                else:
                    data_checks.append(f"[FAIL] Missing columns in {rel_path}: {missing_cols}")

                min_rows = spec.get("min_rows", 10)
                if len(df) >= min_rows:
                    data_score += 5
                    data_checks.append(f"[PASS] Minimum dataset size met (has {len(df)} >= {min_rows})")
                else:
                    data_checks.append(f"[WARN] Dataset too small ({len(df)} rows < expected {min_rows})")
            except Exception as e:
                data_checks.append(f"[FAIL] Error reading CSV {rel_path}: {str(e)}")

        elif rel_path.endswith(".json"):
            try:
                with open(data_path, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                data_score += 5
                items = data if isinstance(data, list) else data.get("items", [data])
                data_checks.append(f"[PASS] Valid JSON parsed: {rel_path} ({len(items)} items)")

                req_keys = spec.get("required_json_keys", [])
                if items and isinstance(items[0], dict):
                    first_item_keys = set(items[0].keys())
                    missing_keys = [k for k in req_keys if k not in first_item_keys]
                    if not missing_keys:
                        data_score += 5
                        data_checks.append(f"[PASS] Required JSON keys present: {req_keys}")
                    else:
                        data_checks.append(f"[FAIL] Missing JSON keys: {missing_keys}")
                else:
                    data_checks.append("[WARN] JSON root is not an array of objects")

                min_items = spec.get("min_items", 5)
                if len(items) >= min_items:
                    data_score += 5
                    data_checks.append(f"[PASS] Item count met ({len(items)} >= {min_items})")
                else:
                    data_checks.append(f"[WARN] JSON item count low ({len(items)} < {min_items})")
            except Exception as e:
                data_checks.append(f"[FAIL] Error reading JSON {rel_path}: {str(e)}")

        elif rel_path.endswith(".txt"):
            try:
                with open(data_path, "r", encoding="utf-8") as tf:
                    lines = [line.strip() for line in tf if line.strip()]
                data_score += 5
                data_checks.append(f"[PASS] Valid text file loaded: {rel_path} ({len(lines)} lines)")

                min_lines = spec.get("min_lines", 20)
                if len(lines) >= min_lines:
                    data_score += 10
                    data_checks.append(f"[PASS] Sample review volume met ({len(lines)} >= {min_lines})")
                else:
                    data_checks.append(f"[WARN] Low line count in {rel_path} ({len(lines)} < {min_lines})")
            except Exception as e:
                data_checks.append(f"[FAIL] Error reading TXT {rel_path}: {str(e)}")

    report["categories"]["data_quality"] = {
        "score": min(data_score, 15),
        "max": 15,
        "checks": data_checks
    }

    # ---------------------------------------------------------
    # Pillar 5: Documentation and Prompts (Max: 15 pts)
    # ---------------------------------------------------------
    doc_score = 0
    doc_checks = []

    if readme_file.exists():
        try:
            with open(readme_file, "r", encoding="utf-8") as rf:
                readme_text = rf.read()

            if len(readme_text.split()) >= 100:
                doc_score += 5
                doc_checks.append("[PASS] README contains substantial project documentation")
            else:
                doc_checks.append("[WARN] README is too brief (< 100 words)")

            prompt_indicators = ["vibe-coding", "prompt", "chatgpt", "cursor", "claude", "gemini", "execution strategy"]
            has_prompts = any(term in readme_text.lower() for term in prompt_indicators)
            if has_prompts:
                doc_score += 5
                doc_checks.append("[PASS] Prompt Log documented")
            else:
                doc_checks.append("[FAIL] Missing Prompt Log in README")

            if any(term in readme_text.lower() for term in ["team members", "author", "problem", "solution"]):
                doc_score += 5
                doc_checks.append("[PASS] Team identification and Problem Statement documented")
            else:
                doc_checks.append("[WARN] Please add Team Members and Target Customer sections")
        except Exception as e:
            doc_checks.append(f"[FAIL] Error reading README.md: {str(e)}")
    else:
        doc_checks.append("[FAIL] README.md missing")

    report["categories"]["documentation"] = {
        "score": min(doc_score, 15),
        "max": 15,
        "checks": doc_checks
    }

    # ---------------------------------------------------------
    # Aggregate Totals and Conversion
    # ---------------------------------------------------------
    total_raw = sum(cat["score"] for cat in report["categories"].values())
    report["raw_score"] = total_raw
    report["final_marks"] = round(total_raw / 4.0, 2)
    report["passed"] = total_raw >= 60

    return report


def detect_modified_team() -> list:
    """Detects which team folder was modified using git diff."""
    detected = set()
    commands = [
        ["git", "diff", "--name-only", "target/main...HEAD"],
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        ["git", "diff", "--name-only", "main...HEAD"],
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        ["git", "status", "--porcelain"]
    ]
    for cmd in commands:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                for line in res.stdout.splitlines():
                    f = line.strip().split()[-1]
                    for team_id, spec in TEAM_SPECS.items():
                        if f"teams/{spec['folder']}" in f:
                            detected.add(team_id)
                if detected:
                    return sorted(list(detected))
        except Exception:
            continue
    return list(range(1, 10))


def format_markdown_summary(reports: list) -> str:
    md = []
    md.append("# Retail AI Lab Evaluation Scorecard\n")
    md.append("| Team | Application Name | Raw Score (/100) | Final Marks (/25) | Status |")
    md.append("| :--- | :--- | :---: | :---: | :---: |")

    for r in reports:
        if "error" in r:
            continue
        status = "PASS" if r["passed"] else "NEEDS WORK"
        md.append(f"| Team {r['team_id']} | **{r['name']}** | `{r['raw_score']}/100` | **`{r['final_marks']}/25`** | {status} |")

    md.append("\n---\n")

    for r in reports:
        if "error" in r:
            continue
        md.append(f"### Team {r['team_id']}: {r['name']}")
        md.append(f"- Category: {r['category']}")
        md.append(f"- Final Converted Grade: **{r['final_marks']} / 25 Marks** (`{r['raw_score']}%`)")
        md.append("")
        md.append("| Evaluation Pillar | Score | Max Points | Status |")
        md.append("| :--- | :---: | :---: | :--- |")

        cats = r["categories"]
        for cat_key, cat_data in cats.items():
            name_map = {
                "architecture": "1. Repository Architecture",
                "logic_and_tests": "2. Algorithmic Logic and Unit Tests",
                "ui_readiness": "3. Interactive UI and Dashboard",
                "data_quality": "4. Data Quality and Schema",
                "documentation": "5. Prompt Documentation"
            }
            display_name = name_map.get(cat_key, cat_key.title())
            status_text = "[PASS]" if cat_data["score"] == cat_data["max"] else ("[WARN]" if cat_data["score"] > 0 else "[FAIL]")
            md.append(f"| {display_name} | {cat_data['score']} | {cat_data['max']} | {status_text} |")

        md.append("\nDiagnostic Checks:")
        for cat_data in cats.values():
            for chk in cat_data["checks"]:
                md.append(f"- {chk}")
        md.append("\n")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="Autograder for Retail AI Lab")
    parser.add_argument("--team", type=int, help="Team number (1-9) to grade")
    parser.add_argument("--all", action="store_true", help="Grade all 9 teams")
    parser.add_argument("--detect", action="store_true", help="Detect modified team from git changes")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")
    parser.add_argument("--json-output", type=str, help="Save JSON results to file path")
    parser.add_argument("--github-summary", action="store_true", help="Write summary to $GITHUB_STEP_SUMMARY")
    parser.add_argument("--output", type=str, help="Save report to file path")

    args = parser.parse_args()

    teams_to_grade = []
    if args.team:
        teams_to_grade = [args.team]
    elif args.all:
        teams_to_grade = list(range(1, 10))
    elif args.detect:
        teams_to_grade = detect_modified_team()
    else:
        teams_to_grade = list(range(1, 10))

    reports = [evaluate_team(t) for t in teams_to_grade]

    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as f:
            json.dump(reports, f, indent=2)

    if args.json:
        print(json.dumps(reports, indent=2))
        return

    summary_md = format_markdown_summary(reports)
    print(summary_md)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary_md)

    if args.github_summary and "GITHUB_STEP_SUMMARY" in os.environ:
        summary_path = os.environ["GITHUB_STEP_SUMMARY"]
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("\n" + summary_md + "\n")

    all_passed = all(r.get("passed", False) for r in reports if "error" not in r)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
