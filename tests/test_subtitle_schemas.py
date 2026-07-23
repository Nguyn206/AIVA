import pytest

from schemas.subtitles import SubtitleCue, SubtitleTrack


def test_subtitle_cue_validates_times() -> None:
    with pytest.raises(ValueError):
        SubtitleCue(
            index=1,
            start_seconds=2,
            end_seconds=1,
            text="Invalid",
        )


def test_subtitle_track_reports_duration() -> None:
    track = SubtitleTrack(
        cues=(
            SubtitleCue(
                index=1,
                start_seconds=0,
                end_seconds=2.5,
                text="Hello",
            ),
            SubtitleCue(
                index=2,
                start_seconds=2.5,
                end_seconds=5,
                text="World",
            ),
        )
    )

    assert track.duration_seconds == 5
