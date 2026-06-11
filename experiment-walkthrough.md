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
