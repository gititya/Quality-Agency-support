# Quality Agency Support

This repo tests one question: _Can a small local model review a support response like a QA lead, catch the risky parts, and explain what needs to be fixed?_

The answer is **yes**, for the five support quality areas tested here. It is meant for B2C and B2B support alike.

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
2. Compare rubric variant with a **Vague**, a **detailed** and a **detailed example** set that has some sample graded answers to use as **reference**. 
3. Compare Qwen against Phi as a challenger.
4. Save metrics and disagreement reports.
5. Run all five judges on a support case.
6. Synthesize those verdicts into one readable support QA report.
7. Run a calibration eval to decide whether fine-tuning is worth doing.

The important part is that the report does not hide the evidence. It shows which judge passed or failed, what text caused the failure, what requirement was missing, and when a deterministic calibration guardrail changed a model verdict.


### For each judge:

1. Built gold pass/fail examples - some obvious good and some obvious bad responses for the judge for which the correct answers were pre-decided by me. 
2. Built red-team examples that sound polished but should fail (like trick questions) 
3. Tested three rubric styles: vague, detailed, detailed with examples.
4. Ran Qwen and Phi.
5. Measured accuracy, false-safe rate, false-unsafe rate, JSON validity, span quality, and disagreement.
6. Wrote corrected records for the model mistakes.

A judge was not done when its run finished. For every verdict the model got wrong I classified the miss, wrote a corrected record with the real verdict and the exact failure span, and filed it into the gold set or a future fine-tuning set. Each judge also got a short wind-up note: what it catches, what it misses, and whether the challenger was worth running. Skip that pass and you are left with metrics and no learning.

## The rubric finding

The rubric ablation (the process of trying out the decision with and without the rubrics I choose above) was the most important experiment, and it went the opposite way to what I expected. **The vague rubric won, and adding more detail made the small model worse.**

For the source-of-truth judge on Qwen3-4B:

| Rubric | Accuracy | Missed bad answers  | Pinpointed the exact problem  |
|---|---:|---:|---:|
| **Vague** | **92%** | **13%** | **87%** |
| Detailed | 72% | 47% | 53% |
| Detailed + examples | 68% | 53% | 47% |

At 4B parameters a long checklist backfires. The model finds one rule that looks satisfied ("the agent mentioned the policy") and uses that to wave the answer through, even when the answer contradicts the policy. More rules just give it more excuses. The vague rubric forces it to make one judgement call instead of ticking boxes.

The practical read: when a more detailed rubric does not beat the vague one, the next lever is fine-tuning, not more prompt writing. That is what the calibration eval below set out to test.

## Where the models disagreed

Qwen and Phi almost never argued about the good answers. They split only on the bad ones. When a response was clearly fine, both passed it. Every disagreement was about whether something was wrong.

On the source-of-truth judge there were 14 disagreements. Qwen caught 11 bad answers that Phi let through. Phi caught 3 that Qwen missed, and all 3 were red-team cases: vague, hedging answers that dodge the context without flatly contradicting it. Those 3 are the sharpest picture of what the model still cannot catch.

Phi's worst habit is worth keeping in view. One agent said data was held for 90 days when the policy said 30. Phi passed it and wrote that the agent "correctly stated 90 days, consistent with the 30-day grace period." It invented a reason instead of reading the context. That is why Phi runs as a challenger and not a judge: if it flags something Qwen passed, look closer, but do not trust it on its own.

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
| SOP/process adherence | FAIL |
| Unsupported promise | PASS after calibration |
| Technical diagnosis | PASS |
| Handoff completeness | FAIL |

That is a useful QA outcome. The agent used the logs and diagnosed the issue correctly, but missed the urgency acknowledgement and wrote a weak handoff.

## Final result

The system runs locally and catches real support quality issues:

- policy misuse
- skipped workflow steps
- risky promises
- overconfident technical reasoning
- thin handoffs

One number keeps the rest honest: the false-safe rate, the share of bad answers a judge waves through. It is high. Phi missed between 57% and 80% of bad answers depending on the rubric, and Qwen on the detailed rubrics missed about half. The vague rubric is what pulled Qwen down to 13% on source-of-truth, which is why it is the default. Even then, this is a reviewer that flags the clear-cut failures before a human reads them. It is not a replacement for the human.

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
reports/                                     saved judge runs and pipeline reports
run_judge.py                                per-judge runner
run_pipeline.py                             five-judge support QA runner
synthesize_report.py                        support QA report generator
run_pipeline_calibration.py                 fine-tuning decision eval
```

