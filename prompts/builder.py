from __future__ import annotations

from typing import Any

from prompts.template import PromptTemplate


class PromptBuilder:
    """Fluent builder for preparing a rendered AI prompt."""

    def __init__(self, template: PromptTemplate) -> None:
        self.template = template
        self._variables: dict[str, Any] = {}

    def with_variable(
        self,
        name: str,
        value: Any,
    ) -> PromptBuilder:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Prompt variable name must not be empty.")

        self._variables[normalized_name] = value
        return self

    def with_variables(
        self,
        variables: dict[str, Any],
    ) -> PromptBuilder:
        for name, value in variables.items():
            self.with_variable(name, value)
        return self

    def build(self, *, strict: bool = True) -> str:
        return self.template.render(
            self._variables,
            strict=strict,
        )

    def reset(self) -> PromptBuilder:
        self._variables.clear()
        return self
