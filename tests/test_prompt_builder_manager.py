from pathlib import Path

from prompts.builder import PromptBuilder
from prompts.manager import PromptManager
from prompts.template import PromptTemplate


def test_builder_renders_prompt() -> None:
    prompt = PromptTemplate(
        name="image",
        content="{{style}} image of {{product}}",
    )

    result = (
        PromptBuilder(prompt)
        .with_variable("style", "cinematic")
        .with_variable("product", "smartwatch")
        .build()
    )

    assert result == "cinematic image of smartwatch"


def test_manager_loads_and_renders_prompt(tmp_path: Path) -> None:
    path = tmp_path / "script.md"
    path.write_text(
        "Create {{duration}} second video about {{product}}.",
        encoding="utf-8",
    )

    manager = PromptManager()
    manager.load_and_register(path)

    result = manager.render(
        "script",
        {"duration": 30, "product": "headphones"},
    )

    assert result == "Create 30 second video about headphones."
