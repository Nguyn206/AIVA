from __future__ import annotations

import json
from typing import Any


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse an object from plain JSON or a fenced Markdown block."""
    normalized = text.strip()
    if not normalized:
        raise ValueError("Cannot parse an empty JSON response.")

    if normalized.startswith("```"):
        normalized = _strip_code_fence(normalized)

    try:
        value = json.loads(normalized)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"AI response is not valid JSON: {exc.msg}"
        ) from exc

    if not isinstance(value, dict):
        raise ValueError("AI response must be a JSON object.")

    return value


def _strip_code_fence(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return text

    first = lines[0].strip()
    if not first.startswith("```"):
        return text

    if lines[-1].strip() == "```":
        lines = lines[1:-1]
    else:
        lines = lines[1:]

    return "\n".join(lines).strip()
