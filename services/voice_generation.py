from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.result import Result
from providers.audio.base import BaseVoiceProvider
from providers.audio.models import GeneratedAudio, VoiceGenerationRequest
from schemas.video_planning import Storyboard


@dataclass(frozen=True, slots=True)
class SceneNarrationAsset:
    scene_number: int
    audio: GeneratedAudio


class StoryboardVoiceGenerator:
    """Generate narration audio for every storyboard scene."""

    def __init__(
        self,
        provider: BaseVoiceProvider,
        *,
        output_directory: str | Path,
        voice: str = "alloy",
        instructions: str | None = None,
        speed: float = 1.0,
        response_format: str = "mp3",
    ) -> None:
        self.provider = provider
        self.output_directory = Path(output_directory)
        self.voice = voice
        self.instructions = instructions
        self.speed = speed
        self.response_format = response_format

    def generate(
        self,
        storyboard: Storyboard,
    ) -> Result[tuple[SceneNarrationAsset, ...]]:
        assets: list[SceneNarrationAsset] = []

        for scene in storyboard.scenes:
            output_path = (
                self.output_directory
                / f"scene_{scene.scene_number:03d}"
                / f"narration.{self.response_format}"
            )
            result = self.provider.generate(
                VoiceGenerationRequest(
                    text=scene.narration,
                    voice=self.voice,
                    instructions=self.instructions,
                    response_format=self.response_format,
                    speed=self.speed,
                    metadata={"scene_number": scene.scene_number},
                ),
                output_path=output_path,
            )

            if not result.success:
                return Result.fail(
                    result.error
                    or (
                        "Voice generation failed for scene "
                        f"{scene.scene_number}."
                    ),
                    error_type=result.error_type,
                )

            assets.append(
                SceneNarrationAsset(
                    scene_number=scene.scene_number,
                    audio=result.unwrap().audio,
                )
            )

        return Result.ok(tuple(assets))
