from pathlib import Path

from config.runtime import RuntimeConfig
from services.runtime_factory import build_real_pipeline


def test_factory_builds_real_pipeline() -> None:
    runtime = RuntimeConfig(
        openai_api_key="test-key",
        llm_model="gpt-5",
        image_model="gpt-image-1",
        voice_model="gpt-4o-mini-tts",
        voice_name="alloy",
        ffmpeg_path="ffmpeg",
        output_root=Path("output"),
    )

    pipeline = build_real_pipeline(runtime)

    assert pipeline.llm_provider.name == "openai"
    assert pipeline.image_provider.name == "openai-image"
    assert pipeline.video_provider.name == "ffmpeg-image-video"
    assert pipeline.voice_provider.name == "openai-voice"
