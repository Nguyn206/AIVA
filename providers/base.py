from __future__ import annotations

from abc import ABC, abstractmethod

from core.result import Result
from providers.models import LLMRequest, LLMResponse


class BaseLLMProvider(ABC):
    """Common interface for every text-generation provider used by AIVA."""

    def __init__(
        self,
        name: str,
        *,
        default_model: str,
    ) -> None:
        normalized_name = name.strip().lower()
        normalized_model = default_model.strip()

        if not normalized_name:
            raise ValueError("Provider name must not be empty.")
        if not normalized_model:
            raise ValueError("Default model must not be empty.")

        self.name = normalized_name
        self.default_model = normalized_model

    @abstractmethod
    def generate(
        self,
        request: LLMRequest,
    ) -> Result[LLMResponse]:
        """Generate a text response for an AIVA video-production step."""

    def health_check(self) -> Result[bool]:
        """Return whether the provider is ready for requests."""
        return Result.ok(True)

    def resolve_model(self, request: LLMRequest) -> str:
        return request.model or self.default_model

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, default_model={self.default_model!r})"
        )
