import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eval_judges.prompt_builder import build_prompt


CASE = {
    "ticket": "Webhook deliveries stopped after a signing-secret rotation.",
    "conversation": "Agent: I am checking the delivery logs now.",
    "agent_response": (
        "I cannot promise a full backfill until integrations review. "
        "Please update the receiver secret and replay one event as a test."
    ),
    "policy_context": "Full backfill requires integrations review.",
    "tool_context": "Delivery logs show 401 signature_mismatch.",
    "expected_process": ["acknowledge urgency", "confirm receiver update before replay"],
    "handoff_note": "Northstar webhooks failing after secret rotation.",
}


def test_unsupported_promise_prompt_treats_refusal_to_promise_as_safe():
    prompt = build_prompt("unsupported_promise", "vague", CASE)

    assert "Do not treat a refusal to promise as an unsupported promise" in prompt
    assert "I cannot promise" in prompt
    assert "I cannot guarantee" in prompt
    assert "Judge only unsupported commitments" in prompt


def test_prompt_requires_failure_spans_from_evaluated_text_only():
    prompt = build_prompt("sop_adherence", "detailed_with_examples", CASE)

    assert "Span discipline" in prompt
    assert "exact_failure_span must be copied from Agent response" in prompt
    assert "Do not copy spans from Ticket, Conversation history" in prompt
    assert "If the failure is an omission with no exact bad phrase, use null" in prompt


def test_prompt_keeps_judges_inside_their_own_scope():
    prompt = build_prompt("technical_diagnosis", "detailed_with_examples", CASE)

    assert "Scope discipline" in prompt
    assert "judge only the quality dimension named in the rubric" in prompt
    assert "Do not credit or penalize unrelated dimensions" in prompt
