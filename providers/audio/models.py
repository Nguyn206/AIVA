from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class VoiceGenerationRequest:
    text: str
    voice: str = "alloy"
    model: str | None = None
    instructions: str | None = None
    response_format: str = "mp3"
    speed: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Voice text must not be empty.")
        if not self.voice.strip():
            raise ValueError("Voice name must not be empty.")
        if self.response_format not in {
            "mp3",
            "opus",
            "aac",
            "flac",
            "wav",
            "pcm",
        }:
            raise ValueError("Unsupported voice response format.")
        if not 0.25 <= self.speed <= 4.0:
            raise ValueError("Voice speed must be between 0.25 and 4.0.")


@dataclass(frozen=True, slots=True)
class GeneratedAudio:
    path: Path
    provider: str
    model: str
    voice: str
    text: str
    response_format: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("Audio provider name must not be empty.")
        if not self.model.strip():
            raise ValueError("Audio model name must not be empty.")
        if not self.voice.strip():
            raise ValueError("Audio voice name must not be empty.")
        if not self.text.strip():
            raise ValueError("Generated audio text must not be empty.")


@dataclass(frozen=True, slots=True)
class VoiceGenerationResponse:
    audio: GeneratedAudio
    request_id: str | None = None
    raw: Any = None
