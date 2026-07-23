from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.result import Result
from providers.video.base import BaseVideoProvider
from providers.video.models import GeneratedVideo, VideoGenerationRequest
from schemas.video_planning import Storyboard
from services.image_generation import SceneImageAsset


@dataclass(frozen=True, slots=True)
class SceneVideoAsset:
    scene_number: int
    video: GeneratedVideo


class StoryboardVideoGenerator:
    """Turn storyboard images into scene-level video clips."""

    def __init__(
        self,
        provider: BaseVideoProvider,
        *,
        output_directory: str | Path,
        aspect_ratio: str = "9:16",
        fps: int = 24,
    ) -> None:
        self.provider = provider
        self.output_directory = Path(output_directory)
        self.aspect_ratio = aspect_ratio
        self.fps = fps

    def generate(
        self,
        storyboard: Storyboard,
        scene_images: tuple[SceneImageAsset, ...],
    ) -> Result[tuple[SceneVideoAsset, ...]]:
        image_by_scene = {
            asset.scene_number: asset.image
            for asset in scene_images
        }
        assets: list[SceneVideoAsset] = []

        for scene in storyboard.scenes:
            image = image_by_scene.get(scene.scene_number)
            if image is None:
                return Result.fail(
                    f"Missing source image for scene {scene.scene_number}."
                )

            output_path = (
                self.output_directory
                / f"scene_{scene.scene_number:03d}"
                / "clip.mp4"
            )
            result = self.provider.generate(
                VideoGenerationRequest(
                    prompt=scene.video_prompt,
                    source_image=image.path,
                    duration_seconds=scene.duration_seconds,
                    aspect_ratio=self.aspect_ratio,
                    fps=self.fps,
                    metadata={"scene_number": scene.scene_number},
                ),
                output_path=output_path,
            )

            if not result.success:
                return Result.fail(
                    result.error
                    or (
                        "Video generation failed for scene "
                        f"{scene.scene_number}."
                    ),
                    error_type=result.error_type,
                )

            assets.append(
                SceneVideoAsset(
                    scene_number=scene.scene_number,
                    video=result.unwrap().video,
                )
            )

        return Result.ok(tuple(assets))
