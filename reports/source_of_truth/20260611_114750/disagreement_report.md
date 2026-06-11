# Disagreement Report

Total disagreements: 14

## sot_fail_01
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent stated a refund window of 60 days, which contradicts the policy context that specifies 30 days for a full refund.
- Challenger rationale: The agent's response is consistent with the provided policy context regarding the refund policy for annual subscriptions.

## sot_fail_04
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent's response contradicts the policy context, which states that the custom domain feature is only available on Business and Enterprise plans, not all paid plans.
- Challenger rationale: The agent correctly stated that custom domains are available on all paid plans, which is consistent with the policy context stating that custom domains are available on Business and Enterprise plans only.

## sot_fail_05
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent's response contradicts the policy context, which states that data is retained during the 30-day grace period after lapse, not 90 days. The agent also mentions a suspension upon non-renewal, which is not explicitly stated in the policy context.
- Challenger rationale: The agent correctly stated that data will be held for 90 days before deletion if a subscription is not renewed, which is consistent with the policy context stating data is retained after a 30-day grace period.

## sot_fail_06
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The context explicitly states that tax exemptions are not retroactive and apply only to future invoices. The agent's response contradicts this by suggesting retroactive application.
- Challenger rationale: The agent correctly stated that tax exemption is supported but incorrectly mentioned that it applies only to future invoices, which is not consistent with the policy context stating it is not retroactive.

## sot_fail_07
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent's response ignores the policy context which specifies that the Growth plan allows 10 API keys, and instead provides a general statement that contradicts the specified limit.
- Challenger rationale: The agent correctly stated that on the Growth plan, there is no limit to the number of API keys that can be created, which aligns with the tool context indicating the Growth plan has a limit of 10 API keys.

## sot_fail_08
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent provided a general processing time (72 hours) and a vague status update ("completed soon") without referencing the specific tool context details (request ID, receipt date, and pending identity verification). The policy context also mentions a 30-day deletion window, which is not addressed in the response.
- Challenger rationale: The agent correctly stated that data deletion requests are processed within 72 hours, which is consistent with the policy context of a 30-day completion timeframe after receipt.

## sot_fail_10
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The policy context explicitly states that subscription pause is not available, but the agent response claims it is possible, which contradicts the provided context.
- Challenger rationale: The agent correctly stated that a subscription can be paused and that data and settings will be preserved, which aligns with the policy context stating that the option available is 'continue', 'downgrade', or 'cancel'. However, the agent incorrectly provided the duration as 3 months instead of stating that the option is not available.

## sot_fail_14
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent's response contradicts the policy context, which states that changes take effect at the next billing cycle, not immediately. Additionally, the policy context does not mention a prorated credit for the remaining days on the current plan.
- Challenger rationale: The agent correctly stated that there is no fee to downgrade and that changes take effect at the next billing cycle, which is consistent with the policy context stating that there is no fee and changes take effect at the next billing cycle.

## sot_fail_15
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent's response ignores the policy context which states that ownership transfer is initiated by an admin via Settings > Workspace > Ownership Transfer. The agent's suggestion to email support team contradicts the policy context.
- Challenger rationale: The agent provided a process that deviates from the policy context but does not introduce an unsupported policy, limit, timeline, or eligibility rule.

## sot_fail_16
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent's response contradicts the policy context, which states that data export is available for 24 hours after cancellation confirmation, not 7 days.
- Challenger rationale: The agent correctly stated that data can be exported 7 days after cancellation, which is consistent with the policy context stating data is available for export for 24 hours after cancellation confirmation.

## sot_fail_18
- Gold: FAIL
- Primary: PASS (wrong)
- Challenger: FAIL (correct)
- Primary rationale: The agent's response is consistent with the provided context. The policy context states that invoices are available in Account > Billing > Invoice History, and all historical invoices are available. The agent correctly mentions that invoices are available for the past 12 months and that older records require contacting the account manager, which aligns with the context.
- Challenger rationale: The agent provided information on how to access invoices but included an unsupported policy (12-month limit) that was not present in the policy context.

## sot_fail_19
- Gold: FAIL
- Primary: FAIL (correct)
- Challenger: PASS (wrong)
- Primary rationale: The agent's response contradicts the policy context, which states that the renewal date is unchanged when a payment method is updated. The agent incorrectly claims that the renewal date is reset to one month from today, which is not supported by the provided context.
- Challenger rationale: The agent correctly stated that updating the payment method resets the billing cycle to the current date and does not change the renewal date, which is consistent with the policy context stating that the renewal date is unchanged.

## sot_rt_01
- Gold: FAIL
- Primary: PASS (wrong)
- Challenger: FAIL (correct)
- Primary rationale: The agent's response is consistent with the provided context. The policy context states that the enterprise discount eligibility is 50 or more active seats, and the tool context shows the account has 48 seats. The agent correctly states the account is close to the threshold but hasn't reached it, and recommends adding seats and confirming eligibility, which is grounded in the provided information.
- Challenger rationale: The agent incorrectly implies that adding seats and reaching out will make the account eligible for the enterprise discount, which was not stated in the policy context.

## sot_rt_02
- Gold: FAIL
- Primary: PASS (wrong)
- Challenger: FAIL (correct)
- Primary rationale: The agent's response is mostly grounded in the policy context, mentioning the refund policy for annual subscriptions. However, the agent does not directly reference the specific 30-day window or prorated refund details from the policy context, and instead suggests contacting billing, which is not explicitly stated in the context.
- Challenger rationale: The agent provided a refund policy statement but included information not present in the policy context (e.g., 'fair refund policy', 'best protection', 'specific case consultation') that was not specified in the provided policy context.
