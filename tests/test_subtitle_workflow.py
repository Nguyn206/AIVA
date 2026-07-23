from engine.context import WorkflowContext
from engine.executor import WorkflowExecutor
from schemas.video_planning import Storyboard
from workflows.subtitle_generation import (
    build_subtitle_generation_workflow,
)


def test_subtitle_workflow_adds_asset_to_context(tmp_path) -> None:
    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 2,
                    "narration": "Opening hook.",
                    "visual_description": "Product close-up",
                    "image_prompt": "Image prompt",
                    "video_prompt": "Video prompt",
                }
            ]
        }
    )
    workflow = build_subtitle_generation_workflow(
        output_directory=tmp_path
    )
    context = WorkflowContext(data={"storyboard": storyboard})

    report = WorkflowExecutor().run(workflow, context).unwrap()
    asset = report.context.require("subtitle_asset")

    assert asset.srt_path.exists()
    assert asset.vtt_path.exists()


def test_subtitle_workflow_requires_storyboard(tmp_path) -> None:
    workflow = build_subtitle_generation_workflow(
        output_directory=tmp_path
    )

    result = WorkflowExecutor().run(
        workflow,
        WorkflowContext(),
    )

    assert result.success is False
    assert "Storyboard" in (result.error or "")
