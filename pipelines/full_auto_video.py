from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.helpers import ensure_directory, generate_id
from core.result import Result
from engine.context import WorkflowContext
from engine.executor import WorkflowExecutor
from providers.audio.base import BaseVoiceProvider
from providers.base import BaseLLMProvider
from providers.image.base import BaseImageProvider
from providers.video.base import BaseVideoProvider
from render.engine import RenderEngine
from schemas.video_planning import ProductInput
from workflows.image_generation import build_image_generation_workflow
from workflows.rendering import build_render_workflow
from workflows.subtitle_generation import build_subtitle_generation_workflow
from workflows.video_generation import build_video_generation_workflow
from workflows.video_planning import (
    VideoPlanningConfig,
    build_video_planning_workflow,
)
from workflows.voice_generation import build_voice_generation_workflow


@dataclass(frozen=True, slots=True)
class FullAutoVideoConfig:
    output_root: Path = Path("output")
    duration_seconds: int = 30
    tone: str = "persuasive"
    platform: str = "TikTok"
    aspect_ratio: str = "9:16"
    visual_style: str = "cinematic product advertising"
    voice: str = "alloy"
    voice_instructions: str | None = (
        "Warm, natural, persuasive, and suitable for short-form ads."
    )
    voice_speed: float = 1.0
    voice_format: str = "mp3"
    subtitle_language: str = "en"
    width: int = 1080
    height: int = 1920
    fps: int = 30

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0:
            raise ValueError("Video duration must be greater than zero.")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Output dimensions must be positive.")
        if self.fps <= 0:
            raise ValueError("Output FPS must be greater than zero.")


@dataclass(frozen=True, slots=True)
class FullAutoVideoResult:
    project_id: str
    project_directory: Path
    final_video_path: Path
    context: WorkflowContext


class FullAutoVideoPipeline:
    """Run the complete AIVA pipeline from product input to final MP4."""

    def __init__(
        self,
        *,
        llm_provider: BaseLLMProvider,
        image_provider: BaseImageProvider,
        video_provider: BaseVideoProvider,
        voice_provider: BaseVoiceProvider,
        render_engine: RenderEngine,
        config: FullAutoVideoConfig | None = None,
        executor: WorkflowExecutor | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.image_provider = image_provider
        self.video_provider = video_provider
        self.voice_provider = voice_provider
        self.render_engine = render_engine
        self.config = config or FullAutoVideoConfig()
        self.executor = executor or WorkflowExecutor()

    def run(
        self,
        product: ProductInput,
        *,
        project_id: str | None = None,
    ) -> Result[FullAutoVideoResult]:
        active_project_id = project_id or generate_id("video")
        project_directory = ensure_directory(
            self.config.output_root / active_project_id
        )

        context = WorkflowContext(
            project_id=active_project_id,
            data={"product_input": product},
            metadata={
                "platform": self.config.platform,
                "aspect_ratio": self.config.aspect_ratio,
            },
        )

        workflows = self._build_workflows(project_directory)

        for workflow in workflows:
            result = self.executor.run(workflow, context)
            if not result.success:
                return Result.fail(
                    result.error
                    or f"Pipeline failed in workflow: {workflow.name}",
                    error_type=result.error_type,
                )

            report = result.unwrap()
            context = report.context

        final_video = context.require("final_video")

        return Result.ok(
            FullAutoVideoResult(
                project_id=active_project_id,
                project_directory=project_directory,
                final_video_path=final_video.output_path,
                context=context,
            )
        )

    def _build_workflows(self, project_directory: Path):
        planning_config = VideoPlanningConfig(
            duration_seconds=self.config.duration_seconds,
            tone=self.config.tone,
            platform=self.config.platform,
            aspect_ratio=self.config.aspect_ratio,
            visual_style=self.config.visual_style,
        )

        return (
            build_video_planning_workflow(
                self.llm_provider,
                config=planning_config,
            ),
            build_image_generation_workflow(
                self.image_provider,
                output_directory=project_directory / "images",
            ),
            build_video_generation_workflow(
                self.video_provider,
                output_directory=project_directory / "clips",
                aspect_ratio=self.config.aspect_ratio,
                fps=self.config.fps,
            ),
            build_voice_generation_workflow(
                self.voice_provider,
                output_directory=project_directory / "audio",
                voice=self.config.voice,
                instructions=self.config.voice_instructions,
                speed=self.config.voice_speed,
                response_format=self.config.voice_format,
            ),
            build_subtitle_generation_workflow(
                output_directory=project_directory / "subtitles",
                language=self.config.subtitle_language,
            ),
            build_render_workflow(
                engine=self.render_engine,
                output_path=project_directory / "final.mp4",
                width=self.config.width,
                height=self.config.height,
                fps=self.config.fps,
            ),
        )
