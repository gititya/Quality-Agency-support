# Support QA Synthesis Report

**Case ID:** northstar_learning_webhook_secret_rotation
**Run ID:** 20260612_192051
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

- Judge evidence: Source-of-truth returned PASS (high confidence): The agent's response aligns with the policy, tool, and expected process. The agent acknowledged the urgency, checked the delivery logs, explained the 401 error, recommended updating the CRM receiver, and provided the necessary event IDs and details for replay. The response also respected the customer's request not to rotate the secret again and avoided promising a full backfill.
- Judge evidence: Technical diagnosis returned PASS (high confidence): The agent's response demonstrates sound diagnostic reasoning. The agent acknowledges the urgency of the launch review, uses the customer's identity as a verified workspace admin, checks the delivery logs for relevant details, explains the 401 signature_mismatch issue in context of the secret rotation, asks the customer to confirm the CRM receiver has been updated, recommends replaying an event as a test, respects the customer's request not to rotate the secret again, and avoids promising a full backfill. The response includes a clear handoff with all required details.

## What Failed

- Judge evidence: Unsupported promise returned FAIL (high confidence) on `unsupported_promise`: The agent made a promise that they could not guarantee a full backfill until integrations review, which lacks a basis in the policy. The policy states that support must not guarantee a full backfill before integrations review.
- Judge evidence: SOP/process adherence returned FAIL (medium confidence) on `skipped_step`: The agent did not explicitly acknowledge the launch-review urgency and the missing signup impact as required in the expected process.
- Judge evidence: Handoff completeness returned FAIL (high confidence) on `incomplete_handoff`: The handoff lacks customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step. It only mentions the issue and a task without providing necessary details for the receiving agent to act.

## Evidence Spans

- Judge evidence: Unsupported promise span: `I cannot promise a full backfill until they review the failed-event window.`
- Judge evidence: SOP/process adherence span: `I am checking the delivery logs now.` Missing requirement: Acknowledgment of the launch-review urgency and the impact of missing signups Evidence gap: No mention of the urgency or the impact of the missing 36 signups in the response
- Judge evidence: Handoff completeness span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.` Missing requirement: Customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step Evidence gap: No mention of customer name, account ID, or contact information; no details on the issue beyond the general statement; no prior troubleshooting attempts; no diagnostic findings; no urgency or business impact; no clear next step for the receiving team.

## Human Review Needs

- Synthesis: remove or rewrite unsupported commitments before sending; the judge found a promise without policy, SLA, or approval support. Review span: `I cannot promise a full backfill until they review the failed-event window.`. Required correction: I cannot guarantee a full backfill until integrations review. Please confirm the CRM receiver has been updated to the active signing secret, and replay one recent event as a test.
- Synthesis: check the required workflow steps before sending; the judge found a skipped or insufficiently evidenced process step. Missing requirement: Acknowledgment of the launch-review urgency and the impact of missing signups. Evidence gap: No mention of the urgency or the impact of the missing 36 signups in the response. Review span: `I am checking the delivery logs now.`. Required correction: Acknowledge the launch-review urgency and the missing signup impact
- Synthesis: rewrite the handoff before escalation; the judge found missing context the receiving agent needs to act. Missing requirement: Customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step. Evidence gap: No mention of customer name, account ID, or contact information; no details on the issue beyond the general statement; no prior troubleshooting attempts; no diagnostic findings; no urgency or business impact; no clear next step for the receiving team.. Review span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.`. Required correction: The handoff must include customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step.

## Prioritized Fixes

1. Synthesis priority from judge failure: fix Unsupported promise. I cannot guarantee a full backfill until integrations review. Please confirm the CRM receiver has been updated to the active signing secret, and replay one recent event as a test. Target span: `I cannot promise a full backfill until they review the failed-event window.`
2. Synthesis priority from judge failure: fix SOP/process adherence. Acknowledge the launch-review urgency and the missing signup impact Missing requirement: Acknowledgment of the launch-review urgency and the impact of missing signups Evidence gap: No mention of the urgency or the impact of the missing 36 signups in the response Target span: `I am checking the delivery logs now.`
3. Synthesis priority from judge failure: fix Handoff completeness. The handoff must include customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step. Missing requirement: Customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step Evidence gap: No mention of customer name, account ID, or contact information; no details on the issue beyond the general statement; no prior troubleshooting attempts; no diagnostic findings; no urgency or business impact; no clear next step for the receiving team. Target span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.`

## Judge Evidence

| Judge | Verdict | Failure Type | Confidence | Rationale |
|---|---|---|---|---|
| Source-of-truth | PASS | - | high | The agent's response aligns with the policy, tool, and expected process. The agent acknowledged the urgency, checked the delivery logs, explained the 401 error, recommended updating the CRM receiver, and provided the necessary event IDs and details for replay. The response also respected the customer's request not to rotate the secret again and avoided promising a full backfill. |
| SOP/process adherence | FAIL | skipped_step | medium | The agent did not explicitly acknowledge the launch-review urgency and the missing signup impact as required in the expected process. |
| Unsupported promise | FAIL | unsupported_promise | high | The agent made a promise that they could not guarantee a full backfill until integrations review, which lacks a basis in the policy. The policy states that support must not guarantee a full backfill before integrations review. |
| Technical diagnosis | PASS | - | high | The agent's response demonstrates sound diagnostic reasoning. The agent acknowledges the urgency of the launch review, uses the customer's identity as a verified workspace admin, checks the delivery logs for relevant details, explains the 401 signature_mismatch issue in context of the secret rotation, asks the customer to confirm the CRM receiver has been updated, recommends replaying an event as a test, respects the customer's request not to rotate the secret again, and avoids promising a full backfill. The response includes a clear handoff with all required details. |
| Handoff completeness | FAIL | incomplete_handoff | high | The handoff lacks customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step. It only mentions the issue and a task without providing necessary details for the receiving agent to act. |
