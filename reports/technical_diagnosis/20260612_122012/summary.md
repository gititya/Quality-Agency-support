# Run Summary — 2026-06-12 14:10

## Primary model (Qwen3-4B-4bit)
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 100.0% |
| Binary accuracy | 94.0% |
| False-safe rate | 10.0% |
| False-unsafe rate | 0.0% |
| Span coverage (on fails) | 90.0% |
| Avg confidence (correct) | 60.2% |
| Avg confidence (incorrect) | 67.0% |

## Challenger model (Phi-4-mini-instruct-4bit)
| Metric | Value |
|---|---|
| Total examples | 50 |
| JSON validity | 98.0% |
| Binary accuracy | 64.0% |
| False-safe rate | 60.0% |
| False-unsafe rate | 0.0% |
| Span coverage (on fails) | 40.0% |
| Avg confidence (correct) | 86.4% |
| Avg confidence (incorrect) | 100.0% |

## Rubric ablation

| Rubric | Accuracy | False-safe rate | Span coverage |
|---|---|---|---|
| vague | 92.0% | 13.3% | 100.0% |
| detailed | 88.0% | 20.0% | 80.0% |
| detailed_with_examples | 94.0% | 10.0% | 90.0% |

## Disagreements
Primary vs challenger disagreements: 15
