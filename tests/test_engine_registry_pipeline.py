import pytest

from engine.context import WorkflowContext
from engine.pipeline import Pipeline
from engine.registry import WorkflowRegistry
from engine.step import FunctionStep
from engine.workflow import Workflow


def test_registry_registers_and_returns_workflow() -> None:
    registry = WorkflowRegistry()
    workflow = Workflow("affiliate_video")

    registry.register(workflow)

    assert registry.get("affiliate_video") is workflow
    assert registry.names() == ("affiliate_video",)


def test_registry_rejects_duplicate_workflow() -> None:
    registry = WorkflowRegistry()
    registry.register(Workflow("affiliate_video"))

    with pytest.raises(ValueError, match="already registered"):
        registry.register(Workflow("affiliate_video"))


def test_pipeline_builds_and_runs_workflow() -> None:
    pipeline = (
        Pipeline("automatic_video")
        .then(
            FunctionStep(
                "create_script",
                lambda context: context.put(
                    "script",
                    "AI-generated script",
                ),
            )
        )
        .then(
            FunctionStep(
                "create_voice",
                lambda context: context.put(
                    "voice",
                    f"voice:{context.require('script')}",
                ),
            )
        )
    )

    result = pipeline.run(WorkflowContext(project_id="video-001"))
    report = result.unwrap()

    assert report.context.require("voice") == (
        "voice:AI-generated script"
    )
    assert pipeline.build().name == "automatic_video"
