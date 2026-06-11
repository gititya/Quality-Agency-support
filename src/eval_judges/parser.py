"""Parse model output into verdict dict. Handles JSON in markdown fences and raw JSON."""
import json
import re

REQUIRED_FIELDS = {"pass", "score", "failure_type", "exact_failure_span", "rationale", "safer_requirement", "confidence"}


def extract_json(text: str) -> dict | None:
    # Strip markdown code fences if present
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()

    # Find first { ... } block
    brace_match = re.search(r"\{[\s\S]*\}", text)
    if not brace_match:
        return None

    try:
        return json.loads(brace_match.group())
    except json.JSONDecodeError:
        return None


def parse_verdict(raw_output: str) -> tuple[dict | None, list[str]]:
    """
    Returns (verdict_dict, errors).
    verdict_dict is None if JSON could not be parsed.
    errors lists any missing or invalid fields even when verdict_dict is present.
    """
    verdict = extract_json(raw_output)
    if verdict is None:
        return None, ["could not parse JSON from output"]

    errors = []
    for field in REQUIRED_FIELDS:
        if field not in verdict:
            errors.append(f"missing field: {field}")

    if "pass" in verdict and not isinstance(verdict["pass"], bool):
        errors.append("'pass' must be a boolean")

    if "score" in verdict:
        try:
            s = float(verdict["score"])
            if not (0.0 <= s <= 1.0):
                errors.append("'score' must be between 0.0 and 1.0")
        except (TypeError, ValueError):
            errors.append("'score' must be a float")

    if "confidence" in verdict and verdict["confidence"] not in ("low", "medium", "high"):
        errors.append("'confidence' must be 'low', 'medium', or 'high'")

    return verdict, errors
