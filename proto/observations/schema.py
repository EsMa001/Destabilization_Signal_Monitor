from __future__ import annotations

"""
Validation helpers for canonical observations.

Traceability:
- PSyR-018
- PSwR-036
- PSwR-037
- PSwR-038
- PSwR-044
- PM-016
"""

from proto.observations.models import ObservationRecord

VALID_LAYERS = {
    "Event",
    "Narrative",
    "Governance",
    "Market/Food",
    "Shock",
    "Displacement",
    "Structural",
}


class ObservationValidationError(ValueError):
    """
    Raised when a canonical observation violates required schema constraints.

    Traceability:
    - PSwR-036
    - PSwR-037
    """


def _require_non_empty(value: str, *, field_name: str) -> None:
    if not value.strip():
        raise ObservationValidationError(f"observation field {field_name!r} must be non-empty")


def validate_observation_record(record: ObservationRecord) -> None:
    """
    Validate one canonical observation.

    Traceability:
    - PSwR-036
    - PSwR-037
    - PSwR-038
    - PSwR-044
    """
    _require_non_empty(record.source_id, field_name="source_id")
    _require_non_empty(record.layer, field_name="layer")
    _require_non_empty(record.signal_family, field_name="signal_family")
    _require_non_empty(record.country, field_name="country")
    _require_non_empty(record.unit, field_name="unit")
    _require_non_empty(record.provenance, field_name="provenance")

    if record.layer not in VALID_LAYERS:
        raise ObservationValidationError(
            f"observation layer {record.layer!r} is invalid; expected one of {sorted(VALID_LAYERS)}"
        )
    if record.period_start > record.period_end:
        raise ObservationValidationError("observation period_start must be <= period_end")
    if not (0.0 <= record.normalized_value <= 1.0):
        raise ObservationValidationError("observation normalized_value must be in [0, 1]")
    if not (0.0 <= record.quality_completeness <= 1.0):
        raise ObservationValidationError("observation quality_completeness must be in [0, 1]")


def validate_observation_records(records: list[ObservationRecord]) -> None:
    """
    Validate canonical observation list.

    Traceability:
    - PSwR-036
    - PSwR-037
    """
    for record in records:
        validate_observation_record(record)
