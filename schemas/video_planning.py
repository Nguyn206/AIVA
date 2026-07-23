from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ProductInput:
    name: str
    description: str
    target_market: str
    product_url: str | None = None
    features: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Product name must not be empty.")
        if not self.description.strip():
            raise ValueError("Product description must not be empty.")
        if not self.target_market.strip():
            raise ValueError("Target market must not be empty.")

    def to_prompt_text(self) -> str:
        lines = [
            f"Name: {self.name}",
            f"Description: {self.description}",
            f"Target market: {self.target_market}",
        ]
        if self.product_url:
            lines.append(f"URL: {self.product_url}")
        if self.features:
            lines.append("Features:")
            lines.extend(f"- {feature}" for feature in self.features)
        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class VideoScript:
    title: str
    hook: str
    scenes: tuple[dict[str, Any], ...]
    narration: str
    call_to_action: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VideoScript:
        required = {
            "title",
            "hook",
            "scenes",
            "narration",
            "call_to_action",
        }
        missing = required.difference(data)
        if missing:
            raise ValueError(
                "Video script is missing fields: "
                + ", ".join(sorted(missing))
            )

        scenes = data["scenes"]
        if not isinstance(scenes, list):
            raise ValueError("Video script scenes must be a list.")

        return cls(
            title=str(data["title"]),
            hook=str(data["hook"]),
            scenes=tuple(
                scene if isinstance(scene, dict) else {"content": scene}
                for scene in scenes
            ),
            narration=str(data["narration"]),
            call_to_action=str(data["call_to_action"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "hook": self.hook,
            "scenes": list(self.scenes),
            "narration": self.narration,
            "call_to_action": self.call_to_action,
        }


@dataclass(frozen=True, slots=True)
class StoryboardScene:
    scene_number: int
    duration_seconds: float
    narration: str
    visual_description: str
    image_prompt: str
    video_prompt: str
    on_screen_text: str = ""
    transition: str = "cut"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryboardScene:
        required = {
            "scene_number",
            "duration_seconds",
            "narration",
            "visual_description",
            "image_prompt",
            "video_prompt",
        }
        missing = required.difference(data)
        if missing:
            raise ValueError(
                "Storyboard scene is missing fields: "
                + ", ".join(sorted(missing))
            )

        return cls(
            scene_number=int(data["scene_number"]),
            duration_seconds=float(data["duration_seconds"]),
            narration=str(data["narration"]),
            visual_description=str(data["visual_description"]),
            image_prompt=str(data["image_prompt"]),
            video_prompt=str(data["video_prompt"]),
            on_screen_text=str(data.get("on_screen_text", "")),
            transition=str(data.get("transition", "cut")),
        )


@dataclass(frozen=True, slots=True)
class Storyboard:
    scenes: tuple[StoryboardScene, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Storyboard:
        raw_scenes = data.get("scenes")
        if not isinstance(raw_scenes, list) or not raw_scenes:
            raise ValueError(
                "Storyboard must contain a non-empty scenes list."
            )

        scenes = tuple(
            StoryboardScene.from_dict(scene)
            for scene in raw_scenes
            if isinstance(scene, dict)
        )
        if len(scenes) != len(raw_scenes):
            raise ValueError("Every storyboard scene must be an object.")

        return cls(scenes=scenes)

    @property
    def total_duration_seconds(self) -> float:
        return sum(scene.duration_seconds for scene in self.scenes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenes": [
                {
                    "scene_number": scene.scene_number,
                    "duration_seconds": scene.duration_seconds,
                    "narration": scene.narration,
                    "visual_description": scene.visual_description,
                    "image_prompt": scene.image_prompt,
                    "video_prompt": scene.video_prompt,
                    "on_screen_text": scene.on_screen_text,
                    "transition": scene.transition,
                }
                for scene in self.scenes
            ]
        }
