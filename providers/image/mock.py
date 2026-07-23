from __future__ import annotations

import base64
from pathlib import Path

from core.helpers import ensure_directory, generate_id
from core.result import Result
from providers.image.base import BaseImageProvider
from providers.image.models import (
    GeneratedImage,
    ImageGenerationRequest,
    ImageGenerationResponse,
)

_ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC"
    "AAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class MockImageProvider(BaseImageProvider):
    """Offline image provider for tests and local development."""

    def __init__(
        self,
        *,
        name: str = "mock-image",
        default_model: str = "mock-image-model",
    ) -> None:
        super().__init__(name, default_model=default_model)
        self.requests: list[ImageGenerationRequest] = []

    def generate(
        self,
        request: ImageGenerationRequest,
        *,
        output_directory: str | Path,
    ) -> Result[ImageGenerationResponse]:
        self.requests.append(request)
        directory = ensure_directory(output_directory)
        model = self.resolve_model(request)
        images: list[GeneratedImage] = []

        try:
            for index in range(request.count):
                filename = (
                    f"{generate_id('image')}_{index + 1}."
                    f"{request.output_format}"
                )
                path = directory / filename
                path.write_bytes(_ONE_PIXEL_PNG)

                images.append(
                    GeneratedImage(
                        path=path,
                        prompt=request.prompt,
                        provider=self.name,
                        model=model,
                        metadata={"mock": True},
                    )
                )

            return Result.ok(
                ImageGenerationResponse(
                    images=tuple(images),
                    provider=self.name,
                    model=model,
                    request_id=f"mock-image-{len(self.requests)}",
                )
            )
        except Exception as exc:
            return Result.from_exception(exc)
