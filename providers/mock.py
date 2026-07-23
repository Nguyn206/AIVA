from __future__ import annotations

from collections.abc import Callable

from core.result import Result
from providers.base import BaseLLMProvider
from providers.models import (
    LLMRequest,
    LLMResponse,
    TokenUsage,
)

MockResponseFactory = Callable[[LLMRequest], str]


class MockLLMProvider(BaseLLMProvider):
    """Deterministic provider used by tests and offline development."""

    def __init__(
        self,
        response: str | MockResponseFactory = "Mock AI response",
        *,
        name: str = "mock",
        default_model: str = "mock-model",
    ) -> None:
        super().__init__(name, default_model=default_model)
        self._response = response
        self.requests: list[LLMRequest] = []

    def generate(
        self,
        request: LLMRequest,
    ) -> Result[LLMResponse]:
        self.requests.append(request)

        try:
            text = (
                self._response(request)
                if callable(self._response)
                else self._response
            )
            model = self.resolve_model(request)
            usage = TokenUsage(
                input_tokens=len(request.prompt.split()),
                output_tokens=len(text.split()),
                total_tokens=(
                    len(request.prompt.split()) + len(text.split())
                ),
            )
            return Result.ok(
                LLMResponse(
                    text=text,
                    provider=self.name,
                    model=model,
                    request_id=f"mock-{len(self.requests)}",
                    usage=usage,
                )
            )
        except Exception as exc:
            return Result.from_exception(exc)
