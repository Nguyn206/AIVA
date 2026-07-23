from __future__ import annotations

from pathlib import Path

from core.helpers import ensure_directory
from core.result import Result
from providers.video.base import BaseVideoProvider
from providers.video.models import (
    GeneratedVideo,
    VideoGenerationRequest,
    VideoGenerationResponse,
)


class MockVideoProvider(BaseVideoProvider):
    """Offline provider that creates a deterministic placeholder clip."""

    def __init__(
        self,
        *,
        name: str = "mock-video",
        default_model: str = "mock-video-model",
    ) -> None:
        super().__init__(name, default_model=default_model)
        self.requests: list[VideoGenerationRequest] = []

    def generate(
        self,
        request: VideoGenerationRequest,
        *,
        output_path: str | Path,
    ) -> Result[VideoGenerationResponse]:
        self.requests.append(request)
        destination = Path(output_path)
        ensure_directory(destination.parent)

        try:
            destination.write_bytes(
                (
                    "AIVA_MOCK_VIDEO\n"
                    f"prompt={request.prompt}\n"
                    f"duration={request.duration_seconds}\n"
                    f"source_image={request.source_image}\n"
                ).encode()
            )

            video = GeneratedVideo(
                path=destination,
                prompt=request.prompt,
                provider=self.name,
                model=self.resolve_model(request),
                duration_seconds=request.duration_seconds,
                source_image=request.source_image,
                metadata={"mock": True},
            )
            return Result.ok(
                VideoGenerationResponse(
                    video=video,
                    request_id=f"mock-video-{len(self.requests)}",
                )
            )
        except Exception as exc:
            return Result.from_exception(exc)
