
from providers.video.ffmpeg_image_provider import (
    FFmpegImageVideoProvider,
    _dimensions_for_ratio,
    _prefers_zoom_in,
)


def test_dimensions_follow_aspect_ratio() -> None:
    assert _dimensions_for_ratio("9:16") == (1080, 1920)
    assert _dimensions_for_ratio("16:9") == (1920, 1080)


def test_prompt_can_select_zoom_direction() -> None:
    assert _prefers_zoom_in("Slow cinematic push-in") is True
    assert _prefers_zoom_in("Wide static reveal") is False


def test_health_check_reports_missing_ffmpeg(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda executable: None)
    provider = FFmpegImageVideoProvider(executable="missing-ffmpeg")

    result = provider.health_check()

    assert result.success is False
    assert result.error_type == "FFmpegNotFoundError"
