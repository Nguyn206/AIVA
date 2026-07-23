import pytest

from providers.audio.models import VoiceGenerationRequest


def test_voice_request_validates_text() -> None:
    with pytest.raises(ValueError):
        VoiceGenerationRequest(text=" ")


def test_voice_request_validates_speed() -> None:
    with pytest.raises(ValueError):
        VoiceGenerationRequest(text="Narration", speed=5.0)


def test_voice_request_validates_format() -> None:
    with pytest.raises(ValueError):
        VoiceGenerationRequest(
            text="Narration",
            response_format="avi",
        )
