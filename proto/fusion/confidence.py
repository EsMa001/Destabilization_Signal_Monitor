from __future__ import annotations

"""
Fusion confidence helpers (kept separate from score values).

Traceability:
- PSwR-045
- ALG-017
- PM-021
"""

from statistics import mean, pstdev
from dataclasses import dataclass

from proto.fusion.models import FusionGroupScoreRecord, FusionSourceSignalRecord


def _clamp(value: float, *, low: float = 0.0, high: float = 100.0) -> float:
    # Traceability:
    # - PSwR-045
    # - ALG-017
    # - PM-021
    return max(low, min(high, value))


def map_fusion_confidence_level(score: float) -> str:
    """
    Map fusion confidence score to qualitative level.

    Traceability:
    - PSwR-045
    - ALG-017
    """
    if score < 34:
        return "niedrig"
    if score < 67:
        return "mittel"
    return "hoch"


@dataclass(frozen=True)
class FusionTotalConfidenceResult:
    confidence_score: float
    confidence_level: str
    coverage_component: float
    recency_component: float
    completeness_component: float
    consistency_component: float
    dominance_penalty: float
    limited_penalty: float
    dominant_contribution_share: float


def derive_group_confidence(
    *,
    signals: list[FusionSourceSignalRecord],
    expected_source_count: int,
    max_age_days: int,
    coverage_weight: float,
    recency_weight: float,
    completeness_weight: float,
    consistency_weight: float,
) -> tuple[float, str, float, float, float, float]:
    """
    Derive confidence for one fusion group from explicit components.

    Traceability:
    - PSwR-045
    - ALG-017
    """
    if expected_source_count <= 0:
        raise ValueError("expected_source_count must be > 0")
    if max_age_days <= 0:
        raise ValueError("max_age_days must be > 0")

    source_coverage_ratio = min(1.0, len(signals) / float(expected_source_count))
    coverage_component = round(100.0 * source_coverage_ratio, 2)
    if signals:
        recency_values = [
            max(0.0, 1.0 - (signal.age_days / float(max_age_days)))
            for signal in signals
        ]
        recency_component = round(100.0 * mean(recency_values), 2)
        completeness_component = round(
            100.0 * mean(signal.quality_completeness for signal in signals),
            2,
        )
        if len(signals) == 1:
            consistency_component = 70.0
        else:
            spread = pstdev(signal.normalized_value for signal in signals)
            consistency_component = round(_clamp(100.0 - spread * 120.0), 2)
    else:
        recency_component = 0.0
        completeness_component = 0.0
        consistency_component = 0.0

    weight_sum = coverage_weight + recency_weight + completeness_weight + consistency_weight
    if weight_sum <= 0:
        raise ValueError("confidence weights must sum to > 0")
    confidence_score = round(
        _clamp(
            (
                coverage_weight * coverage_component
                + recency_weight * recency_component
                + completeness_weight * completeness_component
                + consistency_weight * consistency_component
            )
            / weight_sum
        ),
        2,
    )
    return (
        confidence_score,
        map_fusion_confidence_level(confidence_score),
        coverage_component,
        recency_component,
        completeness_component,
        consistency_component,
    )


def derive_total_confidence(
    *,
    group_records: list[FusionGroupScoreRecord],
    expected_group_count: int,
    group_weights: dict[str, float],
) -> FusionTotalConfidenceResult:
    """
    Derive total fusion confidence from available group records.

    Traceability:
    - PSwR-045
    - ALG-017
    """
    if expected_group_count <= 0:
        raise ValueError("expected_group_count must be > 0")
    available = [record for record in group_records if record.status in {"ok", "limited"}]
    group_coverage = 100.0 * (len(available) / float(expected_group_count))
    if not available:
        return FusionTotalConfidenceResult(
            confidence_score=0.0,
            confidence_level="niedrig",
            coverage_component=0.0,
            recency_component=0.0,
            completeness_component=0.0,
            consistency_component=0.0,
            dominance_penalty=0.0,
            limited_penalty=0.0,
            dominant_contribution_share=0.0,
        )

    recency = mean(record.recency_component for record in available)
    completeness = mean(record.completeness_component for record in available)
    consistency = mean(record.consistency_component for record in available)

    base_confidence = (
        0.35 * group_coverage + 0.25 * recency + 0.25 * completeness + 0.15 * consistency
    )
    weighted_contributions: list[float] = []
    for record in available:
        group_weight = float(group_weights.get(record.group, 1.0))
        group_score = float(record.group_score or 0.0)
        weighted_contributions.append(max(0.0, group_weight * group_score))
    weighted_sum = sum(weighted_contributions)
    dominant_contribution_share = (
        max(weighted_contributions) / weighted_sum if weighted_sum > 0 else 0.0
    )
    dominance_penalty = round(max(0.0, dominant_contribution_share - 0.55) * 35.0, 2)

    limited_ratio = len([record for record in available if record.status == "limited"]) / float(len(available))
    limited_penalty = round(12.0 * limited_ratio, 2)

    confidence_score = round(_clamp(base_confidence - dominance_penalty - limited_penalty), 2)
    return FusionTotalConfidenceResult(
        confidence_score=confidence_score,
        confidence_level=map_fusion_confidence_level(confidence_score),
        coverage_component=round(group_coverage, 2),
        recency_component=round(recency, 2),
        completeness_component=round(completeness, 2),
        consistency_component=round(consistency, 2),
        dominance_penalty=dominance_penalty,
        limited_penalty=limited_penalty,
        dominant_contribution_share=round(dominant_contribution_share, 4),
    )
