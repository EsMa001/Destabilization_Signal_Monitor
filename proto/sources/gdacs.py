from __future__ import annotations

"""
GDACS source adapter for V3.2 `Shock` layer observations.

Traceability:
- PSyR-024
- PSwR-059
- PSwR-039
- PSwR-040
- PM-016
- PM-018
"""

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from proto.common import canonical_country
from proto.observations.adapter_contract import enforce_adapter_contract
from proto.observations.models import ObservationRecord
from proto.observations.normalization import normalize_series
from proto.sources.common import parse_float, parse_iso_date

SOURCE_ID = "gdacs"
LAYER = "Shock"
SIGNAL_FAMILY = "disaster_shock_pressure"
ALERT_LEVEL_WEIGHTS = {
    "green": 0.3,
    "orange": 0.7,
    "red": 1.0,
}


@dataclass(frozen=True)
class GdacsRecord:
    period_start: date
    period_end: date
    country: str
    severity: float
    alert_level: str
    relevance: float
    unit: str
    provenance: str
    quality_completeness: float


def _alert_weight(alert_level: str) -> float:
    # Traceability:
    # - PSyR-024
    # - PSwR-059
    # - PSwR-039
    # - PSwR-040
    # - PM-016
    # - PM-018
    return ALERT_LEVEL_WEIGHTS.get(alert_level.strip().lower(), 0.5)


def _derive_raw_signal(record: GdacsRecord) -> float:
    # Transparent MVP mapping: severity * alert_weight * relevance.
    # Traceability:
    # - PSyR-024
    # - PSwR-059
    # - PSwR-039
    # - PSwR-040
    # - PM-016
    # - PM-018
    return round(record.severity * _alert_weight(record.alert_level) * record.relevance, 4)


def load_gdacs_records(path: Path) -> list[GdacsRecord]:
    """
    Load raw GDACS rows from CSV snapshot.

    Traceability:
    - PSwR-059
    - PSwR-039
    """
    rows: list[GdacsRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                GdacsRecord(
                    period_start=parse_iso_date(row["period_start"]),
                    period_end=parse_iso_date(row["period_end"]),
                    country=canonical_country(row["country"]),
                    severity=parse_float(row["severity"], field_name="severity"),
                    alert_level=row["alert_level"].strip(),
                    relevance=parse_float(row["relevance"], field_name="relevance"),
                    unit=row["unit"].strip(),
                    provenance=row["provenance"].strip() or "GDACS_snapshot",
                    quality_completeness=parse_float(
                        row["quality_completeness"],
                        field_name="quality_completeness",
                    ),
                )
            )
    return rows


def load_gdacs_observations(
    path: Path,
    *,
    normalization_method: str,
    baseline_value: float | None = None,
    baseline_scale: float | None = None,
) -> list[ObservationRecord]:
    """
    Load GDACS as canonical `Shock` observations.

    Traceability:
    - PSwR-059
    - PSwR-039
    - PSwR-040
    """
    rows = load_gdacs_records(path)
    by_country: dict[str, list[GdacsRecord]] = defaultdict(list)
    for row in rows:
        by_country[row.country].append(row)

    observations: list[ObservationRecord] = []
    for country, values in sorted(by_country.items()):
        sorted_values = sorted(values, key=lambda item: item.period_end)
        raw_signals = [_derive_raw_signal(item) for item in sorted_values]
        normalized_values = normalize_series(
            raw_signals,
            method=normalization_method,
            baseline_value=baseline_value,
            baseline_scale=baseline_scale,
        )
        for row, raw_signal, normalized_value in zip(sorted_values, raw_signals, normalized_values):
            observations.append(
                ObservationRecord(
                    source_id=SOURCE_ID,
                    layer=LAYER,
                    signal_family=SIGNAL_FAMILY,
                    country=country,
                    period_start=row.period_start,
                    period_end=row.period_end,
                    raw_value=raw_signal,
                    normalized_value=normalized_value,
                    unit=row.unit,
                    provenance=row.provenance,
                    quality_completeness=row.quality_completeness,
                    native_periodicity="monthly",
                    metadata={
                        "severity": row.severity,
                        "alert_level": row.alert_level,
                        "relevance": row.relevance,
                        "mapping": "severity*alert_weight*relevance",
                    },
                )
            )
    return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)
