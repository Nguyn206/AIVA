from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class JobRecord:
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0
    message: str = "Queued"
    project_id: str | None = None
    final_video_path: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def set_progress(
        self,
        progress: int,
        message: str,
    ) -> None:
        self.progress = max(0, min(100, progress))
        self.message = message
