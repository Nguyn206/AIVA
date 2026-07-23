from __future__ import annotations

from pathlib import Path

from core.result import Result
from engine.context import WorkflowContext
from engine.step import BaseStep
from engine.workflow import Workflow
from providers.audio.base import BaseVoiceProvider
from schemas.video_planning import Storyboard
from services.voice_generation import StoryboardVoiceGenerator


class GenerateStoryboardVoiceStep(BaseStep):
    def __init__(
        self,
        *,
        provider: BaseVoiceProvider,
        output_directory: str | Path,
        voice: str = "alloy",
        instructions: str | None = None,
        speed: float = 1.0,
        response_format: str = "mp3",
    ) -> None:
        super().__init__(
            "generate_storyboard_voice",
            description="Generate narration audio for every scene.",
        )
        self.generator = StoryboardVoiceGenerator(
            provider,
            output_directory=output_directory,
            voice=voice,
            instructions=instructions,
            speed=speed,
            response_format=response_format,
        )

    def validate(self, context: WorkflowContext) -> Result[None]:
        if not isinstance(context.get("storyboard"), Storyboard):
            return Result.fail(
                "Storyboard is required before voice generation."
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
                result.error or "Storyboard voice generation failed.",
                error_type=result.error_type,
            )

        context.put("scene_narration_audio", result.unwrap())
        return Result.ok(context)


def build_voice_generation_workflow(
    provider: BaseVoiceProvider,
    *,
    output_directory: str | Path,
    voice: str = "alloy",
    instructions: str | None = None,
    speed: float = 1.0,
    response_format: str = "mp3",
) -> Workflow:
    return Workflow(
        "ai_voice_generation",
        description="Generate narration audio from storyboard scenes.",
        steps=[
            GenerateStoryboardVoiceStep(
                provider=provider,
                output_directory=output_directory,
                voice=voice,
                instructions=instructions,
                speed=speed,
                response_format=response_format,
            )
        ],
    )
