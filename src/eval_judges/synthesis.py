"""Synthesize pipeline verdict artifacts into one support QA report."""
import json
from pathlib import Path
from typing import Any


JUDGE_LABELS = {
    "source_of_truth": "Source-of-truth",
    "sop_adherence": "SOP/process adherence",
    "unsupported_promise": "Unsupported promise",
    "technical_diagnosis": "Technical diagnosis",
    "handoff_completeness": "Handoff completeness",
}

PRIORITY_ORDER = {
    "source_of_truth": 0,
    "unsupported_promise": 1,
    "technical_diagnosis": 2,
    "sop_adherence": 3,
    "handoff_completeness": 4,
}


def load_pipeline_artifacts(run_dir: Path) -> dict[str, Any]:
    """Load the Step 3 pipeline artifacts needed for Step 5 synthesis."""
    run_dir = Path(run_dir)
    paths = {
        "case": run_dir / "case.json",
        "verdicts": run_dir / "verdicts.jsonl",
        "summary": run_dir / "run_summary.json",
    }

    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing pipeline artifact(s): " + ", ".join(missing)
        )

    with open(paths["case"]) as f:
        case = json.load(f)
    with open(paths["summary"]) as f:
        summary = json.load(f)

    verdicts = []
    with open(paths["verdicts"]) as f:
        for line in f:
            line = line.strip()
            if line:
                verdicts.append(json.loads(line))

    return {
        "case": case,
        "verdicts": verdicts,
        "summary": summary,
        "run_dir": run_dir,
    }


def build_support_qa_report(artifacts: dict[str, Any]) -> dict[str, Any]:
    """Build a structured QA synthesis without changing judge verdicts."""
    verdict_records = artifacts["verdicts"]
    summary = artifacts["summary"]

    passes = []
    failures = []
    parse_errors = []
    missing_spans = []

    for record in verdict_records:
        verdict = record.get("verdict")
        errors = record.get("parse_errors") or []
        if verdict is None or errors:
            parse_errors.append(record)
        if verdict is None or errors:
            continue
        if verdict.get("pass") is True:
            passes.append(record)
        else:
            failures.append(record)
            if not verdict.get("exact_failure_span"):
                missing_spans.append(record)

    human_review_needs = _human_review_needs(
        failures,
        parse_errors,
        missing_spans,
        summary.get("judges_skipped", []),
    )
    calibration_adjustments = _calibration_adjustments(verdict_records)

    return {
        "case_id": summary.get("case_id", "unknown"),
        "run_id": summary.get("run_id", "unknown"),
        "model": summary.get("model", "unknown"),
        "judges_run": summary.get("judges_run", []),
        "judges_skipped": summary.get("judges_skipped", []),
        "what_went_well": _what_went_well(passes),
        "what_failed": _what_failed(failures, parse_errors),
        "risk_level": _risk_level(failures, parse_errors),
        "calibration_adjustments": calibration_adjustments,
        "evidence_spans": _evidence_spans(failures),
        "human_review_needs": human_review_needs,
        "overall_grade": _overall_grade(failures, parse_errors),
        "prioritized_fixes": _prioritized_fixes(failures),
        "judge_evidence": verdict_records,
        "synthesis_notes": [
            "This report uses calibrated verdicts when deterministic guardrails are recorded in the artifacts.",
            "Original model verdicts are preserved in the verdict artifacts when calibration occurs.",
            "Risk level, grade, human-review needs, and fix priority are synthesis derived from judge verdicts.",
            "Evidence spans are judge evidence when supplied by the verdict artifact.",
        ],
    }


def render_support_qa_report(report: dict[str, Any]) -> str:
    """Render the structured synthesis as markdown."""
    lines = [
        "# Support QA Synthesis Report",
        "",
        f"**Case ID:** {report['case_id']}",
        f"**Run ID:** {report['run_id']}",
        f"**Model:** {report['model']}",
        f"**Judges run:** {len(report['judges_run'])}",
    ]
    if report["judges_skipped"]:
        lines.append(f"**Judges skipped:** {', '.join(report['judges_skipped'])}")
    lines += [
        "",
        "## Source Boundary",
        "",
    ]
    for note in report["synthesis_notes"]:
        lines.append(f"- {note}")

    lines += [
        "",
        "## Overall Synthesis",
        "",
        f"- **Risk level:** {report['risk_level']}",
        f"- **Overall grade:** {report['overall_grade']}",
        "",
        "## What Went Well",
        "",
    ]
    lines.extend(_bullet_lines(report["what_went_well"]))

    lines += [
        "",
        "## What Failed",
        "",
    ]
    lines.extend(_bullet_lines(report["what_failed"]))

    if report["calibration_adjustments"]:
        lines += [
            "",
            "## Calibration Adjustments",
            "",
        ]
        lines.extend(_bullet_lines(report["calibration_adjustments"]))

    lines += [
        "",
        "## Evidence Spans",
        "",
    ]
    lines.extend(_bullet_lines(report["evidence_spans"]))

    lines += [
        "",
        "## Human Review Needs",
        "",
    ]
    lines.extend(_bullet_lines(report["human_review_needs"]))

    lines += [
        "",
        "## Prioritized Fixes",
        "",
    ]
    lines.extend(_numbered_lines(report["prioritized_fixes"]))

    lines += [
        "",
        "## Judge Evidence",
        "",
        "| Judge | Verdict | Failure Type | Confidence | Rationale |",
        "|---|---|---|---|---|",
    ]
    for record in report["judge_evidence"]:
        judge_id = record.get("judge_id", "unknown")
        verdict = record.get("verdict")
        errors = record.get("parse_errors") or []
        if verdict is None:
            lines.append(
                f"| {_escape_md(judge_id)} | PARSE ERROR | - | - | {_escape_md('; '.join(errors))} |"
            )
            continue
        verdict_text = "PASS" if verdict.get("pass") else "FAIL"
        failure_type = verdict.get("failure_type") or "-"
        confidence = verdict.get("confidence") or "-"
        rationale = verdict.get("rationale") or "-"
        lines.append(
            f"| {_escape_md(_judge_label(judge_id))} | {verdict_text} | "
            f"{_escape_md(str(failure_type))} | {_escape_md(str(confidence))} | "
            f"{_escape_md(str(rationale))} |"
        )

    return "\n".join(lines) + "\n"


def synthesize_pipeline_run(
    run_dir: Path,
    output_name: str = "support_qa_report.md",
) -> Path:
    """Read pipeline artifacts and write the Step 5 synthesis report."""
    artifacts = load_pipeline_artifacts(Path(run_dir))
    report = build_support_qa_report(artifacts)
    output_path = Path(run_dir) / output_name
    output_path.write_text(render_support_qa_report(report))
    return output_path


def _what_went_well(passes: list[dict[str, Any]]) -> list[str]:
    if not passes:
        return [
            "Synthesis: no judge-level positives were recorded because no judge returned PASS."
        ]
    return [
        (
            f"Judge evidence: {_judge_label(record['judge_id'])} returned PASS"
            f" ({_confidence(record)} confidence): {_rationale(record)}"
        )
        for record in passes
    ]


def _what_failed(
    failures: list[dict[str, Any]],
    parse_errors: list[dict[str, Any]],
) -> list[str]:
    items = []
    for record in _sorted_failures(failures):
        verdict = record["verdict"]
        items.append(
            f"Judge evidence: {_judge_label(record['judge_id'])} returned FAIL"
            f" ({_confidence(record)} confidence)"
            f" on `{verdict.get('failure_type') or 'unspecified_failure'}`:"
            f" {_rationale(record)}"
        )
    for record in parse_errors:
        status = "unavailable" if record.get("verdict") is None else "incomplete"
        items.append(
            f"Judge evidence {status}: {record.get('judge_id', 'unknown')} had parse errors "
            f"({'; '.join(record.get('parse_errors') or [])})."
        )
    if not items:
        items.append("Synthesis: no failed judge verdicts or parse errors were recorded.")
    return items


def _calibration_adjustments(records: list[dict[str, Any]]) -> list[str]:
    items = []
    for record in records:
        adjustments = record.get("calibration_adjustments") or []
        if not adjustments:
            continue
        original = record.get("original_verdict") or {}
        original_status = "FAIL" if original.get("pass") is False else "PASS"
        current = record.get("verdict") or {}
        current_status = "FAIL" if current.get("pass") is False else "PASS"
        items.append(
            f"Synthesis: {_judge_label(record.get('judge_id', 'unknown'))} "
            f"was calibrated from {original_status} to {current_status}: "
            f"{'; '.join(adjustments)}"
        )
    return items


def _evidence_spans(failures: list[dict[str, Any]]) -> list[str]:
    if not failures:
        return ["Judge evidence: no failure spans were supplied because no judge returned FAIL."]

    spans = []
    for record in _sorted_failures(failures):
        verdict = record["verdict"]
        span = verdict.get("exact_failure_span")
        evidence_gap = verdict.get("evidence_gap")
        missing_requirement = verdict.get("missing_requirement")
        if span:
            detail = f"Judge evidence: {_judge_label(record['judge_id'])} span: `{span}`"
            if missing_requirement:
                detail += f" Missing requirement: {missing_requirement}"
            if evidence_gap:
                detail += f" Evidence gap: {evidence_gap}"
            spans.append(detail)
        elif evidence_gap:
            spans.append(
                f"Judge evidence gap: {_judge_label(record['judge_id'])}: "
                f"{evidence_gap}"
            )
        elif missing_requirement:
            spans.append(
                f"Judge missing requirement: {_judge_label(record['judge_id'])}: "
                f"{missing_requirement}"
            )
        else:
            spans.append(
                f"Judge evidence gap: {_judge_label(record['judge_id'])} returned FAIL without an exact span."
            )
    return spans


def _human_review_needs(
    failures: list[dict[str, Any]],
    parse_errors: list[dict[str, Any]],
    missing_spans: list[dict[str, Any]],
    skipped: list[str],
) -> list[str]:
    needs = []
    for record in parse_errors:
        needs.append(
            f"Synthesis: review {record.get('judge_id', 'unknown')} manually because its verdict could not be parsed cleanly."
        )
    for record in _sorted_failures(failures):
        needs.append(_human_review_reason(record))
    for record in missing_spans:
        needs.append(
            f"Synthesis: ask for human span review on {_judge_label(record['judge_id'])}; the judge did not provide an exact failure span."
        )
    for judge_id in skipped:
        needs.append(
            f"Synthesis: {_judge_label(judge_id)} was skipped due to missing context; review manually if that dimension matters for this case."
        )
    if not needs:
        needs.append("Synthesis: no mandatory human-review needs were derived from the judge artifacts.")
    return needs


def _human_review_reason(record: dict[str, Any]) -> str:
    judge_id = record.get("judge_id", "unknown")
    verdict = record.get("verdict") or {}
    span = verdict.get("exact_failure_span")
    missing_requirement = verdict.get("missing_requirement")
    evidence_gap = verdict.get("evidence_gap")
    safer = verdict.get("safer_requirement") or "Revise the response before sending."

    if judge_id == "source_of_truth":
        return _review_line(
            "verify the response against policy/tool context before sending",
            "the judge found ignored or misused source-of-truth evidence",
            span,
            missing_requirement,
            evidence_gap,
            safer,
        )
    if judge_id == "unsupported_promise":
        return _review_line(
            "remove or rewrite unsupported commitments before sending",
            "the judge found a promise without policy, SLA, or approval support",
            span,
            missing_requirement,
            evidence_gap,
            safer,
        )
    if judge_id == "technical_diagnosis":
        return _review_line(
            "have a technical reviewer confirm the diagnosis before sending",
            "the judge found an unsupported or incorrect technical explanation",
            span,
            missing_requirement,
            evidence_gap,
            safer,
        )
    if judge_id == "sop_adherence":
        return _review_line(
            "check the required workflow steps before sending",
            "the judge found a skipped or insufficiently evidenced process step",
            span,
            missing_requirement,
            evidence_gap,
            safer,
        )
    if judge_id == "handoff_completeness":
        return _review_line(
            "rewrite the handoff before escalation",
            "the judge found missing context the receiving agent needs to act",
            span,
            missing_requirement,
            evidence_gap,
            safer,
        )

    return _review_line(
        f"review {_judge_label(judge_id)} before sending",
        "the judge returned a failure verdict",
        span,
        missing_requirement,
        evidence_gap,
        safer,
    )


def _review_line(
    action: str,
    reason: str,
    span: str | None,
    missing_requirement: str | None,
    evidence_gap: str | None,
    safer: str,
) -> str:
    line = f"Synthesis: {action}; {reason}."
    if missing_requirement:
        line += f" Missing requirement: {missing_requirement}."
    if evidence_gap:
        line += f" Evidence gap: {evidence_gap}."
    if span:
        line += f" Review span: `{span}`."
    line += f" Required correction: {safer}"
    return line


def _prioritized_fixes(failures: list[dict[str, Any]]) -> list[str]:
    if not failures:
        return ["Synthesis: no fixes are prioritized because all parsed judge verdicts passed."]

    fixes = []
    for record in _sorted_failures(failures):
        verdict = record["verdict"]
        safer = verdict.get("safer_requirement") or "Revise the response to satisfy this judge."
        span = verdict.get("exact_failure_span")
        missing_requirement = verdict.get("missing_requirement")
        evidence_gap = verdict.get("evidence_gap")
        detail = f"Synthesis priority from judge failure: fix {_judge_label(record['judge_id'])}. {safer}"
        if missing_requirement:
            detail += f" Missing requirement: {missing_requirement}"
        if evidence_gap:
            detail += f" Evidence gap: {evidence_gap}"
        if span:
            detail += f" Target span: `{span}`"
        fixes.append(detail)
    return fixes


def _risk_level(
    failures: list[dict[str, Any]],
    parse_errors: list[dict[str, Any]],
) -> str:
    if parse_errors:
        return "High (synthesis: at least one judge verdict could not be parsed)"
    if len(failures) >= 3:
        return "High (synthesis: three or more judges returned FAIL)"
    if failures:
        return "Medium (synthesis: at least one judge returned FAIL)"
    return "Low (synthesis: all parsed judge verdicts passed)"


def _overall_grade(
    failures: list[dict[str, Any]],
    parse_errors: list[dict[str, Any]],
) -> str:
    if parse_errors:
        return "F (synthesis: incomplete judge evidence due to parse error)"
    fail_count = len(failures)
    if fail_count == 0:
        return "A"
    if fail_count == 1:
        return "B"
    if fail_count == 2:
        return "C"
    if fail_count == 3:
        return "D"
    return "F"


def _sorted_failures(failures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        failures,
        key=lambda record: PRIORITY_ORDER.get(record.get("judge_id"), 99),
    )


def _judge_label(judge_id: str) -> str:
    return JUDGE_LABELS.get(judge_id, judge_id)


def _confidence(record: dict[str, Any]) -> str:
    verdict = record.get("verdict") or {}
    return verdict.get("confidence") or "unknown"


def _rationale(record: dict[str, Any]) -> str:
    verdict = record.get("verdict") or {}
    return verdict.get("rationale") or "No rationale supplied."


def _bullet_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def _numbered_lines(items: list[str]) -> list[str]:
    return [f"{i}. {item}" for i, item in enumerate(items, start=1)]


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
