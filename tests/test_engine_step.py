from core.result import Result
from engine.context import WorkflowContext
from engine.step import BaseStep, FunctionStep


class AddScriptStep(BaseStep):
    def __init__(self) -> None:
        super().__init__("generate_script")

    def execute(self, context: WorkflowContext) -> Result[WorkflowContext]:
        context.put("script", "Opening hook")
        return Result.ok(context)


class FailingStep(BaseStep):
    def __init__(self) -> None:
        super().__init__("failing_step")

    def execute(self, context: WorkflowContext) -> Result[WorkflowContext]:
        return Result.fail(
            "provider unavailable",
            error_type="ProviderError",
        )


def test_base_step_updates_context() -> None:
    context = WorkflowContext()

    result = AddScriptStep()(context)

    assert result.success is True
    assert result.unwrap().require("script") == "Opening hook"


def test_disabled_step_is_skipped() -> None:
    context = WorkflowContext()
    step = FunctionStep(
        "disabled",
        lambda active_context: active_context.put("called", True),
        enabled=False,
    )

    result = step(context)

    assert result.success is True
    assert context.exists("called") is False


def test_function_step_supports_none_return() -> None:
    context = WorkflowContext()
    step = FunctionStep(
        "set_topic",
        lambda active_context: active_context.put("topic", "camera"),
    )

    result = step(context)

    assert result.unwrap().require("topic") == "camera"


def test_failed_step_returns_failure() -> None:
    result = FailingStep()(WorkflowContext())

    assert result.success is False
    assert result.error == "provider unavailable"
