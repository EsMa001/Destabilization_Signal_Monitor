from __future__ import annotations

"""
Traceability:
- PSyR-010
- PSwR-017
- ProtoRunbook: Referenz-Run
"""

from pathlib import Path
from datetime import UTC, datetime
import json
import shutil
from typing import Any

from proto.runs.compare_runs import load_summary_records

REFERENCE_SCHEMA_VERSION = "v2"
RUN_METADATA_SCHEMA_VERSION = "v2"
LEGACY_METADATA_SCHEMA_VERSION = "legacy_fallback_v1"
LEGACY_REFERENCE_TIMESTAMP = "unknown_legacy_reference"
REQUIRED_RUN_METADATA_KEYS = (
    "run_timestamp",
    "countries",
    "short_days",
    "recent_days",
    "baseline_days",
    "query_version",
    "scoring_version",
    "bridge_file_version",
    "context_table_version",
    "proposed_run_status",
    "run_status",
    "run_status_overridden",
)


def _summary_path_candidates(base_dir: Path) -> list[Path]:
    # Traceability:
    # - PSyR-010
    # - PSwR-017
    # - ALG-008
    # - PSyR-008
    return [
        base_dir / "exports" / "snapshot" / "summary_export.json",
        base_dir / "exports" / "summary_export.json",
    ]


def _resolve_summary_path(base_dir: Path) -> Path | None:
    # Traceability:
    # - PSyR-010
    # - PSwR-017
    # - ALG-008
    # - PSyR-008
    return next((path for path in _summary_path_candidates(base_dir) if path.exists()), None)


def freeze_reference_run_if_absent(
    *,
    current_run_dir: Path,
    reference_dir: Path,
    proposed_run_status: str,
    effective_run_status: str,
    run_status_overridden: bool,
    force_refresh: bool = False,
) -> str:
    """
    Freeze first clean successful standard run as reference.

    Traceability:
    - PSyR-010
    - ALG-008
    - OI-006
    """
    if effective_run_status != "erfolgreich":
        return "skipped_not_successful"
    if run_status_overridden and proposed_run_status != "erfolgreich":
        return "skipped_override_conflict"

    summary_path = _resolve_summary_path(current_run_dir)
    metadata_path = current_run_dir / "run_metadata.json"
    if summary_path is None or not metadata_path.exists():
        return "skipped_missing_artifacts"

    reference_summary = _resolve_summary_path(reference_dir)
    if reference_summary is not None:
        if force_refresh:
            if reference_dir.exists():
                shutil.rmtree(reference_dir)
            shutil.copytree(current_run_dir, reference_dir)
            _write_reference_info(reference_dir, action="refreshed_forced")
            return "refreshed_forced"

        reference_metadata = ensure_reference_metadata_schema(reference_dir)
        reference_payload = _load_json_payload(reference_metadata) if reference_metadata else {}
        if reference_payload and _is_legacy_reference_metadata(reference_payload):
            shutil.rmtree(reference_dir)
            shutil.copytree(current_run_dir, reference_dir)
            _write_reference_info(reference_dir, action="migrated_legacy_to_current")
            return "migrated_legacy_to_current"
        _write_reference_info(reference_dir, action="already_exists")
        return "already_exists"

    if reference_dir.exists():
        shutil.rmtree(reference_dir)
    shutil.copytree(current_run_dir, reference_dir)
    _write_reference_info(reference_dir, action="created")
    return "created"


def ensure_reference_metadata_schema(reference_dir: Path) -> Path | None:
    """
    Ensure legacy reference runs have a metadata file with required keys.

    Traceability:
    - PSyR-008
    - PSyR-010
    """
    summary_path = _resolve_summary_path(reference_dir)
    metadata_path = reference_dir / "run_metadata.json"
    if summary_path is None:
        return None

    summary = load_summary_records(summary_path)
    countries = sorted({entry.get("country", "") for entry in summary if entry.get("country")})
    legacy_placeholder = _legacy_reference_placeholder(countries)
    metadata_payload = _load_json_payload(metadata_path) if metadata_path.exists() else {}
    changed = not metadata_path.exists()

    if not metadata_payload:
        metadata_payload = legacy_placeholder
        changed = True
    else:
        missing_keys = [key for key in REQUIRED_RUN_METADATA_KEYS if key not in metadata_payload]
        if missing_keys:
            for key in missing_keys:
                metadata_payload[key] = legacy_placeholder[key]
            metadata_payload["metadata_schema_version"] = LEGACY_METADATA_SCHEMA_VERSION
            changed = True

        if not isinstance(metadata_payload.get("countries"), list) or not metadata_payload.get("countries"):
            metadata_payload["countries"] = countries
            changed = True

        schema_version = str(metadata_payload.get("metadata_schema_version", "")).strip()
        if not schema_version:
            if metadata_payload.get("run_timestamp") == LEGACY_REFERENCE_TIMESTAMP:
                metadata_payload["metadata_schema_version"] = LEGACY_METADATA_SCHEMA_VERSION
            elif _is_complete_run_metadata(metadata_payload):
                metadata_payload["metadata_schema_version"] = RUN_METADATA_SCHEMA_VERSION
            else:
                metadata_payload["metadata_schema_version"] = LEGACY_METADATA_SCHEMA_VERSION
            changed = True

    if changed:
        metadata_path.write_text(
            json.dumps(metadata_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        action = "legacy_fallback_metadata_created" if _is_legacy_reference_metadata(metadata_payload) else "metadata_schema_normalized"
        _write_reference_info(reference_dir, action=action)
    return metadata_path


def _write_reference_info(reference_dir: Path, *, action: str) -> None:
    """
    Persist full reference documentation metadata.

    Traceability:
    - PSyR-010
    - PSwR-017
    """
    metadata_path = reference_dir / "run_metadata.json"
    summary_path = _resolve_summary_path(reference_dir)
    metadata_payload = _load_json_payload(metadata_path) if metadata_path.exists() else {}
    missing_metadata_keys = [key for key in REQUIRED_RUN_METADATA_KEYS if key not in metadata_payload]
    run_metadata_complete = len(missing_metadata_keys) == 0
    legacy_fallback_mode = _is_legacy_reference_metadata(metadata_payload)

    info_payload = {
        "reference_schema_version": REFERENCE_SCHEMA_VERSION,
        "reference_info_timestamp": datetime.now(UTC).isoformat(),
        "reference_action": action,
        "reference_dir": str(reference_dir.as_posix()),
        "summary_present": summary_path is not None and summary_path.exists(),
        "summary_path": summary_path.as_posix() if summary_path else None,
        "metadata_schema_version": metadata_payload.get("metadata_schema_version"),
        "required_run_metadata_keys": list(REQUIRED_RUN_METADATA_KEYS),
        "missing_run_metadata_keys": missing_metadata_keys,
        "run_metadata_complete": run_metadata_complete,
        "legacy_fallback_mode": legacy_fallback_mode,
        "run_timestamp": metadata_payload.get("run_timestamp"),
        "proposed_run_status": metadata_payload.get("proposed_run_status"),
        "effective_run_status": metadata_payload.get("run_status"),
        "run_status_overridden": metadata_payload.get("run_status_overridden"),
        "query_version": metadata_payload.get("query_version"),
        "scoring_version": metadata_payload.get("scoring_version"),
        "bridge_file_version": metadata_payload.get("bridge_file_version"),
        "context_table_version": metadata_payload.get("context_table_version"),
        "countries": metadata_payload.get("countries", []),
        "time_windows": {
            "short_days": metadata_payload.get("short_days"),
            "recent_days": metadata_payload.get("recent_days"),
            "baseline_days": metadata_payload.get("baseline_days"),
        },
        "run_metadata": metadata_payload,
    }
    (reference_dir / "reference_info.json").write_text(
        json.dumps(info_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_json_payload(path: Path) -> dict[str, Any]:
    # Traceability:
    # - PSyR-010
    # - PSwR-017
    # - ALG-008
    # - PSyR-008
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def _legacy_reference_placeholder(countries: list[str]) -> dict[str, Any]:
    # Traceability:
    # - PSyR-010
    # - PSwR-017
    # - ALG-008
    # - PSyR-008
    return {
        "run_timestamp": LEGACY_REFERENCE_TIMESTAMP,
        "countries": countries,
        "short_days": 7,
        "recent_days": 30,
        "baseline_days": 365,
        "query_version": "unknown",
        "scoring_version": "unknown",
        "bridge_file_version": "unknown",
        "context_table_version": "unknown",
        "metadata_schema_version": LEGACY_METADATA_SCHEMA_VERSION,
        "proposed_run_status": "unbekannt",
        "run_status": "unbekannt",
        "run_status_overridden": False,
    }


def _is_complete_run_metadata(payload: dict[str, Any]) -> bool:
    # Traceability:
    # - PSyR-010
    # - PSwR-017
    # - ALG-008
    # - PSyR-008
    return all(key in payload for key in REQUIRED_RUN_METADATA_KEYS)


def _is_legacy_reference_metadata(payload: dict[str, Any]) -> bool:
    # Traceability:
    # - PSyR-010
    # - PSwR-017
    # - ALG-008
    # - PSyR-008
    if not payload:
        return False
    if payload.get("run_timestamp") == LEGACY_REFERENCE_TIMESTAMP:
        return True
    schema_version = str(payload.get("metadata_schema_version", "")).strip()
    return bool(schema_version) and schema_version != RUN_METADATA_SCHEMA_VERSION
