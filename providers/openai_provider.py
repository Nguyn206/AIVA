from __future__ import annotations

import os
from typing import Any

from core.result import Result
from providers.base import BaseLLMProvider
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderRequestError,
)
from providers.models import (
    LLMRequest,
    LLMResponse,
    TokenUsage,
)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Responses API adapter for AIVA text-generation tasks."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str = "gpt-5.5",
        client: Any = None,
    ) -> None:
        super().__init__("openai", default_model=default_model)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._client = client

    def health_check(self) -> Result[bool]:
        if self._client is not None:
            return Result.ok(True)
        if not self.api_key:
            return Result.fail(
                "OPENAI_API_KEY is not configured.",
                error_type="ProviderConfigurationError",
            )
        return Result.ok(True)

    def generate(
        self,
        request: LLMRequest,
    ) -> Result[LLMResponse]:
        readiness = self.health_check()
        if not readiness.success:
            return Result.fail(
                readiness.error or "OpenAI provider is not ready.",
                error_type=readiness.error_type,
            )

        try:
            client = self._get_client()
            parameters: dict[str, Any] = {
                "model": self.resolve_model(request),
                "input": request.prompt,
            }

            if request.system_instruction:
                parameters["instructions"] = request.system_instruction
            if request.max_output_tokens is not None:
                parameters["max_output_tokens"] = (
                    request.max_output_tokens
                )
            if request.temperature is not None:
                parameters["temperature"] = request.temperature

            response = client.responses.create(**parameters)
            text = _extract_output_text(response)

            if not text.strip():
                raise ProviderRequestError(
                    "OpenAI returned an empty text response."
                )

            return Result.ok(
                LLMResponse(
                    text=text,
                    provider=self.name,
                    model=getattr(
                        response,
                        "model",
                        self.resolve_model(request),
                    ),
                    request_id=getattr(
                        response,
                        "_request_id",
                        None,
                    ),
                    usage=_extract_usage(response),
                    raw=response,
                )
            )
        except ProviderRequestError as exc:
            return Result.from_exception(exc)
        except Exception as exc:
            return self._map_exception(exc)

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        if not self.api_key:
            raise ProviderConfigurationError(
                "OPENAI_API_KEY is not configured."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderConfigurationError(
                "OpenAI SDK is not installed. "
                "Run: pip install openai"
            ) from exc

        self._client = OpenAI(api_key=self.api_key)
        return self._client

    @staticmethod
    def _map_exception(exc: Exception) -> Result[LLMResponse]:
        name = exc.__class__.__name__

        if name in {"AuthenticationError", "PermissionDeniedError"}:
            mapped = ProviderAuthenticationError(str(exc))
        elif name in {
            "APIConnectionError",
            "APITimeoutError",
            "BadRequestError",
            "RateLimitError",
            "APIStatusError",
        }:
            mapped = ProviderRequestError(str(exc))
        else:
            mapped = ProviderRequestError(
                str(exc) or exc.__class__.__name__
            )

        return Result.from_exception(mapped)


def _extract_output_text(response: Any) -> str:
    direct_text = getattr(response, "output_text", None)
    if isinstance(direct_text, str):
        return direct_text

    collected: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if isinstance(text, str) and text:
                collected.append(text)

    return "\n".join(collected)


def _extract_usage(response: Any) -> TokenUsage:
    usage = getattr(response, "usage", None)
    if usage is None:
        return TokenUsage()

    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
    total_tokens = int(
        getattr(
            usage,
            "total_tokens",
            input_tokens + output_tokens,
        )
        or 0
    )

    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
    )
