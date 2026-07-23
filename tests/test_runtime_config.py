import pytest

from config.runtime import RuntimeConfig


def test_runtime_config_reads_defaults(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = RuntimeConfig.from_env("missing.env")

    assert config.llm_model == "gpt-5"
    assert config.image_model == "gpt-image-1"
    assert config.voice_model == "gpt-4o-mini-tts"


def test_real_mode_requires_api_key() -> None:
    config = RuntimeConfig(
        openai_api_key=None,
        llm_model="gpt-5",
        image_model="gpt-image-1",
        voice_model="gpt-4o-mini-tts",
        voice_name="alloy",
        ffmpeg_path="ffmpeg",
        output_root=__import__("pathlib").Path("output"),
    )

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        config.validate_real_mode()
