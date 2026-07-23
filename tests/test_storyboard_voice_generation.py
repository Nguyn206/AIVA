from engine.context import WorkflowContext
from engine.executor import WorkflowExecutor
from providers.audio.mock import MockVoiceProvider
from schemas.video_planning import Storyboard
from workflows.voice_generation import build_voice_generation_workflow


def test_voice_workflow_generates_audio_for_each_scene(tmp_path) -> None:
    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 3,
                    "narration": "Stop scrolling.",
                    "visual_description": "Product close-up",
                    "image_prompt": "Image one",
                    "video_prompt": "Video one",
                },
                {
                    "scene_number": 2,
                    "duration_seconds": 4,
                    "narration": "Here is the solution.",
                    "visual_description": "Product in use",
                    "image_prompt": "Image two",
                    "video_prompt": "Video two",
                },
            ]
        }
    )
    provider = MockVoiceProvider()
    workflow = build_voice_generation_workflow(
        provider,
        output_directory=tmp_path,
        response_format="wav",
    )
    context = WorkflowContext(data={"storyboard": storyboard})

    report = WorkflowExecutor().run(workflow, context).unwrap()
    assets = report.context.require("scene_narration_audio")

    assert len(assets) == 2
    assert all(asset.audio.path.exists() for asset in assets)
    assert [asset.scene_number for asset in assets] == [1, 2]
