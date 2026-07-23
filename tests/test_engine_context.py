import pytest

from engine.context import WorkflowContext


def test_context_stores_and_requires_values() -> None:
    context = WorkflowContext(project_id="video-001")
    context.put("product_name", "AI Camera")

    assert context.get("product_name") == "AI Camera"
    assert context.require("product_name") == "AI Camera"
    assert "product_name" in context


def test_context_require_raises_for_missing_key() -> None:
    context = WorkflowContext()

    with pytest.raises(KeyError, match="missing"):
        context.require("missing")


def test_context_snapshot_is_independent_copy() -> None:
    context = WorkflowContext(data={"storyboard": {"scenes": [1]}})

    snapshot = context.snapshot()
    snapshot["data"]["storyboard"]["scenes"].append(2)

    assert context.require("storyboard") == {"scenes": [1]}


def test_context_rejects_empty_keys() -> None:
    context = WorkflowContext()

    with pytest.raises(ValueError):
        context.put("  ", "invalid")
