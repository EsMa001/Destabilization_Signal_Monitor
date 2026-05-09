from __future__ import annotations

"""
Traceability:
- PSwR-013
- ALG-006
"""

from collections import defaultdict
from datetime import date, timedelta
from statistics import mean

from proto.models import ScoreRecord


def infer_trend(
    current_value: float,
    baseline_value: float,
    eps: float,
) -> str:
    """
    Compare current and baseline values.

    Traceability:
    - PSwR-013
    - ALG-006
    """
    delta = current_value - baseline_value
    if delta > eps:
        return "zunehmend"
    if delta < -eps:
        return "rückläufig"
    return "stabil"


def _window_mean(
    scores: list[ScoreRecord],
    start_date: date,
    end_date: date,
) -> float:
    # Traceability:
    # - PSwR-013
    # - ALG-006
    # - PM-005
    values = [
        score.score_value
        for score in scores
        if start_date <= score.date <= end_date
    ]
    if not values:
        return mean([score.score_value for score in scores])
    return mean(values)


def derive_trend_by_cluster(
    cluster_scores: list[ScoreRecord],
    *,
    short_days: int = 7,
    recent_days: int = 30,
    delta_epsilon: float,
) -> dict[tuple[str, str], str]:
    """
    Derive trend from robust 7d-vs-30d comparisons.

    Traceability:
    - PSwR-013
    - ALG-006
    - PM-005
    """
    grouped: dict[tuple[str, str], list[ScoreRecord]] = defaultdict(list)
    for score in cluster_scores:
        grouped[(score.country, score.cluster)].append(score)

    trend_by_cluster: dict[tuple[str, str], str] = {}
    for key, values in grouped.items():
        sorted_values = sorted(values, key=lambda item: item.date)
        latest_date = sorted_values[-1].date
        short_start = latest_date - timedelta(days=short_days - 1)
        recent_start = latest_date - timedelta(days=recent_days - 1)
        baseline_end = short_start - timedelta(days=1)

        short_mean = _window_mean(sorted_values, short_start, latest_date)
        baseline_candidates = [
            score
            for score in sorted_values
            if recent_start <= score.date <= baseline_end
        ]
        if baseline_candidates:
            baseline_mean = mean(item.score_value for item in baseline_candidates)
        else:
            baseline_mean = mean(item.score_value for item in sorted_values)
        trend_by_cluster[key] = infer_trend(short_mean, baseline_mean, eps=delta_epsilon)

    return trend_by_cluster
