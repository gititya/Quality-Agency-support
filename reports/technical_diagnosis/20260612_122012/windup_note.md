# Wind-up Note — technical_diagnosis — run 20260612_122012

## What the judge catches well

The technical_diagnosis judge (detailed_with_examples rubric) reliably catches the four explicit failure modes:

- **false_certainty** on direct cases: When an agent says "definitely" or "always caused by X" or prescribes a fix without hedging, Qwen catches it consistently. All 20 gold fail examples were correctly classified.
- **incorrect_diagnosis** on clear cases: When the named cause mechanically contradicts the symptoms (e.g., blaming network latency for account-specific 504s), Qwen flags it.
- **missing_repro**: When an agent skips diagnostic questions entirely and jumps straight to a fix (browser cache clear for SSO, reindex for search), Qwen catches the absence.
- **weak_test_plan**: "Try again later" and "rerun at off-peak hours" are correctly flagged as non-diagnostic.

Zero false-unsafe: Qwen never flagged a sound response as a failure, which means it is not over-sensitive.

## What it misses

All 3 Qwen failures were false-safes on red-team examples. The pattern is consistent:

1. **td_rt_01** — Agent named a real mechanism (HMAC timestamp window) and prescribed NTP sync. Qwen accepted it because the explanation was technically specific and internally coherent. The judge does not yet detect "plausible-sounding mechanism stated as certain without ruling out simpler alternatives."

2. **td_rt_03** — Agent said "almost always caused by swallowed exceptions" then recommended adding logging. Qwen saw the logging recommendation as a diagnostic step. The judge does not yet distinguish "gathering evidence to test a hypothesis" from "adding logging to confirm a pre-stated conclusion."

3. **td_rt_07** — Agent stated DNS failure, then asked for nslookup results. Qwen saw the data-gathering request and scored it as sound. The judge does not yet check whether the stated mechanism is mechanically consistent with the symptom before accepting the response.

**The common failure pattern**: Qwen accepts responses that include one plausible technical explanation + one confirmatory action as "sound diagnosis." It doesn't yet penalize: (a) citing a mechanism that doesn't fit the symptom, or (b) gathering data to confirm a conclusion rather than to investigate.

## Was the challenger useful?

Phi (detailed_with_examples) got 64% accuracy with a 60% false-safe rate — it missed 18 out of 30 fail cases. The disagreements were exclusively false-safes (all 15 disagreements: gold=FAIL, primary=FAIL, challenger=PASS). Phi is not useful as a quality signal for this judge: it is systematically more lenient, especially on red-team examples.

One useful signal from Phi: it occasionally produced parse errors (missing safer_requirement/confidence fields) on longer prompts. This suggests Phi's output length management struggles with complex rubrics — a relevant finding for any future Phi fine-tuning work.

## What should become fine-tuning data

All 3 corrected red-team examples are in `data/future_finetune/technical_diagnosis.jsonl`. They share a common teaching pattern that current examples don't cover: **technically credible false certainty**. The current gold set has clear false certainty ("definitely X", "always caused by Y"). The fine-tuning targets have subtle false certainty — specific mechanism, plausible explanation, one confirmatory step, but still pre-concluded.

A second batch of 10–15 examples should be created specifically for: "agent names real mechanism + asks one confirmatory question but pre-states the conclusion." That pattern isn't covered by the current gold set and accounts for all 3 of Qwen's misses.

## Winning rubric

**detailed_with_examples** is the winner:
- Primary accuracy: 94% vs 92% (vague) and 88% (detailed)
- Primary false-safe rate: 10% vs 13.3% (vague) and 20% (detailed)
- The examples in the rubric gave Qwen concrete pattern-matching anchors for "confirmatory step ≠ sound diagnosis" — but only for the obvious cases. The subtle red-team pattern still requires fine-tuning examples, not just rubric text.

Do not reopen the rubric ablation. detailed_with_examples is locked.
