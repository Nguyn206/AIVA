from pathlib import Path

from config.runtime import RuntimeConfig
from services.resumable_runtime_factory import (
    build_resumable_mock_pipeline,
    build_resumable_real_pipeline,
)


def test_mock_factory_builds_resumable_pipeline(tmp_path) -> None:
    pipeline = build_resumable_mock_pipeline(tmp_path)

    assert pipeline.config.output_root == tmp_path


def test_real_factory_builds_resumable_pipeline() -> None:
    runtime = RuntimeConfig(
        openai_api_key="test-key",
        llm_model="gpt-5",
        image_model="gpt-image-1",
        voice_model="gpt-4o-mini-tts",
        voice_name="alloy",
        ffmpeg_path="ffmpeg",
        output_root=Path("output"),
    )

    pipeline = build_resumable_real_pipeline(runtime)

    assert pipeline.llm_provider.name == "openai"
    assert pipeline.video_provider.name == "ffmpeg-image-video"
