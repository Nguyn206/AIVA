from engine.context import WorkflowContext
from engine.pipeline import Pipeline
from engine.step import FunctionStep
from providers.mock import MockLLMProvider
from providers.models import LLMRequest


def test_provider_can_run_inside_video_workflow() -> None:
    provider = MockLLMProvider(
        response='{"hook": "Stop scrolling"}'
    )

    def generate_script(context: WorkflowContext) -> None:
        result = provider.generate(
            LLMRequest(prompt=context.require("prompt"))
        )
        context.put("script", result.unwrap().text)

    pipeline = Pipeline("ai_video").then(
        FunctionStep("generate_script", generate_script)
    )
    context = WorkflowContext(
        data={"prompt": "Write an advertising hook"}
    )

    report = pipeline.run(context).unwrap()

    assert report.context.require("script") == (
        '{"hook": "Stop scrolling"}'
    )
