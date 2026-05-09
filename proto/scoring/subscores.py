from __future__ import annotations

"""
Traceability:
- PSwR-010
- PM-001
"""

from collections import defaultdict
from statistics import mean

from proto.models import FeatureRecord, ScoreRecord


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def _build_tension_subscores(
    *,
    country: str,
    score_date,
    features_by_name: dict[str, list[float]],
) -> list[ScoreRecord]:
    output: list[ScoreRecord] = []
    mapping = {
        "protest_signal": "protest_subscore",
        "crisis_discourse_signal": "crisis_subscore",
        "negativity_signal": "negativity_subscore",
    }
    for feature_name, score_name in mapping.items():
        value = mean(features_by_name.get(feature_name, [0.0]))
        output.append(
            ScoreRecord(
                score_id=f"{country}-{score_date.isoformat()}-tension-{score_name}",
                country=country,
                date=score_date,
                cluster="tension",
                subcluster="na",
                score_name=score_name,
                score_value=_clamp_score(value),
            )
        )

    if "stability_signal" in features_by_name:
        stability_value = mean(features_by_name["stability_signal"])
        output.append(
            ScoreRecord(
                score_id=f"{country}-{score_date.isoformat()}-tension-stability_inverse_subscore",
                country=country,
                date=score_date,
                cluster="tension",
                subcluster="na",
                score_name="stability_inverse_subscore",
                score_value=_clamp_score(100.0 - stability_value),
            )
        )
    return output


def _build_escalation_subscores(
    *,
    country: str,
    score_date,
    features_by_name: dict[str, list[float]],
) -> list[ScoreRecord]:
    internal_features = [
        "internal_violence_signal",
        "repression_signal",
        "domestic_attack_signal",
    ]
    external_features = [
        "war_activity_signal",
        "external_attack_signal",
        "regional_spillover_signal",
    ]
    internal_values = [
        mean(features_by_name.get(name, [0.0]))
        for name in internal_features
    ]
    external_values = [
        mean(features_by_name.get(name, [0.0]))
        for name in external_features
    ]
    internal_mean = mean(internal_values)
    external_mean = mean(external_values)
    all_values = internal_values + external_values
    aggregate_mean = mean([internal_mean, external_mean])

    return [
        ScoreRecord(
            score_id=f"{country}-{score_date.isoformat()}-escalation-internal_dynamics_subscore",
            country=country,
            date=score_date,
            cluster="escalation",
            subcluster="internal",
            score_name="internal_dynamics_subscore",
            score_value=_clamp_score(internal_mean),
        ),
        ScoreRecord(
            score_id=f"{country}-{score_date.isoformat()}-escalation-external_dynamics_subscore",
            country=country,
            date=score_date,
            cluster="escalation",
            subcluster="external",
            score_name="external_dynamics_subscore",
            score_value=_clamp_score(external_mean),
        ),
        ScoreRecord(
            score_id=f"{country}-{score_date.isoformat()}-escalation-peak_subscore",
            country=country,
            date=score_date,
            cluster="escalation",
            subcluster="all",
            score_name="peak_subscore",
            score_value=_clamp_score(max(all_values)),
        ),
        ScoreRecord(
            score_id=f"{country}-{score_date.isoformat()}-escalation-intensity_subscore",
            country=country,
            date=score_date,
            cluster="escalation",
            subcluster="all",
            score_name="intensity_subscore",
            score_value=_clamp_score(aggregate_mean),
        ),
    ]


def _build_vulnerability_subscores(
    *,
    country: str,
    score_date,
    features_by_name: dict[str, list[float]],
) -> list[ScoreRecord]:
    mapping = {
        "economic_vulnerability_signal": ("economic", "economic_subscore"),
        "hybrid_vulnerability_signal": ("hybrid", "hybrid_subscore"),
        "governance_stress_signal": ("governance", "governance_subscore"),
    }
    output: list[ScoreRecord] = []
    for feature_name, (subcluster, score_name) in mapping.items():
        value = mean(features_by_name.get(feature_name, [0.0]))
        output.append(
            ScoreRecord(
                score_id=f"{country}-{score_date.isoformat()}-vulnerability-{score_name}",
                country=country,
                date=score_date,
                cluster="vulnerability",
                subcluster=subcluster,
                score_name=score_name,
                score_value=_clamp_score(value),
            )
        )
    return output


def compute_subscores(features: list[FeatureRecord]) -> list[ScoreRecord]:
    """
    Compute 3-5 subscores per cluster from feature sets.

    Traceability:
    - PSwR-010
    - ALG-001
    - ALG-002
    - ALG-003
    """
    grouped: dict[tuple[str, object, str], list[FeatureRecord]] = defaultdict(list)
    for feature in features:
        grouped[(feature.country, feature.date, feature.cluster)].append(feature)

    output: list[ScoreRecord] = []
    for (country, score_date, cluster), cluster_features in sorted(grouped.items()):
        features_by_name: dict[str, list[float]] = defaultdict(list)
        for feature in cluster_features:
            features_by_name[feature.feature_name].append(feature.feature_value)

        if cluster == "tension":
            output.extend(
                _build_tension_subscores(
                    country=country,
                    score_date=score_date,
                    features_by_name=features_by_name,
                )
            )
        elif cluster == "escalation":
            output.extend(
                _build_escalation_subscores(
                    country=country,
                    score_date=score_date,
                    features_by_name=features_by_name,
                )
            )
        elif cluster == "vulnerability":
            output.extend(
                _build_vulnerability_subscores(
                    country=country,
                    score_date=score_date,
                    features_by_name=features_by_name,
                )
            )
    return output
