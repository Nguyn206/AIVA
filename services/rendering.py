from __future__ import annotations

from pathlib import Path

from core.result import Result
from render.engine import RenderEngine
from render.models import (
    RenderRequest,
    RenderResult,
    SceneRenderInput,
)
from services.subtitle_generation import SubtitleAsset
from services.video_generation import SceneVideoAsset
from services.voice_generation import SceneNarrationAsset


class AIVideoRenderer:
    """Map workflow assets into a final render request."""

    def __init__(
        self,
        engine: RenderEngine,
        *,
        output_path: str | Path,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
    ) -> None:
        self.engine = engine
        self.output_path = Path(output_path)
        self.width = width
        self.height = height
        self.fps = fps

    def render(
        self,
        scene_videos: tuple[SceneVideoAsset, ...],
        scene_audio: tuple[SceneNarrationAsset, ...] = (),
        subtitle_asset: SubtitleAsset | None = None,
    ) -> Result[RenderResult]:
        audio_by_scene = {
            asset.scene_number: asset.audio.path
            for asset in scene_audio
        }

        scenes = tuple(
            SceneRenderInput(
                scene_number=asset.scene_number,
                video_path=asset.video.path,
                audio_path=audio_by_scene.get(asset.scene_number),
            )
            for asset in scene_videos
        )

        return self.engine.render(
            RenderRequest(
                scenes=scenes,
                output_path=self.output_path,
                subtitle_path=(
                    subtitle_asset.srt_path
                    if subtitle_asset is not None
                    else None
                ),
                width=self.width,
                height=self.height,
                fps=self.fps,
            )
        )
