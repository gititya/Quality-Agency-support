"""Generate markdown reports from run artifacts."""
import json
from datetime import datetime
from pathlib import Path


def save_run_artifacts(
    run_dir: Path,
    primary_results: list[dict],
    challenger_results: list[dict],
    primary_metrics: dict,
    challenger_metrics: dict,
    rubric_comparison: list[dict],
    disagreements: list[dict],
):
    run_dir.mkdir(parents=True, exist_ok=True)

    with open(run_dir / "primary_outputs.jsonl", "w") as f:
        for r in primary_results:
            f.write(json.dumps({
                "example_id": r["example"]["example_id"],
                "gold": r["example"]["label"],
                "verdict": r["verdict"],
                "parse_errors": r["parse_errors"],
                "raw_output": r["raw_output"],
            }) + "\n")

    with open(run_dir / "challenger_outputs.jsonl", "w") as f:
        for r in challenger_results:
            f.write(json.dumps({
                "example_id": r["example"]["example_id"],
                "gold": r["example"]["label"],
                "verdict": r["verdict"],
                "parse_errors": r["parse_errors"],
                "raw_output": r["raw_output"],
            }) + "\n")

    with open(run_dir / "metrics.json", "w") as f:
        json.dump({
            "primary": primary_metrics,
            "challenger": challenger_metrics,
            "rubric_comparison": rubric_comparison,
        }, f, indent=2)

    with open(run_dir / "disagreement_report.md", "w") as f:
        f.write(_disagreement_md(disagreements))

    with open(run_dir / "summary.md", "w") as f:
        f.write(_summary_md(primary_metrics, challenger_metrics, rubric_comparison, disagreements))


def _disagreement_md(disagreements: list[dict]) -> str:
    lines = ["# Disagreement Report", ""]
    if not disagreements:
        lines.append("No disagreements between primary and challenger.")
        return "\n".join(lines)

    lines.append(f"Total disagreements: {len(disagreements)}")
    lines.append("")

    for d in disagreements:
        gold_str = "PASS" if d["gold"] else "FAIL"
        p_str = "PASS" if d["primary_pass"] else "FAIL"
        c_str = "PASS" if d["challenger_pass"] else "FAIL"
        p_correct = "correct" if d["primary_correct"] else "wrong"
        c_correct = "correct" if d["challenger_correct"] else "wrong"

        lines += [
            f"## {d['example_id']}",
            f"- Gold: {gold_str}",
            f"- Primary: {p_str} ({p_correct})",
            f"- Challenger: {c_str} ({c_correct})",
            f"- Primary rationale: {d['primary_rationale']}",
            f"- Challenger rationale: {d['challenger_rationale']}",
            "",
        ]

    return "\n".join(lines)


def _summary_md(primary: dict, challenger: dict, rubric_comparison: list[dict], disagreements: list[dict]) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# Run Summary — {ts}", ""]

    lines += [
        "## Primary model (Qwen3-4B-4bit)",
        _metrics_table(primary),
        "",
        "## Challenger model (Phi-4-mini-instruct-4bit)",
        _metrics_table(challenger),
        "",
    ]

    lines += ["## Rubric ablation", ""]
    lines.append("| Rubric | Accuracy | False-safe rate | Span coverage |")
    lines.append("|---|---|---|---|")
    for rc in rubric_comparison:
        acc = f"{rc['metrics']['binary_accuracy']:.1%}" if rc['metrics']['binary_accuracy'] is not None else "—"
        fsr = f"{rc['metrics']['false_safe_rate']:.1%}" if rc['metrics']['false_safe_rate'] is not None else "—"
        sc = f"{rc['metrics']['span_coverage']:.1%}" if rc['metrics']['span_coverage'] is not None else "—"
        lines.append(f"| {rc['rubric']} | {acc} | {fsr} | {sc} |")

    lines += [
        "",
        f"## Disagreements",
        f"Primary vs challenger disagreements: {len(disagreements)}",
        "",
    ]

    return "\n".join(lines)


def _metrics_table(m: dict) -> str:
    def fmt(v):
        if v is None:
            return "—"
        if isinstance(v, float):
            return f"{v:.1%}"
        return str(v)

    return (
        f"| Metric | Value |\n"
        f"|---|---|\n"
        f"| Total examples | {m['total']} |\n"
        f"| JSON validity | {fmt(m['json_validity_rate'])} |\n"
        f"| Binary accuracy | {fmt(m['binary_accuracy'])} |\n"
        f"| False-safe rate | {fmt(m['false_safe_rate'])} |\n"
        f"| False-unsafe rate | {fmt(m['false_unsafe_rate'])} |\n"
        f"| Span coverage (on fails) | {fmt(m['span_coverage'])} |\n"
        f"| Avg confidence (correct) | {fmt(m['avg_confidence_on_correct'])} |\n"
        f"| Avg confidence (incorrect) | {fmt(m['avg_confidence_on_incorrect'])} |"
    )
