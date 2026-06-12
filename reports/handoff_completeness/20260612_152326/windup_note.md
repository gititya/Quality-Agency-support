# Wind-up Note — handoff_completeness — run 20260612_152326

## What the judge catches well

The handoff_completeness judge (detailed_with_examples rubric) achieved perfect scores on this baseline:

- **100% accuracy, 0% false-safe, 0% false-unsafe** on 50 examples (20 pass, 20 fail, 10 red-team)
- **All red-team examples correctly flagged** — the 10 false-safe traps (handoffs that sound complete but omit one critical element) were all caught
- **High-confidence correct verdicts**: avg confidence 99.3% on correct calls — Qwen was not hedging
- **Full span coverage**: every fail verdict included a specific failure span identifying what was missing

The checklist structure of handoff completeness (6 required elements: identity, problem, prior attempts, findings, urgency, next step) is well-suited to Qwen's pattern-matching strengths. When the rubric explicitly names each element, Qwen checks each one and catches absences reliably.

## What it misses

Zero Qwen failures on the winning rubric — no corrected records needed. `data/corrected/handoff_completeness.jsonl` is empty.

The most notable near-miss pattern visible in the rubric ablation:

- **Vague rubric (86% acc, 35% false-unsafe)**: Without explicit element enumeration, Qwen applied stricter standards than gold labels — it invented requirements not in the rubric and flagged 7 valid handoffs as incomplete. This is the inverse failure mode: over-flagging due to under-specified criteria, not under-flagging due to permissive criteria.
- **Detailed rubric (98% acc, 3.4% false-safe)**: One false-safe remained even with the full checklist. The examples in detailed_with_examples closed this gap by showing concretely what "identity present" and "findings present" look like in a pass vs. fail.

## Was the challenger useful?

Phi got 74% accuracy with 43.3% false-safe across 13 disagreements. Every disagreement was gold=FAIL, Qwen=FAIL (correct), Phi=PASS (wrong). Phi added no signal that Qwen missed.

The pattern across all 13 Phi errors is consistent: **inference over verification**. Phi accepted missing elements by inferring them from context:
- "prior attempts (none provided but implied)"
- "urgency (implied by customer dissatisfaction)"
- "identity (implied customer contacted support)"

This is a fundamental scorer behavior difference, not a rubric sensitivity issue. Phi's false-safe problem on checklist judges is structural — it infers rather than verifies. Phi is not useful as a quality signal for handoff_completeness.

One Phi parse error on hc_rt_06 (missing `confidence` field on detailed_with_examples) — consistent with prior Phi output stability issues on longer prompts.

## What should become fine-tuning data

No Qwen failures to correct. Two patterns documented in `data/future_finetune/handoff_completeness.jsonl`:

1. **hc_ft_pattern_01 (inference_over_verification)**: For any future Phi fine-tuning, 13 examples of Phi inferring missing elements should be used to teach that explicit presence is required, not inferability.

2. **hc_ft_pattern_02 (vague_rubric_false_unsafe)**: Documents the rubric design lesson — vague rubrics on checklist judges cause over-flagging. Confirms the pattern across Judge 2 (SOP) and Judge 5 (handoff_completeness): checklist tasks require explicit element lists.

## Winning rubric

**detailed_with_examples** is the winner:
- 100% acc vs 86% (vague) and 98% (detailed)
- 0% false-safe and 0% false-unsafe — perfect calibration
- The examples anchored what each required element looks like in practice, eliminating both the vague-rubric false-unsafes and the one remaining detailed-rubric false-safe

Pattern confirmed: checklist-type failure modes (Judge 2: SOP adherence, Judge 5: handoff_completeness) both peaked with detailed_with_examples. Holistic failure modes (Judge 1: source_of_truth, Judge 3: unsupported_promise) peaked with detailed. Judge 4 (technical_diagnosis, hybrid) also peaked with detailed_with_examples.

Do not reopen the rubric ablation. detailed_with_examples is locked.
