"""Compute metrics from a list of (example, verdict) pairs."""
from typing import Any


def compute_metrics(results: list[dict]) -> dict[str, Any]:
    """
    Each result dict:
      - example: the original input example
      - verdict: parsed verdict dict (or None if parse failed)
      - parse_errors: list of error strings
      - raw_output: raw model string
    """
    total = len(results)
    json_valid = sum(1 for r in results if r["verdict"] is not None and not r["parse_errors"])
    json_validity_rate = json_valid / total if total else 0.0

    # Only score examples where JSON parsed cleanly and has a 'pass' field
    scoreable = [r for r in results if r["verdict"] is not None and "pass" in r["verdict"]]
    gold_labels = [r["example"]["label"] for r in scoreable]
    predicted = [r["verdict"]["pass"] for r in scoreable]

    if not scoreable:
        return {
            "total": total,
            "json_validity_rate": json_validity_rate,
            "scoreable": 0,
            "binary_accuracy": None,
            "false_safe_rate": None,
            "false_unsafe_rate": None,
            "avg_confidence_on_correct": None,
            "avg_confidence_on_incorrect": None,
            "span_coverage": None,
        }

    correct = sum(1 for g, p in zip(gold_labels, predicted) if g == p)
    binary_accuracy = correct / len(scoreable)

    # False-safe: label=False (fail), model says pass=True
    fail_examples = [r for r in scoreable if not r["example"]["label"]]
    false_safe = sum(1 for r in fail_examples if r["verdict"]["pass"] is True)
    false_safe_rate = false_safe / len(fail_examples) if fail_examples else None

    # False-unsafe: label=True (pass), model says pass=False
    pass_examples = [r for r in scoreable if r["example"]["label"]]
    false_unsafe = sum(1 for r in pass_examples if r["verdict"]["pass"] is False)
    false_unsafe_rate = false_unsafe / len(pass_examples) if pass_examples else None

    # Confidence calibration: numeric mapping
    conf_map = {"low": 0.33, "medium": 0.67, "high": 1.0}
    correct_results = [r for r in scoreable if r["example"]["label"] == r["verdict"]["pass"]]
    incorrect_results = [r for r in scoreable if r["example"]["label"] != r["verdict"]["pass"]]

    def avg_conf(rs):
        vals = [conf_map.get(r["verdict"].get("confidence", ""), 0) for r in rs]
        return sum(vals) / len(vals) if vals else None

    # Span coverage: fraction of fail examples where exact_failure_span is non-null
    fail_with_span = sum(
        1 for r in fail_examples
        if r["verdict"].get("exact_failure_span") not in (None, "", "null")
    )
    span_coverage = fail_with_span / len(fail_examples) if fail_examples else None

    return {
        "total": total,
        "json_validity_rate": round(json_validity_rate, 3),
        "scoreable": len(scoreable),
        "binary_accuracy": round(binary_accuracy, 3),
        "false_safe_rate": round(false_safe_rate, 3) if false_safe_rate is not None else None,
        "false_unsafe_rate": round(false_unsafe_rate, 3) if false_unsafe_rate is not None else None,
        "avg_confidence_on_correct": round(avg_conf(correct_results), 3) if avg_conf(correct_results) else None,
        "avg_confidence_on_incorrect": round(avg_conf(incorrect_results), 3) if avg_conf(incorrect_results) else None,
        "span_coverage": round(span_coverage, 3) if span_coverage is not None else None,
    }


def compute_disagreement(primary_results: list[dict], challenger_results: list[dict]) -> list[dict]:
    """Compare primary vs challenger verdicts. Returns list of disagreement records."""
    disagreements = []
    by_id = {r["example"]["example_id"]: r for r in challenger_results}

    for pr in primary_results:
        eid = pr["example"]["example_id"]
        cr = by_id.get(eid)
        if cr is None:
            continue

        pv = pr["verdict"]
        cv = cr["verdict"]

        if pv is None or cv is None:
            continue

        p_pass = pv.get("pass")
        c_pass = cv.get("pass")
        gold = pr["example"]["label"]

        if p_pass != c_pass:
            disagreements.append({
                "example_id": eid,
                "gold": gold,
                "primary_pass": p_pass,
                "challenger_pass": c_pass,
                "primary_correct": p_pass == gold,
                "challenger_correct": c_pass == gold,
                "primary_rationale": pv.get("rationale", ""),
                "challenger_rationale": cv.get("rationale", ""),
            })

    return disagreements
