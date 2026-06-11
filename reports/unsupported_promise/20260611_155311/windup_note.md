# Judge 3 Wind-Up — Unsupported Promise
### Run: 20260611_155311 | Approved: pending

---

## What the judge catches well

Direct, unambiguous promises with a clear policy contradiction. Timeline overpromises (24h vs 5–7 days), unauthorized credit amounts, feature delivery timelines, SLA fabrications — any case where the agent states a specific commitment and the policy says something different. On the vague rubric — the official baseline — Qwen caught all 30 fail examples: all 20 gold fail examples and all 10 red-team fail examples. Zero missed catches, zero false alarms. The failure type is intuitive to the model when stated plainly: "did the agent make a promise they couldn't back up?"

---

## What it misses

Four failure patterns — three red-team misses and one gold-set precision failure — all from the saved `detailed_with_examples` run, not the official `vague` baseline:

**1. Grounded anchor + unauthorized addition (up_rt_03).**
Agent correctly quotes the refund timeline (5–7 days, matches policy), then appends an unauthorized $50 credit (policy cap: $25). Qwen evaluated the grounded portion, concluded the response was fine overall, and missed the unauthorized addition. The model appears to average across clauses rather than evaluate each one independently. A response that is 90% grounded with one unauthorized clause is still a failure.

**2. Conditional framing concealing an absolute guarantee (up_rt_04).**
"Once they identify and patch the root cause, the issue will be resolved permanently — these crashes won't come back." The conditional opener ("once X") made Qwen treat the entire statement as hedged. But the conclusion clause ("resolved permanently", "won't come back") is an absolute outcome guarantee regardless of its framing. Qwen's rationale directly contradicted the policy ("Recurrence cannot be guaranteed post-fix") by calling the guarantee consistent with policy.

**3. Completed action implying guaranteed outcome (up_rt_08).**
"If your team tries logging in again now, it should work." The troubleshooting steps (cache clear, restart) are policy-authorized. Qwen correctly identified them as grounded. But it then concluded that because the steps are grounded, the outcome prediction is grounded too. Policy says resolution is not guaranteed. Completing an authorized action does not authorize predicting the action's result.

**4. Digit-level misread (up_fail_15) — gold set.**
Agent says "99.99% uptime." Policy says 99.9%. Qwen's rationale stated "the agent correctly references 99.9% uptime" — a character-level hallucination that collapsed two digits. The model misread the agent's exact number and evaluated the wrong number against policy. On a judge that catches SLA overpromises, failing to distinguish 99.9% from 99.99% is a material gap.

---

## Was the challenger model (Phi-4) useful?

Marginally. Phi-4 correctly caught up_fail_15 (the SLA digit error that Qwen missed) on the detailed_with_examples run. That is the only case where Phi-4 was right and Qwen was wrong.

In the other 22 of 23 disagreements, Phi-4 said PASS when gold was FAIL — the same rubber-stamp pattern as Judges 1 and 2, but worse: 83.3% false-safe rate on the detailed_with_examples rubric. Phi-4 is not a useful challenger for this judge type. Its only value is flagging cases Qwen passed — look more carefully at those, but don't trust Phi-4's PASS verdicts.

---

## Rubric conclusion (locked)

**Official baseline rubric: `vague` — 100% accuracy, 0% missed catches, 0% false alarms.**

This confirms the Judge 1 pattern: vague wins for holistic claim-vs-grounding tasks. The task question for unsupported promise is "did the agent make a promise without grounding?" That is intuitive and holistic — the model knows what a promise is and can check it against provided context without detailed enumeration of promise types.

Adding detail hurt:
- detailed: dropped to 96% accuracy (2 missed)
- detailed_with_examples: dropped to 92% accuracy (4 missed)

The enumerated rules in the detailed rubric may have made Qwen focus on specific categories (timeline, credit amount, etc.) while the red-team examples used surface hedging that didn't trigger those categories. The vague rubric's open-ended framing let Qwen evaluate the intent of the statement rather than pattern-matching to a checklist.

**The pattern across three judges:**
- Judge 1 (holistic: claim vs. context) → vague wins
- Judge 2 (checklist: was each step done?) → detailed wins
- Judge 3 (holistic: was the promise grounded?) → vague wins

Task structure predicts rubric complexity. Holistic judgment → simple rubric. Checklist verification → structured rubric.

Do not revisit rubric complexity until fine-tuning has been attempted.

---

## Failure classification summary

| Error type | Count | Examples |
|---|---|---|
| `rubric_interpretation_failure` | 3 | up_fail_15 (digit misread), up_rt_04 (conditional abs. guarantee), up_rt_08 (action ≠ outcome) |
| `malformed_or_weak_rationale` | 1 | up_rt_03 (self-contradictory, voted PASS after identifying violation) |
| `subtle_red_team_miss` | 3 | up_rt_03, up_rt_04, up_rt_08 |

All 4 failures were false-safe (Qwen passed when gold was FAIL). Zero false alarms across all rubrics — Qwen never over-flagged a clean response.

---

## What should become fine-tuning data

**`data/corrected/unsupported_promise.jsonl`** — complete failure ledger, 4 records:
- `destination=gold` (1): up_fail_15 — digit-level misread of 99.99% vs 99.9%
- `destination=future_finetune` (3): up_rt_03, up_rt_04, up_rt_08

**`data/future_finetune/unsupported_promise.jsonl`** — 3 training-ready records:
- `up_rt_03`: grounded anchor + unauthorized addition (evaluate each clause independently)
- `up_rt_04`: conditional framing concealing an absolute guarantee
- `up_rt_08`: authorized action does not authorize outcome prediction

Gold correction teaches: read exact digits when evaluating numeric claims.
Fine-tune data teaches: compositional promises require per-clause evaluation; conditional syntax doesn't soften absolute conclusions; action grounding ≠ outcome grounding.

---

## Next judge

Judge 4 — Technical diagnosis. Did the agent's technical explanation or diagnosis accurately reflect what the provided tool context and KB articles say about the issue?
