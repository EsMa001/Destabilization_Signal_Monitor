from __future__ import annotations

"""
Traceability:
- PSwR-014
- ALG-007
- PSwR-027
- ALG-012
"""

from collections import defaultdict
from statistics import mean, pstdev

from proto.models import ScoreRecord


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def map_confidence(score: float) -> str:
    """
    Map numeric confidence to qualitative level.

    Traceability:
    - PSwR-014
    - ALG-007
    """
    if score < 34:
        return "niedrig"
    if score < 67:
        return "mittel"
    return "hoch"


def compute_confidence_score(
    *,
    data_density: float,
    signal_consistency: float,
    deviation_strength: float,
    source_plausibility: float,
) -> float:
    """
    Weighted confidence score (0-100).

    Traceability:
    - PSwR-014
    - ALG-007
    - OI-005
    """
    weighted = (
        0.30 * _clamp_score(data_density)
        + 0.25 * _clamp_score(signal_consistency)
        + 0.25 * _clamp_score(deviation_strength)
        + 0.20 * _clamp_score(source_plausibility)
    )
    return round(_clamp_score(weighted), 2)


def derive_confidence_by_cluster(
    *,
    subscores: list[ScoreRecord],
    cluster_scores: list[ScoreRecord],
    expected_subscores_by_cluster: dict[str, int],
    source_count_by_cluster: dict[tuple[str, str], int],
) -> dict[tuple[str, str], tuple[float, str]]:
    """
    Derive confidence per country/cluster from method components.

    Traceability:
    - PSwR-014
    - ALG-007
    """
    grouped_subscores: dict[tuple[str, str], list[ScoreRecord]] = defaultdict(list)
    for subscore in subscores:
        grouped_subscores[(subscore.country, subscore.cluster)].append(subscore)

    grouped_cluster_scores: dict[tuple[str, str], list[ScoreRecord]] = defaultdict(list)
    for cluster_score in cluster_scores:
        grouped_cluster_scores[(cluster_score.country, cluster_score.cluster)].append(cluster_score)

    output: dict[tuple[str, str], tuple[float, str]] = {}
    for key, score_series in grouped_cluster_scores.items():
        country, cluster = key
        cluster_subscores = grouped_subscores.get(key, [])
        expected_count = max(1, expected_subscores_by_cluster.get(cluster, len(cluster_subscores) or 1))

        latest_date = max(item.date for item in score_series)
        latest_subscores = [item for item in cluster_subscores if item.date == latest_date]
        data_density = 100.0 * (len(latest_subscores) / expected_count)

        latest_values = [item.score_value for item in latest_subscores] or [0.0]
        deviation_strength = abs(mean(latest_values) - 50.0) * 2.0
        deviation_strength = _clamp_score(deviation_strength)

        if len(latest_values) == 1:
            signal_consistency = 70.0
        else:
            spread = pstdev(latest_values)
            signal_consistency = _clamp_score(100.0 - spread * 2.0)

        source_count = source_count_by_cluster.get((country, cluster), 1)
        source_plausibility = _clamp_score(min(100.0, source_count * 25.0))

        confidence_score = compute_confidence_score(
            data_density=data_density,
            signal_consistency=signal_consistency,
            deviation_strength=deviation_strength,
            source_plausibility=source_plausibility,
        )
        output[key] = (confidence_score, map_confidence(confidence_score))

    return output


def derive_historical_confidence(
    *,
    score_value: float,
    coverage_ratio: float,
) -> tuple[float, str]:
    """
    Derive historical confidence from condensed numeric value + window coverage.

    Traceability:
    - PSwR-023
    - PSwR-027
    - ALG-012
    """
    clamped_coverage = _clamp_score(coverage_ratio * 100.0)
    numeric_strength = _clamp_score(abs(score_value - 50.0) * 2.0)
    condensed_numeric = _clamp_score(50.0 + 0.5 * numeric_strength)
    confidence_score = round(
        _clamp_score(0.65 * clamped_coverage + 0.35 * condensed_numeric),
        2,
    )
    return confidence_score, map_confidence(confidence_score)


def apply_snapshot_fallback_penalty(
    *,
    confidence_score: float,
    valid_days: int,
    min_valid_days: int,
) -> tuple[float, str, float]:
    """
    Apply explicit snapshot fallback penalty for below-threshold window coverage.

    Traceability:
    - PSwR-022
    - PSwR-026
    - PM-010
    - PM-012
    - OI-021
    """
    if min_valid_days <= 0:
        raise ValueError("min_valid_days must be > 0")

    base_score = _clamp_score(confidence_score)
    if valid_days >= min_valid_days:
        rounded = round(base_score, 2)
        return rounded, map_confidence(rounded), 0.0

    # Linear penalty up to 12 points for severe under-coverage.
    coverage_deficit_ratio = (min_valid_days - max(0, valid_days)) / float(min_valid_days)
    penalty = round(12.0 * coverage_deficit_ratio, 2)
    adjusted_score = round(_clamp_score(base_score - penalty), 2)
    return adjusted_score, map_confidence(adjusted_score), penalty
