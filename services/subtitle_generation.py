from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.helpers import ensure_directory
from core.result import Result
from schemas.subtitles import SubtitleCue, SubtitleTrack
from schemas.video_planning import Storyboard


@dataclass(frozen=True, slots=True)
class SubtitleAsset:
    track: SubtitleTrack
    srt_path: Path
    vtt_path: Path


class StoryboardSubtitleGenerator:
    """Create subtitle timing from storyboard narration and durations."""

    def __init__(
        self,
        *,
        output_directory: str | Path,
        language: str = "en",
    ) -> None:
        self.output_directory = Path(output_directory)
        self.language = language

    def generate(
        self,
        storyboard: Storyboard,
    ) -> Result[SubtitleAsset]:
        try:
            cues = self._build_cues(storyboard)
            track = SubtitleTrack(
                cues=tuple(cues),
                language=self.language,
            )

            ensure_directory(self.output_directory)
            srt_path = self.output_directory / "subtitles.srt"
            vtt_path = self.output_directory / "subtitles.vtt"

            srt_path.write_text(
                render_srt(track),
                encoding="utf-8",
            )
            vtt_path.write_text(
                render_vtt(track),
                encoding="utf-8",
            )

            return Result.ok(
                SubtitleAsset(
                    track=track,
                    srt_path=srt_path,
                    vtt_path=vtt_path,
                )
            )
        except Exception as exc:
            return Result.from_exception(exc)

    @staticmethod
    def _build_cues(
        storyboard: Storyboard,
    ) -> list[SubtitleCue]:
        cues: list[SubtitleCue] = []
        cursor = 0.0

        for index, scene in enumerate(storyboard.scenes, start=1):
            start = cursor
            end = cursor + scene.duration_seconds
            cues.append(
                SubtitleCue(
                    index=index,
                    start_seconds=start,
                    end_seconds=end,
                    text=scene.narration.strip(),
                )
            )
            cursor = end

        return cues


def render_srt(track: SubtitleTrack) -> str:
    blocks: list[str] = []

    for cue in track.cues:
        blocks.append(
            "\n".join(
                [
                    str(cue.index),
                    (
                        f"{_format_srt_time(cue.start_seconds)} --> "
                        f"{_format_srt_time(cue.end_seconds)}"
                    ),
                    cue.text,
                ]
            )
        )

    return "\n\n".join(blocks) + "\n"


def render_vtt(track: SubtitleTrack) -> str:
    blocks = ["WEBVTT", ""]

    for cue in track.cues:
        blocks.extend(
            [
                (
                    f"{_format_vtt_time(cue.start_seconds)} --> "
                    f"{_format_vtt_time(cue.end_seconds)}"
                ),
                cue.text,
                "",
            ]
        )

    return "\n".join(blocks)


def _format_srt_time(seconds: float) -> str:
    hours, minutes, secs, milliseconds = _split_time(seconds)
    return (
        f"{hours:02d}:{minutes:02d}:{secs:02d},"
        f"{milliseconds:03d}"
    )


def _format_vtt_time(seconds: float) -> str:
    hours, minutes, secs, milliseconds = _split_time(seconds)
    return (
        f"{hours:02d}:{minutes:02d}:{secs:02d}."
        f"{milliseconds:03d}"
    )


def _split_time(seconds: float) -> tuple[int, int, int, int]:
    total_milliseconds = round(seconds * 1000)
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return hours, minutes, secs, milliseconds
