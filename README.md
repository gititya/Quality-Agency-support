# Quality Agency Support

This repo tests one question: _Can a small local model review a support response like a QA lead, catch the risky parts, and explain what needs to be fixed?_

The answer is **yes**, for the five support quality areas tested here. This is intended for both B2C & B2B alike. 

## The core idea

Support QA is usually treated as one broad score: **was the answer good or bad?**

That is too vague to be useful because: 
1. A support call can be polite, helpful, and still ignore policy.
2. It can technically be correct, yet still skip a required process step.
3. It can give a good customer answer and still leave the next support agent with a useless handoff. 

This repo breaks support QA into five specialist reviewers:

1. **Source of truth** - did the agent use the policy, account data, tool output, or logs?
2. **SOP/Process adherence** - did the agent follow the required support workflow?
3. **Unsupported promise** - did the agent promise a fix, refund, credit, backfill, escalation, or timeline without authority?
4. **Technical diagnosis** - did the technical explanation actually make sense?
5. **Handoff completeness** - could the next agent continue without making the customer repeat everything?

Each judge gives a structured verdict with pass/fail, confidence, rationale, exact failure span, and a safer requirement.

## What was built

A five-judge evaluation system for customer support AI responses. The stack runs on 2 local MLX models (Qwen3-4B-4bit **primary**, Phi-4-mini-instruct-4bit **challenger**). 

This system can:

1. Run one judge on a labeled example set.
2. Compare rubric variants.
3. Compare Qwen against Phi as a challenger.
4. Save metrics and disagreement reports.
5. Run all five judges on 2 support cases.
6. Synthesize those verdicts into one readable support QA report.
7. Run a calibration eval to decide whether fine-tuning is worth doing.

The important part is that the report does not hide the evidence. It shows which judge passed or failed, what text caused the failure, what requirement was missing, and when a deterministic calibration guardrail changed a model verdict.


### For each judge:

1. Built gold pass/fail examples.
2. Built red-team examples that sound polished but should fail.
3. Tested three rubric styles: vague, detailed, detailed with examples.
4. Ran Qwen and Phi.
5. Measured accuracy, false-safe rate, false-unsafe rate, JSON validity, span quality, and disagreement.
6. Wrote corrected records for the model mistakes.

## The rubric finding

The rubric ablation was the most important experiment, and the result was the opposite of the obvious guess: **the vague rubric won, and adding more detail made the small model worse.**

For the source-of-truth judge on Qwen3-4B:

| Rubric | Accuracy | Missed bad answers (false-safe) | Pinpointed the exact problem (span) |
|---|---:|---:|---:|
| **Vague** | **92%** | **13%** | **87%** |
| Detailed | 72% | 47% | 53% |
| Detailed + examples | 68% | 53% | 47% |

At 4B parameters the model is small enough that a detailed checklist invites rationalisation: it finds one rule that looks satisfied ("the agent mentioned the policy") and uses it to justify a pass, even when the answer contradicted the policy. More rules meant more escape routes. The vague rubric forced a holistic judgement instead of box-ticking.

The practical implication: when better rubrics do not beat the vague one, the next lever is fine-tuning, not more prompt engineering — which is exactly what the calibration eval below tested.

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

The system supports local support QAs and catches real support quality issues:

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

That would be useful if the model kept making the same mistakes after good prompts and visible guardrails, which did not happen here.

The calibration eval says the current system is already strong enough for the final build:

- The misses are low.
- The misses are not concentrated in one repeated pattern.
- The guardrails are narrow and visible.
- The original model verdicts are preserved.
- The final support QA report remains auditable.

So fine-tuning is left as an optional depth exercise, not required repo work.

If this project is reopened later, the fine-tuning target should be narrow:

> Teach Qwen not to pass a response just because part of it is grounded. Evaluate each claim, step, and handoff element independently, and require explicit evidence.

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
```

