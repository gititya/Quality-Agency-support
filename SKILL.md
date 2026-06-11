# SKILL.md — eval-judges

## Current phase

Judge factory v1 — Judges 1–3 approved and merged to main. Starting Judge 4 (Technical Diagnosis).

## Completed

### Judge 1 — Source-of-Truth (approved, merged)
- 40 gold + 10 red-team examples
- Official rubric: `vague` (84% accuracy, 20% false-safe)
- 6 corrected gold + 10 red-team records in data/corrected and data/future_finetune
- Key finding: vague wins for holistic claim-vs-context tasks; examples rubric hurt Qwen

### Judge 2 — SOP/Process Adherence (approved, merged)
- 40 gold + 10 red-team examples
- Official rubric: `detailed` (82% accuracy, 13.3% missed catches)
- 9 corrected records (5 gold, 4 future_finetune)
- Key finding: detailed wins for checklist tasks — mirrors the step-checking structure of the task
- Dominant failure: rationale hallucination (Qwen inventing step completions that aren't in the text)

### Judge 3 — Unsupported Promise (approved, merged)
- 40 gold + 10 red-team examples
- Official rubric: `vague` (100% accuracy, 0% missed catches, 0% false alarms — perfect baseline)
- 4 corrected records (1 gold, 3 future_finetune)
- Key finding: vague wins again for holistic claim-vs-grounding tasks
- New failure mode identified: compositional evaluation — model anchors on grounded portion and misses unauthorized additions
- Specific failures: digit misread (99.99% vs 99.9%), self-contradictory rationale, conditional framing hiding absolute guarantees, authorized action ≠ authorized outcome

## Cross-judge patterns (confirmed after 3 judges)

- **Rubric selection rule:** holistic judgment → vague; checklist verification → detailed
- **Phi-4 signal:** if Phi-4 flags something Qwen passed, look carefully — but never trust Phi-4 PASS verdicts
- **Confidence inversion:** Qwen most confident when wrong (avg ~93–100% on incorrect verdicts vs 82–94% on correct)
- **Rationale hallucination:** cross-judge model-level issue — Qwen invents facts to justify PASS verdicts; appears in every judge so far

## Active next steps

- Build Judge 4: Technical Diagnosis — did the agent's technical explanation accurately reflect the KB/tool context?
- Branch: `judge-4-technical-diagnosis`
- Expected rubric winner: likely vague (holistic accuracy check, similar to Judges 1 and 3)
- Watch for: digit/version misreads (previewed in Judge 3 up_fail_15); model reading past technical detail

## Architecture

```
judges/registry.yaml         — all judge definitions and rubric variants (3 judges defined)
data/gold/<judge>.jsonl      — 40 examples per judge (20 pass, 20 fail)
data/red_team/<judge>.jsonl  — 10 subtle false-safe examples per judge
data/corrected/<judge>.jsonl — complete Qwen3 failure ledger per judge
data/future_finetune/<judge>.jsonl — training-ready records
reports/<judge>/<run_id>/    — metrics, outputs, disagreement report, summary, windup_note
src/eval_judges/             — adapter, prompt_builder, parser, scorer, report
experiment-walkthrough.md    — teaching doc, one section per approved judge
run_judge.py                 — runs all 3 rubrics × 2 models, saves artifacts
```

## Key numbers

| Judge | Official rubric | Accuracy | Missed catches | False alarms |
|---|---|---|---|---|
| source_of_truth | vague | 84% | 20% | 10% |
| sop_adherence | detailed | 82% | 13.3% | 25% |
| unsupported_promise | vague | **100%** | **0%** | **0%** |

## Session log

- 2026-06-11: Judges 1 and 2 complete from prior sessions
- 2026-06-11: Judge 3 (unsupported_promise) built, run, wind-up complete, approved, merged to main
- 2026-06-11: All branches (judge-factory-v1, judge-2-sop-adherence, judge-3-unsupported-promise) merged to main
- 2026-06-11: Ready to start Judge 4 on branch judge-4-technical-diagnosis
