from __future__ import annotations

import json
from pathlib import Path

from config.runtime import RuntimeConfig
from pipelines.full_auto_video import FullAutoVideoConfig
from pipelines.resumable_video import ResumableVideoPipeline
from providers.audio.mock import MockVoiceProvider
from providers.audio.openai_provider import OpenAIVoiceProvider
from providers.image.mock import MockImageProvider
from providers.image.openai_provider import OpenAIImageProvider
from providers.mock import MockLLMProvider
from providers.openai_provider import OpenAIProvider
from providers.video.ffmpeg_image_provider import (
    FFmpegImageVideoProvider,
)
from providers.video.mock import MockVideoProvider
from render.engine import RenderEngine
from render.ffmpeg import FFmpegRunner, MockFFmpegRunner


def build_resumable_real_pipeline(
    runtime: RuntimeConfig,
) -> ResumableVideoPipeline:
    runtime.validate_real_mode()

    return ResumableVideoPipeline(
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


def build_resumable_mock_pipeline(
    output_root: str | Path,
) -> ResumableVideoPipeline:
    return ResumableVideoPipeline(
        llm_provider=MockLLMProvider(
            response=_mock_response_factory
        ),
        image_provider=MockImageProvider(),
        video_provider=MockVideoProvider(),
        voice_provider=MockVoiceProvider(),
        render_engine=RenderEngine(MockFFmpegRunner()),
        config=FullAutoVideoConfig(
            output_root=Path(output_root),
            voice_format="wav",
        ),
    )


def _mock_response_factory(request) -> str:
    if "product analysis AI" in request.prompt:
        return json.dumps(
            {
                "product_name": "Demo product",
                "category": "Demo",
                "primary_problem": "Customer problem",
                "unique_selling_points": ["AI-generated benefit"],
                "customer_benefits": ["Useful result"],
                "emotional_benefits": ["Confidence"],
                "target_audience": ["Target customer"],
                "objections": ["Price"],
                "proof_points": ["Feature"],
                "recommended_video_angle": "Problem to solution",
            }
        )

    if "advertising script writer" in request.prompt:
        return json.dumps(
            {
                "title": "AI Product Video",
                "hook": "Stop scrolling.",
                "scenes": [{"scene": 1}, {"scene": 2}],
                "narration": "This product solves your problem.",
                "call_to_action": "Try it today.",
            }
        )

    return json.dumps(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 3,
                    "narration": "Stop scrolling.",
                    "visual_description": "Product hero shot",
                    "image_prompt": "Cinematic product hero image",
                    "video_prompt": "Slow cinematic push-in",
                    "on_screen_text": "Stop scrolling",
                    "transition": "cut",
                },
                {
                    "scene_number": 2,
                    "duration_seconds": 4,
                    "narration": "This product solves your problem.",
                    "visual_description": "Product in use",
                    "image_prompt": "Product being used naturally",
                    "video_prompt": "Smooth tracking movement",
                    "on_screen_text": "The solution",
                    "transition": "fade",
                },
            ]
        }
    )
