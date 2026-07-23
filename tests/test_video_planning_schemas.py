import pytest

from schemas.video_planning import (
    ProductInput,
    Storyboard,
    VideoScript,
)


def test_product_input_builds_prompt_text() -> None:
    product = ProductInput(
        name="Smart Camera",
        description="AI security camera",
        target_market="Home owners",
        features=("Night vision", "Motion detection"),
    )

    text = product.to_prompt_text()

    assert "Smart Camera" in text
    assert "Night vision" in text


def test_video_script_requires_all_fields() -> None:
    with pytest.raises(ValueError, match="missing"):
        VideoScript.from_dict({"title": "Incomplete"})


def test_storyboard_calculates_total_duration() -> None:
    storyboard = Storyboard.from_dict(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 3,
                    "narration": "Hook",
                    "visual_description": "Product close-up",
                    "image_prompt": "Image prompt",
                    "video_prompt": "Video prompt",
                },
                {
                    "scene_number": 2,
                    "duration_seconds": 5,
                    "narration": "Benefit",
                    "visual_description": "Product in use",
                    "image_prompt": "Second image prompt",
                    "video_prompt": "Second video prompt",
                },
            ]
        }
    )

    assert storyboard.total_duration_seconds == 8
