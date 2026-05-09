from __future__ import annotations

"""
GDELT event adapter for V3.3 `Event` layer observations.

Traceability:
- PSyR-029
- PSwR-071
- PSwR-072
- PSwR-039
- PSwR-040
- PM-032
- PM-033
- ALG-023
- ALG-024
"""

import csv
import math
from calendar import monthrange
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean

from proto.common import canonical_country
from proto.observations.adapter_contract import enforce_adapter_contract
from proto.observations.models import ObservationRecord
from proto.observations.normalization import normalize_series
from proto.sources.common import parse_float, parse_iso_date

SOURCE_ID = "gdelt_event"
LAYER = "Event"
SIGNAL_FAMILY = "observed_conflict_disruption_pressure"

EVENT_CATEGORY_WEIGHTS = {
    "crisis": 1.0,
    "protest": 0.85,
    "negativity": 0.6,
}


@dataclass(frozen=True)
class GdeltEventRow:
    event_date: date
    country: str
    event_type: str
    raw_value: float
    tone: float
    article_count: float
    provenance: str


@dataclass(frozen=True)
class GdeltEventMonthlyRecord:
    period_start: date
    period_end: date
    country: str
    raw_value: float
    unit: str
    provenance: str
    quality_completeness: float
    event_count: int
    unique_event_types: int
    category_coverage: float
    average_raw_value: float
    average_abs_tone: float
    average_article_count: float


def _month_bounds(value: date) -> tuple[date, date]:
    # Traceability:
    # - PSyR-029
    # - PSwR-071
    # - PSwR-072
    # - PSwR-039
    # - PSwR-040
    # - PM-032
    start = date(value.year, value.month, 1)
    end = date(value.year, value.month, monthrange(value.year, value.month)[1])
    return start, end


def _clamp_01(value: float) -> float:
    # Traceability:
    # - PSyR-029
    # - PSwR-071
    # - PSwR-072
    # - PSwR-039
    # - PSwR-040
    # - PM-032
    return max(0.0, min(1.0, value))


def _recency_weight(*, event_date: date, period_start: date, period_end: date) -> float:
    # Traceability:
    # - PSyR-029
    # - PSwR-071
    # - PSwR-072
    # - PSwR-039
    # - PSwR-040
    # - PM-032
    period_days = max(1, (period_end - period_start).days + 1)
    lag_days = max(0, (period_end - event_date).days)
    freshness = _clamp_01(1.0 - (lag_days / float(period_days)))
    # Lower bound >0 keeps older same-month events visible while favoring recent events.
    return 0.7 + 0.3 * freshness


def _event_type_weight(event_type: str) -> float:
    # Traceability:
    # - PSyR-029
    # - PSwR-071
    # - PSwR-072
    # - PSwR-039
    # - PSwR-040
    # - PM-032
    return EVENT_CATEGORY_WEIGHTS.get(event_type.strip().lower(), 0.65)


def _row_event_intensity(
    record: GdeltEventRow,
    *,
    period_start: date,
    period_end: date,
) -> float:
    # Traceability:
    # - PSyR-029
    # - PSwR-071
    # - PSwR-072
    # - PSwR-039
    # - PSwR-040
    # - PM-032
    raw_component = _clamp_01(record.raw_value / 100.0)
    tone_component = _clamp_01(abs(record.tone) / 10.0)
    article_component = _clamp_01(math.log1p(max(0.0, record.article_count)) / math.log1p(250.0))

    base_intensity = 0.55 * raw_component + 0.25 * tone_component + 0.20 * article_component
    weighted = _event_type_weight(record.event_type) * base_intensity
    return round(weighted * _recency_weight(event_date=record.event_date, period_start=period_start, period_end=period_end), 4)


def load_gdelt_event_rows(path: Path) -> list[GdeltEventRow]:
    """
    Load raw GDELT event rows for Event-layer processing.

    Traceability:
    - PSwR-071
    - PSwR-039
    """
    rows: list[GdeltEventRow] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            event_date = parse_iso_date(row["date"])
            country = canonical_country(row["country"])
            event_type = row["category"].strip().lower()
            raw_value = parse_float(row["raw_value"], field_name="raw_value")
            tone = parse_float(row.get("tone", "0"), field_name="tone")
            article_count = parse_float(row.get("article_count", "0"), field_name="article_count")
            rows.append(
                GdeltEventRow(
                    event_date=event_date,
                    country=country,
                    event_type=event_type,
                    raw_value=raw_value,
                    tone=tone,
                    article_count=article_count,
                    provenance="GDELT_snapshot",
                )
            )
    return rows


def load_gdelt_event_records(path: Path) -> list[GdeltEventMonthlyRecord]:
    """
    Aggregate raw GDELT rows to monthly Event records.

    Traceability:
    - PSwR-071
    - PSwR-072
    - ALG-023
    - ALG-024
    """
    rows = load_gdelt_event_rows(path)
    grouped: dict[tuple[str, int, int], list[GdeltEventRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.country, row.event_date.year, row.event_date.month)].append(row)

    output: list[GdeltEventMonthlyRecord] = []
    for (country, year_value, month_value), month_rows in sorted(grouped.items()):
        period_start = date(year_value, month_value, 1)
        period_end = date(year_value, month_value, monthrange(year_value, month_value)[1])
        intensities = [
            _row_event_intensity(item, period_start=period_start, period_end=period_end)
            for item in month_rows
        ]
        severity_component = mean(intensities)
        frequency_component = _clamp_01(len(month_rows) / 6.0)
        unique_types = {item.event_type for item in month_rows}
        category_coverage = _clamp_01(len(unique_types) / 3.0)

        raw_signal = round(
            _clamp_01(0.65 * severity_component + 0.20 * frequency_component + 0.15 * category_coverage),
            4,
        )
        quality_completeness = round(
            _clamp_01(0.5 * category_coverage + 0.5 * min(1.0, len(month_rows) / 3.0)),
            4,
        )
        output.append(
            GdeltEventMonthlyRecord(
                period_start=period_start,
                period_end=period_end,
                country=country,
                raw_value=raw_signal,
                unit="event_pressure_index",
                provenance=f"GDELT_event_monthly_{year_value:04d}-{month_value:02d}",
                quality_completeness=quality_completeness,
                event_count=len(month_rows),
                unique_event_types=len(unique_types),
                category_coverage=round(category_coverage, 4),
                average_raw_value=round(mean(item.raw_value for item in month_rows), 4),
                average_abs_tone=round(mean(abs(item.tone) for item in month_rows), 4),
                average_article_count=round(mean(item.article_count for item in month_rows), 4),
            )
        )
    return output


def load_gdelt_event_observations(
    path: Path,
    *,
    normalization_method: str,
    normalization_scope: str = "per_country",
    baseline_value: float | None = None,
    baseline_scale: float | None = None,
) -> list[ObservationRecord]:
    """
    Load monthly GDELT Event records as canonical observations.

    Traceability:
    - PSwR-071
    - PSwR-072
    - PSwR-039
    - PSwR-040
    """
    monthly_records = load_gdelt_event_records(path)
    normalized_scope = normalization_scope.strip().lower()
    if normalized_scope not in {"per_country", "global"}:
        raise ValueError("normalization_scope must be 'per_country' or 'global'")

    observations: list[ObservationRecord] = []
    by_country: dict[str, list[GdeltEventMonthlyRecord]] = defaultdict(list)
    for record in monthly_records:
        by_country[record.country].append(record)

    if normalized_scope == "global":
        ordered_records: list[GdeltEventMonthlyRecord] = []
        for country, values in sorted(by_country.items()):
            ordered_records.extend(sorted(values, key=lambda item: item.period_end))
        normalized_values = normalize_series(
            [item.raw_value for item in ordered_records],
            method=normalization_method,
            baseline_value=baseline_value,
            baseline_scale=baseline_scale,
        )
        for record, normalized_value in zip(ordered_records, normalized_values):
            observations.append(
                ObservationRecord(
                    source_id=SOURCE_ID,
                    layer=LAYER,
                    signal_family=SIGNAL_FAMILY,
                    country=record.country,
                    period_start=record.period_start,
                    period_end=record.period_end,
                    raw_value=record.raw_value,
                    normalized_value=normalized_value,
                    unit=record.unit,
                    provenance=record.provenance,
                    quality_completeness=record.quality_completeness,
                    native_periodicity="monthly",
                    metadata={
                        "event_count": record.event_count,
                        "unique_event_types": record.unique_event_types,
                        "category_coverage": record.category_coverage,
                        "average_raw_value": record.average_raw_value,
                        "average_abs_tone": record.average_abs_tone,
                        "average_article_count": record.average_article_count,
                        "normalization_scope": normalized_scope,
                        "mapping": "0.65*severity + 0.20*frequency + 0.15*type_coverage",
                    },
                )
            )
        return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)

    for country, values in sorted(by_country.items()):
        sorted_values = sorted(values, key=lambda item: item.period_end)
        normalized_values = normalize_series(
            [item.raw_value for item in sorted_values],
            method=normalization_method,
            baseline_value=baseline_value,
            baseline_scale=baseline_scale,
        )
        for record, normalized_value in zip(sorted_values, normalized_values):
            observations.append(
                ObservationRecord(
                    source_id=SOURCE_ID,
                    layer=LAYER,
                    signal_family=SIGNAL_FAMILY,
                    country=country,
                    period_start=record.period_start,
                    period_end=record.period_end,
                    raw_value=record.raw_value,
                    normalized_value=normalized_value,
                    unit=record.unit,
                    provenance=record.provenance,
                    quality_completeness=record.quality_completeness,
                    native_periodicity="monthly",
                    metadata={
                        "event_count": record.event_count,
                        "unique_event_types": record.unique_event_types,
                        "category_coverage": record.category_coverage,
                        "average_raw_value": record.average_raw_value,
                        "average_abs_tone": record.average_abs_tone,
                        "average_article_count": record.average_article_count,
                        "normalization_scope": normalized_scope,
                        "mapping": "0.65*severity + 0.20*frequency + 0.15*type_coverage",
                    },
                )
            )
    return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)
