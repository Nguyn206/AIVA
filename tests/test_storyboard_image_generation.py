from engine.context import WorkflowContext
from engine.executor import WorkflowExecutor
from providers.image.mock import MockImageProvider
from schemas.video_planning import Storyboard
from workflows.image_generation import (
    build_image_generation_workflow,
)


def test_image_workflow_generates_asset_for_each_scene(tmp_path) -> None:
    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 3,
                    "narration": "Hook",
                    "visual_description": "Product close-up",
                    "image_prompt": "Cinematic camera close-up",
                    "video_prompt": "Slow push-in",
                },
                {
                    "scene_number": 2,
                    "duration_seconds": 4,
                    "narration": "Benefit",
                    "visual_description": "Product in use",
                    "image_prompt": "Camera protecting a home",
                    "video_prompt": "Smooth tracking shot",
                },
            ]
        }
    )
    provider = MockImageProvider()
    workflow = build_image_generation_workflow(
        provider,
        output_directory=tmp_path,
    )
    context = WorkflowContext(data={"storyboard": storyboard})

    report = WorkflowExecutor().run(workflow, context).unwrap()
    assets = report.context.require("scene_images")

    assert len(assets) == 2
    assert all(asset.image.path.exists() for asset in assets)
    assert [asset.scene_number for asset in assets] == [1, 2]
