# Quality Agency Support

Local customer support QA judges for B2B and B2C SaaS replies.

This repo tests one question: can a small local model review a support response like a QA lead, catch the risky parts, and explain what needs to be fixed?

The answer is yes, for the five support quality areas tested here.

## About

Support QA is usually treated as one broad score: was the answer good or bad?

That is too vague to be useful. A reply can be polite and still ignore policy. It can be technically correct and still skip a required process step. It can give a good customer answer and still leave the next support agent with a useless handoff.

This repo breaks support QA into five specialist reviewers:

1. **Source of truth** - did the agent use the policy, account data, tool output, or logs?
2. **SOP adherence** - did the agent follow the required support workflow?
3. **Unsupported promise** - did the agent promise a fix, refund, credit, backfill, escalation, or timeline without authority?
4. **Technical diagnosis** - did the technical explanation actually make sense?
5. **Handoff completeness** - could the next agent continue without making the customer repeat everything?

Each judge gives a structured verdict with pass/fail, confidence, rationale, exact failure span, and a safer requirement.

## Description

The final build is a local evaluation system, not a support bot.

It does not answer customers. It reviews support answers.

The system can:

1. Run one judge on a labeled example set.
2. Compare rubric variants.
3. Compare Qwen against Phi as a challenger.
4. Save metrics and disagreement reports.
5. Run all five judges on one support case.
6. Synthesize those verdicts into one readable support QA report.
7. Run a calibration eval to decide whether fine-tuning is worth doing.

The important part is that the report does not hide the evidence. It shows which judge passed or failed, what text caused the failure, what requirement was missing, and when a deterministic calibration guardrail changed a model verdict.

## The one idea

A good support QA system should not ask "does this sound helpful?"

It should ask narrower questions:

- Did the agent use the facts available to them?
- Did they follow the required process?
- Did they create an expectation support cannot meet?
- Did they diagnose the technical issue from evidence?
- Did they give the next agent enough context to act?

That is the whole experiment.

One broad judge is easy to fool. Five narrow judges are easier to inspect.

## What I built and ran

I built five local judges using `mlx-community/Qwen3-4B-4bit` as the primary model and `mlx-community/Phi-4-mini-instruct-4bit` as the challenger.

For each judge:

1. Built gold pass/fail examples.
2. Built red-team examples that sound polished but should fail.
3. Tested three rubric styles: vague, detailed, detailed with examples.
4. Ran Qwen and Phi.
5. Measured accuracy, false-safe rate, false-unsafe rate, JSON validity, span quality, and disagreement.
6. Wrote corrected records for the model mistakes.

Then I built the end-to-end support QA pipeline:

```text
support case
    |
    v
five specialist judges
    |
    v
calibrated verdict artifacts
    |
    v
one support QA report
```

Two realistic support cases are included:

1. `acme_analytics_enterprise_export_billing`
2. `northstar_learning_webhook_secret_rotation`

The Northstar case is the cleaner final case. It produces the intended shape:

| Judge | Result |
|---|---|
| Source of truth | PASS |
| SOP adherence | FAIL |
| Unsupported promise | PASS after calibration |
| Technical diagnosis | PASS |
| Handoff completeness | FAIL |

That is a useful QA outcome. The agent used the logs and diagnosed the issue correctly, but missed the urgency acknowledgement and wrote a weak handoff.

## Final result

The system works as a proof of work for local support QA.

It catches real support quality issues:

- policy misuse
- skipped workflow steps
- risky promises
- overconfident technical reasoning
- thin handoffs

It also records known judge mistakes instead of hiding them. For example, Qwen sometimes misread "I cannot promise a full backfill" as if the agent had promised a full backfill. The pipeline now preserves the original model verdict, applies a visible calibration adjustment, and uses the calibrated verdict in the final QA report.

The calibration eval tested 40 examples:

| Metric | Result |
|---|---:|
| Raw Qwen accuracy | 92.5% |
| Calibrated Qwen accuracy | 95% |
| Calibrated miss rate | 5% |
| JSON validity | 95% |
| Repeated post-guardrail failure pattern | None |

The decision was not to fine-tune yet.

## Why no fine-tuning

Fine-tuning would try to teach the model these judge boundaries internally.

That would be useful if the model kept making the same mistakes after good prompts and visible guardrails.

That did not happen here.

The calibration eval says the current system is already strong enough for the final build:

- The misses are low.
- The misses are not concentrated in one repeated pattern.
- The guardrails are narrow and visible.
- The original model verdicts are preserved.
- The final support QA report remains auditable.

So fine-tuning is left as an optional depth exercise, not required repo work.

If this project is reopened later, the fine-tuning target should be narrow:

> Teach Qwen not to pass a response just because part of it is grounded. Evaluate each claim, step, and handoff element independently, and require explicit evidence.

## What this is not

1. NOT a customer-facing support bot.
2. NOT a support response generator.
3. NOT a replacement for human QA.
4. NOT a claim that five judges cover every support quality issue.
5. NOT a fine-tuned model.
6. NOT a production integration with Zendesk, Intercom, Salesforce, Stripe, or product logs.

It is a local, auditable support QA experiment.

## How to run

Run all tests:

```bash
python3 -m pytest
```

Run one judge baseline:

```bash
python3 run_judge.py source_of_truth --rubric vague
```

Run the five-judge pipeline on a support case:

```bash
python3 run_pipeline.py --case data/cases/northstar_learning_webhook_secret_rotation.json
```

Synthesize a saved pipeline run:

```bash
python3 synthesize_report.py --run-dir reports/pipeline/<run_id>
```

Run the calibration eval:

```bash
python3 run_pipeline_calibration.py
```

MLX inference needs Apple Silicon with Metal access. In a sandboxed session, tests will run, but model inference may need to run outside the sandbox.

## Files

```text
judges/registry.yaml                         judge definitions and rubrics
data/gold/                                   approved pass/fail examples
data/red_team/                               subtle bad answers
data/corrected/                              corrected model mistakes
data/future_finetune/                        possible future training data
data/cases/                                  end-to-end support cases
src/eval_judges/                             parser, prompt builder, scorer, pipeline, synthesis
reports/                                    saved judge runs and pipeline reports
run_judge.py                                per-judge runner
run_pipeline.py                             five-judge support QA runner
synthesize_report.py                        support QA report generator
run_pipeline_calibration.py                 fine-tuning decision eval
experiment-walkthrough.md                   narrative writeup of the experiment
PLAN.md                                     final implementation plan and decision record
CLAUDE.md                                   agent working context
SKILL.md                                    repo status note for future agents
```

## The honest claim

This repo shows how to build a small local QA agency for support responses.

The useful result is not "the model is perfect." It is that the system is inspectable. Every judge has a narrow job. Every verdict has evidence. Known model mistakes are calibrated visibly. Fine-tuning was considered, tested, and rejected for now based on metrics.

That is enough to close the repo as a completed support QA proof of work.
