from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ImageGenerationRequest:
    prompt: str
    model: str | None = None
    size: str = "1024x1024"
    quality: str = "auto"
    background: str = "auto"
    output_format: str = "png"
    count: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise ValueError("Image prompt must not be empty.")
        if self.count <= 0:
            raise ValueError("Image count must be greater than zero.")
        if not self.size.strip():
            raise ValueError("Image size must not be empty.")
        if self.output_format not in {"png", "jpeg", "webp"}:
            raise ValueError(
                "Image output format must be png, jpeg, or webp."
            )


@dataclass(frozen=True, slots=True)
class GeneratedImage:
    path: Path
    prompt: str
    provider: str
    model: str
    revised_prompt: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise ValueError("Generated image prompt must not be empty.")
        if not self.provider.strip():
            raise ValueError("Image provider name must not be empty.")
        if not self.model.strip():
            raise ValueError("Image model name must not be empty.")


@dataclass(frozen=True, slots=True)
class ImageGenerationResponse:
    images: tuple[GeneratedImage, ...]
    provider: str
    model: str
    request_id: str | None = None
    raw: Any = None

    def __post_init__(self) -> None:
        if not self.images:
            raise ValueError(
                "Image generation response must contain images."
            )
