"""Validate that data files are well-formed and labels are consistent."""
import sys, json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def test_gold_labels_are_bool():
    for path in (DATA_DIR / "gold").glob("*.jsonl"):
        for i, ex in enumerate(load_jsonl(path)):
            assert isinstance(ex["label"], bool), f"{path.name} row {i}: label must be bool"

def test_gold_has_required_fields():
    required = {"judge_id", "example_id", "label", "ticket", "agent_response"}
    for path in (DATA_DIR / "gold").glob("*.jsonl"):
        for i, ex in enumerate(load_jsonl(path)):
            missing = required - ex.keys()
            assert not missing, f"{path.name} row {i}: missing fields {missing}"

def test_gold_balanced():
    for path in (DATA_DIR / "gold").glob("*.jsonl"):
        rows = load_jsonl(path)
        passes = sum(1 for r in rows if r["label"] is True)
        fails = sum(1 for r in rows if r["label"] is False)
        assert passes == fails, f"{path.name}: pass={passes} fail={fails} — should be balanced"

def test_red_team_all_fail():
    for path in (DATA_DIR / "red_team").glob("*.jsonl"):
        for i, ex in enumerate(load_jsonl(path)):
            assert ex["label"] is False, f"{path.name} row {i}: red_team examples must all be label=false"

def test_corrected_has_required_fields():
    required = {"example_id", "original_label", "qwen_verdict", "corrected_verdict",
                "error_buckets", "exact_failure_span", "why_qwen_missed",
                "what_judge_should_learn", "destination"}
    for path in (DATA_DIR / "corrected").glob("*.jsonl"):
        for i, ex in enumerate(load_jsonl(path)):
            missing = required - ex.keys()
            assert not missing, f"{path.name} row {i}: missing fields {missing}"

def test_future_finetune_verdicts_are_fail():
    for path in (DATA_DIR / "future_finetune").glob("*.jsonl"):
        if path.name == "pipeline_calibration.jsonl":
            continue
        for i, ex in enumerate(load_jsonl(path)):
            if ex.get("record_type") == "pattern_note":
                continue  # pattern notes are rubric design lessons, not training verdicts
            v = ex.get("corrected_verdict", {})
            assert v.get("pass") is False, f"{path.name} row {i}: future_finetune corrected_verdict must be pass=false"

def test_pipeline_calibration_dataset_contract():
    path = DATA_DIR / "future_finetune" / "pipeline_calibration.jsonl"
    rows = load_jsonl(path)
    required = {"example_id", "judge_id", "label", "ticket", "agent_response",
                "original_model_verdict", "corrected_verdict",
                "why_model_was_wrong", "teaching_note", "metadata"}
    verdict_required = {"pass", "score", "failure_type", "exact_failure_span",
                        "rationale", "safer_requirement", "confidence"}

    assert len(rows) == 40
    pattern_counts = {}
    real_sources = 0
    for i, ex in enumerate(rows):
        missing = required - ex.keys()
        assert not missing, f"pipeline_calibration row {i}: missing fields {missing}"
        verdict = ex["corrected_verdict"]
        missing_verdict = verdict_required - verdict.keys()
        assert not missing_verdict, f"pipeline_calibration row {i}: corrected_verdict missing {missing_verdict}"
        assert ex["label"] == verdict["pass"], f"pipeline_calibration row {i}: label must match corrected verdict"
        if verdict["pass"] is True:
            assert verdict["failure_type"] is None
            assert verdict["exact_failure_span"] is None
        else:
            assert (
                verdict.get("exact_failure_span")
                or verdict.get("missing_requirement")
                or verdict.get("evidence_gap")
            ), f"pipeline_calibration row {i}: fail rows need span or omission evidence"

        pattern = ex["metadata"]["pattern"]
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        if ex["metadata"].get("source") not in ("synthetic_variant", "synthetic_control"):
            real_sources += 1

    assert pattern_counts == {
        "negated_promise_safe": 8,
        "real_unsupported_promise": 8,
        "invalid_span": 8,
        "judge_scope_drift": 8,
        "clean_pass_control": 8,
    }
    assert real_sources >= 10

if __name__ == "__main__":
    tests = [test_gold_labels_are_bool, test_gold_has_required_fields, test_gold_balanced,
             test_red_team_all_fail, test_corrected_has_required_fields,
             test_future_finetune_verdicts_are_fail,
             test_pipeline_calibration_dataset_contract]
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
