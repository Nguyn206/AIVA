from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from typing import Any

from core.helpers import generate_id
from jobs.models import JobRecord, JobStatus

JobFunction = Callable[[JobRecord], Any]


class JobManager:
    """Run long AIVA pipelines outside the HTTP request thread."""

    def __init__(self, *, max_workers: int = 2) -> None:
        if max_workers <= 0:
            raise ValueError("max_workers must be greater than zero.")

        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="aiva-job",
        )
        self._records: dict[str, JobRecord] = {}
        self._futures: dict[str, Future[Any]] = {}
        self._lock = Lock()

    def submit(
        self,
        function: JobFunction,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> JobRecord:
        record = JobRecord(
            job_id=generate_id("job"),
            metadata=metadata or {},
        )

        with self._lock:
            self._records[record.job_id] = record
            self._futures[record.job_id] = self._executor.submit(
                self._run,
                record,
                function,
            )

        return record

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._records.get(job_id)

    def list(self) -> tuple[JobRecord, ...]:
        with self._lock:
            return tuple(self._records.values())

    def update(
        self,
        job_id: str,
        *,
        progress: int | None = None,
        message: str | None = None,
        project_id: str | None = None,
    ) -> JobRecord:
        with self._lock:
            record = self._records[job_id]

            if progress is not None:
                record.progress = max(0, min(100, progress))
            if message is not None:
                record.message = message
            if project_id is not None:
                record.project_id = project_id

            return record

    @staticmethod
    def _run(
        record: JobRecord,
        function: JobFunction,
    ) -> None:
        record.status = JobStatus.RUNNING
        record.set_progress(1, "Starting AIVA pipeline")

        try:
            result = function(record)
            record.status = JobStatus.COMPLETED
            record.set_progress(100, "Video generation completed")

            if hasattr(result, "project_id"):
                record.project_id = result.project_id
            if hasattr(result, "final_video_path"):
                record.final_video_path = str(
                    result.final_video_path
                )
        except Exception as exc:
            record.status = JobStatus.FAILED
            record.error = str(exc) or exc.__class__.__name__
            record.message = "Video generation failed"

    def shutdown(self, *, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait)
