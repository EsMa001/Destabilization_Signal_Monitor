from __future__ import annotations

"""
Historical rolling-trend scoring helpers.

Traceability:
- PSR-010
- PSwR-020
- PSwR-021
- PSwR-023
- PSwR-025
- PSwR-026
- PSwR-027
- PSwR-028
- PSwR-029
- PSwR-034
- ALG-009
- ALG-010
- ALG-011
- ALG-012
"""

from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import date, timedelta
from statistics import mean

from proto.models import ScoreRecord
from proto.scoring.confidence import derive_historical_confidence
from proto.scoring.thresholds import StageThresholds, map_score_to_stage
from proto.scoring.trend import infer_trend

TREND_NO_COMPARISON = "kein_vergleich"
STAGE_NOT_ASSESSED = "nicht_bewertbar"
REVIEW_DEFAULT_CLUSTERS = frozenset({"tension", "escalation"})
REVIEW_STAGE_PRIORITY = {
    "nicht_bewertbar": -1,
    "niedrig": 0,
    "erhöht": 1,
    "hoch": 2,
    "sehr hoch": 3,
}
REVIEW_CANDIDATE_MIN_ROLLING_VALUE = 60.0
REVIEW_CANDIDATE_MIN_ABS_DELTA = 8.0


@dataclass(frozen=True)
class HistoricalRollingRecord:
    """
    One daily historical rolling point for one score series.

    Traceability:
    - PSyR-015
    - PSwR-023
    - PSwR-025
    - PSwR-030
    """

    country: str
    cluster: str
    score_name: str
    date: date
    rolling_value: float | None
    window_days: int
    min_valid_days: int
    valid_days: int
    coverage_ratio: float
    is_valid: bool
    stage: str
    trend: str
    confidence_score: float
    confidence_level: str


@dataclass(frozen=True)
class HistoricalReviewCandidateRecord:
    """
    Analyst-oriented historical review candidate.

    Traceability:
    - PSR-010
    - PSwR-029
    - PM-015
    """

    rank: int
    country: str
    cluster: str
    date: date
    rolling_value: float
    is_valid: bool
    valid_days: int
    min_valid_days: int
    coverage_ratio: float
    stage: str
    trend: str
    confidence_score: float
    confidence_level: str
    evidence_tier: str
    snapshot_relation: str
    snapshot_source_mode: str
    snapshot_source_date: str | None
    baseline_marker: bool
    delta_previous_numeric: float | None
    abs_delta_previous_numeric: float
    stage_priority: int
    top_driver_1_name: str | None
    top_driver_1_value: float | None
    top_driver_2_name: str | None
    top_driver_2_value: float | None
    dominant_driver: str | None
    driver_concentration_ratio: float | None
    candidate_reason: str


def _iter_days(start_date: date, end_date: date):
    cursor = start_date
    while cursor <= end_date:
        yield cursor
        cursor += timedelta(days=1)


def build_historical_rolling_records(
    *,
    base_scores: list[ScoreRecord],
    run_date: date,
    countries: list[str],
    horizon_days: int,
    window_days: int,
    min_valid_days: int,
    aggregation: str,
    delta_epsilon: float,
    thresholds: StageThresholds,
    constant_clusters: set[str] | None = None,
) -> list[HistoricalRollingRecord]:
    """
    Build historical rolling trend from official daily subscores + cluster scores.

    Traceability:
    - PSyR-012
    - PSyR-013
    - PSyR-014
    - PSwR-020
    - PSwR-021
    - PSwR-023
    - PSwR-024
    - PSwR-025
    - PSwR-026
    - PSwR-027
    - PSwR-028
    - ALG-009
    - ALG-010
    - ALG-011
    - ALG-012
    - PM-009
    - PM-011
    - PM-012
    """
    if aggregation != "rolling_mean":
        raise ValueError("unsupported historical aggregation")
    if window_days <= 0:
        raise ValueError("window_days must be > 0")
    if min_valid_days <= 0 or min_valid_days > window_days:
        raise ValueError("min_valid_days must be in range [1, window_days]")
    if horizon_days <= 0:
        raise ValueError("horizon_days must be > 0")

    horizon_start = run_date - timedelta(days=horizon_days - 1)
    country_set = set(countries)
    constant_cluster_set = constant_clusters or set()

    score_maps: dict[tuple[str, str, str], dict[date, float]] = {}
    for score in base_scores:
        if score.country not in country_set:
            continue
        if not (horizon_start <= score.date <= run_date):
            continue
        key = (score.country, score.cluster, score.score_name)
        score_maps.setdefault(key, {})[score.date] = float(score.score_value)

    output: list[HistoricalRollingRecord] = []
    for key in sorted(score_maps.keys()):
        country, cluster, score_name = key
        date_to_value = dict(score_maps[key])

        # Bridge/context helper inputs are currently treated as time-constant
        # for historical trend output where configured via cluster-level rule.
        if cluster in constant_cluster_set and date_to_value:
            latest_date = max(date_to_value.keys())
            constant_value = date_to_value[latest_date]
            for day in _iter_days(horizon_start, run_date):
                date_to_value.setdefault(day, constant_value)

        previous_valid_value: float | None = None
        for point_date in _iter_days(horizon_start, run_date):
            window_start = point_date - timedelta(days=window_days - 1)
            window_values = [
                date_to_value[window_day]
                for window_day in _iter_days(window_start, point_date)
                if window_day in date_to_value
            ]
            valid_days = len(window_values)
            coverage_ratio = round(valid_days / float(window_days), 4)

            if valid_days < min_valid_days:
                if valid_days == 0:
                    rolling_value = None
                    stage = STAGE_NOT_ASSESSED
                    confidence_score, confidence_level = 0.0, "niedrig"
                else:
                    rolling_value = round(mean(window_values), 4)
                    stage = map_score_to_stage(rolling_value, thresholds)
                    confidence_score, confidence_level = derive_historical_confidence(
                        score_value=rolling_value,
                        coverage_ratio=coverage_ratio,
                    )
                output.append(
                    HistoricalRollingRecord(
                        country=country,
                        cluster=cluster,
                        score_name=score_name,
                        date=point_date,
                        rolling_value=rolling_value,
                        window_days=window_days,
                        min_valid_days=min_valid_days,
                        valid_days=valid_days,
                        coverage_ratio=coverage_ratio,
                        is_valid=False,
                        stage=stage,
                        trend=TREND_NO_COMPARISON,
                        confidence_score=confidence_score,
                        confidence_level=confidence_level,
                    )
                )
                continue

            rolling_value = round(mean(window_values), 4)
            if previous_valid_value is None:
                trend = TREND_NO_COMPARISON
            else:
                trend = infer_trend(
                    current_value=rolling_value,
                    baseline_value=previous_valid_value,
                    eps=delta_epsilon,
                )
            previous_valid_value = rolling_value
            confidence_score, confidence_level = derive_historical_confidence(
                score_value=rolling_value,
                coverage_ratio=coverage_ratio,
            )
            output.append(
                HistoricalRollingRecord(
                    country=country,
                    cluster=cluster,
                    score_name=score_name,
                    date=point_date,
                    rolling_value=rolling_value,
                    window_days=window_days,
                    min_valid_days=min_valid_days,
                    valid_days=valid_days,
                    coverage_ratio=coverage_ratio,
                    is_valid=True,
                    stage=map_score_to_stage(rolling_value, thresholds),
                    trend=trend,
                    confidence_score=confidence_score,
                    confidence_level=confidence_level,
                )
            )
    return output


def latest_valid_points_by_series(
    records: list[HistoricalRollingRecord],
) -> dict[tuple[str, str, str], HistoricalRollingRecord]:
    """
    Return latest valid rolling point per (country, cluster, score_name).

    Traceability:
    - PSwR-022
    - PM-010
    """
    latest: dict[tuple[str, str, str], HistoricalRollingRecord] = {}
    for record in records:
        if not record.is_valid:
            continue
        key = (record.country, record.cluster, record.score_name)
        previous = latest.get(key)
        if previous is None or record.date > previous.date:
            latest[key] = record
    return latest


def latest_points_with_value_by_series(
    records: list[HistoricalRollingRecord],
) -> dict[tuple[str, str, str], HistoricalRollingRecord]:
    """
    Return latest rolling point with numeric value per (country, cluster, score_name).

    Traceability:
    - PSwR-022
    - PM-010
    """
    latest: dict[tuple[str, str, str], HistoricalRollingRecord] = {}
    for record in records:
        if record.rolling_value is None:
            continue
        key = (record.country, record.cluster, record.score_name)
        previous = latest.get(key)
        if previous is None or record.date > previous.date:
            latest[key] = record
    return latest


def points_on_date_by_series(
    records: list[HistoricalRollingRecord],
    *,
    point_date: date,
) -> dict[tuple[str, str, str], HistoricalRollingRecord]:
    """
    Return rolling points at a specific date per (country, cluster, score_name).

    Traceability:
    - PSwR-022
    - PM-010
    """
    selected: dict[tuple[str, str, str], HistoricalRollingRecord] = {}
    for record in records:
        if record.date != point_date:
            continue
        key = (record.country, record.cluster, record.score_name)
        selected[key] = record
    return selected


def build_snapshot_context_by_cluster(
    records: list[HistoricalRollingRecord],
) -> dict[tuple[str, str], dict[str, float | int | str | None]]:
    """
    Build required annual snapshot context metrics from historical cluster points.

    Traceability:
    - PSR-009
    - PSwR-033
    - PM-014
    - PM-015
    """
    grouped: dict[tuple[str, str], list[HistoricalRollingRecord]] = {}
    for record in records:
        if record.score_name != "cluster_score" or record.rolling_value is None:
            continue
        key = (record.country, record.cluster)
        grouped.setdefault(key, []).append(record)

    context: dict[tuple[str, str], dict[str, float | int | str | None]] = {}
    for key, values in grouped.items():
        sorted_values = sorted(values, key=lambda item: item.date)
        numeric_values = [item.rolling_value for item in sorted_values if item.rolling_value is not None]
        if not numeric_values:
            context[key] = {
                "current_value": None,
                "year_max": None,
                "year_min": None,
                "high_or_very_high_days": 0,
                "latest_valid_date": None,
            }
            continue
        latest = sorted_values[-1]
        context[key] = {
            "current_value": latest.rolling_value,
            "year_max": round(max(numeric_values), 4),
            "year_min": round(min(numeric_values), 4),
            "high_or_very_high_days": sum(
                1 for item in sorted_values if item.stage in {"hoch", "sehr hoch"}
            ),
            "latest_valid_date": latest.date.isoformat(),
        }
    return context


def _parse_iso_date(value: object) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _derive_snapshot_relation(
    *,
    point_date: date,
    snapshot_source_date: date | None,
) -> str:
    if snapshot_source_date is None:
        return "unknown_snapshot_source"
    if point_date == snapshot_source_date:
        return "same_as_snapshot_source"
    if point_date < snapshot_source_date:
        return "before_snapshot_source"
    return "after_snapshot_source"


def _driver_details_for_candidates(
    records: list[HistoricalRollingRecord],
) -> dict[tuple[str, str, date], dict[str, str | float | None]]:
    grouped: dict[tuple[str, str, date], list[HistoricalRollingRecord]] = defaultdict(list)
    for record in records:
        if record.score_name == "cluster_score" or record.rolling_value is None:
            continue
        grouped[(record.country, record.cluster, record.date)].append(record)

    output: dict[tuple[str, str, date], dict[str, str | float | None]] = {}
    for key, values in grouped.items():
        ranked = sorted(values, key=lambda item: item.rolling_value or 0.0, reverse=True)
        top_1 = ranked[0] if ranked else None
        top_2 = ranked[1] if len(ranked) > 1 else None
        total = sum(item.rolling_value or 0.0 for item in ranked)
        concentration = None
        if top_1 is not None and total > 0:
            concentration = round((top_1.rolling_value or 0.0) / total, 4)
        dominant = None
        if top_1 is not None and concentration is not None and concentration >= 0.45:
            dominant = top_1.score_name
        output[key] = {
            "top_driver_1_name": top_1.score_name if top_1 else None,
            "top_driver_1_value": round(top_1.rolling_value, 4) if top_1 else None,
            "top_driver_2_name": top_2.score_name if top_2 else None,
            "top_driver_2_value": round(top_2.rolling_value, 4) if top_2 else None,
            "dominant_driver": dominant,
            "driver_concentration_ratio": concentration,
        }
    return output


def build_historical_review_candidates(
    *,
    records: list[HistoricalRollingRecord],
    snapshot_source_by_cluster: dict[tuple[str, str], dict[str, object]],
    candidate_clusters: set[str] | None = None,
    baseline_clusters: set[str] | None = None,
    min_rolling_value: float = REVIEW_CANDIDATE_MIN_ROLLING_VALUE,
    min_abs_delta: float = REVIEW_CANDIDATE_MIN_ABS_DELTA,
    include_baseline_clusters: bool = False,
) -> list[HistoricalReviewCandidateRecord]:
    """
    Build transparent historical review candidates for analyst validation.

    Traceability:
    - PSR-010
    - PSwR-022
    - PSwR-026
    - PSwR-029
    - PSwR-034
    - PM-013
    - PM-015
    """
    enabled_clusters = candidate_clusters or set(REVIEW_DEFAULT_CLUSTERS)
    baseline_cluster_set = baseline_clusters or {"vulnerability"}
    driver_details = _driver_details_for_candidates(records)

    cluster_points: dict[tuple[str, str], list[HistoricalRollingRecord]] = defaultdict(list)
    for record in records:
        if record.score_name != "cluster_score" or record.rolling_value is None:
            continue
        cluster_points[(record.country, record.cluster)].append(record)

    candidates: list[HistoricalReviewCandidateRecord] = []
    for (country, cluster), values in sorted(cluster_points.items()):
        is_baseline_cluster = cluster in baseline_cluster_set
        if is_baseline_cluster and not include_baseline_clusters:
            continue
        if cluster not in enabled_clusters and not is_baseline_cluster:
            continue

        source = snapshot_source_by_cluster.get((country, cluster), {})
        snapshot_source_date = _parse_iso_date(source.get("source_date"))
        snapshot_source_mode = str(source.get("source_mode", "unknown_snapshot_source_mode"))

        previous_numeric_value: float | None = None
        for point in sorted(values, key=lambda item: item.date):
            rolling_value = float(point.rolling_value)
            delta_previous = (
                None if previous_numeric_value is None else round(rolling_value - previous_numeric_value, 4)
            )
            abs_delta = round(abs(delta_previous), 4) if delta_previous is not None else 0.0
            stage_priority = REVIEW_STAGE_PRIORITY.get(point.stage, 0)

            is_high_stage = stage_priority >= REVIEW_STAGE_PRIORITY["hoch"]
            has_high_value = rolling_value >= float(min_rolling_value)
            has_large_delta = abs_delta >= float(min_abs_delta)
            if not (is_high_stage or has_high_value or has_large_delta):
                previous_numeric_value = rolling_value
                continue
            is_plateau_repeat = delta_previous is not None and abs_delta == 0.0
            if is_plateau_repeat and not has_large_delta:
                previous_numeric_value = rolling_value
                continue

            reason_parts: list[str] = []
            if is_high_stage:
                reason_parts.append("high_stage")
            if has_high_value:
                reason_parts.append("high_rolling_value")
            if has_large_delta:
                reason_parts.append("large_abs_delta")
            if not point.is_valid:
                reason_parts.append("low_coverage_numeric")

            driver_key = (country, cluster, point.date)
            drivers = driver_details.get(driver_key, {})
            candidates.append(
                HistoricalReviewCandidateRecord(
                    rank=0,
                    country=country,
                    cluster=cluster,
                    date=point.date,
                    rolling_value=round(rolling_value, 4),
                    is_valid=point.is_valid,
                    valid_days=point.valid_days,
                    min_valid_days=point.min_valid_days,
                    coverage_ratio=point.coverage_ratio,
                    stage=point.stage,
                    trend=point.trend,
                    confidence_score=point.confidence_score,
                    confidence_level=point.confidence_level,
                    evidence_tier="full_validity" if point.is_valid else "low_coverage_numeric",
                    snapshot_relation=_derive_snapshot_relation(
                        point_date=point.date,
                        snapshot_source_date=snapshot_source_date,
                    ),
                    snapshot_source_mode=snapshot_source_mode,
                    snapshot_source_date=source.get("source_date") if isinstance(source.get("source_date"), str) else None,
                    baseline_marker=is_baseline_cluster,
                    delta_previous_numeric=delta_previous,
                    abs_delta_previous_numeric=abs_delta,
                    stage_priority=stage_priority,
                    top_driver_1_name=drivers.get("top_driver_1_name"),
                    top_driver_1_value=drivers.get("top_driver_1_value"),
                    top_driver_2_name=drivers.get("top_driver_2_name"),
                    top_driver_2_value=drivers.get("top_driver_2_value"),
                    dominant_driver=drivers.get("dominant_driver"),
                    driver_concentration_ratio=drivers.get("driver_concentration_ratio"),
                    candidate_reason=";".join(reason_parts),
                )
            )
            previous_numeric_value = rolling_value

    ordered = sorted(
        candidates,
        key=lambda item: (
            0 if item.evidence_tier == "full_validity" else 1,
            -item.abs_delta_previous_numeric,
            -item.stage_priority,
            -item.rolling_value,
            item.country,
            item.cluster,
            item.date,
        ),
    )
    return [
        replace(candidate, rank=index + 1)
        for index, candidate in enumerate(ordered)
    ]
