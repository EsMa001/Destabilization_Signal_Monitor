from __future__ import annotations

"""
Structured narrative/expert input adapter for V3.2 `Narrative` layer.

Traceability:
- PSyR-026
- PSwR-061
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

SOURCE_ID = "narrative_input"
LAYER = "Narrative"
SIGNAL_FAMILY = "narrative_pressure_index"
DIRECTION_WEIGHTS = {
    "deescalatory": 0.2,
    "neutral": 0.5,
    "escalatory": 1.0,
}


@dataclass(frozen=True)
class NarrativeInputRecord:
    input_source_id: str
    country: str
    period_start: date
    period_end: date
    topic: str
    narrative_direction: str
    relevance: float
    confidence: float
    provenance: str


def _direction_weight(raw_direction: str) -> float:
    # Traceability:
    # - PSyR-026
    # - PSwR-061
    # - PSwR-039
    # - PSwR-040
    # - PM-016
    # - PM-018
    return DIRECTION_WEIGHTS.get(raw_direction.strip().lower(), 0.5)


def _derive_raw_signal(record: NarrativeInputRecord) -> float:
    # Transparent MVP mapping from structured analyst/expert input.
    # Traceability:
    # - PSyR-026
    # - PSwR-061
    # - PSwR-039
    # - PSwR-040
    # - PM-016
    # - PM-018
    return round(
        _direction_weight(record.narrative_direction) * record.relevance * record.confidence,
        4,
    )


def load_narrative_input_records(path: Path) -> list[NarrativeInputRecord]:
    """
    Load structured narrative input rows.

    Traceability:
    - PSwR-061
    - PSwR-039
    """
    rows: list[NarrativeInputRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                NarrativeInputRecord(
                    input_source_id=row["source_id"].strip(),
                    country=canonical_country(row["country"]),
                    period_start=parse_iso_date(row["period_start"]),
                    period_end=parse_iso_date(row["period_end"]),
                    topic=row["topic"].strip(),
                    narrative_direction=row["narrative_direction"].strip(),
                    relevance=parse_float(row["relevance"], field_name="relevance"),
                    confidence=parse_float(row["confidence"], field_name="confidence"),
                    provenance=row["provenance"].strip() or "Narrative_Input_snapshot",
                )
            )
    return rows


def load_narrative_input_observations(
    path: Path,
    *,
    normalization_method: str,
    normalization_scope: str = "per_country",
    baseline_value: float | None = None,
    baseline_scale: float | None = None,
) -> list[ObservationRecord]:
    """
    Load structured narrative input as canonical `Narrative` observations.

    Traceability:
    - PSwR-061
    - PSwR-039
    - PSwR-040
    """
    rows = load_narrative_input_records(path)
    observations: list[ObservationRecord] = []
    normalized_scope = normalization_scope.strip().lower()
    if normalized_scope not in {"per_country", "global"}:
        raise ValueError("normalization_scope must be 'per_country' or 'global'")

    by_country: dict[str, list[NarrativeInputRecord]] = defaultdict(list)
    for row in rows:
        by_country[row.country].append(row)

    ordered_rows: list[NarrativeInputRecord] = []
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
                    unit="narrative_index",
                    provenance=row.provenance,
                    quality_completeness=max(0.0, min(1.0, row.confidence)),
                    native_periodicity="monthly",
                    metadata={
                        "input_source_id": row.input_source_id,
                        "topic": row.topic,
                        "narrative_direction": row.narrative_direction,
                        "relevance": row.relevance,
                        "confidence": row.confidence,
                        "normalization_scope": normalized_scope,
                        "mapping": "direction_weight*relevance*confidence",
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
                    unit="narrative_index",
                    provenance=row.provenance,
                    quality_completeness=max(0.0, min(1.0, row.confidence)),
                    native_periodicity="monthly",
                    metadata={
                        "input_source_id": row.input_source_id,
                        "topic": row.topic,
                        "narrative_direction": row.narrative_direction,
                        "relevance": row.relevance,
                        "confidence": row.confidence,
                        "normalization_scope": normalized_scope,
                        "mapping": "direction_weight*relevance*confidence",
                    },
                )
            )
    return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)
