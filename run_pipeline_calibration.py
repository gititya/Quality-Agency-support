"""
Run the pipeline calibration set against the current Qwen judge stack.

Usage:
  python3 run_pipeline_calibration.py
  python3 run_pipeline_calibration.py --input data/future_finetune/pipeline_calibration.jsonl
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "src"))

from eval_judges.parser import parse_verdict
from eval_judges.pipeline import WINNING_RUBRICS, calibrate_verdict
from eval_judges.prompt_builder import build_prompt


DEFAULT_INPUT = Path("data") / "future_finetune" / "pipeline_calibration.jsonl"
REPORTS_DIR = Path("reports") / "pipeline_calibration"
PRIMARY_MODEL = "mlx-community/Qwen3-4B-4bit"


def load_examples(path: Path) -> list[dict[str, Any]]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def run_calibration_eval(
    examples: list[dict[str, Any]],
    model_id: str = PRIMARY_MODEL,
    inference_fn=None,
) -> list[dict[str, Any]]:
    if inference_fn is None:
        from eval_judges.adapter import run_inference as inference_fn

    results = []
    for i, example in enumerate(examples, start=1):
        judge_id = example["judge_id"]
        rubric = WINNING_RUBRICS[judge_id]
        prompt = build_prompt(judge_id, rubric, example)
        print(f"[{i}/{len(examples)}] {example['example_id']} ({judge_id}) ... ", end="", flush=True)
        t0 = time.time()
        raw_output = inference_fn(model_id, prompt)
        elapsed_s = round(time.time() - t0, 2)
        raw_verdict, parse_errors = parse_verdict(raw_output)
        calibrated_verdict, adjustments, original_verdict = calibrate_verdict(
            judge_id,
            example,
            raw_verdict,
        )
        status = "ok" if not parse_errors else f"errors: {parse_errors}"
        if adjustments:
            status += f"; calibrated: {adjustments}"
        print(f"{elapsed_s}s - {status}")
        results.append({
            "example_id": example["example_id"],
            "example": example,
            "judge_id": judge_id,
            "pattern": example.get("metadata", {}).get("pattern", "unknown"),
            "label": example["label"],
            "raw_model_verdict": raw_verdict,
            "calibrated_verdict": calibrated_verdict,
            "calibration_adjustments": adjustments,
            "original_verdict": original_verdict,
            "parse_errors": parse_errors,
            "raw_output": raw_output,
            "elapsed_s": elapsed_s,
        })
    return results


def compute_calibration_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "raw": _metrics_for_verdict_key(results, "raw_model_verdict"),
        "calibrated": _metrics_for_verdict_key(results, "calibrated_verdict"),
        "calibration_guardrail_activation_count": sum(
            1 for result in results if result["calibration_adjustments"]
        ),
        "calibration_guardrail_activations": dict(Counter(
            adjustment
            for result in results
            for adjustment in result["calibration_adjustments"]
        )),
    }


def _metrics_for_verdict_key(results: list[dict[str, Any]], key: str) -> dict[str, Any]:
    total = len(results)
    json_valid = sum(1 for result in results if result[key] is not None and not result["parse_errors"])
    scoreable = [result for result in results if result[key] is not None and "pass" in result[key]]
    correct = [
        result for result in scoreable
        if result[key].get("pass") == result["label"]
    ]
    misses = [
        result for result in scoreable
        if result[key].get("pass") != result["label"]
    ]
    fail_examples = [result for result in scoreable if result["label"] is False]
    pass_examples = [result for result in scoreable if result["label"] is True]
    false_safe = [result for result in fail_examples if result[key].get("pass") is True]
    false_unsafe = [result for result in pass_examples if result[key].get("pass") is False]
    span_rows = [
        result for result in scoreable
        if result["label"] is False and result[key].get("pass") is False
    ]
    valid_spans = [
        result for result in span_rows
        if _has_valid_failure_evidence(result, result[key])
    ]
    pattern_misses = Counter(result["pattern"] for result in misses)
    scope_drift_misses = pattern_misses.get("judge_scope_drift", 0)

    return {
        "total": total,
        "json_validity_rate": _rate(json_valid, total),
        "scoreable": len(scoreable),
        "binary_accuracy": _rate(len(correct), len(scoreable)),
        "miss_count": len(misses),
        "miss_rate": _rate(len(misses), len(scoreable)),
        "false_safe_rate": _rate(len(false_safe), len(fail_examples)),
        "false_unsafe_rate": _rate(len(false_unsafe), len(pass_examples)),
        "span_correctness": _rate(len(valid_spans), len(span_rows)),
        "scope_drift_count": scope_drift_misses,
        "pattern_misses": dict(pattern_misses),
    }


def _has_valid_failure_evidence(result: dict[str, Any], verdict: dict[str, Any]) -> bool:
    span = verdict.get("exact_failure_span")
    if span:
        example = result["example"]
        allowed_texts = [example.get("agent_response", "")]
        if result["judge_id"] == "handoff_completeness":
            allowed_texts.append(example.get("handoff_note", ""))
        return any(span in text for text in allowed_texts if text)
    return bool(verdict.get("missing_requirement") or verdict.get("evidence_gap"))


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 3)


def write_artifacts(
    run_dir: Path,
    examples: list[dict[str, Any]],
    results: list[dict[str, Any]],
    metrics: dict[str, Any],
    model_id: str,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    with open(run_dir / "results.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
    (run_dir / "failure_review.md").write_text(render_failure_review(results))
    (run_dir / "fine_tune_decision.md").write_text(
        render_fine_tune_decision(metrics, model_id, run_dir.name)
    )
    (run_dir / "examples_snapshot.jsonl").write_text(
        "".join(json.dumps(example) + "\n" for example in examples)
    )


def render_failure_review(results: list[dict[str, Any]]) -> str:
    lines = [
        "# Pipeline Calibration Failure Review",
        "",
    ]
    misses = [
        result for result in results
        if _is_miss(result, "raw_model_verdict") or _is_miss(result, "calibrated_verdict")
    ]
    if not misses:
        lines.append("No raw or calibrated misses were recorded.")
        return "\n".join(lines) + "\n"

    for result in misses:
        raw = result.get("raw_model_verdict") or {}
        calibrated = result.get("calibrated_verdict") or {}
        expected = "PASS" if result["label"] else "FAIL"
        raw_status = _status(raw)
        calibrated_status = _status(calibrated)
        lines += [
            f"## {result['example_id']} - {result['judge_id']}",
            "",
            f"- Pattern: `{result['pattern']}`",
            f"- Expected: {expected}",
            f"- Raw model verdict: {raw_status}",
            f"- Calibrated verdict: {calibrated_status}",
            f"- Calibration adjustments: {', '.join(result['calibration_adjustments']) or 'none'}",
            f"- Likely cause: {_likely_cause(result)}",
            "",
        ]
    return "\n".join(lines)


def render_fine_tune_decision(metrics: dict[str, Any], model_id: str, run_id: str) -> str:
    calibrated = metrics["calibrated"]
    calibrated_miss_rate = calibrated["miss_rate"] or 0.0
    repeated_patterns = {
        pattern: count
        for pattern, count in calibrated["pattern_misses"].items()
        if count >= 3
    }
    recommend_fine_tune = calibrated_miss_rate >= 0.2 or bool(repeated_patterns)
    recommendation = "fine-tune" if recommend_fine_tune else "do not fine-tune yet"

    lines = [
        "# Fine-Tune Decision",
        "",
        f"**Run ID:** {run_id}",
        f"**Model:** {model_id}",
        f"**Recommendation:** {recommendation}",
        "",
        "## Raw Qwen Metrics",
        "",
        "```json",
        json.dumps(metrics["raw"], indent=2),
        "```",
        "",
        "## Calibrated Qwen Metrics",
        "",
        "```json",
        json.dumps(metrics["calibrated"], indent=2),
        "```",
        "",
        "## Guardrails",
        "",
        f"- Activation count: {metrics['calibration_guardrail_activation_count']}",
        f"- Activations: `{metrics['calibration_guardrail_activations']}`",
        "",
        "## Decision Rationale",
        "",
    ]
    if recommend_fine_tune:
        lines += [
            "- Fine-tuning is justified because calibrated misses meet the decision threshold.",
            f"- Repeated calibrated miss patterns: `{repeated_patterns}`",
            "- Training target: corrected verdict JSON behavior for the repeated calibration patterns.",
            "- Holdout split: keep 30% of `pipeline_calibration.jsonl` untouched as eval before any LoRA run.",
        ]
    else:
        lines += [
            "- Do not fine-tune yet.",
            "- Calibrated Qwen is below the miss threshold and no pattern repeats 3+ times after guardrails.",
            "- Prompt + calibration is enough for v1.",
        ]
    lines += [
        "",
        "## Subagent Usage",
        "",
        "- GPT-5.4-mini subagent used: no",
    ]
    return "\n".join(lines) + "\n"


def _is_miss(result: dict[str, Any], key: str) -> bool:
    verdict = result.get(key)
    if verdict is None or "pass" not in verdict:
        return True
    return verdict.get("pass") != result["label"]


def _status(verdict: dict[str, Any]) -> str:
    if not verdict:
        return "PARSE ERROR"
    return "PASS" if verdict.get("pass") else "FAIL"


def _likely_cause(result: dict[str, Any]) -> str:
    pattern = result["pattern"]
    if result["parse_errors"]:
        return "Model output did not parse cleanly."
    if pattern == "negated_promise_safe":
        return "Model treated a refusal to promise as an actual promise."
    if pattern == "invalid_span":
        return "Model used context/checklist text as the failure span or missed omission evidence."
    if pattern == "judge_scope_drift":
        return "Model graded a neighboring judge dimension instead of the active judge."
    if pattern == "real_unsupported_promise":
        return "Model missed a real unsupported commitment."
    return "Unexpected miss on a clean control."


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--model", default=PRIMARY_MODEL)
    args = parser.parse_args()

    input_path = Path(args.input)
    examples = load_examples(input_path)

    run_id = time.strftime("%Y%m%d_%H%M%S")
    run_dir = REPORTS_DIR / run_id
    results = run_calibration_eval(examples, args.model)
    metrics = compute_calibration_metrics(results)
    write_artifacts(run_dir, examples, results, metrics, args.model)

    print(f"\nArtifacts saved to: {run_dir}")
    print(f"Raw accuracy: {metrics['raw']['binary_accuracy']}")
    print(f"Calibrated accuracy: {metrics['calibrated']['binary_accuracy']}")
    print(f"Decision: {run_dir / 'fine_tune_decision.md'}")


if __name__ == "__main__":
    main()
