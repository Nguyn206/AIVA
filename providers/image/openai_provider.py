from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

from core.helpers import ensure_directory, generate_id
from core.result import Result
from providers.exceptions import (
    ProviderConfigurationError,
    ProviderRequestError,
)
from providers.image.base import BaseImageProvider
from providers.image.models import (
    GeneratedImage,
    ImageGenerationRequest,
    ImageGenerationResponse,
)


class OpenAIImageProvider(BaseImageProvider):
    """OpenAI image-generation adapter for AIVA storyboard scenes."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str = "gpt-image-1",
        client: Any = None,
    ) -> None:
        super().__init__("openai-image", default_model=default_model)
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
        request: ImageGenerationRequest,
        *,
        output_directory: str | Path,
    ) -> Result[ImageGenerationResponse]:
        readiness = self.health_check()
        if not readiness.success:
            return Result.fail(
                readiness.error or "OpenAI image provider is not ready.",
                error_type=readiness.error_type,
            )

        try:
            client = self._get_client()
            model = self.resolve_model(request)
            response = client.images.generate(
                model=model,
                prompt=request.prompt,
                size=request.size,
                quality=request.quality,
                background=request.background,
                output_format=request.output_format,
                n=request.count,
            )

            directory = ensure_directory(output_directory)
            generated: list[GeneratedImage] = []

            for index, item in enumerate(response.data, start=1):
                encoded = getattr(item, "b64_json", None)
                if not encoded:
                    raise ProviderRequestError(
                        "OpenAI image response did not contain base64 data."
                    )

                filename = (
                    f"{generate_id('scene-image')}_{index}."
                    f"{request.output_format}"
                )
                path = directory / filename
                path.write_bytes(base64.b64decode(encoded))

                generated.append(
                    GeneratedImage(
                        path=path,
                        prompt=request.prompt,
                        provider=self.name,
                        model=model,
                        revised_prompt=getattr(
                            item,
                            "revised_prompt",
                            None,
                        ),
                    )
                )

            return Result.ok(
                ImageGenerationResponse(
                    images=tuple(generated),
                    provider=self.name,
                    model=model,
                    request_id=getattr(response, "_request_id", None),
                    raw=response,
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
