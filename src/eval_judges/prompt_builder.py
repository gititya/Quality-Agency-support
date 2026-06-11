"""Build judge prompts from registry rubric variant + example input."""
import yaml
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent.parent / "judges" / "registry.yaml"

_registry = None


def _load_registry():
    global _registry
    if _registry is None:
        with open(REGISTRY_PATH) as f:
            data = yaml.safe_load(f)
        _registry = {j["id"]: j for j in data["judges"]}
    return _registry


def build_prompt(judge_id: str, rubric_variant: str, example: dict) -> str:
    registry = _load_registry()
    judge = registry[judge_id]
    rubric = judge["rubric_variants"][rubric_variant]["prompt"].strip()

    parts = [rubric, ""]

    parts.append(f"Ticket: {example['ticket']}")
    parts.append(f"Agent response: {example['agent_response']}")

    if example.get("conversation"):
        parts.append(f"Conversation history: {example['conversation']}")
    if example.get("policy_context"):
        parts.append(f"Policy context: {example['policy_context']}")
    if example.get("tool_context"):
        parts.append(f"Tool context: {example['tool_context']}")
    if example.get("expected_process"):
        parts.append(f"Expected process: {example['expected_process']}")
    if example.get("handoff_note"):
        parts.append(f"Handoff note: {example['handoff_note']}")

    parts.append("")
    parts.append("Return your verdict as a JSON object only. No markdown fences, no explanation outside the JSON.")

    return "\n".join(parts)
