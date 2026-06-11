"""
Run a judge against gold + red-team examples for all three rubric variants.
Usage: python run_judge.py <judge_id> [--rubric vague|detailed|detailed_with_examples|all]
"""
import sys
import json
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from eval_judges.adapter import run_inference
from eval_judges.prompt_builder import build_prompt
from eval_judges.parser import parse_verdict
from eval_judges.scorer import compute_metrics, compute_disagreement
from eval_judges.report import save_run_artifacts

PRIMARY_MODEL = "mlx-community/Qwen3-4B-4bit"
CHALLENGER_MODEL = "mlx-community/Phi-4-mini-instruct-4bit"

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")


def load_examples(judge_id: str) -> list[dict]:
    gold_path = DATA_DIR / "gold" / f"{judge_id}.jsonl"
    red_team_path = DATA_DIR / "red_team" / f"{judge_id}.jsonl"

    examples = []
    for path in [gold_path, red_team_path]:
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        examples.append(json.loads(line))
    return examples


def run_model_on_examples(
    model_id: str, judge_id: str, rubric: str, examples: list[dict]
) -> list[dict]:
    results = []
    for i, ex in enumerate(examples):
        prompt = build_prompt(judge_id, rubric, ex)
        print(f"  [{i+1}/{len(examples)}] {ex['example_id']} ... ", end="", flush=True)
        t0 = time.time()
        raw = run_inference(model_id, prompt)
        elapsed = time.time() - t0
        verdict, errors = parse_verdict(raw)
        status = "ok" if not errors else f"errors: {errors}"
        print(f"{elapsed:.1f}s — {status}")
        results.append({
            "example": ex,
            "verdict": verdict,
            "parse_errors": errors,
            "raw_output": raw,
        })
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("judge_id", help="e.g. source_of_truth")
    parser.add_argument("--rubric", default="all",
                        choices=["vague", "detailed", "detailed_with_examples", "all"])
    args = parser.parse_args()

    judge_id = args.judge_id
    rubrics = (
        ["vague", "detailed", "detailed_with_examples"]
        if args.rubric == "all"
        else [args.rubric]
    )

    examples = load_examples(judge_id)
    print(f"\nLoaded {len(examples)} examples for judge: {judge_id}")

    run_id = time.strftime("%Y%m%d_%H%M%S")
    run_dir = REPORTS_DIR / judge_id / run_id

    rubric_comparison = []
    all_primary = {}
    all_challenger = {}

    for rubric in rubrics:
        print(f"\n=== Rubric: {rubric} ===")

        print(f"\n--- Primary model ({PRIMARY_MODEL}) ---")
        primary_results = run_model_on_examples(PRIMARY_MODEL, judge_id, rubric, examples)

        print(f"\n--- Challenger model ({CHALLENGER_MODEL}) ---")
        challenger_results = run_model_on_examples(CHALLENGER_MODEL, judge_id, rubric, examples)

        primary_metrics = compute_metrics(primary_results)
        challenger_metrics = compute_metrics(challenger_results)

        rubric_comparison.append({
            "rubric": rubric,
            "metrics": primary_metrics,
            "challenger_metrics": challenger_metrics,
        })

        all_primary[rubric] = primary_results
        all_challenger[rubric] = challenger_results

        print(f"\nPrimary   — accuracy: {primary_metrics['binary_accuracy']}, "
              f"false-safe: {primary_metrics['false_safe_rate']}, "
              f"JSON valid: {primary_metrics['json_validity_rate']}")
        print(f"Challenger — accuracy: {challenger_metrics['binary_accuracy']}, "
              f"false-safe: {challenger_metrics['false_safe_rate']}, "
              f"JSON valid: {challenger_metrics['json_validity_rate']}")

    # Use detailed_with_examples as the primary rubric for the disagreement report
    best_rubric = "detailed_with_examples" if "detailed_with_examples" in rubrics else rubrics[-1]
    best_primary = all_primary[best_rubric]
    best_challenger = all_challenger[best_rubric]
    best_primary_metrics = compute_metrics(best_primary)
    best_challenger_metrics = compute_metrics(best_challenger)
    disagreements = compute_disagreement(best_primary, best_challenger)

    print(f"\n=== Disagreements (on {best_rubric} rubric): {len(disagreements)} ===")
    for d in disagreements:
        gold = "PASS" if d["gold"] else "FAIL"
        print(f"  {d['example_id']} — gold: {gold}, primary: {'PASS' if d['primary_pass'] else 'FAIL'}, "
              f"challenger: {'PASS' if d['challenger_pass'] else 'FAIL'}")

    save_run_artifacts(
        run_dir,
        best_primary,
        best_challenger,
        best_primary_metrics,
        best_challenger_metrics,
        rubric_comparison,
        disagreements,
    )

    print(f"\nArtifacts saved to: {run_dir}")
    print("\nReady for review. Awaiting approval before commit.")


if __name__ == "__main__":
    main()
