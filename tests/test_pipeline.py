"""Tests for the E2E pipeline: judge selection, artifact writing, skipped judge recording."""
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eval_judges.pipeline import (
    select_judges,
    run_pipeline,
    save_pipeline_artifacts,
    ALL_JUDGES,
    WINNING_RUBRICS,
)

# Minimal valid case — only ticket + agent_response
MINIMAL_CASE = {
    "case_id": "test_case_001",
    "ticket": "My payment keeps failing. Card is valid.",
    "agent_response": "Your card might be expired. Please update your billing info.",
}

# Full case — all optional fields present
FULL_CASE = {
    "case_id": "test_case_002",
    "ticket": "API keys stopped working after password change.",
    "agent_response": "API keys are tied to your account. Reset them in the dashboard.",
    "policy_context": "API keys are account-scoped, not user-scoped. Password changes do not invalidate keys.",
    "tool_context": "Account lookup shows 3 active API keys, all valid.",
    "expected_process": ["verify account", "check key status", "confirm key scope"],
    "handoff_note": "Escalating to account team. Customer cannot authenticate.",
    "conversation": "Customer: my keys stopped working. Agent: have you changed your password?",
}

STUB_VERDICT = json.dumps({
    "pass": True,
    "score": 0.9,
    "failure_type": None,
    "exact_failure_span": None,
    "rationale": "Response is grounded and appropriate.",
    "safer_requirement": "n/a",
    "confidence": "high",
})

STUB_FAIL_VERDICT = json.dumps({
    "pass": False,
    "score": 0.2,
    "failure_type": "unsupported_promise",
    "exact_failure_span": "Your card might be expired",
    "rationale": "Agent stated a cause without diagnostic evidence.",
    "safer_requirement": "Ask for more information before diagnosing.",
    "confidence": "medium",
})


def fake_inference(model_id, prompt):
    return STUB_VERDICT


def fail_inference(model_id, prompt):
    return STUB_FAIL_VERDICT


def bad_inference(model_id, prompt):
    return "not json at all"


def test_judge_selection_minimal_case():
    """Only unsupported_promise and technical_diagnosis apply to a bare case."""
    applicable, skipped = select_judges(MINIMAL_CASE)
    assert "unsupported_promise" in applicable
    assert "technical_diagnosis" in applicable
    assert "source_of_truth" in skipped
    assert "sop_adherence" in skipped
    assert "handoff_completeness" in skipped
    assert set(applicable) | set(skipped) == set(ALL_JUDGES)


def test_judge_selection_full_case():
    """All five judges apply when all context fields are present."""
    applicable, skipped = select_judges(FULL_CASE)
    assert set(applicable) == set(ALL_JUDGES)
    assert skipped == []


def test_judge_selection_with_policy_context():
    """source_of_truth fires when policy_context is present."""
    case = {**MINIMAL_CASE, "policy_context": "Refunds require manager approval."}
    applicable, _ = select_judges(case)
    assert "source_of_truth" in applicable


def test_judge_selection_with_tool_context_only():
    """source_of_truth fires with tool_context even without policy_context."""
    case = {**MINIMAL_CASE, "tool_context": "Account lookup: Pro plan, 90-day history."}
    applicable, _ = select_judges(case)
    assert "source_of_truth" in applicable


def test_judge_selection_with_expected_process():
    """sop_adherence fires when expected_process is present."""
    case = {**MINIMAL_CASE, "expected_process": ["verify identity", "check account"]}
    applicable, _ = select_judges(case)
    assert "sop_adherence" in applicable


def test_judge_selection_with_handoff_note():
    """handoff_completeness fires when handoff_note is present."""
    case = {**MINIMAL_CASE, "handoff_note": "Routing to billing team."}
    applicable, _ = select_judges(case)
    assert "handoff_completeness" in applicable


def test_applicable_plus_skipped_equals_all():
    """applicable + skipped always covers every judge exactly once."""
    for case in [MINIMAL_CASE, FULL_CASE]:
        applicable, skipped = select_judges(case)
        assert sorted(applicable + skipped) == sorted(ALL_JUDGES)


def test_winning_rubrics_all_judges_present():
    """Every judge has a locked winning rubric."""
    for judge_id in ALL_JUDGES:
        assert judge_id in WINNING_RUBRICS, f"{judge_id} missing from WINNING_RUBRICS"
        assert WINNING_RUBRICS[judge_id] in ("vague", "detailed", "detailed_with_examples")


def test_run_pipeline_calls_correct_judges():
    """run_pipeline only calls inference for applicable judges."""
    called = []

    def counting_inference(model_id, prompt):
        called.append(model_id)
        return STUB_VERDICT

    applicable, skipped = select_judges(MINIMAL_CASE)
    result = run_pipeline(MINIMAL_CASE, "fake-model", inference_fn=counting_inference)

    assert result["judges_run"] == applicable
    assert result["judges_skipped"] == skipped
    assert len(result["judge_results"]) == len(applicable)
    assert len(called) == len(applicable)


def test_run_pipeline_records_verdicts():
    """run_pipeline stores verdict and parse_errors per judge."""
    result = run_pipeline(MINIMAL_CASE, "fake-model", inference_fn=fake_inference)

    for jr in result["judge_results"]:
        assert "judge_id" in jr
        assert "rubric" in jr
        assert jr["verdict"] is not None
        assert jr["parse_errors"] == []
        assert "elapsed_s" in jr


def test_run_pipeline_handles_parse_failure():
    """A judge verdict that fails JSON parse is recorded as verdict=None with errors."""
    result = run_pipeline(MINIMAL_CASE, "fake-model", inference_fn=bad_inference)

    for jr in result["judge_results"]:
        assert jr["verdict"] is None
        assert jr["parse_errors"] != []


def test_save_pipeline_artifacts_writes_all_files():
    """save_pipeline_artifacts creates case.json, verdicts.jsonl, run_summary.json, report.md."""
    result = run_pipeline(FULL_CASE, "fake-model", inference_fn=fake_inference)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "test_run"
        save_pipeline_artifacts(run_dir, FULL_CASE, result, "fake-model", "20260101_000000")

        assert (run_dir / "case.json").exists()
        assert (run_dir / "verdicts.jsonl").exists()
        assert (run_dir / "run_summary.json").exists()
        assert (run_dir / "report.md").exists()


def test_save_pipeline_artifacts_case_json_roundtrip():
    """case.json written by the pipeline matches the input case."""
    result = run_pipeline(FULL_CASE, "fake-model", inference_fn=fake_inference)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "test_run"
        save_pipeline_artifacts(run_dir, FULL_CASE, result, "fake-model", "20260101_000000")

        with open(run_dir / "case.json") as f:
            written = json.load(f)
        assert written["case_id"] == FULL_CASE["case_id"]
        assert written["ticket"] == FULL_CASE["ticket"]


def test_save_pipeline_artifacts_verdicts_jsonl():
    """verdicts.jsonl has one line per judge that ran."""
    result = run_pipeline(FULL_CASE, "fake-model", inference_fn=fake_inference)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "test_run"
        save_pipeline_artifacts(run_dir, FULL_CASE, result, "fake-model", "20260101_000000")

        with open(run_dir / "verdicts.jsonl") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        assert len(lines) == len(result["judges_run"])
        judge_ids = {l["judge_id"] for l in lines}
        assert judge_ids == set(result["judges_run"])


def test_save_pipeline_artifacts_run_summary():
    """run_summary.json records judges_run, judges_skipped, and applicability_map."""
    result = run_pipeline(MINIMAL_CASE, "fake-model", inference_fn=fake_inference)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "test_run"
        save_pipeline_artifacts(run_dir, MINIMAL_CASE, result, "fake-model", "20260101_000000")

        with open(run_dir / "run_summary.json") as f:
            summary = json.load(f)

        assert summary["case_id"] == MINIMAL_CASE["case_id"]
        assert set(summary["judges_run"]) == set(result["judges_run"])
        assert set(summary["judges_skipped"]) == set(result["judges_skipped"])
        assert set(summary["applicability_map"].keys()) == set(ALL_JUDGES)

        for j in result["judges_run"]:
            assert summary["applicability_map"][j] is True
        for j in result["judges_skipped"]:
            assert summary["applicability_map"][j] is False


def test_report_md_contains_verdict_table():
    """report.md contains a markdown table with each judge's verdict."""
    result = run_pipeline(FULL_CASE, "fake-model", inference_fn=fake_inference)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "test_run"
        save_pipeline_artifacts(run_dir, FULL_CASE, result, "fake-model", "20260101_000000")

        report = (run_dir / "report.md").read_text()

    assert "## Judge Verdicts" in report
    for judge_id in result["judges_run"]:
        assert judge_id in report


def test_report_md_flags_failures():
    """report.md includes a Failures section when any judge returns FAIL."""
    result = run_pipeline(MINIMAL_CASE, "fake-model", inference_fn=fail_inference)

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "test_run"
        save_pipeline_artifacts(run_dir, MINIMAL_CASE, result, "fake-model", "20260101_000000")

        report = (run_dir / "report.md").read_text()

    assert "## Failures and Flags" in report


if __name__ == "__main__":
    tests = [
        test_judge_selection_minimal_case,
        test_judge_selection_full_case,
        test_judge_selection_with_policy_context,
        test_judge_selection_with_tool_context_only,
        test_judge_selection_with_expected_process,
        test_judge_selection_with_handoff_note,
        test_applicable_plus_skipped_equals_all,
        test_winning_rubrics_all_judges_present,
        test_run_pipeline_calls_correct_judges,
        test_run_pipeline_records_verdicts,
        test_run_pipeline_handles_parse_failure,
        test_save_pipeline_artifacts_writes_all_files,
        test_save_pipeline_artifacts_case_json_roundtrip,
        test_save_pipeline_artifacts_verdicts_jsonl,
        test_save_pipeline_artifacts_run_summary,
        test_report_md_contains_verdict_table,
        test_report_md_flags_failures,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)
