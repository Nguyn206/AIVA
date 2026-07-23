from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from core.helpers import ensure_directory
from core.result import Result
from providers.audio.base import BaseVoiceProvider
from providers.audio.models import (
    GeneratedAudio,
    VoiceGenerationRequest,
    VoiceGenerationResponse,
)
from providers.exceptions import (
    ProviderConfigurationError,
    ProviderRequestError,
)


class OpenAIVoiceProvider(BaseVoiceProvider):
    """OpenAI text-to-speech adapter for AIVA narration."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str = "gpt-4o-mini-tts",
        client: Any = None,
    ) -> None:
        super().__init__("openai-voice", default_model=default_model)
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
        request: VoiceGenerationRequest,
        *,
        output_path: str | Path,
    ) -> Result[VoiceGenerationResponse]:
        readiness = self.health_check()
        if not readiness.success:
            return Result.fail(
                readiness.error or "OpenAI voice provider is not ready.",
                error_type=readiness.error_type,
            )

        destination = Path(output_path)
        ensure_directory(destination.parent)

        try:
            client = self._get_client()
            parameters: dict[str, Any] = {
                "model": self.resolve_model(request),
                "voice": request.voice,
                "input": request.text,
                "response_format": request.response_format,
                "speed": request.speed,
            }
            if request.instructions:
                parameters["instructions"] = request.instructions

            with client.audio.speech.with_streaming_response.create(
                **parameters
            ) as response:
                response.stream_to_file(destination)
                request_id = getattr(response, "_request_id", None)

            generated = GeneratedAudio(
                path=destination,
                provider=self.name,
                model=self.resolve_model(request),
                voice=request.voice,
                text=request.text,
                response_format=request.response_format,
            )
            return Result.ok(
                VoiceGenerationResponse(
                    audio=generated,
                    request_id=request_id,
                )
            )
        except Exception as exc:
            mapped = (
                exc
                if isinstance(
                    exc,
                    (
                        ProviderConfigurationError,
                        ProviderRequestError,
                    ),
                )
                else ProviderRequestError(
                    str(exc) or exc.__class__.__name__
                )
            )
            return Result.from_exception(mapped)

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
                "OpenAI SDK is not installed."
            ) from exc

        self._client = OpenAI(api_key=self.api_key)
        return self._client
