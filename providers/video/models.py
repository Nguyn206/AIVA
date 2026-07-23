from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class VideoGenerationRequest:
    prompt: str
    source_image: Path
    duration_seconds: float
    model: str | None = None
    aspect_ratio: str = "9:16"
    fps: int = 24
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise ValueError("Video prompt must not be empty.")
        if self.duration_seconds <= 0:
            raise ValueError("Video duration must be greater than zero.")
        if self.fps <= 0:
            raise ValueError("Video FPS must be greater than zero.")
        if not self.aspect_ratio.strip():
            raise ValueError("Video aspect ratio must not be empty.")


@dataclass(frozen=True, slots=True)
class GeneratedVideo:
    path: Path
    prompt: str
    provider: str
    model: str
    duration_seconds: float
    source_image: Path
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise ValueError("Generated video prompt must not be empty.")
        if not self.provider.strip():
            raise ValueError("Video provider name must not be empty.")
        if not self.model.strip():
            raise ValueError("Video model name must not be empty.")
        if self.duration_seconds <= 0:
            raise ValueError("Generated video duration must be positive.")


@dataclass(frozen=True, slots=True)
class VideoGenerationResponse:
    video: GeneratedVideo
    request_id: str | None = None
    raw: Any = None
