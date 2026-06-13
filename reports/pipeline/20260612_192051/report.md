# Support Quality Pipeline Report

**Case ID:** northstar_learning_webhook_secret_rotation
**Run ID:** 20260612_192051
**Model:** mlx-community/Qwen3-4B-4bit
**Judges run:** 5 / 5

## Case Summary

**Ticket:** Northstar Learning is a Growth-plan B2B SaaS customer using webhooks to sync product-qualified trial signups into its CRM. Their lifecycle operations manager reports that webhook deliveries stopped af
**Agent response:** Thanks, I checked the delivery logs for workspace ws_northstar_337 and endpoint wh_crm_882. There is no active platform incident. The failures start at 2026-06-12 14:05 UTC, right after the signing-se

## Judge Verdicts

| Judge | Verdict | Failure Type | Confidence | Span |
|---|---|---|---|---|
| source_of_truth | PASS | — | high | — |
| sop_adherence | FAIL | skipped_step | medium | I am checking the delivery logs now. |
| unsupported_promise | FAIL | unsupported_promise | high | I cannot promise a full backfill until they review the fa... |
| technical_diagnosis | PASS | — | high | — |
| handoff_completeness | FAIL | incomplete_handoff | high | Northstar webhooks failing after secret rotation. Logs sh... |

## Failures and Flags

- **sop_adherence** (medium confidence): The agent did not explicitly acknowledge the launch-review urgency and the missing signup impact as required in the expected process. | Span: `I am checking the delivery logs now.` | Missing: `Acknowledgment of the launch-review urgency and the impact of missing signups` | Evidence gap: `No mention of the urgency or the impact of the missing 36 signups in the response`
- **unsupported_promise** (high confidence): The agent made a promise that they could not guarantee a full backfill until integrations review, which lacks a basis in the policy. The policy states that support must not guarantee a full backfill before integrations review. | Span: `I cannot promise a full backfill until they review the failed-event window.`
- **handoff_completeness** (high confidence): The handoff lacks customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step. It only mentions the issue and a task without providing necessary details for the receiving agent to act. | Span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.` | Missing: `Customer identity, problem description, prior attempts, diagnostic findings, urgency, and clear next step` | Evidence gap: `No mention of customer name, account ID, or contact information; no details on the issue beyond the general statement; no prior troubleshooting attempts; no diagnostic findings; no urgency or business impact; no clear next step for the receiving team.`

*Total inference time: 130.36s*
