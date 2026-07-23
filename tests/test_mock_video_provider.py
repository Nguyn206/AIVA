from providers.video.mock import MockVideoProvider
from providers.video.models import VideoGenerationRequest


def test_mock_video_provider_creates_clip(tmp_path) -> None:
    source_image = tmp_path / "source.png"
    source_image.write_bytes(b"image")
    output_path = tmp_path / "clip.mp4"
    provider = MockVideoProvider()

    result = provider.generate(
        VideoGenerationRequest(
            prompt="Slow cinematic push-in",
            source_image=source_image,
            duration_seconds=4,
        ),
        output_path=output_path,
    )

    response = result.unwrap()
    assert response.video.path.exists()
    assert response.video.duration_seconds == 4
    assert len(provider.requests) == 1
