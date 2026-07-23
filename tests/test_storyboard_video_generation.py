from engine.context import WorkflowContext
from engine.executor import WorkflowExecutor
from providers.image.mock import MockImageProvider
from providers.image.models import ImageGenerationRequest
from providers.video.mock import MockVideoProvider
from schemas.video_planning import Storyboard
from services.image_generation import SceneImageAsset
from workflows.video_generation import (
    build_video_generation_workflow,
)


def test_video_workflow_generates_clip_for_each_scene(tmp_path) -> None:
    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 3,
                    "narration": "Hook",
                    "visual_description": "Product close-up",
                    "image_prompt": "Image one",
                    "video_prompt": "Slow push-in",
                },
                {
                    "scene_number": 2,
                    "duration_seconds": 4,
                    "narration": "Benefit",
                    "visual_description": "Product in use",
                    "image_prompt": "Image two",
                    "video_prompt": "Tracking shot",
                },
            ]
        }
    )
    image_provider = MockImageProvider()
    images = []

    for scene in storyboard.scenes:
        image = image_provider.generate(
            ImageGenerationRequest(prompt=scene.image_prompt),
            output_directory=tmp_path / f"image_{scene.scene_number}",
        ).unwrap().images[0]
        images.append(
            SceneImageAsset(
                scene_number=scene.scene_number,
                image=image,
            )
        )

    workflow = build_video_generation_workflow(
        MockVideoProvider(),
        output_directory=tmp_path / "videos",
    )
    context = WorkflowContext(
        data={
            "storyboard": storyboard,
            "scene_images": tuple(images),
        }
    )

    report = WorkflowExecutor().run(workflow, context).unwrap()
    assets = report.context.require("scene_videos")

    assert len(assets) == 2
    assert all(asset.video.path.exists() for asset in assets)
    assert [asset.scene_number for asset in assets] == [1, 2]


def test_video_workflow_requires_scene_images(tmp_path) -> None:
    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 2,
                    "narration": "Hook",
                    "visual_description": "Product",
                    "image_prompt": "Image",
                    "video_prompt": "Video",
                }
            ]
        }
    )
    workflow = build_video_generation_workflow(
        MockVideoProvider(),
        output_directory=tmp_path,
    )

    result = WorkflowExecutor().run(
        workflow,
        WorkflowContext(data={"storyboard": storyboard}),
    )

    assert result.success is False
    assert "Scene images" in (result.error or "")
