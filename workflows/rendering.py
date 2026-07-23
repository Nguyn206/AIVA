from __future__ import annotations

from pathlib import Path

from core.result import Result
from engine.context import WorkflowContext
from engine.step import BaseStep
from engine.workflow import Workflow
from render.engine import RenderEngine
from services.rendering import AIVideoRenderer
from services.subtitle_generation import SubtitleAsset
from services.video_generation import SceneVideoAsset
from services.voice_generation import SceneNarrationAsset


class RenderFinalVideoStep(BaseStep):
    def __init__(
        self,
        *,
        engine: RenderEngine,
        output_path: str | Path,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
    ) -> None:
        super().__init__(
            "render_final_video",
            description=(
                "Combine scene videos, narration, and subtitles "
                "into the final MP4."
            ),
        )
        self.renderer = AIVideoRenderer(
            engine,
            output_path=output_path,
            width=width,
            height=height,
            fps=fps,
        )

    def validate(self, context: WorkflowContext) -> Result[None]:
        scene_videos = context.get("scene_videos")
        if not isinstance(scene_videos, tuple) or not scene_videos:
            return Result.fail(
                "Scene videos are required before final rendering."
            )
        if not all(
            isinstance(asset, SceneVideoAsset)
            for asset in scene_videos
        ):
            return Result.fail("Invalid scene video assets.")

        scene_audio = context.get("scene_narration_audio", ())
        if not isinstance(scene_audio, tuple) or not all(
            isinstance(asset, SceneNarrationAsset)
            for asset in scene_audio
        ):
            return Result.fail("Invalid scene narration assets.")

        subtitle_asset = context.get("subtitle_asset")
        if (
            subtitle_asset is not None
            and not isinstance(subtitle_asset, SubtitleAsset)
        ):
            return Result.fail("Invalid subtitle asset.")

        return Result.ok()

    def execute(
        self,
        context: WorkflowContext,
    ) -> Result[WorkflowContext]:
        result = self.renderer.render(
            context.require("scene_videos"),
            context.get("scene_narration_audio", ()),
            context.get("subtitle_asset"),
        )

        if not result.success:
            return Result.fail(
                result.error or "Final video rendering failed.",
                error_type=result.error_type,
            )

        context.put("final_video", result.unwrap())
        return Result.ok(context)


def build_render_workflow(
    *,
    engine: RenderEngine,
    output_path: str | Path,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
) -> Workflow:
    return Workflow(
        "final_video_rendering",
        description=(
            "Render all generated AI assets into a final MP4."
        ),
        steps=[
            RenderFinalVideoStep(
                engine=engine,
                output_path=output_path,
                width=width,
                height=height,
                fps=fps,
            )
        ],
    )
