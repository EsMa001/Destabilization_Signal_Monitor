from __future__ import annotations

from datetime import date
from pathlib import Path

from proto.features.escalation_features import build_escalation_features
from proto.features.gdelt_features import build_tension_features
from proto.features.vulnerability_features import build_vulnerability_features
from proto.models import ScoreRecord
from proto.scoring.cluster_scores import compute_cluster_scores, compute_simple_average
from proto.scoring.confidence import (
    apply_snapshot_fallback_penalty,
    compute_confidence_score,
    derive_historical_confidence,
    derive_confidence_by_cluster,
    map_confidence,
)
from proto.scoring.subscores import compute_subscores
from proto.scoring.thresholds import StageThresholds, derive_stage_by_cluster, map_score_to_stage
from proto.scoring.trend_history import (
    HistoricalRollingRecord,
    build_historical_review_candidates,
    build_historical_rolling_records,
    build_snapshot_context_by_cluster,
    latest_points_with_value_by_series,
    latest_valid_points_by_series,
    points_on_date_by_series,
)
from proto.scoring.trend import derive_trend_by_cluster, infer_trend
from proto.sources.bridge import load_bridge_records
from proto.sources.context import load_context_records
from proto.sources.gdelt import load_gdelt_records
from proto.sources.ucdp import load_ucdp_records

COUNTRIES = ["Iran", "Israel", "Germany"]
CALIBRATED_THRESHOLDS = StageThresholds(low_max=30, elevated_max=56, high_max=80)
CALIBRATED_TREND_EPSILON = 1.25
STAGE_ELEVATED = "erh\u00f6ht"
TREND_DOWN = "r\u00fcckl\u00e4ufig"


def _build_all_features():
    # Traceability:
    # - PSwR-011
    # - ALG-004
    # - PSwR-010
    # - ALG-001
    # - ALG-002
    # - ALG-003
    gdelt_records = load_gdelt_records(Path("data/gdelt/gdelt_events.csv"))
    ucdp_records = load_ucdp_records(Path("data/ucdp/ucdp_events.csv"))
    bridge_records = load_bridge_records(Path("data/bridge/bridge_events.csv"))
    context_records = load_context_records(Path("data/context/country_context.csv"))
    return (
        build_tension_features(gdelt_records, bridge_records, countries=COUNTRIES)
        + build_escalation_features(ucdp_records, bridge_records, countries=COUNTRIES)
        + build_vulnerability_features(
            context_records,
            countries=COUNTRIES,
            feature_date=date(2026, 1, 20),
        )
    )


def test_compute_simple_average():
    """
    Traceability:
    - PSwR-011
    - ALG-004
    - TV-PSwR-011-001
    """
    assert compute_simple_average([10.0, 20.0, 30.0]) == 20.0


def test_compute_subscores_uses_3_to_5_per_cluster():
    """
    Traceability:
    - PSwR-010
    - ALG-001
    - ALG-002
    - ALG-003
    - TV-PSwR-010-001
    """
    subscores = compute_subscores(_build_all_features())
    iran_latest = [
        score
        for score in subscores
        if score.country == "Iran" and score.date == date(2026, 1, 20)
    ]
    cluster_counts: dict[str, int] = {}
    for score in iran_latest:
        cluster_counts[score.cluster] = cluster_counts.get(score.cluster, 0) + 1
    assert cluster_counts["tension"] == 3
    assert cluster_counts["escalation"] == 4
    assert cluster_counts["vulnerability"] == 3


def test_compute_cluster_scores_from_subscores():
    """
    Traceability:
    - PSwR-011
    - ALG-004
    - TV-PSwR-011-002
    """
    cluster_scores = compute_cluster_scores(compute_subscores(_build_all_features()))
    assert len(cluster_scores) == 2139
    germany_tension_latest = [
        score
        for score in cluster_scores
        if score.country == "Germany"
        and score.cluster == "tension"
        and score.date == date(2026, 1, 20)
    ]
    assert len(germany_tension_latest) == 1
    assert 0.0 <= germany_tension_latest[0].score_value <= 100.0


def test_map_score_to_stage_and_derivation():
    """
    Traceability:
    - PSwR-012
    - ALG-005
    - TV-PSwR-012-001
    """
    assert map_score_to_stage(10, CALIBRATED_THRESHOLDS) == "niedrig"
    assert map_score_to_stage(30, CALIBRATED_THRESHOLDS) == STAGE_ELEVATED
    assert map_score_to_stage(60, CALIBRATED_THRESHOLDS) == "hoch"
    assert map_score_to_stage(90, CALIBRATED_THRESHOLDS) == "sehr hoch"
    stage_map = derive_stage_by_cluster(
        compute_cluster_scores(compute_subscores(_build_all_features())),
        thresholds=CALIBRATED_THRESHOLDS,
    )
    assert stage_map[("Iran", "vulnerability")] == "sehr hoch"


def test_map_score_to_stage_with_calibrated_thresholds():
    """
    Traceability:
    - PSwR-012
    - ALG-005
    - TV-PSwR-012-003
    """
    thresholds = CALIBRATED_THRESHOLDS
    assert map_score_to_stage(29.9, thresholds) == "niedrig"
    assert map_score_to_stage(55.9, thresholds) == STAGE_ELEVATED
    assert map_score_to_stage(79.9, thresholds) == "hoch"
    assert map_score_to_stage(80.0, thresholds) == "sehr hoch"


def test_infer_and_derive_trend():
    """
    Traceability:
    - PSwR-013
    - ALG-006
    - TV-PSwR-013-001
    """
    assert infer_trend(52.0, 40.0, eps=CALIBRATED_TREND_EPSILON) == "zunehmend"
    assert infer_trend(40.0, 52.0, eps=CALIBRATED_TREND_EPSILON) == TREND_DOWN
    assert infer_trend(50.0, 49.0, eps=CALIBRATED_TREND_EPSILON) == "stabil"
    trend_map = derive_trend_by_cluster(
        compute_cluster_scores(compute_subscores(_build_all_features())),
        short_days=7,
        recent_days=30,
        delta_epsilon=CALIBRATED_TREND_EPSILON,
    )
    assert trend_map[("Germany", "tension")] == "stabil"


def test_infer_trend_with_calibrated_epsilon():
    """
    Traceability:
    - PSwR-013
    - ALG-006
    - TV-PSwR-013-003
    """
    assert infer_trend(51.2, 50.0, eps=CALIBRATED_TREND_EPSILON) == "stabil"
    assert infer_trend(51.3, 50.0, eps=CALIBRATED_TREND_EPSILON) == "zunehmend"


def test_map_and_compute_confidence():
    """
    Traceability:
    - PSwR-014
    - ALG-007
    - TV-PSwR-014-001
    """
    assert map_confidence(10) == "niedrig"
    assert map_confidence(50) == "mittel"
    assert map_confidence(90) == "hoch"
    score = compute_confidence_score(
        data_density=100.0,
        signal_consistency=80.0,
        deviation_strength=70.0,
        source_plausibility=75.0,
    )
    assert score == 82.5


def test_derive_confidence_by_cluster():
    """
    Traceability:
    - PSwR-014
    - ALG-007
    - TV-PSwR-014-002
    """
    subscores = compute_subscores(_build_all_features())
    cluster_scores = compute_cluster_scores(subscores)
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
            ("Iran", "escalation"): 3,
            ("Iran", "vulnerability"): 1,
            ("Israel", "tension"): 1,
            ("Israel", "escalation"): 2,
            ("Israel", "vulnerability"): 1,
            ("Germany", "tension"): 2,
            ("Germany", "escalation"): 1,
            ("Germany", "vulnerability"): 1,
        },
    )
    assert ("Iran", "escalation") in confidence
    assert confidence[("Iran", "escalation")][1] in {"niedrig", "mittel", "hoch"}


def test_build_historical_rolling_records_min_coverage_and_first_valid_trend():
    """
    Traceability:
    - PSwR-021
    - PSwR-025
    - PSwR-026
    - PSwR-028
    - ALG-009
    - ALG-011
    - TV-PSwR-021-002
    """
    base_scores = [
        ScoreRecord(
            score_id="iran-2026-01-01-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 1),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=50.0,
        ),
        ScoreRecord(
            score_id="iran-2026-01-02-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 2),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=60.0,
        ),
        ScoreRecord(
            score_id="iran-2026-01-04-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 4),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=70.0,
        ),
    ]
    records = build_historical_rolling_records(
        base_scores=base_scores,
        run_date=date(2026, 1, 4),
        countries=["Iran"],
        horizon_days=4,
        window_days=3,
        min_valid_days=2,
        aggregation="rolling_mean",
        delta_epsilon=1.25,
        thresholds=CALIBRATED_THRESHOLDS,
    )
    by_date = {record.date: record for record in records}
    assert by_date[date(2026, 1, 1)].is_valid is False
    assert by_date[date(2026, 1, 2)].is_valid is True
    assert by_date[date(2026, 1, 2)].rolling_value == 55.0
    assert by_date[date(2026, 1, 2)].trend == "kein_vergleich"
    assert by_date[date(2026, 1, 3)].rolling_value == 55.0
    assert by_date[date(2026, 1, 3)].trend == "stabil"
    assert by_date[date(2026, 1, 4)].rolling_value == 65.0
    assert by_date[date(2026, 1, 4)].trend == "zunehmend"
    assert by_date[date(2026, 1, 4)].valid_days == 2
    assert by_date[date(2026, 1, 4)].coverage_ratio == 0.6667


def test_derive_historical_confidence_penalizes_lower_coverage():
    """
    Traceability:
    - PSwR-027
    - ALG-012
    - TV-PSwR-027-001
    """
    full_score, _ = derive_historical_confidence(score_value=65.0, coverage_ratio=1.0)
    partial_score, _ = derive_historical_confidence(score_value=65.0, coverage_ratio=5 / 7)
    assert full_score > partial_score


def test_apply_snapshot_fallback_penalty_reduces_confidence_below_min_coverage():
    """
    Traceability:
    - PSwR-022
    - PSwR-026
    - PM-010
    - PM-012
    - OI-021
    - TV-PSwR-022-003
    """
    adjusted_score, adjusted_level, penalty = apply_snapshot_fallback_penalty(
        confidence_score=36.25,
        valid_days=2,
        min_valid_days=5,
    )
    assert penalty > 0.0
    assert adjusted_score < 36.25
    assert adjusted_level == "niedrig"

    unchanged_score, unchanged_level, unchanged_penalty = apply_snapshot_fallback_penalty(
        confidence_score=72.0,
        valid_days=5,
        min_valid_days=5,
    )
    assert unchanged_penalty == 0.0
    assert unchanged_score == 72.0
    assert unchanged_level == "hoch"


def test_latest_valid_points_by_series_ignores_later_invalid_days():
    """
    Traceability:
    - PSwR-022
    - PSwR-026
    - PM-010
    - TV-PSwR-022-001
    """
    base_scores = [
        ScoreRecord(
            score_id="iran-2026-01-01-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 1),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=40.0,
        ),
        ScoreRecord(
            score_id="iran-2026-01-02-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 2),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=60.0,
        ),
    ]
    records = build_historical_rolling_records(
        base_scores=base_scores,
        run_date=date(2026, 1, 4),
        countries=["Iran"],
        horizon_days=4,
        window_days=3,
        min_valid_days=2,
        aggregation="rolling_mean",
        delta_epsilon=1.25,
        thresholds=CALIBRATED_THRESHOLDS,
    )
    latest = latest_valid_points_by_series(records)
    point = latest[("Iran", "tension", "cluster_score")]
    assert point.date == date(2026, 1, 3)
    assert point.is_valid is True


def test_points_on_date_and_latest_with_value_cover_invalid_endpoint_case():
    """
    Traceability:
    - PSwR-022
    - PSwR-026
    - PM-010
    - OI-021
    - TV-PSwR-022-004
    """
    base_scores = [
        ScoreRecord(
            score_id="iran-2026-01-14-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 14),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=50.0,
        ),
        ScoreRecord(
            score_id="iran-2026-01-20-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 20),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=80.0,
        ),
    ]
    records = build_historical_rolling_records(
        base_scores=base_scores,
        run_date=date(2026, 1, 20),
        countries=["Iran"],
        horizon_days=7,
        window_days=7,
        min_valid_days=5,
        aggregation="rolling_mean",
        delta_epsilon=1.25,
        thresholds=CALIBRATED_THRESHOLDS,
    )
    points_on_run_date = points_on_date_by_series(records, point_date=date(2026, 1, 20))
    latest_valid = latest_valid_points_by_series(records)
    latest_with_value = latest_points_with_value_by_series(records)
    key = ("Iran", "tension", "cluster_score")
    assert key in points_on_run_date
    assert points_on_run_date[key].is_valid is False
    assert key not in latest_valid
    assert key in latest_with_value
    assert latest_with_value[key].date == date(2026, 1, 20)


def test_build_historical_rolling_records_treats_vulnerability_as_constant():
    """
    Traceability:
    - PSwR-034
    - PM-013
    - TV-PSwR-034-001
    """
    base_scores = [
        ScoreRecord(
            score_id="iran-2026-01-20-vulnerability-cluster-score",
            country="Iran",
            date=date(2026, 1, 20),
            cluster="vulnerability",
            subcluster="all",
            score_name="cluster_score",
            score_value=42.0,
        )
    ]
    records = build_historical_rolling_records(
        base_scores=base_scores,
        run_date=date(2026, 1, 22),
        countries=["Iran"],
        horizon_days=3,
        window_days=2,
        min_valid_days=2,
        aggregation="rolling_mean",
        delta_epsilon=1.25,
        thresholds=CALIBRATED_THRESHOLDS,
        constant_clusters={"vulnerability"},
    )
    by_date = {record.date: record for record in records}
    assert by_date[date(2026, 1, 22)].is_valid is True
    assert by_date[date(2026, 1, 22)].rolling_value == 42.0


def test_build_historical_rolling_records_enforces_as_of_date_semantics():
    """
    Traceability:
    - PSwR-024
    - PM-011
    - TV-PSwR-024-001
    """
    base_scores = [
        ScoreRecord(
            score_id="iran-2026-01-01-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 1),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=10.0,
        ),
        ScoreRecord(
            score_id="iran-2026-01-02-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 2),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=20.0,
        ),
        ScoreRecord(
            score_id="iran-2026-01-03-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 3),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=100.0,
        ),
    ]
    records = build_historical_rolling_records(
        base_scores=base_scores,
        run_date=date(2026, 1, 3),
        countries=["Iran"],
        horizon_days=3,
        window_days=2,
        min_valid_days=1,
        aggregation="rolling_mean",
        delta_epsilon=1.25,
        thresholds=CALIBRATED_THRESHOLDS,
    )
    by_date = {record.date: record for record in records}
    assert by_date[date(2026, 1, 2)].rolling_value == 15.0


def test_build_historical_rolling_records_uses_full_365d_horizon_inclusive():
    """
    Traceability:
    - PSyR-013
    - PSwR-030
    - PM-009
    - TV-PSyR-013-001
    """
    run_date = date(2026, 4, 4)
    base_scores = [
        ScoreRecord(
            score_id="iran-2026-04-04-tension-cluster-score",
            country="Iran",
            date=run_date,
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=50.0,
        )
    ]
    records = build_historical_rolling_records(
        base_scores=base_scores,
        run_date=run_date,
        countries=["Iran"],
        horizon_days=365,
        window_days=7,
        min_valid_days=5,
        aggregation="rolling_mean",
        delta_epsilon=1.25,
        thresholds=CALIBRATED_THRESHOLDS,
    )
    assert len(records) == 365
    assert records[0].date == date(2025, 4, 5)
    assert records[-1].date == run_date


def test_build_historical_rolling_records_keeps_missing_days_uninterpolated():
    """
    Traceability:
    - PSwR-025
    - PM-012
    - TV-PSwR-025-001
    """
    base_scores = [
        ScoreRecord(
            score_id="iran-2026-01-01-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 1),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=42.0,
        )
    ]
    records = build_historical_rolling_records(
        base_scores=base_scores,
        run_date=date(2026, 1, 9),
        countries=["Iran"],
        horizon_days=9,
        window_days=7,
        min_valid_days=5,
        aggregation="rolling_mean",
        delta_epsilon=1.25,
        thresholds=CALIBRATED_THRESHOLDS,
    )
    by_date = {record.date: record for record in records}
    assert by_date[date(2026, 1, 9)].valid_days == 0
    assert by_date[date(2026, 1, 9)].rolling_value is None
    assert by_date[date(2026, 1, 9)].is_valid is False


def test_build_snapshot_context_by_cluster_uses_historical_year_values():
    """
    Traceability:
    - PSwR-033
    - PM-014
    - TV-PSwR-033-001
    """
    base_scores = [
        ScoreRecord(
            score_id="iran-2026-01-01-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 1),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=30.0,
        ),
        ScoreRecord(
            score_id="iran-2026-01-02-tension-cluster-score",
            country="Iran",
            date=date(2026, 1, 2),
            cluster="tension",
            subcluster="all",
            score_name="cluster_score",
            score_value=90.0,
        ),
    ]
    records = build_historical_rolling_records(
        base_scores=base_scores,
        run_date=date(2026, 1, 2),
        countries=["Iran"],
        horizon_days=2,
        window_days=1,
        min_valid_days=1,
        aggregation="rolling_mean",
        delta_epsilon=1.25,
        thresholds=CALIBRATED_THRESHOLDS,
    )
    context = build_snapshot_context_by_cluster(records)
    iran_tension = context[("Iran", "tension")]
    assert iran_tension["current_value"] == 90.0
    assert iran_tension["year_max"] == 90.0
    assert iran_tension["year_min"] == 30.0
    assert iran_tension["high_or_very_high_days"] == 1


def test_build_historical_review_candidates_excludes_baseline_and_prioritizes_jump():
    """
    Traceability:
    - PSR-010
    - PSwR-029
    - PSwR-034
    - PM-013
    - PM-015
    - TV-PSwR-029-003
    """
    records = [
        HistoricalRollingRecord(
            country="Germany",
            cluster="tension",
            score_name="cluster_score",
            date=date(2026, 1, 20),
            rolling_value=40.0,
            window_days=7,
            min_valid_days=5,
            valid_days=2,
            coverage_ratio=0.2857,
            is_valid=False,
            stage=STAGE_ELEVATED,
            trend="kein_vergleich",
            confidence_score=39.0,
            confidence_level="mittel",
        ),
        HistoricalRollingRecord(
            country="Germany",
            cluster="tension",
            score_name="cluster_score",
            date=date(2026, 1, 21),
            rolling_value=50.0,
            window_days=7,
            min_valid_days=5,
            valid_days=2,
            coverage_ratio=0.2857,
            is_valid=False,
            stage=STAGE_ELEVATED,
            trend="kein_vergleich",
            confidence_score=40.0,
            confidence_level="mittel",
        ),
        HistoricalRollingRecord(
            country="Germany",
            cluster="tension",
            score_name="protest_subscore",
            date=date(2026, 1, 21),
            rolling_value=71.0,
            window_days=7,
            min_valid_days=5,
            valid_days=2,
            coverage_ratio=0.2857,
            is_valid=False,
            stage=STAGE_ELEVATED,
            trend="kein_vergleich",
            confidence_score=40.0,
            confidence_level="mittel",
        ),
        HistoricalRollingRecord(
            country="Germany",
            cluster="tension",
            score_name="crisis_subscore",
            date=date(2026, 1, 21),
            rolling_value=20.0,
            window_days=7,
            min_valid_days=5,
            valid_days=2,
            coverage_ratio=0.2857,
            is_valid=False,
            stage=STAGE_ELEVATED,
            trend="kein_vergleich",
            confidence_score=40.0,
            confidence_level="mittel",
        ),
        HistoricalRollingRecord(
            country="Germany",
            cluster="tension",
            score_name="negativity_subscore",
            date=date(2026, 1, 21),
            rolling_value=10.0,
            window_days=7,
            min_valid_days=5,
            valid_days=2,
            coverage_ratio=0.2857,
            is_valid=False,
            stage=STAGE_ELEVATED,
            trend="kein_vergleich",
            confidence_score=40.0,
            confidence_level="mittel",
        ),
        HistoricalRollingRecord(
            country="Iran",
            cluster="escalation",
            score_name="cluster_score",
            date=date(2026, 1, 22),
            rolling_value=68.0,
            window_days=7,
            min_valid_days=5,
            valid_days=1,
            coverage_ratio=0.1429,
            is_valid=False,
            stage="hoch",
            trend="kein_vergleich",
            confidence_score=34.0,
            confidence_level="niedrig",
        ),
        HistoricalRollingRecord(
            country="Iran",
            cluster="vulnerability",
            score_name="cluster_score",
            date=date(2026, 1, 22),
            rolling_value=72.0,
            window_days=7,
            min_valid_days=5,
            valid_days=7,
            coverage_ratio=1.0,
            is_valid=True,
            stage="hoch",
            trend="stabil",
            confidence_score=90.0,
            confidence_level="hoch",
        ),
    ]
    candidates = build_historical_review_candidates(
        records=records,
        snapshot_source_by_cluster={
            ("Germany", "tension"): {
                "source_mode": "historical_numeric_fallback_below_min_valid_days",
                "source_date": "2026-01-26",
            },
            ("Iran", "escalation"): {
                "source_mode": "historical_numeric_fallback_below_min_valid_days",
                "source_date": "2026-01-26",
            },
            ("Iran", "vulnerability"): {
                "source_mode": "historical_valid_endpoint",
                "source_date": "2026-04-06",
            },
        },
    )
    assert candidates
    assert all(candidate.cluster != "vulnerability" for candidate in candidates)
    assert [candidate.rank for candidate in candidates] == [1, 2]
    assert candidates[0].country == "Germany"
    assert candidates[0].cluster == "tension"
    assert candidates[0].abs_delta_previous_numeric == 10.0
    assert candidates[0].dominant_driver == "protest_subscore"
    assert candidates[0].snapshot_relation == "before_snapshot_source"
    assert candidates[0].evidence_tier == "low_coverage_numeric"
