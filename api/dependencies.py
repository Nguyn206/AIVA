from __future__ import annotations

from pathlib import Path

from config.runtime import RuntimeConfig
from pipelines.resumable_video import ResumableVideoPipeline
from services.resumable_runtime_factory import (
    build_resumable_mock_pipeline,
    build_resumable_real_pipeline,
)


def build_pipeline(
    mode: str,
    *,
    output_root: str | Path,
) -> ResumableVideoPipeline:
    root = Path(output_root)

    if mode == "mock":
        return build_resumable_mock_pipeline(root)

    runtime = RuntimeConfig.from_env()
    runtime = RuntimeConfig(
        openai_api_key=runtime.openai_api_key,
        llm_model=runtime.llm_model,
        image_model=runtime.image_model,
        voice_model=runtime.voice_model,
        voice_name=runtime.voice_name,
        ffmpeg_path=runtime.ffmpeg_path,
        output_root=root,
    )
    return build_resumable_real_pipeline(runtime)
