import pytest

from prompts.exceptions import (
    DuplicatePromptError,
    PromptNotFoundError,
)
from prompts.registry import PromptRegistry
from prompts.template import PromptTemplate


def test_registry_returns_latest_version() -> None:
    registry = PromptRegistry()
    registry.register(
        PromptTemplate(
            name="script",
            content="version one",
            version="1.0.0",
        )
    )
    registry.register(
        PromptTemplate(
            name="script",
            content="version two",
            version="2.0.0",
        )
    )

    assert registry.get("script").content == "version two"
    assert registry.versions("script") == ("1.0.0", "2.0.0")


def test_registry_rejects_duplicate_version() -> None:
    registry = PromptRegistry()
    prompt = PromptTemplate(name="script", content="content")
    registry.register(prompt)

    with pytest.raises(DuplicatePromptError):
        registry.register(prompt)


def test_registry_reports_missing_prompt() -> None:
    registry = PromptRegistry()

    with pytest.raises(PromptNotFoundError):
        registry.get("missing")
