"""
Run the five-judge E2E support quality pipeline on a single support case.

Usage:
  python run_pipeline.py --case path/to/case.json [--model mlx-community/Qwen3-4B-4bit]

The case JSON must have at minimum:
  - ticket: str
  - agent_response: str

Optional fields determine which judges run:
  - policy_context / tool_context  → enables source_of_truth
  - expected_process               → enables sop_adherence
  - handoff_note                   → enables handoff_completeness

unsupported_promise and technical_diagnosis always run.
"""
import sys
import json
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from eval_judges.pipeline import run_pipeline, save_pipeline_artifacts, select_judges

PRIMARY_MODEL = "mlx-community/Qwen3-4B-4bit"
REPORTS_DIR = Path("reports") / "pipeline"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, help="Path to case JSON file")
    parser.add_argument("--model", default=PRIMARY_MODEL)
    args = parser.parse_args()

    case_path = Path(args.case)
    if not case_path.exists():
        print(f"Case file not found: {case_path}", file=sys.stderr)
        sys.exit(1)

    with open(case_path) as f:
        case = json.load(f)

    applicable, skipped = select_judges(case)
    print(f"\nCase: {case.get('case_id', case_path.stem)}")
    print(f"Judges applicable: {applicable}")
    if skipped:
        print(f"Judges skipped (missing context): {skipped}")
    print(f"Model: {args.model}")
    print()

    run_id = time.strftime("%Y%m%d_%H%M%S")
    run_dir = REPORTS_DIR / run_id

    t_start = time.time()
    result = _run_with_progress(case, args.model, applicable)
    total = round(time.time() - t_start, 1)

    save_pipeline_artifacts(run_dir, case, result, args.model, run_id)

    print(f"\nDone in {total}s — artifacts at {run_dir}")
    print()

    # Quick summary table to stdout
    print(f"{'Judge':<26} {'Verdict':<8} {'Confidence':<12} {'Failure type'}")
    print("-" * 70)
    for r in result["judge_results"]:
        v = r["verdict"]
        if v is None:
            print(f"  {r['judge_id']:<24} PARSE ERROR")
            continue
        verdict_str = "PASS" if v.get("pass") else "FAIL"
        confidence = v.get("confidence", "?")
        failure_type = v.get("failure_type") or "—"
        print(f"  {r['judge_id']:<24} {verdict_str:<8} {confidence:<12} {failure_type}")

    print()
    print("Awaiting approval before commit.")


def _run_with_progress(case, model_id, applicable):
    """Wraps run_pipeline to print per-judge timing."""
    import time
    from eval_judges.adapter import run_inference
    from eval_judges.prompt_builder import build_prompt
    from eval_judges.parser import parse_verdict
    from eval_judges.pipeline import WINNING_RUBRICS, calibrate_verdict, select_judges

    _, skipped = select_judges(case)

    judge_results = []
    for judge_id in applicable:
        rubric = WINNING_RUBRICS[judge_id]
        prompt = build_prompt(judge_id, rubric, case)
        print(f"Running {judge_id} ({rubric}) ... ", end="", flush=True)
        t0 = time.time()
        raw = run_inference(model_id, prompt)
        elapsed = round(time.time() - t0, 2)
        verdict, errors = parse_verdict(raw)
        verdict, calibration_adjustments, original_verdict = calibrate_verdict(
            judge_id,
            case,
            verdict,
        )
        status = "ok" if not errors else f"errors: {errors}"
        if calibration_adjustments:
            status += f"; calibrated: {calibration_adjustments}"
        print(f"{elapsed}s — {status}")
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


if __name__ == "__main__":
    main()
