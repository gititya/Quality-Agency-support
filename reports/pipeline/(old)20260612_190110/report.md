# Support Quality Pipeline Report

**Case ID:** acme_analytics_enterprise_export_billing
**Run ID:** 20260612_190110
**Model:** mlx-community/Qwen3-4B-4bit
**Judges run:** 5 / 5

## Case Summary

**Ticket:** Acme Analytics is an Enterprise customer. Their RevOps admin reports that CSV exports for the board metrics workspace have timed out three times since their SSO migration. They also say 14 deactivated
**Agent response:** Thanks for the detail. I checked your workspace and the export service is healthy, so this is definitely a browser download limit caused by the 18-month file size. Try Chrome incognito and rerun the C

## Judge Verdicts

| Judge | Verdict | Failure Type | Confidence | Span |
|---|---|---|---|---|
| source_of_truth | FAIL | ignored_context | high | I checked your workspace and the export service is health... |
| sop_adherence | FAIL | skipped_step | medium | I am checking the workspace now. |
| unsupported_promise | FAIL | unsupported_promise | medium | I have verified the account and escalated this to enginee... |
| technical_diagnosis | FAIL | incorrect_diagnosis | low | this is definitely a browser download limit caused by the... |
| handoff_completeness | FAIL | incomplete_handoff | high | Acme has export and billing issue after SSO. Customer nee... |

## Failures and Flags

- **source_of_truth** (high confidence): The agent ignored the export logs and tool context indicating a backend_timeout on async handoff, and the 1.8GB export size requiring async export path. The agent also ignored the billing context regarding seat overage credits requiring audit-log review and finance approval. | Span: `I checked your workspace and the export service is healthy, so this is definitely a browser download limit caused by the 18-month file size.`
- **sop_adherence** (medium confidence): The agent did not acknowledge the customer's urgency and board-report deadline as required in the expected process. Additionally, the agent did not verify that the requester is an authorized workspace admin in the visible interaction, even though prior verification was done in CRM. | Span: `I am checking the workspace now.`
- **unsupported_promise** (medium confidence): The agent promised that engineering will ship a patch by 10 AM ET tomorrow, which is not supported by the policy. The policy states that support should not promise an engineering patch or a same-day fix unless an incident SLA is active. There is no mention of an incident SLA being active in this case. | Span: `I have verified the account and escalated this to engineering, and they will ship a patch by 10 AM ET tomorrow.`
- **technical_diagnosis** (low confidence): The agent incorrectly identifies the root cause as a browser download limit without gathering sufficient diagnostic data. The symptoms suggest a timeout during an async export job, not a browser-related issue. The agent also promises a patch without an incident SLA and applies a credit without CSM approval. | Span: `this is definitely a browser download limit caused by the 18-month file size`
- **handoff_completeness** (high confidence): The handoff lacks customer identity (name, account ID, or contact), specific problem description (including export_id, workspace_id, date range, and failure mode), prior attempts (including verification of workspace and export status), diagnostic findings (including export logs, failure timestamp, and async export path explanation), urgency context (including board-report deadline and SLA requirements), and clear next step (including engineering escalation and credit approval process). | Span: `Acme has export and billing issue after SSO. Customer needs this fixed by tomorrow. Please investigate.`

*Total inference time: 129.43s*
