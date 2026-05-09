from __future__ import annotations

"""
UNHCR source adapter for V3.2 `Displacement` layer observations.

Traceability:
- PSyR-025
- PSwR-060
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

SOURCE_ID = "unhcr"
LAYER = "Displacement"
SIGNAL_FAMILY = "displacement_pressure_index"


@dataclass(frozen=True)
class UnhcrRecord:
    period_start: date
    period_end: date
    country: str
    displacement_pressure: float
    delta_pressure: float
    exposure: float
    unit: str
    provenance: str
    quality_completeness: float


def _derive_raw_signal(record: UnhcrRecord) -> float:
    # Transparent MVP mapping with positive-change emphasis.
    # Traceability:
    # - PSyR-025
    # - PSwR-060
    # - PSwR-039
    # - PSwR-040
    # - PM-016
    # - PM-018
    positive_delta = max(0.0, record.delta_pressure)
    return round(
        0.6 * record.displacement_pressure + 0.25 * positive_delta + 0.15 * record.exposure,
        4,
    )


def load_unhcr_records(path: Path) -> list[UnhcrRecord]:
    """
    Load raw UNHCR rows from CSV snapshot.

    Traceability:
    - PSwR-060
    - PSwR-039
    """
    rows: list[UnhcrRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                UnhcrRecord(
                    period_start=parse_iso_date(row["period_start"]),
                    period_end=parse_iso_date(row["period_end"]),
                    country=canonical_country(row["country"]),
                    displacement_pressure=parse_float(
                        row["displacement_pressure"],
                        field_name="displacement_pressure",
                    ),
                    delta_pressure=parse_float(row["delta_pressure"], field_name="delta_pressure"),
                    exposure=parse_float(row["exposure"], field_name="exposure"),
                    unit=row["unit"].strip(),
                    provenance=row["provenance"].strip() or "UNHCR_snapshot",
                    quality_completeness=parse_float(
                        row["quality_completeness"],
                        field_name="quality_completeness",
                    ),
                )
            )
    return rows


def load_unhcr_observations(
    path: Path,
    *,
    normalization_method: str,
    normalization_scope: str = "per_country",
    baseline_value: float | None = None,
    baseline_scale: float | None = None,
) -> list[ObservationRecord]:
    """
    Load UNHCR as canonical `Displacement` observations.

    Traceability:
    - PSwR-060
    - PSwR-039
    - PSwR-040
    """
    rows = load_unhcr_records(path)
    observations: list[ObservationRecord] = []
    normalized_scope = normalization_scope.strip().lower()
    if normalized_scope not in {"per_country", "global"}:
        raise ValueError("normalization_scope must be 'per_country' or 'global'")

    by_country: dict[str, list[UnhcrRecord]] = defaultdict(list)
    for row in rows:
        by_country[row.country].append(row)

    ordered_rows: list[UnhcrRecord] = []
    if normalized_scope == "global":
        for country, values in sorted(by_country.items()):
            ordered_rows.extend(sorted(values, key=lambda item: item.period_end))
        raw_signals = [_derive_raw_signal(item) for item in ordered_rows]
        normalized_values = normalize_series(
            raw_signals,
            method=normalization_method,
            baseline_value=baseline_value,
            baseline_scale=baseline_scale,
        )
        for row, raw_signal, normalized_value in zip(ordered_rows, raw_signals, normalized_values):
            observations.append(
                ObservationRecord(
                    source_id=SOURCE_ID,
                    layer=LAYER,
                    signal_family=SIGNAL_FAMILY,
                    country=row.country,
                    period_start=row.period_start,
                    period_end=row.period_end,
                    raw_value=raw_signal,
                    normalized_value=normalized_value,
                    unit=row.unit,
                    provenance=row.provenance,
                    quality_completeness=row.quality_completeness,
                    native_periodicity="monthly",
                    metadata={
                        "displacement_pressure": row.displacement_pressure,
                        "delta_pressure": row.delta_pressure,
                        "exposure": row.exposure,
                        "normalization_scope": normalized_scope,
                        "mapping": "0.6*pressure + 0.25*positive_delta + 0.15*exposure",
                    },
                )
            )
        return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)

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
                        "displacement_pressure": row.displacement_pressure,
                        "delta_pressure": row.delta_pressure,
                        "exposure": row.exposure,
                        "normalization_scope": normalized_scope,
                        "mapping": "0.6*pressure + 0.25*positive_delta + 0.15*exposure",
                    },
                )
            )
    return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)
