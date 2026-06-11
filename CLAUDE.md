# CLAUDE.md — eval-judges

## What this project is

A local customer-support quality judge agency for B2C and B2B SaaS. The system evaluates support responses — it does not generate them. Build one judge at a time, stop for Adi's approval after each model run, then commit that approved run before moving on.

Reference: `PLAN.md` — full judge build order, per-judge workflow, implementation structure, and test plan.

## Models

| Role | Model |
|---|---|
| Primary | `mlx-community/Qwen3-4B-4bit` |
| Challenger | `mlx-community/Phi-4-mini-instruct-4bit` |

The primary model is the default judge. The challenger is used for disagreement analysis and learning — not as a fallback.

## Judge build order

| Rank | Judge |
|---:|---|
| 1 | Source-of-truth |
| 2 | SOP/process adherence |
| 3 | Unsupported promise |
| 4 | Technical diagnosis |
| 5 | Handoff completeness |
| 6 | Escalation timing |
| 7 | Failed-step repetition |
| 8 | Answer completeness |
| 9 | Actual-question |
| 10 | Customer-input verification |
| 11 | Sensitive-info |
| 12 | Concision |
| 13 | Friction recovery |
| 14 | Next-action |
| 15 | Support-summary |

## Stack

- Python 3.11
- `mlx-lm` — model inference
- `mlx-community` MLX-format models (Qwen3-4B-4bit, Phi-4-mini-instruct-4bit)
- No TypeScript, no web UI, no server

## Project layout

```
eval-judges/
  judges/
    registry.yaml           # all judge definitions, rubrics, failure labels, prompt variants
  data/
    gold/<judge_id>.jsonl   # human-approved pass/fail examples (40 per judge: 20 pass, 20 fail)
    red_team/<judge_id>.jsonl # subtle false-safe examples (10 per judge)
  reports/<judge_id>/<run_id>/
    model_outputs.jsonl
    metrics.json
    disagreement_report.md
    summary.md
  src/eval_judges/
    adapter.py              # MLX model adapter
    prompt_builder.py       # rubric variant builder
    parser.py               # JSON output parser
    scorer.py               # metrics: accuracy, false-safe rate, disagreement, span quality
    report.py               # report generator
  tests/
  CLAUDE.md
  SKILL.md
  PLAN.md
```

## Per-judge workflow (must follow this order)

1. Create 40 seed examples: 20 pass, 20 fail
2. Create 10 false-safe red-team examples
3. Add three rubric variants: vague / detailed / detailed + examples
4. Run both models (primary: Qwen3-4B-4bit, challenger: Phi-4-mini-instruct-4bit)
5. Generate metrics: JSON validity, binary accuracy, false-safe rate, false-unsafe rate, exact-span quality, primary/challenger disagreement, confidence calibration
6. Produce short report: what failed, what the rubric/model missed
7. **Stop and ask Adi to approve the run**
8. After approval: commit and push, then start next judge

Commit format: `judge: approve <judge-id> baseline run`
Branch: `judge-factory-v1`

## Success state

Each approved judge run has: a metrics file, a disagreement report, a summary, and a locked set of ≥10 regression examples. Fine-tuning starts only after the top 3 judges have corrected gold data and baseline reports.

## What we are NOT doing

- No support response generation — evaluation only
- No models beyond Qwen primary and Phi challenger in v1
- No fine-tuning until prompted baselines and rubric ablations show what needs to improve
- No healthcare, diabetes, or personal finance domains in v1
- No TypeScript

## Teaching style — experiment walkthrough (mandatory after every judge)

After each judge's approved run, write an experiment walkthrough following the style in `/Users/aditya/Documents/Projects/experiments/intent_classifier/experiment-walkthrough.md` and the principles in `teaching-style-guide.md` in that same folder.

**The structure for each judge walkthrough:**

1. **Before you start** — three concepts to get straight for this judge. What failure type it catches, why it matters, and what a naive model misses.
2. **The rubric ablation** — explain vague vs. detailed vs. detailed+examples. State which variant won and why. Make the comparison explicit — don't make Adi infer it.
3. **What the examples teach** — for the seed and red-team sets: what a pass looks like, what a fail looks like, and what makes the red-team examples hard to catch.
4. **Primary model run** — explain the metrics while they're on screen. JSON validity, accuracy, false-safe rate, span quality — not just numbers, but what they mean for this judge's specific failure type.
5. **Challenger run + disagreement** — compare Qwen vs. Phi vs. gold. Where did they agree? Where did they diverge? What does the divergence reveal about the rubric or the failure type?
6. **What this run teaches** — the results lesson, separate from the mechanics lesson. What does this judge's baseline tell you about how hard the failure type is to detect programmatically?

**Teaching principles to follow (from `teaching-style-guide.md`):**

- Why before what. Never explain what a metric is without explaining why it matters for this judge.
- Name failure modes before they appear. If false-safe rate will be high for this judge type, say so before running.
- Explain output while it's on screen. Don't wait until the end.
- Make the before/after comparison explicit. Vague rubric vs. detailed rubric vs. detailed+examples — state the delta, don't imply it.
- Separate the mechanics lesson (how to run the judge) from the results lesson (what the scores mean about support quality evaluation).
- End each stage with a bridge to the next.
- The baseline comparison is always mandatory — rubric ablation is the baseline for prompt engineering, just as the untuned model is the baseline for fine-tuning.

## Wind-up workflow — standing rule after every judge baseline run

Do not treat a judge as complete until this pass is done. Before moving to the next judge:

1. Read `primary_outputs.jsonl` and identify every case where Qwen's verdict was wrong.
2. For each failure, classify into one or more buckets: `obvious_context_contradiction_miss`, `subtle_red_team_miss`, `span_location_failure`, `overconfident_wrong_verdict`, `rubric_interpretation_failure`, `malformed_or_weak_rationale`.
3. Write a corrected record for each failure: original label, Qwen verdict, corrected verdict, exact failure span, why Qwen missed it, what the judge should learn, destination (`gold`, `red_team`, or `future_finetune`).
4. Save corrected gold records to `data/corrected/<judge_id>.jsonl`.
5. Save red-team and nuanced failures to `data/future_finetune/<judge_id>.jsonl` with full corrected verdict.
6. Preserve the winning rubric-ablation conclusion for that judge. Do not reopen it.
7. Write `reports/<judge_id>/<run_id>/windup_note.md` covering: what the judge catches well, what it misses, whether the challenger was useful, and what should become fine-tuning data.
8. Run all tests (`python3 tests/test_parser.py && python3 tests/test_scorer.py && python3 tests/test_data_integrity.py`). All must pass before committing.
9. Show Adi the diff and ask for approval. Do not commit until approved.
10. After approval, commit with message: `judge: approve <judge-id> baseline run` and push before starting the next judge.

## File integrity

CLAUDE.md and SKILL.md are append-only. No wholesale rewrites.
