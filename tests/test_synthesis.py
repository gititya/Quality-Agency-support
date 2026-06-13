"""Tests for Step 5 support QA synthesis over saved pipeline artifacts."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eval_judges.synthesis import (
    build_support_qa_report,
    load_pipeline_artifacts,
    render_support_qa_report,
    synthesize_pipeline_run,
)


CASE = {
    "case_id": "fixture_case",
    "ticket": "Customer needs export fixed and billing credit reviewed.",
    "agent_response": "Engineering will patch it tomorrow and I applied a credit.",
}


def pass_record(judge_id):
    return {
        "judge_id": judge_id,
        "rubric": "vague",
        "verdict": {
            "pass": True,
            "score": 0.9,
            "failure_type": None,
            "exact_failure_span": None,
            "rationale": "The response satisfied this judge.",
            "safer_requirement": "n/a",
            "confidence": "high",
        },
        "parse_errors": [],
        "elapsed_s": 0.1,
    }


def fail_record(judge_id, failure_type, span, safer_requirement, confidence="high"):
    return {
        "judge_id": judge_id,
        "rubric": "vague",
        "verdict": {
            "pass": False,
            "score": 0.2,
            "failure_type": failure_type,
            "exact_failure_span": span,
            "rationale": f"{judge_id} found a support-quality failure.",
            "safer_requirement": safer_requirement,
            "confidence": confidence,
        },
        "parse_errors": [],
        "elapsed_s": 0.1,
    }


def parse_error_record(judge_id):
    return {
        "judge_id": judge_id,
        "rubric": "detailed_with_examples",
        "verdict": None,
        "parse_errors": ["could not parse JSON from output"],
        "elapsed_s": 0.1,
    }


def schema_error_record(judge_id):
    record = pass_record(judge_id)
    record["parse_errors"] = ["missing field: safer_requirement"]
    return record


def write_artifacts(run_dir, records, skipped=None):
    skipped = skipped or []
    run_dir.mkdir(parents=True)
    (run_dir / "case.json").write_text(json.dumps(CASE, indent=2))
    with open(run_dir / "verdicts.jsonl", "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    summary = {
        "run_id": "20260612_000000",
        "case_id": CASE["case_id"],
        "model": "fake-model",
        "judges_run": [record["judge_id"] for record in records],
        "judges_skipped": skipped,
        "total_elapsed_s": 0.3,
        "timestamp": "20260612_000000",
    }
    (run_dir / "run_summary.json").write_text(json.dumps(summary, indent=2))


def test_synthesis_writes_support_qa_report_from_pipeline_artifacts():
    records = [
        pass_record("source_of_truth"),
        fail_record(
            "unsupported_promise",
            "unauthorized_credit",
            "I applied a credit",
            "Do not promise or apply credits without approval.",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, records)

        output_path = synthesize_pipeline_run(run_dir)
        report = output_path.read_text()

    assert output_path.name == "support_qa_report.md"
    assert "# Support QA Synthesis Report" in report
    assert "## What Went Well" in report
    assert "## What Failed" in report
    assert "## Evidence Spans" in report
    assert "## Human Review Needs" in report
    assert "## Prioritized Fixes" in report
    assert "I applied a credit" in report


def test_synthesis_keeps_judge_evidence_visible_and_labels_synthesis():
    records = [
        fail_record(
            "technical_diagnosis",
            "false_certainty",
            "Engineering will patch it tomorrow",
            "Describe uncertainty and route through the supported escalation path.",
            confidence="medium",
        )
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, records)
        artifacts = load_pipeline_artifacts(run_dir)
        structured = build_support_qa_report(artifacts)
        markdown = render_support_qa_report(structured)

    assert structured["judge_evidence"][0]["verdict"]["pass"] is False
    assert "This report uses calibrated verdicts" in markdown
    assert "Judge evidence: Technical diagnosis returned FAIL" in markdown
    assert "Synthesis priority from judge failure" in markdown


def test_risk_and_grade_are_high_when_three_or_more_judges_fail():
    records = [
        fail_record("source_of_truth", "ignored_context", "export service is healthy", "Use the export logs."),
        fail_record("unsupported_promise", "unsupported_patch", "ship a patch", "Do not promise a patch."),
        fail_record("technical_diagnosis", "false_cause", "browser download limit", "Do not invent a cause."),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, records)
        report = build_support_qa_report(load_pipeline_artifacts(run_dir))

    assert report["risk_level"].startswith("High")
    assert report["overall_grade"] == "D"


def test_parse_errors_require_human_review_and_make_grade_incomplete():
    records = [parse_error_record("handoff_completeness")]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, records)
        report = build_support_qa_report(load_pipeline_artifacts(run_dir))

    assert report["risk_level"].startswith("High")
    assert report["overall_grade"].startswith("F")
    assert any("could not be parsed" in item for item in report["human_review_needs"])


def test_human_review_needs_are_judge_specific():
    records = [
        fail_record(
            "source_of_truth",
            "ignored_context",
            "export service is healthy",
            "Use the export logs and policy context.",
        ),
        fail_record(
            "unsupported_promise",
            "unsupported_promise",
            "ship a patch by tomorrow",
            "Remove the unsupported patch timeline.",
        ),
        fail_record(
            "technical_diagnosis",
            "incorrect_diagnosis",
            "browser download limit",
            "Have a technical reviewer verify the diagnosis.",
        ),
        fail_record(
            "sop_adherence",
            "skipped_step",
            "I am checking the workspace now",
            "Complete the required workflow steps.",
        ),
        fail_record(
            "handoff_completeness",
            "incomplete_handoff",
            "Please investigate.",
            "Rewrite the handoff with required context.",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, records)
        report = build_support_qa_report(load_pipeline_artifacts(run_dir))

    needs = report["human_review_needs"]
    assert len(set(needs)) == len(needs)
    assert any("policy/tool context" in item for item in needs)
    assert any("unsupported commitments" in item for item in needs)
    assert any("technical reviewer" in item for item in needs)
    assert any("workflow steps" in item for item in needs)
    assert any("rewrite the handoff" in item for item in needs)


def test_synthesis_uses_missing_requirement_and_evidence_gap():
    record = fail_record(
        "sop_adherence",
        "skipped_step",
        "Escalating this now",
        "Complete the required workflow before escalation.",
    )
    record["verdict"]["missing_requirement"] = "Ask for consent before escalation."
    record["verdict"]["evidence_gap"] = "No consent question appears before escalation."

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, [record])
        report = build_support_qa_report(load_pipeline_artifacts(run_dir))

    assert any(
        "Missing requirement: Ask for consent before escalation." in item
        for item in report["human_review_needs"]
    )
    assert any(
        "Evidence gap: No consent question appears before escalation." in item
        for item in report["human_review_needs"]
    )
    assert any(
        "Missing requirement: Ask for consent before escalation." in item
        and "Evidence gap: No consent question appears before escalation." in item
        for item in report["evidence_spans"]
    )
    assert any(
        "Missing requirement: Ask for consent before escalation." in item
        and "Evidence gap: No consent question appears before escalation." in item
        for item in report["prioritized_fixes"]
    )


def test_synthesis_surfaces_calibration_adjustments():
    record = fail_record(
        "unsupported_promise",
        "unsupported_promise",
        "I cannot promise a full backfill until integrations review.",
        "Do not promise a full backfill.",
    )
    record["original_verdict"] = record["verdict"]
    record["verdict"] = {
        "pass": True,
        "score": 0.9,
        "failure_type": None,
        "exact_failure_span": None,
        "rationale": "Calibration override: refusal to promise is safe.",
        "safer_requirement": "No unsupported-promise correction required.",
        "confidence": "medium",
    }
    record["calibration_adjustments"] = [
        "unsupported_promise_false_positive_negated_commitment"
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, [record])
        report = build_support_qa_report(load_pipeline_artifacts(run_dir))
        markdown = render_support_qa_report(report)

    assert report["overall_grade"] == "A"
    assert "## Calibration Adjustments" in markdown
    assert "Unsupported promise was calibrated from FAIL to PASS" in markdown
    assert "unsupported_promise_false_positive_negated_commitment" in markdown


def test_schema_errors_are_not_counted_as_clean_passes():
    records = [schema_error_record("source_of_truth")]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, records)
        report = build_support_qa_report(load_pipeline_artifacts(run_dir))

    assert report["overall_grade"].startswith("F")
    assert report["what_went_well"] == [
        "Synthesis: no judge-level positives were recorded because no judge returned PASS."
    ]
    assert any("Judge evidence incomplete" in item for item in report["what_failed"])


def test_all_passes_get_low_risk_and_no_prioritized_fixes():
    records = [
        pass_record("source_of_truth"),
        pass_record("sop_adherence"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, records)
        report = build_support_qa_report(load_pipeline_artifacts(run_dir))

    assert report["risk_level"].startswith("Low")
    assert report["overall_grade"] == "A"
    assert report["prioritized_fixes"] == [
        "Synthesis: no fixes are prioritized because all parsed judge verdicts passed."
    ]


def test_missing_pipeline_artifact_raises_file_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        run_dir.mkdir()
        (run_dir / "case.json").write_text(json.dumps(CASE))

        try:
            load_pipeline_artifacts(run_dir)
            raised = False
        except FileNotFoundError as exc:
            raised = True
            message = str(exc)

    assert raised is True
    assert "verdicts.jsonl" in message
    assert "run_summary.json" in message


if __name__ == "__main__":
    tests = [
        test_synthesis_writes_support_qa_report_from_pipeline_artifacts,
        test_synthesis_keeps_judge_evidence_visible_and_labels_synthesis,
        test_risk_and_grade_are_high_when_three_or_more_judges_fail,
        test_parse_errors_require_human_review_and_make_grade_incomplete,
        test_human_review_needs_are_judge_specific,
        test_synthesis_uses_missing_requirement_and_evidence_gap,
        test_synthesis_surfaces_calibration_adjustments,
        test_schema_errors_are_not_counted_as_clean_passes,
        test_all_passes_get_low_risk_and_no_prioritized_fixes,
        test_missing_pipeline_artifact_raises_file_not_found,
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
