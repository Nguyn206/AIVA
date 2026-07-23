from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from prompts.exceptions import PromptRenderError, PromptValidationError

_PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_.-]*)\s*}}")


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    """Immutable prompt template used by AIVA's AI-video pipeline."""

    name: str
    content: str
    version: str = "1.0.0"
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise PromptValidationError("Prompt name must not be empty.")
        if not self.content.strip():
            raise PromptValidationError(
                f"Prompt content must not be empty: {self.name}"
            )
        if not self.version.strip():
            raise PromptValidationError(
                f"Prompt version must not be empty: {self.name}"
            )

    @property
    def variables(self) -> frozenset[str]:
        return frozenset(_PLACEHOLDER_PATTERN.findall(self.content))

    def render(
        self,
        variables: dict[str, Any],
        *,
        strict: bool = True,
    ) -> str:
        missing = self.variables.difference(variables)

        if strict and missing:
            names = ", ".join(sorted(missing))
            raise PromptRenderError(
                f"Missing prompt variables for {self.name!r}: {names}"
            )

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in variables:
                return match.group(0)
            return str(variables[key])

        rendered = _PLACEHOLDER_PATTERN.sub(replace, self.content)

        if strict and _PLACEHOLDER_PATTERN.search(rendered):
            raise PromptRenderError(
                f"Unresolved placeholders remain in prompt: {self.name}"
            )

        return rendered.strip()
