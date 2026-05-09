from __future__ import annotations

"""
FAO FFPI source adapter for V3.1 canonical observations.

Traceability:
- PSyR-021
- PSwR-039
- PSwR-048
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

SOURCE_ID = "fao_ffpi"
LAYER = "Market/Food"
SIGNAL_FAMILY = "ffpi_price_index"


@dataclass(frozen=True)
class FaoFfpiRecord:
    period_start: date
    period_end: date
    country: str
    raw_value: float
    unit: str
    provenance: str
    quality_completeness: float


def load_fao_ffpi_records(path: Path) -> list[FaoFfpiRecord]:
    """
    Load raw FAO FFPI rows from CSV snapshot.

    Traceability:
    - PSwR-048
    - PSwR-039
    """
    rows: list[FaoFfpiRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                FaoFfpiRecord(
                    period_start=parse_iso_date(row["period_start"]),
                    period_end=parse_iso_date(row["period_end"]),
                    country=canonical_country(row["country"]),
                    raw_value=parse_float(row["raw_value"], field_name="raw_value"),
                    unit=row["unit"].strip(),
                    provenance=row["provenance"].strip() or "FAO_FFPI",
                    quality_completeness=parse_float(
                        row["quality_completeness"],
                        field_name="quality_completeness",
                    ),
                )
            )
    return rows


def load_fao_ffpi_observations(
    path: Path,
    *,
    normalization_method: str,
    baseline_value: float | None = None,
    baseline_scale: float | None = None,
) -> list[ObservationRecord]:
    """
    Load FAO FFPI as canonical observations.

    Traceability:
    - PSwR-048
    - PSwR-039
    - PSwR-040
    """
    rows = load_fao_ffpi_records(path)
    by_country: dict[str, list[FaoFfpiRecord]] = defaultdict(list)
    for row in rows:
        by_country[row.country].append(row)

    observations: list[ObservationRecord] = []
    for country, values in sorted(by_country.items()):
        sorted_values = sorted(values, key=lambda item: item.period_end)
        normalized_values = normalize_series(
            [item.raw_value for item in sorted_values],
            method=normalization_method,
            baseline_value=baseline_value,
            baseline_scale=baseline_scale,
        )
        for row, normalized_value in zip(sorted_values, normalized_values):
            observations.append(
                ObservationRecord(
                    source_id=SOURCE_ID,
                    layer=LAYER,
                    signal_family=SIGNAL_FAMILY,
                    country=country,
                    period_start=row.period_start,
                    period_end=row.period_end,
                    raw_value=row.raw_value,
                    normalized_value=normalized_value,
                    unit=row.unit,
                    provenance=row.provenance,
                    quality_completeness=row.quality_completeness,
                    native_periodicity="monthly",
                    metadata={"dataset": "FAO_FFPI"},
                )
            )
    return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)
