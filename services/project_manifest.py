from __future__ import annotations

from pathlib import Path
from typing import Any

from core.helpers import write_json
from engine.context import WorkflowContext
from schemas.video_planning import Storyboard, VideoScript


def write_project_manifest(
    context: WorkflowContext,
    destination: str | Path,
) -> Path:
    """Persist the most important pipeline outputs as JSON metadata."""
    payload: dict[str, Any] = context.snapshot()
    data = payload["data"]

    script = data.get("video_script")
    if isinstance(script, VideoScript):
        data["video_script"] = script.to_dict()

    storyboard = data.get("storyboard")
    if isinstance(storyboard, Storyboard):
        data["storyboard"] = storyboard.to_dict()

    for key in (
        "scene_images",
        "scene_videos",
        "scene_narration_audio",
        "subtitle_asset",
        "final_video",
        "product_input",
    ):
        if key in data:
            data[key] = _serialize_value(data[key])

    return write_json(destination, payload)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)

    if hasattr(value, "__dataclass_fields__"):
        result: dict[str, Any] = {}
        for field_name in value.__dataclass_fields__:
            result[field_name] = _serialize_value(
                getattr(value, field_name)
            )
        return result

    if isinstance(value, tuple):
        return [_serialize_value(item) for item in value]

    if isinstance(value, list):
        return [_serialize_value(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): _serialize_value(item)
            for key, item in value.items()
        }

    return value
