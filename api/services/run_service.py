from __future__ import annotations

"""
Run orchestration service for API endpoints.

Traceability:
- AP-04
- AP-05
- AP-08
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
from typing import Any
from uuid import uuid4
import zipfile

from proto.common import canonical_country
from proto.runs.compare_runs import load_summary_records

from api.schemas.runs import (
    ApiRunError,
    ArtifactItem,
    RunCreateRequest,
    RunCreateResponse,
    RunDetailResponse,
    RunRecord,
    RunsResponse,
    RunStatusResponse,
    RunSummaryResponse,
    RunStatusProgress,
    RunArtifactsResponse,
)
from api.services.config_service import get_pipeline_config
from api.services.errors import ApiServiceError

_RUNS_LOCK = threading.Lock()
_RUNS: dict[str, "_RunJob"] = {}
_ACTIVE_RUN_ID: str | None = None


@dataclass(slots=True)
class _RunJob:
    run_id: str
    request: RunCreateRequest
    created_at: str
    status: str = "queued"
    started_at: str | None = None
    finished_at: str | None = None
    progress_percent: int | None = 0
    warning_count: int = 0
    error: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    summary: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    artifacts: list[ArtifactItem] = field(default_factory=list)
    artifact_files: dict[str, Path] = field(default_factory=dict)
    archive_dir: Path | None = None


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _is_truthy_env(name: str) -> bool:
    value = os.environ.get(name, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _sanitize_pipeline_status(value: str | None) -> str:
    if not value:
        return ""
    lowered = value.strip().lower()
    return (
        lowered.replace("ae", "a")
        .replace("oe", "o")
        .replace("ue", "u")
        .replace("ß", "ss")
        .replace("ä", "a")
        .replace("ö", "o")
        .replace("ü", "u")
    )


def _map_pipeline_status_to_api(value: str | None) -> str:
    normalized = _sanitize_pipeline_status(value)
    if normalized == "erfolgreich":
        return "completed"
    if "eingeschrankt brauchbar" in normalized:
        return "completed"
    if normalized == "unbrauchbar":
        return "failed"
    return "completed"


def _execute_pipeline_process() -> subprocess.CompletedProcess[str]:
    """
    Execute the existing pipeline as subprocess to avoid blocking request threads.

    Traceability:
    - AP-05
    """
    return subprocess.run(
        [sys.executable, "-m", "proto.pipeline.run_proto"],
        capture_output=True,
        text=True,
        check=False,
    )


def _summary_export_path(run_dir: Path) -> Path | None:
    candidates = [
        run_dir / "exports" / "snapshot" / "summary_export.json",
        run_dir / "exports" / "summary_export.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _archive_current_run(run_id: str) -> Path:
    config = get_pipeline_config()
    current_run_dir = config.report_dir / "current_run"
    if not current_run_dir.exists():
        raise ApiServiceError(
            code="run_execution_failed",
            message="Pipeline completed but current run directory was not found.",
            status_code=500,
        )
    archive_root = config.report_dir / "api_archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    target_dir = archive_root / run_id
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(current_run_dir, target_dir)
    return target_dir


def _artifact_type_for_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"
    if suffix == ".md":
        return "md"
    if suffix == ".png":
        return "png"
    return "other"


def _collect_artifacts(run_id: str, run_dir: Path) -> tuple[list[ArtifactItem], dict[str, Path]]:
    artifact_specs: list[tuple[str, str, Path]] = []
    summary_path = _summary_export_path(run_dir)
    if summary_path is not None:
        artifact_specs.append(("summary_export", "Summary Export", summary_path))

    file_candidates = [
        ("scores_export", "Scores Export", run_dir / "exports" / "snapshot" / "scores_export.csv"),
        ("features_export", "Features Export", run_dir / "exports" / "snapshot" / "features_export.csv"),
        ("handout", "Handout", run_dir / "handout.md"),
        ("run_comparison", "Run Comparison", run_dir / "run_comparison.json"),
        ("reference_comparison", "Reference Comparison", run_dir / "reference_comparison.json"),
        ("validation_summary", "Validation Summary", run_dir / "exports" / "fusion" / "validation_summary.json"),
    ]
    for artifact_id, label, path in file_candidates:
        if path.exists():
            artifact_specs.append((artifact_id, label, path))

    artifacts: list[ArtifactItem] = []
    files: dict[str, Path] = {}
    created_at = _utc_now()
    for artifact_id, label, path in artifact_specs:
        files[artifact_id] = path
        artifacts.append(
            ArtifactItem(
                id=artifact_id,
                label=label,
                type=_artifact_type_for_file(path),  # type: ignore[arg-type]
                path=f"/api/v1/runs/{run_id}/artifacts/{artifact_id}/download",
                size_bytes=path.stat().st_size,
                available=True,
                status="available",
                created_at=created_at,
                run_id=run_id,
            )
        )

    artifacts.append(
        ArtifactItem(
            id="bundle",
            label="Review Bundle",
            type="bundle",
            path=f"/api/v1/runs/{run_id}/bundle",
            available=True,
            status="available",
            created_at=created_at,
            run_id=run_id,
        )
    )
    return artifacts, files


def _build_summary_payload(run_dir: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    summary_path = _summary_export_path(run_dir)
    if summary_path is None:
        warnings.append("summary_export is not available for this run.")
        return {"records": []}, warnings

    records = load_summary_records(summary_path)
    summary_payload: dict[str, Any] = {"records": records}
    if records:
        try:
            top_record = max(
                records,
                key=lambda item: float(item.get("cluster_score", -1.0)),
            )
            summary_payload["top_country"] = top_record.get("country")
            summary_payload["top_cluster"] = top_record.get("cluster")
            summary_payload["top_score"] = top_record.get("cluster_score")
        except Exception:
            warnings.append("summary records exist but top-country derivation failed.")
    return summary_payload, warnings


def _run_record_from_job(job: _RunJob) -> RunRecord:
    return RunRecord(
        run_id=job.run_id,
        status=job.status,  # type: ignore[arg-type]
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        countries=list(job.request.countries),
        progress_percent=job.progress_percent,
        warning_count=job.warning_count,
        error=ApiRunError(**job.error) if job.error else None,
    )


def _set_job_failed(job: _RunJob, *, message: str, details: Any | None = None) -> None:
    job.status = "failed"
    job.progress_percent = 100
    job.finished_at = _utc_now()
    job.error = {
        "code": "run_execution_failed",
        "message": message,
        "details": details,
    }


def _execute_job(run_id: str) -> None:
    global _ACTIVE_RUN_ID
    with _RUNS_LOCK:
        job = _RUNS.get(run_id)
        if job is None:
            return
        job.status = "running"
        job.started_at = _utc_now()
        job.progress_percent = 35

    try:
        completed_process = _execute_pipeline_process()
    except Exception as exc:  # pragma: no cover - defensive fallback
        with _RUNS_LOCK:
            latest_job = _RUNS.get(run_id)
            if latest_job is not None:
                _set_job_failed(
                    latest_job,
                    message="Pipeline execution crashed before completion.",
                    details={"exception": str(exc)},
                )
        return
    finally:
        with _RUNS_LOCK:
            if _ACTIVE_RUN_ID == run_id:
                _ACTIVE_RUN_ID = None

    with _RUNS_LOCK:
        job = _RUNS.get(run_id)
        if job is None:
            return

    if completed_process.returncode != 0:
        with _RUNS_LOCK:
            latest_job = _RUNS.get(run_id)
            if latest_job is not None:
                _set_job_failed(
                    latest_job,
                    message="Pipeline process returned non-zero exit code.",
                    details={
                        "returncode": completed_process.returncode,
                        "stderr_tail": completed_process.stderr[-2000:],
                    },
                )
        return

    try:
        archive_dir = _archive_current_run(run_id)
        metadata = _load_json(archive_dir / "run_metadata.json")
        summary_payload, summary_warnings = _build_summary_payload(archive_dir)
        artifacts, artifact_files = _collect_artifacts(run_id, archive_dir)
        pipeline_status = metadata.get("run_status")
        api_status = _map_pipeline_status_to_api(str(pipeline_status) if pipeline_status else None)
    except ApiServiceError as exc:
        with _RUNS_LOCK:
            latest_job = _RUNS.get(run_id)
            if latest_job is not None:
                _set_job_failed(
                    latest_job,
                    message=exc.message,
                    details=exc.details,
                )
        return
    except Exception as exc:  # pragma: no cover - defensive fallback
        with _RUNS_LOCK:
            latest_job = _RUNS.get(run_id)
            if latest_job is not None:
                _set_job_failed(
                    latest_job,
                    message="Pipeline completed but artifact hydration failed.",
                    details={"exception": str(exc)},
                )
        return

    with _RUNS_LOCK:
        latest_job = _RUNS.get(run_id)
        if latest_job is None:
            return
        latest_job.archive_dir = archive_dir
        latest_job.metadata = metadata or None
        latest_job.summary = summary_payload
        latest_job.warnings = summary_warnings
        latest_job.artifacts = artifacts
        latest_job.artifact_files = artifact_files
        latest_job.warning_count = len(summary_warnings)
        latest_job.status = api_status
        latest_job.progress_percent = 100
        latest_job.finished_at = _utc_now()
        if api_status == "failed":
            latest_job.error = {
                "code": "run_execution_failed",
                "message": "Pipeline reported run status 'unbrauchbar'.",
                "details": {"pipeline_status": pipeline_status},
            }


def _validate_create_payload(payload: RunCreateRequest) -> RunCreateRequest:
    config = get_pipeline_config()
    allowed_countries = {country.lower(): country for country in config.countries}
    allowed_layers = {layer.lower(): layer for layer in config.v3_1.fusion.groups}

    normalized_countries: list[str] = []
    invalid_countries: list[str] = []
    for value in payload.countries:
        candidate = canonical_country(value)
        resolved = allowed_countries.get(candidate.lower())
        if resolved is None:
            invalid_countries.append(value)
        else:
            normalized_countries.append(resolved)

    normalized_layers: list[str] = []
    invalid_layers: list[str] = []
    for value in payload.layers:
        resolved = allowed_layers.get(value.strip().lower())
        if resolved is None:
            invalid_layers.append(value)
        else:
            normalized_layers.append(resolved)

    if invalid_countries or invalid_layers:
        raise ApiServiceError(
            code="validation_error",
            message="Run payload contains unsupported countries or layers.",
            status_code=422,
            details={
                "invalid_countries": invalid_countries,
                "invalid_layers": invalid_layers,
                "allowed_countries": config.countries,
                "allowed_layers": config.v3_1.fusion.groups,
            },
        )

    if payload.horizon_days not in {config.short_days, config.recent_days, config.baseline_days}:
        raise ApiServiceError(
            code="validation_error",
            message="Unsupported horizon_days for MVP run execution.",
            status_code=422,
            details={
                "horizon_days": payload.horizon_days,
                "supported_horizons": [config.short_days, config.recent_days, config.baseline_days],
            },
        )

    return RunCreateRequest(
        countries=sorted(set(normalized_countries)),
        horizon_days=payload.horizon_days,
        layers=sorted(set(normalized_layers)),
        advanced=payload.advanced,
    )


def create_run(payload: RunCreateRequest) -> RunCreateResponse:
    """
    Create and start a run asynchronously.

    Traceability:
    - AP-04
    - AP-05
    """
    global _ACTIVE_RUN_ID
    validated = _validate_create_payload(payload)
    with _RUNS_LOCK:
        if _ACTIVE_RUN_ID:
            active = _RUNS.get(_ACTIVE_RUN_ID)
            if active is not None and active.status in {"queued", "running"}:
                raise ApiServiceError(
                    code="run_execution_failed",
                    message="Another run is currently active. Retry after completion.",
                    status_code=409,
                    details={"active_run_id": active.run_id},
                )

        created_at = _utc_now()
        run_id = f"run_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
        job = _RunJob(
            run_id=run_id,
            request=validated,
            created_at=created_at,
            status="queued",
            progress_percent=5,
        )
        _RUNS[run_id] = job
        _ACTIVE_RUN_ID = run_id

    if _is_truthy_env("API_RUN_SYNC_EXECUTION"):
        _execute_job(run_id)
    else:
        thread = threading.Thread(target=_execute_job, args=(run_id,), daemon=True)
        thread.start()

    with _RUNS_LOCK:
        latest = _RUNS[run_id]
        return RunCreateResponse(
            run_id=latest.run_id,
            status=latest.status,  # type: ignore[arg-type]
            created_at=latest.created_at,
        )


def list_runs() -> RunsResponse:
    with _RUNS_LOCK:
        runs = [_run_record_from_job(job) for job in _RUNS.values()]
    runs.sort(key=lambda item: item.created_at, reverse=True)
    return RunsResponse(runs=runs)


def _get_job_or_raise(run_id: str) -> _RunJob:
    with _RUNS_LOCK:
        job = _RUNS.get(run_id)
        if job is None:
            raise ApiServiceError(
                code="run_not_found",
                message=f"Run '{run_id}' does not exist.",
                status_code=404,
            )
        return job


def get_run_detail(run_id: str) -> RunDetailResponse:
    job = _get_job_or_raise(run_id)
    return RunDetailResponse(
        run=_run_record_from_job(job),
        metadata=job.metadata,
    )


def get_run_status(run_id: str) -> RunStatusResponse:
    job = _get_job_or_raise(run_id)
    progress = RunStatusProgress(
        phase="queued" if job.status == "queued" else "pipeline_execution" if job.status == "running" else "completed",
        percent=job.progress_percent,
        message="Run queued" if job.status == "queued" else "Run in progress" if job.status == "running" else "Run finished",
    )
    return RunStatusResponse(
        run_id=run_id,
        status=job.status,  # type: ignore[arg-type]
        progress=progress,
        started_at=job.started_at,
        finished_at=job.finished_at,
        updated_at=_utc_now(),
        error=ApiRunError(**job.error) if job.error else None,
    )


def get_run_summary(run_id: str) -> RunSummaryResponse:
    job = _get_job_or_raise(run_id)
    return RunSummaryResponse(
        run_id=run_id,
        summary=job.summary if job.summary else {"records": []},
        warnings=list(job.warnings),
    )


def get_run_artifacts(run_id: str) -> RunArtifactsResponse:
    job = _get_job_or_raise(run_id)
    return RunArtifactsResponse(
        run_id=run_id,
        artifacts=list(job.artifacts),
    )


def get_artifact_file(run_id: str, artifact_id: str) -> Path:
    job = _get_job_or_raise(run_id)
    path = job.artifact_files.get(artifact_id)
    if path is None or not path.exists():
        raise ApiServiceError(
            code="artifact_not_found",
            message=f"Artifact '{artifact_id}' for run '{run_id}' was not found.",
            status_code=404,
        )
    return path


def get_bundle_file(run_id: str) -> Path:
    job = _get_job_or_raise(run_id)
    if job.archive_dir is None or not job.archive_dir.exists():
        raise ApiServiceError(
            code="run_execution_failed",
            message="Run artifacts are not available yet.",
            status_code=409,
            details={"run_id": run_id, "status": job.status},
        )
    bundle_path = job.archive_dir / f"bundle_{run_id}.zip"
    if bundle_path.exists():
        return bundle_path

    with zipfile.ZipFile(bundle_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(job.archive_dir.rglob("*")):
            if path.is_dir():
                continue
            if path == bundle_path:
                continue
            archive.write(path, arcname=path.relative_to(job.archive_dir))
    return bundle_path


def reset_state_for_tests() -> None:
    """
    Reset in-memory run state.

    Traceability:
    - AP-09
    """
    global _ACTIVE_RUN_ID
    with _RUNS_LOCK:
        _RUNS.clear()
        _ACTIVE_RUN_ID = None
