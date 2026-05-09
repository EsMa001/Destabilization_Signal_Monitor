from __future__ import annotations

"""
Traceability:
- PSwR-012
- ALG-005
"""

from collections import defaultdict
from dataclasses import dataclass

from proto.models import ScoreRecord


@dataclass(frozen=True)
class StageThresholds:
    """
    Stage thresholds for calibrated mapping.

    Traceability:
    - PSwR-012
    - ALG-005
    """

    low_max: float
    elevated_max: float
    high_max: float


def map_score_to_stage(
    score: float,
    thresholds: StageThresholds,
) -> str:
    """
    Map cluster score to stage.

    Traceability:
    - PSwR-012
    - ALG-005
    - OI-004
    """
    if score < thresholds.low_max:
        return "niedrig"
    if score < thresholds.elevated_max:
        return "erhöht"
    if score < thresholds.high_max:
        return "hoch"
    return "sehr hoch"


def derive_stage_by_cluster(
    cluster_scores: list[ScoreRecord],
    *,
    thresholds: StageThresholds,
) -> dict[tuple[str, str], str]:
    """
    Derive stage for latest score of each country/cluster.

    Traceability:
    - PSwR-012
    - ALG-005
    """
    latest_by_cluster: dict[tuple[str, str], ScoreRecord] = {}
    grouped: dict[tuple[str, str], list[ScoreRecord]] = defaultdict(list)
    for record in cluster_scores:
        grouped[(record.country, record.cluster)].append(record)

    for key, values in grouped.items():
        latest_by_cluster[key] = max(values, key=lambda item: item.date)

    return {
        key: map_score_to_stage(value.score_value, thresholds)
        for key, value in latest_by_cluster.items()
    }
