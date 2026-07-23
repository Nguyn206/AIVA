from pathlib import Path

from config.runtime import RuntimeConfig
from services.preflight import run_real_mode_preflight


def test_preflight_reports_missing_api_key(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr("shutil.which", lambda executable: executable)

    report = run_real_mode_preflight(
        RuntimeConfig(
            openai_api_key=None,
            llm_model="llm-model",
            image_model="image-model",
            voice_model="voice-model",
            voice_name="alloy",
            ffmpeg_path="ffmpeg",
            output_root=tmp_path,
        )
    )

    assert report.passed is False
    key_check = next(
        check
        for check in report.checks
        if check.name == "openai_api_key"
    )
    assert key_check.passed is False


def test_preflight_passes_with_valid_configuration(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "shutil.which",
        lambda executable: str(Path(tmp_path) / executable),
    )

    report = run_real_mode_preflight(
        RuntimeConfig(
            openai_api_key="test-key",
            llm_model="llm-model",
            image_model="image-model",
            voice_model="voice-model",
            voice_name="alloy",
            ffmpeg_path="ffmpeg",
            output_root=tmp_path,
        )
    )

    assert report.passed is True
