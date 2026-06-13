# Support QA Synthesis Report

**Case ID:** northstar_learning_webhook_secret_rotation
**Run ID:** 20260613_141315
**Model:** mlx-community/Qwen3-4B-4bit
**Judges run:** 5

## Source Boundary

- This report does not change any judge verdict.
- Risk level, grade, human-review needs, and fix priority are synthesis derived from judge verdicts.
- Evidence spans are judge evidence when supplied by the verdict artifact.

## Overall Synthesis

- **Risk level:** High (synthesis: three or more judges returned FAIL)
- **Overall grade:** D

## What Went Well

- Judge evidence: Source-of-truth returned PASS (high confidence): The agent's response accurately uses the available context, including delivery logs, event IDs, and the signing-secret rotation details. The agent explains the 401 signature mismatch issue, recommends updating the CRM receiver, and suggests replaying a recent event as a test. The response also respects the customer's request not to rotate the secret again and avoids promising a full backfill.
- Judge evidence: Technical diagnosis returned PASS (high confidence): The agent's response demonstrates sound diagnostic reasoning. The agent acknowledges the urgency of the launch review, checks the delivery logs, identifies the 401 signature_mismatch error after the secret rotation, and explains that the CRM receiver is likely validating against the previous secret. The agent asks the customer to confirm the receiver has been updated to the active secret, recommends replaying a recent event as a test, and explains the 72-hour replay window. The agent also respects the customer's request not to rotate the secret again without approval and avoids promising a full backfill until integrations review. The response includes all necessary details for the handoff and follows the policy guidelines.

## What Failed

- Judge evidence: Unsupported promise returned FAIL (medium confidence) on `unsupported_promise`: The agent made an unsupported promise by stating they cannot guarantee a full backfill until the customer reviews the failed-event window. The policy explicitly states that support must not guarantee a full backfill before integrations review.
- Judge evidence: SOP/process adherence returned FAIL (medium confidence) on `skipped_step`: The agent did not acknowledge the launch-review urgency and the missing signup impact as required in the expected process.
- Judge evidence: Handoff completeness returned FAIL (high confidence) on `incomplete_handoff`: The handoff lacks customer identity (name, account ID, or contact information), problem description with urgency, prior attempts, diagnostic findings, and a clear next step.

## Evidence Spans

- Judge evidence: Unsupported promise span: `I cannot promise a full backfill until they review the failed-event window.`
- Judge evidence: SOP/process adherence span: `I am checking the delivery logs now.` Missing requirement: Acknowledge the launch-review urgency and the missing signup impact Evidence gap: No mention of the urgency or the impact of missing signups in the response
- Judge evidence: Handoff completeness span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.` Missing requirement: Customer identity, problem description with urgency, prior attempts, diagnostic findings, and clear next step Evidence gap: No mention of customer name, account ID, or contact information; no details on the urgency of the launch review; no prior troubleshooting attempts; no specific diagnostic findings beyond the 401 error; no clear next step for the receiving team

## Human Review Needs

- Synthesis: remove or rewrite unsupported commitments before sending; the judge found a promise without policy, SLA, or approval support. Review span: `I cannot promise a full backfill until they review the failed-event window.`. Required correction: Avoid promising a full backfill or guaranteed recovery before integrations review.
- Synthesis: check the required workflow steps before sending; the judge found a skipped or insufficiently evidenced process step. Missing requirement: Acknowledge the launch-review urgency and the missing signup impact. Evidence gap: No mention of the urgency or the impact of missing signups in the response. Review span: `I am checking the delivery logs now.`. Required correction: Acknowledge the launch-review urgency and the missing signup impact
- Synthesis: rewrite the handoff before escalation; the judge found missing context the receiving agent needs to act. Missing requirement: Customer identity, problem description with urgency, prior attempts, diagnostic findings, and clear next step. Evidence gap: No mention of customer name, account ID, or contact information; no details on the urgency of the launch review; no prior troubleshooting attempts; no specific diagnostic findings beyond the 401 error; no clear next step for the receiving team. Review span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.`. Required correction: The handoff must include the customer's identity, the urgency of the issue, prior troubleshooting attempts, specific diagnostic findings, and a clear next step for the receiving team.

## Prioritized Fixes

1. Synthesis priority from judge failure: fix Unsupported promise. Avoid promising a full backfill or guaranteed recovery before integrations review. Target span: `I cannot promise a full backfill until they review the failed-event window.`
2. Synthesis priority from judge failure: fix SOP/process adherence. Acknowledge the launch-review urgency and the missing signup impact Missing requirement: Acknowledge the launch-review urgency and the missing signup impact Evidence gap: No mention of the urgency or the impact of missing signups in the response Target span: `I am checking the delivery logs now.`
3. Synthesis priority from judge failure: fix Handoff completeness. The handoff must include the customer's identity, the urgency of the issue, prior troubleshooting attempts, specific diagnostic findings, and a clear next step for the receiving team. Missing requirement: Customer identity, problem description with urgency, prior attempts, diagnostic findings, and clear next step Evidence gap: No mention of customer name, account ID, or contact information; no details on the urgency of the launch review; no prior troubleshooting attempts; no specific diagnostic findings beyond the 401 error; no clear next step for the receiving team Target span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.`

## Judge Evidence

| Judge | Verdict | Failure Type | Confidence | Rationale |
|---|---|---|---|---|
| Source-of-truth | PASS | - | high | The agent's response accurately uses the available context, including delivery logs, event IDs, and the signing-secret rotation details. The agent explains the 401 signature mismatch issue, recommends updating the CRM receiver, and suggests replaying a recent event as a test. The response also respects the customer's request not to rotate the secret again and avoids promising a full backfill. |
| SOP/process adherence | FAIL | skipped_step | medium | The agent did not acknowledge the launch-review urgency and the missing signup impact as required in the expected process. |
| Unsupported promise | FAIL | unsupported_promise | medium | The agent made an unsupported promise by stating they cannot guarantee a full backfill until the customer reviews the failed-event window. The policy explicitly states that support must not guarantee a full backfill before integrations review. |
| Technical diagnosis | PASS | - | high | The agent's response demonstrates sound diagnostic reasoning. The agent acknowledges the urgency of the launch review, checks the delivery logs, identifies the 401 signature_mismatch error after the secret rotation, and explains that the CRM receiver is likely validating against the previous secret. The agent asks the customer to confirm the receiver has been updated to the active secret, recommends replaying a recent event as a test, and explains the 72-hour replay window. The agent also respects the customer's request not to rotate the secret again without approval and avoids promising a full backfill until integrations review. The response includes all necessary details for the handoff and follows the policy guidelines. |
| Handoff completeness | FAIL | incomplete_handoff | high | The handoff lacks customer identity (name, account ID, or contact information), problem description with urgency, prior attempts, diagnostic findings, and a clear next step. |
