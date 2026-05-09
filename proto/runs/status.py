from __future__ import annotations

"""
Traceability:
- PSwR-017
- ALG-008
"""

VALID_RUN_STATUSES = (
    "erfolgreich",
    "eingeschränkt brauchbar",
    "unbrauchbar",
)


def validate_status_override(value: str | None) -> str | None:
    """
    Validate manual status override.

    Traceability:
    - PSwR-017
    - ALG-008
    """
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized not in VALID_RUN_STATUSES:
        raise ValueError(
            "Invalid run status override. Expected one of: "
            + ", ".join(VALID_RUN_STATUSES)
        )
    return normalized


def propose_run_status(
    *,
    required_source_availability: dict[str, bool],
    data_quality_score: float,
    consistency_score: float,
    outputs_complete: bool,
) -> str:
    """
    Propose run status from source availability, quality, consistency, and output completeness.

    Traceability:
    - PSwR-017
    - ALG-008
    """
    all_sources_available = all(required_source_availability.values())
    severe_issue = (
        (not all_sources_available and not outputs_complete)
        or data_quality_score < 40.0
        or consistency_score < 40.0
    )
    if severe_issue:
        return "unbrauchbar"

    successful = (
        all_sources_available
        and outputs_complete
        and data_quality_score >= 60.0
        and consistency_score >= 60.0
    )
    if successful:
        return "erfolgreich"

    return "eingeschränkt brauchbar"
