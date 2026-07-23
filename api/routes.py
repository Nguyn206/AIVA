from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.dependencies import build_pipeline
from api.job_dependencies import job_manager
from api.models import (
    CreateJobResponse,
    CreateVideoRequest,
    CreateVideoResponse,
    JobStatusResponse,
    ProjectStatusResponse,
    ProjectSummaryResponse,
)
from jobs.models import JobRecord
from schemas.video_planning import ProductInput
from services.project_registry import list_projects
from services.project_status import get_project_status

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/projects",
    response_model=list[ProjectSummaryResponse],
)
def projects(output_root: str = "output") -> list[ProjectSummaryResponse]:
    return [
        ProjectSummaryResponse(
            project_id=project.project_id,
            stage=project.stage,
            final_video_exists=project.final_video_exists,
            project_directory=str(project.project_directory),
        )
        for project in list_projects(output_root)
    ]


@router.get(
    "/projects/{project_id}",
    response_model=ProjectStatusResponse,
)
def project_status(
    project_id: str,
    output_root: str = "output",
) -> ProjectStatusResponse:
    status = get_project_status(output_root, project_id)

    if not status.project_directory.is_dir():
        raise HTTPException(status_code=404, detail="Project not found.")

    return ProjectStatusResponse(
        project_id=status.project_id,
        stage=status.stage.value if status.stage else "unknown",
        checkpoint_exists=status.checkpoint_exists,
        context_exists=status.context_exists,
        final_video_exists=status.final_video_exists,
        project_directory=str(status.project_directory),
    )


@router.post(
    "/videos",
    response_model=CreateVideoResponse,
)
def create_video(
    request: CreateVideoRequest,
    output_root: str = "output",
) -> CreateVideoResponse:
    """Synchronous endpoint retained for tests and direct API usage."""
    pipeline = _get_pipeline(request.mode, output_root)

    result = pipeline.run(
        _to_product_input(request),
        project_id=request.project_id,
    )

    if not result.success:
        return CreateVideoResponse(
            project_id=request.project_id or "unknown",
            status="failed",
            error=result.error,
        )

    output = result.unwrap()
    return CreateVideoResponse(
        project_id=output.project_id,
        status="completed",
        final_video_path=str(output.final_video_path),
    )


@router.post(
    "/jobs/videos",
    response_model=CreateJobResponse,
)
def create_video_job(
    request: CreateVideoRequest,
    output_root: str = "output",
) -> CreateJobResponse:
    """Start video generation in a background worker."""

    def run(record: JobRecord):
        pipeline = _get_pipeline(request.mode, output_root)
        record.set_progress(5, "Pipeline configured")

        result = pipeline.run(
            _to_product_input(request),
            project_id=request.project_id,
        )
        if not result.success:
            raise RuntimeError(
                result.error or "AIVA pipeline failed."
            )

        return result.unwrap()

    record = job_manager.submit(
        run,
        metadata={
            "mode": request.mode,
            "product_name": request.name,
        },
    )

    return CreateJobResponse(
        job_id=record.job_id,
        status=record.status.value,
        progress=record.progress,
        message=record.message,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
)
def job_status(job_id: str) -> JobStatusResponse:
    record = job_manager.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    return JobStatusResponse(
        job_id=record.job_id,
        status=record.status.value,
        progress=record.progress,
        message=record.message,
        project_id=record.project_id,
        final_video_path=record.final_video_path,
        error=record.error,
    )


@router.post(
    "/projects/{project_id}/resume",
    response_model=CreateVideoResponse,
)
def resume_project(
    project_id: str,
    mode: str = "mock",
    output_root: str = "output",
) -> CreateVideoResponse:
    pipeline = _get_pipeline(mode, output_root)

    result = pipeline.run(
        project_id=project_id,
        resume=True,
    )

    if not result.success:
        return CreateVideoResponse(
            project_id=project_id,
            status="failed",
            error=result.error,
        )

    output = result.unwrap()
    return CreateVideoResponse(
        project_id=output.project_id,
        status="completed",
        final_video_path=str(output.final_video_path),
    )


def _get_pipeline(mode: str, output_root: str):
    try:
        return build_pipeline(
            mode,
            output_root=Path(output_root),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Configuration error: {exc}",
        ) from exc


def _to_product_input(
    request: CreateVideoRequest,
) -> ProductInput:
    return ProductInput(
        name=request.name,
        description=request.description,
        target_market=request.target_market,
        product_url=request.product_url,
        features=tuple(request.features),
    )
