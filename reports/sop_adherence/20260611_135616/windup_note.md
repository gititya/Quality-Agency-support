# Judge 2 Wind-Up — SOP/Process Adherence
### Run: 20260611_135616 | Approved: pending

---

## What the judge catches well

Missing steps that have a clear absence signal — when the agent goes straight from step A to step C with no trace of step B. The clearest cases: password reset without identity verification (sop_fail_01), refund without eligibility check (sop_fail_02), cancellation without retention offer (sop_fail_04), escalation without consent (sop_fail_05). These are unambiguous omissions and Qwen3 caught them reliably.

---

## What it misses

**Three distinct failure patterns:**

**1. Vague commitment ≠ system action.**
`sop_fail_09` — agent said "I'll pass your feedback along" for a step that required logging to a product backlog system. Qwen passed it. The judge equates verbal promises with concrete system actions. This matters for any step that requires a tool interaction (log to CRM, ticket system, backlog) — the agent can verbally imply it without doing it.

**2. Rationale hallucinations (3 gold-set failures).**
On `sop_fail_10` (data deletion), `sop_fail_17` (complaint follow-up), Qwen invented step completions that don't exist in the response. For sop_fail_10: the explanation step ("here's what gets deleted and this is irreversible") simply isn't in the text — Qwen wrote it into the rationale anyway. For sop_fail_17: "I hope that resolves things" is a closing line, not a follow-up commitment — Qwen called it one. Three hallucinations on gold, all in the false-safe direction.

**3. Self-assertion accepted as step evidence (red-team).**
Four red-team misses follow this pattern: the agent states "I've [done the step]" without showing how. The clearest is `sop_rt_07` — agent says "For security I've verified your identity and confirmed the account owner initiated this request" with no security exchange visible in the interaction. Qwen accepted the claim as proof. Same pattern appears in `sop_rt_05` (escalation accepted as evidence of prior consent), `sop_rt_06` (generic close accepted as receipt confirmation), `sop_rt_10` (ambiguous "I guess if I have to" accepted as explicit confirmation).

---

## Was the challenger model (Phi-4) useful?

Partially. Phi-4 was correct in 3 of the 18 disagreements where Qwen was wrong:

- **sop_fail_09**: Phi correctly flagged "I'll pass your feedback along" as not equivalent to logging in the product backlog system. Qwen passed it.
- **sop_rt_10**: Phi correctly flagged "I guess if I have to" as insufficient for explicit confirmation before an irreversible deletion. Qwen accepted it.
- **sop_pass_02**: Phi correctly identified this as a pass (implicit step completion counts). Qwen wrongly flagged it as a fail.

In the remaining 15 of 18 disagreements, Phi-4 said PASS when gold was FAIL — the same over-agreement pattern as Judge 1.

Phi-4's vague and detailed rubric runs were essentially unusable: 93.3% false-safe rate, 44% accuracy. It was rubber-stamping pass on everything. The detailed+examples rubric improved it to 58% accuracy / 63.3% false-safe — a meaningful improvement, unlike Judge 1 where examples hurt Qwen but helped Phi-4 slightly.

Phi-4's value here is the same as Judge 1: if Phi-4 flags something Qwen passed, look more carefully. Not the other way around.

---

## Rubric conclusion (locked)

**Official baseline rubric: `detailed` — 82% accuracy, 13.3% missed catches.**

This is the opposite of Judge 1, where vague won. The reason: SOP adherence is inherently a checklist task — check that steps A, B, C happened in order. The detailed rubric mirrors this structure. It tells the model to look for each step type, which is exactly what the task requires.

The vague rubric over-flagged heavily: 0% missed catches but 65% false alarms (flagged 13 of 20 pass examples as fails). Too aggressive. The detailed+examples rubric matched detailed's accuracy (82%) but let more bad responses through (23.3% missed vs 13.3%) — examples made Qwen more lenient, not more discriminating.

**Note on saved artifacts:** `primary_outputs.jsonl` and the failure analysis below were generated from the `detailed_with_examples` run, which is what the runner saves by default. That run had 7 missed catches and 2 false alarms at the same 82% accuracy. The detailed and detailed_with_examples runs share 6 of their 9 failures; the remaining 3 differ. The rubric conclusion stands regardless.

Do not revisit rubric complexity until fine-tuning has been attempted.

---

## Failure classification summary

| Error type | Count | Examples |
|---|---|---|
| `malformed_or_weak_rationale` | 5 | fail_10, fail_17, rt_05, rt_06 (hallucinated steps), rt_07 (assertion as evidence) |
| `rubric_interpretation_failure` | 5 | pass_02, pass_04, fail_09, rt_07, rt_10 |
| `span_location_failure` | 1 | pass_04 |
| `subtle_red_team_miss` | 4 | rt_05, rt_06, rt_07, rt_10 |

The dominant failure mode is **rationale hallucination** — Qwen inventing step completions that aren't in the text. 5 of 9 failures involve the model asserting a step was done when it wasn't observable. This is the same pattern as Judge 1 and confirms it's a model-level issue, not rubric-specific.

---

## What should become fine-tuning data

**`data/corrected/sop_adherence.jsonl`** is the complete failure ledger — all 9 Qwen3 failures from the saved `detailed_with_examples` run, each classified with error buckets, failure span, and what the judge should learn. Of the 9 records, 5 have `destination=gold` and 4 have `destination=future_finetune`:

- `destination=gold` (5): sop_pass_02, sop_pass_04, sop_fail_09, sop_fail_10, sop_fail_17
- `destination=future_finetune` (4): sop_rt_05, sop_rt_06, sop_rt_07, sop_rt_10

**`data/future_finetune/sop_adherence.jsonl`** contains the same 4 red-team records in training-ready format with full corrected verdicts (`pass=false`) and failure-pattern metadata. These are the highest-priority training examples:
- `sop_rt_05`: escalation-without-consent + hallucinated documentation
- `sop_rt_06`: generic close substituted for specific receipt confirmation
- `sop_rt_07`: security step asserted without observable exchange
- `sop_rt_10`: ambiguous consent treated as explicit

**Gold corrections teach two things:** sop_pass_02/04 — implicit step completion counts (actions prove steps, not announcements); sop_fail_09/10/17 — vague promise ≠ system action, and rationale hallucinations must be caught.

---

## Next judge

Judge 3 — Unsupported promise. Did the agent promise an outcome, refund, fix, escalation, or timeline without a basis for it?

This is closer to source-of-truth than SOP adherence: the failure is making a claim without grounding, rather than skipping a step. Expect overlap with Judge 1 failure patterns.
