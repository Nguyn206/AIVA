from pathlib import Path

from providers.audio.models import VoiceGenerationRequest
from providers.audio.openai_provider import OpenAIVoiceProvider


class FakeStreamingResponse:
    _request_id = "voice-request-123"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def stream_to_file(self, path: Path) -> None:
        Path(path).write_bytes(b"fake-audio-data")


class FakeCreate:
    def __init__(self) -> None:
        self.parameters = None

    def create(self, **parameters):
        self.parameters = parameters
        return FakeStreamingResponse()


class FakeSpeech:
    def __init__(self) -> None:
        self.with_streaming_response = FakeCreate()


class FakeAudio:
    def __init__(self) -> None:
        self.speech = FakeSpeech()


class FakeClient:
    def __init__(self) -> None:
        self.audio = FakeAudio()


def test_openai_voice_provider_saves_audio(tmp_path) -> None:
    client = FakeClient()
    provider = OpenAIVoiceProvider(
        client=client,
        default_model="test-tts-model",
    )
    output_path = tmp_path / "speech.mp3"

    result = provider.generate(
        VoiceGenerationRequest(
            text="Create this narration.",
            voice="alloy",
            instructions="Warm and persuasive.",
        ),
        output_path=output_path,
    )

    response = result.unwrap()
    assert output_path.read_bytes() == b"fake-audio-data"
    assert response.request_id == "voice-request-123"
    assert client.audio.speech.with_streaming_response.parameters[
        "model"
    ] == "test-tts-model"
