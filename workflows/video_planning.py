from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.constants import PROJECT_ROOT
from core.result import Result
from engine.context import WorkflowContext
from engine.step import BaseStep
from engine.workflow import Workflow
from prompts.manager import PromptManager
from providers.base import BaseLLMProvider
from providers.models import LLMRequest
from schemas.video_planning import (
    ProductInput,
    Storyboard,
    VideoScript,
)
from services.json_parser import parse_json_object


@dataclass(frozen=True, slots=True)
class VideoPlanningConfig:
    duration_seconds: int = 30
    tone: str = "persuasive"
    platform: str = "TikTok"
    aspect_ratio: str = "9:16"
    visual_style: str = "cinematic product advertising"

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0:
            raise ValueError("Video duration must be greater than zero.")
        if not self.tone.strip():
            raise ValueError("Video tone must not be empty.")
        if not self.platform.strip():
            raise ValueError("Platform must not be empty.")
        if not self.aspect_ratio.strip():
            raise ValueError("Aspect ratio must not be empty.")
        if not self.visual_style.strip():
            raise ValueError("Visual style must not be empty.")


class PromptBackedStep(BaseStep):
    def __init__(
        self,
        name: str,
        *,
        prompt_manager: PromptManager,
        provider: BaseLLMProvider,
        description: str = "",
    ) -> None:
        super().__init__(name, description=description)
        self.prompt_manager = prompt_manager
        self.provider = provider

    def _generate_json(
        self,
        prompt_name: str,
        variables: dict[str, Any],
        *,
        system_instruction: str,
    ) -> Result[dict[str, Any]]:
        try:
            prompt = self.prompt_manager.render(
                prompt_name,
                variables,
            )
            response = self.provider.generate(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=system_instruction,
                )
            )
            if not response.success:
                return Result.fail(
                    response.error or "LLM provider failed.",
                    error_type=response.error_type,
                )

            payload = parse_json_object(response.unwrap().text)
            return Result.ok(payload)
        except Exception as exc:
            return Result.from_exception(exc)


class ProductAnalysisStep(PromptBackedStep):
    def __init__(
        self,
        *,
        prompt_manager: PromptManager,
        provider: BaseLLMProvider,
    ) -> None:
        super().__init__(
            "analyze_product",
            prompt_manager=prompt_manager,
            provider=provider,
            description="Analyze product positioning for the AI video.",
        )

    def validate(self, context: WorkflowContext) -> Result[None]:
        product = context.get("product_input")
        if not isinstance(product, ProductInput):
            return Result.fail(
                "Workflow context requires ProductInput at "
                "'product_input'."
            )
        return Result.ok()

    def execute(
        self,
        context: WorkflowContext,
    ) -> Result[WorkflowContext]:
        product = context.require("product_input")
        result = self._generate_json(
            "product_analysis",
            {
                "product": product.to_prompt_text(),
                "target_market": product.target_market,
            },
            system_instruction=(
                "You analyze products for fully automated AI video ads. "
                "Return only valid JSON."
            ),
        )
        if not result.success:
            return Result.fail(
                result.error or "Product analysis failed.",
                error_type=result.error_type,
            )

        context.put("product_analysis", result.unwrap())
        return Result.ok(context)


class ScriptGenerationStep(PromptBackedStep):
    def __init__(
        self,
        *,
        prompt_manager: PromptManager,
        provider: BaseLLMProvider,
        config: VideoPlanningConfig,
    ) -> None:
        super().__init__(
            "generate_script",
            prompt_manager=prompt_manager,
            provider=provider,
            description="Generate an AI advertising script.",
        )
        self.config = config

    def validate(self, context: WorkflowContext) -> Result[None]:
        if not context.exists("product_analysis"):
            return Result.fail(
                "Product analysis is required before script generation."
            )
        return Result.ok()

    def execute(
        self,
        context: WorkflowContext,
    ) -> Result[WorkflowContext]:
        analysis = context.require("product_analysis")
        result = self._generate_json(
            "script_generation",
            {
                "product_analysis": json.dumps(
                    analysis,
                    ensure_ascii=False,
                    indent=2,
                ),
                "duration_seconds": self.config.duration_seconds,
                "tone": self.config.tone,
                "platform": self.config.platform,
            },
            system_instruction=(
                "You write short-form advertising scripts for fully "
                "automated AI videos. Return only valid JSON."
            ),
        )
        if not result.success:
            return Result.fail(
                result.error or "Script generation failed.",
                error_type=result.error_type,
            )

        try:
            script = VideoScript.from_dict(result.unwrap())
        except Exception as exc:
            return Result.from_exception(exc)

        context.put("video_script", script)
        return Result.ok(context)


class StoryboardGenerationStep(PromptBackedStep):
    def __init__(
        self,
        *,
        prompt_manager: PromptManager,
        provider: BaseLLMProvider,
        config: VideoPlanningConfig,
    ) -> None:
        super().__init__(
            "generate_storyboard",
            prompt_manager=prompt_manager,
            provider=provider,
            description="Generate scene-level image and video prompts.",
        )
        self.config = config

    def validate(self, context: WorkflowContext) -> Result[None]:
        if not isinstance(context.get("video_script"), VideoScript):
            return Result.fail(
                "VideoScript is required before storyboard generation."
            )
        return Result.ok()

    def execute(
        self,
        context: WorkflowContext,
    ) -> Result[WorkflowContext]:
        script = context.require("video_script")
        result = self._generate_json(
            "storyboard_generation",
            {
                "script": json.dumps(
                    script.to_dict(),
                    ensure_ascii=False,
                    indent=2,
                ),
                "aspect_ratio": self.config.aspect_ratio,
                "visual_style": self.config.visual_style,
            },
            system_instruction=(
                "You create production-ready storyboards for fully "
                "automated AI videos. Return only valid JSON."
            ),
        )
        if not result.success:
            return Result.fail(
                result.error or "Storyboard generation failed.",
                error_type=result.error_type,
            )

        try:
            storyboard = Storyboard.from_dict(result.unwrap())
        except Exception as exc:
            return Result.from_exception(exc)

        context.put("storyboard", storyboard)
        return Result.ok(context)


def build_video_planning_workflow(
    provider: BaseLLMProvider,
    *,
    config: VideoPlanningConfig | None = None,
    prompt_manager: PromptManager | None = None,
    template_directory: str | Path | None = None,
) -> Workflow:
    active_config = config or VideoPlanningConfig()
    manager = prompt_manager or PromptManager()
    directory = Path(
        template_directory
        or PROJECT_ROOT / "prompts" / "templates"
    )

    for prompt_name in (
        "product_analysis",
        "script_generation",
        "storyboard_generation",
    ):
        if not manager.registry.contains(prompt_name):
            manager.load_and_register(
                directory / f"{prompt_name}.md",
                name=prompt_name,
            )

    return Workflow(
        "ai_video_planning",
        description=(
            "Analyze a product and generate a script and storyboard."
        ),
        steps=[
            ProductAnalysisStep(
                prompt_manager=manager,
                provider=provider,
            ),
            ScriptGenerationStep(
                prompt_manager=manager,
                provider=provider,
                config=active_config,
            ),
            StoryboardGenerationStep(
                prompt_manager=manager,
                provider=provider,
                config=active_config,
            ),
        ],
    )
