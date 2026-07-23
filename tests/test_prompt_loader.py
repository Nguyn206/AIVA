from pathlib import Path

from prompts.loader import PromptLoader


def test_loader_reads_markdown_file(tmp_path: Path) -> None:
    path = tmp_path / "storyboard.md"
    path.write_text(
        "Storyboard for {{script}}",
        encoding="utf-8",
    )

    prompt = PromptLoader().load_file(path)

    assert prompt.name == "storyboard"
    assert prompt.variables == frozenset({"script"})


def test_loader_reads_directory(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("A", encoding="utf-8")
    (tmp_path / "b.md").write_text("B", encoding="utf-8")
    (tmp_path / "ignore.txt").write_text(
        "ignored",
        encoding="utf-8",
    )

    prompts = PromptLoader().load_directory(tmp_path)

    assert [prompt.name for prompt in prompts] == ["a", "b"]
