from render.engine import RenderEngine
from render.ffmpeg import MockFFmpegRunner
from render.models import RenderRequest, SceneRenderInput


def test_render_engine_creates_final_output(tmp_path) -> None:
    video_one = tmp_path / "scene1.mp4"
    video_two = tmp_path / "scene2.mp4"
    audio_one = tmp_path / "scene1.wav"
    subtitle = tmp_path / "subtitles.srt"

    video_one.write_bytes(b"video-one")
    video_two.write_bytes(b"video-two")
    audio_one.write_bytes(b"audio-one")
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHello\n",
        encoding="utf-8",
    )

    runner = MockFFmpegRunner()
    engine = RenderEngine(runner)
    output = tmp_path / "final.mp4"

    result = engine.render(
        RenderRequest(
            scenes=(
                SceneRenderInput(
                    scene_number=1,
                    video_path=video_one,
                    audio_path=audio_one,
                ),
                SceneRenderInput(
                    scene_number=2,
                    video_path=video_two,
                ),
            ),
            output_path=output,
            subtitle_path=subtitle,
        )
    )

    render_result = result.unwrap()
    assert output.exists()
    assert render_result.scene_count == 2
    assert render_result.subtitle_burned is True
    assert len(runner.commands) == 4


def test_render_engine_reports_missing_scene_video(tmp_path) -> None:
    engine = RenderEngine(MockFFmpegRunner())

    result = engine.render(
        RenderRequest(
            scenes=(
                SceneRenderInput(
                    scene_number=1,
                    video_path=tmp_path / "missing.mp4",
                ),
            ),
            output_path=tmp_path / "final.mp4",
        )
    )

    assert result.success is False
    assert "not found" in (result.error or "").lower()
