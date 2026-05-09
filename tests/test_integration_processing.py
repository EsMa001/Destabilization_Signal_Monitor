from __future__ import annotations

from datetime import date
from pathlib import Path

from proto.models import FeatureRecord, ScoreRecord, SourceRecord
from proto.runs.compare_runs import compare_summary_records
from proto.scoring.cluster_scores import compute_cluster_scores
from proto.scoring.confidence import derive_confidence_by_cluster
from proto.scoring.subscores import compute_subscores
from proto.scoring.thresholds import StageThresholds, derive_stage_by_cluster
from proto.scoring.trend import derive_trend_by_cluster
from proto.sources.bridge import load_bridge_records
from proto.sources.context import load_context_records
from proto.sources.gdelt import load_gdelt_records
from proto.sources.ucdp import load_ucdp_records
from proto.features.gdelt_features import build_tension_features
from proto.features.escalation_features import build_escalation_features
from proto.features.vulnerability_features import build_vulnerability_features

COUNTRIES = ["Iran", "Israel", "Germany"]
CALIBRATED_THRESHOLDS = StageThresholds(low_max=30, elevated_max=56, high_max=80)
CALIBRATED_TREND_EPSILON = 1.25


def _latest_summary_records_for_gdelt(gdelt_path: Path) -> list[dict]:
    # Traceability:
    # - PSwR-001
    # - PSwR-003
    # - PSwR-004
    # - PSwR-005
    # - PSwR-006
    # - PSwR-007
    gdelt_records = load_gdelt_records(gdelt_path)
    ucdp_records = load_ucdp_records(Path("data/ucdp/ucdp_events.csv"))
    bridge_records = load_bridge_records(Path("data/bridge/bridge_events.csv"))
    context_records = load_context_records(Path("data/context/country_context.csv"))
    features = (
        build_tension_features(gdelt_records, bridge_records, countries=COUNTRIES)
        + build_escalation_features(ucdp_records, bridge_records, countries=COUNTRIES)
        + build_vulnerability_features(context_records, countries=COUNTRIES, feature_date=date(2026, 1, 20))
    )
    cluster_scores = compute_cluster_scores(compute_subscores(features))
    latest_by_cluster: dict[tuple[str, str], ScoreRecord] = {}
    for score in cluster_scores:
        key = (score.country, score.cluster)
        previous = latest_by_cluster.get(key)
        if previous is None or score.date > previous.date:
            latest_by_cluster[key] = score
    return [
        {
            "country": key[0],
            "cluster": key[1],
            "cluster_score": value.score_value,
        }
        for key, value in latest_by_cluster.items()
    ]


def test_integration_raw_to_feature_generation():
    """
    Traceability:
    - PSwR-001
    - PSwR-003
    - PSwR-004
    - PSwR-005
    - PSwR-006
    - PSwR-007
    - PSwR-008
    - PSwR-009
    - PSyR-005
    - ALG-001
    - ALG-002
    - ALG-003
    - TV-PSwR-001-INT-001
    """
    gdelt_records = load_gdelt_records(Path("data/gdelt/gdelt_events.csv"))
    ucdp_records = load_ucdp_records(Path("data/ucdp/ucdp_events.csv"))
    bridge_records = load_bridge_records(Path("data/bridge/bridge_events.csv"))
    context_records = load_context_records(Path("data/context/country_context.csv"))

    assert gdelt_records and isinstance(gdelt_records[0], SourceRecord)
    assert ucdp_records and isinstance(ucdp_records[0], SourceRecord)

    features = (
        build_tension_features(gdelt_records, bridge_records, countries=COUNTRIES)
        + build_escalation_features(ucdp_records, bridge_records, countries=COUNTRIES)
        + build_vulnerability_features(context_records, countries=COUNTRIES, feature_date=date(2026, 1, 20))
    )
    assert features and isinstance(features[0], FeatureRecord)
    assert all(feature.cluster in {"tension", "escalation", "vulnerability"} for feature in features)
    assert any(feature.cluster == "tension" for feature in features)
    assert any(feature.cluster == "escalation" for feature in features)
    assert any(feature.cluster == "vulnerability" for feature in features)


def test_integration_features_to_scoring_logic():
    """
    Traceability:
    - PSwR-010
    - PSwR-011
    - PSwR-012
    - PSwR-013
    - PSwR-014
    - ALG-004
    - ALG-005
    - ALG-006
    - ALG-007
    - TV-PSwR-010-INT-001
    """
    gdelt_records = load_gdelt_records(Path("data/gdelt/gdelt_events.csv"))
    ucdp_records = load_ucdp_records(Path("data/ucdp/ucdp_events.csv"))
    bridge_records = load_bridge_records(Path("data/bridge/bridge_events.csv"))
    context_records = load_context_records(Path("data/context/country_context.csv"))

    features = (
        build_tension_features(gdelt_records, bridge_records, countries=COUNTRIES)
        + build_escalation_features(ucdp_records, bridge_records, countries=COUNTRIES)
        + build_vulnerability_features(context_records, countries=COUNTRIES, feature_date=date(2026, 1, 20))
    )
    subscores = compute_subscores(features)
    cluster_scores = compute_cluster_scores(subscores)
    stages = derive_stage_by_cluster(cluster_scores, thresholds=CALIBRATED_THRESHOLDS)
    trends = derive_trend_by_cluster(
        cluster_scores,
        short_days=7,
        recent_days=30,
        delta_epsilon=CALIBRATED_TREND_EPSILON,
    )
    confidence = derive_confidence_by_cluster(
        subscores=subscores,
        cluster_scores=cluster_scores,
        expected_subscores_by_cluster={
            "tension": 3,
            "escalation": 4,
            "vulnerability": 3,
        },
        source_count_by_cluster={
            ("Iran", "tension"): 2,
            ("Iran", "escalation"): 2,
            ("Iran", "vulnerability"): 1,
            ("Israel", "tension"): 1,
            ("Israel", "escalation"): 2,
            ("Israel", "vulnerability"): 1,
            ("Germany", "tension"): 2,
            ("Germany", "escalation"): 1,
            ("Germany", "vulnerability"): 1,
        },
    )

    assert subscores and isinstance(subscores[0], ScoreRecord)
    assert cluster_scores and isinstance(cluster_scores[0], ScoreRecord)
    for country in COUNTRIES:
        for cluster in ("tension", "escalation", "vulnerability"):
            assert (country, cluster) in stages
            assert (country, cluster) in trends
            assert (country, cluster) in confidence


def test_integration_controlled_change_case_produces_non_zero_delta():
    """
    Traceability:
    - PSyR-009
    - PSwR-017
    - PSwR-018
    - ALG-008
    - TV-PSyR-009-008
    """
    baseline = _latest_summary_records_for_gdelt(
        Path("tests/fixtures/change_case/gdelt_events_baseline.csv")
    )
    changed = _latest_summary_records_for_gdelt(
        Path("tests/fixtures/change_case/gdelt_events_changed.csv")
    )
    comparisons = compare_summary_records(changed, baseline)

    iran_tension = next(
        entry
        for entry in comparisons
        if entry["country"] == "Iran" and entry["cluster"] == "tension"
    )
    assert iran_tension["delta_absolute"] > 0.0
    assert iran_tension["delta_relative_percent"] is not None
    assert iran_tension["delta_direction"] == "zunehmend"


def test_integration_germany_tension_protest_jump_is_data_driven_not_artifact():
    """
    Traceability:
    - PSwR-007
    - PSwR-010
    - PSwR-011
    - ALG-001
    - ALG-004
    - OI-023
    - TV-PSwR-007-002
    """
    gdelt_records = load_gdelt_records(Path("data/gdelt/gdelt_events.csv"))
    bridge_records = load_bridge_records(Path("data/bridge/bridge_events.csv"))
    tension_features = build_tension_features(gdelt_records, bridge_records, countries=COUNTRIES)
    tension_subscores = [
        score
        for score in compute_subscores(tension_features)
        if score.country == "Germany" and score.cluster == "tension"
    ]
    tension_cluster_scores = [
        score
        for score in compute_cluster_scores(tension_subscores)
        if score.country == "Germany" and score.cluster == "tension"
    ]
    tension_features_no_bridge = build_tension_features(gdelt_records, [], countries=COUNTRIES)
    tension_subscores_no_bridge = [
        score
        for score in compute_subscores(tension_features_no_bridge)
        if score.country == "Germany"
        and score.cluster == "tension"
        and score.date == date(2025, 10, 22)
    ]
    tension_subscores_with_bridge = [
        score
        for score in compute_subscores(tension_features)
        if score.country == "Germany"
        and score.cluster == "tension"
        and score.date == date(2025, 10, 22)
    ]

    germany_tension_features = [row for row in tension_features if row.country == "Germany"]
    by_feature = {(row.date, row.feature_name): row.feature_value for row in germany_tension_features}
    by_cluster = {row.date: row.score_value for row in tension_cluster_scores}

    assert by_feature[(date(2026, 1, 20), "protest_signal")] >= 0.0
    assert by_cluster[date(2026, 4, 12)] >= 0.0
    assert tension_subscores_with_bridge
    assert tension_subscores_no_bridge
    with_bridge_protest = next(
        score for score in tension_subscores_with_bridge if score.score_name == "protest_subscore"
    ).score_value
    no_bridge_protest = next(
        score for score in tension_subscores_no_bridge if score.score_name == "protest_subscore"
    ).score_value
    assert with_bridge_protest > no_bridge_protest
