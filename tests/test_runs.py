from __future__ import annotations

from pathlib import Path
import json

import pytest

from proto.runs.compare_runs import compare_summary_records, write_run_comparison
from proto.runs.reference import ensure_reference_metadata_schema, freeze_reference_run_if_absent
from proto.runs.status import propose_run_status, validate_status_override

STATUS_LIMITED = "eingeschr\u00e4nkt brauchbar"
TREND_DOWN = "r\u00fcckl\u00e4ufig"


def test_propose_run_status():
    """
    Traceability:
    - PSwR-017
    - ALG-008
    - TV-PSwR-017-001
    """
    assert (
        propose_run_status(
            required_source_availability={"gdelt": True, "ucdp": True, "bridge": True, "context": True},
            data_quality_score=90.0,
            consistency_score=82.0,
            outputs_complete=True,
        )
        == "erfolgreich"
    )
    assert (
        propose_run_status(
            required_source_availability={"gdelt": True, "ucdp": False, "bridge": True, "context": True},
            data_quality_score=66.0,
            consistency_score=62.0,
            outputs_complete=True,
        )
        == STATUS_LIMITED
    )
    assert (
        propose_run_status(
            required_source_availability={"gdelt": False, "ucdp": False, "bridge": False, "context": False},
            data_quality_score=20.0,
            consistency_score=25.0,
            outputs_complete=False,
        )
        == "unbrauchbar"
    )


def test_validate_status_override():
    """
    Traceability:
    - PSwR-017
    - ALG-008
    - TV-PSwR-017-002
    """
    assert validate_status_override("erfolgreich") == "erfolgreich"
    assert validate_status_override("") is None
    assert validate_status_override(None) is None
    with pytest.raises(ValueError):
        validate_status_override("invalid")


def test_compare_summary_records_with_delta_fields():
    """
    Traceability:
    - PSyR-009
    - TV-PSyR-009-001
    """
    current = [
        {"country": "Iran", "cluster": "tension", "cluster_score": 70.0},
        {"country": "Germany", "cluster": "tension", "cluster_score": 30.0},
    ]
    previous = [
        {"country": "Iran", "cluster": "tension", "cluster_score": 65.0},
    ]
    comparison = compare_summary_records(current, previous)
    iran = next(item for item in comparison if item["country"] == "Iran")
    germany = next(item for item in comparison if item["country"] == "Germany")
    assert iran["delta_absolute"] == 5.0
    assert iran["delta_direction"] == "zunehmend"
    assert germany["baseline_score"] is None
    assert germany["delta_direction"] == "kein_vergleich"


def test_compare_summary_records_reports_bidirectional_changes():
    """
    Traceability:
    - PSyR-009
    - TV-PSyR-009-004
    """
    current = [
        {"country": "Iran", "cluster": "tension", "cluster_score": 64.0},
        {"country": "Israel", "cluster": "escalation", "cluster_score": 44.0},
    ]
    baseline = [
        {"country": "Iran", "cluster": "tension", "cluster_score": 60.0},
        {"country": "Israel", "cluster": "escalation", "cluster_score": 47.0},
    ]
    comparison = compare_summary_records(current, baseline)
    iran = next(item for item in comparison if item["country"] == "Iran")
    israel = next(item for item in comparison if item["country"] == "Israel")
    assert iran["delta_direction"] == "zunehmend"
    assert iran["delta_absolute"] == 4.0
    assert israel["delta_direction"] == TREND_DOWN
    assert israel["delta_absolute"] == -3.0


def test_compare_summary_records_sets_relative_and_threshold_directions():
    """
    Traceability:
    - PSyR-009
    - PSwR-017
    - TV-PSyR-009-007
    """
    current = [
        {"country": "Iran", "cluster": "tension", "cluster_score": 100.0},
        {"country": "Israel", "cluster": "tension", "cluster_score": 80.5},
        {"country": "Germany", "cluster": "tension", "cluster_score": 40.5},
        {"country": "Germany", "cluster": "escalation", "cluster_score": 0.4},
    ]
    baseline = [
        {"country": "Iran", "cluster": "tension", "cluster_score": 80.0},
        {"country": "Israel", "cluster": "tension", "cluster_score": 80.0},
        {"country": "Germany", "cluster": "tension", "cluster_score": 41.0},
        {"country": "Germany", "cluster": "escalation", "cluster_score": 0.0},
    ]
    comparison = compare_summary_records(current, baseline)

    iran = next(item for item in comparison if item["country"] == "Iran")
    israel = next(item for item in comparison if item["country"] == "Israel")
    germany_tension = next(
        item
        for item in comparison
        if item["country"] == "Germany" and item["cluster"] == "tension"
    )
    germany_escalation = next(
        item
        for item in comparison
        if item["country"] == "Germany" and item["cluster"] == "escalation"
    )

    assert iran["delta_absolute"] == 20.0
    assert iran["delta_relative_percent"] == 25.0
    assert iran["delta_direction"] == "zunehmend"

    # Boundary: +0.5 is still stable.
    assert israel["delta_absolute"] == 0.5
    assert israel["delta_direction"] == "stabil"

    # Boundary: -0.5 is still stable.
    assert germany_tension["delta_absolute"] == -0.5
    assert germany_tension["delta_direction"] == "stabil"

    # Baseline zero must not emit relative percent.
    assert germany_escalation["delta_relative_percent"] is None
    assert germany_escalation["delta_direction"] == "stabil"


def test_write_run_comparison_payload_contains_run_context(tmp_path: Path):
    """
    Traceability:
    - PSyR-009
    - PSwR-017
    - TV-PSyR-009-002
    """
    current_summary = tmp_path / "current.json"
    baseline_summary = tmp_path / "baseline.json"
    baseline_meta = tmp_path / "baseline_meta.json"
    current_summary.write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":70.0}]',
        encoding="utf-8",
    )
    baseline_summary.write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":65.0}]',
        encoding="utf-8",
    )
    baseline_meta.write_text(
        '{"run_timestamp":"2026-01-01T00:00:00+00:00","run_status":"erfolgreich","proposed_run_status":"erfolgreich"}',
        encoding="utf-8",
    )

    out_path = tmp_path / "run_comparison.json"
    payload = write_run_comparison(
        current_summary_path=current_summary,
        baseline_summary_path=baseline_summary,
        out_path=out_path,
        baseline_label="previous_run",
        current_run_info={
            "run_timestamp": "2026-01-02T00:00:00+00:00",
            "proposed_run_status": "erfolgreich",
            "effective_run_status": "erfolgreich",
            "run_status_overridden": False,
        },
        baseline_metadata_path=baseline_meta,
    )
    assert payload["status"] == "ok"
    assert payload["baseline_label"] == "previous_run"
    assert payload["overview"]["items"] == 1
    parsed = json.loads(out_path.read_text(encoding="utf-8"))
    assert parsed["current_run"]["effective_run_status"] == "erfolgreich"


def test_freeze_reference_run_guards_override_conflict(tmp_path: Path):
    """
    Traceability:
    - PSyR-010
    - PSwR-017
    - ALG-008
    - TV-PSyR-010-001
    """
    run_dir = tmp_path / "run"
    (run_dir / "exports").mkdir(parents=True)
    (run_dir / "exports" / "summary_export.json").write_text("[]", encoding="utf-8")
    (run_dir / "run_metadata.json").write_text(
        '{"run_status":"eingeschr\\u00e4nkt brauchbar","proposed_run_status":"unbrauchbar"}',
        encoding="utf-8",
    )
    reference_dir = tmp_path / "reference"
    action = freeze_reference_run_if_absent(
        current_run_dir=run_dir,
        reference_dir=reference_dir,
        proposed_run_status="unbrauchbar",
        effective_run_status="erfolgreich",
        run_status_overridden=True,
    )
    assert action == "skipped_override_conflict"


def test_ensure_reference_metadata_schema_for_legacy_reference(tmp_path: Path):
    """
    Traceability:
    - PSyR-008
    - PSyR-010
    - TV-PSyR-010-002
    """
    reference_dir = tmp_path / "reference"
    (reference_dir / "exports").mkdir(parents=True)
    (reference_dir / "exports" / "summary_export.json").write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":70.0}]',
        encoding="utf-8",
    )
    metadata_path = ensure_reference_metadata_schema(reference_dir)
    assert metadata_path is not None and metadata_path.exists()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["run_timestamp"] == "unknown_legacy_reference"
    assert metadata["countries"] == ["Iran"]
    assert metadata["metadata_schema_version"] == "legacy_fallback_v1"


def test_ensure_reference_metadata_schema_marks_incomplete_legacy_metadata(tmp_path: Path):
    """
    Traceability:
    - PSyR-008
    - PSyR-010
    - TV-PSyR-010-008
    """
    reference_dir = tmp_path / "reference"
    (reference_dir / "exports").mkdir(parents=True)
    (reference_dir / "exports" / "summary_export.json").write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":66.0}]',
        encoding="utf-8",
    )
    (reference_dir / "run_metadata.json").write_text(
        '{"run_timestamp":"2026-01-01T00:00:00+00:00","run_status":"erfolgreich"}',
        encoding="utf-8",
    )
    metadata_path = ensure_reference_metadata_schema(reference_dir)
    assert metadata_path is not None and metadata_path.exists()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["query_version"] == "unknown"
    assert metadata["metadata_schema_version"] == "legacy_fallback_v1"
    info = json.loads((reference_dir / "reference_info.json").read_text(encoding="utf-8"))
    assert info["legacy_fallback_mode"] is True
    assert info["run_metadata_complete"] is True


def test_ensure_reference_metadata_schema_keeps_complete_current_metadata(tmp_path: Path):
    """
    Traceability:
    - PSyR-008
    - PSyR-010
    - TV-PSyR-010-010
    """
    reference_dir = tmp_path / "reference"
    (reference_dir / "exports").mkdir(parents=True)
    (reference_dir / "exports" / "summary_export.json").write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":66.0}]',
        encoding="utf-8",
    )
    (reference_dir / "run_metadata.json").write_text(
        '{"run_timestamp":"2026-01-05T00:00:00+00:00","countries":["Iran","Israel","Germany"],"short_days":7,"recent_days":30,"baseline_days":365,"query_version":"v1","scoring_version":"v2.1","bridge_file_version":"v1","context_table_version":"v1","proposed_run_status":"erfolgreich","run_status":"erfolgreich","run_status_overridden":false,"metadata_schema_version":"v2"}',
        encoding="utf-8",
    )

    metadata_path = ensure_reference_metadata_schema(reference_dir)
    assert metadata_path is not None and metadata_path.exists()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["run_timestamp"] == "2026-01-05T00:00:00+00:00"
    assert metadata["metadata_schema_version"] == "v2"


def test_freeze_reference_run_creates_reference_info(tmp_path: Path):
    """
    Traceability:
    - PSyR-010
    - PSwR-017
    - TV-PSyR-010-003
    """
    run_dir = tmp_path / "run"
    (run_dir / "exports").mkdir(parents=True)
    (run_dir / "exports" / "summary_export.json").write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":70.0}]',
        encoding="utf-8",
    )
    (run_dir / "run_metadata.json").write_text(
        '{"run_timestamp":"2026-01-02T00:00:00+00:00","run_status":"erfolgreich","proposed_run_status":"erfolgreich","run_status_overridden":false,"query_version":"v1","scoring_version":"v2.1","bridge_file_version":"v1","context_table_version":"v1","countries":["Iran","Israel","Germany"],"short_days":7,"recent_days":30,"baseline_days":365,"metadata_schema_version":"v2"}',
        encoding="utf-8",
    )
    reference_dir = tmp_path / "reference"
    action = freeze_reference_run_if_absent(
        current_run_dir=run_dir,
        reference_dir=reference_dir,
        proposed_run_status="erfolgreich",
        effective_run_status="erfolgreich",
        run_status_overridden=False,
    )
    assert action == "created"
    info = json.loads((reference_dir / "reference_info.json").read_text(encoding="utf-8"))
    assert info["reference_schema_version"] == "v2"
    assert info["reference_action"] == "created"
    assert info["run_metadata_complete"] is True
    assert info["legacy_fallback_mode"] is False


def test_freeze_reference_run_force_refresh_replaces_existing_reference(tmp_path: Path):
    """
    Traceability:
    - PSyR-010
    - PSwR-017
    - ALG-008
    - TV-PSyR-010-006
    """
    run_dir = tmp_path / "run"
    (run_dir / "exports").mkdir(parents=True)
    (run_dir / "exports" / "summary_export.json").write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":75.0}]',
        encoding="utf-8",
    )
    (run_dir / "run_metadata.json").write_text(
        '{"run_timestamp":"2026-01-15T00:00:00+00:00","run_status":"erfolgreich","proposed_run_status":"erfolgreich","run_status_overridden":false,"query_version":"v1","scoring_version":"v2.1","bridge_file_version":"v1","context_table_version":"v1","countries":["Iran","Israel","Germany"],"short_days":7,"recent_days":30,"baseline_days":365,"metadata_schema_version":"v2"}',
        encoding="utf-8",
    )

    reference_dir = tmp_path / "reference"
    (reference_dir / "exports").mkdir(parents=True)
    (reference_dir / "exports" / "summary_export.json").write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":60.0}]',
        encoding="utf-8",
    )
    (reference_dir / "run_metadata.json").write_text(
        '{"run_timestamp":"2026-01-01T00:00:00+00:00","run_status":"erfolgreich","proposed_run_status":"erfolgreich"}',
        encoding="utf-8",
    )

    action = freeze_reference_run_if_absent(
        current_run_dir=run_dir,
        reference_dir=reference_dir,
        proposed_run_status="erfolgreich",
        effective_run_status="erfolgreich",
        run_status_overridden=False,
        force_refresh=True,
    )
    assert action == "refreshed_forced"
    refreshed_metadata = json.loads((reference_dir / "run_metadata.json").read_text(encoding="utf-8"))
    assert refreshed_metadata["run_timestamp"] == "2026-01-15T00:00:00+00:00"
    info = json.loads((reference_dir / "reference_info.json").read_text(encoding="utf-8"))
    assert info["reference_action"] == "refreshed_forced"


def test_freeze_reference_run_migrates_legacy_reference(tmp_path: Path):
    """
    Traceability:
    - PSyR-010
    - PSwR-017
    - TV-PSyR-010-005
    """
    run_dir = tmp_path / "run"
    (run_dir / "exports").mkdir(parents=True)
    (run_dir / "exports" / "summary_export.json").write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":71.0}]',
        encoding="utf-8",
    )
    (run_dir / "run_metadata.json").write_text(
        '{"run_timestamp":"2026-01-10T00:00:00+00:00","run_status":"erfolgreich","proposed_run_status":"erfolgreich","run_status_overridden":false,"query_version":"v1","scoring_version":"v2.1","bridge_file_version":"v1","context_table_version":"v1","countries":["Iran","Israel","Germany"],"short_days":7,"recent_days":30,"baseline_days":365,"metadata_schema_version":"v2"}',
        encoding="utf-8",
    )

    reference_dir = tmp_path / "reference"
    (reference_dir / "exports").mkdir(parents=True)
    (reference_dir / "exports" / "summary_export.json").write_text(
        '[{"country":"Iran","cluster":"tension","cluster_score":60.0}]',
        encoding="utf-8",
    )
    (reference_dir / "run_metadata.json").write_text(
        '{"run_timestamp":"unknown_legacy_reference","run_status":"unbekannt"}',
        encoding="utf-8",
    )

    action = freeze_reference_run_if_absent(
        current_run_dir=run_dir,
        reference_dir=reference_dir,
        proposed_run_status="erfolgreich",
        effective_run_status="erfolgreich",
        run_status_overridden=False,
    )
    assert action == "migrated_legacy_to_current"
    migrated = json.loads((reference_dir / "run_metadata.json").read_text(encoding="utf-8"))
    assert migrated["run_timestamp"] == "2026-01-10T00:00:00+00:00"
    assert migrated["metadata_schema_version"] == "v2"
