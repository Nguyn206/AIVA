from engine.context import WorkflowContext
from engine.executor import WorkflowExecutor
from providers.audio.mock import MockVoiceProvider
from providers.audio.models import VoiceGenerationRequest
from providers.image.mock import MockImageProvider
from providers.image.models import ImageGenerationRequest
from providers.video.mock import MockVideoProvider
from providers.video.models import VideoGenerationRequest
from render.engine import RenderEngine
from render.ffmpeg import MockFFmpegRunner
from services.image_generation import SceneImageAsset
from services.subtitle_generation import StoryboardSubtitleGenerator
from services.video_generation import SceneVideoAsset
from services.voice_generation import SceneNarrationAsset
from workflows.rendering import build_render_workflow


def test_render_workflow_creates_final_video(tmp_path) -> None:
    image_provider = MockImageProvider()
    image = image_provider.generate(
        ImageGenerationRequest(prompt="Product image"),
        output_directory=tmp_path / "image",
    ).unwrap().images[0]

    video_provider = MockVideoProvider()
    video = video_provider.generate(
        VideoGenerationRequest(
            prompt="Animate product",
            source_image=image.path,
            duration_seconds=2,
        ),
        output_path=tmp_path / "clip.mp4",
    ).unwrap().video

    voice_provider = MockVoiceProvider()
    audio = voice_provider.generate(
        VoiceGenerationRequest(
            text="Buy this product.",
            response_format="wav",
        ),
        output_path=tmp_path / "voice.wav",
    ).unwrap().audio

    from schemas.video_planning import Storyboard

    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 2,
                    "narration": "Buy this product.",
                    "visual_description": "Product",
                    "image_prompt": "Image",
                    "video_prompt": "Video",
                }
            ]
        }
    )
    subtitles = StoryboardSubtitleGenerator(
        output_directory=tmp_path / "subs"
    ).generate(storyboard).unwrap()

    context = WorkflowContext(
        data={
            "scene_videos": (
                SceneVideoAsset(scene_number=1, video=video),
            ),
            "scene_narration_audio": (
                SceneNarrationAsset(scene_number=1, audio=audio),
            ),
            "subtitle_asset": subtitles,
            "scene_images": (
                SceneImageAsset(scene_number=1, image=image),
            ),
        }
    )
    output_path = tmp_path / "final.mp4"
    workflow = build_render_workflow(
        engine=RenderEngine(MockFFmpegRunner()),
        output_path=output_path,
    )

    report = WorkflowExecutor().run(workflow, context).unwrap()
    result = report.context.require("final_video")

    assert result.output_path.exists()
    assert result.scene_count == 1
