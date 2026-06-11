# Judge 1 Wind-Up — Source-of-Truth
### Run: 20260611_114750 | Approved: 2026-06-11

---

## What the judge catches well

Direct contradictions. When an agent stated a specific number that flatly contradicted the policy — wrong refund window, wrong seat threshold, wrong rate limit, fabricated pause feature — Qwen caught it reliably on the vague rubric. The 14 correct fail catches out of 30 total fails were almost all of this type: agent said X, policy said Y, numbers don't match.

---

## What it misses

**Two distinct failure patterns:**

**1. Avoidance without contradiction.** The red-team set was designed around this. If an agent gives a directionally correct but vague answer, deflects to an account manager, says "depends on your billing setup," or says "enough time" instead of "24 hours" — Qwen passes it. The judge currently requires a visible contradiction. It cannot catch an agent who simply refuses to state the fact.

**2. Rationale hallucination.** On 4 of the 10 red-team misses, Qwen's rationale attributed statements to the agent that the agent never made. It said the agent "mentions the 24-hour window" when the agent only said "enough time." It said the agent "mentions next billing cycle" when the agent said "depends on your billing setup." The model invented alignment to justify a pass. This is the most concerning failure mode because the judge thinks it caught something when it didn't.

---

## Was the challenger model (Phi-4) useful?

Partially. Phi-4 caught 3 failures that Qwen missed (sot_fail_18, sot_rt_01, sot_rt_02). On sot_fail_18, Phi-4 correctly flagged the 12-month invoice restriction that Qwen passed. That's a useful second opinion.

However, Phi-4's 80% missed-catch rate and its habit of generating plausible-sounding but wrong rationale (on sot_fail_05 it said "agent correctly stated 90 days, which is consistent with the 30-day grace period") makes it unreliable as a standalone judge. Its value in v1 is: if Phi-4 flags something Qwen passed, look more carefully. Not the other way around.

---

## Rubric conclusion (preserved)

**Vague rubric wins: 92% accuracy vs 68% (detailed+examples).**

More instructions made Qwen worse. The detailed rubric gave the model more escape routes. For a 4B model, a longer checklist means more ways to rationalise a pass rather than a clearer decision boundary. This conclusion stands. Do not revisit rubric complexity until fine-tuning has been attempted and the accuracy ceiling on the vague rubric is established.

---

## Failure classification summary

| Error type | Count | Examples |
|---|---|---|
| `rubric_interpretation_failure` | 5 | fail_02 (internal contradiction), fail_03 (charitable range), fail_11 (evaluated action not grounding), fail_18 (restriction accepted), fail_20 (actor confusion) |
| `overconfident_wrong_verdict` | 3 | fail_02, fail_17 (hallucinated 500=1000), fail_18 |
| `obvious_context_contradiction_miss` | 1 | fail_17 |
| `subtle_red_team_miss` | 10 | all rt_01–10 |
| `malformed_or_weak_rationale` | 4 | rt_04, rt_06, rt_07, rt_08 (rationale hallucinations) |

Rationale hallucination (a subtype of `malformed_or_weak_rationale`) is the highest-priority failure mode for fine-tuning: the model invents agent statements that don't exist in order to justify a pass. 4 confirmed cases in this run.

---

## What should become fine-tuning data

**Immediate priority (high):** rt_02, rt_03, rt_04, rt_05, rt_06, rt_10 — these cover the patterns of vague-answer-passing, no-contradiction-passing, and specific-answer-avoided. All in `data/future_finetune/source_of_truth.jsonl` with corrected verdicts.

**Gold set corrections (6 records):** fail_02 through fail_20 failures are in `data/corrected/source_of_truth.jsonl`. These should be added to the training set once fine-tuning starts — they cover the `rubric_interpretation_failure` patterns that the vague rubric doesn't fully solve.

**Minimum fine-tuning target:** The top 3 judges each need corrected gold + red-team data before fine-tuning begins. This is judge 1 of 3.

---

## Next judge

Judge 2 — SOP/process adherence. Did the agent skip a required step in the workflow?

This is structurally different from source-of-truth: instead of comparing a claim to a fact, the model must track whether a sequence of steps was followed. The failure patterns will be different — expect omission-based failures rather than contradiction-based ones.
