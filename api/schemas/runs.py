from __future__ import annotations

"""
Run API schemas.

Traceability:
- AP-04
- AP-06
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


RunStatus = Literal[
    "queued",
    "running",
    "succeeded",
    "failed",
    "completed",
    "cancelled",
    "unknown",
]


class RunCreateAdvanced(BaseModel):
    query_version: str | None = None
    scoring_version: str | None = None
    note: str | None = None


class RunCreateRequest(BaseModel):
    countries: list[str] = Field(min_length=1)
    horizon_days: int = Field(gt=0)
    layers: list[str] = Field(min_length=1)
    advanced: RunCreateAdvanced | None = None


class RunCreateResponse(BaseModel):
    run_id: str
    status: RunStatus
    created_at: str


class ApiRunError(BaseModel):
    code: str
    message: str
    details: Any | None = None
    trace_id: str | None = None


class RunRecord(BaseModel):
    run_id: str
    status: RunStatus
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    countries: list[str]
    progress_percent: int | None = None
    warning_count: int = 0
    error: ApiRunError | None = None


class RunsResponse(BaseModel):
    runs: list[RunRecord]


class RunDetailResponse(BaseModel):
    run: RunRecord
    metadata: dict[str, Any] | None = None


class RunStatusProgress(BaseModel):
    phase: str | None = None
    percent: int | None = None
    message: str | None = None


class RunStatusResponse(BaseModel):
    run_id: str
    status: RunStatus
    progress: RunStatusProgress | None = None
    started_at: str | None = None
    finished_at: str | None = None
    updated_at: str | None = None
    error: ApiRunError | None = None


class RunSummaryResponse(BaseModel):
    run_id: str
    summary: dict[str, Any]
    warnings: list[str]


ArtifactType = Literal["json", "csv", "md", "png", "bundle", "other"]


class ArtifactItem(BaseModel):
    id: str
    label: str
    type: ArtifactType
    path: str
    size_bytes: int | None = None
    available: bool = True
    status: str = "available"
    created_at: str | None = None
    run_id: str | None = None


class RunArtifactsResponse(BaseModel):
    run_id: str
    artifacts: list[ArtifactItem]

