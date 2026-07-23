from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from storage.checkpoints import CheckpointStore, PipelineStage


@dataclass(frozen=True, slots=True)
class ProjectStatus:
    project_id: str
    project_directory: Path
    stage: PipelineStage | None
    final_video_exists: bool
    context_exists: bool
    checkpoint_exists: bool


def get_project_status(
    output_root: str | Path,
    project_id: str,
) -> ProjectStatus:
    project_directory = Path(output_root) / project_id
    store = CheckpointStore(project_directory)
    checkpoint = store.load()

    return ProjectStatus(
        project_id=project_id,
        project_directory=project_directory,
        stage=checkpoint.stage if checkpoint else None,
        final_video_exists=(project_directory / "final.mp4").is_file(),
        context_exists=(project_directory / "context.json").is_file(),
        checkpoint_exists=store.checkpoint_path.is_file(),
    )
