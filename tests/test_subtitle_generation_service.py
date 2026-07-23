from schemas.video_planning import Storyboard
from services.subtitle_generation import (
    StoryboardSubtitleGenerator,
    render_srt,
    render_vtt,
)


def test_subtitle_generator_creates_srt_and_vtt(tmp_path) -> None:
    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 2.5,
                    "narration": "Stop scrolling.",
                    "visual_description": "Product close-up",
                    "image_prompt": "Image prompt one",
                    "video_prompt": "Video prompt one",
                },
                {
                    "scene_number": 2,
                    "duration_seconds": 3.5,
                    "narration": "This solves the problem.",
                    "visual_description": "Product in use",
                    "image_prompt": "Image prompt two",
                    "video_prompt": "Video prompt two",
                },
            ]
        }
    )

    result = StoryboardSubtitleGenerator(
        output_directory=tmp_path
    ).generate(storyboard)

    asset = result.unwrap()
    assert asset.srt_path.exists()
    assert asset.vtt_path.exists()
    assert "00:00:00,000 --> 00:00:02,500" in (
        asset.srt_path.read_text(encoding="utf-8")
    )
    assert "WEBVTT" in asset.vtt_path.read_text(encoding="utf-8")


def test_renderers_produce_expected_formats(tmp_path) -> None:
    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 1,
                    "narration": "Hello",
                    "visual_description": "Scene",
                    "image_prompt": "Image",
                    "video_prompt": "Video",
                }
            ]
        }
    )
    asset = StoryboardSubtitleGenerator(
        output_directory=tmp_path
    ).generate(storyboard).unwrap()

    assert render_srt(asset.track).startswith("1\n")
    assert render_vtt(asset.track).startswith("WEBVTT")
