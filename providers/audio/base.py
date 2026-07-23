from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.result import Result
from providers.audio.models import (
    VoiceGenerationRequest,
    VoiceGenerationResponse,
)


class BaseVoiceProvider(ABC):
    """Common interface for narration providers used by AIVA."""

    def __init__(
        self,
        name: str,
        *,
        default_model: str,
    ) -> None:
        normalized_name = name.strip().lower()
        normalized_model = default_model.strip()

        if not normalized_name:
            raise ValueError("Voice provider name must not be empty.")
        if not normalized_model:
            raise ValueError("Default voice model must not be empty.")

        self.name = normalized_name
        self.default_model = normalized_model

    @abstractmethod
    def generate(
        self,
        request: VoiceGenerationRequest,
        *,
        output_path: str | Path,
    ) -> Result[VoiceGenerationResponse]:
        """Generate narration audio and save it to disk."""

    def health_check(self) -> Result[bool]:
        return Result.ok(True)

    def resolve_model(
        self,
        request: VoiceGenerationRequest,
    ) -> str:
        return request.model or self.default_model
