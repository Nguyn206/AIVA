from __future__ import annotations

from pydantic import BaseModel, Field


class CreateVideoRequest(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    target_market: str = Field(min_length=1)
    product_url: str | None = None
    features: list[str] = Field(default_factory=list)
    mode: str = Field(default="mock", pattern="^(mock|real)$")
    project_id: str | None = None


class CreateVideoResponse(BaseModel):
    project_id: str
    status: str
    final_video_path: str | None = None
    error: str | None = None


class CreateJobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    project_id: str | None = None
    final_video_path: str | None = None
    error: str | None = None


class ProjectStatusResponse(BaseModel):
    project_id: str
    stage: str
    checkpoint_exists: bool
    context_exists: bool
    final_video_exists: bool
    project_directory: str


class ProjectSummaryResponse(BaseModel):
    project_id: str
    stage: str
    final_video_exists: bool
    project_directory: str


class ProjectAssetResponse(BaseModel):
    name: str
    relative_path: str
    size_bytes: int
    asset_type: str
    download_url: str


class PreflightCheckResponse(BaseModel):
    name: str
    passed: bool
    message: str


class PreflightReportResponse(BaseModel):
    passed: bool
    checks: list[PreflightCheckResponse]
