from __future__ import annotations

from config.runtime import RuntimeConfig
from pipelines.full_auto_video import (
    FullAutoVideoConfig,
    FullAutoVideoPipeline,
)
from providers.audio.openai_provider import OpenAIVoiceProvider
from providers.image.openai_provider import OpenAIImageProvider
from providers.openai_provider import OpenAIProvider
from providers.video.ffmpeg_image_provider import (
    FFmpegImageVideoProvider,
)
from render.engine import RenderEngine
from render.ffmpeg import FFmpegRunner


def build_real_pipeline(
    runtime: RuntimeConfig,
) -> FullAutoVideoPipeline:
    """Build an end-to-end pipeline using real OpenAI and FFmpeg providers."""
    runtime.validate_real_mode()

    return FullAutoVideoPipeline(
        llm_provider=OpenAIProvider(
            api_key=runtime.openai_api_key,
            default_model=runtime.llm_model,
        ),
        image_provider=OpenAIImageProvider(
            api_key=runtime.openai_api_key,
            default_model=runtime.image_model,
        ),
        video_provider=FFmpegImageVideoProvider(
            executable=runtime.ffmpeg_path,
        ),
        voice_provider=OpenAIVoiceProvider(
            api_key=runtime.openai_api_key,
            default_model=runtime.voice_model,
        ),
        render_engine=RenderEngine(
            FFmpegRunner(runtime.ffmpeg_path)
        ),
        config=FullAutoVideoConfig(
            output_root=runtime.output_root,
            voice=runtime.voice_name,
            voice_format="mp3",
        ),
    )
