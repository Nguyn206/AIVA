import json

from pipelines.full_auto_video import FullAutoVideoConfig
from pipelines.resumable_video import ResumableVideoPipeline
from providers.audio.mock import MockVoiceProvider
from providers.image.mock import MockImageProvider
from providers.mock import MockLLMProvider
from providers.video.mock import MockVideoProvider
from render.engine import RenderEngine
from render.ffmpeg import MockFFmpegRunner
from schemas.video_planning import ProductInput
from storage.checkpoints import CheckpointStore, PipelineStage


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
                "recommended_video_angle": "Better workspace",
            }
        )
    if "advertising script writer" in request.prompt:
        return json.dumps(
            {
                "title": "Better Light",
                "hook": "Your eyes deserve better.",
                "scenes": [{"scene": 1}],
                "narration": "Upgrade your workspace.",
                "call_to_action": "Try it today.",
            }
        )
    return json.dumps(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 2,
                    "narration": "Upgrade your workspace.",
                    "visual_description": "Lamp on desk",
                    "image_prompt": "Smart lamp product image",
                    "video_prompt": "Slow cinematic push-in",
                }
            ]
        }
    )


def test_resumable_pipeline_writes_checkpoint(tmp_path) -> None:
    pipeline = ResumableVideoPipeline(
        llm_provider=MockLLMProvider(response=response_factory),
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
            description="Adaptive lamp",
            target_market="Home workers",
        ),
        project_id="resume-test",
    )

    output = result.unwrap()
    store = CheckpointStore(output.project_directory)

    assert output.final_video_path.exists()
    assert store.reached(PipelineStage.RENDERED) is True
    assert (output.project_directory / "context.json").exists()
