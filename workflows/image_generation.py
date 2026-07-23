from __future__ import annotations

from pathlib import Path

from core.result import Result
from engine.context import WorkflowContext
from engine.step import BaseStep
from engine.workflow import Workflow
from providers.image.base import BaseImageProvider
from schemas.video_planning import Storyboard
from services.image_generation import StoryboardImageGenerator


class GenerateStoryboardImagesStep(BaseStep):
    def __init__(
        self,
        *,
        provider: BaseImageProvider,
        output_directory: str | Path,
    ) -> None:
        super().__init__(
            "generate_storyboard_images",
            description=(
                "Generate source images for every storyboard scene."
            ),
        )
        self.generator = StoryboardImageGenerator(
            provider,
            output_directory=output_directory,
        )

    def validate(self, context: WorkflowContext) -> Result[None]:
        if not isinstance(context.get("storyboard"), Storyboard):
            return Result.fail(
                "Storyboard is required before image generation."
            )
        return Result.ok()

    def execute(
        self,
        context: WorkflowContext,
    ) -> Result[WorkflowContext]:
        storyboard = context.require("storyboard")
        result = self.generator.generate(storyboard)

        if not result.success:
            return Result.fail(
                result.error or "Storyboard image generation failed.",
                error_type=result.error_type,
            )

        context.put("scene_images", result.unwrap())
        return Result.ok(context)


def build_image_generation_workflow(
    provider: BaseImageProvider,
    *,
    output_directory: str | Path,
) -> Workflow:
    return Workflow(
        "ai_image_generation",
        description=(
            "Generate source images from storyboard image prompts."
        ),
        steps=[
            GenerateStoryboardImagesStep(
                provider=provider,
                output_directory=output_directory,
            )
        ],
    )
