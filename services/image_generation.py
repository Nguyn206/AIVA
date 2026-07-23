from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.result import Result
from providers.image.base import BaseImageProvider
from providers.image.models import (
    GeneratedImage,
    ImageGenerationRequest,
)
from schemas.video_planning import Storyboard


@dataclass(frozen=True, slots=True)
class SceneImageAsset:
    scene_number: int
    image: GeneratedImage


class StoryboardImageGenerator:
    """Generate one or more source images for every storyboard scene."""

    def __init__(
        self,
        provider: BaseImageProvider,
        *,
        output_directory: str | Path,
        size: str = "1024x1536",
        quality: str = "auto",
    ) -> None:
        self.provider = provider
        self.output_directory = Path(output_directory)
        self.size = size
        self.quality = quality

    def generate(
        self,
        storyboard: Storyboard,
    ) -> Result[tuple[SceneImageAsset, ...]]:
        assets: list[SceneImageAsset] = []

        for scene in storyboard.scenes:
            scene_directory = (
                self.output_directory
                / f"scene_{scene.scene_number:03d}"
            )
            result = self.provider.generate(
                ImageGenerationRequest(
                    prompt=scene.image_prompt,
                    size=self.size,
                    quality=self.quality,
                    count=1,
                    metadata={"scene_number": scene.scene_number},
                ),
                output_directory=scene_directory,
            )

            if not result.success:
                return Result.fail(
                    result.error
                    or (
                        "Image generation failed for scene "
                        f"{scene.scene_number}."
                    ),
                    error_type=result.error_type,
                )

            image = result.unwrap().images[0]
            assets.append(
                SceneImageAsset(
                    scene_number=scene.scene_number,
                    image=image,
                )
            )

        return Result.ok(tuple(assets))
