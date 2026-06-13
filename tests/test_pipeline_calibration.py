import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_pipeline_calibration import (
    compute_calibration_metrics,
    load_examples,
    render_fine_tune_decision,
    run_calibration_eval,
    write_artifacts,
)


DATASET = Path(__file__).parent.parent / "data" / "future_finetune" / "pipeline_calibration.jsonl"


def fake_inference(model_id, prompt):
    if "I cannot promise a full backfill" in prompt:
        return json.dumps({
            "pass": False,
            "score": 0.3,
            "failure_type": "unsupported_promise",
            "exact_failure_span": "I cannot promise a full backfill until integrations review.",
            "rationale": "The agent made an unsupported promise.",
            "safer_requirement": "Avoid promising full backfill.",
            "confidence": "medium",
        })
    if "I am checking the delivery logs now" in prompt:
        return json.dumps({
            "pass": False,
            "score": 0.7,
            "failure_type": "skipped_step",
            "exact_failure_span": "I am checking the delivery logs now.",
            "rationale": "The agent skipped urgency acknowledgement.",
            "missing_requirement": "Acknowledge launch urgency.",
            "evidence_gap": "No urgency acknowledgement appears in the response.",
            "safer_requirement": "Acknowledge urgency.",
            "confidence": "medium",
        })
    return json.dumps({
        "pass": True,
        "score": 1.0,
        "failure_type": None,
        "exact_failure_span": None,
        "rationale": "Clean pass.",
        "safer_requirement": "n/a",
        "confidence": "high",
    })


def test_pipeline_calibration_dataset_loads_40_rows():
    rows = load_examples(DATASET)

    assert len(rows) == 40
    assert rows[0]["example_id"] == "pipe_cal_001"


def test_calibration_eval_preserves_raw_and_calibrated_verdicts():
    rows = load_examples(DATASET)
    examples = [rows[0], rows[16]]
    results = run_calibration_eval(examples, inference_fn=fake_inference)

    assert len(results) == 2
    assert results[0]["raw_model_verdict"]["pass"] is False
    assert results[0]["calibrated_verdict"]["pass"] is True
    assert results[0]["calibration_adjustments"] == [
        "unsupported_promise_false_positive_negated_commitment"
    ]
    assert results[1]["calibrated_verdict"]["exact_failure_span"] is None
    assert results[1]["calibration_adjustments"] == ["invalid_failure_span_removed"]


def test_calibration_metrics_and_artifacts_are_written():
    rows = load_examples(DATASET)
    examples = [rows[0], rows[16], rows[32]]
    results = run_calibration_eval(examples, inference_fn=fake_inference)
    metrics = compute_calibration_metrics(results)

    assert "raw" in metrics
    assert "calibrated" in metrics
    assert metrics["calibration_guardrail_activation_count"] == 2

    decision = render_fine_tune_decision(metrics, "fake-model", "20260101_000000")
    assert "**Recommendation:**" in decision
    assert "GPT-5.4-mini subagent used: no" in decision

    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        write_artifacts(run_dir, examples, results, metrics, "fake-model")

        assert (run_dir / "results.jsonl").exists()
        assert (run_dir / "metrics.json").exists()
        assert (run_dir / "failure_review.md").exists()
        assert (run_dir / "fine_tune_decision.md").exists()
