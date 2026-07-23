import pytest

from providers.video.models import VideoGenerationRequest


def test_video_request_validates_prompt(tmp_path) -> None:
    with pytest.raises(ValueError):
        VideoGenerationRequest(
            prompt=" ",
            source_image=tmp_path / "image.png",
            duration_seconds=3,
        )


def test_video_request_validates_duration(tmp_path) -> None:
    with pytest.raises(ValueError):
        VideoGenerationRequest(
            prompt="Animate product",
            source_image=tmp_path / "image.png",
            duration_seconds=0,
        )
