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
    parts.append(
        "Scope discipline: judge only the quality dimension named in the rubric. "
        "Do not credit or penalize unrelated dimensions such as handoff completeness, "
        "process adherence, technical diagnosis, or source grounding unless that dimension "
        "is the rubric's actual target."
    )
    parts.append(
        "Span discipline: exact_failure_span must be copied from Agent response, "
        "or from Handoff note when judging handoff_completeness. Do not copy spans from "
        "Ticket, Conversation history, Policy context, Tool context, or Expected process. "
        "If the failure is an omission with no exact bad phrase, use null and explain the "
        "missing item through missing_requirement and evidence_gap."
    )
    parts.append(
        "For failures caused by omitted steps, missing evidence, or incomplete handoff details, "
        "also include optional JSON fields: "
        '"missing_requirement" (what required item is absent) and '
        '"evidence_gap" (what evidence is missing from the response or handoff).'
    )
    parts.append("Return your verdict as a JSON object only. No markdown fences, no explanation outside the JSON.")

    return "\n".join(parts)
