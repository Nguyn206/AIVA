from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.result import Result
from providers.video.models import (
    VideoGenerationRequest,
    VideoGenerationResponse,
)


class BaseVideoProvider(ABC):
    """Common interface for image-to-video providers used by AIVA."""

    def __init__(
        self,
        name: str,
        *,
        default_model: str,
    ) -> None:
        normalized_name = name.strip().lower()
        normalized_model = default_model.strip()

        if not normalized_name:
            raise ValueError("Video provider name must not be empty.")
        if not normalized_model:
            raise ValueError("Default video model must not be empty.")

        self.name = normalized_name
        self.default_model = normalized_model

    @abstractmethod
    def generate(
        self,
        request: VideoGenerationRequest,
        *,
        output_path: str | Path,
    ) -> Result[VideoGenerationResponse]:
        """Generate a scene clip and save it to disk."""

    def health_check(self) -> Result[bool]:
        return Result.ok(True)

    def resolve_model(
        self,
        request: VideoGenerationRequest,
    ) -> str:
        return request.model or self.default_model
