from __future__ import annotations

from pathlib import Path

from core.result import Result
from engine.context import WorkflowContext
from engine.step import BaseStep
from engine.workflow import Workflow
from schemas.video_planning import Storyboard
from services.subtitle_generation import StoryboardSubtitleGenerator


class GenerateSubtitlesStep(BaseStep):
    def __init__(
        self,
        *,
        output_directory: str | Path,
        language: str = "en",
    ) -> None:
        super().__init__(
            "generate_subtitles",
            description=(
                "Generate synchronized SRT and VTT subtitles "
                "from storyboard narration."
            ),
        )
        self.generator = StoryboardSubtitleGenerator(
            output_directory=output_directory,
            language=language,
        )

    def validate(self, context: WorkflowContext) -> Result[None]:
        if not isinstance(context.get("storyboard"), Storyboard):
            return Result.fail(
                "Storyboard is required before subtitle generation."
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
                result.error or "Subtitle generation failed.",
                error_type=result.error_type,
            )

        context.put("subtitle_asset", result.unwrap())
        return Result.ok(context)


def build_subtitle_generation_workflow(
    *,
    output_directory: str | Path,
    language: str = "en",
) -> Workflow:
    return Workflow(
        "subtitle_generation",
        description=(
            "Create synchronized subtitle files from the storyboard."
        ),
        steps=[
            GenerateSubtitlesStep(
                output_directory=output_directory,
                language=language,
            )
        ],
    )
