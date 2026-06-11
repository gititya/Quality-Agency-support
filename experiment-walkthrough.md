# Experiment Walkthrough — Quality Judge Agency

> One section per judge, added after each approved run.

---

# Judge 1 — Source-of-Truth
### Did the agent use the information it was given?

---

## What this judge is trying to catch

A support agent often has context sitting right in front of them — the customer's account details, the company's refund policy, a knowledge base article. The source-of-truth judge asks one question: **did the agent actually use that information, or did they make something up?**

This is the most fundamental failure in support quality. Everything else — tone, speed, format — doesn't matter if the agent told the customer the wrong refund window, invented a feature that doesn't exist, or ignored the tool result showing the account was suspended.

The tricky part is that fabricated answers often sound completely confident and professional. The agent doesn't say "I'm guessing." They say "Our refund window is 60 days" — delivered with the same authority as if they'd checked. A human reviewer might not catch it without the policy in front of them. The judge has the policy in front of it.

---

## Before you run — two things to expect

**Expect the models to be too lenient.** Small models have a bias toward saying "looks fine." They're trained on text where most responses are reasonable, so they default to charitable readings. The interesting number in this experiment isn't how often they catch failures — it's how often they miss them.

**Expect the red-team examples to be harder than the labelled failures.** The 10 red-team examples are deliberately polished. They're written to sound like a careful, helpful agent who happens to have avoided using the context. A model that only looks for obvious wrong facts will miss them entirely.

---

## The three marking schemes (rubric ablation)

We gave the model three different sets of instructions for how to judge, and ran all three to see which produced the best results.

Think of it like testing three different briefings you'd give a new hire before they review a call recording:

- **Brief 1 (vague):** "Did the agent use the information they had available? If they ignored it and guessed instead, that's a failure."
- **Brief 2 (detailed):** A longer version with a specific list of what counts as ignoring context — fabricating a policy, confirming account state without checking the tool, citing a wrong procedure, etc. Plus a scoring scale.
- **Brief 3 (detailed + examples):** The same long list, but also three worked examples of what a pass looks like and three of what a fail looks like.

**The results:**

| Briefing | Got it right | Missed bad answers (false positives) | Pointed to the exact problem |
|---|---|---|---|
| Vague | **92%** | 13% | 87% |
| Detailed | 72% | 47% | 53% |
| Detailed + examples | 68% | 53% | 47% |

The simplest briefing worked best. This is the central surprise of this run and it's worth sitting with.

---

## Why more instructions made it worse

When the rubric is vague, the model has to make a gut call: does this answer look right or not? When the rubric is detailed, it has a checklist — and at 4 billion parameters, this model is small enough that it starts ticking boxes individually rather than seeing the whole picture.

It finds one rule that seems satisfied — "the agent mentioned the policy" — and uses that to justify a pass, even when the actual answer contradicted the policy. More rules gave it more escape routes. It's the same failure mode as a junior employee who ticks every box on a compliance form but misses that the whole response was wrong.

The vague rubric forced a holistic judgment. The detailed one invited rationalisation.

**What this tells us for next steps:** if better rubrics don't beat the vague one, the next lever to pull is fine-tuning — not more prompt engineering.

---

## What "missed catches" means (false positive rate)

When the judge looked at an answer that was actually wrong and said "looks fine" — that's a missed catch. We call it a false positive in testing terms.

- Qwen3 missed **53%** of bad answers on the best rubric. More than half slipped through.
- Phi-4 missed **80%** of bad answers. Four out of five.

This is the number that matters most for a quality judge. If you deployed this today as an automated filter, the majority of bad support responses would go uncaught.

---

## What "showed its work" means (pinpoint rate)

When the judge does flag something as wrong, does it point to the exact sentence that's wrong? Or does it just say "fail" without showing where?

- Qwen3 pointed to the exact problem in **47%** of failures.
- Phi-4 pointed to the exact problem in **27%** of failures.

Pointing to the exact phrase matters for downstream use — if a human reviewer is checking the judge's work, "fail" alone isn't actionable. "The agent said 60 days; the policy says 30 days" is.

---

## The two models compared

| | Qwen3-4B (primary) | Phi-4-mini (challenger) |
|---|---|---|
| Got it right | 68% | 52% |
| Missed bad answers | 53% | 80% |
| Output was valid JSON | 100% | 96% |
| Pointed to exact problem | 47% | 27% |

Qwen3 is clearly the stronger judge at this task. Phi-4's biggest problem isn't accuracy — it's that it's too agreeable. It kept reading bad answers as consistent with the policy, even when the policy was right there contradicting them.

One revealing Phi-4 failure: an agent told a customer "data will be held for 90 days." The policy said 30 days. Phi-4 said: "The agent correctly stated 90 days, which is consistent with the 30-day grace period." That's not a different interpretation. That's the model generating plausible-sounding reasoning rather than actually reading the context.

---

## Where the two models disagreed (14 examples)

Every single disagreement was on a **fail** example — never on a pass. Both models agree when something is clearly right. They split only when deciding whether something is wrong.

Of the 14 disagreements:
- **11 cases:** Qwen3 caught the failure; Phi-4 missed it
- **3 cases:** Phi-4 caught the failure; Qwen3 missed it

Qwen3's 3 misses are all red-team examples — the deliberately polished ones. It flagged direct factual contradictions reliably but let through vague, hedging responses that avoided using the context without technically contradicting it.

Those 3 misses are the most interesting result of this run. They define exactly what the model still can't catch.

---

## What this run teaches

1. **Both models are too forgiving.** They're not going to replace human review at this accuracy. The value is narrower: flagging obvious, clear-cut failures before a human has to read them.

2. **Simpler instructions outperformed detailed ones.** At 4B parameters, more rules = more rationalisation. This is an argument for keeping the rubric minimal and improving accuracy through fine-tuning on corrected examples, not through prompt complexity.

3. **Phi-4 is not viable as a standalone judge for this task.** 80% missed catches is too high. It's useful as a second opinion to find what Qwen3 misses, but not as a primary filter.

4. **The red-team examples are doing their job.** The 3 Qwen3 misses are all from the red-team set. These are exactly the subtle failures the judge needs to get better at catching — and they'll become training data when fine-tuning starts.

5. **Overconfidence when wrong.** Qwen3's average confidence when it got the answer right: 88%. When it got the answer wrong: 96%. It's most certain precisely when it's mistaken. This is a known failure mode of small models and matters if you're using confidence scores to decide when to auto-flag vs. escalate to a human.

---

## What comes next

The rubric debate is settled for now: vague wins. The next lever is data quality, not prompt length.

Before moving to Judge 2, the corrected examples from this run (the 16 Qwen3 failures, especially the red-team misses) should be marked up and added to the gold set. That corrected data is what fine-tuning will use once the top 3 judges have baselines.

Judge 2 is the **SOP / process adherence judge** — did the agent skip a required step in the workflow? That's a structurally different judgment because it requires the model to track a sequence, not just compare a statement to a fact.

---

# Judge 2 — SOP/Process Adherence
### Did the agent follow all required steps in the workflow?

---

## What this judge is trying to catch

Support teams work from scripts. A password reset has required steps: verify identity, confirm email, send reset, confirm the customer received it. A refund has required steps: pull history, check eligibility, process, send confirmation. These steps exist for reasons — skipping identity verification before a reset is a security risk, skipping the retention offer before cancelling is a lost save opportunity, skipping consent before escalating is bad manners and sometimes a compliance issue.

The SOP adherence judge asks: **did the agent follow the required sequence, or did they skip something?**

This is structurally different from Judge 1. There, the question was "did the agent use this fact?" — a comparison between a claim and a source. Here the question is "did the agent do these things?" — a sequence check. The failure type is omission, not contradiction.

---

## Before you run — two things to expect

**Expect this judge to be easier for the model than Judge 1.** SOP adherence maps naturally to what small models are good at: reading a list and checking whether items appear. The model doesn't have to compare values or detect subtle mismatches — it needs to find steps in the text.

**Expect the hard cases to be about self-assertion.** The red-team examples were built around a specific trap: the agent says "I've verified your identity" without actually showing a verification exchange. A model checking for step mentions will pass this. A model checking for step evidence will catch it.

---

## The three marking schemes

Same three-tier test as Judge 1.

- **Brief 1 (vague):** "Did the agent follow all required steps? If they skipped one, that's a failure."
- **Brief 2 (detailed):** Spells out what counts as skipping — including doing steps out of order, claiming a step was done with no evidence, vague commitment instead of system action, consent after the fact rather than before.
- **Brief 3 (detailed + examples):** Same as detailed plus three worked pass/fail pairs showing what step completion looks like in practice.

**The results:**

| Briefing | Got it right | Missed bad answers | False alarms (flagged good) | Pointed to exact problem |
|---|---|---|---|---|
| Vague | 74% | **0%** | 65% | 100% |
| Detailed | **82%** | **13.3%** | 25% | 86.7% |
| Detailed + examples | **82%** | 23.3% | 10% | 76.7% |

---

## Why the result flipped from Judge 1

In Judge 1, the vague rubric won. More instructions made Qwen worse. Here, the detailed rubric wins. More instructions made it better. Why the difference?

**Judge 1** asked for holistic judgment: is this response grounded in the context? That's a single impressionistic question. Giving the model a checklist let it tick individual boxes and miss the overall picture. Each additional rule became an escape route.

**Judge 2** is inherently a checklist task: did step A happen, did step B happen, did step C happen? The detailed rubric mirrors the structure of the task. Telling the model "watch for steps performed out of order, steps claimed without evidence, vague commitments instead of system actions" is not adding escape routes — it's describing the failure patterns the model needs to look for.

The lesson: the right rubric complexity depends on what the task is. For tasks that require holistic judgment, go simple. For tasks that are inherently about checking a list, give the model the list.

But notice the vague rubric's 0% missed catches. It caught every single bad response — it was just too aggressive, flagging 13 out of 20 good responses as failures. Qwen on vague rubric was the strictest possible judge: never lets anything through. That's not useful in practice (too many false alarms), but it tells you something about where the model sits before you give it structure.

---

## What the examples teach

**Pass examples** cover scenarios where the agent demonstrates step completion through actions rather than announcements. The important pattern: the agent doesn't say "I'm now pulling up your history." It says "I can see your most recent payment was $49.99 on June 4th." That IS the history step — the output of the action proves the action. Judges need to recognize this.

**Fail examples** each skip exactly one step. The coverage was deliberately varied — skipped identity verification, skipped eligibility check, skipped documentation, skipped retention offer, skipped consent, skipped scope confirmation. Each scenario uses a different domain (password reset, refund, billing dispute, cancellation, escalation...) so the model can't memorize domain-specific patterns.

**Red-team examples** target the self-assertion trap specifically: the agent claims step completion without evidence. Eight of the ten red-team examples involve either a step asserted without an observable exchange, a step performed in the wrong order, a step completed with inadequate quality (ambiguous consent), or a generic phrase substituted for a specific action.

---

## Primary model run (Qwen3-4B)

**Official baseline rubric: `detailed`.** Its numbers are the Judge 2 scorecard:

| Metric | Value |
|---|---|
| Got it right | **82%** — better than Judge 1's 68% best result |
| Missed bad answers | **13.3%** — 4 of 30 fail examples slipped through |
| False alarms | **25%** — 5 of 20 good responses wrongly flagged |
| Valid JSON | 100% |
| Pointed to exact problem | 86.7% |

The failure analysis below is from the `detailed_with_examples` run that the runner saves as `primary_outputs.jsonl`. At the same 82% accuracy, that run had a different error distribution: **7 missed catches and 2 false alarms**. Adding worked examples made Qwen more lenient on fail cases (more missed catches) but less trigger-happy on pass cases (fewer false alarms). The detailed rubric's 13.3% missed catches is why it wins.

The 9 failures from the saved run break into clear patterns:

**Two good responses wrongly flagged (false alarms):**
- `sop_pass_02`: Qwen expected the agent to announce "I'm pulling up your history now" as a separate sentence. The agent instead demonstrated history lookup by stating the payment date and amount — showing the output of the action. Qwen didn't recognise implicit step completion.
- `sop_pass_04`: The response included the reason-gathering question and the retention offer in lines 1–3, then the cancellation at line 5. Qwen read the cancellation phrase in isolation and concluded the prior steps were missing. It was reading the response non-sequentially.

**Seven bad responses that slipped through (missed catches):**
- `sop_fail_09`: Agent said "I'll pass your feedback along" — Qwen counted this as logging to the product backlog system. These are different things. One is a verbal promise; the other is a system action that creates a trackable record.
- `sop_fail_10`, `sop_fail_17`: Qwen hallucinated step completions. For the data deletion case, it invented an explanation of what gets deleted — the explanation isn't in the text. For the complaint case, it read "I hope that resolves things" as a follow-up commitment. These are the same rationale hallucinations we saw in Judge 1.
- `sop_rt_05`: Agent said "I've escalated to engineering" — Qwen hallucinated a prior consent request that never happened. Escalating is not the same as asking for consent to escalate.
- `sop_rt_06`: Agent ended with "let me know if there's anything else" — Qwen read this generic close as confirming receipt of a data export file.
- `sop_rt_07`: Agent said "For security I've verified your identity" — Qwen accepted the self-assertion as evidence. No security exchange was visible in the interaction.
- `sop_rt_10`: Customer replied "I guess if I have to" — Qwen treated this reluctant, ambiguous response as explicit confirmation before an irreversible account deletion.

---

## Challenger run + disagreement

**Phi-4 on detailed+examples rubric:**
- 58% accuracy (up from 44% on vague — examples helped more than for Qwen)
- 63.3% missed catches
- 10% false alarms

18 disagreements total. Phi-4 was right in 3 of them — the cases where Qwen was wrong:

- **sop_fail_09**: Phi correctly caught that "I'll pass your feedback along" is not the same as logging to the backlog system. Qwen passed it.
- **sop_rt_10**: Phi correctly flagged "I guess if I have to" as ambiguous consent. Qwen accepted it as explicit.
- **sop_pass_02**: Phi correctly said PASS (implicit step completion counts). Qwen wrongly flagged it as a fail.

In the remaining 15 of 18 disagreements, Phi-4 said PASS when gold was FAIL — the same over-agreement problem as Judge 1.

The interesting shift: adding examples improved Phi-4 by 14 percentage points (44% → 58%), while it hurt Qwen slightly (23.3% missed catches vs 13.3% on plain detailed). This suggests the two models use examples differently. Qwen uses them as evidence for leniency ("here's what a pass looks like — this looks similar"). Phi-4 uses them to learn the boundary ("here's a fail — oh, like this response"). Worth keeping in mind for fine-tuning strategy.

---

## What this run teaches

1. **The right rubric complexity depends on the task type.** For holistic judgment (source-of-truth): simple wins. For sequence checking (SOP adherence): structured wins. Don't assume the vague rubric is always better at 4B parameters.

2. **Rationale hallucination is a model-level problem, not a judge-level one.** It appeared in Judge 1 on 4 red-team examples, and it reappears here in 3 gold-set examples. Qwen invents step completions to justify a pass verdict. This is going to show up in every judge that checks for specific actions. The fine-tuning data needs to target this pattern specifically.

3. **Self-assertion without evidence is the signature red-team pattern for this judge.** The agent says "I've verified your identity" and Qwen accepts it. The fix requires the judge to look for observable evidence of step completion, not just claims of it. Four of the ten red-team failures follow this pattern.

4. **82% accuracy is meaningfully better than Judge 1's 68%.** Step-presence checking is an easier task for a 4B model than claim-vs-context grounding. This matters for judge prioritization: some failure types are inherently easier to detect programmatically.

5. **Qwen still overconfident when wrong.** Correct answers: average confidence 0.815. Wrong answers: 0.927. Same pattern as Judge 1. The model is most certain when it's mistaken.

---

## What comes next

The detailed rubric is locked as the winner for SOP adherence. The next lever is the same as Judge 1: data quality, not prompt engineering.

Judge 3 is the **unsupported promise judge** — did the agent promise an outcome, refund, fix, escalation, or timeline without having a basis for that promise? That's closer to Judge 1 (claim vs. grounding) than to Judge 2 (sequence checking). Expect the vague rubric to perform better again.

---

## Wind-up — what the 16 failures teach

Every Qwen3 miss fell into one of two patterns. It's worth understanding both before moving on.

**Pattern 1: The agent says something wrong and Qwen still passes it.**
This happened on 6 gold-set failures. The clearest case: agent said the API rate limit was 500 req/min; the tool right in front of the judge said 1,000. Qwen said the agent "correctly states the rate limit." It never compared the number. Two other cases were more subtle — Qwen identified the problem in its own reasoning ("this is incorrect") but still returned pass=true in the verdict. The reasoning and the answer contradicted each other.

**Pattern 2: The agent avoids the context without contradicting it, and Qwen passes it.**
This is the harder failure mode, and all 10 red-team examples fell here. The agents in these examples are careful — they say "enough time" instead of 24 hours, "close to the threshold" instead of 48 vs 50, "depends on your billing setup" instead of "next billing cycle." No fact is wrong. But no fact from the provided context is used either.

Qwen's mistake here was using the wrong test. It asked "does this response contradict the context?" instead of "does this response use the context?" Those are different questions. A response can avoid every fact the context contains without contradicting a single one. The red-team was designed to expose that gap, and it did.

**The four rationale hallucinations.** The most alarming finding: on 4 red-team examples, Qwen invented facts from the agent response. It said the agent "mentions the 24-hour window" when the agent said "enough time." It said the agent "mentions next billing cycle" when the agent said "depends on your billing setup." The model was generating plausible-sounding justification rather than reading what the agent actually wrote. If you can't trust the rationale, you can't use it to audit the verdict.

**What goes into fine-tuning data:**
- 6 corrected gold failures → `data/corrected/source_of_truth.jsonl` — cover the rubric interpretation errors
- 10 corrected red-team examples → `data/future_finetune/source_of_truth.jsonl` — cover the avoidance-without-contradiction patterns
- Highest priority training signal: the "doesn't contradict ≠ uses context" pattern (rt_03, rt_10) and the rationale hallucinations (rt_04, rt_06, rt_07, rt_08)

---

# Judge 3 — Unsupported Promise
### Did the agent promise something they couldn't back up?

---

## Before you start — three things to get straight

**What this judge catches.** A support agent sometimes makes commitments that go beyond what they can actually deliver: "You'll have your refund in 24 hours" (policy says 5–7 days), "I can guarantee this won't happen again" (no one can guarantee that), "I'll have a senior engineer call you in 2 hours" (no such SLA exists). These are unsupported promises — specific commitments made without grounding in the available policy or account data. The failure type is `unsupported_promise`.

**Why it matters.** An unsupported promise creates a customer expectation the company can't meet. When the refund doesn't arrive in 24 hours, the customer is angrier than if no timeline had been given at all. When the bug recurs after "I can guarantee it won't," the company has a credibility problem, not just a technical one. The promise itself causes the damage — the failure is in the moment the agent said it.

**What a naive model misses.** Two things. First, hedged language that still implies a specific commitment: "you should receive this within 24 hours" is still a wrong timeline even though it says "should." Second, compositional promises — where part of the response is grounded and a small addition is not. A response that's 90% correct with one unauthorized clause is still a failure. A naive model will read the correct portion, conclude the response is fine, and miss the unauthorized addition at the end.

---

## The three marking schemes

This judge is structurally similar to Judge 1: the model is asked to evaluate a claim against provided context, using holistic judgment rather than checking off a list of steps. That similarity predicts the rubric result before you run it.

**Vague:** "Did the agent make any promises without a basis for them?" — Simple, open-ended. The model knows what a promise is. It can check it against the provided policy.

**Detailed:** Enumerates six types of unsupported promises (timeline, outcome guarantee, unauthorized credit, escalation SLA, feature delivery, invented policy rule). Plus a scoring scale. Makes the model go through a checklist of failure modes.

**Detailed with examples:** Same enumeration plus three worked pass/fail examples and a "tricky cases" section.

**Which rubric won: vague.** With a perfect score.

| Rubric | Accuracy | Missed catches | False alarms |
|---|---|---|---|
| **vague** ← official | **100%** | **0%** | 0% |
| detailed | 96% | 6.7% | 0% |
| detailed_with_examples | 92% | 13.3% | 0% |

More detail made Qwen worse, not better. Adding failure-type categories may have caused Qwen to pattern-match against specific categories (timeline, credit amount) rather than asking the fundamental question. The red-team examples were designed to not fit neatly into categories — conditional framing, compositional promises, hedged language. The vague rubric's open question let Qwen evaluate intent rather than match patterns.

This confirms the cross-judge pattern: holistic judgment → simple rubric. Checklist verification → structured rubric.

---

## What the examples teach

**A pass** looks like an agent who quotes policy exactly ("you'll see the refund within 5–7 business days"), hedges appropriately when outcomes are uncertain ("I can't give you a specific timeframe — it depends on engineering triage"), or stays within authorized limits ("I've applied the $25 loyalty credit"). The agent makes no specific commitment they can't back up.

**An unambiguous fail** looks like a specific number the policy contradicts: "within 24 hours" when policy says 5–7 days. Or a guarantee that is logically impossible: "I can guarantee this won't happen again." Or an amount that exceeds authorization: offering $100 when only $25 is approved. These are easy catches — the model just needs to compare the agent's claim to the policy number.

**What makes the red-team hard.** Ten examples, all `label: false`, all designed to look like reasonable responses:

- **Hedged wrong timelines** (rt_01): Agent says "you should receive it within 24–48 hours." The "should" sounds cautious. But "24–48 hours" is still a factually wrong timeline relative to the 5–7 day policy — hedging the wrong number doesn't make it right.
- **Grounded anchor + unauthorized addition** (rt_03): Agent correctly quotes the refund timeline, then appends "I've also applied a $50 loyalty credit." The first part is fully grounded. The $50 exceeds the $25 policy cap. A model that averages across the whole response will pass it.
- **Conditional framing hiding an absolute guarantee** (rt_04): "Once they identify and patch the root cause, the issue will be resolved permanently — these crashes won't come back." The "once they..." opener sounds like hedging. The conclusion is an absolute guarantee. Policy: "Recurrence cannot be guaranteed."
- **Completed action implying guaranteed outcome** (rt_08): Agent performs two authorized troubleshooting steps, then says "it should work." The steps are grounded. The prediction isn't. Policy: "Resolution not guaranteed — may require engineering escalation."
- **Empathy as cover** (rt_10): Agent opens by explicitly refusing to overpromise ("I can't wave a magic wand"), then immediately makes three specific operational commitments that aren't in policy. The anti-promise framing makes the promises invisible.

---

## Primary model run

**Official rubric (vague): 100% accuracy. No missed catches. No false alarms.**

This is the highest score across all three judges on their official rubric. The unsupported promise judge, run on the simple rubric, produced a perfect baseline. The model's intuition about what constitutes a promise — and whether it's grounded — is strong enough that it doesn't need enumeration.

The saved run (detailed_with_examples) shows where things break down:

**Four missed catches on detailed_with_examples:**

- **up_fail_15** — Agent says "99.99% uptime"; policy says 99.9%. Qwen's rationale said the agent "correctly references 99.9% uptime." It misread a digit. 99.9% and 99.99% are different commitments — 99.99% allows 52 minutes of downtime per year, 99.9% allows 8.7 hours. Qwen collapsed two similar-looking numbers and evaluated the wrong one.

- **up_rt_03** — The $50 credit appended to a grounded refund response. Qwen's rationale is extraordinary: it first says "$50 is within the policy's maximum of $25" (arithmetic error — $50 > $25), then catches itself ("which is not in the policy"), then rationalizes it away ("the agent does not explicitly promise the credit") despite the agent saying "I've applied a $50 loyalty credit." The model identified the violation in its own reasoning and then voted PASS anyway.

- **up_rt_04** — "Resolved permanently, these crashes won't come back." Qwen's rationale called this "consistent with the policy context." The policy says "Recurrence cannot be guaranteed post-fix." Direct contradiction. The conditional opener tricked the model into reading the whole sentence as hedged.

- **up_rt_08** — "It should work." Qwen correctly identified the troubleshooting steps as grounded, then concluded the outcome prediction was grounded too. Authorized action ≠ authorized outcome claim. These are different claims requiring separate evaluation.

Confidence pattern holds: Qwen averaged 100% confidence on its 4 wrong verdicts — most certain when wrong.

---

## Challenger run + disagreement

**Phi-4 on detailed_with_examples: 50% accuracy, 83.3% missed catches.**

Same rubber-stamp pattern as Judges 1 and 2, amplified. Phi-4 said PASS on 25 of the 30 fail examples. In 22 of 23 disagreements with Qwen, Phi-4 said PASS when gold was FAIL. The detailed_with_examples rubric made it worse than vague (72% accuracy on vague, 50% on detailed_with_examples) — adding category detail to a model that's already inclined to agree makes it more confused, not more precise.

The one useful Phi-4 catch: **up_fail_15** — the SLA digit error. Phi-4 correctly flagged "99.99%" as wrong when Qwen passed it. This is the same pattern as Judges 1 and 2: if Phi-4 flags something Qwen passed, look carefully. That signal fired once here, and it was correct.

Phi-4's PASS verdicts carry no weight. Its FAIL verdicts on Qwen passes are worth a second look.

---

## What this run teaches

**The task structure prediction held.** Before running, the expectation was that vague would win again — because unsupported promise is a holistic claim-vs-grounding task like source-of-truth, not a checklist task like SOP adherence. The result confirmed it exactly: vague 100%, detailed 96%, detailed_with_examples 92%. The degradation from simple to complex rubric follows the same direction as Judge 1, just steeper.

**Three judges, a clear pattern:**
- Holistic judgment (does this claim have a basis?) → simple rubric
- Checklist verification (was each step completed?) → structured rubric

This means rubric selection is not just prompt engineering — it's task classification. Before building the rubric for Judge 4 (technical diagnosis), the first question is: is this a holistic judgment or a checklist? The answer determines the rubric before you run a single example.

**The new failure mode: compositional evaluation.** All three red-team failures that Qwen missed involve evaluating a response that is partially grounded. The model anchors on the grounded portion and extends that judgment to the whole response. This is a structural gap: the judge needs to evaluate each claim in a response independently, not holistically. Fine-tuning data for this pattern: rt_03 (grounded anchor + unauthorized addition), rt_04 (conditional opener + absolute conclusion), rt_08 (authorized action + unauthorized outcome claim).

**What comes next:** Judge 4 — technical diagnosis. Did the agent's explanation of a technical issue accurately reflect what the KB article or tool context says? This may require reading technical content precisely — the digit-misread failure (up_fail_15) is a preview of what happens when precision matters and the model reads loosely.
