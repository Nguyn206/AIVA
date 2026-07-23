import json

from pipelines.full_auto_video import (
    FullAutoVideoConfig,
    FullAutoVideoPipeline,
)
from providers.audio.mock import MockVoiceProvider
from providers.image.mock import MockImageProvider
from providers.mock import MockLLMProvider
from providers.video.mock import MockVideoProvider
from render.engine import RenderEngine
from render.ffmpeg import MockFFmpegRunner
from schemas.video_planning import ProductInput


def response_factory(request):
    if "product analysis AI" in request.prompt:
        return json.dumps(
            {
                "product_name": "Smart Lamp",
                "category": "Home",
                "primary_problem": "Poor lighting",
                "unique_selling_points": ["Adaptive brightness"],
                "customer_benefits": ["Better comfort"],
                "emotional_benefits": ["Relaxation"],
                "target_audience": ["Home workers"],
                "objections": ["Price"],
                "proof_points": ["Energy efficient"],
                "recommended_video_angle": "Transform your workspace",
            }
        )

    if "advertising script writer" in request.prompt:
        return json.dumps(
            {
                "title": "Better Light",
                "hook": "Your workspace is tiring your eyes.",
                "scenes": [{"scene": 1}, {"scene": 2}],
                "narration": "Upgrade your workspace lighting.",
                "call_to_action": "Try the smart lamp today.",
            }
        )

    return json.dumps(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 3,
                    "narration": "Your workspace is tiring your eyes.",
                    "visual_description": "Dark desk",
                    "image_prompt": "Dark desk with poor lighting",
                    "video_prompt": "Slow push toward dark desk",
                },
                {
                    "scene_number": 2,
                    "duration_seconds": 4,
                    "narration": "Upgrade your workspace lighting.",
                    "visual_description": "Smart lamp illuminating desk",
                    "image_prompt": "Smart lamp on modern desk",
                    "video_prompt": "Smooth reveal of smart lamp",
                },
            ]
        }
    )


def test_full_auto_pipeline_creates_final_video(tmp_path) -> None:
    pipeline = FullAutoVideoPipeline(
        llm_provider=MockLLMProvider(
            response=response_factory
        ),
        image_provider=MockImageProvider(),
        video_provider=MockVideoProvider(),
        voice_provider=MockVoiceProvider(),
        render_engine=RenderEngine(MockFFmpegRunner()),
        config=FullAutoVideoConfig(
            output_root=tmp_path,
            voice_format="wav",
        ),
    )

    result = pipeline.run(
        ProductInput(
            name="Smart Lamp",
            description="Adaptive desk lamp",
            target_market="Home workers",
        ),
        project_id="test-project",
    )

    output = result.unwrap()
    assert output.final_video_path.exists()
    assert output.project_directory == tmp_path / "test-project"
    assert output.context.exists("product_analysis")
    assert output.context.exists("video_script")
    assert output.context.exists("storyboard")
    assert output.context.exists("scene_images")
    assert output.context.exists("scene_videos")
    assert output.context.exists("scene_narration_audio")
    assert output.context.exists("subtitle_asset")
    assert output.context.exists("final_video")
