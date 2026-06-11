# Run Summary — 2026-06-11 12:52

## Primary model (Qwen3-4B-4bit)
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 100.0% |
| Binary accuracy | 68.0% |
| False-safe rate | 53.3% |
| False-unsafe rate | 0.0% |
| Span coverage (on fails) | 46.7% |
| Avg confidence (correct) | 88.4% |
| Avg confidence (incorrect) | 95.9% |

## Challenger model (Phi-4-mini-instruct-4bit)
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 96.0% |
| Binary accuracy | 52.0% |
| False-safe rate | 80.0% |
| False-unsafe rate | 0.0% |
| Span coverage (on fails) | 26.7% |
| Avg confidence (correct) | 100.0% |
| Avg confidence (incorrect) | 100.0% |

## Rubric ablation

| Rubric | Accuracy | False-safe rate | Span coverage |
|---|---|---|---|
| vague | 92.0% | 13.3% | 86.7% |
| detailed | 72.0% | 46.7% | 53.3% |
| detailed_with_examples | 68.0% | 53.3% | 46.7% |

## Disagreements
Primary vs challenger disagreements: 14
