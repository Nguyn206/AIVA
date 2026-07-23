import pytest

from engine.step import FunctionStep
from engine.workflow import Workflow


def test_workflow_manages_ordered_steps() -> None:
    first = FunctionStep("research", lambda context: context)
    second = FunctionStep("script", lambda context: context)
    workflow = Workflow("video_generation", steps=[first, second])

    assert [step.name for step in workflow] == ["research", "script"]
    assert workflow.get_step("script") is second


def test_workflow_rejects_duplicate_step_names() -> None:
    workflow = Workflow("video_generation")
    workflow.add_step(
        FunctionStep("research", lambda context: context)
    )

    with pytest.raises(ValueError, match="already contains"):
        workflow.add_step(
            FunctionStep("research", lambda context: context)
        )


def test_workflow_remove_step() -> None:
    workflow = Workflow(
        "video_generation",
        steps=[FunctionStep("research", lambda context: context)],
    )

    removed = workflow.remove_step("research")

    assert removed.name == "research"
    assert len(workflow) == 0
