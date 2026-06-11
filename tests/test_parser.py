import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eval_judges.parser import parse_verdict

def test_valid_json():
    raw = json.dumps({
        "pass": True, "score": 0.9, "failure_type": None,
        "exact_failure_span": None, "rationale": "ok",
        "safer_requirement": "n/a", "confidence": "high"
    })
    verdict, errors = parse_verdict(raw)
    assert verdict is not None
    assert errors == []
    assert verdict["pass"] is True

def test_markdown_fence_stripped():
    raw = '```json\n{"pass": false, "score": 0.2, "failure_type": "ignored_context", "exact_failure_span": "bad span", "rationale": "bad", "safer_requirement": "fix it", "confidence": "medium"}\n```'
    verdict, errors = parse_verdict(raw)
    assert verdict is not None
    assert errors == []

def test_missing_fields_flagged():
    raw = json.dumps({"pass": True, "score": 0.9})
    verdict, errors = parse_verdict(raw)
    assert verdict is not None
    assert any("missing field" in e for e in errors)

def test_bad_json_returns_none():
    verdict, errors = parse_verdict("the answer is probably fine")
    assert verdict is None
    assert errors == ["could not parse JSON from output"]

def test_invalid_score_range():
    raw = json.dumps({
        "pass": True, "score": 1.5, "failure_type": None,
        "exact_failure_span": None, "rationale": "r",
        "safer_requirement": "s", "confidence": "high"
    })
    verdict, errors = parse_verdict(raw)
    assert any("score" in e for e in errors)

def test_invalid_confidence_value():
    raw = json.dumps({
        "pass": True, "score": 0.8, "failure_type": None,
        "exact_failure_span": None, "rationale": "r",
        "safer_requirement": "s", "confidence": "very_high"
    })
    verdict, errors = parse_verdict(raw)
    assert any("confidence" in e for e in errors)

if __name__ == "__main__":
    tests = [test_valid_json, test_markdown_fence_stripped, test_missing_fields_flagged,
             test_bad_json_returns_none, test_invalid_score_range, test_invalid_confidence_value]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)
