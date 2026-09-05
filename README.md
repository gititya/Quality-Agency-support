# Quality Agency

**For a small local model, the vague rubric beat the detailed one. And the number that matters is how many bad replies the judge waves through, not how many good ones it passes.**

This repo tests one question: _Can a small local model review a support response like a QA lead, catch the risky parts, and explain what needs to be fixed?_

The answer is **yes for clear-cut failures, with a human still reading. The false-safe numbers below say why.** The tests cover five support-quality areas on labeled fixtures; they do not show performance on customer cases.

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

Each judge gives a structured verdict: pass or fail, how confident it is, its reasoning, the exact piece of text that caused the failure, and what a safer reply would have looked like.

## What the judge actually reads

Each judge is a small AI model with one job, which is to read a single support reply and decide whether it holds up. It gets the same three things every time: the customer's question, the reply the agent sent back, and the source material the agent was supposed to rely on, which is usually a policy document or the customer's account data. The judge never sees anything the agent didn't have, so all it is really doing is checking the reply against the facts that were available when it was written.

Here is one fixture from the test set. A customer asks, "What is your refund policy for annual subscriptions?", and the supplied policy says a full refund is available within 30 days, prorated after that. The agent writes back that the refund window is 60 days, and adds that anything later is handled case by case. Both are wrong: the agent doubled the window and invented a fallback that the fixture policy never mentions. The reply reads well, but it does not match its source.

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
5. Measured how often it was right, how often it waved a bad answer through (the false-safe rate), how often it failed a good answer, whether its output came back in the format I asked for, whether it pointed at the exact text that was wrong, and how often it disagreed with the second model.
6. Wrote corrected records for the model mistakes.

A judge was not done when its run finished. For every verdict the model got wrong I classified the miss, wrote a corrected record with the real verdict and the exact failure span, and filed it into the gold set or a future fine-tuning set. Each judge also got a short wind-up note: what it catches, what it misses, and whether the challenger was worth running. Skip that pass and you are left with metrics and no learning.

## The rubric finding

The rubric ablation (the process of trying out the decision with and without the rubrics I choose above) was the most important experiment, and it went the opposite way to what I expected. **The vague rubric won, and adding more detail made the small model worse.**

For the source-of-truth judge on Qwen:

| Rubric | Accuracy | Missed bad answers | Pinpointed the exact problem |
|---|---:|---:|---:|
| **Vague** | **92% (46/50)** | **13% (4/30)** | **87% (26/30)** |
| Detailed | 72% (36/50) | 47% (14/30) | 53% (16/30) |
| Detailed + examples | 68% (34/50) | 53% (16/30) | 47% (14/30) |

The refund example explains why. With the short instructions the model has only one thing to do, which is hold the reply up against the policy and decide whether the two agree, so it notices that 60 days and 30 days don't match and fails the answer. The detailed version, oddly, gets in its own way: it hands the model a checklist (did the agent cite a policy, was the tone professional, did it give a timeframe), and because the reply happens to satisfy most of those boxes, the model decides it is fine and never circles back to the one detail that mattered. The more boxes there are to tick, the easier it is for the model to talk itself into a pass while walking straight past the real mistake.

## Where the models disagreed

Qwen does the actual judging, but I also ran every example through a second model called Phi, purely as a sanity check to see where the two of them would land differently. On the clearly good replies they almost never disagreed; when an answer plainly matched the policy, both passed it without any fuss. The interesting splits were all on the bad answers, which is exactly where it matters.

On the source-of-truth judge the two models disagreed fourteen times. Qwen caught eleven bad replies that Phi had waved through, and Phi caught three that Qwen had missed. Those three were all red-team cases, the deliberately polished-but-wrong replies described above: instead of stating a number that flatly contradicts the policy, they stay vague and talk around it, which makes them genuinely hard to catch.

Phi, though, cannot be trusted to make the call on its own, and one example makes the reason obvious. A reply claimed customer data is kept for 90 days when the policy clearly said 30, the same kind of mismatch as the refund example. Phi not only passed it, it justified itself, writing that the agent "correctly stated 90 days, consistent with the 30-day grace period." There is no grace period anywhere in the policy; Phi invented one to bridge the gap between what the agent said and what the policy said, and then used its own invention to excuse the wrong answer. That is worse than a plain mistake, because the reasoning looks confident and reads as if it checks out. So Phi only ever gets a second opinion: if it flags something Qwen passed, I take another look, but it never decides anything on its own.

Then I built the full five-judge support QA pipeline:

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

Two fictional B2B support cases are included, each written so that all five judges have something to inspect.

The first is Acme Analytics (`acme_analytics_enterprise_export_billing`), an enterprise customer whose large data export keeps timing out after a login-system migration, while they are also disputing a bill for user accounts they say they cancelled. The agent's reply sounds confident but goes wrong in almost every direction: it blames the customer's browser instead of the real cause, which is the size of the file, promises an engineering fix by the next morning that nobody authorised, hands out a $500 credit without finance sign-off, and leaves the next agent a handoff note so thin they would have to start the whole investigation over.

The second is Northstar Learning (`northstar_learning_webhook_secret_rotation`), a customer whose automated messages into their own system stopped going through after they rotated a security key, leaving 36 new signups stranded right before a launch review. This is the cleaner case. The agent does the hard part well, reading the logs and correctly working out that the messages are being rejected because they are still signed with the old key, and it sensibly avoids promising to recover everything. Where it falls short is on the human and procedural side: it never acknowledges how urgent the situation is, it tells the customer to retry before confirming they have fixed their end, and it leaves a handoff that drops most of what the next person would need.

The Northstar case is the one I used for the final saved run, and it produces this result:

| Judge | Result |
|---|---|
| Source of truth | PASS |
| SOP/process adherence | FAIL |
| Unsupported promise | PASS after calibration |
| Technical diagnosis | PASS |
| Handoff completeness | FAIL |

That is a useful QA outcome. The agent used the logs and diagnosed the issue correctly, but missed the urgency acknowledgement and wrote a weak handoff.

## Final result

The system runs locally and flags these support-quality issues in the fixtures:

- policy misuse
- skipped workflow steps
- risky promises
- overconfident technical reasoning
- thin handoffs

One number keeps the rest honest: the false-safe rate, the share of bad answers a judge waves through. Across the three 30-bad-answer source-of-truth runs, Phi missed between 57% (17/30) and 80% (24/30). Qwen missed 47% (14/30) with the detailed rubric and 53% (16/30) with detailed examples. The vague rubric cut Qwen's misses to 13% (4/30), which is why it is the default. Even then, this is a reviewer that flags clear-cut failures before a human reads them. It is not a replacement for the human.

It also keeps its own mistakes out in the open instead of hiding them. Qwen has one habit worth knowing about: it sometimes reads a refused promise as if it were a real one. In the Northstar case the agent wrote, "I cannot promise a full backfill," which is the agent clearly declining to promise anything, and yet Qwen flagged it as an unsupported promise, having latched onto the words "promise a full backfill" without registering the "I cannot" in front of them. Rather than quietly fix the verdict behind the scenes, the pipeline keeps Qwen's original answer on the record, applies a named rule that flips it to the correct call, and shows both versions in the final report, so anyone reading can see exactly what was changed and why. If the rule is ever wrong, it is visible; if the model improves later and stops making the mistake, the rule simply stops firing.

The calibration eval tested 40 examples:

| Metric | Result |
|---|---:|
| Raw Qwen accuracy | 92.5% (37/40) |
| Calibrated Qwen accuracy | 95% (38/40) |
| Calibrated miss rate | 5% (2/40) |
| JSON validity | 95% (38/40) |
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
data/cases/                                  five-judge support cases
src/eval_judges/                             parser, prompt builder, scorer, pipeline, synthesis
reports/                                     saved judge runs and pipeline reports
run_judge.py                                per-judge runner
run_pipeline.py                             five-judge support QA runner
synthesize_report.py                        support QA report generator
run_pipeline_calibration.py                 fine-tuning decision eval
```
