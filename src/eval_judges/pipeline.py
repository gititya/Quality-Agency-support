"""E2E support quality pipeline over the five completed judges."""
import json
import re
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

from eval_judges.prompt_builder import build_prompt
from eval_judges.parser import parse_verdict

# Locked winning rubric per judge (from approved baseline runs)
WINNING_RUBRICS = {
    "source_of_truth": "vague",
    "sop_adherence": "detailed_with_examples",
    "unsupported_promise": "vague",
    "technical_diagnosis": "detailed_with_examples",
    "handoff_completeness": "detailed_with_examples",
}

ALL_JUDGES = list(WINNING_RUBRICS.keys())

NEGATED_PROMISE_RE = re.compile(
    r"\b(?:cannot|can't|can not|do not|don't)\s+"
    r"(?:promise|guarantee|confirm|commit)\b",
    re.IGNORECASE,
)
POSITIVE_COMMITMENT_RE = re.compile(
    r"\b(?:will|guarantee|promise|committed|confirmed)\b",
    re.IGNORECASE,
)

# A judge is applicable only when its required context fields are present.
# unsupported_promise and technical_diagnosis apply to every case.
def _applicable(judge_id: str, case: dict) -> bool:
    if judge_id == "source_of_truth":
        return bool(case.get("policy_context") or case.get("tool_context"))
    if judge_id == "sop_adherence":
        return bool(case.get("expected_process"))
    if judge_id == "handoff_completeness":
        return bool(case.get("handoff_note"))
    return True  # unsupported_promise, technical_diagnosis


def select_judges(case: dict) -> tuple[list[str], list[str]]:
    """Return (applicable_judges, skipped_judges) for the given case."""
    applicable = [j for j in ALL_JUDGES if _applicable(j, case)]
    skipped = [j for j in ALL_JUDGES if not _applicable(j, case)]
    return applicable, skipped


def run_pipeline(case: dict, model_id: str, inference_fn=None) -> dict[str, Any]:
    """
    Run all applicable judges on a single support case.

    inference_fn: optional callable(model_id, prompt) -> str.
    If None, imports and uses eval_judges.adapter.run_inference lazily.

    Returns a result dict:
    {
        "judges_run": [...],
        "judges_skipped": [...],
        "judge_results": [
            {
                "judge_id": ...,
                "rubric": ...,
                "verdict": ...,
                "parse_errors": [...],
                "elapsed_s": ...
            },
            ...
        ]
    }
    """
    if inference_fn is None:
        from eval_judges.adapter import run_inference as inference_fn

    applicable, skipped = select_judges(case)

    judge_results = []
    for judge_id in applicable:
        rubric = WINNING_RUBRICS[judge_id]
        prompt = build_prompt(judge_id, rubric, case)
        t0 = time.time()
        raw = inference_fn(model_id, prompt)
        elapsed = round(time.time() - t0, 2)
        verdict, errors = parse_verdict(raw)
        verdict, calibration_adjustments, original_verdict = calibrate_verdict(
            judge_id,
            case,
            verdict,
        )
        judge_results.append({
            "judge_id": judge_id,
            "rubric": rubric,
            "verdict": verdict,
            "original_verdict": original_verdict,
            "calibration_adjustments": calibration_adjustments,
            "parse_errors": errors,
            "raw_output": raw,
            "elapsed_s": elapsed,
        })

    return {
        "judges_run": applicable,
        "judges_skipped": skipped,
        "judge_results": judge_results,
    }


def save_pipeline_artifacts(
    run_dir: Path,
    case: dict,
    pipeline_result: dict[str, Any],
    model_id: str,
    run_id: str,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    with open(run_dir / "case.json", "w") as f:
        json.dump(case, f, indent=2)

    with open(run_dir / "verdicts.jsonl", "w") as f:
        for r in pipeline_result["judge_results"]:
            f.write(json.dumps({
                "judge_id": r["judge_id"],
                "rubric": r["rubric"],
                "verdict": r["verdict"],
                "original_verdict": r.get("original_verdict"),
                "calibration_adjustments": r.get("calibration_adjustments", []),
                "parse_errors": r["parse_errors"],
                "elapsed_s": r["elapsed_s"],
            }) + "\n")

    total_elapsed = sum(r["elapsed_s"] for r in pipeline_result["judge_results"])
    run_summary = {
        "run_id": run_id,
        "case_id": case.get("case_id", "unknown"),
        "model": model_id,
        "judges_run": pipeline_result["judges_run"],
        "judges_skipped": pipeline_result["judges_skipped"],
        "applicability_map": {
            j: (j in pipeline_result["judges_run"]) for j in ALL_JUDGES
        },
        "total_elapsed_s": round(total_elapsed, 2),
        "timestamp": run_id,
    }
    with open(run_dir / "run_summary.json", "w") as f:
        json.dump(run_summary, f, indent=2)

    with open(run_dir / "report.md", "w") as f:
        f.write(_render_report(case, pipeline_result, run_summary))


def _render_report(case: dict, result: dict, summary: dict) -> str:
    lines = ["# Support Quality Pipeline Report", ""]
    lines.append(f"**Case ID:** {summary['case_id']}")
    lines.append(f"**Run ID:** {summary['run_id']}")
    lines.append(f"**Model:** {summary['model']}")
    lines.append(f"**Judges run:** {len(summary['judges_run'])} / {len(ALL_JUDGES)}")
    if summary["judges_skipped"]:
        lines.append(f"**Judges skipped (missing context):** {', '.join(summary['judges_skipped'])}")
    lines.append("")

    lines.append("## Case Summary")
    lines.append("")
    if case.get("ticket"):
        lines.append(f"**Ticket:** {case['ticket'][:200]}")
    if case.get("agent_response"):
        lines.append(f"**Agent response:** {case['agent_response'][:200]}")
    lines.append("")

    lines.append("## Judge Verdicts")
    lines.append("")
    lines.append("| Judge | Verdict | Failure Type | Confidence | Span |")
    lines.append("|---|---|---|---|---|")

    flags = []
    for r in result["judge_results"]:
        v = r["verdict"]
        if v is None:
            lines.append(f"| {r['judge_id']} | PARSE ERROR | — | — | — |")
            flags.append(f"- **{r['judge_id']}**: parse error — {r['parse_errors']}")
            continue
        verdict_str = "PASS" if v.get("pass") else "FAIL"
        failure_type = v.get("failure_type") or "—"
        confidence = v.get("confidence") or "—"
        span = v.get("exact_failure_span") or "—"
        if len(span) > 60:
            span = span[:57] + "..."
        lines.append(f"| {r['judge_id']} | {verdict_str} | {failure_type} | {confidence} | {span} |")
        adjustments = r.get("calibration_adjustments") or []
        if not v.get("pass"):
            evidence_gap = v.get("evidence_gap")
            missing_requirement = v.get("missing_requirement")
            extra = ""
            if missing_requirement:
                extra += f" | Missing: `{missing_requirement}`"
            if evidence_gap:
                extra += f" | Evidence gap: `{evidence_gap}`"
            flags.append(
                f"- **{r['judge_id']}** ({v.get('confidence', '?')} confidence): "
                f"{v.get('rationale', '')} | Span: `{v.get('exact_failure_span') or 'n/a'}`"
                f"{extra}"
            )
        elif adjustments:
            flags.append(
                f"- **{r['judge_id']}** calibration adjustment: "
                f"{'; '.join(adjustments)}"
            )

    lines.append("")

    if flags:
        lines.append("## Failures and Flags")
        lines.append("")
        lines.extend(flags)
        lines.append("")

    lines.append(f"*Total inference time: {summary['total_elapsed_s']}s*")
    return "\n".join(lines) + "\n"


def calibrate_verdict(
    judge_id: str,
    case: dict,
    verdict: dict | None,
) -> tuple[dict | None, list[str], dict | None]:
    """Apply deterministic guardrails for known judge-output failure modes."""
    if verdict is None:
        return None, [], None

    calibrated = deepcopy(verdict)
    original_verdict = None
    adjustments = []

    if _is_negated_promise_false_positive(judge_id, calibrated):
        original_verdict = original_verdict or deepcopy(verdict)
        calibrated["pass"] = True
        calibrated["score"] = max(float(calibrated.get("score", 0.0)), 0.9)
        calibrated["failure_type"] = None
        calibrated["exact_failure_span"] = None
        calibrated["rationale"] = (
            "Calibration override: the original unsupported-promise verdict flagged "
            "a refusal to promise or guarantee an outcome, which is safe expectation-setting."
        )
        calibrated["safer_requirement"] = "No unsupported-promise correction required."
        calibrated["confidence"] = "medium"
        calibrated.pop("missing_requirement", None)
        calibrated.pop("evidence_gap", None)
        adjustments.append(
            "unsupported_promise_false_positive_negated_commitment"
        )

    span_adjustment = _calibrate_span(judge_id, case, calibrated)
    if span_adjustment:
        original_verdict = original_verdict or deepcopy(verdict)
        adjustments.append(span_adjustment)

    return calibrated, adjustments, original_verdict


def _calibrate_span(judge_id: str, case: dict, verdict: dict) -> str | None:
    span = verdict.get("exact_failure_span")
    if not span:
        return None

    allowed_texts = [case.get("agent_response", "")]
    if judge_id == "handoff_completeness":
        allowed_texts.append(case.get("handoff_note", ""))

    if any(span in text for text in allowed_texts if text):
        return None

    verdict["exact_failure_span"] = None
    verdict.setdefault(
        "evidence_gap",
        "The judge supplied a failure span from context rather than the evaluated response or handoff.",
    )
    return "invalid_failure_span_removed"


def _is_negated_promise_false_positive(judge_id: str, verdict: dict) -> bool:
    if judge_id != "unsupported_promise":
        return False
    if verdict.get("pass") is not False:
        return False

    span = verdict.get("exact_failure_span") or ""
    if not NEGATED_PROMISE_RE.search(span):
        return False

    remainder = NEGATED_PROMISE_RE.sub("", span)
    return not POSITIVE_COMMITMENT_RE.search(remainder)
