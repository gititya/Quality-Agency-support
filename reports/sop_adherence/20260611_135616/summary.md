# Run Summary — 2026-06-11 14:57

**Official baseline rubric: `detailed`** — best balance of accuracy (82%) and missed catches (13.3%).

Note: `primary_outputs.jsonl` and the failure analysis in `windup_note.md` are from the `detailed_with_examples` run, which is what the runner saves by default. That run has the same accuracy (82%) but a different error distribution (7 missed catches, 2 false alarms vs. 4 missed, 5 false alarms on the official detailed rubric).

---

## Official baseline — Primary model (Qwen3-4B-4bit) on `detailed` rubric
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 100.0% |
| Binary accuracy | **82.0%** |
| Missed catches (false-safe) | **13.3%** |
| False alarms (false-unsafe) | 25.0% |
| Span coverage (on fails) | 86.7% |
| Avg confidence (correct) | 81.5% |
| Avg confidence (incorrect) | 81.7% |

## Saved run — Primary model (Qwen3-4B-4bit) on `detailed_with_examples` rubric
*(source of primary_outputs.jsonl and wind-up failure analysis)*
| Metric | Value |
|---|---|
| Binary accuracy | 82.0% |
| Missed catches (false-safe) | 23.3% |
| False alarms (false-unsafe) | 10.0% |
| Span coverage (on fails) | 76.7% |
| Avg confidence (correct) | 81.5% |
| Avg confidence (incorrect) | 92.7% |

## Challenger model (Phi-4-mini-instruct-4bit) on `detailed_with_examples` rubric
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 98.0% |
| Binary accuracy | 58.0% |
| Missed catches (false-safe) | 63.3% |
| False alarms (false-unsafe) | 10.0% |
| Span coverage (on fails) | 36.7% |
| Avg confidence (correct) | 98.9% |
| Avg confidence (incorrect) | 95.2% |

## Rubric ablation (Qwen3-4B-4bit)

| Rubric | Accuracy | Missed catches | False alarms | Span coverage |
|---|---|---|---|---|
| vague | 74.0% | 0.0% | 65.0% | 100.0% |
| **detailed** ← official | **82.0%** | **13.3%** | 25.0% | 86.7% |
| detailed_with_examples | 82.0% | 23.3% | 10.0% | 76.7% |

## Disagreements
Primary vs challenger disagreements: 18
