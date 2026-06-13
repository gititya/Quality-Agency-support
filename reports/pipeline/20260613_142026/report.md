# Support Quality Pipeline Report

**Case ID:** northstar_learning_webhook_secret_rotation
**Run ID:** 20260613_142026
**Model:** mlx-community/Qwen3-4B-4bit
**Judges run:** 5 / 5

## Case Summary

**Ticket:** Northstar Learning is a Growth-plan B2B SaaS customer using webhooks to sync product-qualified trial signups into its CRM. Their lifecycle operations manager reports that webhook deliveries stopped af
**Agent response:** Thanks, I checked the delivery logs for workspace ws_northstar_337 and endpoint wh_crm_882. There is no active platform incident. The failures start at 2026-06-12 14:05 UTC, right after the signing-se

## Judge Verdicts

| Judge | Verdict | Failure Type | Confidence | Span |
|---|---|---|---|---|
| source_of_truth | PASS | — | high | — |
| sop_adherence | FAIL | skipped_step | medium | — |
| unsupported_promise | PASS | — | medium | — |
| technical_diagnosis | PASS | — | high | — |
| handoff_completeness | FAIL | incomplete_handoff | high | Northstar webhooks failing after secret rotation. Logs sh... |

## Failures and Flags

- **sop_adherence** (medium confidence): The agent did not acknowledge the launch-review urgency and the missing signup impact as required in the expected process. | Span: `n/a` | Missing: `Acknowledge the launch-review urgency and the missing signup impact` | Evidence gap: `No mention of the urgency or the impact of missing signups in the response`
- **unsupported_promise** calibration adjustment: unsupported_promise_false_positive_negated_commitment
- **handoff_completeness** (high confidence): The handoff lacks customer identity (name, account ID, or contact information), problem description with urgency, prior attempts, diagnostic findings, and a clear next step. | Span: `Northstar webhooks failing after secret rotation. Logs show 401 signature_mismatch. Please check replay eligibility.` | Missing: `Customer identity, problem description with urgency, prior attempts, diagnostic findings, and clear next step` | Evidence gap: `No mention of customer name, account ID, or contact information; no details on the urgency of the launch review; no prior troubleshooting attempts; no specific diagnostic findings beyond the 401 error; no clear next step for the receiving team`

*Total inference time: 210.37s*
