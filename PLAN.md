# Quality Agency Support: Sonnet Handoff Plan

## Summary

Build `gititya/Quality-Agency-support` as a local customer-support quality judge agency for B2C and B2B SaaS. The system evaluates support responses, not generates them. It should build one judge at a time, stop for Adi’s approval after each model run, then commit that approved run before moving on.

Use two MLX models only:

| Role | Model |
|---|---|
| Primary | `mlx-community/Qwen3-4B-4bit` |
| Challenger | `mlx-community/Phi-4-mini-instruct-4bit` |

The primary model is the default judge. The challenger model is used for disagreement analysis and learning, not as a fallback.

## Judge Build Order

| Rank | Judge | Failure Type |
|---:|---|---|
| 1 | Source-of-truth judge | Answered without using available policy, account, tool, or KB context |
| 2 | SOP/process adherence judge | Skipped a required workflow step |
| 3 | Unsupported promise judge | Promised outcome, refund, fix, escalation, or timeline without basis |
| 4 | Technical diagnosis judge | Incorrect technical reasoning, missing repro, weak test plan, or fake certainty |
| 5 | Handoff completeness judge | Human agent lacks key context, prior attempts, customer state, or next step |
| 6 | Escalation timing judge | Escalated too late, too early, or without required evidence |
| 7 | Failed-step repetition judge | Asked user to repeat an already failed troubleshooting step |
| 8 | Answer completeness judge | Correct but missing required caveat, instruction, or next step |
| 9 | Actual-question judge | Responded to an adjacent issue instead of the user’s actual question |
| 10 | Customer-input verification judge | Acted before confirming required user/account details |
| 11 | Sensitive-info judge | Requested, exposed, or mishandled unnecessary PII/security data |
| 12 | Concision judge | Bloated, vague, repetitive, or low-signal answer |
| 13 | Friction recovery judge | Ignored frustration, prior effort, or emotional escalation |
| 14 | Next-action judge | No clear owner, next step, timeline, or resolution path |
| 15 | Support-summary judge | Internal note is incomplete, misleading, or not actionable |

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

## Per-Judge Workflow

For each judge, in rank order:

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

Work on branch `judge-factory-v1` and push after every approved commit.

## Learning Additions

Include these in v1, not later:

- **Rubric ablation**: prove whether better rubrics beat fine-tuning.
- **False-safe red-team set**: prioritize catching subtle bad answers that sound polished.
- **Judge disagreement report**: compare Qwen vs Phi vs gold label.
- **Process graph judge**: for SOP/process adherence, score which required workflow step was skipped.

Fine-tuning starts only after the top 3 judges have corrected gold data and baseline reports. First fine-tune target should be one judge with 150-200 examples and 20% held out.

## End-to-End Support Quality Pipeline

After all 15 narrow judges have approved baseline runs, build an E2E pipeline that runs the full judge agency against one support case and produces a single quality review.

This should be a synthesis layer over the judges, not a replacement for them:

- Run all applicable narrow judges on the same ticket/conversation/response bundle.
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

Build this only after the narrow judges exist, because the proof of work is the interpretable judge agency plus the E2E synthesis report.

## Test Plan

- Schema tests for valid and invalid judge inputs.
- Parser tests for malformed or non-JSON model outputs.
- Metrics tests for false-safe rate, false-unsafe rate, disagreement, and span quality.
- Regression tests with at least 10 locked examples per approved judge.
- Model adapter test confirming both MLX model IDs run through the same judge interface.
- Report test confirming every approved run produces reproducible artifacts before commit.
- Wind-up test confirming primary-model failures are bucketed and corrected examples are written before the judge is marked complete.

## Assumptions

- Repo target is `https://github.com/gititya/Quality-Agency-support`.
- Adi approves each model run before it is committed.
- The project remains domain-neutral for B2C and B2B SaaS support.
- Healthcare, diabetes, and personal finance domains are excluded from v1.
- No large model sprawl: only Qwen primary and Phi challenger for v1.
- Fine-tuning is not attempted until prompted baselines and rubric ablations prove what needs to improve.
