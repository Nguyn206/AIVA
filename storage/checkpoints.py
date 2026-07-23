from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from core.helpers import read_json, utc_now_iso, write_json


class PipelineStage(StrEnum):
    CREATED = "created"
    PLANNED = "planned"
    IMAGES_GENERATED = "images_generated"
    VIDEOS_GENERATED = "videos_generated"
    VOICE_GENERATED = "voice_generated"
    SUBTITLES_GENERATED = "subtitles_generated"
    RENDERED = "rendered"


_STAGE_ORDER = {
    stage: index
    for index, stage in enumerate(PipelineStage)
}


@dataclass(frozen=True, slots=True)
class PipelineCheckpoint:
    project_id: str
    stage: PipelineStage
    updated_at: str
    context_path: Path
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.project_id.strip():
            raise ValueError("Checkpoint project_id must not be empty.")


class CheckpointStore:
    """Persist pipeline progress so expensive AI work can be resumed."""

    def __init__(self, project_directory: str | Path) -> None:
        self.project_directory = Path(project_directory)
        self.checkpoint_path = (
            self.project_directory / "checkpoint.json"
        )

    def save(
        self,
        *,
        project_id: str,
        stage: PipelineStage,
        context_path: str | Path,
        metadata: dict[str, Any] | None = None,
    ) -> PipelineCheckpoint:
        checkpoint = PipelineCheckpoint(
            project_id=project_id,
            stage=stage,
            updated_at=utc_now_iso(),
            context_path=Path(context_path),
            metadata=metadata or {},
        )
        write_json(
            self.checkpoint_path,
            {
                "project_id": checkpoint.project_id,
                "stage": checkpoint.stage.value,
                "updated_at": checkpoint.updated_at,
                "context_path": str(checkpoint.context_path),
                "metadata": checkpoint.metadata,
            },
        )
        return checkpoint

    def load(self) -> PipelineCheckpoint | None:
        if not self.checkpoint_path.is_file():
            return None

        payload = read_json(self.checkpoint_path)
        return PipelineCheckpoint(
            project_id=str(payload["project_id"]),
            stage=PipelineStage(str(payload["stage"])),
            updated_at=str(payload["updated_at"]),
            context_path=Path(payload["context_path"]),
            metadata=dict(payload.get("metadata", {})),
        )

    def reached(self, stage: PipelineStage) -> bool:
        checkpoint = self.load()
        if checkpoint is None:
            return False
        return _STAGE_ORDER[checkpoint.stage] >= _STAGE_ORDER[stage]

    def clear(self) -> None:
        if self.checkpoint_path.exists():
            self.checkpoint_path.unlink()
