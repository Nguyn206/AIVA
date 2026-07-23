from __future__ import annotations

from pathlib import Path
from typing import Any

from prompts.builder import PromptBuilder
from prompts.loader import PromptLoader
from prompts.registry import PromptRegistry
from prompts.template import PromptTemplate


class PromptManager:
    """High-level interface used by AIVA workflow steps."""

    def __init__(
        self,
        registry: PromptRegistry | None = None,
        loader: PromptLoader | None = None,
    ) -> None:
        self.registry = registry or PromptRegistry()
        self.loader = loader or PromptLoader()

    def register(
        self,
        prompt: PromptTemplate,
        *,
        replace: bool = False,
    ) -> PromptTemplate:
        return self.registry.register(
            prompt,
            replace=replace,
        )

    def load_and_register(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        version: str = "1.0.0",
        description: str = "",
        metadata: dict[str, Any] | None = None,
        replace: bool = False,
    ) -> PromptTemplate:
        prompt = self.loader.load_file(
            path,
            name=name,
            version=version,
            description=description,
            metadata=metadata,
        )
        return self.register(prompt, replace=replace)

    def render(
        self,
        name: str,
        variables: dict[str, Any],
        *,
        version: str | None = None,
        strict: bool = True,
    ) -> str:
        prompt = self.registry.get(name, version=version)
        return PromptBuilder(prompt).with_variables(
            variables
        ).build(strict=strict)
