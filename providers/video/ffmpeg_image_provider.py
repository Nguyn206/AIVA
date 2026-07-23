from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from core.helpers import ensure_directory
from core.result import Result
from providers.video.base import BaseVideoProvider
from providers.video.models import (
    GeneratedVideo,
    VideoGenerationRequest,
    VideoGenerationResponse,
)


class FFmpegImageVideoProvider(BaseVideoProvider):
    """Create real MP4 clips by animating AI-generated still images."""

    def __init__(
        self,
        *,
        executable: str = "ffmpeg",
        default_model: str = "ffmpeg-ken-burns",
    ) -> None:
        super().__init__("ffmpeg-image-video", default_model=default_model)
        self.executable = executable

    def health_check(self) -> Result[bool]:
        if shutil.which(self.executable) is None:
            return Result.fail(
                f"FFmpeg executable was not found: {self.executable}",
                error_type="FFmpegNotFoundError",
            )
        return Result.ok(True)

    def generate(
        self,
        request: VideoGenerationRequest,
        *,
        output_path: str | Path,
    ) -> Result[VideoGenerationResponse]:
        readiness = self.health_check()
        if not readiness.success:
            return Result.fail(
                readiness.error or "FFmpeg is unavailable.",
                error_type=readiness.error_type,
            )

        if not request.source_image.is_file():
            return Result.fail(
                f"Source image not found: {request.source_image}",
                error_type="SourceImageNotFoundError",
            )

        destination = Path(output_path)
        ensure_directory(destination.parent)
        width, height = _dimensions_for_ratio(request.aspect_ratio)
        frame_count = max(1, round(request.duration_seconds * request.fps))

        zoom_expression = (
            "min(zoom+0.0015,1.15)"
            if _prefers_zoom_in(request.prompt)
            else "max(zoom-0.001,1.0)"
        )
        filter_graph = (
            f"scale={width * 2}:{height * 2}:"
            "force_original_aspect_ratio=increase,"
            f"crop={width * 2}:{height * 2},"
            f"zoompan=z='{zoom_expression}':"
            "x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':"
            f"d={frame_count}:s={width}x{height}:fps={request.fps},"
            "format=yuv420p"
        )

        command = [
            self.executable,
            "-y",
            "-loop",
            "1",
            "-i",
            str(request.source_image),
            "-vf",
            filter_graph,
            "-t",
            str(request.duration_seconds),
            "-r",
            str(request.fps),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-movflags",
            "+faststart",
            str(destination),
        ]

        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            return Result.from_exception(exc)

        if completed.returncode != 0:
            return Result.fail(
                completed.stderr.strip() or "FFmpeg video generation failed.",
                error_type="FFmpegExecutionError",
            )

        video = GeneratedVideo(
            path=destination,
            prompt=request.prompt,
            provider=self.name,
            model=self.resolve_model(request),
            duration_seconds=request.duration_seconds,
            source_image=request.source_image,
            metadata={
                "command": command,
                "animation": "ken-burns",
            },
        )
        return Result.ok(VideoGenerationResponse(video=video))


def _dimensions_for_ratio(aspect_ratio: str) -> tuple[int, int]:
    normalized = aspect_ratio.strip()
    mapping = {
        "9:16": (1080, 1920),
        "16:9": (1920, 1080),
        "1:1": (1080, 1080),
        "4:5": (1080, 1350),
    }
    return mapping.get(normalized, (1080, 1920))


def _prefers_zoom_in(prompt: str) -> bool:
    normalized = prompt.lower()
    return any(
        phrase in normalized
        for phrase in ("push-in", "push in", "zoom in", "close-up")
    )
