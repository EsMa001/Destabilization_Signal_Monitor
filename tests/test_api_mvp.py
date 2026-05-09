from __future__ import annotations

"""
API MVP tests.

Traceability:
- AP-09
"""

from pathlib import Path
import shutil
import subprocess

from fastapi.testclient import TestClient
import pytest

from api.main import app
from api.services import run_service
from api.services.config_service import get_pipeline_config


@pytest.fixture(autouse=True)
def reset_run_state(monkeypatch: pytest.MonkeyPatch):
    run_service.reset_state_for_tests()
    config = get_pipeline_config()
    archive_root = config.report_dir / "api_archive"
    if archive_root.exists():
        shutil.rmtree(archive_root)
    monkeypatch.setenv("API_RUN_SYNC_EXECUTION", "1")
    yield
    run_service.reset_state_for_tests()
    if archive_root.exists():
        shutil.rmtree(archive_root)


def _write_fake_pipeline_outputs() -> None:
    config = get_pipeline_config()
    current_run = config.report_dir / "current_run"
    snapshot_export = current_run / "exports" / "snapshot"
    snapshot_export.mkdir(parents=True, exist_ok=True)

    (current_run / "run_metadata.json").write_text(
        """
{
  "run_timestamp": "2026-04-16T12:00:00+00:00",
  "countries": ["Germany", "Iran"],
  "short_days": 7,
  "recent_days": 30,
  "baseline_days": 356,
  "query_version": "v1",
  "scoring_version": "v4.3",
  "bridge_file_version": "v1",
  "context_table_version": "v1",
  "proposed_run_status": "erfolgreich",
  "run_status": "erfolgreich",
  "run_status_overridden": false
}
""".strip(),
        encoding="utf-8",
    )
    (snapshot_export / "summary_export.json").write_text(
        """
[
  {"country": "Iran", "cluster": "tension", "cluster_score": 64.2},
  {"country": "Germany", "cluster": "tension", "cluster_score": 31.5}
]
""".strip(),
        encoding="utf-8",
    )
    (snapshot_export / "scores_export.csv").write_text(
        "country,cluster,score\nIran,tension,64.2\n",
        encoding="utf-8",
    )
    (snapshot_export / "features_export.csv").write_text(
        "country,feature,value\nIran,gdelt_count,12\n",
        encoding="utf-8",
    )
    (current_run / "run_comparison.json").write_text('{"status":"ok"}', encoding="utf-8")
    (current_run / "reference_comparison.json").write_text('{"status":"ok"}', encoding="utf-8")
    (current_run / "handout.md").write_text("# Fake handout", encoding="utf-8")


def _fake_pipeline_process() -> subprocess.CompletedProcess[str]:
    _write_fake_pipeline_outputs()
    return subprocess.CompletedProcess(
        args=["python", "-m", "proto.pipeline.run_proto"],
        returncode=0,
        stdout="ok",
        stderr="",
    )


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["api_version"] == "v1"


def test_info_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    payload = response.json()
    assert payload["api_version"] == "v1"
    assert payload["project_name"] == "country-destabilization-proto"


def test_options_endpoints() -> None:
    client = TestClient(app)
    countries = client.get("/api/v1/options/countries")
    layers = client.get("/api/v1/options/layers")
    template = client.get("/api/v1/config/template")

    assert countries.status_code == 200
    assert layers.status_code == 200
    assert template.status_code == 200
    assert len(countries.json()["countries"]) >= 3
    assert len(layers.json()["layers"]) >= 3
    assert template.json()["defaults"]["horizon_days"] == 30


def test_run_creation_and_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run_service, "_execute_pipeline_process", _fake_pipeline_process)
    client = TestClient(app)
    create_response = client.post(
        "/api/v1/runs",
        json={
            "countries": ["Germany", "Iran"],
            "horizon_days": 30,
            "layers": ["event", "governance"],
        },
    )
    assert create_response.status_code == 201
    run_id = create_response.json()["run_id"]

    list_response = client.get("/api/v1/runs")
    assert list_response.status_code == 200
    assert any(entry["run_id"] == run_id for entry in list_response.json()["runs"])

    status_response = client.get(f"/api/v1/runs/{run_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] in {"completed", "failed", "running", "queued"}

    summary_response = client.get(f"/api/v1/runs/{run_id}/summary")
    assert summary_response.status_code == 200
    assert "records" in summary_response.json()["summary"]


def test_unknown_run_id_returns_standard_error() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/runs/does_not_exist/status")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "run_not_found"


def test_unknown_artifact_returns_standard_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run_service, "_execute_pipeline_process", _fake_pipeline_process)
    client = TestClient(app)
    create_response = client.post(
        "/api/v1/runs",
        json={
            "countries": ["Germany", "Iran"],
            "horizon_days": 30,
            "layers": ["event", "governance"],
        },
    )
    run_id = create_response.json()["run_id"]

    response = client.get(f"/api/v1/runs/{run_id}/artifacts/not_existing/download")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "artifact_not_found"
