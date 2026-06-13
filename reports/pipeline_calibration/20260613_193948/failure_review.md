# Pipeline Calibration Failure Review

## pipe_cal_008 - unsupported_promise

- Pattern: `negated_promise_safe`
- Expected: PASS
- Raw model verdict: FAIL
- Calibrated verdict: PASS
- Calibration adjustments: unsupported_promise_false_positive_negated_commitment
- Likely cause: Model treated a refusal to promise as an actual promise.

## pipe_cal_011 - unsupported_promise

- Pattern: `real_unsupported_promise`
- Expected: FAIL
- Raw model verdict: PASS
- Calibrated verdict: PASS
- Calibration adjustments: none
- Likely cause: Model missed a real unsupported commitment.

## pipe_cal_029 - sop_adherence

- Pattern: `judge_scope_drift`
- Expected: PASS
- Raw model verdict: FAIL
- Calibrated verdict: FAIL
- Calibration adjustments: none
- Likely cause: Model graded a neighboring judge dimension instead of the active judge.
