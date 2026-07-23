import pytest

from prompts.exceptions import (
    PromptRenderError,
    PromptValidationError,
)
from prompts.template import PromptTemplate


def test_template_extracts_variables() -> None:
    prompt = PromptTemplate(
        name="script",
        content="Create {{tone}} video about {{product}}.",
    )

    assert prompt.variables == frozenset({"tone", "product"})


def test_template_renders_variables() -> None:
    prompt = PromptTemplate(
        name="script",
        content="Create {{tone}} video about {{product}}.",
    )

    rendered = prompt.render(
        {"tone": "energetic", "product": "camera"}
    )

    assert rendered == "Create energetic video about camera."


def test_template_reports_missing_variables() -> None:
    prompt = PromptTemplate(
        name="script",
        content="Create video about {{product}}.",
    )

    with pytest.raises(PromptRenderError, match="product"):
        prompt.render({})


def test_template_rejects_empty_content() -> None:
    with pytest.raises(PromptValidationError):
        PromptTemplate(name="invalid", content=" ")
