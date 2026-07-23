from __future__ import annotations

from pathlib import Path

from core.result import Result
from engine.context import WorkflowContext
from engine.step import BaseStep
from engine.workflow import Workflow
from providers.video.base import BaseVideoProvider
from schemas.video_planning import Storyboard
from services.image_generation import SceneImageAsset
from services.video_generation import StoryboardVideoGenerator


class GenerateStoryboardVideosStep(BaseStep):
    def __init__(
        self,
        *,
        provider: BaseVideoProvider,
        output_directory: str | Path,
        aspect_ratio: str = "9:16",
        fps: int = 24,
    ) -> None:
        super().__init__(
            "generate_storyboard_videos",
            description=(
                "Turn storyboard source images into scene-level clips."
            ),
        )
        self.generator = StoryboardVideoGenerator(
            provider,
            output_directory=output_directory,
            aspect_ratio=aspect_ratio,
            fps=fps,
        )

    def validate(self, context: WorkflowContext) -> Result[None]:
        if not isinstance(context.get("storyboard"), Storyboard):
            return Result.fail(
                "Storyboard is required before video generation."
            )

        scene_images = context.get("scene_images")
        if not isinstance(scene_images, tuple) or not all(
            isinstance(asset, SceneImageAsset)
            for asset in scene_images
        ):
            return Result.fail(
                "Scene images are required before video generation."
            )

        return Result.ok()

    def execute(
        self,
        context: WorkflowContext,
    ) -> Result[WorkflowContext]:
        storyboard = context.require("storyboard")
        scene_images = context.require("scene_images")
        result = self.generator.generate(
            storyboard,
            scene_images,
        )

        if not result.success:
            return Result.fail(
                result.error or "Storyboard video generation failed.",
                error_type=result.error_type,
            )

        context.put("scene_videos", result.unwrap())
        return Result.ok(context)


def build_video_generation_workflow(
    provider: BaseVideoProvider,
    *,
    output_directory: str | Path,
    aspect_ratio: str = "9:16",
    fps: int = 24,
) -> Workflow:
    return Workflow(
        "ai_video_generation",
        description=(
            "Generate a short clip for every storyboard scene."
        ),
        steps=[
            GenerateStoryboardVideosStep(
                provider=provider,
                output_directory=output_directory,
                aspect_ratio=aspect_ratio,
                fps=fps,
            )
        ],
    )
