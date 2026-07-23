from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubtitleCue:
    index: int
    start_seconds: float
    end_seconds: float
    text: str

    def __post_init__(self) -> None:
        if self.index <= 0:
            raise ValueError("Subtitle cue index must be greater than zero.")
        if self.start_seconds < 0:
            raise ValueError("Subtitle start time cannot be negative.")
        if self.end_seconds <= self.start_seconds:
            raise ValueError(
                "Subtitle end time must be greater than start time."
            )
        if not self.text.strip():
            raise ValueError("Subtitle text must not be empty.")


@dataclass(frozen=True, slots=True)
class SubtitleTrack:
    cues: tuple[SubtitleCue, ...]
    language: str = "en"

    def __post_init__(self) -> None:
        if not self.cues:
            raise ValueError("Subtitle track must contain at least one cue.")
        if not self.language.strip():
            raise ValueError("Subtitle language must not be empty.")

    @property
    def duration_seconds(self) -> float:
        return max(cue.end_seconds for cue in self.cues)
