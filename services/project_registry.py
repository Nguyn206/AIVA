from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from services.project_status import ProjectStatus, get_project_status


@dataclass(frozen=True, slots=True)
class ProjectSummary:
    project_id: str
    project_directory: Path
    stage: str
    final_video_exists: bool


def list_projects(
    output_root: str | Path,
) -> tuple[ProjectSummary, ...]:
    root = Path(output_root)
    if not root.is_dir():
        return ()

    projects: list[ProjectSummary] = []

    for directory in sorted(root.iterdir()):
        if not directory.is_dir():
            continue

        status = get_project_status(root, directory.name)
        if not _looks_like_aiva_project(status):
            continue

        projects.append(
            ProjectSummary(
                project_id=directory.name,
                project_directory=directory,
                stage=(
                    status.stage.value
                    if status.stage is not None
                    else "unknown"
                ),
                final_video_exists=status.final_video_exists,
            )
        )

    return tuple(projects)


def _looks_like_aiva_project(status: ProjectStatus) -> bool:
    return (
        status.checkpoint_exists
        or status.context_exists
        or status.final_video_exists
    )
