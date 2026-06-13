# Quality Agency Support: Five-Judge Completion Plan

## Summary

`gititya/Quality-Agency-support` is a completed five-judge customer-support QA experiment, not the original 15-judge buildout. The system evaluates support responses, not generates them. The final build includes the five completed judges, an end-to-end support QA pipeline, calibrated QA reports, a 40-example calibration eval set, and a metrics-based decision that fine-tuning is not needed for this completed repo.

Use two MLX models only:

| Role | Model |
|---|---|
| Primary | `mlx-community/Qwen3-4B-4bit` |
| Challenger | `mlx-community/Phi-4-mini-instruct-4bit` |

The primary model is the default judge. The challenger model is used for disagreement analysis and learning, not as a fallback.

## Completed Judge Scope

| Rank | Judge | Failure Type |
|---:|---|---|
| 1 | Source-of-truth | Answered without using available policy, account, tool, or KB context |
| 2 | SOP/process adherence | Skipped a required workflow step |
| 3 | Unsupported promise | Promised outcome, refund, fix, escalation, or timeline without basis |
| 4 | Technical diagnosis | Incorrect technical reasoning, missing repro, weak test plan, or fake certainty |
| 5 | Handoff completeness | Human agent lacks key context, prior attempts, customer state, or next step |

The original plan included ten more judges: escalation timing, failed-step repetition, answer completeness, actual-question, customer-input verification, sensitive-info, concision, friction recovery, next-action, and support-summary. Those are intentionally out of scope for this completed repo. Do not build them unless the project is explicitly reopened.

## Implementation Structure

Create a Python project with these core pieces:

- `judges/registry.yaml`: all judge definitions, rubrics, failure labels, and prompt variants.
- `data/gold/<judge_id>.jsonl`: human-approved pass/fail examples.
- `data/red_team/<judge_id>.jsonl`: subtle false-safe examples.
- `reports/<judge_id>/<run_id>/`: model outputs, metrics, disagreement report, and summary.
- `src/eval_judges/`: model adapter, prompt builder, JSON parser, scorer, report generator.

Use one shared input contract:

```json
{
  "judge_id": "source_of_truth",
  "ticket": "...",
  "agent_response": "...",
  "conversation": "... optional ...",
  "policy_context": "... optional ...",
  "tool_context": "... optional ...",
  "expected_process": ["optional", "ordered", "steps"],
  "handoff_note": "... optional ...",
  "metadata": {}
}
```

Use one shared verdict contract:

```json
{
  "pass": true,
  "score": 0.0,
  "failure_type": "string_or_null",
  "exact_failure_span": "string_or_null",
  "rationale": "short explanation",
  "safer_requirement": "what should have happened",
  "confidence": "low|medium|high"
}
```

## Completed Per-Judge Workflow

Each completed judge followed this workflow:

1. Create 40 seed examples: 20 pass, 20 fail.
2. Create 10 false-safe red-team examples.
3. Add three rubric variants:
   - vague rubric
   - detailed rubric
   - detailed rubric plus examples
4. Run both models:
   - primary: `Qwen3-4B-4bit`
   - challenger: `Phi-4-mini-instruct-4bit`
5. Generate metrics:
   - JSON validity
   - binary accuracy
   - false-safe rate
   - false-unsafe rate
   - exact-span quality
   - primary/challenger disagreement
   - confidence calibration
6. Produce a short report explaining what failed and what the rubric/model missed.
7. Perform the judge wind-up pass:
   - identify all primary-model failures
   - classify each failure into judge-specific error buckets
   - add or update corrected gold, red-team, or future-finetune records
   - preserve the winning rubric-ablation conclusion
   - write a short wind-up note covering what the judge catches, what it misses, whether the challenger helped, and what should become fine-tuning data
8. Stop and ask Adi to approve the run and wind-up artifacts.
9. After approval, commit and push that judge/run before starting the next judge.

A judge is not complete when the model run finishes. A judge is complete only after wind-up, corrected examples, approval, and commit.

Commit message format:

```text
judge: approve <judge-id> baseline run
```

For later fine-tuned runs:

```text
judge: approve <judge-id> lora run <run-id>
```

All five approved baseline runs are merged into `main`.

## Learning Additions

Included in the final build:

- **Rubric ablation**: prove when better rubrics beat model changes.
- **False-safe red-team set**: prioritize catching subtle bad answers that sound polished.
- **Judge disagreement report**: compare Qwen vs Phi vs gold label.
- **Process graph judge**: for SOP/process adherence, score which required workflow step was skipped.

The five completed judges produced enough corrected and future-finetune examples to test whether a focused LoRA would be justified. The calibration eval showed it is not justified for the completed repo: calibrated Qwen reached 95% accuracy on the 40-row calibration set, with no repeated post-guardrail failure pattern crossing the fine-tuning threshold.

## End-to-End Support Quality Pipeline

Build an E2E pipeline that runs the five completed judges against one support case and produces a single quality review.

This should be a synthesis layer over the judges, not a replacement for them:

- Run all five completed judges on the same ticket/conversation/response bundle when inputs are available.
- Collect each judge verdict, exact failure span, confidence, and rationale.
- Feed the collected verdicts into the best available synthesis model.
- Output a support-quality report with:
  - what the agent did well
  - what failed
  - what is risky or uncertain
  - which failures need human review
  - overall quality grade
  - prioritized fix list

The synthesis model must not override judge evidence silently. If it disagrees with a judge, the report should show the disagreement.

The E2E report is the final proof-of-work artifact: the interpretable judge outputs plus one readable QA synthesis.

## Final Fine-Tuning Decision

Fine-tuning was evaluated as a decision, not treated as mandatory work.

The proposed fine-tuning target was:

- Teach Qwen to reduce recurring false-safes across the five judges.
- Do not train a broad generic support judge.
- Do not train on Phi-only failures except as optional contrast notes.

Primary training theme:

> Do not pass a response just because part of it is grounded. Evaluate each claim, step, and handoff element independently, and require explicit evidence.

The calibration set used corrected and future-finetune patterns from the five completed judges, especially:

- source-of-truth: avoidance without contradiction, rationale hallucination
- SOP adherence: self-assertion accepted as step evidence
- unsupported promise: grounded anchor plus unauthorized addition
- technical diagnosis: technically credible false certainty
- handoff completeness: inference over verification as a contrast/pattern note

Decision evaluation:

- Build a 40-example calibration set covering negated promises, real unsupported promises, invalid spans, judge-scope drift, and clean pass controls.
- Run base Qwen through the current prompt and calibration stack.
- Compare raw Qwen and calibrated Qwen on accuracy, false-safe rate, false-unsafe rate, span correctness, JSON validity, and recurring failure patterns.
- Fine-tune only if raw or calibrated Qwen still misses 20% or more of the calibration set, or if one pattern repeats 3+ times after guardrails.

Final result from `reports/pipeline_calibration/20260613_193948/fine_tune_decision.md`:

- Raw Qwen accuracy: 92.5%.
- Calibrated Qwen accuracy: 95%.
- Calibrated miss rate: 5%.
- No repeated pattern crossed the 3+ threshold after guardrails.
- Recommendation: do not fine-tune yet.

In customer-support terms: the existing reviewers are already good enough for the final proof-of-work. Fine-tuning would be an extra learning exercise, not a necessary step to make this repo complete.

## Final Completion Sequence

Completed sequence:

1. Repo docs reflect five completed judges and the close-out scope.
2. E2E support quality pipeline runs the five completed judges.
3. Two realistic support cases are saved and run through the pipeline.
4. Pipeline verdicts synthesize into readable support QA reports.
5. Calibration eval tested whether fine-tuning is justified.
6. Fine-tuning decision recorded: prompt plus calibration is enough for the final build.

The repo is complete after the final README update is added later. Do not build more judges or run LoRA fine-tuning unless the project is explicitly reopened as a separate learning exercise.

## Test Plan

- Schema tests for valid and invalid judge inputs.
- Parser tests for malformed or non-JSON model outputs.
- Metrics tests for false-safe rate, false-unsafe rate, disagreement, and span quality.
- Regression tests with at least 10 locked examples per approved judge.
- Model adapter test confirming both MLX model IDs run through the same judge interface.
- Report test confirming every approved run produces reproducible artifacts before commit.
- Wind-up test confirming primary-model failures are bucketed and corrected examples are written before the judge is marked complete.
- E2E pipeline test confirming one support case can run through the five completed judges and produce a synthesis report.
- Calibration decision test/report confirming base Qwen is evaluated before any LoRA work is attempted.

## Assumptions

- Repo target is `https://github.com/gititya/Quality-Agency-support`.
- Adi approves each model run before it is committed.
- The project remains domain-neutral for B2C and B2B SaaS support.
- Healthcare, diabetes, and personal finance domains are excluded from the final build.
- No large model sprawl: only Qwen primary and Phi challenger were used for the final build.
- The repo is considered complete after the five-judge E2E pipeline, synthesis reports, calibration eval, and final README update are committed.
