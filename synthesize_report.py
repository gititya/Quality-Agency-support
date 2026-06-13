"""
Synthesize a saved E2E pipeline run into one support QA report.

Usage:
  python synthesize_report.py --run-dir reports/pipeline/<run_id>
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from eval_judges.synthesis import synthesize_pipeline_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-dir",
        required=True,
        help="Pipeline run directory containing case.json, verdicts.jsonl, and run_summary.json",
    )
    parser.add_argument(
        "--output",
        default="support_qa_report.md",
        help="Output markdown filename inside the run directory",
    )
    args = parser.parse_args()

    try:
        output_path = synthesize_pipeline_run(Path(args.run_dir), args.output)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    print(f"Synthesis report written to: {output_path}")


if __name__ == "__main__":
    main()
