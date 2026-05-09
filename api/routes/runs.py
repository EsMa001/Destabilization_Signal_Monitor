from __future__ import annotations

"""
Run routes.

Traceability:
- AP-04
- AP-05
"""

from fastapi import APIRouter, status
from fastapi.responses import FileResponse

from api.schemas.runs import (
    RunArtifactsResponse,
    RunCreateRequest,
    RunCreateResponse,
    RunDetailResponse,
    RunsResponse,
    RunStatusResponse,
    RunSummaryResponse,
)
from api.services.run_service import (
    create_run,
    get_artifact_file,
    get_bundle_file,
    get_run_artifacts,
    get_run_detail,
    get_run_status,
    get_run_summary,
    list_runs,
)

router = APIRouter()


@router.post("/runs", response_model=RunCreateResponse, status_code=status.HTTP_201_CREATED)
def post_run(payload: RunCreateRequest) -> RunCreateResponse:
    return create_run(payload)


@router.get("/runs", response_model=RunsResponse)
def get_runs() -> RunsResponse:
    return list_runs()


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
def get_run(run_id: str) -> RunDetailResponse:
    return get_run_detail(run_id)


@router.get("/runs/{run_id}/status", response_model=RunStatusResponse)
def get_run_status_route(run_id: str) -> RunStatusResponse:
    return get_run_status(run_id)


@router.get("/runs/{run_id}/summary", response_model=RunSummaryResponse)
def get_run_summary_route(run_id: str) -> RunSummaryResponse:
    return get_run_summary(run_id)


@router.get("/runs/{run_id}/artifacts", response_model=RunArtifactsResponse)
def get_run_artifacts_route(run_id: str) -> RunArtifactsResponse:
    return get_run_artifacts(run_id)


@router.get("/runs/{run_id}/bundle")
def get_run_bundle_route(run_id: str) -> FileResponse:
    bundle_path = get_bundle_file(run_id)
    return FileResponse(
        path=bundle_path,
        filename=bundle_path.name,
        media_type="application/zip",
    )


@router.get("/runs/{run_id}/artifacts/{artifact_id}/download")
def get_run_artifact_download_route(run_id: str, artifact_id: str) -> FileResponse:
    artifact_path = get_artifact_file(run_id, artifact_id)
    return FileResponse(
        path=artifact_path,
        filename=artifact_path.name,
    )

