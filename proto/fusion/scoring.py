from __future__ import annotations

"""
V3.1 layer/group fusion scoring helpers.

Traceability:
- PSR-022
- PSyR-032
- PSyR-019
- PSyR-020
- PSyR-029
- PSwR-041
- PSwR-042
- PSwR-043
- PSwR-045
- PSwR-046
- PSwR-056
- PSwR-057
- PSwR-058
- PSwR-062
- PSwR-063
- PSwR-064
- PSwR-068
- PSwR-071
- PSwR-072
- PSwR-073
- PSwR-079
- PSwR-070
- PSwR-083
- PSwR-084
- PSwR-087
- ALG-014
- ALG-015
- ALG-016
- ALG-021
- ALG-022
- ALG-029
- PM-019
- PM-020
- PM-021
- PM-022
- PM-024
- PM-025
- PM-027
- PM-028
- PM-029
- PM-032
- PM-033
- PM-034
- PM-039
- PM-042
- PM-043
- PM-044
"""

from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean

from proto.fusion.confidence import (
    derive_group_confidence,
    derive_total_confidence,
    map_fusion_confidence_level,
)
from proto.fusion.freshness import (
    classify_freshness,
    freshness_decay_factor,
    resolve_freshness_rule,
)
from proto.fusion.models import (
    FusionGroupScoreRecord,
    FusionHistoricalGroupScoreRecord,
    FusionHistoricalSourceSignalRecord,
    FusionHistoricalTotalScoreRecord,
    FusionSourceSignalRecord,
    FusionTotalScoreRecord,
)
from proto.observations.models import ObservationRecord


def _group_contribution_points(
    *,
    group_scores: dict[str, float],
    group_weights: dict[str, float],
) -> dict[str, float]:
    # Traceability:
    # - PSR-022
    # - PSyR-032
    # - PSyR-019
    # - PSyR-020
    # - PSyR-029
    # - PSwR-041
    if not group_scores:
        return {}
    weight_sum = sum(float(group_weights.get(group, 1.0)) for group in group_scores)
    if weight_sum <= 0:
        return {}
    return {
        group: round(float(group_weights.get(group, 1.0)) / weight_sum * value, 2)
        for group, value in group_scores.items()
    }


def _event_age_decay_factor(
    *,
    age_days: int,
    stale_after_days: int,
    decay_half_life_days: int,
    minimum_decay_factor: float,
) -> float:
    # Traceability:
    # - PSR-022
    # - PSyR-032
    # - PSyR-019
    # - PSyR-020
    # - PSyR-029
    # - PSwR-041
    if age_days <= stale_after_days:
        return 1.0
    overdue_days = age_days - stale_after_days
    exponent = overdue_days / float(max(1, decay_half_life_days))
    decay_factor = 0.5 ** exponent
    return max(minimum_decay_factor, decay_factor)


def _select_latest_observation(
    observations: list[ObservationRecord],
    *,
    run_date: date,
) -> ObservationRecord | None:
    # Traceability:
    # - PSR-022
    # - PSyR-032
    # - PSyR-019
    # - PSyR-020
    # - PSyR-029
    # - PSwR-041
    valid = [record for record in observations if record.period_end <= run_date]
    if not valid:
        return None
    return max(valid, key=lambda item: item.period_end)


def build_fusion_source_signals(
    *,
    observations: list[ObservationRecord],
    countries: list[str],
    run_date: date,
    target_period_days: int,
    source_to_group: dict[str, str],
) -> list[FusionSourceSignalRecord]:
    """
    Select one latest canonical observation per country/source for fusion target period.

    Traceability:
    - PSwR-043
    - PM-022
    """
    if target_period_days <= 0:
        raise ValueError("target_period_days must be > 0")
    target_end = run_date
    target_start = run_date - timedelta(days=target_period_days - 1)

    grouped: dict[tuple[str, str], list[ObservationRecord]] = defaultdict(list)
    for observation in observations:
        grouped[(observation.country, observation.source_id)].append(observation)

    output: list[FusionSourceSignalRecord] = []
    for country in countries:
        for source_id, group in source_to_group.items():
            selected = _select_latest_observation(
                grouped.get((country, source_id), []),
                run_date=run_date,
            )
            if selected is None:
                continue
            output.append(
                FusionSourceSignalRecord(
                    country=country,
                    source_id=source_id,
                    group=group,
                    layer=selected.layer,
                    signal_family=selected.signal_family,
                    target_period_start=target_start,
                    target_period_end=target_end,
                    native_period_start=selected.period_start,
                    native_period_end=selected.period_end,
                    raw_value=round(selected.raw_value, 4),
                    normalized_value=round(selected.normalized_value, 4),
                    unit=selected.unit,
                    provenance=selected.provenance,
                    quality_completeness=round(selected.quality_completeness, 4),
                    age_days=max(0, (run_date - selected.period_end).days),
                )
            )
    return sorted(
        output,
        key=lambda item: (
            item.country,
            item.group,
            item.source_id,
        ),
    )


def build_fusion_group_scores(
    *,
    signals: list[FusionSourceSignalRecord],
    countries: list[str],
    groups: list[str],
    source_weights: dict[str, dict[str, float]],
    max_age_days: int,
    coverage_weight: float,
    recency_weight: float,
    completeness_weight: float,
    consistency_weight: float,
    event_stale_after_days: int = 30,
    event_decay_half_life_days: int = 45,
    event_min_decay_factor: float = 0.4,
    freshness_model: dict[str, dict[str, float]] | None = None,
    event_fresh_boost_factor: float = 1.0,
) -> list[FusionGroupScoreRecord]:
    """
    Build group scores with transparent weighted mean and separate confidence.

    Traceability:
    - PSwR-041
    - PSwR-045
    - PSwR-046
    - PSwR-079
    - PSwR-083
    - PSwR-084
    - PSwR-087
    - ALG-014
    - ALG-028
    - ALG-029
    - PM-019
    - PM-039
    - PM-042
    - PM-043
    - PM-044
    """
    if event_stale_after_days < 0:
        raise ValueError("event_stale_after_days must be >= 0")
    if event_decay_half_life_days <= 0:
        raise ValueError("event_decay_half_life_days must be > 0")
    if not (0.0 < event_min_decay_factor <= 1.0):
        raise ValueError("event_min_decay_factor must be in range (0, 1]")
    if event_fresh_boost_factor < 1.0:
        raise ValueError("event_fresh_boost_factor must be >= 1.0")

    grouped_signals: dict[tuple[str, str], list[FusionSourceSignalRecord]] = defaultdict(list)
    for signal in signals:
        grouped_signals[(signal.country, signal.group)].append(signal)

    output: list[FusionGroupScoreRecord] = []
    for country in countries:
        for group in groups:
            current_signals = grouped_signals.get((country, group), [])
            expected_sources = source_weights.get(group, {})
            expected_source_count = len(expected_sources)
            if current_signals:
                weight_sum = 0.0
                weighted_value_sum = 0.0
                freshness_classes: list[str] = []
                for signal in current_signals:
                    source_weight = float(expected_sources.get(signal.source_id, 1.0))
                    adjusted_value = signal.normalized_value
                    if freshness_model is not None:
                        freshness_rule = resolve_freshness_rule(
                            freshness_model=freshness_model,
                            group=group,
                        )
                        freshness_class = classify_freshness(
                            age_days=signal.age_days,
                            rule=freshness_rule,
                        )
                        freshness_classes.append(freshness_class)
                        adjusted_value *= freshness_decay_factor(
                            age_days=signal.age_days,
                            rule=freshness_rule,
                            fresh_boost_factor=(
                                event_fresh_boost_factor if group == "event" else 1.0
                            ),
                        )
                    elif group == "event":
                        adjusted_value *= _event_age_decay_factor(
                            age_days=signal.age_days,
                            stale_after_days=event_stale_after_days,
                            decay_half_life_days=event_decay_half_life_days,
                            minimum_decay_factor=event_min_decay_factor,
                        )
                    weight_sum += source_weight
                    weighted_value_sum += source_weight * adjusted_value
                group_score = round(100.0 * (weighted_value_sum / max(weight_sum, 1e-9)), 2)
                confidence_score, confidence_level, coverage_component, recency_component, completeness_component, consistency_component = derive_group_confidence(
                    signals=current_signals,
                    expected_source_count=max(1, expected_source_count),
                    max_age_days=max_age_days,
                    coverage_weight=coverage_weight,
                    recency_weight=recency_weight,
                    completeness_weight=completeness_weight,
                    consistency_weight=consistency_weight,
                )
                if freshness_model is not None and freshness_classes:
                    aging_ratio = (
                        len([value for value in freshness_classes if value == "aging"])
                        / float(len(freshness_classes))
                    )
                    stale_ratio = (
                        len([value for value in freshness_classes if value == "stale"])
                        / float(len(freshness_classes))
                    )
                    freshness_penalty = round(6.0 * aging_ratio + 18.0 * stale_ratio, 2)
                    confidence_score = round(max(0.0, confidence_score - freshness_penalty), 2)
                    confidence_level = map_fusion_confidence_level(confidence_score)
                target_start = min(signal.target_period_start for signal in current_signals)
                target_end = max(signal.target_period_end for signal in current_signals)
                coverage_ratio = round(
                    min(1.0, len(current_signals) / float(max(1, expected_source_count))),
                    4,
                )
                status = (
                    "ok"
                    if len(current_signals) >= max(1, expected_source_count)
                    else "limited"
                )
                output.append(
                    FusionGroupScoreRecord(
                        country=country,
                        group=group,
                        target_period_start=target_start,
                        target_period_end=target_end,
                        group_score=group_score,
                        status=status,
                        source_count=len(current_signals),
                        expected_source_count=max(1, expected_source_count),
                        source_coverage_ratio=coverage_ratio,
                        confidence_score=confidence_score,
                        confidence_level=confidence_level,
                        coverage_component=coverage_component,
                        recency_component=recency_component,
                        completeness_component=completeness_component,
                        consistency_component=consistency_component,
                        sources_used=",".join(sorted(signal.source_id for signal in current_signals)),
                    )
                )
            else:
                output.append(
                    FusionGroupScoreRecord(
                        country=country,
                        group=group,
                        target_period_start=date.min,
                        target_period_end=date.min,
                        group_score=None,
                        status="not_available",
                        source_count=0,
                        expected_source_count=max(1, expected_source_count),
                        source_coverage_ratio=0.0,
                        confidence_score=0.0,
                        confidence_level="niedrig",
                        coverage_component=0.0,
                        recency_component=0.0,
                        completeness_component=0.0,
                        consistency_component=0.0,
                        sources_used="",
                    )
                )
    return sorted(output, key=lambda item: (item.country, groups.index(item.group)))


def build_fusion_total_scores(
    *,
    group_records: list[FusionGroupScoreRecord],
    countries: list[str],
    groups: list[str],
    group_weights: dict[str, float],
    bonus_enabled: bool,
    bonus_threshold: float,
    bonus_points: float,
    bonus_min_groups: int,
) -> list[FusionTotalScoreRecord]:
    """
    Build total fusion score from group records (parallel to existing cluster score path).

    Traceability:
    - PSwR-042
    - PSwR-045
    - ALG-015
    - ALG-016
    - PM-020
    - PM-021
    """
    grouped_by_country: dict[str, list[FusionGroupScoreRecord]] = defaultdict(list)
    for record in group_records:
        grouped_by_country[record.country].append(record)

    output: list[FusionTotalScoreRecord] = []
    expected_group_count = len(groups)
    for country in countries:
        records = grouped_by_country.get(country, [])
        available = [
            record
            for record in records
            if record.status in {"ok", "limited"} and record.group_score is not None
        ]
        if available:
            weighted_sum = 0.0
            weight_sum = 0.0
            for record in available:
                group_weight = float(group_weights.get(record.group, 1.0))
                weight_sum += group_weight
                weighted_sum += group_weight * float(record.group_score)
            fusion_score = weighted_sum / max(weight_sum, 1e-9)
            high_groups = [
                record
                for record in available
                if float(record.group_score) >= bonus_threshold
            ]
            should_apply_bonus = bonus_enabled and len(high_groups) >= bonus_min_groups
            applied_bonus = float(bonus_points) if should_apply_bonus else 0.0
            fusion_score = round(min(100.0, fusion_score + applied_bonus), 2)
            confidence = derive_total_confidence(
                group_records=records,
                expected_group_count=max(1, expected_group_count),
                group_weights=group_weights,
            )
            target_period_start = min(record.target_period_start for record in available)
            target_period_end = max(record.target_period_end for record in available)
            available_group_count = len(available)
            available_group_ratio = round(
                available_group_count / float(max(1, expected_group_count)),
                4,
            )
            output.append(
                FusionTotalScoreRecord(
                    country=country,
                    target_period_start=target_period_start,
                    target_period_end=target_period_end,
                    fusion_score=fusion_score,
                    confidence_score=confidence.confidence_score,
                    confidence_level=confidence.confidence_level,
                    group_count=expected_group_count,
                    expected_group_count=expected_group_count,
                    available_group_count=available_group_count,
                    available_group_ratio=available_group_ratio,
                    confidence_coverage_component=confidence.coverage_component,
                    confidence_recency_component=confidence.recency_component,
                    confidence_completeness_component=confidence.completeness_component,
                    confidence_consistency_component=confidence.consistency_component,
                    confidence_dominance_penalty=confidence.dominance_penalty,
                    confidence_limited_penalty=confidence.limited_penalty,
                    dominant_group_contribution_share=confidence.dominant_contribution_share,
                    groups_used=",".join(sorted(record.group for record in available)),
                    bonus_applied=should_apply_bonus,
                    bonus_points=round(applied_bonus, 2),
                )
            )
        else:
            output.append(
                FusionTotalScoreRecord(
                    country=country,
                    target_period_start=date.min,
                    target_period_end=date.min,
                    fusion_score=0.0,
                    confidence_score=0.0,
                    confidence_level="niedrig",
                    group_count=expected_group_count,
                    expected_group_count=expected_group_count,
                    available_group_count=0,
                    available_group_ratio=0.0,
                    confidence_coverage_component=0.0,
                    confidence_recency_component=0.0,
                    confidence_completeness_component=0.0,
                    confidence_consistency_component=0.0,
                    confidence_dominance_penalty=0.0,
                    confidence_limited_penalty=0.0,
                    dominant_group_contribution_share=0.0,
                    groups_used="",
                    bonus_applied=False,
                    bonus_points=0.0,
                )
            )
    return sorted(output, key=lambda item: countries.index(item.country))


def summarize_group_availability(
    group_records: list[FusionGroupScoreRecord],
) -> dict[str, float]:
    """
    Build compact availability diagnostics for fusion status export.

    Traceability:
    - PSwR-051
    """
    if not group_records:
        return {"available_ratio": 0.0, "mean_confidence": 0.0}
    available = [record for record in group_records if record.status in {"ok", "limited"}]
    available_ratio = len(available) / float(len(group_records))
    mean_confidence = mean(record.confidence_score for record in group_records)
    return {
        "available_ratio": round(available_ratio, 4),
        "mean_confidence": round(mean_confidence, 2),
    }


def _shift_year_month(*, year: int, month: int, delta_months: int) -> tuple[int, int]:
    # Traceability:
    # - PSR-022
    # - PSyR-032
    # - PSyR-019
    # - PSyR-020
    # - PSyR-029
    # - PSwR-041
    month_index = (year * 12 + (month - 1)) + delta_months
    shifted_year = month_index // 12
    shifted_month = (month_index % 12) + 1
    return shifted_year, shifted_month


def build_monthly_target_periods(
    *,
    run_date: date,
    horizon_months: int,
) -> list[tuple[str, date, date]]:
    """
    Build monthly fusion target periods (oldest -> newest).

    Traceability:
    - PSwR-056
    - PSwR-057
    - PM-024
    """
    if horizon_months <= 0:
        raise ValueError("horizon_months must be > 0")
    current_year = run_date.year
    current_month = run_date.month
    start_year, start_month = _shift_year_month(
        year=current_year,
        month=current_month,
        delta_months=-(horizon_months - 1),
    )
    periods: list[tuple[str, date, date]] = []
    for offset in range(horizon_months):
        year_value, month_value = _shift_year_month(
            year=start_year,
            month=start_month,
            delta_months=offset,
        )
        period_start = date(year_value, month_value, 1)
        period_end = date(year_value, month_value, monthrange(year_value, month_value)[1])
        if year_value == run_date.year and month_value == run_date.month:
            period_end = run_date
        periods.append((f"{year_value:04d}-{month_value:02d}", period_start, period_end))
    return periods


def _map_stage(
    *,
    score: float,
    low_max: float,
    elevated_max: float,
    high_max: float,
) -> str:
    # Traceability:
    # - PSR-022
    # - PSyR-032
    # - PSyR-019
    # - PSyR-020
    # - PSyR-029
    # - PSwR-041
    if score <= low_max:
        return "niedrig"
    if score <= elevated_max:
        return "erhoeht"
    if score <= high_max:
        return "hoch"
    return "sehr hoch"


def _map_trend(*, current: float, previous: float | None, delta_epsilon: float) -> str:
    # Traceability:
    # - PSR-022
    # - PSyR-032
    # - PSyR-019
    # - PSyR-020
    # - PSyR-029
    # - PSwR-041
    if previous is None:
        return "kein_vergleich"
    delta = current - previous
    if delta > delta_epsilon:
        return "zunehmend"
    if delta < -delta_epsilon:
        return "ruecklaeufig"
    return "stabil"


def _historical_interpretation_status(*, available_group_ratio: float) -> str:
    # Traceability:
    # - PSR-022
    # - PSyR-032
    # - PSyR-019
    # - PSyR-020
    # - PSyR-029
    # - PSwR-041
    if available_group_ratio < 0.5:
        return "limited_historical_coverage"
    if available_group_ratio < 0.75:
        return "reduced_historical_coverage"
    return "standard"


def build_historical_fusion_scores(
    *,
    observations: list[ObservationRecord],
    countries: list[str],
    run_date: date,
    horizon_months: int,
    groups: list[str],
    source_to_group: dict[str, str],
    source_weights: dict[str, dict[str, float]],
    group_weights: dict[str, float],
    bonus_enabled: bool,
    bonus_threshold: float,
    bonus_points: float,
    bonus_min_groups: int,
    max_age_days: int,
    coverage_weight: float,
    recency_weight: float,
    completeness_weight: float,
    consistency_weight: float,
    low_max: float,
    elevated_max: float,
    high_max: float,
    delta_epsilon: float,
    event_stale_after_days: int = 30,
    event_decay_half_life_days: int = 45,
    event_min_decay_factor: float = 0.4,
    freshness_model: dict[str, dict[str, float]] | None = None,
    event_fresh_boost_factor: float = 1.0,
    limited_coverage_threshold: float = 0.5,
    reduced_coverage_threshold: float = 0.75,
) -> tuple[
    list[FusionHistoricalSourceSignalRecord],
    list[FusionHistoricalGroupScoreRecord],
    list[FusionHistoricalTotalScoreRecord],
]:
    """
    Build monthly historical fusion signals and scores.

    Traceability:
    - PSyR-023
    - PSwR-056
    - PSwR-057
    - PSwR-062
    - PSwR-063
    - PSwR-066
    - PSwR-079
    - PSwR-083
    - PSwR-084
    - PSwR-087
    - PM-024
    - PM-025
    - PM-029
    - PM-039
    - PM-042
    - PM-043
    - PM-044
    """
    if not (0.0 < limited_coverage_threshold <= 1.0):
        raise ValueError("limited_coverage_threshold must be in range (0, 1]")
    if not (limited_coverage_threshold < reduced_coverage_threshold <= 1.0):
        raise ValueError(
            "reduced_coverage_threshold must be in range (limited_coverage_threshold, 1]"
        )

    periods = build_monthly_target_periods(run_date=run_date, horizon_months=horizon_months)
    historical_source_records: list[FusionHistoricalSourceSignalRecord] = []
    historical_group_records: list[FusionHistoricalGroupScoreRecord] = []
    historical_total_records: list[FusionHistoricalTotalScoreRecord] = []
    previous_total_by_country: dict[str, float] = {}
    previous_group_scores_by_country: dict[str, dict[str, float]] = {
        country: {} for country in countries
    }

    for period_label, period_start, period_end in periods:
        period_days = max(1, (period_end - period_start).days + 1)
        source_signals = build_fusion_source_signals(
            observations=observations,
            countries=countries,
            run_date=period_end,
            target_period_days=period_days,
            source_to_group=source_to_group,
        )
        group_scores = build_fusion_group_scores(
            signals=source_signals,
            countries=countries,
            groups=groups,
            source_weights=source_weights,
            max_age_days=max_age_days,
            coverage_weight=coverage_weight,
            recency_weight=recency_weight,
            completeness_weight=completeness_weight,
            consistency_weight=consistency_weight,
            event_stale_after_days=event_stale_after_days,
            event_decay_half_life_days=event_decay_half_life_days,
            event_min_decay_factor=event_min_decay_factor,
            freshness_model=freshness_model,
            event_fresh_boost_factor=event_fresh_boost_factor,
        )
        total_scores = build_fusion_total_scores(
            group_records=group_scores,
            countries=countries,
            groups=groups,
            group_weights=group_weights,
            bonus_enabled=bonus_enabled,
            bonus_threshold=bonus_threshold,
            bonus_points=bonus_points,
            bonus_min_groups=bonus_min_groups,
        )

        for signal in source_signals:
            historical_source_records.append(
                FusionHistoricalSourceSignalRecord(
                    country=signal.country,
                    source_id=signal.source_id,
                    group=signal.group,
                    layer=signal.layer,
                    period_label=period_label,
                    target_period_start=signal.target_period_start,
                    target_period_end=signal.target_period_end,
                    native_period_start=signal.native_period_start,
                    native_period_end=signal.native_period_end,
                    normalized_value=signal.normalized_value,
                    raw_value=signal.raw_value,
                    provenance=signal.provenance,
                    quality_completeness=signal.quality_completeness,
                    age_days=signal.age_days,
                )
            )

        current_group_scores_by_country: dict[str, dict[str, float]] = {
            country: {} for country in countries
        }
        for record in group_scores:
            if record.group_score is not None and record.status in {"ok", "limited"}:
                current_group_scores_by_country[record.country][record.group] = float(record.group_score)
            historical_group_records.append(
                FusionHistoricalGroupScoreRecord(
                    country=record.country,
                    group=record.group,
                    period_label=period_label,
                    target_period_start=record.target_period_start,
                    target_period_end=record.target_period_end,
                    group_score=record.group_score,
                    status=record.status,
                    source_count=record.source_count,
                    expected_source_count=record.expected_source_count,
                    source_coverage_ratio=record.source_coverage_ratio,
                    confidence_score=record.confidence_score,
                    confidence_level=record.confidence_level,
                    sources_used=record.sources_used,
                )
            )

        for record in total_scores:
            previous_total = previous_total_by_country.get(record.country)
            trend = _map_trend(
                current=record.fusion_score,
                previous=previous_total,
                delta_epsilon=delta_epsilon,
            )
            stage = _map_stage(
                score=record.fusion_score,
                low_max=low_max,
                elevated_max=elevated_max,
                high_max=high_max,
            )

            dominant_group: str | None = None
            dominant_group_delta: float | None = None
            strongest_change_group: str | None = None
            strongest_change_delta: float | None = None
            no_material_change = True
            previous_group_map = previous_group_scores_by_country.get(record.country, {})
            current_group_map = current_group_scores_by_country.get(record.country, {})
            deltas: list[tuple[str, float]] = []
            for group in groups:
                current_value = current_group_map.get(group)
                previous_value = previous_group_map.get(group)
                if current_value is None or previous_value is None:
                    continue
                deltas.append((group, current_value - previous_value))
            if deltas:
                candidate_group, candidate_delta = max(
                    deltas,
                    key=lambda item: abs(item[1]),
                )
                if abs(candidate_delta) > float(delta_epsilon):
                    strongest_change_group = candidate_group
                    strongest_change_delta = round(candidate_delta, 2)
                    dominant_group = strongest_change_group
                    dominant_group_delta = strongest_change_delta
                    no_material_change = False

            if record.available_group_ratio < limited_coverage_threshold:
                interpretation_status = "limited_historical_coverage"
            elif record.available_group_ratio < reduced_coverage_threshold:
                interpretation_status = "reduced_historical_coverage"
            else:
                interpretation_status = "standard"

            contribution_points = _group_contribution_points(
                group_scores=current_group_map,
                group_weights=group_weights,
            )
            top_contributors = sorted(
                contribution_points.items(),
                key=lambda item: item[1],
                reverse=True,
            )
            top_positive_group_1 = top_contributors[0][0] if top_contributors else None
            top_positive_group_1_contribution = (
                round(top_contributors[0][1], 2) if top_contributors else None
            )
            top_positive_group_2 = top_contributors[1][0] if len(top_contributors) > 1 else None
            top_positive_group_2_contribution = (
                round(top_contributors[1][1], 2) if len(top_contributors) > 1 else None
            )

            historical_total_records.append(
                FusionHistoricalTotalScoreRecord(
                    country=record.country,
                    period_label=period_label,
                    target_period_start=record.target_period_start,
                    target_period_end=record.target_period_end,
                    fusion_score=record.fusion_score,
                    stage=stage,
                    trend=trend,
                    confidence_score=record.confidence_score,
                    confidence_level=record.confidence_level,
                    group_count=record.group_count,
                    expected_group_count=record.expected_group_count,
                    available_group_count=record.available_group_count,
                    available_group_ratio=record.available_group_ratio,
                    confidence_coverage_component=record.confidence_coverage_component,
                    confidence_recency_component=record.confidence_recency_component,
                    confidence_completeness_component=record.confidence_completeness_component,
                    confidence_consistency_component=record.confidence_consistency_component,
                    confidence_dominance_penalty=record.confidence_dominance_penalty,
                    confidence_limited_penalty=record.confidence_limited_penalty,
                    dominant_group_contribution_share=record.dominant_group_contribution_share,
                    groups_used=record.groups_used,
                    dominant_group=dominant_group,
                    dominant_group_delta=dominant_group_delta,
                    top_positive_group_1=top_positive_group_1,
                    top_positive_group_1_contribution=top_positive_group_1_contribution,
                    top_positive_group_2=top_positive_group_2,
                    top_positive_group_2_contribution=top_positive_group_2_contribution,
                    strongest_change_group=strongest_change_group,
                    strongest_change_delta=strongest_change_delta,
                    no_material_change=no_material_change,
                    interpretation_status=interpretation_status,
                    bonus_applied=record.bonus_applied,
                    bonus_points=record.bonus_points,
                )
            )
            previous_total_by_country[record.country] = record.fusion_score
        previous_group_scores_by_country = current_group_scores_by_country

    return (
        historical_source_records,
        historical_group_records,
        historical_total_records,
    )
