from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class SceneRenderInput:
    scene_number: int
    video_path: Path
    audio_path: Path | None = None

    def __post_init__(self) -> None:
        if self.scene_number <= 0:
            raise ValueError("Scene number must be greater than zero.")


@dataclass(frozen=True, slots=True)
class RenderRequest:
    scenes: tuple[SceneRenderInput, ...]
    output_path: Path
    subtitle_path: Path | None = None
    width: int = 1080
    height: int = 1920
    fps: int = 30
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    preset: str = "medium"
    crf: int = 20
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.scenes:
            raise ValueError("Render request must contain at least one scene.")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Render dimensions must be positive.")
        if self.fps <= 0:
            raise ValueError("Render FPS must be greater than zero.")
        if not 0 <= self.crf <= 51:
            raise ValueError("CRF must be between 0 and 51.")


@dataclass(frozen=True, slots=True)
class RenderResult:
    output_path: Path
    scene_count: int
    subtitle_burned: bool
    command: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.scene_count <= 0:
            raise ValueError("Rendered scene count must be positive.")
