from __future__ import annotations

from pathlib import Path
from typing import Any

from prompts.exceptions import PromptValidationError
from prompts.template import PromptTemplate


class PromptLoader:
    """Loads Markdown prompt templates from disk."""

    def load_file(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        version: str = "1.0.0",
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> PromptTemplate:
        source = Path(path)

        if not source.is_file():
            raise FileNotFoundError(
                f"Prompt template file not found: {source}"
            )

        content = source.read_text(encoding="utf-8")
        prompt_name = name or source.stem

        return PromptTemplate(
            name=prompt_name,
            content=content,
            version=version,
            description=description,
            metadata=metadata or {},
        )

    def load_directory(
        self,
        directory: str | Path,
        *,
        pattern: str = "*.md",
    ) -> tuple[PromptTemplate, ...]:
        source = Path(directory)

        if not source.is_dir():
            raise PromptValidationError(
                f"Prompt directory not found: {source}"
            )

        return tuple(
            self.load_file(path)
            for path in sorted(source.glob(pattern))
            if path.is_file()
        )
