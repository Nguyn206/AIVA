from __future__ import annotations

import wave
from pathlib import Path

from core.helpers import ensure_directory
from core.result import Result
from providers.audio.base import BaseVoiceProvider
from providers.audio.models import (
    GeneratedAudio,
    VoiceGenerationRequest,
    VoiceGenerationResponse,
)


class MockVoiceProvider(BaseVoiceProvider):
    """Offline provider that creates a valid silent WAV test file."""

    def __init__(
        self,
        *,
        name: str = "mock-voice",
        default_model: str = "mock-voice-model",
    ) -> None:
        super().__init__(name, default_model=default_model)
        self.requests: list[VoiceGenerationRequest] = []

    def generate(
        self,
        request: VoiceGenerationRequest,
        *,
        output_path: str | Path,
    ) -> Result[VoiceGenerationResponse]:
        self.requests.append(request)
        destination = Path(output_path)
        ensure_directory(destination.parent)

        try:
            with wave.open(str(destination), "wb") as audio_file:
                audio_file.setnchannels(1)
                audio_file.setsampwidth(2)
                audio_file.setframerate(16000)
                audio_file.writeframes(b"\x00\x00" * 1600)

            generated = GeneratedAudio(
                path=destination,
                provider=self.name,
                model=self.resolve_model(request),
                voice=request.voice,
                text=request.text,
                response_format="wav",
                metadata={"mock": True},
            )
            return Result.ok(
                VoiceGenerationResponse(
                    audio=generated,
                    request_id=f"mock-voice-{len(self.requests)}",
                )
            )
        except Exception as exc:
            return Result.from_exception(exc)
