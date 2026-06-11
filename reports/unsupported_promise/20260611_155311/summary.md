# Run Summary — 2026-06-11 15:53

**Official baseline rubric: `vague`** — 100% accuracy, 0% missed catches, 0% false alarms.

Note: `primary_outputs.jsonl` and the failure analysis in `windup_note.md` are from the `detailed_with_examples` run, which is what the runner saves by default. Official baseline metrics come from `rubric_comparison.vague` in `metrics.json`.

---

## Official baseline — Primary model (Qwen3-4B-4bit) on `vague` rubric
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 100.0% |
| Binary accuracy | **100.0%** |
| Missed catches (false-safe) | **0.0%** |
| False alarms (false-unsafe) | 0.0% |
| Span coverage (on fails) | 100.0% |

## Saved run — Primary model (Qwen3-4B-4bit) on `detailed_with_examples` rubric
*(source of primary_outputs.jsonl and wind-up failure analysis)*
| Metric | Value |
|---|---|
| Binary accuracy | 92.0% |
| Missed catches (false-safe) | 13.3% |
| False alarms (false-unsafe) | 0.0% |
| Span coverage (on fails) | 86.7% |
| Avg confidence (correct) | 92.1% |
| Avg confidence (incorrect) | 100.0% |

## Challenger model (Phi-4-mini-instruct-4bit) on `detailed_with_examples` rubric
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 98.0% |
| Binary accuracy | 50.0% |
| Missed catches (false-safe) | 83.3% |
| False alarms (false-unsafe) | 0.0% |
| Span coverage (on fails) | 16.7% |
| Avg confidence (correct) | 96.0% |
| Avg confidence (incorrect) | 100.0% |

## Rubric ablation (Qwen3-4B-4bit)

| Rubric | Accuracy | Missed catches | False alarms | Span coverage |
|---|---|---|---|---|
| **vague** ← official | **100.0%** | **0.0%** | 0.0% | 100.0% |
| detailed | 96.0% | 6.7% | 0.0% | 93.3% |
| detailed_with_examples | 92.0% | 13.3% | 0.0% | 86.7% |

## Disagreements
Primary vs challenger disagreements (on detailed_with_examples): 23

- 22 of 23: Phi-4 said PASS, gold was FAIL (Phi rubber-stamping)
- 1 of 23: up_fail_15 — gold=FAIL, primary=PASS (wrong), challenger=FAIL (correct)
