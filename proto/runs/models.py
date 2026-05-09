from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunMetadata:
    """
    Run metadata model.

    Traceability:
    - PSyR-008
    - DataModel: Run metadata
    """

    run_timestamp: str
    countries: list[str]
    short_days: int
    recent_days: int
    baseline_days: int
    query_version: str
    scoring_version: str
    bridge_file_version: str
    context_table_version: str
    metadata_schema_version: str = "v2"
    proposed_run_status: str = "unbekannt"
    run_status: str = "unbekannt"
    run_status_overridden: bool = False
