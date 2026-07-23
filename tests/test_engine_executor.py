from core.result import Result
from engine.context import WorkflowContext
from engine.executor import WorkflowExecutor
from engine.step import BaseStep, FunctionStep
from engine.workflow import Workflow


class FailureStep(BaseStep):
    def __init__(self) -> None:
        super().__init__("render_video")

    def execute(self, context: WorkflowContext) -> Result[WorkflowContext]:
        return Result.fail("render failed")


def test_executor_runs_steps_in_order() -> None:
    workflow = Workflow(
        "automatic_video",
        steps=[
            FunctionStep(
                "research",
                lambda context: context.put("research", True),
            ),
            FunctionStep(
                "script",
                lambda context: context.put(
                    "script",
                    context.require("research"),
                ),
            ),
        ],
    )

    result = WorkflowExecutor().run(workflow)

    report = result.unwrap()
    assert report.success is True
    assert report.completed_steps == ("research", "script")
    assert report.context.require("script") is True


def test_executor_stops_after_failure() -> None:
    workflow = Workflow(
        "automatic_video",
        steps=[
            FunctionStep(
                "research",
                lambda context: context.put("research", True),
            ),
            FailureStep(),
            FunctionStep(
                "publish",
                lambda context: context.put("published", True),
            ),
        ],
    )

    result = WorkflowExecutor().run(workflow, WorkflowContext())

    assert result.success is False
    assert result.error == "render failed"
