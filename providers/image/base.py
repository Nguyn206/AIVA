from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.result import Result
from providers.image.models import (
    ImageGenerationRequest,
    ImageGenerationResponse,
)


class BaseImageProvider(ABC):
    """Common interface for image generators used by AIVA."""

    def __init__(
        self,
        name: str,
        *,
        default_model: str,
    ) -> None:
        normalized_name = name.strip().lower()
        normalized_model = default_model.strip()

        if not normalized_name:
            raise ValueError("Image provider name must not be empty.")
        if not normalized_model:
            raise ValueError("Default image model must not be empty.")

        self.name = normalized_name
        self.default_model = normalized_model

    @abstractmethod
    def generate(
        self,
        request: ImageGenerationRequest,
        *,
        output_directory: str | Path,
    ) -> Result[ImageGenerationResponse]:
        """Generate image files and return their saved paths."""

    def health_check(self) -> Result[bool]:
        return Result.ok(True)

    def resolve_model(
        self,
        request: ImageGenerationRequest,
    ) -> str:
        return request.model or self.default_model
