# Fine-Tune Decision

**Run ID:** 20260613_193948
**Model:** mlx-community/Qwen3-4B-4bit
**Recommendation:** do not fine-tune yet

## Raw Qwen Metrics

```json
{
  "total": 40,
  "json_validity_rate": 0.95,
  "scoreable": 40,
  "binary_accuracy": 0.925,
  "miss_count": 3,
  "miss_rate": 0.075,
  "false_safe_rate": 0.062,
  "false_unsafe_rate": 0.083,
  "span_correctness": 1.0,
  "scope_drift_count": 1,
  "pattern_misses": {
    "negated_promise_safe": 1,
    "real_unsupported_promise": 1,
    "judge_scope_drift": 1
  }
}
```

## Calibrated Qwen Metrics

```json
{
  "total": 40,
  "json_validity_rate": 0.95,
  "scoreable": 40,
  "binary_accuracy": 0.95,
  "miss_count": 2,
  "miss_rate": 0.05,
  "false_safe_rate": 0.062,
  "false_unsafe_rate": 0.042,
  "span_correctness": 1.0,
  "scope_drift_count": 1,
  "pattern_misses": {
    "real_unsupported_promise": 1,
    "judge_scope_drift": 1
  }
}
```

## Guardrails

- Activation count: 1
- Activations: `{'unsupported_promise_false_positive_negated_commitment': 1}`

## Decision Rationale

- Do not fine-tune yet.
- Calibrated Qwen is below the miss threshold and no pattern repeats 3+ times after guardrails.
- Prompt + calibration is enough for v1.

## Subagent Usage

- GPT-5.4-mini subagent used: no
