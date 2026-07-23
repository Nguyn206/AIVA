from __future__ import annotations

from pathlib import Path
from typing import Any

from core.helpers import read_json, write_json
from engine.context import WorkflowContext
from providers.audio.models import GeneratedAudio
from providers.image.models import GeneratedImage
from providers.video.models import GeneratedVideo
from render.models import RenderResult
from schemas.subtitles import SubtitleCue, SubtitleTrack
from schemas.video_planning import (
    ProductInput,
    Storyboard,
    StoryboardScene,
    VideoScript,
)
from services.image_generation import SceneImageAsset
from services.subtitle_generation import SubtitleAsset
from services.video_generation import SceneVideoAsset
from services.voice_generation import SceneNarrationAsset


def save_context(
    context: WorkflowContext,
    destination: str | Path,
) -> Path:
    payload = context.snapshot()
    payload["data"] = _serialize(payload["data"])
    return write_json(destination, payload)


def load_context(path: str | Path) -> WorkflowContext:
    payload = read_json(path)
    data = _restore_data(dict(payload.get("data", {})))

    return WorkflowContext(
        workflow_id=str(payload["workflow_id"]),
        project_id=payload.get("project_id"),
        data=data,
        metadata=dict(payload.get("metadata", {})),
        created_at=str(payload["created_at"]),
    )


def _serialize(value: Any) -> Any:
    if isinstance(value, Path):
        return {"__type__": "Path", "value": str(value)}

    if isinstance(value, ProductInput):
        return {
            "__type__": "ProductInput",
            "name": value.name,
            "description": value.description,
            "target_market": value.target_market,
            "product_url": value.product_url,
            "features": list(value.features),
        }

    if isinstance(value, VideoScript):
        return {"__type__": "VideoScript", **value.to_dict()}

    if isinstance(value, Storyboard):
        return {"__type__": "Storyboard", **value.to_dict()}

    if isinstance(value, StoryboardScene):
        return {
            "__type__": "StoryboardScene",
            "scene_number": value.scene_number,
            "duration_seconds": value.duration_seconds,
            "narration": value.narration,
            "visual_description": value.visual_description,
            "image_prompt": value.image_prompt,
            "video_prompt": value.video_prompt,
            "on_screen_text": value.on_screen_text,
            "transition": value.transition,
        }

    if isinstance(value, GeneratedImage):
        return {
            "__type__": "GeneratedImage",
            "path": str(value.path),
            "prompt": value.prompt,
            "provider": value.provider,
            "model": value.model,
            "revised_prompt": value.revised_prompt,
            "metadata": _serialize(value.metadata),
        }

    if isinstance(value, GeneratedVideo):
        return {
            "__type__": "GeneratedVideo",
            "path": str(value.path),
            "prompt": value.prompt,
            "provider": value.provider,
            "model": value.model,
            "duration_seconds": value.duration_seconds,
            "source_image": str(value.source_image),
            "metadata": _serialize(value.metadata),
        }

    if isinstance(value, GeneratedAudio):
        return {
            "__type__": "GeneratedAudio",
            "path": str(value.path),
            "provider": value.provider,
            "model": value.model,
            "voice": value.voice,
            "text": value.text,
            "response_format": value.response_format,
            "metadata": _serialize(value.metadata),
        }

    if isinstance(value, SceneImageAsset):
        return {
            "__type__": "SceneImageAsset",
            "scene_number": value.scene_number,
            "image": _serialize(value.image),
        }

    if isinstance(value, SceneVideoAsset):
        return {
            "__type__": "SceneVideoAsset",
            "scene_number": value.scene_number,
            "video": _serialize(value.video),
        }

    if isinstance(value, SceneNarrationAsset):
        return {
            "__type__": "SceneNarrationAsset",
            "scene_number": value.scene_number,
            "audio": _serialize(value.audio),
        }

    if isinstance(value, SubtitleCue):
        return {
            "__type__": "SubtitleCue",
            "index": value.index,
            "start_seconds": value.start_seconds,
            "end_seconds": value.end_seconds,
            "text": value.text,
        }

    if isinstance(value, SubtitleTrack):
        return {
            "__type__": "SubtitleTrack",
            "cues": _serialize(value.cues),
            "language": value.language,
        }

    if isinstance(value, SubtitleAsset):
        return {
            "__type__": "SubtitleAsset",
            "track": _serialize(value.track),
            "srt_path": str(value.srt_path),
            "vtt_path": str(value.vtt_path),
        }

    if isinstance(value, RenderResult):
        return {
            "__type__": "RenderResult",
            "output_path": str(value.output_path),
            "scene_count": value.scene_count,
            "subtitle_burned": value.subtitle_burned,
            "command": list(value.command),
            "metadata": _serialize(value.metadata),
        }

    if isinstance(value, tuple):
        return {
            "__type__": "tuple",
            "items": [_serialize(item) for item in value],
        }

    if isinstance(value, list):
        return [_serialize(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): _serialize(item)
            for key, item in value.items()
        }

    return value


def _restore_data(data: dict[str, Any]) -> dict[str, Any]:
    return {
        key: _restore(value)
        for key, value in data.items()
    }


def _restore(value: Any) -> Any:
    if isinstance(value, list):
        return [_restore(item) for item in value]

    if not isinstance(value, dict):
        return value

    type_name = value.get("__type__")
    if not type_name:
        return {
            key: _restore(item)
            for key, item in value.items()
        }

    if type_name == "Path":
        return Path(value["value"])

    if type_name == "tuple":
        return tuple(_restore(item) for item in value["items"])

    if type_name == "ProductInput":
        return ProductInput(
            name=value["name"],
            description=value["description"],
            target_market=value["target_market"],
            product_url=value.get("product_url"),
            features=tuple(value.get("features", [])),
        )

    if type_name == "VideoScript":
        return VideoScript.from_dict(value)

    if type_name == "Storyboard":
        return Storyboard.from_dict(value)

    if type_name == "GeneratedImage":
        return GeneratedImage(
            path=Path(value["path"]),
            prompt=value["prompt"],
            provider=value["provider"],
            model=value["model"],
            revised_prompt=value.get("revised_prompt"),
            metadata=_restore(value.get("metadata", {})),
        )

    if type_name == "GeneratedVideo":
        return GeneratedVideo(
            path=Path(value["path"]),
            prompt=value["prompt"],
            provider=value["provider"],
            model=value["model"],
            duration_seconds=float(value["duration_seconds"]),
            source_image=Path(value["source_image"]),
            metadata=_restore(value.get("metadata", {})),
        )

    if type_name == "GeneratedAudio":
        return GeneratedAudio(
            path=Path(value["path"]),
            provider=value["provider"],
            model=value["model"],
            voice=value["voice"],
            text=value["text"],
            response_format=value["response_format"],
            metadata=_restore(value.get("metadata", {})),
        )

    if type_name == "SceneImageAsset":
        return SceneImageAsset(
            scene_number=int(value["scene_number"]),
            image=_restore(value["image"]),
        )

    if type_name == "SceneVideoAsset":
        return SceneVideoAsset(
            scene_number=int(value["scene_number"]),
            video=_restore(value["video"]),
        )

    if type_name == "SceneNarrationAsset":
        return SceneNarrationAsset(
            scene_number=int(value["scene_number"]),
            audio=_restore(value["audio"]),
        )

    if type_name == "SubtitleCue":
        return SubtitleCue(
            index=int(value["index"]),
            start_seconds=float(value["start_seconds"]),
            end_seconds=float(value["end_seconds"]),
            text=value["text"],
        )

    if type_name == "SubtitleTrack":
        return SubtitleTrack(
            cues=tuple(_restore(value["cues"])),
            language=value["language"],
        )

    if type_name == "SubtitleAsset":
        return SubtitleAsset(
            track=_restore(value["track"]),
            srt_path=Path(value["srt_path"]),
            vtt_path=Path(value["vtt_path"]),
        )

    if type_name == "RenderResult":
        return RenderResult(
            output_path=Path(value["output_path"]),
            scene_count=int(value["scene_count"]),
            subtitle_burned=bool(value["subtitle_burned"]),
            command=tuple(value["command"]),
            metadata=_restore(value.get("metadata", {})),
        )

    return {
        key: _restore(item)
        for key, item in value.items()
        if key != "__type__"
    }
