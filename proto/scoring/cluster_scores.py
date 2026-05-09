from __future__ import annotations

"""
Traceability:
- PSwR-011
- ALG-004
"""

from collections import defaultdict

from proto.models import ScoreRecord


def compute_simple_average(values: list[float]) -> float:
    """
    Traceability:
    - PSwR-011
    - ALG-004
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def compute_cluster_scores(subscores: list[ScoreRecord]) -> list[ScoreRecord]:
    """
    Aggregate subscores into one cluster score per country/date/cluster.

    Traceability:
    - PSwR-011
    - ALG-004
    - PM-001
    """
    buckets: dict[tuple[str, object, str], list[float]] = defaultdict(list)
    for subscore in subscores:
        buckets[(subscore.country, subscore.date, subscore.cluster)].append(
            subscore.score_value
        )

    output: list[ScoreRecord] = []
    for (country, score_date, cluster), values in sorted(buckets.items()):
        cluster_score = compute_simple_average(values)
        output.append(
            ScoreRecord(
                score_id=f"{country}-{score_date.isoformat()}-{cluster}-cluster-score",
                country=country,
                date=score_date,
                cluster=cluster,
                subcluster="all",
                score_name="cluster_score",
                score_value=cluster_score,
            )
        )
    return output
