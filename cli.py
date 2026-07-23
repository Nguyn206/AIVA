from __future__ import annotations

import argparse
import json
from pathlib import Path

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aiva",
        description=(
            "AIVA - fully automated AI video generation pipeline."
        ),
    )
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--target-market", required=True)
    parser.add_argument("--product-url")
    parser.add_argument(
        "--feature",
        action="append",
        default=[],
        help="Repeat this option for multiple product features.",
    )
    parser.add_argument(
        "--output-root",
        default="output",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run entirely offline using deterministic mock providers.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.mock:
        raise SystemExit(
            "Real provider mode is not configured by this CLI yet. "
            "Run with --mock."
        )

    llm_provider = MockLLMProvider(
        response=_mock_response_factory
    )
    pipeline = FullAutoVideoPipeline(
        llm_provider=llm_provider,
        image_provider=MockImageProvider(),
        video_provider=MockVideoProvider(),
        voice_provider=MockVoiceProvider(),
        render_engine=RenderEngine(MockFFmpegRunner()),
        config=FullAutoVideoConfig(
            output_root=Path(args.output_root),
            voice_format="wav",
        ),
    )

    result = pipeline.run(
        ProductInput(
            name=args.name,
            description=args.description,
            target_market=args.target_market,
            product_url=args.product_url,
            features=tuple(args.feature),
        )
    )

    if not result.success:
        print(f"AIVA failed: {result.error}")
        return 1

    output = result.unwrap()
    print(f"Project: {output.project_id}")
    print(f"Final video: {output.final_video_path}")
    return 0


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
                "scenes": [
                    {"scene": 1, "purpose": "hook"},
                    {"scene": 2, "purpose": "benefit"},
                ],
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


if __name__ == "__main__":
    raise SystemExit(main())
