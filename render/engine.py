from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from core.helpers import ensure_directory
from core.result import Result
from render.ffmpeg import BaseCommandRunner, FFmpegRunner
from render.models import RenderRequest, RenderResult


class RenderEngine:
    """Compose scene clips, narration, and subtitles into one MP4."""

    def __init__(
        self,
        runner: BaseCommandRunner | None = None,
        *,
        ffmpeg_executable: str = "ffmpeg",
    ) -> None:
        self.runner = runner or FFmpegRunner(ffmpeg_executable)

    def render(
        self,
        request: RenderRequest,
    ) -> Result[RenderResult]:
        try:
            self._validate_input_files(request)
            ensure_directory(request.output_path.parent)

            with TemporaryDirectory(prefix="aiva-render-") as temp_dir:
                temp_path = Path(temp_dir)
                normalized_clips: list[Path] = []

                for scene in sorted(
                    request.scenes,
                    key=lambda item: item.scene_number,
                ):
                    normalized = (
                        temp_path
                        / f"scene_{scene.scene_number:03d}.mp4"
                    )
                    command = self._build_scene_command(
                        scene.video_path,
                        scene.audio_path,
                        normalized,
                        request,
                    )
                    result = self.runner.run(command)
                    if not result.success:
                        return Result.fail(
                            result.error
                            or (
                                "Failed to normalize scene "
                                f"{scene.scene_number}."
                            ),
                            error_type=result.error_type,
                        )
                    normalized_clips.append(normalized)

                concat_file = temp_path / "concat.txt"
                concat_file.write_text(
                    "\n".join(
                        f"file '{_escape_concat_path(path)}'"
                        for path in normalized_clips
                    )
                    + "\n",
                    encoding="utf-8",
                )

                merged_path = temp_path / "merged.mp4"
                concat_command = [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(concat_file),
                    "-c",
                    "copy",
                    str(merged_path),
                ]
                concat_result = self.runner.run(concat_command)
                if not concat_result.success:
                    return Result.fail(
                        concat_result.error
                        or "Failed to concatenate scene clips.",
                        error_type=concat_result.error_type,
                    )

                final_command = self._build_final_command(
                    merged_path,
                    request,
                )
                final_result = self.runner.run(final_command)
                if not final_result.success:
                    return Result.fail(
                        final_result.error
                        or "Failed to create final video.",
                        error_type=final_result.error_type,
                    )

            return Result.ok(
                RenderResult(
                    output_path=request.output_path,
                    scene_count=len(request.scenes),
                    subtitle_burned=request.subtitle_path is not None,
                    command=tuple(final_command),
                )
            )
        except Exception as exc:
            return Result.from_exception(exc)

    @staticmethod
    def _validate_input_files(request: RenderRequest) -> None:
        for scene in request.scenes:
            if not scene.video_path.is_file():
                raise FileNotFoundError(
                    f"Scene video not found: {scene.video_path}"
                )
            if (
                scene.audio_path is not None
                and not scene.audio_path.is_file()
            ):
                raise FileNotFoundError(
                    f"Scene audio not found: {scene.audio_path}"
                )

        if (
            request.subtitle_path is not None
            and not request.subtitle_path.is_file()
        ):
            raise FileNotFoundError(
                f"Subtitle file not found: {request.subtitle_path}"
            )

    @staticmethod
    def _build_scene_command(
        video_path: Path,
        audio_path: Path | None,
        output_path: Path,
        request: RenderRequest,
    ) -> list[str]:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
        ]

        if audio_path is not None:
            command.extend(["-i", str(audio_path)])

        video_filter = (
            f"scale={request.width}:{request.height}:"
            "force_original_aspect_ratio=decrease,"
            f"pad={request.width}:{request.height}:"
            "(ow-iw)/2:(oh-ih)/2,"
            f"fps={request.fps},format=yuv420p"
        )
        command.extend(
            [
                "-vf",
                video_filter,
                "-c:v",
                request.video_codec,
                "-preset",
                request.preset,
                "-crf",
                str(request.crf),
            ]
        )

        if audio_path is not None:
            command.extend(
                [
                    "-c:a",
                    request.audio_codec,
                    "-shortest",
                ]
            )
        else:
            command.append("-an")

        command.append(str(output_path))
        return command

    @staticmethod
    def _build_final_command(
        merged_path: Path,
        request: RenderRequest,
    ) -> list[str]:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(merged_path),
        ]

        if request.subtitle_path is not None:
            subtitle_filter = (
                "subtitles="
                + _escape_filter_path(request.subtitle_path)
            )
            command.extend(["-vf", subtitle_filter])

        command.extend(
            [
                "-c:v",
                request.video_codec,
                "-preset",
                request.preset,
                "-crf",
                str(request.crf),
                "-c:a",
                request.audio_codec,
                "-movflags",
                "+faststart",
                str(request.output_path),
            ]
        )
        return command


def _escape_concat_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "'\\''")


def _escape_filter_path(path: Path) -> str:
    value = str(path.resolve()).replace("\\", "/")
    value = value.replace(":", "\\:")
    value = value.replace("'", "\\'")
    return f"'{value}'"
