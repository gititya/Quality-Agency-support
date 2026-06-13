# Support QA Synthesis Report

**Case ID:** northstar_learning_webhook_secret_rotation
**Run ID:** 20260613_142026
**Model:** mlx-community/Qwen3-4B-4bit
**Judges run:** 5

## Source Boundary

- This report uses calibrated verdicts when deterministic guardrails are recorded in the artifacts.
- Original model verdicts are preserved in the verdict artifacts when calibration occurs.
- Risk level, grade, human-review needs, and fix priority are synthesis derived from judge verdicts.
- Evidence spans are judge evidence when supplied by the verdict artifact.

## Overall Synthesis

- **Risk level:** Medium (synthesis: at least one judge returned FAIL)
- **Overall grade:** C

## What Went Well

- Judge evidence: Source-of-truth returned PASS (high confidence): The agent's response accurately uses the available context, including delivery logs, event IDs, and the signing-secret rotation details. The agent explains the 401 signature mismatch issue, recommends updating the CRM receiver, and suggests replaying a recent event as a test. The response also respects the customer's request not to rotate the secret again and avoids promising a full backfill.
- Judge evidence: Unsupported promise returned PASS (medium confidence): Calibration override: the original unsupported-promise verdict flagged a refusal to promise or guarantee an outcome, which is safe expectation-setting.
- Judge evidence: Technical diagnosis returned PASS (high confidence): The agent's response demonstrates sound diagnostic reasoning. The agent acknowledges the urgency of the launch review, checks the delivery logs, identifies the 401 signature_mismatch error after the secret rotation, and explains that the CRM receiver is likely validating against the previous secret. The agent asks the customer to confirm the receiver has been updated to the active secret, recommends replaying a recent event as a test, and explains the 72-hour replay window. The agent also respects the customer's request not to rotate the secret again without approval and avoids promising a full backfill until integrations review. The response includes all necessary details for the handoff and follows the policy guidelines.

## What Failed

- Judge evidence: SOP/process adherence returned FAIL (medium confidence) on `skipped_step`: The agent did not acknowledge the launch-review urgency and the missing signup impact as required in the expected process.
- Judge evidence: Handoff completeness returned FAIL (high confidence) on `incomplete_handoff`: The handoff lacks customer identity (name, account ID, or contact information), problem description with urgency, prior attempts, diagnostic findings, and a clear next step.

## Calibration Adjustments

- Synthesis: SOP/process adherence was calibrated from FAIL to FAIL: invalid_failure_span_removed
- Synthesis: Unsupported promise was calibrated from FAIL to PASS: unsupported_promise_false_positive_negated_commitment

## Evidence Spans

- Judge evidence gap: SOP/process adherence: No mention of the urgency or the impact of missing signups in the response
- Judge evidence: Handoff completeness span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.` Missing requirement: Customer identity, problem description with urgency, prior attempts, diagnostic findings, and clear next step Evidence gap: No mention of customer name, account ID, or contact information; no details on the urgency of the launch review; no prior troubleshooting attempts; no specific diagnostic findings beyond the 401 error; no clear next step for the receiving team

## Human Review Needs

- Synthesis: check the required workflow steps before sending; the judge found a skipped or insufficiently evidenced process step. Missing requirement: Acknowledge the launch-review urgency and the missing signup impact. Evidence gap: No mention of the urgency or the impact of missing signups in the response. Required correction: Acknowledge the launch-review urgency and the missing signup impact
- Synthesis: rewrite the handoff before escalation; the judge found missing context the receiving agent needs to act. Missing requirement: Customer identity, problem description with urgency, prior attempts, diagnostic findings, and clear next step. Evidence gap: No mention of customer name, account ID, or contact information; no details on the urgency of the launch review; no prior troubleshooting attempts; no specific diagnostic findings beyond the 401 error; no clear next step for the receiving team. Review span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.`. Required correction: The handoff must include the customer's identity, the urgency of the issue, prior troubleshooting attempts, specific diagnostic findings, and a clear next step for the receiving team.
- Synthesis: ask for human span review on SOP/process adherence; the judge did not provide an exact failure span.

## Prioritized Fixes

1. Synthesis priority from judge failure: fix SOP/process adherence. Acknowledge the launch-review urgency and the missing signup impact Missing requirement: Acknowledge the launch-review urgency and the missing signup impact Evidence gap: No mention of the urgency or the impact of missing signups in the response
2. Synthesis priority from judge failure: fix Handoff completeness. The handoff must include the customer's identity, the urgency of the issue, prior troubleshooting attempts, specific diagnostic findings, and a clear next step for the receiving team. Missing requirement: Customer identity, problem description with urgency, prior attempts, diagnostic findings, and clear next step Evidence gap: No mention of customer name, account ID, or contact information; no details on the urgency of the launch review; no prior troubleshooting attempts; no specific diagnostic findings beyond the 401 error; no clear next step for the receiving team Target span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.`

## Judge Evidence

| Judge | Verdict | Failure Type | Confidence | Rationale |
|---|---|---|---|---|
| Source-of-truth | PASS | - | high | The agent's response accurately uses the available context, including delivery logs, event IDs, and the signing-secret rotation details. The agent explains the 401 signature mismatch issue, recommends updating the CRM receiver, and suggests replaying a recent event as a test. The response also respects the customer's request not to rotate the secret again and avoids promising a full backfill. |
| SOP/process adherence | FAIL | skipped_step | medium | The agent did not acknowledge the launch-review urgency and the missing signup impact as required in the expected process. |
| Unsupported promise | PASS | - | medium | Calibration override: the original unsupported-promise verdict flagged a refusal to promise or guarantee an outcome, which is safe expectation-setting. |
| Technical diagnosis | PASS | - | high | The agent's response demonstrates sound diagnostic reasoning. The agent acknowledges the urgency of the launch review, checks the delivery logs, identifies the 401 signature_mismatch error after the secret rotation, and explains that the CRM receiver is likely validating against the previous secret. The agent asks the customer to confirm the receiver has been updated to the active secret, recommends replaying a recent event as a test, and explains the 72-hour replay window. The agent also respects the customer's request not to rotate the secret again without approval and avoids promising a full backfill until integrations review. The response includes all necessary details for the handoff and follows the policy guidelines. |
| Handoff completeness | FAIL | incomplete_handoff | high | The handoff lacks customer identity (name, account ID, or contact information), problem description with urgency, prior attempts, diagnostic findings, and a clear next step. |
