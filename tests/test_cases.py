"""Tests for full-context support cases used by the E2E pipeline."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eval_judges.pipeline import ALL_JUDGES, select_judges


CASE_DIR = Path(__file__).parent.parent / "data" / "cases"
CASE_PATHS = sorted(CASE_DIR.glob("*.json"))


def load_case(path):
    with open(path) as f:
        return json.load(f)


def test_cases_exercise_all_five_judges():
    assert CASE_PATHS, "expected at least one support case fixture"

    for path in CASE_PATHS:
        case = load_case(path)
        applicable, skipped = select_judges(case)

        assert set(applicable) == set(ALL_JUDGES), path.name
        assert skipped == [], path.name


def test_cases_have_required_run_fields():
    for path in CASE_PATHS:
        case = load_case(path)

        assert case["case_id"], path.name
        assert case["ticket"], path.name
        assert case["agent_response"], path.name
        assert case["policy_context"], path.name
        assert case["tool_context"], path.name
        assert case["expected_process"], path.name
        assert case["handoff_note"], path.name


def test_cases_record_design_intent():
    for path in CASE_PATHS:
        case = load_case(path)

        designed_to_exercise = set(case["metadata"]["designed_to_exercise"])

        assert designed_to_exercise == set(ALL_JUDGES), path.name
        assert "case_design_notes" in case["metadata"], path.name
