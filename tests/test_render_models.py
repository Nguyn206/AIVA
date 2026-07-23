import pytest

from render.models import RenderRequest, SceneRenderInput


def test_render_request_requires_scenes(tmp_path) -> None:
    with pytest.raises(ValueError):
        RenderRequest(
            scenes=(),
            output_path=tmp_path / "video.mp4",
        )


def test_scene_render_input_validates_number(tmp_path) -> None:
    with pytest.raises(ValueError):
        SceneRenderInput(
            scene_number=0,
            video_path=tmp_path / "clip.mp4",
        )
