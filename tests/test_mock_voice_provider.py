from providers.audio.mock import MockVoiceProvider
from providers.audio.models import VoiceGenerationRequest


def test_mock_voice_provider_creates_audio_file(tmp_path) -> None:
    provider = MockVoiceProvider()
    output_path = tmp_path / "voice.wav"

    result = provider.generate(
        VoiceGenerationRequest(
            text="This is the narration.",
            response_format="wav",
        ),
        output_path=output_path,
    )

    response = result.unwrap()
    assert response.audio.path.exists()
    assert response.audio.path.stat().st_size > 0
    assert len(provider.requests) == 1
