import json

from engine.context import WorkflowContext
from engine.executor import WorkflowExecutor
from providers.mock import MockLLMProvider
from schemas.video_planning import (
    ProductInput,
    Storyboard,
    VideoScript,
)
from workflows.video_planning import (
    VideoPlanningConfig,
    build_video_planning_workflow,
)


def response_factory(request):
    if "product analysis AI" in request.prompt:
        return json.dumps(
            {
                "product_name": "Smart Camera",
                "category": "Home security",
                "primary_problem": "Unmonitored homes",
                "unique_selling_points": ["AI motion alerts"],
                "customer_benefits": ["Faster awareness"],
                "emotional_benefits": ["Peace of mind"],
                "target_audience": ["Home owners"],
                "objections": ["Privacy"],
                "proof_points": ["Night vision"],
                "recommended_video_angle": "See threats early",
            }
        )

    if "advertising script writer" in request.prompt:
        return json.dumps(
            {
                "title": "See It Before It Happens",
                "hook": "Your home cannot warn you. This camera can.",
                "scenes": [{"scene": 1, "purpose": "hook"}],
                "narration": "Protect your home with AI alerts.",
                "call_to_action": "Secure your home today.",
            }
        )

    return json.dumps(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 5,
                    "narration": "Protect your home.",
                    "visual_description": "Camera watching a doorway",
                    "image_prompt": "Cinematic smart camera close-up",
                    "video_prompt": "Slow push-in toward smart camera",
                    "on_screen_text": "AI protection",
                    "transition": "cut",
                }
            ]
        }
    )


def test_video_planning_workflow_builds_complete_plan() -> None:
    provider = MockLLMProvider(response=response_factory)
    workflow = build_video_planning_workflow(
        provider,
        config=VideoPlanningConfig(duration_seconds=20),
    )
    context = WorkflowContext(
        data={
            "product_input": ProductInput(
                name="Smart Camera",
                description="AI security camera with motion alerts",
                target_market="Home owners",
            )
        }
    )

    report = WorkflowExecutor().run(workflow, context).unwrap()

    assert report.completed_steps == (
        "analyze_product",
        "generate_script",
        "generate_storyboard",
    )
    assert isinstance(
        report.context.require("video_script"),
        VideoScript,
    )
    assert isinstance(
        report.context.require("storyboard"),
        Storyboard,
    )
    assert len(provider.requests) == 3


def test_video_planning_stops_without_product_input() -> None:
    provider = MockLLMProvider(response=response_factory)
    workflow = build_video_planning_workflow(provider)

    result = WorkflowExecutor().run(workflow, WorkflowContext())

    assert result.success is False
    assert "ProductInput" in (result.error or "")
