from __future__ import annotations

"""
Validation and calibration helpers for V4.x external review.

Traceability:
- PSR-004
- PSR-016
- PSR-018
- PSR-021
- PSR-022
- PSR-023
- PSR-024
- PSR-025
- PSyR-023
- PSyR-028
- PSyR-030
- PSyR-031
- PSyR-032
- PSyR-033
- PSyR-034
- PSyR-035
- PSyR-036
- PSyR-037
- PSyR-038
- PSyR-039
- PSyR-040
- PSwR-041
- PSwR-042
- PSwR-045
- PSwR-056
- PSwR-062
- PSwR-063
- PSwR-064
- PSwR-069
- PSwR-075
- PSwR-076
- PSwR-077
- PSwR-078
- PSwR-079
- PSwR-080
- PSwR-081
- PSwR-082
- PSwR-083
- PSwR-084
- PSwR-085
- PSwR-086
- PSwR-087
- PSwR-088
- PSwR-089
- PSwR-090
- PSwR-093
- PSwR-094
- PSwR-095
- PSwR-096
- PSwR-097
- PSwR-098
- PSwR-099
- PSwR-100
- PSwR-101
- PSwR-102
- PSwR-103
- PSwR-104
- PSwR-105
- PSwR-106
- PSwR-107
- PSwR-108
- PSwR-109
- PSwR-110
- PSwR-111
- PSwR-112
- PM-028
- PM-029
- PM-035
- PM-036
- PM-037
- PM-038
- PM-039
- PM-040
- PM-041
- PM-042
- PM-043
- PM-044
- PM-045
- PM-046
- PM-047
- PM-048
- PM-051
- PM-052
- PM-053
- PM-054
- PM-055
- PM-056
- PM-057
- PM-058
- PM-059
- PM-060
- PM-061
- PM-062
- ALG-021
- ALG-022
- ALG-025
- ALG-026
- ALG-027
- ALG-028
- ALG-029
- ALG-030
- ALG-031
- ALG-032
- ALG-035
- ALG-036
- ALG-037
- ALG-038
- ALG-039
- ALG-040
- ALG-041
- ALG-042
- ALG-043
- ALG-044
- ALG-045
- ALG-046
- ALG-047
"""

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean, median, pstdev

from proto.fusion.freshness import (
    classify_freshness,
    copy_default_freshness_model,
    freshness_decay_factor,
    resolve_freshness_rule,
)
from proto.fusion.models import (
    FusionGroupScoreRecord,
    FusionHistoricalGroupScoreRecord,
    FusionHistoricalTotalScoreRecord,
    FusionSourceSignalRecord,
    FusionTotalScoreRecord,
)

STAGE_RANK = {
    "niedrig": 1,
    "erhoeht": 2,
    "hoch": 3,
    "sehr hoch": 4,
}

EXPECTED_REACTION_MIN_SCORE = {
    "low": 25.0,
    "elevated": 45.0,
    "high": 65.0,
    "very_high": 80.0,
}

EXPECTED_REACTION_MIN_STAGE = {
    "low": "niedrig",
    "elevated": "erhoeht",
    "high": "hoch",
    "very_high": "sehr hoch",
}


@dataclass(frozen=True)
class ValidationReferenceEpisodeRecord:
    """
    Analyst-reviewed episode anchor for validation.

    Traceability:
    - PSwR-076
    - PM-036
    """

    episode_id: str
    country: str
    period_start: date
    period_end: date
    expected_peak_period: str
    expected_total_reaction: str
    expected_groups: str
    timing_tolerance_months: int
    real_world_summary: str
    expected_total_summary: str

    def expected_groups_list(self) -> list[str]:
        return [item.strip().lower() for item in self.expected_groups.split("|") if item.strip()]


@dataclass(frozen=True)
class ValidationEpisodeResultRecord:
    """
    Episode-level validation result.

    Traceability:
    - PSwR-077
    - ALG-025
    """

    episode_id: str
    country: str
    period_start: date
    period_end: date
    expected_peak_period: str
    expected_total_reaction: str
    expected_groups: str
    data_available: bool
    observed_peak_period: str | None
    observed_peak_score: float | None
    observed_peak_stage: str | None
    peak_hit: bool | None
    peak_gap_points: float | None
    timing_lag_months: int | None
    timing_fit: bool | None
    expected_group_hit: bool | None
    group_match_ratio: float | None
    low_coverage_context: bool | None
    outcome: str


@dataclass(frozen=True)
class ValidationRankingRecord:
    """
    Snapshot ranking plausibility record.

    Traceability:
    - PSwR-077
    - ALG-026
    """

    country: str
    fusion_score: float
    actual_rank: int
    expected_rank: int
    rank_delta: int
    plausible_rank: bool


@dataclass(frozen=True)
class ValidationFreshnessGroupRecord:
    """
    Per-country/per-group freshness diagnostics.

    Traceability:
    - PSwR-083
    - PSwR-085
    - ALG-029
    """

    country: str
    group: str
    status: str
    source_count: int
    expected_source_count: int
    source_coverage_ratio: float
    latest_observation_date: date | None
    last_fresh_observation_date: date | None
    freshest_age_days: int | None
    stalest_age_days: int | None
    fresh_signal_count: int
    aging_signal_count: int
    stale_signal_count: int
    freshness_class: str
    freshness_decay_factor_mean: float
    group_score: float | None
    contribution_points: float
    contribution_share: float


@dataclass(frozen=True)
class ValidationHistoricalResponsivenessRecord:
    """
    Historical responsiveness metrics per country.

    Traceability:
    - PSwR-086
    - PM-045
    - ALG-031
    """

    country: str
    period_count: int
    compared_period_count: int
    mean_abs_delta: float
    max_abs_delta: float
    significant_change_count: int
    significant_change_ratio: float
    latest_delta: float | None
    recent_change_detected: bool
    responsiveness_profile: str


@dataclass(frozen=True)
class ValidationLayerDiagnosticRecord:
    """
    Analyst-focused diagnostics for dominance and support breadth.

    Traceability:
    - PSwR-081
    - PSwR-094
    - PSwR-095
    - PSwR-096
    - PM-051
    - ALG-027
    - ALG-035
    """

    country: str
    fusion_score: float
    dominant_group: str | None
    dominant_group_share: float
    dominance_flag: bool
    market_food_dominance_flag: bool
    event_stale_flag: bool
    governance_score: float | None
    governance_contribution_share: float
    governance_instability_flag: bool
    governance_low_freshness_flag: bool
    structural_score: float | None
    structural_outlier_flag: bool
    structural_contribution_share: float
    active_group_count: int
    available_group_count: int
    layer_support_ratio: float
    support_profile: str
    fresh_signal_count: int
    aging_signal_count: int
    stale_signal_count: int
    fresh_group_count: int
    aging_group_count: int
    stale_group_count: int
    fresh_contribution_share: float
    aging_contribution_share: float
    stale_contribution_share: float
    fresh_support_profile: str
    stale_support_profile: str
    dominant_fresh_group: str | None
    dominant_aging_group: str | None
    dominant_stale_group: str | None
    dynamic_layer_readiness: bool
    latest_fresh_observation_date: date | None


@dataclass(frozen=True)
class ValidationCountryProfileRecord:
    """
    Country-level 356-day comparative profile.

    Traceability:
    - PSwR-098
    - PSwR-099
    - PM-052
    - PM-053
    - ALG-036
    - ALG-040
    """

    country: str
    current_fusion_score: float
    confidence_score: float
    confidence_level: str
    operational_freshness_status: str
    fresh_contribution_share: float
    stale_contribution_share: float
    dynamic_layer_readiness: bool
    year_max_score: float
    year_max_period: str
    year_min_score: float
    year_min_period: str
    year_range_score: float
    year_mean_score: float
    year_volatility_std: float
    year_mean_abs_delta: float
    peak_count: int
    peak_intensity_mean: float
    dominant_group: str | None
    support_profile: str
    fresh_support_profile: str
    stale_support_profile: str


@dataclass(frozen=True)
class ValidationCountryPeakPhaseRecord:
    """
    Top critical peak phases per country.

    Traceability:
    - PSwR-098
    - PSwR-100
    - PM-053
    - ALG-037
    """

    country: str
    peak_rank: int
    period_label: str
    target_period_end: date
    fusion_score: float
    stage: str
    trend: str
    confidence_score: float
    confidence_level: str
    dominant_group: str | None
    top_positive_group_1: str | None
    strongest_change_group: str | None
    interpretation_status: str
    fresh_contribution_share: float
    stale_contribution_share: float
    dynamic_layer_readiness: bool


@dataclass(frozen=True)
class ValidationCountryGroupProfileRecord:
    """
    Mean and peak group-contribution profile over the 356-day horizon.

    Traceability:
    - PSwR-098
    - PSwR-100
    - PM-053
    - PM-054
    - ALG-038
    """

    country: str
    group: str
    period_count: int
    observed_period_count: int
    availability_ratio: float
    mean_group_score: float
    max_group_score: float
    min_group_score: float
    score_range: float
    active_period_ratio: float
    dominant_period_count: int
    mean_contribution_share: float


@dataclass(frozen=True)
class ValidationRankingTrajectoryRecord:
    """
    Period-level country ranking trajectory.

    Traceability:
    - PSwR-098
    - PSwR-102
    - PM-053
    - ALG-039
    """

    period_label: str
    target_period_end: date
    country: str
    fusion_score: float
    rank: int
    country_count: int


@dataclass(frozen=True)
class ValidationEventMarkerRecord:
    """
    Analyst-maintained event-marker registry entry.

    Traceability:
    - PSwR-106
    - PM-060
    - ALG-043
    """

    marker_id: str
    country: str
    period_start: date
    period_end: date
    event_label: str
    event_type: str
    support_weight: float
    support_confidence: float
    provenance: str


@dataclass(frozen=True)
class ValidationEventRegistryRecord:
    """
    Analyst-maintained event-registry entry for V4.3.2 alignment.

    Traceability:
    - PSwR-113
    - PSwR-114
    - PM-063
    - PM-064
    - ALG-048
    """

    event_id: str
    country: str
    title: str
    start_date: date
    end_date: date
    event_type: str
    summary: str
    source_category: str
    source_reference: str
    confidence: float
    relevance_groups: str
    expected_effect_direction: str
    expected_peak_window_start: date
    expected_peak_window_end: date
    notes: str


@dataclass(frozen=True)
class ValidationPeakAttributionRecord:
    """
    Peak-attribution record with global-vs-country decomposition.

    Traceability:
    - PSwR-105
    - PSwR-107
    - PSwR-108
    - PM-057
    - PM-058
    - PM-059
    - ALG-041
    - ALG-042
    - ALG-044
    """

    country: str
    peak_rank: int
    period_label: str
    target_period_end: date
    fusion_score: float
    prominence_score: float
    peak_width_periods: int
    rise_slope: float
    fall_slope: float
    separation_periods: int
    peak_quality_score: float
    dominant_group: str | None
    second_group: str | None
    support_profile: str
    support_breadth_ratio: float
    dominant_group_share: float
    fresh_contribution_share: float
    stale_contribution_share: float
    global_component_score: float
    country_specific_component_score: float
    global_share: float
    country_specific_share: float
    market_food_global_pressure: float
    market_food_local_pressure: float
    attribution_label: str
    peak_confidence_score: float
    peak_confidence_level: str
    event_support_status: str
    event_marker_count: int
    event_marker_ids: str


@dataclass(frozen=True)
class ValidationPeakEventMatchRecord:
    """
    Peak-to-event alignment result in the analyst event-registry space.

    Traceability:
    - PSwR-115
    - PSwR-116
    - PM-065
    - PM-066
    - ALG-049
    - ALG-050
    - ALG-051
    """

    country: str
    peak_rank: int
    period_label: str
    target_period_end: date
    fusion_score: float
    attribution_label: str
    trajectory_profile: str
    peak_confidence_score: float
    match_class: str
    match_confidence: float
    credible_match: bool
    matched_event_count: int
    matched_event_ids: str
    matched_event_titles: str
    best_event_id: str
    best_event_title: str
    best_event_type: str
    best_event_start: date | None
    best_event_end: date | None
    best_event_source_category: str
    time_distance_days: int
    overlap_days: int
    temporal_score: float
    thematic_score: float
    support_score: float
    evidence_chain: str
    uncertainty_note: str


@dataclass(frozen=True)
class ValidationPeakEventSupportRecord:
    """
    Compact event-support view for detected peaks.

    Traceability:
    - PSwR-106
    - PSwR-108
    - PM-060
    - ALG-043
    """

    country: str
    period_label: str
    target_period_end: date
    peak_rank: int
    event_support_status: str
    event_supported: bool
    event_marker_count: int
    event_marker_ids: str
    event_support_weight: float
    event_support_confidence: float
    event_label_summary: str


@dataclass(frozen=True)
class ValidationEventCoverageSummaryRecord:
    """
    Coverage diagnostics for peak-to-event matching quality.

    Traceability:
    - PSwR-118
    - PM-067
    - ALG-053
    """

    scope: str
    country: str
    peak_count: int
    direct_match_count: int
    plausible_context_match_count: int
    weak_match_count: int
    no_credible_match_count: int
    multi_event_overlap_count: int
    credible_match_count: int
    credible_match_ratio: float
    no_credible_match_ratio: float
    multi_event_overlap_ratio: float
    mean_match_confidence: float
    coverage_band: str


@dataclass(frozen=True)
class ValidationCountryEventAlignmentRecord:
    """
    Country-level alignment maturity and analyst commentary.

    Traceability:
    - PSwR-117
    - PSwR-123
    - PM-068
    - PM-069
    - ALG-052
    - ALG-054
    """

    country: str
    trajectory_profile: str
    peak_count: int
    direct_match_count: int
    plausible_context_match_count: int
    weak_match_count: int
    no_credible_match_count: int
    multi_event_overlap_count: int
    credible_match_ratio: float
    mean_match_confidence: float
    global_wave_peak_ratio: float
    country_specific_peak_ratio: float
    alignment_maturity_score: float
    alignment_maturity: str
    alignment_commentary: str
    top_linked_events: str
    open_uncertainties: str


@dataclass(frozen=True)
class ValidationTrajectoryProfileRecord:
    """
    Country-level trajectory interpretation label.

    Traceability:
    - PSwR-107
    - PSwR-109
    - PM-061
    - ALG-046
    """

    country: str
    trajectory_profile: str
    peak_count: int
    event_supported_peak_ratio: float
    weakly_supported_peak_ratio: float
    globally_co_moving_peak_ratio: float
    model_driven_peak_ratio: float
    country_specific_peak_ratio: float
    mean_global_share: float
    mean_country_specific_share: float
    dominant_peak_group: str | None
    mean_peak_confidence_score: float
    differentiation_flag: bool


@dataclass(frozen=True)
class ValidationGlobalPeakSynchronizationRecord:
    """
    Multi-country peak synchronization diagnostics per period.

    Traceability:
    - PSwR-107
    - PSwR-110
    - PM-062
    - ALG-047
    """

    period_label: str
    target_period_end: date
    peak_country_count: int
    total_country_count: int
    peak_country_ratio: float
    peak_countries: str
    mean_global_share: float
    mean_country_specific_share: float
    mean_peak_confidence_score: float
    dominant_wave_group: str | None
    synchronization_class: str


@dataclass(frozen=True)
class _PeakCandidate:
    country: str
    index: int
    period_label: str
    target_period_end: date
    fusion_score: float
    stage: str
    trend: str
    confidence_score: float
    confidence_level: str
    dominant_group: str | None
    top_positive_group_1: str | None
    strongest_change_group: str | None
    interpretation_status: str
    prominence_score: float
    peak_width_periods: int
    rise_slope: float
    fall_slope: float
    separation_periods: int
    peak_quality_score: float


def _parse_date(value: str) -> date:
    return date.fromisoformat(value.strip())


def _month_index(period_label: str) -> int:
    year_text, month_text = period_label.split("-", maxsplit=1)
    year_value = int(year_text)
    month_value = int(month_text)
    return year_value * 12 + month_value


def _month_lag(current_period: str, expected_period: str) -> int:
    return _month_index(current_period) - _month_index(expected_period)


def _expected_stage_rank(expected_reaction: str) -> int:
    normalized = expected_reaction.strip().lower()
    stage = EXPECTED_REACTION_MIN_STAGE.get(normalized, "erhoeht")
    return STAGE_RANK.get(stage, 2)


def _expected_min_score(expected_reaction: str) -> float:
    return EXPECTED_REACTION_MIN_SCORE.get(expected_reaction.strip().lower(), 45.0)


def compute_snapshot_freshness_groups(
    *,
    source_signals: list[FusionSourceSignalRecord],
    group_records: list[FusionGroupScoreRecord],
    group_weights: dict[str, float],
    freshness_model: dict[str, dict[str, float]] | None,
    event_fresh_boost_factor: float,
) -> list[ValidationFreshnessGroupRecord]:
    """
    Build per-group freshness diagnostics for snapshot fusion.

    Traceability:
    - PSwR-083
    - PSwR-085
    - ALG-029
    - ALG-030
    """
    signals_by_key: dict[tuple[str, str], list[FusionSourceSignalRecord]] = {}
    for signal in source_signals:
        signals_by_key.setdefault((signal.country, signal.group), []).append(signal)

    total_contribution_by_country: dict[str, float] = {}
    for record in group_records:
        if record.status not in {"ok", "limited"} or record.group_score is None:
            continue
        contribution_points = float(group_weights.get(record.group, 1.0)) * float(record.group_score)
        total_contribution_by_country[record.country] = (
            total_contribution_by_country.get(record.country, 0.0) + contribution_points
        )

    output: list[ValidationFreshnessGroupRecord] = []
    for record in sorted(group_records, key=lambda item: (item.country, item.group)):
        current_signals = signals_by_key.get((record.country, record.group), [])
        freshest_age_days: int | None = None
        stalest_age_days: int | None = None
        latest_observation_date: date | None = None
        last_fresh_observation_date: date | None = None
        fresh_count = 0
        aging_count = 0
        stale_count = 0
        factor_values: list[float] = []
        class_points = {"fresh": 0.0, "aging": 0.0, "stale": 0.0}
        for signal in current_signals:
            rule = resolve_freshness_rule(
                freshness_model=freshness_model,
                group=record.group,
            )
            freshness_class = classify_freshness(age_days=signal.age_days, rule=rule)
            if freshness_class == "fresh":
                fresh_count += 1
                if last_fresh_observation_date is None or signal.native_period_end > last_fresh_observation_date:
                    last_fresh_observation_date = signal.native_period_end
            elif freshness_class == "aging":
                aging_count += 1
            else:
                stale_count += 1

            boost = event_fresh_boost_factor if record.group == "event" else 1.0
            factor = freshness_decay_factor(
                age_days=signal.age_days,
                rule=rule,
                fresh_boost_factor=boost,
            )
            factor_values.append(factor)
            class_points[freshness_class] += max(0.0, float(signal.normalized_value) * factor)

            if freshest_age_days is None or signal.age_days < freshest_age_days:
                freshest_age_days = signal.age_days
            if stalest_age_days is None or signal.age_days > stalest_age_days:
                stalest_age_days = signal.age_days
            if latest_observation_date is None or signal.native_period_end > latest_observation_date:
                latest_observation_date = signal.native_period_end

        if not current_signals:
            freshness_class = "no_signal"
        else:
            freshness_class = max(class_points.items(), key=lambda item: item[1])[0]

        contribution_points = (
            float(group_weights.get(record.group, 1.0)) * float(record.group_score)
            if record.group_score is not None and record.status in {"ok", "limited"}
            else 0.0
        )
        total_country_points = total_contribution_by_country.get(record.country, 0.0)
        contribution_share = (
            contribution_points / total_country_points if total_country_points > 0 else 0.0
        )
        output.append(
            ValidationFreshnessGroupRecord(
                country=record.country,
                group=record.group,
                status=record.status,
                source_count=record.source_count,
                expected_source_count=record.expected_source_count,
                source_coverage_ratio=record.source_coverage_ratio,
                latest_observation_date=latest_observation_date,
                last_fresh_observation_date=last_fresh_observation_date,
                freshest_age_days=freshest_age_days,
                stalest_age_days=stalest_age_days,
                fresh_signal_count=fresh_count,
                aging_signal_count=aging_count,
                stale_signal_count=stale_count,
                freshness_class=freshness_class,
                freshness_decay_factor_mean=(
                    round(sum(factor_values) / float(len(factor_values)), 4)
                    if factor_values
                    else 0.0
                ),
                group_score=round(float(record.group_score), 2) if record.group_score is not None else None,
                contribution_points=round(contribution_points, 4),
                contribution_share=round(contribution_share, 4),
            )
        )
    return output


def compute_historical_responsiveness(
    *,
    historical_total_records: list[FusionHistoricalTotalScoreRecord],
    delta_threshold: float,
) -> list[ValidationHistoricalResponsivenessRecord]:
    """
    Build pragmatic historical responsiveness metrics by country.

    Traceability:
    - PSwR-086
    - PM-045
    - ALG-031
    """
    if delta_threshold <= 0:
        raise ValueError("delta_threshold must be > 0")

    by_country: dict[str, list[FusionHistoricalTotalScoreRecord]] = {}
    for item in historical_total_records:
        by_country.setdefault(item.country, []).append(item)

    output: list[ValidationHistoricalResponsivenessRecord] = []
    for country, records in sorted(by_country.items()):
        ordered = sorted(records, key=lambda item: item.target_period_end)
        deltas = [
            float(current.fusion_score) - float(previous.fusion_score)
            for previous, current in zip(ordered[:-1], ordered[1:])
        ]
        abs_deltas = [abs(value) for value in deltas]
        compared_count = len(deltas)
        significant_count = len([value for value in abs_deltas if value >= delta_threshold])
        significant_ratio = (
            significant_count / float(compared_count) if compared_count > 0 else 0.0
        )
        mean_abs_delta = mean(abs_deltas) if abs_deltas else 0.0
        max_abs_delta = max(abs_deltas) if abs_deltas else 0.0
        latest_delta = deltas[-1] if deltas else None
        recent_change_detected = abs(latest_delta) >= delta_threshold if latest_delta is not None else False

        if compared_count == 0:
            responsiveness_profile = "insufficient_history"
        elif significant_ratio >= 0.4 and mean_abs_delta >= delta_threshold:
            responsiveness_profile = "reactive"
        elif significant_ratio < 0.2:
            responsiveness_profile = "inertia_risk"
        else:
            responsiveness_profile = "balanced"

        output.append(
            ValidationHistoricalResponsivenessRecord(
                country=country,
                period_count=len(ordered),
                compared_period_count=compared_count,
                mean_abs_delta=round(mean_abs_delta, 4),
                max_abs_delta=round(max_abs_delta, 4),
                significant_change_count=significant_count,
                significant_change_ratio=round(significant_ratio, 4),
                latest_delta=round(latest_delta, 4) if latest_delta is not None else None,
                recent_change_detected=recent_change_detected,
                responsiveness_profile=responsiveness_profile,
            )
        )
    return output


def load_validation_reference_episodes(path: Path) -> list[ValidationReferenceEpisodeRecord]:
    """
    Load analyst reference episodes.

    Traceability:
    - PSwR-076
    - PM-036
    """
    rows: list[ValidationReferenceEpisodeRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                ValidationReferenceEpisodeRecord(
                    episode_id=str(row["episode_id"]).strip(),
                    country=str(row["country"]).strip(),
                    period_start=_parse_date(str(row["period_start"])),
                    period_end=_parse_date(str(row["period_end"])),
                    expected_peak_period=str(row["expected_peak_period"]).strip(),
                    expected_total_reaction=str(row["expected_total_reaction"]).strip().lower(),
                    expected_groups=str(row["expected_groups"]).strip().lower(),
                    timing_tolerance_months=int(str(row["timing_tolerance_months"]).strip()),
                    real_world_summary=str(row["real_world_summary"]).strip(),
                    expected_total_summary=str(row["expected_total_summary"]).strip(),
                )
            )
    return sorted(rows, key=lambda item: (item.country, item.period_start, item.episode_id))


def compute_validation_episode_results(
    *,
    reference_episodes: list[ValidationReferenceEpisodeRecord],
    historical_total_records: list[FusionHistoricalTotalScoreRecord],
    historical_group_records: list[FusionHistoricalGroupScoreRecord],
    group_activation_threshold: float,
) -> list[ValidationEpisodeResultRecord]:
    """
    Compare historical fusion behavior against reference episodes.

    Traceability:
    - PSwR-077
    - ALG-025
    """
    groups_by_country_period: dict[tuple[str, str], list[FusionHistoricalGroupScoreRecord]] = {}
    for item in historical_group_records:
        groups_by_country_period.setdefault((item.country, item.period_label), []).append(item)

    output: list[ValidationEpisodeResultRecord] = []
    for episode in reference_episodes:
        candidates = [
            record
            for record in historical_total_records
            if record.country == episode.country
            and episode.period_start <= record.target_period_end <= episode.period_end
        ]
        if not candidates:
            output.append(
                ValidationEpisodeResultRecord(
                    episode_id=episode.episode_id,
                    country=episode.country,
                    period_start=episode.period_start,
                    period_end=episode.period_end,
                    expected_peak_period=episode.expected_peak_period,
                    expected_total_reaction=episode.expected_total_reaction,
                    expected_groups=episode.expected_groups,
                    data_available=False,
                    observed_peak_period=None,
                    observed_peak_score=None,
                    observed_peak_stage=None,
                    peak_hit=None,
                    peak_gap_points=None,
                    timing_lag_months=None,
                    timing_fit=None,
                    expected_group_hit=None,
                    group_match_ratio=None,
                    low_coverage_context=None,
                    outcome="data_gap",
                )
            )
            continue

        observed_peak = max(candidates, key=lambda item: item.fusion_score)
        expected_groups = episode.expected_groups_list()
        top_groups = {
            group
            for group in (
                observed_peak.top_positive_group_1,
                observed_peak.top_positive_group_2,
                observed_peak.strongest_change_group,
            )
            if group
        }
        expected_group_hit = bool(set(expected_groups) & top_groups)
        matching_groups = 0
        period_group_records = groups_by_country_period.get(
            (episode.country, observed_peak.period_label),
            [],
        )
        for expected_group in expected_groups:
            match = next(
                (
                    item
                    for item in period_group_records
                    if item.group == expected_group
                    and item.group_score is not None
                    and float(item.group_score) >= group_activation_threshold
                ),
                None,
            )
            if match is not None:
                matching_groups += 1
        group_match_ratio = (
            round(matching_groups / float(len(expected_groups)), 4) if expected_groups else 0.0
        )

        observed_stage_rank = STAGE_RANK.get(observed_peak.stage, 1)
        peak_hit = observed_stage_rank >= _expected_stage_rank(episode.expected_total_reaction)
        peak_gap_points = round(
            observed_peak.fusion_score - _expected_min_score(episode.expected_total_reaction),
            2,
        )
        timing_lag_months = _month_lag(observed_peak.period_label, episode.expected_peak_period)
        timing_fit = abs(timing_lag_months) <= episode.timing_tolerance_months
        low_coverage_context = observed_peak.interpretation_status != "standard"

        if peak_hit and timing_fit and expected_group_hit:
            outcome = "hit"
        elif peak_hit or expected_group_hit:
            outcome = "partial"
        else:
            outcome = "miss"
        if low_coverage_context and outcome == "miss":
            outcome = "miss_low_coverage_context"

        output.append(
            ValidationEpisodeResultRecord(
                episode_id=episode.episode_id,
                country=episode.country,
                period_start=episode.period_start,
                period_end=episode.period_end,
                expected_peak_period=episode.expected_peak_period,
                expected_total_reaction=episode.expected_total_reaction,
                expected_groups=episode.expected_groups,
                data_available=True,
                observed_peak_period=observed_peak.period_label,
                observed_peak_score=round(observed_peak.fusion_score, 2),
                observed_peak_stage=observed_peak.stage,
                peak_hit=peak_hit,
                peak_gap_points=peak_gap_points,
                timing_lag_months=timing_lag_months,
                timing_fit=timing_fit,
                expected_group_hit=expected_group_hit,
                group_match_ratio=group_match_ratio,
                low_coverage_context=low_coverage_context,
                outcome=outcome,
            )
        )
    return output


def compute_validation_ranking(
    *,
    total_records: list[FusionTotalScoreRecord],
    expected_ranking: list[str],
) -> tuple[list[ValidationRankingRecord], float, bool]:
    """
    Evaluate cross-country ranking plausibility for current snapshot.

    Traceability:
    - PSwR-077
    - ALG-026
    """
    if not total_records:
        return [], 0.0, False

    sorted_records = sorted(total_records, key=lambda item: item.fusion_score, reverse=True)
    expected_rank_map = {country: rank for rank, country in enumerate(expected_ranking, start=1)}
    output: list[ValidationRankingRecord] = []
    max_abs_delta = 0
    sum_abs_delta = 0
    for actual_rank, item in enumerate(sorted_records, start=1):
        expected_rank = expected_rank_map.get(item.country, len(expected_rank_map) + 1)
        delta = actual_rank - expected_rank
        abs_delta = abs(delta)
        max_abs_delta = max(max_abs_delta, abs_delta)
        sum_abs_delta += abs_delta
        output.append(
            ValidationRankingRecord(
                country=item.country,
                fusion_score=round(item.fusion_score, 2),
                actual_rank=actual_rank,
                expected_rank=expected_rank,
                rank_delta=delta,
                plausible_rank=abs_delta <= 1,
            )
        )

    count = len(sorted_records)
    max_possible_delta = sum(abs((idx + 1) - (count - idx)) for idx in range(count))
    if max_possible_delta <= 0:
        fit_score = 1.0
    else:
        fit_score = max(0.0, 1.0 - (sum_abs_delta / float(max_possible_delta)))
    ranking_plausible = max_abs_delta <= 1
    return output, round(fit_score, 4), ranking_plausible


def compute_layer_diagnostics(
    *,
    group_records: list[FusionGroupScoreRecord],
    total_records: list[FusionTotalScoreRecord],
    source_signals: list[FusionSourceSignalRecord],
    group_weights: dict[str, float],
    group_activation_threshold: float,
    dominance_share_threshold: float,
    market_food_dominance_threshold: float,
    structural_outlier_gap: float,
    event_stale_days: int,
    freshness_model: dict[str, dict[str, float]] | None = None,
    event_fresh_boost_factor: float = 1.0,
    dynamic_layer_readiness_min_share: float = 0.5,
    dynamic_groups: list[str] | None = None,
) -> list[ValidationLayerDiagnosticRecord]:
    """
    Build analyst-focused layer diagnostics for snapshot review.

    Traceability:
    - PSwR-081
    - PSwR-083
    - PSwR-085
    - PSwR-089
    - PSwR-094
    - PSwR-095
    - PSwR-096
    - PM-051
    - ALG-027
    - ALG-029
    - ALG-030
    - ALG-035
    - PM-047
    """
    if dynamic_groups is None:
        dynamic_groups = ["event", "narrative", "governance", "shock", "displacement"]

    by_country: dict[str, list[FusionGroupScoreRecord]] = {}
    for item in group_records:
        by_country.setdefault(item.country, []).append(item)
    fusion_score_by_country = {item.country: item.fusion_score for item in total_records}
    stale_event_by_country: dict[str, bool] = {}
    for item in source_signals:
        if item.group != "event":
            continue
        stale_event_by_country[item.country] = stale_event_by_country.get(item.country, False) or (
            item.age_days > event_stale_days
        )

    freshness_group_records = compute_snapshot_freshness_groups(
        source_signals=source_signals,
        group_records=group_records,
        group_weights=group_weights,
        freshness_model=freshness_model,
        event_fresh_boost_factor=event_fresh_boost_factor,
    )
    freshness_by_country: dict[str, list[ValidationFreshnessGroupRecord]] = {}
    for item in freshness_group_records:
        freshness_by_country.setdefault(item.country, []).append(item)

    raw_output: list[dict[str, float | int | bool | str | None]] = []
    structural_values: list[float] = []
    for country, records in sorted(by_country.items()):
        available = [
            item
            for item in records
            if item.status in {"ok", "limited"} and item.group_score is not None
        ]
        weighted_points: dict[str, float] = {}
        for item in available:
            group_weight = float(group_weights.get(item.group, 1.0))
            weighted_points[item.group] = max(0.0, group_weight * float(item.group_score))
        total_weighted_points = sum(weighted_points.values())
        dominant_group = max(weighted_points, key=weighted_points.get) if weighted_points else None
        dominant_share = (
            weighted_points[dominant_group] / total_weighted_points
            if dominant_group and total_weighted_points > 0
            else 0.0
        )
        structural_score = next(
            (float(item.group_score) for item in available if item.group == "structural"),
            None,
        )
        governance_score = next(
            (float(item.group_score) for item in available if item.group == "governance"),
            None,
        )
        if structural_score is not None:
            structural_values.append(structural_score)

        active_group_count = len(
            [item for item in available if float(item.group_score) >= group_activation_threshold]
        )
        available_group_count = len(available)
        layer_support_ratio = (
            round(active_group_count / float(available_group_count), 4)
            if available_group_count > 0
            else 0.0
        )
        support_profile = "broad" if active_group_count >= 3 else "narrow"
        structural_contribution_share = (
            weighted_points.get("structural", 0.0) / total_weighted_points
            if total_weighted_points > 0
            else 0.0
        )
        governance_contribution_share = (
            weighted_points.get("governance", 0.0) / total_weighted_points
            if total_weighted_points > 0
            else 0.0
        )
        freshness_items = freshness_by_country.get(country, [])
        fresh_signal_count = sum(item.fresh_signal_count for item in freshness_items)
        aging_signal_count = sum(item.aging_signal_count for item in freshness_items)
        stale_signal_count = sum(item.stale_signal_count for item in freshness_items)
        fresh_groups = [item for item in freshness_items if item.freshness_class == "fresh"]
        aging_groups = [item for item in freshness_items if item.freshness_class == "aging"]
        stale_groups = [item for item in freshness_items if item.freshness_class == "stale"]

        fresh_points = sum(item.contribution_points for item in fresh_groups)
        aging_points = sum(item.contribution_points for item in aging_groups)
        stale_points = sum(item.contribution_points for item in stale_groups)
        total_points = fresh_points + aging_points + stale_points
        fresh_share = fresh_points / total_points if total_points > 0 else 0.0
        aging_share = aging_points / total_points if total_points > 0 else 0.0
        stale_share = stale_points / total_points if total_points > 0 else 0.0

        fresh_support_profile = (
            "broad" if len(fresh_groups) >= 3 else ("narrow" if len(fresh_groups) >= 1 else "none")
        )
        stale_support_profile = (
            "broad" if len(stale_groups) >= 3 else ("narrow" if len(stale_groups) >= 1 else "none")
        )

        dominant_fresh_group = (
            max(fresh_groups, key=lambda item: item.contribution_points).group
            if fresh_groups
            else None
        )
        dominant_aging_group = (
            max(aging_groups, key=lambda item: item.contribution_points).group
            if aging_groups
            else None
        )
        dominant_stale_group = (
            max(stale_groups, key=lambda item: item.contribution_points).group
            if stale_groups
            else None
        )
        latest_fresh_observation_date = None
        for entry in freshness_items:
            if entry.last_fresh_observation_date is None:
                continue
            if latest_fresh_observation_date is None or entry.last_fresh_observation_date > latest_fresh_observation_date:
                latest_fresh_observation_date = entry.last_fresh_observation_date

        dynamic_items = [
            item
            for item in freshness_items
            if item.group in dynamic_groups and item.status in {"ok", "limited"}
        ]
        dynamic_fresh_share = (
            len([item for item in dynamic_items if item.freshness_class == "fresh"])
            / float(len(dynamic_items))
            if dynamic_items
            else 0.0
        )
        dynamic_layer_readiness = dynamic_fresh_share >= dynamic_layer_readiness_min_share
        governance_freshness = next(
            (item for item in freshness_items if item.group == "governance"),
            None,
        )
        governance_low_freshness_flag = bool(
            governance_freshness is not None
            and governance_freshness.freshness_class == "stale"
        )
        governance_instability_flag = bool(
            governance_score is not None and governance_score >= group_activation_threshold
        )

        raw_output.append(
            {
                "country": country,
                "fusion_score": round(float(fusion_score_by_country.get(country, 0.0)), 2),
                "dominant_group": dominant_group,
                "dominant_group_share": round(dominant_share, 4),
                "dominance_flag": dominant_share >= dominance_share_threshold,
                "market_food_dominance_flag": (
                    dominant_group == "market_food"
                    and dominant_share >= market_food_dominance_threshold
                ),
                "event_stale_flag": stale_event_by_country.get(country, False),
                "governance_score": round(governance_score, 2) if governance_score is not None else None,
                "governance_contribution_share": round(governance_contribution_share, 4),
                "governance_instability_flag": governance_instability_flag,
                "governance_low_freshness_flag": governance_low_freshness_flag,
                "structural_score": round(structural_score, 2) if structural_score is not None else None,
                "structural_contribution_share": round(structural_contribution_share, 4),
                "active_group_count": active_group_count,
                "available_group_count": available_group_count,
                "layer_support_ratio": layer_support_ratio,
                "support_profile": support_profile,
                "fresh_signal_count": fresh_signal_count,
                "aging_signal_count": aging_signal_count,
                "stale_signal_count": stale_signal_count,
                "fresh_group_count": len(fresh_groups),
                "aging_group_count": len(aging_groups),
                "stale_group_count": len(stale_groups),
                "fresh_contribution_share": round(fresh_share, 4),
                "aging_contribution_share": round(aging_share, 4),
                "stale_contribution_share": round(stale_share, 4),
                "fresh_support_profile": fresh_support_profile,
                "stale_support_profile": stale_support_profile,
                "dominant_fresh_group": dominant_fresh_group,
                "dominant_aging_group": dominant_aging_group,
                "dominant_stale_group": dominant_stale_group,
                "dynamic_layer_readiness": dynamic_layer_readiness,
                "latest_fresh_observation_date": latest_fresh_observation_date,
            }
        )

    structural_median = median(structural_values) if structural_values else None
    output: list[ValidationLayerDiagnosticRecord] = []
    for item in raw_output:
        structural_score = item["structural_score"]
        structural_outlier = bool(
            structural_score is not None
            and structural_median is not None
            and float(structural_score) >= float(structural_median) + structural_outlier_gap
        )
        output.append(
            ValidationLayerDiagnosticRecord(
                country=str(item["country"]),
                fusion_score=float(item["fusion_score"]),
                dominant_group=str(item["dominant_group"]) if item["dominant_group"] else None,
                dominant_group_share=float(item["dominant_group_share"]),
                dominance_flag=bool(item["dominance_flag"]),
                market_food_dominance_flag=bool(item["market_food_dominance_flag"]),
                event_stale_flag=bool(item["event_stale_flag"]),
                governance_score=(
                    float(item["governance_score"])
                    if item["governance_score"] is not None
                    else None
                ),
                governance_contribution_share=float(item["governance_contribution_share"]),
                governance_instability_flag=bool(item["governance_instability_flag"]),
                governance_low_freshness_flag=bool(item["governance_low_freshness_flag"]),
                structural_score=float(structural_score) if structural_score is not None else None,
                structural_outlier_flag=structural_outlier,
                structural_contribution_share=float(item["structural_contribution_share"]),
                active_group_count=int(item["active_group_count"]),
                available_group_count=int(item["available_group_count"]),
                layer_support_ratio=float(item["layer_support_ratio"]),
                support_profile=str(item["support_profile"]),
                fresh_signal_count=int(item["fresh_signal_count"]),
                aging_signal_count=int(item["aging_signal_count"]),
                stale_signal_count=int(item["stale_signal_count"]),
                fresh_group_count=int(item["fresh_group_count"]),
                aging_group_count=int(item["aging_group_count"]),
                stale_group_count=int(item["stale_group_count"]),
                fresh_contribution_share=float(item["fresh_contribution_share"]),
                aging_contribution_share=float(item["aging_contribution_share"]),
                stale_contribution_share=float(item["stale_contribution_share"]),
                fresh_support_profile=str(item["fresh_support_profile"]),
                stale_support_profile=str(item["stale_support_profile"]),
                dominant_fresh_group=(
                    str(item["dominant_fresh_group"])
                    if item["dominant_fresh_group"] is not None
                    else None
                ),
                dominant_aging_group=(
                    str(item["dominant_aging_group"])
                    if item["dominant_aging_group"] is not None
                    else None
                ),
                dominant_stale_group=(
                    str(item["dominant_stale_group"])
                    if item["dominant_stale_group"] is not None
                    else None
                ),
                dynamic_layer_readiness=bool(item["dynamic_layer_readiness"]),
                latest_fresh_observation_date=item["latest_fresh_observation_date"],
            )
        )
    return sorted(output, key=lambda record: record.country)


def _derive_operational_freshness_status(
    *,
    fresh_contribution_share: float,
    stale_contribution_share: float,
    dynamic_layer_readiness: bool,
) -> str:
    """
    Compact readiness label for operational freshness in comparative views.

    Traceability:
    - PSwR-098
    - PSwR-099
    - ALG-040
    """
    if stale_contribution_share >= 0.5:
        return "stale_attention"
    if dynamic_layer_readiness and fresh_contribution_share >= 0.6:
        return "fresh_operational"
    if fresh_contribution_share >= 0.35:
        return "mixed_watch"
    return "aging_watch"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _estimate_peak_width(
    *,
    scores: list[float],
    peak_index: int,
    prominence: float,
) -> int:
    if not scores:
        return 0
    if prominence <= 0:
        return 1
    threshold = scores[peak_index] - (0.5 * prominence)
    left = peak_index
    right = peak_index
    while left > 0 and scores[left - 1] >= threshold:
        left -= 1
    while right < len(scores) - 1 and scores[right + 1] >= threshold:
        right += 1
    return (right - left) + 1


def _detect_country_peak_candidates(
    *,
    country: str,
    history: list[FusionHistoricalTotalScoreRecord],
    top_peak_count: int,
    prominence_min: float,
    min_rise: float,
    min_fall: float,
    min_separation_periods: int,
    quality_floor: float,
) -> list[_PeakCandidate]:
    if top_peak_count <= 0:
        raise ValueError("top_peak_count must be > 0")
    if not history:
        return []

    scores = [float(item.fusion_score) for item in history]
    raw_candidates: list[_PeakCandidate] = []
    last_index = len(history) - 1
    for index, item in enumerate(history):
        current = scores[index]
        left = scores[index - 1] if index > 0 else None
        right = scores[index + 1] if index < last_index else None

        if left is None and right is None:
            continue
        if left is None:
            local_max = right is not None and current > right
        elif right is None:
            local_max = current > left
        else:
            local_max = current >= left and current >= right and (current > left or current > right)
        if not local_max:
            continue

        compare_left = left if left is not None else current
        compare_right = right if right is not None else current
        prominence = current - max(compare_left, compare_right)
        rise = current - left if left is not None else 0.0
        fall = current - right if right is not None else 0.0

        if prominence < prominence_min:
            continue
        if left is not None and rise < min_rise:
            continue
        if right is not None and fall < min_fall:
            continue

        width = _estimate_peak_width(scores=scores, peak_index=index, prominence=prominence)
        quality_score = (
            (0.55 * prominence)
            + (0.2 * max(rise, 0.0))
            + (0.15 * max(fall, 0.0))
            + (0.1 * min(width, 5))
        )
        if quality_score < quality_floor:
            continue

        raw_candidates.append(
            _PeakCandidate(
                country=country,
                index=index,
                period_label=str(item.period_label),
                target_period_end=item.target_period_end,
                fusion_score=round(current, 2),
                stage=str(item.stage),
                trend=str(item.trend),
                confidence_score=round(float(item.confidence_score), 2),
                confidence_level=str(item.confidence_level),
                dominant_group=str(item.dominant_group) if item.dominant_group else None,
                top_positive_group_1=str(item.top_positive_group_1) if item.top_positive_group_1 else None,
                strongest_change_group=(
                    str(item.strongest_change_group) if item.strongest_change_group else None
                ),
                interpretation_status=str(item.interpretation_status),
                prominence_score=round(prominence, 4),
                peak_width_periods=width,
                rise_slope=round(rise, 4),
                fall_slope=round(fall, 4),
                separation_periods=len(history),
                peak_quality_score=round(quality_score, 4),
            )
        )

    # Fallback: always keep at least one analytically visible peak candidate.
    if not raw_candidates:
        best_index = max(range(len(history)), key=lambda idx: (scores[idx], history[idx].target_period_end))
        best = history[best_index]
        raw_candidates.append(
            _PeakCandidate(
                country=country,
                index=best_index,
                period_label=str(best.period_label),
                target_period_end=best.target_period_end,
                fusion_score=round(float(best.fusion_score), 2),
                stage=str(best.stage),
                trend=str(best.trend),
                confidence_score=round(float(best.confidence_score), 2),
                confidence_level=str(best.confidence_level),
                dominant_group=str(best.dominant_group) if best.dominant_group else None,
                top_positive_group_1=str(best.top_positive_group_1) if best.top_positive_group_1 else None,
                strongest_change_group=(
                    str(best.strongest_change_group) if best.strongest_change_group else None
                ),
                interpretation_status=str(best.interpretation_status),
                prominence_score=0.0,
                peak_width_periods=1,
                rise_slope=0.0,
                fall_slope=0.0,
                separation_periods=len(history),
                peak_quality_score=round(float(best.fusion_score) * 0.02, 4),
            )
        )

    ranked = sorted(
        raw_candidates,
        key=lambda item: (item.peak_quality_score, item.fusion_score, item.target_period_end),
        reverse=True,
    )
    selected: list[_PeakCandidate] = []
    min_gap = max(0, int(min_separation_periods))
    for candidate in ranked:
        if any(abs(candidate.index - chosen.index) <= min_gap for chosen in selected):
            continue
        selected.append(candidate)
        if len(selected) >= top_peak_count:
            break

    if len(selected) < top_peak_count:
        for index, item in enumerate(history):
            if any(existing.index == index for existing in ranked):
                continue
            current = scores[index]
            left = scores[index - 1] if index > 0 else current
            right = scores[index + 1] if index < len(scores) - 1 else current
            prominence = max(0.0, current - max(left, right))
            rise = max(0.0, current - left)
            fall = max(0.0, current - right)
            width = _estimate_peak_width(scores=scores, peak_index=index, prominence=prominence)
            quality_score = (
                (0.55 * prominence)
                + (0.2 * rise)
                + (0.15 * fall)
                + (0.1 * min(width, 5))
                + (0.01 * current)
            )
            ranked.append(
                _PeakCandidate(
                    country=country,
                    index=index,
                    period_label=str(item.period_label),
                    target_period_end=item.target_period_end,
                    fusion_score=round(current, 2),
                    stage=str(item.stage),
                    trend=str(item.trend),
                    confidence_score=round(float(item.confidence_score), 2),
                    confidence_level=str(item.confidence_level),
                    dominant_group=str(item.dominant_group) if item.dominant_group else None,
                    top_positive_group_1=str(item.top_positive_group_1) if item.top_positive_group_1 else None,
                    strongest_change_group=(
                        str(item.strongest_change_group) if item.strongest_change_group else None
                    ),
                    interpretation_status=str(item.interpretation_status),
                    prominence_score=round(prominence, 4),
                    peak_width_periods=width,
                    rise_slope=round(rise, 4),
                    fall_slope=round(fall, 4),
                    separation_periods=len(history),
                    peak_quality_score=round(quality_score, 4),
                )
            )
        ranked = sorted(
            ranked,
            key=lambda item: (item.peak_quality_score, item.fusion_score, item.target_period_end),
            reverse=True,
        )
        for candidate in ranked:
            if any(chosen.index == candidate.index for chosen in selected):
                continue
            if any(abs(candidate.index - chosen.index) <= min_gap for chosen in selected):
                continue
            selected.append(candidate)
            if len(selected) >= top_peak_count:
                break
        if len(selected) < top_peak_count:
            for candidate in ranked:
                if any(chosen.index == candidate.index for chosen in selected):
                    continue
                selected.append(candidate)
                if len(selected) >= top_peak_count:
                    break

    if not selected:
        selected = ranked[:1]

    finalized: list[_PeakCandidate] = []
    for candidate in selected:
        distances = [abs(candidate.index - other.index) for other in selected if other is not candidate]
        separation = min(distances) if distances else len(history)
        finalized.append(
            _PeakCandidate(
                country=candidate.country,
                index=candidate.index,
                period_label=candidate.period_label,
                target_period_end=candidate.target_period_end,
                fusion_score=candidate.fusion_score,
                stage=candidate.stage,
                trend=candidate.trend,
                confidence_score=candidate.confidence_score,
                confidence_level=candidate.confidence_level,
                dominant_group=candidate.dominant_group,
                top_positive_group_1=candidate.top_positive_group_1,
                strongest_change_group=candidate.strongest_change_group,
                interpretation_status=candidate.interpretation_status,
                prominence_score=candidate.prominence_score,
                peak_width_periods=candidate.peak_width_periods,
                rise_slope=candidate.rise_slope,
                fall_slope=candidate.fall_slope,
                separation_periods=separation,
                peak_quality_score=candidate.peak_quality_score,
            )
        )
    return sorted(
        finalized,
        key=lambda item: (item.peak_quality_score, item.fusion_score, item.target_period_end),
        reverse=True,
    )


def _parse_confidence_value(value: object, *, default: float = 0.6) -> float:
    raw = str(value or "").strip().lower()
    if not raw:
        return default
    textual = {
        "very_high": 0.9,
        "high": 0.8,
        "medium": 0.62,
        "low": 0.4,
        "very_low": 0.25,
    }
    if raw in textual:
        return textual[raw]
    try:
        return _clamp(float(raw), 0.0, 1.0)
    except ValueError:
        return default


def _normalize_relevance_groups(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    normalized = raw.replace(";", "|").replace(",", "|")
    parts: list[str] = []
    seen: set[str] = set()
    for token in normalized.split("|"):
        group = token.strip().lower()
        if not group or group in seen:
            continue
        seen.add(group)
        parts.append(group)
    return "|".join(parts)


def _parse_group_set(value: object) -> set[str]:
    normalized = _normalize_relevance_groups(value)
    if not normalized:
        return set()
    return {token for token in normalized.split("|") if token}


def load_event_registry(path: Path) -> list[ValidationEventRegistryRecord]:
    """
    Load analyst event-registry records for V4.3.2.

    Traceability:
    - PSwR-113
    - PSwR-114
    - PM-063
    - PM-064
    - ALG-048
    """
    if not path.exists() or not path.is_file():
        return []

    rows: list[ValidationEventRegistryRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            event_id = str(row.get("event_id", "")).strip() or f"event_{index:03d}"
            country = str(row.get("country", "")).strip()
            if not country:
                continue

            start_raw = (
                str(row.get("start_date", "")).strip()
                or str(row.get("period_start", "")).strip()
            )
            end_raw = (
                str(row.get("end_date", "")).strip()
                or str(row.get("period_end", "")).strip()
            )
            if not start_raw or not end_raw:
                continue
            try:
                start_date = _parse_date(start_raw)
                end_date = _parse_date(end_raw)
            except ValueError:
                continue
            if end_date < start_date:
                continue

            expected_start_raw = str(row.get("expected_peak_window_start", "")).strip()
            expected_end_raw = str(row.get("expected_peak_window_end", "")).strip()
            if expected_start_raw and expected_end_raw:
                try:
                    expected_start = _parse_date(expected_start_raw)
                    expected_end = _parse_date(expected_end_raw)
                except ValueError:
                    expected_start = start_date
                    expected_end = end_date
            else:
                expected_start = start_date
                expected_end = end_date
            if expected_end < expected_start:
                expected_start = start_date
                expected_end = end_date

            rows.append(
                ValidationEventRegistryRecord(
                    event_id=event_id,
                    country=country,
                    title=str(row.get("title", "")).strip() or event_id,
                    start_date=start_date,
                    end_date=end_date,
                    event_type=str(row.get("event_type", "")).strip() or "unspecified",
                    summary=str(row.get("summary", "")).strip(),
                    source_category=str(row.get("source_category", "")).strip() or "analyst_registry",
                    source_reference=str(row.get("source_reference", "")).strip() or "not_specified",
                    confidence=round(
                        _parse_confidence_value(row.get("confidence"), default=0.6),
                        4,
                    ),
                    relevance_groups=_normalize_relevance_groups(row.get("relevance_groups", "")),
                    expected_effect_direction=str(row.get("expected_effect_direction", "")).strip()
                    or "unspecified",
                    expected_peak_window_start=expected_start,
                    expected_peak_window_end=expected_end,
                    notes=str(row.get("notes", "")).strip(),
                )
            )

    return sorted(rows, key=lambda item: (item.country, item.start_date, item.event_id))


def _registry_to_marker_records(
    registry_rows: list[ValidationEventRegistryRecord],
) -> list[ValidationEventMarkerRecord]:
    marker_rows: list[ValidationEventMarkerRecord] = []
    for item in registry_rows:
        marker_rows.append(
            ValidationEventMarkerRecord(
                marker_id=item.event_id,
                country=item.country,
                period_start=item.expected_peak_window_start,
                period_end=item.expected_peak_window_end,
                event_label=item.title,
                event_type=item.event_type,
                support_weight=round(_clamp(item.confidence, 0.0, 1.0), 4),
                support_confidence=round(_clamp(item.confidence, 0.0, 1.0), 4),
                provenance=item.source_category or "analyst_registry",
            )
        )
    return sorted(marker_rows, key=lambda item: (item.country, item.period_start, item.marker_id))


def _load_legacy_event_marker_registry(path: Path) -> list[ValidationEventMarkerRecord]:
    if not path.exists() or not path.is_file():
        return []

    rows: list[ValidationEventMarkerRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            marker_id = str(row.get("marker_id", "")).strip() or f"marker_{index:03d}"
            country = str(row.get("country", "")).strip()
            if not country:
                continue
            period_start_raw = str(row.get("period_start", "")).strip()
            period_end_raw = str(row.get("period_end", "")).strip()
            if not period_start_raw or not period_end_raw:
                continue
            try:
                period_start = _parse_date(period_start_raw)
                period_end = _parse_date(period_end_raw)
            except ValueError:
                continue
            if period_end < period_start:
                continue
            try:
                support_weight = float(str(row.get("support_weight", "0.7")).strip())
            except ValueError:
                support_weight = 0.7
            try:
                support_confidence = float(str(row.get("support_confidence", "0.75")).strip())
            except ValueError:
                support_confidence = 0.75
            rows.append(
                ValidationEventMarkerRecord(
                    marker_id=marker_id,
                    country=country,
                    period_start=period_start,
                    period_end=period_end,
                    event_label=str(row.get("event_label", "")).strip() or marker_id,
                    event_type=str(row.get("event_type", "")).strip() or "unspecified",
                    support_weight=round(_clamp(support_weight, 0.0, 1.0), 4),
                    support_confidence=round(_clamp(support_confidence, 0.0, 1.0), 4),
                    provenance=str(row.get("provenance", "")).strip() or "analyst_annotation",
                )
            )
    return sorted(rows, key=lambda item: (item.country, item.period_start, item.marker_id))


def load_event_marker_registry(path: Path) -> list[ValidationEventMarkerRecord]:
    """
    Load optional analyst event-marker registry.

    Traceability:
    - PSwR-106
    - PM-060
    - ALG-043
    """
    registry_rows = load_event_registry(path)
    if registry_rows:
        return _registry_to_marker_records(registry_rows)
    return _load_legacy_event_marker_registry(path)


def _resolve_peak_event_support(
    *,
    country: str,
    peak_date: date,
    event_markers_by_country: dict[str, list[ValidationEventMarkerRecord]],
    weak_threshold: float,
    strong_threshold: float,
) -> tuple[str, bool, list[ValidationEventMarkerRecord], float, float]:
    markers = [
        marker
        for marker in event_markers_by_country.get(country, [])
        if marker.period_start <= peak_date <= marker.period_end
    ]
    if not markers:
        return ("not_event_validated", False, [], 0.0, 0.0)
    support_weight = max(marker.support_weight for marker in markers)
    support_confidence = max(marker.support_confidence for marker in markers)
    if support_weight >= strong_threshold and support_confidence >= strong_threshold:
        status = "event_supported"
    elif support_weight >= weak_threshold:
        status = "weakly_supported"
    else:
        status = "not_event_validated"
    return (status, status == "event_supported", markers, support_weight, support_confidence)


def _derive_peak_confidence_level(score: float) -> str:
    if score >= 0.67:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _derive_trajectory_profile(
    *,
    dominant_peak_group: str | None,
    peak_count: int,
    event_supported_peak_ratio: float,
    globally_co_moving_peak_ratio: float,
    model_driven_peak_ratio: float,
    country_specific_peak_ratio: float,
    mean_peak_confidence_score: float,
    support_profile: str,
    year_mean_score: float,
) -> str:
    if globally_co_moving_peak_ratio >= 0.6:
        return "globally_co_moving"
    if event_supported_peak_ratio >= 0.4 and peak_count >= 2:
        return "event-spiking"
    if dominant_peak_group == "governance":
        return "governance-heavy"
    if dominant_peak_group == "structural" and year_mean_score >= 45.0:
        return "structurally_elevated"
    if support_profile == "broad" and mean_peak_confidence_score >= 0.55:
        return "broad_multi-layer_stress"
    if year_mean_score >= 55.0 and peak_count <= 2:
        return "baseline-high"
    if model_driven_peak_ratio >= 0.5 and country_specific_peak_ratio < 0.35:
        return "weak_country_specificity"
    return "mixed_profile"


def compute_country_profile_comparison(
    *,
    total_records: list[FusionTotalScoreRecord],
    historical_total_records: list[FusionHistoricalTotalScoreRecord],
    historical_group_records: list[FusionHistoricalGroupScoreRecord],
    layer_diagnostics: list[ValidationLayerDiagnosticRecord],
    group_weights: dict[str, float],
    group_activation_threshold: float,
    high_stage_threshold: float,
    top_peak_count: int = 3,
    peak_prominence_min: float = 1.0,
    peak_min_rise: float = 0.5,
    peak_min_fall: float = 0.5,
    peak_min_separation_periods: int = 0,
    peak_quality_floor: float = 1.0,
) -> tuple[
    list[ValidationCountryProfileRecord],
    list[ValidationCountryPeakPhaseRecord],
    list[ValidationCountryGroupProfileRecord],
    list[ValidationRankingTrajectoryRecord],
]:
    """
    Compute 356-day comparative country profiles and diagnostic tables.

    Traceability:
    - PSR-024
    - PSyR-036
    - PSyR-037
    - PSyR-038
    - PSwR-098
    - PSwR-099
    - PSwR-100
    - PSwR-102
    - PM-052
    - PM-053
    - PM-054
    - ALG-036
    - ALG-037
    - ALG-038
    - ALG-039
    - ALG-040
    """
    if top_peak_count <= 0:
        raise ValueError("top_peak_count must be > 0")

    total_by_country = {record.country: record for record in total_records}
    diagnostics_by_country = {record.country: record for record in layer_diagnostics}

    historical_total_by_country: dict[str, list[FusionHistoricalTotalScoreRecord]] = defaultdict(list)
    for record in historical_total_records:
        historical_total_by_country[record.country].append(record)
    for country in historical_total_by_country:
        historical_total_by_country[country] = sorted(
            historical_total_by_country[country],
            key=lambda item: item.target_period_end,
        )

    historical_group_by_country: dict[str, list[FusionHistoricalGroupScoreRecord]] = defaultdict(list)
    historical_group_by_country_period: dict[
        tuple[str, str],
        list[FusionHistoricalGroupScoreRecord],
    ] = defaultdict(list)
    for record in historical_group_records:
        historical_group_by_country[record.country].append(record)
        historical_group_by_country_period[(record.country, record.period_label)].append(record)
    for country in historical_group_by_country:
        historical_group_by_country[country] = sorted(
            historical_group_by_country[country],
            key=lambda item: (item.target_period_end, item.group),
        )

    country_set = sorted(
        set(total_by_country)
        | set(historical_total_by_country)
        | set(diagnostics_by_country)
    )

    profile_records: list[ValidationCountryProfileRecord] = []
    peak_phase_records: list[ValidationCountryPeakPhaseRecord] = []
    group_profile_records: list[ValidationCountryGroupProfileRecord] = []

    for country in country_set:
        country_history = historical_total_by_country.get(country, [])
        if not country_history:
            continue
        score_values = [float(item.fusion_score) for item in country_history]
        deltas = [
            abs(score_values[index] - score_values[index - 1])
            for index in range(1, len(score_values))
        ]
        max_item = max(country_history, key=lambda item: float(item.fusion_score))
        min_item = min(country_history, key=lambda item: float(item.fusion_score))

        current_total = total_by_country.get(country, country_history[-1])
        diagnostic = diagnostics_by_country.get(country)
        fresh_share = float(diagnostic.fresh_contribution_share) if diagnostic else 0.0
        stale_share = float(diagnostic.stale_contribution_share) if diagnostic else 0.0
        dynamic_ready = bool(diagnostic.dynamic_layer_readiness) if diagnostic else False
        operational_status = _derive_operational_freshness_status(
            fresh_contribution_share=fresh_share,
            stale_contribution_share=stale_share,
            dynamic_layer_readiness=dynamic_ready,
        )
        peak_scores = [value for value in score_values if value >= high_stage_threshold]
        peak_intensity_mean = round(mean(peak_scores), 2) if peak_scores else 0.0

        profile_records.append(
            ValidationCountryProfileRecord(
                country=country,
                current_fusion_score=round(float(current_total.fusion_score), 2),
                confidence_score=round(float(current_total.confidence_score), 2),
                confidence_level=str(current_total.confidence_level),
                operational_freshness_status=operational_status,
                fresh_contribution_share=round(fresh_share, 4),
                stale_contribution_share=round(stale_share, 4),
                dynamic_layer_readiness=dynamic_ready,
                year_max_score=round(float(max_item.fusion_score), 2),
                year_max_period=str(max_item.period_label),
                year_min_score=round(float(min_item.fusion_score), 2),
                year_min_period=str(min_item.period_label),
                year_range_score=round(float(max_item.fusion_score) - float(min_item.fusion_score), 2),
                year_mean_score=round(mean(score_values), 2),
                year_volatility_std=round(pstdev(score_values), 4) if len(score_values) > 1 else 0.0,
                year_mean_abs_delta=round(mean(deltas), 4) if deltas else 0.0,
                peak_count=len(peak_scores),
                peak_intensity_mean=peak_intensity_mean,
                dominant_group=(str(diagnostic.dominant_group) if diagnostic and diagnostic.dominant_group else None),
                support_profile=str(diagnostic.support_profile) if diagnostic else "unknown",
                fresh_support_profile=str(diagnostic.fresh_support_profile) if diagnostic else "unknown",
                stale_support_profile=str(diagnostic.stale_support_profile) if diagnostic else "unknown",
            )
        )

        peak_candidates = _detect_country_peak_candidates(
            country=country,
            history=country_history,
            top_peak_count=top_peak_count,
            prominence_min=peak_prominence_min,
            min_rise=peak_min_rise,
            min_fall=peak_min_fall,
            min_separation_periods=peak_min_separation_periods,
            quality_floor=peak_quality_floor,
        )
        for index, peak in enumerate(peak_candidates, start=1):
            peak_phase_records.append(
                ValidationCountryPeakPhaseRecord(
                    country=country,
                    peak_rank=index,
                    period_label=str(peak.period_label),
                    target_period_end=peak.target_period_end,
                    fusion_score=round(float(peak.fusion_score), 2),
                    stage=str(peak.stage),
                    trend=str(peak.trend),
                    confidence_score=round(float(peak.confidence_score), 2),
                    confidence_level=str(peak.confidence_level),
                    dominant_group=str(peak.dominant_group) if peak.dominant_group else None,
                    top_positive_group_1=(
                        str(peak.top_positive_group_1) if peak.top_positive_group_1 else None
                    ),
                    strongest_change_group=(
                        str(peak.strongest_change_group) if peak.strongest_change_group else None
                    ),
                    interpretation_status=str(peak.interpretation_status),
                    fresh_contribution_share=round(fresh_share, 4),
                    stale_contribution_share=round(stale_share, 4),
                    dynamic_layer_readiness=dynamic_ready,
                )
            )

        country_group_records = historical_group_by_country.get(country, [])
        period_labels = sorted({record.period_label for record in country_history}, key=_month_index)
        period_count = len(period_labels)
        groups = sorted({record.group for record in country_group_records})
        for group in groups:
            group_entries = [record for record in country_group_records if record.group == group]
            scored_entries = [record for record in group_entries if record.group_score is not None]
            score_series = [float(record.group_score) for record in scored_entries]
            if score_series:
                mean_score = round(mean(score_series), 2)
                max_score = round(max(score_series), 2)
                min_score = round(min(score_series), 2)
                score_range = round(max(score_series) - min(score_series), 2)
                active_period_ratio = round(
                    len([value for value in score_series if value >= group_activation_threshold])
                    / float(len(score_series)),
                    4,
                )
            else:
                mean_score = 0.0
                max_score = 0.0
                min_score = 0.0
                score_range = 0.0
                active_period_ratio = 0.0

            dominant_period_count = 0
            contribution_shares: list[float] = []
            for period_label in period_labels:
                period_records = historical_group_by_country_period.get((country, period_label), [])
                scored_period_records = [
                    item for item in period_records if item.group_score is not None and item.status in {"ok", "limited"}
                ]
                if not scored_period_records:
                    continue
                ranked_groups = sorted(
                    scored_period_records,
                    key=lambda item: float(item.group_score if item.group_score is not None else -1.0),
                    reverse=True,
                )
                if ranked_groups and ranked_groups[0].group == group:
                    dominant_period_count += 1
                weighted_total = sum(
                    float(group_weights.get(item.group, 1.0)) * float(item.group_score)
                    for item in scored_period_records
                    if item.group_score is not None
                )
                current = next((item for item in scored_period_records if item.group == group), None)
                if current is not None and current.group_score is not None and weighted_total > 0:
                    contribution_shares.append(
                        (
                            float(group_weights.get(group, 1.0)) * float(current.group_score)
                        ) / weighted_total
                    )

            group_profile_records.append(
                ValidationCountryGroupProfileRecord(
                    country=country,
                    group=group,
                    period_count=period_count,
                    observed_period_count=len(scored_entries),
                    availability_ratio=round(
                        len(scored_entries) / float(period_count),
                        4,
                    ) if period_count > 0 else 0.0,
                    mean_group_score=mean_score,
                    max_group_score=max_score,
                    min_group_score=min_score,
                    score_range=score_range,
                    active_period_ratio=active_period_ratio,
                    dominant_period_count=dominant_period_count,
                    mean_contribution_share=round(mean(contribution_shares), 4) if contribution_shares else 0.0,
                )
            )

    ranking_trajectory_records: list[ValidationRankingTrajectoryRecord] = []
    history_by_period: dict[str, list[FusionHistoricalTotalScoreRecord]] = defaultdict(list)
    for record in historical_total_records:
        history_by_period[record.period_label].append(record)
    for period_label in sorted(history_by_period.keys(), key=_month_index):
        period_records = sorted(
            history_by_period[period_label],
            key=lambda item: (float(item.fusion_score), item.country),
            reverse=True,
        )
        country_count = len(period_records)
        for index, record in enumerate(period_records, start=1):
            ranking_trajectory_records.append(
                ValidationRankingTrajectoryRecord(
                    period_label=period_label,
                    target_period_end=record.target_period_end,
                    country=record.country,
                    fusion_score=round(float(record.fusion_score), 2),
                    rank=index,
                    country_count=country_count,
                )
            )

    return (
        sorted(profile_records, key=lambda item: item.country),
        sorted(peak_phase_records, key=lambda item: (item.country, item.peak_rank)),
        sorted(group_profile_records, key=lambda item: (item.country, item.group)),
        ranking_trajectory_records,
    )


def compute_peak_attribution(
    *,
    country_profile_records: list[ValidationCountryProfileRecord],
    peak_phase_records: list[ValidationCountryPeakPhaseRecord],
    historical_total_records: list[FusionHistoricalTotalScoreRecord],
    historical_group_records: list[FusionHistoricalGroupScoreRecord],
    layer_diagnostics: list[ValidationLayerDiagnosticRecord],
    group_weights: dict[str, float],
    event_markers: list[ValidationEventMarkerRecord] | None = None,
    support_group_min_share: float = 0.12,
    country_specific_share_threshold: float = 0.4,
    global_share_warning_threshold: float = 0.55,
    model_driven_global_share_threshold: float = 0.7,
    single_group_dominance_threshold: float = 0.58,
    event_support_weak_threshold: float = 0.45,
    event_support_strong_threshold: float = 0.7,
    peak_prominence_min: float = 1.0,
    peak_min_rise: float = 0.5,
    peak_min_fall: float = 0.5,
    peak_min_separation_periods: int = 0,
    peak_quality_floor: float = 1.0,
) -> tuple[
    list[ValidationPeakAttributionRecord],
    list[ValidationPeakEventSupportRecord],
    list[ValidationTrajectoryProfileRecord],
    list[ValidationGlobalPeakSynchronizationRecord],
    dict[str, object],
]:
    """
    Build V4.3.1 peak-attribution diagnostics with global-vs-country decomposition.

    Traceability:
    - PSR-025
    - PSyR-039
    - PSyR-040
    - PSwR-105
    - PSwR-106
    - PSwR-107
    - PSwR-108
    - PSwR-109
    - PSwR-110
    - PSwR-111
    - PSwR-112
    - PM-057
    - PM-058
    - PM-059
    - PM-060
    - PM-061
    - PM-062
    - ALG-041
    - ALG-042
    - ALG-043
    - ALG-044
    - ALG-045
    - ALG-046
    - ALG-047
    """
    if not (0.0 <= support_group_min_share <= 1.0):
        raise ValueError("support_group_min_share must be in range [0, 1]")
    if not (0.0 <= country_specific_share_threshold <= 1.0):
        raise ValueError("country_specific_share_threshold must be in range [0, 1]")
    if not (0.0 <= global_share_warning_threshold <= 1.0):
        raise ValueError("global_share_warning_threshold must be in range [0, 1]")
    if not (0.0 <= model_driven_global_share_threshold <= 1.0):
        raise ValueError("model_driven_global_share_threshold must be in range [0, 1]")
    if not (0.0 <= single_group_dominance_threshold <= 1.0):
        raise ValueError("single_group_dominance_threshold must be in range [0, 1]")
    if not (0.0 <= event_support_weak_threshold <= 1.0):
        raise ValueError("event_support_weak_threshold must be in range [0, 1]")
    if not (0.0 <= event_support_strong_threshold <= 1.0):
        raise ValueError("event_support_strong_threshold must be in range [0, 1]")

    event_markers = event_markers or []
    diagnostics_by_country = {item.country: item for item in layer_diagnostics}
    profile_by_country = {item.country: item for item in country_profile_records}

    total_by_period: dict[str, list[FusionHistoricalTotalScoreRecord]] = defaultdict(list)
    historical_total_by_country: dict[str, list[FusionHistoricalTotalScoreRecord]] = defaultdict(list)
    for record in historical_total_records:
        total_by_period[record.period_label].append(record)
        historical_total_by_country[record.country].append(record)
    for country in historical_total_by_country:
        historical_total_by_country[country] = sorted(
            historical_total_by_country[country],
            key=lambda item: item.target_period_end,
        )

    global_mean_score_by_period: dict[str, float] = {}
    for period_label, records in total_by_period.items():
        global_mean_score_by_period[period_label] = (
            mean(float(item.fusion_score) for item in records) if records else 0.0
        )

    historical_group_by_country_period: dict[
        tuple[str, str], list[FusionHistoricalGroupScoreRecord]
    ] = defaultdict(list)
    for record in historical_group_records:
        historical_group_by_country_period[(record.country, record.period_label)].append(record)

    contribution_share_by_country_period: dict[tuple[str, str], dict[str, float]] = {}
    for key, records in historical_group_by_country_period.items():
        weighted: dict[str, float] = {}
        for record in records:
            if record.group_score is None or record.status not in {"ok", "limited"}:
                continue
            weighted[record.group] = float(group_weights.get(record.group, 1.0)) * float(record.group_score)
        weighted_total = sum(weighted.values())
        if weighted_total <= 0:
            contribution_share_by_country_period[key] = {}
        else:
            contribution_share_by_country_period[key] = {
                group: value / weighted_total for group, value in weighted.items()
            }

    global_group_share_by_period: dict[str, dict[str, float]] = defaultdict(dict)
    for period_label in total_by_period.keys():
        period_shares = [
            contribution_share_by_country_period.get((item.country, period_label), {})
            for item in total_by_period.get(period_label, [])
        ]
        group_keys = sorted({key for payload in period_shares for key in payload.keys()})
        for group in group_keys:
            values = [payload.get(group, 0.0) for payload in period_shares]
            global_group_share_by_period[period_label][group] = (
                mean(values) if values else 0.0
            )

    event_markers_by_country: dict[str, list[ValidationEventMarkerRecord]] = defaultdict(list)
    for marker in event_markers:
        event_markers_by_country[marker.country].append(marker)

    top_peak_count = max([item.peak_rank for item in peak_phase_records], default=3)
    candidate_by_country_period: dict[tuple[str, str], _PeakCandidate] = {}
    for country, history in historical_total_by_country.items():
        for candidate in _detect_country_peak_candidates(
            country=country,
            history=history,
            top_peak_count=top_peak_count,
            prominence_min=peak_prominence_min,
            min_rise=peak_min_rise,
            min_fall=peak_min_fall,
            min_separation_periods=peak_min_separation_periods,
            quality_floor=peak_quality_floor,
        ):
            candidate_by_country_period[(country, candidate.period_label)] = candidate

    peak_attribution_records: list[ValidationPeakAttributionRecord] = []
    peak_event_support_records: list[ValidationPeakEventSupportRecord] = []

    sorted_peaks = sorted(peak_phase_records, key=lambda item: (item.country, item.peak_rank))
    for peak in sorted_peaks:
        key = (peak.country, peak.period_label)
        contribution_shares = contribution_share_by_country_period.get(key, {})
        ranked_groups = sorted(
            contribution_shares.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        dominant_group = ranked_groups[0][0] if ranked_groups else peak.dominant_group
        second_group = ranked_groups[1][0] if len(ranked_groups) > 1 else None
        dominant_share = ranked_groups[0][1] if ranked_groups else 0.0
        support_group_count = len(
            [item for item in contribution_shares.values() if item >= support_group_min_share]
        )
        available_group_count = len(contribution_shares)
        support_breadth_ratio = (
            support_group_count / float(available_group_count)
            if available_group_count > 0
            else 0.0
        )
        support_profile = "broad" if support_breadth_ratio >= 0.45 else "narrow"

        diagnostic = diagnostics_by_country.get(peak.country)
        fresh_share = float(diagnostic.fresh_contribution_share) if diagnostic else 0.0
        stale_share = float(diagnostic.stale_contribution_share) if diagnostic else 0.0

        peak_score = float(peak.fusion_score)
        global_period_mean = global_mean_score_by_period.get(peak.period_label, peak_score)
        global_component_score = min(peak_score, global_period_mean)
        country_specific_component_score = max(0.0, peak_score - global_component_score)
        global_share = (global_component_score / peak_score) if peak_score > 0 else 0.0
        country_specific_share = (
            country_specific_component_score / peak_score if peak_score > 0 else 0.0
        )

        market_food_share = contribution_shares.get("market_food", 0.0)
        market_food_global_pressure = global_group_share_by_period.get(peak.period_label, {}).get(
            "market_food",
            0.0,
        )
        market_food_local_pressure = max(0.0, market_food_share - market_food_global_pressure)

        (
            event_support_status,
            event_supported_flag,
            event_support_markers,
            event_support_weight,
            event_support_confidence,
        ) = _resolve_peak_event_support(
            country=peak.country,
            peak_date=peak.target_period_end,
            event_markers_by_country=event_markers_by_country,
            weak_threshold=event_support_weak_threshold,
            strong_threshold=event_support_strong_threshold,
        )

        if event_support_status == "event_supported" and country_specific_share >= country_specific_share_threshold:
            attribution_label = "event_supported_peak"
        elif (
            event_support_status == "weakly_supported"
            and country_specific_share >= (0.5 * country_specific_share_threshold)
        ):
            attribution_label = "weakly_supported_peak"
        elif global_share >= model_driven_global_share_threshold and not event_supported_flag:
            attribution_label = "model_driven_peak"
        elif global_share >= global_share_warning_threshold:
            attribution_label = "globally_co_moving_peak"
        elif country_specific_share >= country_specific_share_threshold:
            attribution_label = "country_specific_peak"
        else:
            attribution_label = "global_background_stress_peak"

        event_component = (
            1.0
            if event_support_status == "event_supported"
            else (0.62 if event_support_status == "weakly_supported" else 0.35)
        )
        dominance_resilience = (
            1.0
            - _clamp(
                (
                    dominant_share - single_group_dominance_threshold
                )
                / max(1e-9, 1.0 - single_group_dominance_threshold),
                0.0,
                1.0,
            )
        )
        global_dependence_penalty = _clamp(
            (
                global_share - global_share_warning_threshold
            )
            / max(1e-9, 1.0 - global_share_warning_threshold),
            0.0,
            1.0,
        )
        confidence_score = _clamp(
            (0.28 * support_breadth_ratio)
            + (0.24 * fresh_share)
            + (0.22 * event_component)
            + (0.14 * dominance_resilience)
            + (0.12 * (1.0 - global_dependence_penalty)),
            0.0,
            1.0,
        )
        confidence_level = _derive_peak_confidence_level(confidence_score)
        marker_ids = "|".join(sorted(marker.marker_id for marker in event_support_markers))
        event_label_summary = " | ".join(
            sorted({marker.event_label for marker in event_support_markers})
        )
        peak_candidate = candidate_by_country_period.get((peak.country, peak.period_label))

        peak_attribution_records.append(
            ValidationPeakAttributionRecord(
                country=peak.country,
                peak_rank=peak.peak_rank,
                period_label=peak.period_label,
                target_period_end=peak.target_period_end,
                fusion_score=round(peak_score, 2),
                prominence_score=round(
                    peak_candidate.prominence_score if peak_candidate is not None else 0.0,
                    4,
                ),
                peak_width_periods=peak_candidate.peak_width_periods if peak_candidate is not None else 1,
                rise_slope=round(peak_candidate.rise_slope if peak_candidate is not None else 0.0, 4),
                fall_slope=round(peak_candidate.fall_slope if peak_candidate is not None else 0.0, 4),
                separation_periods=peak_candidate.separation_periods if peak_candidate is not None else 0,
                peak_quality_score=round(
                    peak_candidate.peak_quality_score if peak_candidate is not None else (
                        (0.45 * peak_score)
                        + (0.3 * support_breadth_ratio * 100.0)
                        + (0.25 * confidence_score * 100.0)
                    ),
                    4,
                ),
                dominant_group=dominant_group,
                second_group=second_group,
                support_profile=support_profile,
                support_breadth_ratio=round(support_breadth_ratio, 4),
                dominant_group_share=round(dominant_share, 4),
                fresh_contribution_share=round(fresh_share, 4),
                stale_contribution_share=round(stale_share, 4),
                global_component_score=round(global_component_score, 4),
                country_specific_component_score=round(country_specific_component_score, 4),
                global_share=round(global_share, 4),
                country_specific_share=round(country_specific_share, 4),
                market_food_global_pressure=round(market_food_global_pressure, 4),
                market_food_local_pressure=round(market_food_local_pressure, 4),
                attribution_label=attribution_label,
                peak_confidence_score=round(confidence_score, 4),
                peak_confidence_level=confidence_level,
                event_support_status=event_support_status,
                event_marker_count=len(event_support_markers),
                event_marker_ids=marker_ids,
            )
        )
        peak_event_support_records.append(
            ValidationPeakEventSupportRecord(
                country=peak.country,
                period_label=peak.period_label,
                target_period_end=peak.target_period_end,
                peak_rank=peak.peak_rank,
                event_support_status=event_support_status,
                event_supported=event_supported_flag,
                event_marker_count=len(event_support_markers),
                event_marker_ids=marker_ids,
                event_support_weight=round(event_support_weight, 4),
                event_support_confidence=round(event_support_confidence, 4),
                event_label_summary=event_label_summary,
            )
        )

    peak_attribution_by_period: dict[str, list[ValidationPeakAttributionRecord]] = defaultdict(list)
    peak_attribution_by_country: dict[str, list[ValidationPeakAttributionRecord]] = defaultdict(list)
    for item in peak_attribution_records:
        peak_attribution_by_period[item.period_label].append(item)
        peak_attribution_by_country[item.country].append(item)

    synchronization_records: list[ValidationGlobalPeakSynchronizationRecord] = []
    total_country_count = len({item.country for item in country_profile_records}) or len(
        {item.country for item in peak_phase_records}
    )
    for period_label in sorted(peak_attribution_by_period.keys(), key=_month_index):
        period_items = peak_attribution_by_period[period_label]
        peak_country_count = len({item.country for item in period_items})
        peak_country_ratio = (
            peak_country_count / float(total_country_count) if total_country_count > 0 else 0.0
        )
        dominant_wave_group = None
        if period_items:
            group_counts: dict[str, int] = {}
            for item in period_items:
                if item.dominant_group is None:
                    continue
                group_counts[item.dominant_group] = group_counts.get(item.dominant_group, 0) + 1
            if group_counts:
                dominant_wave_group = max(
                    sorted(group_counts.items()),
                    key=lambda item: item[1],
                )[0]
        if peak_country_ratio >= 0.6:
            synchronization_class = "highly_synchronized_wave"
        elif peak_country_ratio >= 0.35:
            synchronization_class = "moderately_synchronized_wave"
        else:
            synchronization_class = "country_specific_wave"
        synchronization_records.append(
            ValidationGlobalPeakSynchronizationRecord(
                period_label=period_label,
                target_period_end=max(item.target_period_end for item in period_items),
                peak_country_count=peak_country_count,
                total_country_count=total_country_count,
                peak_country_ratio=round(peak_country_ratio, 4),
                peak_countries="|".join(sorted({item.country for item in period_items})),
                mean_global_share=round(mean(item.global_share for item in period_items), 4),
                mean_country_specific_share=round(
                    mean(item.country_specific_share for item in period_items),
                    4,
                ),
                mean_peak_confidence_score=round(
                    mean(item.peak_confidence_score for item in period_items),
                    4,
                ),
                dominant_wave_group=dominant_wave_group,
                synchronization_class=synchronization_class,
            )
        )

    trajectory_records: list[ValidationTrajectoryProfileRecord] = []
    for country in sorted({item.country for item in country_profile_records} | set(peak_attribution_by_country)):
        country_peaks = peak_attribution_by_country.get(country, [])
        profile = profile_by_country.get(country)
        peak_count = len(country_peaks)
        if peak_count > 0:
            event_supported_peak_ratio = len(
                [item for item in country_peaks if item.attribution_label == "event_supported_peak"]
            ) / float(peak_count)
            weakly_supported_peak_ratio = len(
                [item for item in country_peaks if item.attribution_label == "weakly_supported_peak"]
            ) / float(peak_count)
            globally_co_moving_peak_ratio = len(
                [
                    item
                    for item in country_peaks
                    if item.attribution_label in {"global_background_stress_peak", "globally_co_moving_peak"}
                ]
            ) / float(peak_count)
            model_driven_peak_ratio = len(
                [item for item in country_peaks if item.attribution_label == "model_driven_peak"]
            ) / float(peak_count)
            country_specific_peak_ratio = len(
                [
                    item
                    for item in country_peaks
                    if item.attribution_label in {"country_specific_peak", "event_supported_peak"}
                ]
            ) / float(peak_count)
            mean_global_share = mean(item.global_share for item in country_peaks)
            mean_country_specific_share = mean(
                item.country_specific_share for item in country_peaks
            )
            mean_peak_confidence_score = mean(
                item.peak_confidence_score for item in country_peaks
            )
            dominant_peak_group = None
            group_counts: dict[str, float] = {}
            for item in country_peaks:
                if item.dominant_group is None:
                    continue
                group_counts[item.dominant_group] = group_counts.get(item.dominant_group, 0.0) + item.fusion_score
            if group_counts:
                dominant_peak_group = max(
                    sorted(group_counts.items()),
                    key=lambda item: item[1],
                )[0]
        else:
            event_supported_peak_ratio = 0.0
            weakly_supported_peak_ratio = 0.0
            globally_co_moving_peak_ratio = 0.0
            model_driven_peak_ratio = 0.0
            country_specific_peak_ratio = 0.0
            mean_global_share = 0.0
            mean_country_specific_share = 0.0
            mean_peak_confidence_score = 0.0
            dominant_peak_group = None

        differentiation_flag = (
            country_specific_peak_ratio >= 0.34 and globally_co_moving_peak_ratio <= 0.55
        )
        trajectory_profile = _derive_trajectory_profile(
            dominant_peak_group=dominant_peak_group,
            peak_count=peak_count,
            event_supported_peak_ratio=event_supported_peak_ratio,
            globally_co_moving_peak_ratio=globally_co_moving_peak_ratio,
            model_driven_peak_ratio=model_driven_peak_ratio,
            country_specific_peak_ratio=country_specific_peak_ratio,
            mean_peak_confidence_score=mean_peak_confidence_score,
            support_profile=profile.support_profile if profile is not None else "unknown",
            year_mean_score=profile.year_mean_score if profile is not None else 0.0,
        )
        trajectory_records.append(
            ValidationTrajectoryProfileRecord(
                country=country,
                trajectory_profile=trajectory_profile,
                peak_count=peak_count,
                event_supported_peak_ratio=round(event_supported_peak_ratio, 4),
                weakly_supported_peak_ratio=round(weakly_supported_peak_ratio, 4),
                globally_co_moving_peak_ratio=round(globally_co_moving_peak_ratio, 4),
                model_driven_peak_ratio=round(model_driven_peak_ratio, 4),
                country_specific_peak_ratio=round(country_specific_peak_ratio, 4),
                mean_global_share=round(mean_global_share, 4),
                mean_country_specific_share=round(mean_country_specific_share, 4),
                dominant_peak_group=dominant_peak_group,
                mean_peak_confidence_score=round(mean_peak_confidence_score, 4),
                differentiation_flag=differentiation_flag,
            )
        )

    total_peak_count = len(peak_attribution_records)
    if total_peak_count > 0:
        event_supported_count = len(
            [item for item in peak_attribution_records if item.attribution_label == "event_supported_peak"]
        )
        weakly_supported_count = len(
            [item for item in peak_attribution_records if item.attribution_label == "weakly_supported_peak"]
        )
        globally_co_moving_count = len(
            [
                item
                for item in peak_attribution_records
                if item.attribution_label in {"global_background_stress_peak", "globally_co_moving_peak"}
            ]
        )
        model_driven_count = len(
            [item for item in peak_attribution_records if item.attribution_label == "model_driven_peak"]
        )
        country_specific_count = len(
            [
                item
                for item in peak_attribution_records
                if item.attribution_label in {"country_specific_peak", "event_supported_peak"}
            ]
        )
        mean_peak_confidence_score = mean(item.peak_confidence_score for item in peak_attribution_records)
    else:
        event_supported_count = 0
        weakly_supported_count = 0
        globally_co_moving_count = 0
        model_driven_count = 0
        country_specific_count = 0
        mean_peak_confidence_score = 0.0

    high_sync_count = len(
        [item for item in synchronization_records if item.synchronization_class == "highly_synchronized_wave"]
    )
    low_differentiation_country_count = len(
        [item for item in trajectory_records if not item.differentiation_flag]
    )
    market_food_global_dominance_count = len(
        [
            item
            for item in peak_attribution_records
            if item.dominant_group == "market_food" and item.global_share >= global_share_warning_threshold
        ]
    )

    summary_metrics = {
        "peak_attribution_record_count": total_peak_count,
        "event_supported_peak_count": event_supported_count,
        "weakly_supported_peak_count": weakly_supported_count,
        "globally_co_moving_peak_count": globally_co_moving_count,
        "model_driven_peak_count": model_driven_count,
        "country_specific_peak_count": country_specific_count,
        "event_supported_peak_ratio": round(
            event_supported_count / float(total_peak_count),
            4,
        )
        if total_peak_count > 0
        else 0.0,
        "weakly_supported_peak_ratio": round(
            weakly_supported_count / float(total_peak_count),
            4,
        )
        if total_peak_count > 0
        else 0.0,
        "globally_co_moving_peak_ratio": round(
            globally_co_moving_count / float(total_peak_count),
            4,
        )
        if total_peak_count > 0
        else 0.0,
        "model_driven_peak_ratio": round(
            model_driven_count / float(total_peak_count),
            4,
        )
        if total_peak_count > 0
        else 0.0,
        "country_specific_peak_ratio": round(
            country_specific_count / float(total_peak_count),
            4,
        )
        if total_peak_count > 0
        else 0.0,
        "mean_peak_confidence_score": round(mean_peak_confidence_score, 4),
        "peak_synchronization_record_count": len(synchronization_records),
        "peak_synchronization_high_count": high_sync_count,
        "trajectory_profile_record_count": len(trajectory_records),
        "trajectory_low_differentiation_country_count": low_differentiation_country_count,
        "market_food_global_dominance_peak_count": market_food_global_dominance_count,
    }

    return (
        sorted(peak_attribution_records, key=lambda item: (item.country, item.peak_rank)),
        sorted(peak_event_support_records, key=lambda item: (item.country, item.peak_rank)),
        sorted(trajectory_records, key=lambda item: item.country),
        sorted(synchronization_records, key=lambda item: _month_index(item.period_label)),
        summary_metrics,
    )


def _distance_days_to_window(target: date, *, start: date, end: date) -> int:
    if start <= target <= end:
        return 0
    if target < start:
        return (start - target).days
    return (target - end).days


def _overlap_days(start_a: date, end_a: date, start_b: date, end_b: date) -> int:
    overlap_start = max(start_a, start_b)
    overlap_end = min(end_a, end_b)
    if overlap_end < overlap_start:
        return 0
    return (overlap_end - overlap_start).days + 1


def _coverage_band(value: float) -> str:
    if value >= 0.67:
        return "high"
    if value >= 0.4:
        return "moderate"
    return "low"


def _alignment_maturity_label(value: float) -> str:
    if value >= 0.67:
        return "high"
    if value >= 0.45:
        return "medium"
    return "low"


def compute_peak_event_alignment(
    *,
    peak_attribution_records: list[ValidationPeakAttributionRecord],
    trajectory_profile_records: list[ValidationTrajectoryProfileRecord],
    event_registry_records: list[ValidationEventRegistryRecord],
    temporal_distance_days: int = 75,
    direct_match_threshold: float = 0.72,
    context_match_threshold: float = 0.56,
    weak_match_threshold: float = 0.4,
    multi_overlap_min_events: int = 2,
) -> tuple[
    list[ValidationPeakEventMatchRecord],
    list[ValidationEventCoverageSummaryRecord],
    list[ValidationCountryEventAlignmentRecord],
    dict[str, object],
]:
    """
    Compute V4.3.2 event-alignment diagnostics over detected peaks.

    Traceability:
    - PSR-026
    - PSyR-041
    - PSyR-042
    - PSyR-043
    - PSwR-115
    - PSwR-116
    - PSwR-117
    - PSwR-118
    - PSwR-123
    - PM-065
    - PM-066
    - PM-067
    - PM-068
    - PM-069
    - ALG-049
    - ALG-050
    - ALG-051
    - ALG-052
    - ALG-053
    - ALG-054
    """
    if temporal_distance_days <= 0:
        raise ValueError("temporal_distance_days must be > 0")
    if not (0.0 <= weak_match_threshold <= context_match_threshold <= direct_match_threshold <= 1.0):
        raise ValueError(
            "match thresholds must satisfy 0 <= weak <= context <= direct <= 1"
        )
    if multi_overlap_min_events < 2:
        raise ValueError("multi_overlap_min_events must be >= 2")

    trajectories_by_country = {
        item.country: item for item in trajectory_profile_records
    }
    events_by_country: dict[str, list[ValidationEventRegistryRecord]] = defaultdict(list)
    for event in event_registry_records:
        events_by_country[event.country].append(event)
    for country in events_by_country:
        events_by_country[country] = sorted(
            events_by_country[country],
            key=lambda item: (item.start_date, item.event_id),
        )

    match_records: list[ValidationPeakEventMatchRecord] = []
    for peak in sorted(
        peak_attribution_records,
        key=lambda item: (item.country, item.peak_rank, item.target_period_end),
    ):
        peak_groups = {group for group in [peak.dominant_group, peak.second_group] if group}
        trajectory = trajectories_by_country.get(peak.country)
        trajectory_profile = (
            trajectory.trajectory_profile if trajectory is not None else "unknown"
        )
        candidates: list[dict[str, object]] = []
        for event in events_by_country.get(peak.country, []):
            distance_event_days = _distance_days_to_window(
                peak.target_period_end,
                start=event.start_date,
                end=event.end_date,
            )
            distance_expected_days = _distance_days_to_window(
                peak.target_period_end,
                start=event.expected_peak_window_start,
                end=event.expected_peak_window_end,
            )
            time_distance_days = min(distance_event_days, distance_expected_days)
            overlap_days = max(
                _overlap_days(
                    peak.target_period_end,
                    peak.target_period_end,
                    event.start_date,
                    event.end_date,
                ),
                _overlap_days(
                    peak.target_period_end,
                    peak.target_period_end,
                    event.expected_peak_window_start,
                    event.expected_peak_window_end,
                ),
            )
            event_window_score = (
                1.0
                if distance_event_days == 0
                else _clamp(
                    1.0 - (distance_event_days / float(temporal_distance_days)),
                    0.0,
                    1.0,
                )
            )
            expected_window_score = (
                1.0
                if distance_expected_days == 0
                else _clamp(
                    1.0 - (distance_expected_days / float(temporal_distance_days)),
                    0.0,
                    1.0,
                )
            )
            distance_score = _clamp(
                1.0 - (time_distance_days / float(temporal_distance_days)),
                0.0,
                1.0,
            )
            temporal_score = _clamp(
                (0.46 * event_window_score)
                + (0.34 * expected_window_score)
                + (0.20 * distance_score),
                0.0,
                1.0,
            )

            event_groups = _parse_group_set(event.relevance_groups)
            if event_groups and peak_groups:
                overlap = event_groups & peak_groups
                event_overlap_ratio = len(overlap) / float(len(event_groups))
                peak_overlap_ratio = len(overlap) / float(len(peak_groups))
                thematic_score = _clamp(
                    (0.55 * event_overlap_ratio) + (0.45 * peak_overlap_ratio),
                    0.0,
                    1.0,
                )
            elif event_groups:
                thematic_score = 0.18
            else:
                thematic_score = 0.42

            effect_direction = event.expected_effect_direction.lower()
            if (
                peak.attribution_label in {"globally_co_moving_peak", "global_background_stress_peak"}
                and effect_direction in {"country_specific", "country"}
            ):
                thematic_score = _clamp(thematic_score * 0.85, 0.0, 1.0)
            if (
                peak.attribution_label in {"country_specific_peak", "event_supported_peak"}
                and effect_direction in {"global", "global_wave"}
            ):
                thematic_score = _clamp(thematic_score * 0.9, 0.0, 1.0)

            event_support_component = (
                1.0
                if peak.event_support_status == "event_supported"
                else (0.62 if peak.event_support_status == "weakly_supported" else 0.35)
            )
            support_score = _clamp(
                (0.50 * peak.peak_confidence_score)
                + (0.23 * peak.support_breadth_ratio)
                + (0.15 * event_support_component)
                + (0.12 * (1.0 - peak.stale_contribution_share)),
                0.0,
                1.0,
            )

            global_penalty = 0.0
            if peak.global_share >= 0.65 and effect_direction in {"country_specific", "country"}:
                global_penalty = 0.08
            elif peak.country_specific_share >= 0.55 and effect_direction in {"global", "global_wave"}:
                global_penalty = 0.05

            match_score = _clamp(
                (0.45 * temporal_score)
                + (0.30 * thematic_score)
                + (0.17 * support_score)
                + (0.08 * event.confidence)
                - global_penalty,
                0.0,
                1.0,
            )
            candidates.append(
                {
                    "event": event,
                    "match_score": match_score,
                    "temporal_score": temporal_score,
                    "thematic_score": thematic_score,
                    "support_score": support_score,
                    "time_distance_days": time_distance_days,
                    "overlap_days": overlap_days,
                }
            )

        candidates = sorted(
            candidates,
            key=lambda item: (
                float(item["match_score"]),
                float(item["temporal_score"]),
                float(item["thematic_score"]),
            ),
            reverse=True,
        )
        direct_candidates = [
            item
            for item in candidates
            if float(item["match_score"]) >= direct_match_threshold
            and float(item["temporal_score"]) >= 0.65
            and float(item["thematic_score"]) >= 0.35
        ]
        context_candidates = [
            item for item in candidates if float(item["match_score"]) >= context_match_threshold
        ]
        weak_candidates = [
            item for item in candidates if float(item["match_score"]) >= weak_match_threshold
        ]
        if len([item for item in context_candidates if float(item["temporal_score"]) >= 0.55]) >= multi_overlap_min_events:
            selected = [
                item
                for item in context_candidates
                if float(item["temporal_score"]) >= 0.55
            ][:3]
            match_class = "multi_event_overlap"
            base_confidence = mean(float(item["match_score"]) for item in selected[:2])
        elif direct_candidates:
            selected = [direct_candidates[0]]
            match_class = "direct_match"
            base_confidence = float(selected[0]["match_score"])
        elif context_candidates:
            selected = [context_candidates[0]]
            match_class = "plausible_context_match"
            base_confidence = float(selected[0]["match_score"]) * 0.95
        elif weak_candidates:
            selected = [weak_candidates[0]]
            match_class = "weak_match"
            base_confidence = float(selected[0]["match_score"]) * 0.82
        else:
            selected = candidates[:1]
            match_class = "no_credible_match"
            base_confidence = float(selected[0]["match_score"]) * 0.55 if selected else 0.0

        credible_match = match_class in {"direct_match", "plausible_context_match", "multi_event_overlap"}
        match_confidence = _clamp(
            (0.72 * base_confidence) + (0.28 * peak.peak_confidence_score),
            0.0,
            1.0,
        )
        best = selected[0] if selected else None
        best_event = best.get("event") if best is not None else None
        selected_events = [item.get("event") for item in selected if item.get("event") is not None]
        matched_event_ids = "|".join(item.event_id for item in selected_events)
        matched_event_titles = " | ".join(item.title for item in selected_events)

        if not events_by_country.get(peak.country):
            uncertainty_note = "no_country_events_in_registry"
        elif match_class == "no_credible_match":
            uncertainty_note = "no_credible_match_manual_review"
        elif match_class == "weak_match":
            uncertainty_note = "weak_match_manual_review"
        elif match_class == "multi_event_overlap":
            uncertainty_note = "multi_event_overlap_manual_review"
        elif peak.global_share >= 0.65:
            uncertainty_note = "global_wave_overlap_caution"
        else:
            uncertainty_note = ""

        evidence_chain = (
            "temporal="
            f"{float(best.get('temporal_score', 0.0)):.2f}, "
            "thematic="
            f"{float(best.get('thematic_score', 0.0)):.2f}, "
            "support="
            f"{float(best.get('support_score', 0.0)):.2f}, "
            f"class={match_class}"
            if best is not None
            else f"class={match_class}"
        )
        match_records.append(
            ValidationPeakEventMatchRecord(
                country=peak.country,
                peak_rank=peak.peak_rank,
                period_label=peak.period_label,
                target_period_end=peak.target_period_end,
                fusion_score=peak.fusion_score,
                attribution_label=peak.attribution_label,
                trajectory_profile=trajectory_profile,
                peak_confidence_score=peak.peak_confidence_score,
                match_class=match_class,
                match_confidence=round(match_confidence, 4),
                credible_match=credible_match,
                matched_event_count=len(selected_events),
                matched_event_ids=matched_event_ids,
                matched_event_titles=matched_event_titles,
                best_event_id=(best_event.event_id if best_event is not None else ""),
                best_event_title=(best_event.title if best_event is not None else ""),
                best_event_type=(best_event.event_type if best_event is not None else ""),
                best_event_start=(best_event.start_date if best_event is not None else None),
                best_event_end=(best_event.end_date if best_event is not None else None),
                best_event_source_category=(best_event.source_category if best_event is not None else ""),
                time_distance_days=int(float(best.get("time_distance_days", temporal_distance_days)) if best is not None else temporal_distance_days),
                overlap_days=int(float(best.get("overlap_days", 0)) if best is not None else 0),
                temporal_score=round(float(best.get("temporal_score", 0.0)) if best is not None else 0.0, 4),
                thematic_score=round(float(best.get("thematic_score", 0.0)) if best is not None else 0.0, 4),
                support_score=round(float(best.get("support_score", 0.0)) if best is not None else 0.0, 4),
                evidence_chain=evidence_chain,
                uncertainty_note=uncertainty_note,
            )
        )

    match_by_country: dict[str, list[ValidationPeakEventMatchRecord]] = defaultdict(list)
    for item in match_records:
        match_by_country[item.country].append(item)

    coverage_rows: list[ValidationEventCoverageSummaryRecord] = []
    country_alignment_rows: list[ValidationCountryEventAlignmentRecord] = []
    countries = sorted(set(match_by_country.keys()) | set(trajectories_by_country.keys()))
    for country in countries:
        rows = match_by_country.get(country, [])
        peak_count = len(rows)
        class_counts = Counter(item.match_class for item in rows)
        direct_count = class_counts.get("direct_match", 0)
        context_count = class_counts.get("plausible_context_match", 0)
        weak_count = class_counts.get("weak_match", 0)
        none_count = class_counts.get("no_credible_match", 0)
        multi_count = class_counts.get("multi_event_overlap", 0)
        credible_count = direct_count + context_count + multi_count
        credible_ratio = (credible_count / float(peak_count)) if peak_count > 0 else 0.0
        no_ratio = (none_count / float(peak_count)) if peak_count > 0 else 0.0
        multi_ratio = (multi_count / float(peak_count)) if peak_count > 0 else 0.0
        mean_match_confidence = (
            mean(item.match_confidence for item in rows) if rows else 0.0
        )
        coverage_band = _coverage_band(credible_ratio)
        coverage_rows.append(
            ValidationEventCoverageSummaryRecord(
                scope="country",
                country=country,
                peak_count=peak_count,
                direct_match_count=direct_count,
                plausible_context_match_count=context_count,
                weak_match_count=weak_count,
                no_credible_match_count=none_count,
                multi_event_overlap_count=multi_count,
                credible_match_count=credible_count,
                credible_match_ratio=round(credible_ratio, 4),
                no_credible_match_ratio=round(no_ratio, 4),
                multi_event_overlap_ratio=round(multi_ratio, 4),
                mean_match_confidence=round(mean_match_confidence, 4),
                coverage_band=coverage_band,
            )
        )

        global_wave_ratio = (
            len(
                [
                    item
                    for item in rows
                    if item.attribution_label in {"globally_co_moving_peak", "global_background_stress_peak"}
                ]
            )
            / float(peak_count)
            if peak_count > 0
            else 0.0
        )
        country_specific_ratio = (
            len(
                [
                    item
                    for item in rows
                    if item.attribution_label in {"country_specific_peak", "event_supported_peak"}
                ]
            )
            / float(peak_count)
            if peak_count > 0
            else 0.0
        )
        maturity_score = _clamp(
            (0.45 * credible_ratio)
            + (0.25 * (direct_count / float(peak_count) if peak_count > 0 else 0.0))
            + (0.15 * mean_match_confidence)
            + (0.15 * (1.0 - global_wave_ratio)),
            0.0,
            1.0,
        )
        maturity = _alignment_maturity_label(maturity_score)
        event_counter = Counter()
        for item in rows:
            if item.best_event_title:
                event_counter[item.best_event_title] += 1
        top_events = " | ".join(
            [name for name, _ in event_counter.most_common(3)]
        )
        commentary_parts: list[str] = [
            f"credible={credible_ratio:.2f}",
            f"no_match={no_ratio:.2f}",
            f"global_wave={global_wave_ratio:.2f}",
        ]
        if multi_count > 0:
            commentary_parts.append("multi_event_phase_detected")
        if peak_count == 0:
            commentary_parts.append("no_detected_peaks")
        alignment_commentary = ", ".join(commentary_parts)
        uncertainty_markers: list[str] = []
        if none_count > 0:
            uncertainty_markers.append("peaks_without_credible_match")
        if weak_count > 0:
            uncertainty_markers.append("weak_match_share_present")
        if multi_count > 0:
            uncertainty_markers.append("multi_event_overlap_manual_review")
        if not rows:
            uncertainty_markers.append("no_peak_records")
        country_alignment_rows.append(
            ValidationCountryEventAlignmentRecord(
                country=country,
                trajectory_profile=(
                    trajectories_by_country.get(country).trajectory_profile
                    if country in trajectories_by_country
                    else "unknown"
                ),
                peak_count=peak_count,
                direct_match_count=direct_count,
                plausible_context_match_count=context_count,
                weak_match_count=weak_count,
                no_credible_match_count=none_count,
                multi_event_overlap_count=multi_count,
                credible_match_ratio=round(credible_ratio, 4),
                mean_match_confidence=round(mean_match_confidence, 4),
                global_wave_peak_ratio=round(global_wave_ratio, 4),
                country_specific_peak_ratio=round(country_specific_ratio, 4),
                alignment_maturity_score=round(maturity_score, 4),
                alignment_maturity=maturity,
                alignment_commentary=alignment_commentary,
                top_linked_events=top_events,
                open_uncertainties="|".join(uncertainty_markers),
            )
        )

    total_peak_count = len(match_records)
    total_class_counts = Counter(item.match_class for item in match_records)
    total_direct = total_class_counts.get("direct_match", 0)
    total_context = total_class_counts.get("plausible_context_match", 0)
    total_weak = total_class_counts.get("weak_match", 0)
    total_none = total_class_counts.get("no_credible_match", 0)
    total_multi = total_class_counts.get("multi_event_overlap", 0)
    total_credible = total_direct + total_context + total_multi
    total_credible_ratio = (total_credible / float(total_peak_count)) if total_peak_count > 0 else 0.0
    total_no_ratio = (total_none / float(total_peak_count)) if total_peak_count > 0 else 0.0
    total_multi_ratio = (total_multi / float(total_peak_count)) if total_peak_count > 0 else 0.0
    total_mean_match_confidence = (
        mean(item.match_confidence for item in match_records) if match_records else 0.0
    )
    coverage_rows.insert(
        0,
        ValidationEventCoverageSummaryRecord(
            scope="global",
            country="ALL",
            peak_count=total_peak_count,
            direct_match_count=total_direct,
            plausible_context_match_count=total_context,
            weak_match_count=total_weak,
            no_credible_match_count=total_none,
            multi_event_overlap_count=total_multi,
            credible_match_count=total_credible,
            credible_match_ratio=round(total_credible_ratio, 4),
            no_credible_match_ratio=round(total_no_ratio, 4),
            multi_event_overlap_ratio=round(total_multi_ratio, 4),
            mean_match_confidence=round(total_mean_match_confidence, 4),
            coverage_band=_coverage_band(total_credible_ratio),
        ),
    )

    high_coverage_countries = sorted(
        [item.country for item in coverage_rows if item.scope == "country" and item.coverage_band == "high"]
    )
    low_coverage_countries = sorted(
        [item.country for item in coverage_rows if item.scope == "country" and item.coverage_band == "low"]
    )
    maturity_mean = (
        mean(item.alignment_maturity_score for item in country_alignment_rows)
        if country_alignment_rows
        else 0.0
    )
    alignment_summary = {
        "peak_event_match_record_count": total_peak_count,
        "credible_match_count": total_credible,
        "no_credible_match_count": total_none,
        "multi_event_overlap_count": total_multi,
        "credible_match_ratio": round(total_credible_ratio, 4),
        "no_credible_match_ratio": round(total_no_ratio, 4),
        "multi_event_overlap_ratio": round(total_multi_ratio, 4),
        "mean_match_confidence": round(total_mean_match_confidence, 4),
        "high_coverage_country_count": len(high_coverage_countries),
        "low_coverage_country_count": len(low_coverage_countries),
        "high_coverage_countries": high_coverage_countries,
        "low_coverage_countries": low_coverage_countries,
        "country_alignment_maturity_mean": round(maturity_mean, 4),
        "country_alignment_high_count": len(
            [item for item in country_alignment_rows if item.alignment_maturity == "high"]
        ),
        "country_alignment_low_count": len(
            [item for item in country_alignment_rows if item.alignment_maturity == "low"]
        ),
        "peak_alignment_quality_score": round(
            _clamp(
                (0.5 * total_credible_ratio)
                + (0.3 * (total_direct / float(total_peak_count) if total_peak_count > 0 else 0.0))
                + (0.2 * total_mean_match_confidence),
                0.0,
                1.0,
            ),
            4,
        ),
        "event_coverage_quality_score": round(
            _clamp((0.7 * total_credible_ratio) + (0.3 * (1.0 - total_no_ratio)), 0.0, 1.0),
            4,
        ),
    }

    return (
        sorted(match_records, key=lambda item: (item.country, item.peak_rank)),
        sorted(
            coverage_rows,
            key=lambda item: (
                0 if item.scope == "global" else 1,
                item.country,
            ),
        ),
        sorted(country_alignment_rows, key=lambda item: item.country),
        alignment_summary,
    )


def build_validation_framework(
    *,
    countries: list[str],
    reference_episodes_path: Path,
    reference_episode_count: int,
    expected_ranking: list[str],
    group_weights: dict[str, float],
    source_weights: dict[str, dict[str, float]],
    fusion_stage_low_max: float,
    fusion_stage_elevated_max: float,
    fusion_stage_high_max: float,
    fusion_trend_delta_epsilon: float,
    event_stale_after_days: int,
    event_decay_half_life_days: int,
    event_min_decay_factor: float,
    group_activation_threshold: float,
    dominance_share_threshold: float,
    structural_outlier_gap: float,
    event_fresh_boost_factor: float = 1.0,
    freshness_model: dict[str, dict[str, float]] | None = None,
    freshness_min_fresh_contribution_share: float = 0.35,
    freshness_max_stale_contribution_share: float = 0.5,
    dynamic_layer_readiness_min_share: float = 0.5,
    responsiveness_delta_threshold: float = 2.0,
    responsiveness_lag_tolerance_months: int = 1,
    dynamic_groups: list[str] | None = None,
    peak_prominence_min: float = 1.0,
    peak_min_rise: float = 0.5,
    peak_min_fall: float = 0.5,
    peak_min_separation_periods: int = 0,
    peak_quality_floor: float = 1.0,
    peak_support_group_min_share: float = 0.12,
    peak_country_specific_share_threshold: float = 0.4,
    peak_global_share_warning_threshold: float = 0.55,
    peak_model_driven_global_share_threshold: float = 0.7,
    peak_single_group_dominance_threshold: float = 0.58,
    peak_event_support_weak_threshold: float = 0.45,
    peak_event_support_strong_threshold: float = 0.7,
    event_alignment_temporal_distance_days: int = 75,
    event_alignment_direct_match_threshold: float = 0.72,
    event_alignment_context_match_threshold: float = 0.56,
    event_alignment_weak_match_threshold: float = 0.4,
    event_alignment_multi_overlap_min_events: int = 2,
    event_registry_path: Path | None = None,
    event_marker_registry_path: Path | None = None,
) -> dict[str, object]:
    """
    Build exportable validation framework metadata.

    Traceability:
    - PSwR-075
    - PSwR-078
    - PSwR-083
    - PSwR-086
    - PSwR-089
    - PSwR-095
    - PSwR-096
    - PSwR-105
    - PSwR-106
    - PSwR-107
    - PSwR-108
    - PSwR-109
    - PSwR-110
    - PSwR-111
    - PSwR-112
    - PSwR-113
    - PSwR-115
    - PSwR-116
    - PSwR-118
    - PSwR-123
    - PSwR-124
    - PM-051
    - PM-035
    - PM-038
    - PM-042
    - PM-045
    - PM-048
    - PM-057
    - PM-058
    - PM-059
    - PM-060
    - PM-061
    - PM-062
    - PM-063
    - PM-065
    - PM-066
    - PM-067
    - PM-069
    - ALG-035
    - ALG-041
    - ALG-042
    - ALG-043
    - ALG-044
    - ALG-045
    - ALG-046
    - ALG-047
    - ALG-048
    - ALG-049
    - ALG-051
    - ALG-053
    - ALG-054
    """
    effective_dynamic_groups = (
        dynamic_groups[:] if dynamic_groups is not None else ["event", "narrative", "governance", "shock", "displacement"]
    )
    effective_freshness_model = (
        freshness_model if freshness_model is not None else copy_default_freshness_model()
    )
    return {
        "validation_version": "v4.3.2",
        "reference_episodes_version": "v4.3.2",
        "countries": countries,
        "reference_episodes_path": reference_episodes_path.as_posix(),
        "reference_episode_count": reference_episode_count,
        "expected_country_ranking": expected_ranking,
        "evaluation_criteria": {
            "peak_hit": "observed_peak_stage >= expected_total_reaction_stage",
            "timing_fit": "abs(observed_peak_month - expected_peak_month) <= tolerance_months",
            "group_hit": "expected groups overlap with top validation drivers",
            "ranking_fit": "snapshot rank order compared to expected country ranking",
            "dominance": "dominant_group_share >= configured threshold",
            "governance_instability": "governance group score >= activation threshold",
            "support_profile": "broad if >=3 active groups, else narrow",
            "freshness_coverage": "fresh_contribution_share >= configured minimum",
            "stale_burden": "stale_contribution_share <= configured maximum",
            "dynamic_readiness": "share of fresh dynamic groups >= configured minimum",
            "response_lag": "timing lag compared against configured tolerance",
            "change_detection_fit": "significant historical deltas align with expected episode reaction windows",
            "year_profile_comparison": "country-level 356-day profile metrics (level, range, volatility, peak structure)",
            "country_ranking_trajectory": "period-level rank evolution across all countries",
            "peak_detection_quality": "peaks are local maxima with explicit prominence/rise/fall/width/separation checks",
            "peak_attribution": "peaks provide dominant groups, support breadth and global-vs-country decomposition",
            "event_peak_support": "peaks are classified as event_supported / weakly_supported / not_event_validated",
            "event_registry_alignment": "peaks are matched against analyst event-registry windows with temporal/thematic/support scoring",
            "peak_event_match_classes": "direct_match / plausible_context_match / weak_match / no_credible_match / multi_event_overlap",
            "event_coverage_diagnostics": "coverage tracks credible/no-match/multi-overlap shares globally and per country",
            "country_alignment_maturity": "country-level maturity score combines credible match ratio, directness, confidence and global-wave dependence",
            "peak_synchronization": "cross-country peak clustering flags globally co-moving waves vs country-specific spikes",
            "market_food_dominance_hardening": "market_food global pressure is tracked separately from local peak pressure",
        },
        "calibration_profile": {
            "group_weights": group_weights,
            "source_weights": source_weights,
            "fusion_stage_thresholds": {
                "low_max": fusion_stage_low_max,
                "elevated_max": fusion_stage_elevated_max,
                "high_max": fusion_stage_high_max,
            },
            "fusion_trend_delta_epsilon": fusion_trend_delta_epsilon,
            "event_reactivity": {
                "stale_after_days": event_stale_after_days,
                "decay_half_life_days": event_decay_half_life_days,
                "minimum_decay_factor": event_min_decay_factor,
                "fresh_boost_factor": event_fresh_boost_factor,
            },
            "freshness_model": effective_freshness_model,
            "operational_freshness_thresholds": {
                "minimum_fresh_contribution_share": freshness_min_fresh_contribution_share,
                "maximum_stale_contribution_share": freshness_max_stale_contribution_share,
                "dynamic_layer_readiness_min_share": dynamic_layer_readiness_min_share,
            },
            "historical_responsiveness": {
                "delta_threshold": responsiveness_delta_threshold,
                "response_lag_tolerance_months": responsiveness_lag_tolerance_months,
                "dynamic_groups": effective_dynamic_groups,
            },
            "diagnostics": {
                "group_activation_threshold": group_activation_threshold,
                "dominance_share_threshold": dominance_share_threshold,
                "structural_outlier_gap": structural_outlier_gap,
            },
            "peak_attribution": {
                "peak_prominence_min": peak_prominence_min,
                "peak_min_rise": peak_min_rise,
                "peak_min_fall": peak_min_fall,
                "peak_min_separation_periods": peak_min_separation_periods,
                "peak_quality_floor": peak_quality_floor,
                "support_group_min_share": peak_support_group_min_share,
                "country_specific_share_threshold": peak_country_specific_share_threshold,
                "global_share_warning_threshold": peak_global_share_warning_threshold,
                "model_driven_global_share_threshold": peak_model_driven_global_share_threshold,
                "single_group_dominance_threshold": peak_single_group_dominance_threshold,
                "event_support_weak_threshold": peak_event_support_weak_threshold,
                "event_support_strong_threshold": peak_event_support_strong_threshold,
                "event_marker_registry_path": (
                    event_marker_registry_path.as_posix()
                    if event_marker_registry_path is not None
                    else None
                ),
            },
            "event_alignment": {
                "event_registry_path": (
                    event_registry_path.as_posix()
                    if event_registry_path is not None
                    else None
                ),
                "temporal_distance_days": event_alignment_temporal_distance_days,
                "direct_match_threshold": event_alignment_direct_match_threshold,
                "context_match_threshold": event_alignment_context_match_threshold,
                "weak_match_threshold": event_alignment_weak_match_threshold,
                "multi_overlap_min_events": event_alignment_multi_overlap_min_events,
            },
        },
    }


def build_validation_summary(
    *,
    episode_results: list[ValidationEpisodeResultRecord],
    ranking_results: list[ValidationRankingRecord],
    ranking_fit_score: float,
    ranking_plausible: bool,
    layer_diagnostics: list[ValidationLayerDiagnosticRecord],
    freshness_group_records: list[ValidationFreshnessGroupRecord] | None = None,
    historical_responsiveness_records: list[ValidationHistoricalResponsivenessRecord] | None = None,
    country_profile_records: list[ValidationCountryProfileRecord] | None = None,
    peak_phase_records: list[ValidationCountryPeakPhaseRecord] | None = None,
    group_profile_records: list[ValidationCountryGroupProfileRecord] | None = None,
    ranking_trajectory_records: list[ValidationRankingTrajectoryRecord] | None = None,
    peak_attribution_records: list[ValidationPeakAttributionRecord] | None = None,
    peak_event_support_records: list[ValidationPeakEventSupportRecord] | None = None,
    peak_event_match_records: list[ValidationPeakEventMatchRecord] | None = None,
    event_coverage_summary_records: list[ValidationEventCoverageSummaryRecord] | None = None,
    country_event_alignment_records: list[ValidationCountryEventAlignmentRecord] | None = None,
    trajectory_profile_records: list[ValidationTrajectoryProfileRecord] | None = None,
    peak_synchronization_records: list[ValidationGlobalPeakSynchronizationRecord] | None = None,
    peak_attribution_summary: dict[str, object] | None = None,
    event_alignment_summary: dict[str, object] | None = None,
    freshness_min_fresh_contribution_share: float = 0.35,
    freshness_max_stale_contribution_share: float = 0.5,
    dynamic_layer_readiness_min_share: float = 0.5,
    responsiveness_lag_tolerance_months: int = 1,
) -> dict[str, object]:
    """
    Build compact validation summary for status and review bundle.

    Traceability:
    - PSwR-080
    - PSwR-082
    - PSwR-085
    - PSwR-086
    - PSwR-089
    - PSwR-090
    - PSwR-094
    - PSwR-095
    - PSwR-096
    - PSwR-098
    - PSwR-099
    - PSwR-100
    - PSwR-102
    - PSwR-104
    - PSwR-105
    - PSwR-106
    - PSwR-107
    - PSwR-108
    - PSwR-109
    - PSwR-110
    - PSwR-111
    - PSwR-112
    - PSwR-115
    - PSwR-116
    - PSwR-117
    - PSwR-118
    - PSwR-123
    - PSwR-124
    - PM-051
    - PM-037
    - PM-041
    - PM-045
    - PM-048
    - PM-053
    - PM-054
    - PM-057
    - PM-058
    - PM-059
    - PM-060
    - PM-061
    - PM-062
    - PM-065
    - PM-066
    - PM-067
    - PM-068
    - PM-069
    - PM-070
    - ALG-028
    - ALG-032
    - ALG-035
    - ALG-036
    - ALG-037
    - ALG-038
    - ALG-039
    - ALG-040
    - ALG-041
    - ALG-042
    - ALG-043
    - ALG-044
    - ALG-045
    - ALG-046
    - ALG-047
    - ALG-049
    - ALG-050
    - ALG-051
    - ALG-052
    - ALG-053
    - ALG-054
    - ALG-055
    """
    freshness_group_records = freshness_group_records or []
    historical_responsiveness_records = historical_responsiveness_records or []
    country_profile_records = country_profile_records or []
    peak_phase_records = peak_phase_records or []
    group_profile_records = group_profile_records or []
    ranking_trajectory_records = ranking_trajectory_records or []
    peak_attribution_records = peak_attribution_records or []
    peak_event_support_records = peak_event_support_records or []
    peak_event_match_records = peak_event_match_records or []
    event_coverage_summary_records = event_coverage_summary_records or []
    country_event_alignment_records = country_event_alignment_records or []
    trajectory_profile_records = trajectory_profile_records or []
    peak_synchronization_records = peak_synchronization_records or []
    peak_attribution_summary = peak_attribution_summary or {}
    event_alignment_summary = event_alignment_summary or {}

    data_results = [item for item in episode_results if item.data_available]
    peak_hits = [item for item in data_results if item.peak_hit]
    timing_fits = [item for item in data_results if item.timing_fit]
    group_hits = [item for item in data_results if item.expected_group_hit]
    low_coverage_context = [item for item in data_results if item.low_coverage_context]

    outcome_counts: dict[str, int] = {}
    for item in episode_results:
        outcome_counts[item.outcome] = outcome_counts.get(item.outcome, 0) + 1

    dominance_flags = [item for item in layer_diagnostics if item.dominance_flag]
    structural_outliers = [item for item in layer_diagnostics if item.structural_outlier_flag]
    event_stale = [item for item in layer_diagnostics if item.event_stale_flag]
    governance_instability = [
        item for item in layer_diagnostics if item.governance_instability_flag
    ]
    governance_low_freshness = [
        item for item in layer_diagnostics if item.governance_low_freshness_flag
    ]
    narrow_support = [item for item in layer_diagnostics if item.support_profile == "narrow"]
    low_fresh_coverage = [
        item
        for item in layer_diagnostics
        if item.fresh_contribution_share < freshness_min_fresh_contribution_share
    ]
    stale_burden = [
        item
        for item in layer_diagnostics
        if item.stale_contribution_share > freshness_max_stale_contribution_share
    ]
    dynamic_layer_ready = [
        item
        for item in layer_diagnostics
        if item.dynamic_layer_readiness
    ]

    reactive_profiles = [
        item for item in historical_responsiveness_records if item.responsiveness_profile == "reactive"
    ]
    inertia_risk_profiles = [
        item for item in historical_responsiveness_records if item.responsiveness_profile == "inertia_risk"
    ]
    mean_historical_abs_delta = (
        round(mean(item.mean_abs_delta for item in historical_responsiveness_records), 4)
        if historical_responsiveness_records
        else 0.0
    )

    peak_hit_rate = round(len(peak_hits) / float(len(data_results)), 4) if data_results else 0.0
    timing_fit_rate = round(len(timing_fits) / float(len(data_results)), 4) if data_results else 0.0
    response_lag_fit_rate = round(
        len(
            [
                item
                for item in data_results
                if item.timing_lag_months is not None
                and abs(item.timing_lag_months) <= responsiveness_lag_tolerance_months
            ]
        )
        / float(len(data_results)),
        4,
    ) if data_results else 0.0
    expected_group_hit_rate = (
        round(len(group_hits) / float(len(data_results)), 4) if data_results else 0.0
    )
    change_detection_fit_rate = expected_group_hit_rate
    freshness_coverage_rate = (
        round(
            len(
                [
                    item
                    for item in layer_diagnostics
                    if item.fresh_contribution_share >= freshness_min_fresh_contribution_share
                ]
            )
            / float(len(layer_diagnostics)),
            4,
        )
        if layer_diagnostics
        else 0.0
    )
    stale_burden_rate = (
        round(len(stale_burden) / float(len(layer_diagnostics)), 4)
        if layer_diagnostics
        else 0.0
    )
    dynamic_layer_readiness_rate = (
        round(len(dynamic_layer_ready) / float(len(layer_diagnostics)), 4)
        if layer_diagnostics
        else 0.0
    )
    mean_fresh_contribution_share = (
        round(mean(item.fresh_contribution_share for item in layer_diagnostics), 4)
        if layer_diagnostics
        else 0.0
    )
    mean_stale_contribution_share = (
        round(mean(item.stale_contribution_share for item in layer_diagnostics), 4)
        if layer_diagnostics
        else 0.0
    )
    mean_year_range = (
        round(mean(item.year_range_score for item in country_profile_records), 4)
        if country_profile_records
        else 0.0
    )
    mean_year_volatility = (
        round(mean(item.year_volatility_std for item in country_profile_records), 4)
        if country_profile_records
        else 0.0
    )
    top_current_country = (
        max(country_profile_records, key=lambda item: item.current_fusion_score)
        if country_profile_records
        else None
    )
    highest_peak_country = (
        max(country_profile_records, key=lambda item: item.year_max_score)
        if country_profile_records
        else None
    )
    most_volatile_country = (
        max(country_profile_records, key=lambda item: item.year_volatility_std)
        if country_profile_records
        else None
    )
    fresh_operational_count = len(
        [item for item in country_profile_records if item.operational_freshness_status == "fresh_operational"]
    )
    stale_attention_count = len(
        [item for item in country_profile_records if item.operational_freshness_status == "stale_attention"]
    )
    comparative_profile_coverage_ok = (
        len(country_profile_records) == len(ranking_results)
        if ranking_results
        else bool(country_profile_records)
    )
    peak_attribution_record_count = int(
        peak_attribution_summary.get("peak_attribution_record_count", len(peak_attribution_records)) or 0
    )
    event_supported_peak_ratio = float(
        peak_attribution_summary.get(
            "event_supported_peak_ratio",
            (
                len([item for item in peak_attribution_records if item.attribution_label == "event_supported_peak"])
                / float(len(peak_attribution_records))
            )
            if peak_attribution_records
            else 0.0,
        )
        or 0.0
    )
    weakly_supported_peak_ratio = float(
        peak_attribution_summary.get(
            "weakly_supported_peak_ratio",
            (
                len([item for item in peak_attribution_records if item.attribution_label == "weakly_supported_peak"])
                / float(len(peak_attribution_records))
            )
            if peak_attribution_records
            else 0.0,
        )
        or 0.0
    )
    globally_co_moving_peak_ratio = float(
        peak_attribution_summary.get(
            "globally_co_moving_peak_ratio",
            (
                len(
                    [
                        item
                        for item in peak_attribution_records
                        if item.attribution_label in {"global_background_stress_peak", "globally_co_moving_peak"}
                    ]
                )
                / float(len(peak_attribution_records))
            )
            if peak_attribution_records
            else 0.0,
        )
        or 0.0
    )
    model_driven_peak_ratio = float(
        peak_attribution_summary.get(
            "model_driven_peak_ratio",
            (
                len([item for item in peak_attribution_records if item.attribution_label == "model_driven_peak"])
                / float(len(peak_attribution_records))
            )
            if peak_attribution_records
            else 0.0,
        )
        or 0.0
    )
    country_specific_peak_ratio = float(
        peak_attribution_summary.get(
            "country_specific_peak_ratio",
            (
                len(
                    [
                        item
                        for item in peak_attribution_records
                        if item.attribution_label in {"country_specific_peak", "event_supported_peak"}
                    ]
                )
                / float(len(peak_attribution_records))
            )
            if peak_attribution_records
            else 0.0,
        )
        or 0.0
    )
    mean_peak_confidence_score = float(
        peak_attribution_summary.get(
            "mean_peak_confidence_score",
            mean(item.peak_confidence_score for item in peak_attribution_records)
            if peak_attribution_records
            else 0.0,
        )
        or 0.0
    )
    high_synchronization_count = int(
        peak_attribution_summary.get(
            "peak_synchronization_high_count",
            len(
                [
                    item
                    for item in peak_synchronization_records
                    if item.synchronization_class == "highly_synchronized_wave"
                ]
            ),
        )
        or 0
    )
    trajectory_low_differentiation_country_count = int(
        peak_attribution_summary.get(
            "trajectory_low_differentiation_country_count",
            len([item for item in trajectory_profile_records if not item.differentiation_flag]),
        )
        or 0
    )
    market_food_global_dominance_peak_count = int(
        peak_attribution_summary.get(
            "market_food_global_dominance_peak_count",
            len(
                [
                    item
                    for item in peak_attribution_records
                    if item.dominant_group == "market_food" and item.global_share >= 0.55
                ]
            ),
        )
        or 0
    )
    global_event_coverage = next(
        (
            item
            for item in event_coverage_summary_records
            if item.scope == "global"
        ),
        None,
    )
    event_registry_credible_match_ratio = float(
        event_alignment_summary.get(
            "credible_match_ratio",
            (
                global_event_coverage.credible_match_ratio
                if global_event_coverage is not None
                else (
                    len([item for item in peak_event_match_records if item.credible_match])
                    / float(len(peak_event_match_records))
                    if peak_event_match_records
                    else 0.0
                )
            ),
        )
        or 0.0
    )
    event_registry_no_match_ratio = float(
        event_alignment_summary.get(
            "no_credible_match_ratio",
            (
                global_event_coverage.no_credible_match_ratio
                if global_event_coverage is not None
                else (
                    len(
                        [
                            item
                            for item in peak_event_match_records
                            if item.match_class == "no_credible_match"
                        ]
                    )
                    / float(len(peak_event_match_records))
                    if peak_event_match_records
                    else 0.0
                )
            ),
        )
        or 0.0
    )
    event_registry_multi_overlap_ratio = float(
        event_alignment_summary.get(
            "multi_event_overlap_ratio",
            (
                global_event_coverage.multi_event_overlap_ratio
                if global_event_coverage is not None
                else (
                    len(
                        [
                            item
                            for item in peak_event_match_records
                            if item.match_class == "multi_event_overlap"
                        ]
                    )
                    / float(len(peak_event_match_records))
                    if peak_event_match_records
                    else 0.0
                )
            ),
        )
        or 0.0
    )
    event_registry_mean_match_confidence = float(
        event_alignment_summary.get(
            "mean_match_confidence",
            (
                global_event_coverage.mean_match_confidence
                if global_event_coverage is not None
                else (
                    mean(item.match_confidence for item in peak_event_match_records)
                    if peak_event_match_records
                    else 0.0
                )
            ),
        )
        or 0.0
    )
    event_coverage_sparse_country_count = int(
        event_alignment_summary.get(
            "low_coverage_country_count",
            len(
                [
                    item
                    for item in event_coverage_summary_records
                    if item.scope == "country" and item.coverage_band == "low"
                ]
            ),
        )
        or 0
    )
    event_coverage_high_country_count = int(
        event_alignment_summary.get(
            "high_coverage_country_count",
            len(
                [
                    item
                    for item in event_coverage_summary_records
                    if item.scope == "country" and item.coverage_band == "high"
                ]
            ),
        )
        or 0
    )
    country_alignment_maturity_mean = float(
        event_alignment_summary.get(
            "country_alignment_maturity_mean",
            (
                mean(item.alignment_maturity_score for item in country_event_alignment_records)
                if country_event_alignment_records
                else 0.0
            ),
        )
        or 0.0
    )
    country_alignment_low_count = int(
        event_alignment_summary.get(
            "country_alignment_low_count",
            len(
                [
                    item
                    for item in country_event_alignment_records
                    if item.alignment_maturity == "low"
                ]
            ),
        )
        or 0
    )
    country_alignment_high_count = int(
        event_alignment_summary.get(
            "country_alignment_high_count",
            len(
                [
                    item
                    for item in country_event_alignment_records
                    if item.alignment_maturity == "high"
                ]
            ),
        )
        or 0
    )
    peak_alignment_quality_score = float(
        event_alignment_summary.get(
            "peak_alignment_quality_score",
            _clamp(
                (0.5 * event_registry_credible_match_ratio)
                + (0.3 * event_supported_peak_ratio)
                + (0.2 * event_registry_mean_match_confidence),
                0.0,
                1.0,
            ),
        )
        or 0.0
    )
    event_coverage_quality_score = float(
        event_alignment_summary.get(
            "event_coverage_quality_score",
            _clamp(
                (0.7 * event_registry_credible_match_ratio)
                + (0.3 * (1.0 - event_registry_no_match_ratio)),
                0.0,
                1.0,
            ),
        )
        or 0.0
    )

    if data_results:
        timing_lags = [
            abs(item.timing_lag_months)
            for item in data_results
            if item.timing_lag_months is not None
        ]
        mean_abs_timing_lag = round(
            (sum(timing_lags) / float(len(timing_lags))) if timing_lags else 0.0,
            3,
        )
    else:
        mean_abs_timing_lag = 0.0

    if (
        peak_hit_rate >= 0.66
        and ranking_plausible
        and len(event_stale) == 0
        and not stale_burden
        and freshness_coverage_rate >= 0.66
    ):
        summary_status = "calibrated_for_mvp"
    elif peak_hit_rate >= 0.5 and response_lag_fit_rate >= 0.5:
        summary_status = "partially_calibrated_review_required"
    else:
        summary_status = "calibration_attention_required"
    operational_freshness_attention = bool(stale_burden or low_fresh_coverage)

    key_findings: list[str] = []
    key_findings.append(
        f"Peak-hit rate {peak_hit_rate:.2f} across {len(data_results)} data-backed reference episodes."
    )
    key_findings.append(
        f"Timing-fit rate {timing_fit_rate:.2f}, mean absolute lag {mean_abs_timing_lag:.2f} months."
    )
    key_findings.append(
        f"Ranking fit {ranking_fit_score:.2f} (plausible={str(ranking_plausible).lower()})."
    )
    key_findings.append(
        f"Freshness coverage {freshness_coverage_rate:.2f}, stale burden {stale_burden_rate:.2f}, dynamic readiness {dynamic_layer_readiness_rate:.2f}."
    )
    key_findings.append(
        f"Response-lag fit {response_lag_fit_rate:.2f} (tolerance={responsiveness_lag_tolerance_months}m), change-detection fit {change_detection_fit_rate:.2f}."
    )
    key_findings.append(
        f"Historical responsiveness: reactive={len(reactive_profiles)}, inertia-risk={len(inertia_risk_profiles)}, mean |delta|={mean_historical_abs_delta:.2f}."
    )
    if country_profile_records:
        key_findings.append(
            f"Comparative profile coverage {len(country_profile_records)} countries, mean yearly range {mean_year_range:.2f}, mean volatility {mean_year_volatility:.2f}."
        )
    if top_current_country is not None:
        key_findings.append(
            f"Highest current fusion level: {top_current_country.country} ({top_current_country.current_fusion_score:.2f})."
        )
    if most_volatile_country is not None:
        key_findings.append(
            f"Most volatile 356-day profile: {most_volatile_country.country} ({most_volatile_country.year_volatility_std:.2f})."
        )
    if peak_attribution_record_count > 0:
        key_findings.append(
            "Peak attribution: "
            f"event_supported={event_supported_peak_ratio:.2f}, "
            f"weakly_supported={weakly_supported_peak_ratio:.2f}, "
            f"globally_co_moving={globally_co_moving_peak_ratio:.2f}, "
            f"model_driven={model_driven_peak_ratio:.2f}, "
            f"country_specific={country_specific_peak_ratio:.2f}."
        )
        key_findings.append(
            f"Mean peak confidence {mean_peak_confidence_score:.2f}; highly synchronized peak clusters={high_synchronization_count}."
        )
    if trajectory_profile_records:
        key_findings.append(
            f"Trajectory differentiation risk: {trajectory_low_differentiation_country_count} country profile(s) with low country-specific peak structure."
        )
    if peak_event_match_records:
        key_findings.append(
            "Event registry alignment: "
            f"credible={event_registry_credible_match_ratio:.2f}, "
            f"no_credible={event_registry_no_match_ratio:.2f}, "
            f"multi_event_overlap={event_registry_multi_overlap_ratio:.2f}, "
            f"mean_match_conf={event_registry_mean_match_confidence:.2f}."
        )
        key_findings.append(
            "Alignment maturity: "
            f"mean={country_alignment_maturity_mean:.2f}, "
            f"high_countries={country_alignment_high_count}, "
            f"low_countries={country_alignment_low_count}."
        )
    if market_food_global_dominance_peak_count > 0:
        key_findings.append(
            f"{market_food_global_dominance_peak_count} peak(s) are market_food-dominant with high global-share pressure."
        )
    if dominance_flags:
        key_findings.append(
            f"{len(dominance_flags)} country snapshot(s) show dominant-layer concentration."
        )
    if structural_outliers:
        key_findings.append(
            f"{len(structural_outliers)} country snapshot(s) show unusual structural intensity."
        )
    if event_stale:
        key_findings.append(
            f"{len(event_stale)} country snapshot(s) have stale event signal indicators."
        )
    if governance_instability:
        key_findings.append(
            f"{len(governance_instability)} country snapshot(s) show elevated governance-instability contribution."
        )
    if governance_low_freshness:
        key_findings.append(
            f"{len(governance_low_freshness)} country snapshot(s) have stale governance signal support."
        )
    if low_coverage_context:
        key_findings.append(
            f"{len(low_coverage_context)} episode peak(s) occurred under reduced historical coverage."
        )

    return {
        "status": summary_status,
        "episode_count": len(episode_results),
        "episodes_with_data": len(data_results),
        "episode_outcome_counts": outcome_counts,
        "peak_hit_rate": peak_hit_rate,
        "timing_fit_rate": timing_fit_rate,
        "response_lag_fit_rate": response_lag_fit_rate,
        "expected_group_hit_rate": expected_group_hit_rate,
        "change_detection_fit_rate": change_detection_fit_rate,
        "mean_absolute_timing_lag_months": mean_abs_timing_lag,
        "ranking_fit_score": ranking_fit_score,
        "ranking_plausible": ranking_plausible,
        "ranking_record_count": len(ranking_results),
        "freshness_group_record_count": len(freshness_group_records),
        "freshness_coverage_rate": freshness_coverage_rate,
        "stale_burden_rate": stale_burden_rate,
        "dynamic_layer_readiness_rate": dynamic_layer_readiness_rate,
        "mean_fresh_contribution_share": mean_fresh_contribution_share,
        "mean_stale_contribution_share": mean_stale_contribution_share,
        "country_profile_record_count": len(country_profile_records),
        "peak_phase_record_count": len(peak_phase_records),
        "group_profile_record_count": len(group_profile_records),
        "ranking_trajectory_record_count": len(ranking_trajectory_records),
        "peak_attribution_record_count": peak_attribution_record_count,
        "peak_event_support_record_count": len(peak_event_support_records),
        "peak_event_match_record_count": len(peak_event_match_records),
        "event_coverage_summary_record_count": len(event_coverage_summary_records),
        "country_event_alignment_record_count": len(country_event_alignment_records),
        "trajectory_profile_record_count": len(trajectory_profile_records),
        "peak_synchronization_record_count": len(peak_synchronization_records),
        "event_supported_peak_ratio": round(event_supported_peak_ratio, 4),
        "weakly_supported_peak_ratio": round(weakly_supported_peak_ratio, 4),
        "globally_co_moving_peak_ratio": round(globally_co_moving_peak_ratio, 4),
        "model_driven_peak_ratio": round(model_driven_peak_ratio, 4),
        "country_specific_peak_ratio": round(country_specific_peak_ratio, 4),
        "mean_peak_confidence_score": round(mean_peak_confidence_score, 4),
        "event_registry_credible_match_ratio": round(event_registry_credible_match_ratio, 4),
        "event_registry_no_credible_match_ratio": round(event_registry_no_match_ratio, 4),
        "event_registry_multi_event_overlap_ratio": round(event_registry_multi_overlap_ratio, 4),
        "event_registry_mean_match_confidence": round(event_registry_mean_match_confidence, 4),
        "event_coverage_sparse_country_count": event_coverage_sparse_country_count,
        "event_coverage_high_country_count": event_coverage_high_country_count,
        "peak_alignment_quality_score": round(peak_alignment_quality_score, 4),
        "event_coverage_quality_score": round(event_coverage_quality_score, 4),
        "country_alignment_maturity_mean": round(country_alignment_maturity_mean, 4),
        "country_alignment_high_count": country_alignment_high_count,
        "country_alignment_low_count": country_alignment_low_count,
        "peak_synchronization_high_count": high_synchronization_count,
        "trajectory_low_differentiation_country_count": trajectory_low_differentiation_country_count,
        "market_food_global_dominance_peak_count": market_food_global_dominance_peak_count,
        "comparative_mean_year_range": mean_year_range,
        "comparative_mean_year_volatility": mean_year_volatility,
        "comparative_top_current_country": (
            top_current_country.country if top_current_country is not None else None
        ),
        "comparative_highest_peak_country": (
            highest_peak_country.country if highest_peak_country is not None else None
        ),
        "comparative_most_volatile_country": (
            most_volatile_country.country if most_volatile_country is not None else None
        ),
        "comparative_fresh_operational_country_count": fresh_operational_count,
        "comparative_stale_attention_country_count": stale_attention_count,
        "comparative_profile_coverage_ok": comparative_profile_coverage_ok,
        "operational_freshness_attention": operational_freshness_attention,
        "historical_responsiveness_record_count": len(historical_responsiveness_records),
        "historical_responsiveness_reactive_count": len(reactive_profiles),
        "historical_responsiveness_inertia_risk_count": len(inertia_risk_profiles),
        "historical_responsiveness_mean_abs_delta": mean_historical_abs_delta,
        "dominance_flag_count": len(dominance_flags),
        "structural_outlier_count": len(structural_outliers),
        "event_stale_country_count": len(event_stale),
        "governance_instability_country_count": len(governance_instability),
        "governance_low_freshness_country_count": len(governance_low_freshness),
        "narrow_support_country_count": len(narrow_support),
        "low_fresh_coverage_country_count": len(low_fresh_coverage),
        "stale_burden_country_count": len(stale_burden),
        "dynamic_layer_ready_country_count": len(dynamic_layer_ready),
        "dynamic_layer_readiness_min_share": dynamic_layer_readiness_min_share,
        "low_coverage_episode_context_count": len(low_coverage_context),
        "key_findings": key_findings,
    }
