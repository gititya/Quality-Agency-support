# Run Summary — 2026-06-12 16:58

## Primary model (Qwen3-4B-4bit)
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 100.0% |
| Binary accuracy | 100.0% |
| False-safe rate | 0.0% |
| False-unsafe rate | 0.0% |
| Span coverage (on fails) | 100.0% |
| Avg confidence (correct) | 99.3% |
| Avg confidence (incorrect) | — |

## Challenger model (Phi-4-mini-instruct-4bit)
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 94.0% |
| Binary accuracy | 74.0% |
| False-safe rate | 43.3% |
| False-unsafe rate | 0.0% |
| Span coverage (on fails) | 63.3% |
| Avg confidence (correct) | 84.7% |
| Avg confidence (incorrect) | 69.4% |

## Rubric ablation

| Rubric | Accuracy | False-safe rate | Span coverage |
|---|---|---|---|
| vague | 86.0% | 0.0% | 100.0% |
| detailed | 98.0% | 3.4% | 96.6% |
| detailed_with_examples | 100.0% | 0.0% | 100.0% |

## Disagreements
Primary vs challenger disagreements: 13
