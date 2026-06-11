import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eval_judges.scorer import compute_metrics, compute_disagreement

def _make_result(example_id, gold, pred_pass, confidence="high", span=None):
    return {
        "example": {"example_id": example_id, "label": gold},
        "verdict": {"pass": pred_pass, "score": 1.0 if pred_pass else 0.2,
                    "confidence": confidence, "exact_failure_span": span},
        "parse_errors": [],
        "raw_output": "",
    }

def test_perfect_accuracy():
    results = [
        _make_result("a", True, True),
        _make_result("b", False, False),
    ]
    m = compute_metrics(results)
    assert m["binary_accuracy"] == 1.0
    assert m["false_safe_rate"] == 0.0
    assert m["false_unsafe_rate"] == 0.0

def test_all_false_safe():
    results = [_make_result(f"f{i}", False, True) for i in range(4)]
    m = compute_metrics(results)
    assert m["false_safe_rate"] == 1.0
    assert m["binary_accuracy"] == 0.0

def test_span_coverage():
    results = [
        _make_result("a", False, False, span="bad phrase"),
        _make_result("b", False, False, span=None),
        _make_result("c", False, False, span="another bad phrase"),
    ]
    m = compute_metrics(results)
    assert m["span_coverage"] == pytest_approx(2/3) if False else abs(m["span_coverage"] - 2/3) < 0.01

def test_no_scoreable_returns_nones():
    results = [{"example": {"example_id": "x", "label": True},
                "verdict": None, "parse_errors": ["bad json"], "raw_output": ""}]
    m = compute_metrics(results)
    assert m["binary_accuracy"] is None

def test_disagreement_detection():
    primary = [
        _make_result("a", False, False),
        _make_result("b", False, True),
    ]
    challenger = [
        _make_result("a", False, True),
        _make_result("b", False, False),
    ]
    disagreements = compute_disagreement(primary, challenger)
    assert len(disagreements) == 2
    ids = {d["example_id"] for d in disagreements}
    assert ids == {"a", "b"}

if __name__ == "__main__":
    tests = [test_perfect_accuracy, test_all_false_safe, test_span_coverage,
             test_no_scoreable_returns_nones, test_disagreement_detection]
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
