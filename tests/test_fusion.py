from __future__ import annotations

from datetime import date

from proto.fusion.freshness import copy_default_freshness_model
from proto.fusion.models import (
    FusionHistoricalGroupScoreRecord,
    FusionHistoricalTotalScoreRecord,
    FusionTotalScoreRecord,
)
from proto.fusion.scoring import (
    build_fusion_group_scores,
    build_historical_fusion_scores,
    build_monthly_target_periods,
    build_fusion_source_signals,
    build_fusion_total_scores,
)
from proto.fusion.validation import (
    ValidationEventRegistryRecord,
    ValidationEventMarkerRecord,
    ValidationLayerDiagnosticRecord,
    ValidationPeakAttributionRecord,
    ValidationReferenceEpisodeRecord,
    ValidationTrajectoryProfileRecord,
    build_validation_summary,
    compute_peak_attribution,
    compute_peak_event_alignment,
    compute_country_profile_comparison,
    compute_historical_responsiveness,
    compute_layer_diagnostics,
    compute_snapshot_freshness_groups,
    compute_validation_episode_results,
    compute_validation_ranking,
)
from proto.observations.models import ObservationRecord

COUNTRIES = ["Iran", "Israel", "Germany"]
GROUPS = ["event", "narrative", "market_food", "shock", "displacement", "structural"]


def _observation(
    *,
    source_id: str,
    layer: str,
    signal_family: str,
    country: str,
    period_start: date,
    period_end: date,
    raw_value: float,
    normalized_value: float,
    unit: str,
) -> ObservationRecord:
    # Traceability:
    # - PSwR-043
    # - PSyR-022
    # - PSwR-041
    # - PSwR-042
    # - PSwR-045
    # - ALG-014
    return ObservationRecord(
        source_id=source_id,
        layer=layer,
        signal_family=signal_family,
        country=country,
        period_start=period_start,
        period_end=period_end,
        raw_value=raw_value,
        normalized_value=normalized_value,
        unit=unit,
        provenance=f"{source_id}_snapshot",
        quality_completeness=0.9,
    )


def test_fusion_source_signals_keep_native_periods_and_target_period():
    """
    Traceability:
    - PSwR-043
    - PSyR-022
    - TV-PSwR-043-001
    """
    run_date = date(2026, 4, 6)
    observations = [
        _observation(
            source_id="fao_ffpi",
            layer="Market/Food",
            signal_family="ffpi_price_index",
            country="Iran",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            raw_value=130.0,
            normalized_value=0.7,
            unit="index_points",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="trade_dependency_exposure",
            country="Iran",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.68,
            normalized_value=0.95,
            unit="dependency_share",
        ),
    ]
    signals = build_fusion_source_signals(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        target_period_days=365,
        source_to_group={"fao_ffpi": "market_food", "un_comtrade": "structural"},
    )
    assert len(signals) == 2
    ffpi = next(signal for signal in signals if signal.source_id == "fao_ffpi")
    comtrade = next(signal for signal in signals if signal.source_id == "un_comtrade")
    assert ffpi.native_period_end == date(2026, 1, 31)
    assert comtrade.native_period_end == date(2025, 12, 31)
    assert ffpi.target_period_end == run_date
    assert comtrade.target_period_start == date(2025, 4, 7)


def test_group_fusion_and_total_score_with_bonus_disabled():
    """
    Traceability:
    - PSwR-041
    - PSwR-042
    - PSwR-045
    - ALG-014
    - ALG-015
    - ALG-016
    - ALG-017
    - TV-PSwR-041-001
    """
    run_date = date(2026, 4, 6)
    observations = [
        _observation(
            source_id="fao_ffpi",
            layer="Market/Food",
            signal_family="ffpi_price_index",
            country="Iran",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            raw_value=134.0,
            normalized_value=0.8,
            unit="index_points",
        ),
        _observation(
            source_id="fao_fpma",
            layer="Market/Food",
            signal_family="fpma_food_warning_pressure",
            country="Iran",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            raw_value=70.0,
            normalized_value=0.6,
            unit="warning_index",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="trade_dependency_exposure",
            country="Iran",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.68,
            normalized_value=0.9,
            unit="dependency_share",
        ),
    ]
    signals = build_fusion_source_signals(
        observations=observations,
        countries=COUNTRIES,
        run_date=run_date,
        target_period_days=365,
        source_to_group={
            "fao_ffpi": "market_food",
            "fao_fpma": "market_food",
            "un_comtrade": "structural",
        },
    )
    group_scores = build_fusion_group_scores(
        signals=signals,
        countries=COUNTRIES,
        groups=GROUPS,
        source_weights={
            "market_food": {"fao_ffpi": 0.6, "fao_fpma": 0.4},
            "structural": {"un_comtrade": 1.0},
        },
        max_age_days=400,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
    )
    iran_market = next(
        record
        for record in group_scores
        if record.country == "Iran" and record.group == "market_food"
    )
    iran_structural = next(
        record
        for record in group_scores
        if record.country == "Iran" and record.group == "structural"
    )
    assert iran_market.status == "ok"
    assert iran_structural.status == "ok"
    # 0.6*0.8 + 0.4*0.6 = 0.72 -> 72.0
    assert iran_market.group_score == 72.0
    assert iran_market.confidence_score > 0.0

    total_scores = build_fusion_total_scores(
        group_records=group_scores,
        countries=COUNTRIES,
        groups=GROUPS,
        group_weights={
            "event": 0.2,
            "narrative": 0.15,
            "market_food": 0.3,
            "shock": 0.1,
            "displacement": 0.1,
            "structural": 0.15,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
    )
    iran_total = next(record for record in total_scores if record.country == "Iran")
    assert iran_total.bonus_applied is False
    assert iran_total.bonus_points == 0.0
    assert iran_total.fusion_score > 0.0
    assert iran_total.confidence_score > 0.0
    assert iran_total.expected_group_count == len(GROUPS)
    assert iran_total.available_group_ratio > 0.0
    assert iran_total.confidence_coverage_component > 0.0
    assert iran_total.dominant_group_contribution_share >= 0.0


def test_group_fusion_applies_event_recency_decay_for_stale_signals():
    """
    Traceability:
    - PSwR-041
    - PSwR-079
    - PM-039
    - ALG-028
    - TV-PSwR-079-002
    """
    run_date = date(2026, 4, 6)
    observations = [
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2025, 10, 1),
            period_end=date(2025, 10, 31),
            raw_value=0.75,
            normalized_value=0.9,
            unit="event_pressure_index",
        ),
    ]
    signals = build_fusion_source_signals(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        target_period_days=365,
        source_to_group={"gdelt_event": "event"},
    )

    decayed_scores = build_fusion_group_scores(
        signals=signals,
        countries=["Iran"],
        groups=GROUPS,
        source_weights={"event": {"gdelt_event": 1.0}},
        max_age_days=240,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        event_stale_after_days=30,
        event_decay_half_life_days=45,
        event_min_decay_factor=0.4,
    )
    no_decay_scores = build_fusion_group_scores(
        signals=signals,
        countries=["Iran"],
        groups=GROUPS,
        source_weights={"event": {"gdelt_event": 1.0}},
        max_age_days=240,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        event_stale_after_days=999,
        event_decay_half_life_days=45,
        event_min_decay_factor=0.4,
    )

    decayed_event = next(item for item in decayed_scores if item.country == "Iran" and item.group == "event")
    undecayed_event = next(item for item in no_decay_scores if item.country == "Iran" and item.group == "event")
    assert decayed_event.group_score is not None
    assert undecayed_event.group_score is not None
    assert decayed_event.group_score < undecayed_event.group_score
    assert decayed_event.group_score >= 35.0


def test_historical_fusion_scores_include_new_groups_and_trend():
    """
    Traceability:
    - PSyR-023
    - PSyR-024
    - PSyR-025
    - PSyR-026
    - PSwR-056
    - PSwR-062
    - PSwR-063
    - PSwR-066
    - TV-PSwR-056-002
    """
    run_date = date(2026, 4, 6)
    periods = build_monthly_target_periods(run_date=run_date, horizon_months=4)
    assert len(periods) == 4
    assert periods[-1][2] == run_date

    observations = [
        _observation(
            source_id=source_id,
            layer=layer,
            signal_family=f"{source_id}_signal",
            country="Iran",
            period_start=period_start,
            period_end=period_end,
            raw_value=raw_value,
            normalized_value=normalized_value,
            unit="index",
        )
        for source_id, layer, period_start, period_end, raw_value, normalized_value in [
            ("fao_ffpi", "Market/Food", date(2026, 1, 1), date(2026, 1, 31), 130.0, 0.65),
            ("fao_ffpi", "Market/Food", date(2026, 2, 1), date(2026, 2, 28), 132.0, 0.72),
            ("fao_ffpi", "Market/Food", date(2026, 3, 1), date(2026, 3, 31), 135.0, 0.82),
            ("fao_fpma", "Market/Food", date(2026, 1, 1), date(2026, 1, 31), 45.0, 0.55),
            ("fao_fpma", "Market/Food", date(2026, 2, 1), date(2026, 2, 28), 55.0, 0.62),
            ("fao_fpma", "Market/Food", date(2026, 3, 1), date(2026, 3, 31), 70.0, 0.78),
            ("un_comtrade", "Structural", date(2025, 1, 1), date(2025, 12, 31), 0.68, 0.9),
            ("gdacs", "Shock", date(2026, 1, 1), date(2026, 1, 31), 0.41, 0.58),
            ("gdacs", "Shock", date(2026, 2, 1), date(2026, 2, 28), 0.52, 0.7),
            ("gdacs", "Shock", date(2026, 3, 1), date(2026, 3, 31), 0.66, 0.86),
            ("unhcr", "Displacement", date(2026, 1, 1), date(2026, 1, 31), 0.73, 0.66),
            ("unhcr", "Displacement", date(2026, 2, 1), date(2026, 2, 28), 0.78, 0.72),
            ("unhcr", "Displacement", date(2026, 3, 1), date(2026, 3, 31), 0.83, 0.8),
            ("narrative_input", "Narrative", date(2026, 1, 1), date(2026, 1, 31), 0.45, 0.5),
            ("narrative_input", "Narrative", date(2026, 2, 1), date(2026, 2, 28), 0.53, 0.63),
            ("narrative_input", "Narrative", date(2026, 3, 1), date(2026, 3, 31), 0.61, 0.77),
            ("gdelt_event", "Event", date(2026, 1, 1), date(2026, 1, 31), 0.31, 0.44),
            ("gdelt_event", "Event", date(2026, 2, 1), date(2026, 2, 28), 0.44, 0.68),
            ("gdelt_event", "Event", date(2026, 3, 1), date(2026, 3, 31), 0.56, 0.82),
        ]
    ]

    historical_sources, historical_groups, historical_totals = build_historical_fusion_scores(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        horizon_months=4,
        groups=GROUPS,
        source_to_group={
            "fao_ffpi": "market_food",
            "fao_fpma": "market_food",
            "un_comtrade": "structural",
            "gdacs": "shock",
            "unhcr": "displacement",
            "narrative_input": "narrative",
            "gdelt_event": "event",
        },
        source_weights={
            "market_food": {"fao_ffpi": 0.6, "fao_fpma": 0.4},
            "structural": {"un_comtrade": 1.0},
            "shock": {"gdacs": 1.0},
            "displacement": {"unhcr": 1.0},
            "narrative": {"narrative_input": 1.0},
            "event": {"gdelt_event": 1.0},
        },
        group_weights={
            "event": 0.2,
            "narrative": 0.15,
            "market_food": 0.22,
            "shock": 0.16,
            "displacement": 0.14,
            "structural": 0.13,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
        max_age_days=400,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        low_max=30.0,
        elevated_max=56.0,
        high_max=80.0,
        delta_epsilon=1.25,
    )

    assert historical_sources
    assert historical_groups
    assert historical_totals

    labels = {record.period_label for record in historical_totals}
    assert len(labels) == 4
    assert any(record.group == "shock" and record.status in {"ok", "limited"} for record in historical_groups)
    assert any(record.group == "displacement" and record.status in {"ok", "limited"} for record in historical_groups)
    assert any(record.group == "narrative" and record.status in {"ok", "limited"} for record in historical_groups)
    assert any(record.group == "event" and record.status in {"ok", "limited"} for record in historical_groups)

    latest_total = max(historical_totals, key=lambda item: item.period_label)
    assert latest_total.bonus_applied is False
    assert latest_total.stage in {"niedrig", "erhoeht", "hoch", "sehr hoch"}
    assert latest_total.trend in {"zunehmend", "ruecklaeufig", "stabil", "kein_vergleich"}
    assert 0.0 <= latest_total.available_group_ratio <= 1.0
    assert latest_total.expected_group_count == len(GROUPS)
    assert latest_total.top_positive_group_1 is not None
    assert latest_total.top_positive_group_1_contribution is not None
    assert (
        latest_total.strongest_change_group is None
        or latest_total.strongest_change_delta is not None
    )
    assert latest_total.interpretation_status in {
        "standard",
        "reduced_historical_coverage",
        "limited_historical_coverage",
    }
    assert isinstance(latest_total.no_material_change, bool)


def test_historical_fusion_marks_no_material_change_when_delta_is_zero():
    """
    Traceability:
    - PSwR-063
    - PSwR-064
    - PSwR-066
    - PM-028
    - PM-029
    - ALG-022
    - TV-PSwR-064-002
    """
    run_date = date(2026, 3, 31)
    observations = [
        _observation(
            source_id="fao_ffpi",
            layer="Market/Food",
            signal_family="fao_ffpi_signal",
            country="Iran",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            raw_value=130.0,
            normalized_value=0.7,
            unit="index",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="un_comtrade_signal",
            country="Iran",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.68,
            normalized_value=0.82,
            unit="dependency_share",
        ),
    ]

    _, _, historical_totals = build_historical_fusion_scores(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        horizon_months=2,
        groups=GROUPS,
        source_to_group={
            "fao_ffpi": "market_food",
            "un_comtrade": "structural",
        },
        source_weights={
            "market_food": {"fao_ffpi": 1.0},
            "structural": {"un_comtrade": 1.0},
        },
        group_weights={
            "event": 0.2,
            "narrative": 0.15,
            "market_food": 0.22,
            "shock": 0.16,
            "displacement": 0.14,
            "structural": 0.13,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
        max_age_days=600,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        low_max=30.0,
        elevated_max=56.0,
        high_max=80.0,
        delta_epsilon=1.25,
    )

    latest_total = max(historical_totals, key=lambda item: item.target_period_end)
    assert latest_total.strongest_change_group is None
    assert latest_total.strongest_change_delta is None
    assert latest_total.no_material_change is True
    assert latest_total.interpretation_status == "limited_historical_coverage"


def test_historical_fusion_event_can_be_strongest_change_driver():
    """
    Traceability:
    - PSyR-029
    - PSwR-073
    - PSwR-064
    - PM-028
    - ALG-022
    - TV-PSwR-073-001
    """
    run_date = date(2026, 3, 31)
    observations = [
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            raw_value=0.30,
            normalized_value=0.32,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            raw_value=0.62,
            normalized_value=0.91,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=0.40,
            normalized_value=0.50,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="trade_dependency_exposure",
            country="Iran",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.68,
            normalized_value=0.82,
            unit="dependency_share",
        ),
    ]
    _, _, totals = build_historical_fusion_scores(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        horizon_months=3,
        groups=GROUPS,
        source_to_group={
            "gdelt_event": "event",
            "un_comtrade": "structural",
        },
        source_weights={
            "event": {"gdelt_event": 1.0},
            "structural": {"un_comtrade": 1.0},
        },
        group_weights={
            "event": 0.2,
            "narrative": 0.15,
            "market_food": 0.22,
            "shock": 0.16,
            "displacement": 0.14,
            "structural": 0.13,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
        max_age_days=400,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        low_max=30.0,
        elevated_max=56.0,
        high_max=80.0,
        delta_epsilon=1.25,
    )
    latest = max(totals, key=lambda item: item.target_period_end)
    assert latest.strongest_change_group == "event"
    assert latest.strongest_change_delta is not None
    assert latest.no_material_change is False


def test_validation_episode_metrics_and_summary_are_computed():
    """
    Traceability:
    - PSwR-077
    - PSwR-080
    - ALG-025
    - ALG-028
    - TV-PSwR-077-001
    """
    run_date = date(2026, 3, 31)
    observations = [
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            raw_value=0.2,
            normalized_value=0.25,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            raw_value=0.5,
            normalized_value=0.72,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=0.6,
            normalized_value=0.88,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="trade_dependency_exposure",
            country="Iran",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.68,
            normalized_value=0.86,
            unit="dependency_share",
        ),
    ]
    _, historical_groups, historical_totals = build_historical_fusion_scores(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        horizon_months=3,
        groups=GROUPS,
        source_to_group={
            "gdelt_event": "event",
            "un_comtrade": "structural",
        },
        source_weights={
            "event": {"gdelt_event": 1.0},
            "structural": {"un_comtrade": 1.0},
        },
        group_weights={
            "event": 0.6,
            "narrative": 0.1,
            "market_food": 0.1,
            "shock": 0.1,
            "displacement": 0.05,
            "structural": 0.05,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
        max_age_days=240,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        low_max=34.0,
        elevated_max=60.0,
        high_max=82.0,
        delta_epsilon=2.0,
    )

    episode_results = compute_validation_episode_results(
        reference_episodes=[
            ValidationReferenceEpisodeRecord(
                episode_id="IRN-TEST-2026-Q1",
                country="Iran",
                period_start=date(2026, 1, 1),
                period_end=date(2026, 3, 31),
                expected_peak_period="2026-03",
                expected_total_reaction="high",
                expected_groups="event|structural",
                timing_tolerance_months=1,
                real_world_summary="Synthetic Q1 stress anchor",
                expected_total_summary="High response expected",
            )
        ],
        historical_total_records=historical_totals,
        historical_group_records=historical_groups,
        group_activation_threshold=55.0,
    )
    assert len(episode_results) == 1
    result = episode_results[0]
    assert result.data_available is True
    assert result.peak_hit is True
    assert result.timing_fit is True
    assert result.expected_group_hit is True
    assert result.group_match_ratio is not None
    assert result.group_match_ratio > 0.0

    summary = build_validation_summary(
        episode_results=episode_results,
        ranking_results=[],
        ranking_fit_score=1.0,
        ranking_plausible=True,
        layer_diagnostics=[],
    )
    assert summary["episodes_with_data"] == 1
    assert summary["peak_hit_rate"] == 1.0
    assert summary["timing_fit_rate"] == 1.0


def test_validation_ranking_and_layer_diagnostics_detect_outliers_and_support_profile():
    """
    Traceability:
    - PSwR-077
    - PSwR-081
    - ALG-026
    - ALG-027
    - TV-PSwR-081-001
    """
    run_date = date(2026, 4, 6)
    observations = [
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=0.62,
            normalized_value=0.63,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Israel",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=0.49,
            normalized_value=0.52,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Germany",
            period_start=date(2025, 12, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.2,
            normalized_value=0.24,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="fao_ffpi",
            layer="Market/Food",
            signal_family="ffpi_price_index",
            country="Iran",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=136.0,
            normalized_value=0.82,
            unit="index_points",
        ),
        _observation(
            source_id="fao_ffpi",
            layer="Market/Food",
            signal_family="ffpi_price_index",
            country="Israel",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=128.0,
            normalized_value=0.7,
            unit="index_points",
        ),
        _observation(
            source_id="fao_ffpi",
            layer="Market/Food",
            signal_family="ffpi_price_index",
            country="Germany",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=132.0,
            normalized_value=0.76,
            unit="index_points",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="trade_dependency_exposure",
            country="Iran",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.68,
            normalized_value=0.95,
            unit="dependency_share",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="trade_dependency_exposure",
            country="Israel",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.35,
            normalized_value=0.22,
            unit="dependency_share",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="trade_dependency_exposure",
            country="Germany",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.31,
            normalized_value=0.05,
            unit="dependency_share",
        ),
    ]
    signals = build_fusion_source_signals(
        observations=observations,
        countries=COUNTRIES,
        run_date=run_date,
        target_period_days=365,
        source_to_group={
            "gdelt_event": "event",
            "fao_ffpi": "market_food",
            "un_comtrade": "structural",
        },
    )
    group_scores = build_fusion_group_scores(
        signals=signals,
        countries=COUNTRIES,
        groups=GROUPS,
        source_weights={
            "event": {"gdelt_event": 1.0},
            "market_food": {"fao_ffpi": 1.0},
            "structural": {"un_comtrade": 1.0},
        },
        max_age_days=240,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
    )
    total_scores = build_fusion_total_scores(
        group_records=group_scores,
        countries=COUNTRIES,
        groups=GROUPS,
        group_weights={
            "event": 0.18,
            "narrative": 0.16,
            "market_food": 0.2,
            "shock": 0.17,
            "displacement": 0.17,
            "structural": 0.12,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
    )

    ranking_records, ranking_fit_score, ranking_plausible = compute_validation_ranking(
        total_records=total_scores,
        expected_ranking=["Iran", "Israel", "Germany"],
    )
    assert len(ranking_records) == 3
    assert ranking_plausible is True
    assert ranking_fit_score >= 0.66

    diagnostics = compute_layer_diagnostics(
        group_records=group_scores,
        total_records=total_scores,
        source_signals=signals,
        group_weights={
            "event": 0.18,
            "narrative": 0.16,
            "market_food": 0.2,
            "shock": 0.17,
            "displacement": 0.17,
            "structural": 0.12,
        },
        group_activation_threshold=55.0,
        dominance_share_threshold=0.34,
        market_food_dominance_threshold=0.34,
        structural_outlier_gap=30.0,
        event_stale_days=45,
    )
    iran_diag = next(item for item in diagnostics if item.country == "Iran")
    germany_diag = next(item for item in diagnostics if item.country == "Germany")
    assert iran_diag.structural_outlier_flag is True
    assert iran_diag.support_profile == "broad"
    assert germany_diag.event_stale_flag is True
    assert germany_diag.support_profile == "narrow"


def test_freshness_decay_and_confidence_penalty_reduce_stale_event_impact():
    """
    Traceability:
    - PSwR-083
    - PSwR-084
    - PSwR-087
    - PM-042
    - PM-043
    - ALG-029
    - TV-PSwR-083-001
    """
    run_date = date(2026, 4, 6)
    freshness_model = copy_default_freshness_model()

    stale_signals = build_fusion_source_signals(
        observations=[
            _observation(
                source_id="gdelt_event",
                layer="Event",
                signal_family="observed_conflict_disruption_pressure",
                country="Iran",
                period_start=date(2026, 1, 1),
                period_end=date(2026, 1, 26),
                raw_value=0.8,
                normalized_value=0.8,
                unit="event_pressure_index",
            )
        ],
        countries=["Iran"],
        run_date=run_date,
        target_period_days=365,
        source_to_group={"gdelt_event": "event"},
    )
    fresh_signals = build_fusion_source_signals(
        observations=[
            _observation(
                source_id="gdelt_event",
                layer="Event",
                signal_family="observed_conflict_disruption_pressure",
                country="Iran",
                period_start=date(2026, 3, 1),
                period_end=date(2026, 4, 4),
                raw_value=0.8,
                normalized_value=0.8,
                unit="event_pressure_index",
            )
        ],
        countries=["Iran"],
        run_date=run_date,
        target_period_days=365,
        source_to_group={"gdelt_event": "event"},
    )

    stale_group = build_fusion_group_scores(
        signals=stale_signals,
        countries=["Iran"],
        groups=GROUPS,
        source_weights={"event": {"gdelt_event": 1.0}},
        max_age_days=240,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        freshness_model=freshness_model,
        event_fresh_boost_factor=1.08,
    )
    fresh_group = build_fusion_group_scores(
        signals=fresh_signals,
        countries=["Iran"],
        groups=GROUPS,
        source_weights={"event": {"gdelt_event": 1.0}},
        max_age_days=240,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        freshness_model=freshness_model,
        event_fresh_boost_factor=1.08,
    )

    stale_event = next(item for item in stale_group if item.group == "event")
    fresh_event = next(item for item in fresh_group if item.group == "event")
    assert stale_event.group_score is not None
    assert fresh_event.group_score is not None
    assert stale_event.confidence_score < fresh_event.confidence_score
    assert stale_event.group_score < fresh_event.group_score


def test_snapshot_freshness_diagnostics_detect_stale_burden_and_dynamic_readiness():
    """
    Traceability:
    - PSwR-085
    - PSwR-089
    - PM-046
    - PM-047
    - ALG-030
    - TV-PSwR-085-001
    """
    run_date = date(2026, 4, 6)
    freshness_model = copy_default_freshness_model()
    observations = [
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Germany",
            period_start=date(2025, 12, 1),
            period_end=date(2025, 12, 20),
            raw_value=0.35,
            normalized_value=0.66,
            unit="event_pressure_index",
        ),
        _observation(
            source_id="fao_ffpi",
            layer="Market/Food",
            signal_family="ffpi_price_index",
            country="Germany",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=130.0,
            normalized_value=0.78,
            unit="index_points",
        ),
    ]
    signals = build_fusion_source_signals(
        observations=observations,
        countries=["Germany"],
        run_date=run_date,
        target_period_days=365,
        source_to_group={
            "gdelt_event": "event",
            "fao_ffpi": "market_food",
        },
    )
    group_scores = build_fusion_group_scores(
        signals=signals,
        countries=["Germany"],
        groups=GROUPS,
        source_weights={
            "event": {"gdelt_event": 1.0},
            "market_food": {"fao_ffpi": 1.0},
        },
        max_age_days=240,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        freshness_model=freshness_model,
        event_fresh_boost_factor=1.08,
    )
    totals = build_fusion_total_scores(
        group_records=group_scores,
        countries=["Germany"],
        groups=GROUPS,
        group_weights={
            "event": 0.18,
            "narrative": 0.16,
            "market_food": 0.2,
            "shock": 0.17,
            "displacement": 0.17,
            "structural": 0.12,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
    )

    freshness_groups = compute_snapshot_freshness_groups(
        source_signals=signals,
        group_records=group_scores,
        group_weights={
            "event": 0.18,
            "narrative": 0.16,
            "market_food": 0.2,
            "shock": 0.17,
            "displacement": 0.17,
            "structural": 0.12,
        },
        freshness_model=freshness_model,
        event_fresh_boost_factor=1.08,
    )
    event_freshness = next(item for item in freshness_groups if item.group == "event")
    assert event_freshness.freshness_class == "stale"
    assert event_freshness.last_fresh_observation_date is None

    diagnostics = compute_layer_diagnostics(
        group_records=group_scores,
        total_records=totals,
        source_signals=signals,
        group_weights={
            "event": 0.18,
            "narrative": 0.16,
            "market_food": 0.2,
            "shock": 0.17,
            "displacement": 0.17,
            "structural": 0.12,
        },
        group_activation_threshold=55.0,
        dominance_share_threshold=0.34,
        market_food_dominance_threshold=0.34,
        structural_outlier_gap=30.0,
        event_stale_days=45,
        freshness_model=freshness_model,
        event_fresh_boost_factor=1.08,
    )
    germany = diagnostics[0]
    assert germany.event_stale_flag is True
    assert germany.dynamic_layer_readiness is False
    assert germany.stale_contribution_share > 0.0
    assert germany.stale_support_profile in {"narrow", "broad"}


def test_historical_responsiveness_metrics_and_coverage_interpretation_remain_consistent():
    """
    Traceability:
    - PSwR-056
    - PSwR-063
    - PSwR-086
    - PM-029
    - PM-045
    - ALG-021
    - ALG-031
    - TV-PSwR-086-001
    """
    run_date = date(2026, 4, 6)
    _, _, historical_totals = build_historical_fusion_scores(
        observations=[
            _observation(
                source_id="gdelt_event",
                layer="Event",
                signal_family="observed_conflict_disruption_pressure",
                country="Iran",
                period_start=date(2026, 1, 1),
                period_end=date(2026, 1, 31),
                raw_value=0.25,
                normalized_value=0.2,
                unit="event_pressure_index",
            ),
            _observation(
                source_id="gdelt_event",
                layer="Event",
                signal_family="observed_conflict_disruption_pressure",
                country="Iran",
                period_start=date(2026, 2, 1),
                period_end=date(2026, 2, 28),
                raw_value=0.5,
                normalized_value=0.55,
                unit="event_pressure_index",
            ),
            _observation(
                source_id="gdelt_event",
                layer="Event",
                signal_family="observed_conflict_disruption_pressure",
                country="Iran",
                period_start=date(2026, 3, 1),
                period_end=date(2026, 3, 31),
                raw_value=0.75,
                normalized_value=0.9,
                unit="event_pressure_index",
            ),
            _observation(
                source_id="un_comtrade",
                layer="Structural",
                signal_family="trade_dependency_exposure",
                country="Iran",
                period_start=date(2025, 1, 1),
                period_end=date(2025, 12, 31),
                raw_value=0.66,
                normalized_value=0.72,
                unit="dependency_share",
            ),
        ],
        countries=["Iran"],
        run_date=run_date,
        horizon_months=4,
        groups=GROUPS,
        source_to_group={"gdelt_event": "event", "un_comtrade": "structural"},
        source_weights={"event": {"gdelt_event": 1.0}, "structural": {"un_comtrade": 1.0}},
        group_weights={
            "event": 0.6,
            "narrative": 0.1,
            "market_food": 0.1,
            "shock": 0.1,
            "displacement": 0.05,
            "structural": 0.05,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
        max_age_days=240,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        low_max=34.0,
        elevated_max=60.0,
        high_max=82.0,
        delta_epsilon=2.0,
        limited_coverage_threshold=0.5,
        reduced_coverage_threshold=0.75,
    )
    assert historical_totals
    assert any(item.interpretation_status == "limited_historical_coverage" for item in historical_totals)

    responsiveness = compute_historical_responsiveness(
        historical_total_records=historical_totals,
        delta_threshold=2.0,
    )
    assert len(responsiveness) == 1
    iran = responsiveness[0]
    assert iran.country == "Iran"
    assert iran.period_count >= 3
    assert iran.compared_period_count >= 2
    assert iran.max_abs_delta > 0.0
    assert iran.significant_change_count >= 1
    assert iran.responsiveness_profile in {"reactive", "balanced"}


def test_country_profile_comparison_metrics_cover_profiles_peaks_and_ranking_trajectory():
    """
    Traceability:
    - PSR-024
    - PSyR-036
    - PSyR-037
    - PSyR-038
    - PSwR-098
    - PSwR-099
    - PSwR-100
    - PSwR-102
    - ALG-036
    - ALG-037
    - ALG-038
    - ALG-039
    - ALG-040
    - TV-PSwR-098-001
    """
    totals = [
        FusionTotalScoreRecord(
            country="Iran",
            target_period_start=date(2025, 4, 1),
            target_period_end=date(2026, 3, 31),
            fusion_score=68.0,
            confidence_score=84.0,
            confidence_level="hoch",
            group_count=2,
            expected_group_count=2,
            available_group_count=2,
            available_group_ratio=1.0,
            confidence_coverage_component=100.0,
            confidence_recency_component=88.0,
            confidence_completeness_component=82.0,
            confidence_consistency_component=76.0,
            confidence_dominance_penalty=0.0,
            confidence_limited_penalty=0.0,
            dominant_group_contribution_share=0.58,
            groups_used="event,structural",
            bonus_applied=False,
            bonus_points=0.0,
        ),
        FusionTotalScoreRecord(
            country="Israel",
            target_period_start=date(2025, 4, 1),
            target_period_end=date(2026, 3, 31),
            fusion_score=49.0,
            confidence_score=82.0,
            confidence_level="hoch",
            group_count=2,
            expected_group_count=2,
            available_group_count=2,
            available_group_ratio=1.0,
            confidence_coverage_component=100.0,
            confidence_recency_component=87.0,
            confidence_completeness_component=81.0,
            confidence_consistency_component=75.0,
            confidence_dominance_penalty=0.0,
            confidence_limited_penalty=0.0,
            dominant_group_contribution_share=0.52,
            groups_used="event,structural",
            bonus_applied=False,
            bonus_points=0.0,
        ),
    ]
    historical_totals = [
        FusionHistoricalTotalScoreRecord(
            country=country,
            period_label=period_label,
            target_period_start=date(2026, month, 1),
            target_period_end=target_end,
            fusion_score=fusion_score,
            stage=stage,
            trend=trend,
            confidence_score=82.0,
            confidence_level="hoch",
            group_count=2,
            expected_group_count=2,
            available_group_count=2,
            available_group_ratio=1.0,
            confidence_coverage_component=100.0,
            confidence_recency_component=87.0,
            confidence_completeness_component=81.0,
            confidence_consistency_component=75.0,
            confidence_dominance_penalty=0.0,
            confidence_limited_penalty=0.0,
            dominant_group_contribution_share=0.55,
            groups_used="event,structural",
            dominant_group=dominant_group,
            dominant_group_delta=None,
            top_positive_group_1=dominant_group,
            top_positive_group_1_contribution=dominant_contribution,
            top_positive_group_2="structural" if dominant_group == "event" else "event",
            top_positive_group_2_contribution=20.0,
            strongest_change_group=dominant_group,
            strongest_change_delta=4.0,
            no_material_change=False,
            interpretation_status="standard",
            bonus_applied=False,
            bonus_points=0.0,
        )
        for country, period_label, month, target_end, fusion_score, stage, trend, dominant_group, dominant_contribution in [
            ("Iran", "2026-01", 1, date(2026, 1, 31), 60.0, "hoch", "kein_vergleich", "event", 36.0),
            ("Iran", "2026-02", 2, date(2026, 2, 28), 72.0, "hoch", "zunehmend", "event", 43.0),
            ("Iran", "2026-03", 3, date(2026, 3, 31), 68.0, "hoch", "ruecklaeufig", "event", 40.0),
            ("Israel", "2026-01", 1, date(2026, 1, 31), 44.0, "erhoeht", "kein_vergleich", "structural", 28.0),
            ("Israel", "2026-02", 2, date(2026, 2, 28), 52.0, "erhoeht", "zunehmend", "event", 31.0),
            ("Israel", "2026-03", 3, date(2026, 3, 31), 49.0, "erhoeht", "ruecklaeufig", "event", 29.0),
        ]
    ]
    historical_groups = [
        FusionHistoricalGroupScoreRecord(
            country=country,
            group=group,
            period_label=period_label,
            target_period_start=date(2026, month, 1),
            target_period_end=target_end,
            group_score=group_score,
            status="ok",
            source_count=1,
            expected_source_count=1,
            source_coverage_ratio=1.0,
            confidence_score=80.0,
            confidence_level="hoch",
            sources_used=f"{group}_source",
        )
        for country, period_label, month, target_end, group, group_score in [
            ("Iran", "2026-01", 1, date(2026, 1, 31), "event", 70.0),
            ("Iran", "2026-01", 1, date(2026, 1, 31), "structural", 45.0),
            ("Iran", "2026-02", 2, date(2026, 2, 28), "event", 85.0),
            ("Iran", "2026-02", 2, date(2026, 2, 28), "structural", 48.0),
            ("Iran", "2026-03", 3, date(2026, 3, 31), "event", 78.0),
            ("Iran", "2026-03", 3, date(2026, 3, 31), "structural", 52.0),
            ("Israel", "2026-01", 1, date(2026, 1, 31), "event", 40.0),
            ("Israel", "2026-01", 1, date(2026, 1, 31), "structural", 52.0),
            ("Israel", "2026-02", 2, date(2026, 2, 28), "event", 60.0),
            ("Israel", "2026-02", 2, date(2026, 2, 28), "structural", 47.0),
            ("Israel", "2026-03", 3, date(2026, 3, 31), "event", 54.0),
            ("Israel", "2026-03", 3, date(2026, 3, 31), "structural", 44.0),
        ]
    ]

    diagnostics = [
        ValidationLayerDiagnosticRecord(
            country="Iran",
            fusion_score=68.0,
            dominant_group="event",
            dominant_group_share=0.58,
            dominance_flag=True,
            market_food_dominance_flag=False,
            event_stale_flag=False,
            governance_score=None,
            governance_contribution_share=0.0,
            governance_instability_flag=False,
            governance_low_freshness_flag=False,
            structural_score=52.0,
            structural_outlier_flag=False,
            structural_contribution_share=0.31,
            active_group_count=2,
            available_group_count=2,
            layer_support_ratio=1.0,
            support_profile="broad",
            fresh_signal_count=2,
            aging_signal_count=0,
            stale_signal_count=0,
            fresh_group_count=2,
            aging_group_count=0,
            stale_group_count=0,
            fresh_contribution_share=0.82,
            aging_contribution_share=0.18,
            stale_contribution_share=0.0,
            fresh_support_profile="broad",
            stale_support_profile="none",
            dominant_fresh_group="event",
            dominant_aging_group=None,
            dominant_stale_group=None,
            dynamic_layer_readiness=True,
            latest_fresh_observation_date=date(2026, 3, 31),
        ),
        ValidationLayerDiagnosticRecord(
            country="Israel",
            fusion_score=49.0,
            dominant_group="event",
            dominant_group_share=0.52,
            dominance_flag=True,
            market_food_dominance_flag=False,
            event_stale_flag=False,
            governance_score=None,
            governance_contribution_share=0.0,
            governance_instability_flag=False,
            governance_low_freshness_flag=False,
            structural_score=47.0,
            structural_outlier_flag=False,
            structural_contribution_share=0.48,
            active_group_count=1,
            available_group_count=2,
            layer_support_ratio=0.5,
            support_profile="narrow",
            fresh_signal_count=1,
            aging_signal_count=1,
            stale_signal_count=0,
            fresh_group_count=1,
            aging_group_count=1,
            stale_group_count=0,
            fresh_contribution_share=0.45,
            aging_contribution_share=0.55,
            stale_contribution_share=0.0,
            fresh_support_profile="narrow",
            stale_support_profile="none",
            dominant_fresh_group="event",
            dominant_aging_group="structural",
            dominant_stale_group=None,
            dynamic_layer_readiness=False,
            latest_fresh_observation_date=date(2026, 3, 31),
        ),
    ]

    profiles, peaks, group_profiles, ranking_trajectory = compute_country_profile_comparison(
        total_records=totals,
        historical_total_records=historical_totals,
        historical_group_records=historical_groups,
        layer_diagnostics=diagnostics,
        group_weights={"event": 0.6, "structural": 0.4},
        group_activation_threshold=55.0,
        high_stage_threshold=60.0,
        top_peak_count=2,
    )

    assert len(profiles) == 2
    assert {item.country for item in profiles} == {"Iran", "Israel"}
    iran_profile = next(item for item in profiles if item.country == "Iran")
    assert iran_profile.year_max_score == 72.0
    assert iran_profile.year_min_score == 60.0
    assert iran_profile.peak_count >= 2

    assert len(peaks) == 4
    assert all(item.peak_rank in {1, 2} for item in peaks)
    assert all(item.country in {"Iran", "Israel"} for item in peaks)

    assert len(group_profiles) == 4
    assert any(item.country == "Iran" and item.group == "event" for item in group_profiles)
    assert any(item.country == "Israel" and item.group == "structural" for item in group_profiles)

    assert len(ranking_trajectory) == 6
    last_period = [item for item in ranking_trajectory if item.period_label == "2026-03"]
    assert len(last_period) == 2
    assert min(item.rank for item in last_period) == 1


def test_peak_attribution_decomposes_global_and_country_specific_and_marks_event_support():
    """
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
    - ALG-041
    - ALG-042
    - ALG-043
    - ALG-044
    - ALG-045
    - ALG-046
    - ALG-047
    - TV-PSwR-105-001
    """
    totals = [
        FusionTotalScoreRecord(
            country="Iran",
            target_period_start=date(2025, 4, 1),
            target_period_end=date(2026, 3, 31),
            fusion_score=72.0,
            confidence_score=83.0,
            confidence_level="hoch",
            group_count=3,
            expected_group_count=3,
            available_group_count=3,
            available_group_ratio=1.0,
            confidence_coverage_component=100.0,
            confidence_recency_component=90.0,
            confidence_completeness_component=80.0,
            confidence_consistency_component=76.0,
            confidence_dominance_penalty=0.0,
            confidence_limited_penalty=0.0,
            dominant_group_contribution_share=0.52,
            groups_used="event,market_food,structural",
            bonus_applied=False,
            bonus_points=0.0,
        ),
        FusionTotalScoreRecord(
            country="Israel",
            target_period_start=date(2025, 4, 1),
            target_period_end=date(2026, 3, 31),
            fusion_score=54.0,
            confidence_score=80.0,
            confidence_level="hoch",
            group_count=3,
            expected_group_count=3,
            available_group_count=3,
            available_group_ratio=1.0,
            confidence_coverage_component=100.0,
            confidence_recency_component=87.0,
            confidence_completeness_component=79.0,
            confidence_consistency_component=74.0,
            confidence_dominance_penalty=0.0,
            confidence_limited_penalty=0.0,
            dominant_group_contribution_share=0.5,
            groups_used="event,market_food,structural",
            bonus_applied=False,
            bonus_points=0.0,
        ),
    ]
    historical_totals = [
        FusionHistoricalTotalScoreRecord(
            country=country,
            period_label=period_label,
            target_period_start=date(2026, month, 1),
            target_period_end=target_end,
            fusion_score=fusion_score,
            stage="hoch" if fusion_score >= 60 else "erhoeht",
            trend=trend,
            confidence_score=80.0,
            confidence_level="hoch",
            group_count=3,
            expected_group_count=3,
            available_group_count=3,
            available_group_ratio=1.0,
            confidence_coverage_component=100.0,
            confidence_recency_component=88.0,
            confidence_completeness_component=79.0,
            confidence_consistency_component=74.0,
            confidence_dominance_penalty=0.0,
            confidence_limited_penalty=0.0,
            dominant_group_contribution_share=0.55,
            groups_used="event,market_food,structural",
            dominant_group=dominant_group,
            dominant_group_delta=None,
            top_positive_group_1=dominant_group,
            top_positive_group_1_contribution=35.0,
            top_positive_group_2="market_food",
            top_positive_group_2_contribution=24.0,
            strongest_change_group=dominant_group,
            strongest_change_delta=4.0,
            no_material_change=False,
            interpretation_status="standard",
            bonus_applied=False,
            bonus_points=0.0,
        )
        for country, period_label, month, target_end, fusion_score, trend, dominant_group in [
            ("Iran", "2026-01", 1, date(2026, 1, 31), 63.0, "kein_vergleich", "market_food"),
            ("Iran", "2026-02", 2, date(2026, 2, 28), 74.0, "zunehmend", "event"),
            ("Iran", "2026-03", 3, date(2026, 3, 31), 72.0, "ruecklaeufig", "event"),
            ("Israel", "2026-01", 1, date(2026, 1, 31), 47.0, "kein_vergleich", "market_food"),
            ("Israel", "2026-02", 2, date(2026, 2, 28), 57.0, "zunehmend", "market_food"),
            ("Israel", "2026-03", 3, date(2026, 3, 31), 54.0, "ruecklaeufig", "event"),
        ]
    ]
    historical_groups = [
        FusionHistoricalGroupScoreRecord(
            country=country,
            group=group,
            period_label=period_label,
            target_period_start=date(2026, month, 1),
            target_period_end=target_end,
            group_score=group_score,
            status="ok",
            source_count=1,
            expected_source_count=1,
            source_coverage_ratio=1.0,
            confidence_score=80.0,
            confidence_level="hoch",
            sources_used=f"{group}_source",
        )
        for country, period_label, month, target_end, group, group_score in [
            ("Iran", "2026-01", 1, date(2026, 1, 31), "event", 58.0),
            ("Iran", "2026-01", 1, date(2026, 1, 31), "market_food", 77.0),
            ("Iran", "2026-01", 1, date(2026, 1, 31), "structural", 48.0),
            ("Iran", "2026-02", 2, date(2026, 2, 28), "event", 86.0),
            ("Iran", "2026-02", 2, date(2026, 2, 28), "market_food", 73.0),
            ("Iran", "2026-02", 2, date(2026, 2, 28), "structural", 46.0),
            ("Iran", "2026-03", 3, date(2026, 3, 31), "event", 82.0),
            ("Iran", "2026-03", 3, date(2026, 3, 31), "market_food", 70.0),
            ("Iran", "2026-03", 3, date(2026, 3, 31), "structural", 50.0),
            ("Israel", "2026-01", 1, date(2026, 1, 31), "event", 43.0),
            ("Israel", "2026-01", 1, date(2026, 1, 31), "market_food", 62.0),
            ("Israel", "2026-01", 1, date(2026, 1, 31), "structural", 45.0),
            ("Israel", "2026-02", 2, date(2026, 2, 28), "event", 52.0),
            ("Israel", "2026-02", 2, date(2026, 2, 28), "market_food", 68.0),
            ("Israel", "2026-02", 2, date(2026, 2, 28), "structural", 44.0),
            ("Israel", "2026-03", 3, date(2026, 3, 31), "event", 58.0),
            ("Israel", "2026-03", 3, date(2026, 3, 31), "market_food", 64.0),
            ("Israel", "2026-03", 3, date(2026, 3, 31), "structural", 43.0),
        ]
    ]
    diagnostics = [
        ValidationLayerDiagnosticRecord(
            country="Iran",
            fusion_score=72.0,
            dominant_group="event",
            dominant_group_share=0.52,
            dominance_flag=True,
            market_food_dominance_flag=False,
            event_stale_flag=False,
            governance_score=None,
            governance_contribution_share=0.0,
            governance_instability_flag=False,
            governance_low_freshness_flag=False,
            structural_score=50.0,
            structural_outlier_flag=False,
            structural_contribution_share=0.24,
            active_group_count=3,
            available_group_count=3,
            layer_support_ratio=1.0,
            support_profile="broad",
            fresh_signal_count=3,
            aging_signal_count=0,
            stale_signal_count=0,
            fresh_group_count=3,
            aging_group_count=0,
            stale_group_count=0,
            fresh_contribution_share=0.78,
            aging_contribution_share=0.22,
            stale_contribution_share=0.0,
            fresh_support_profile="broad",
            stale_support_profile="none",
            dominant_fresh_group="event",
            dominant_aging_group=None,
            dominant_stale_group=None,
            dynamic_layer_readiness=True,
            latest_fresh_observation_date=date(2026, 3, 31),
        ),
        ValidationLayerDiagnosticRecord(
            country="Israel",
            fusion_score=54.0,
            dominant_group="market_food",
            dominant_group_share=0.5,
            dominance_flag=True,
            market_food_dominance_flag=True,
            event_stale_flag=False,
            governance_score=None,
            governance_contribution_share=0.0,
            governance_instability_flag=False,
            governance_low_freshness_flag=False,
            structural_score=43.0,
            structural_outlier_flag=False,
            structural_contribution_share=0.22,
            active_group_count=2,
            available_group_count=3,
            layer_support_ratio=0.67,
            support_profile="narrow",
            fresh_signal_count=2,
            aging_signal_count=1,
            stale_signal_count=0,
            fresh_group_count=2,
            aging_group_count=1,
            stale_group_count=0,
            fresh_contribution_share=0.52,
            aging_contribution_share=0.48,
            stale_contribution_share=0.0,
            fresh_support_profile="narrow",
            stale_support_profile="none",
            dominant_fresh_group="market_food",
            dominant_aging_group="structural",
            dominant_stale_group=None,
            dynamic_layer_readiness=True,
            latest_fresh_observation_date=date(2026, 3, 31),
        ),
    ]

    profiles, peaks, _, _ = compute_country_profile_comparison(
        total_records=totals,
        historical_total_records=historical_totals,
        historical_group_records=historical_groups,
        layer_diagnostics=diagnostics,
        group_weights={"event": 0.35, "market_food": 0.4, "structural": 0.25},
        group_activation_threshold=55.0,
        high_stage_threshold=60.0,
        top_peak_count=2,
    )
    markers = [
        ValidationEventMarkerRecord(
            marker_id="evt_irn_001",
            country="Iran",
            period_start=date(2026, 2, 1),
            period_end=date(2026, 3, 31),
            event_label="Regional confrontation pulse",
            event_type="security_escalation",
            support_weight=0.82,
            support_confidence=0.83,
            provenance="test_fixture",
        )
    ]
    attribution, event_support, trajectory, synchronization, summary = compute_peak_attribution(
        country_profile_records=profiles,
        peak_phase_records=peaks,
        historical_total_records=historical_totals,
        historical_group_records=historical_groups,
        layer_diagnostics=diagnostics,
        group_weights={"event": 0.35, "market_food": 0.4, "structural": 0.25},
        event_markers=markers,
    )

    assert attribution
    assert event_support
    assert trajectory
    assert synchronization
    assert summary["peak_attribution_record_count"] == len(attribution)
    assert "event_supported_peak_ratio" in summary
    assert "globally_co_moving_peak_ratio" in summary

    iran_peak = next(item for item in attribution if item.country == "Iran" and item.peak_rank == 1)
    assert iran_peak.event_support_status == "event_supported"
    assert iran_peak.dominant_group is not None
    assert 0.0 <= iran_peak.global_share <= 1.0
    assert 0.0 <= iran_peak.country_specific_share <= 1.0
    assert round(iran_peak.global_share + iran_peak.country_specific_share, 4) <= 1.0001

    israel_peak = next(item for item in attribution if item.country == "Israel" and item.peak_rank == 1)
    assert israel_peak.event_support_status in {"not_event_validated", "weakly_supported"}
    assert israel_peak.market_food_global_pressure >= 0.0
    assert israel_peak.market_food_local_pressure >= 0.0

    assert any(item.country == "Iran" for item in trajectory)
    assert any(item.country == "Israel" for item in trajectory)
    assert any(item.peak_country_ratio >= 0.5 for item in synchronization)


def test_governance_group_integrates_into_snapshot_and_historical_fusion():
    """
    Traceability:
    - PSR-023
    - PSyR-034
    - PSyR-035
    - PSwR-093
    - ALG-034
    - TV-PSwR-093-001
    """
    groups_with_governance = [
        "event",
        "narrative",
        "governance",
        "market_food",
        "shock",
        "displacement",
        "structural",
    ]
    run_date = date(2026, 4, 6)
    observations = [
        _observation(
            source_id="governance_input",
            layer="Governance",
            signal_family="governance_instability_pressure",
            country="Iran",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            raw_value=0.76,
            normalized_value=0.82,
            unit="governance_instability_index",
        ),
        _observation(
            source_id="governance_input",
            layer="Governance",
            signal_family="governance_instability_pressure",
            country="Iran",
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            raw_value=0.79,
            normalized_value=0.9,
            unit="governance_instability_index",
        ),
        _observation(
            source_id="un_comtrade",
            layer="Structural",
            signal_family="trade_dependency_exposure",
            country="Iran",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            raw_value=0.68,
            normalized_value=0.72,
            unit="dependency_share",
        ),
    ]
    signals = build_fusion_source_signals(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        target_period_days=365,
        source_to_group={
            "governance_input": "governance",
            "un_comtrade": "structural",
        },
    )
    group_scores = build_fusion_group_scores(
        signals=signals,
        countries=["Iran"],
        groups=groups_with_governance,
        source_weights={
            "governance": {"governance_input": 1.0},
            "structural": {"un_comtrade": 1.0},
        },
        max_age_days=400,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        freshness_model=copy_default_freshness_model(),
        event_fresh_boost_factor=1.08,
    )
    governance = next(item for item in group_scores if item.group == "governance")
    assert governance.status in {"ok", "limited"}
    assert governance.group_score is not None
    assert governance.group_score > 0.0

    totals = build_fusion_total_scores(
        group_records=group_scores,
        countries=["Iran"],
        groups=groups_with_governance,
        group_weights={
            "event": 0.16,
            "narrative": 0.14,
            "governance": 0.15,
            "market_food": 0.18,
            "shock": 0.14,
            "displacement": 0.13,
            "structural": 0.1,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
    )
    iran_total = totals[0]
    assert iran_total.expected_group_count == len(groups_with_governance)
    assert iran_total.available_group_count >= 2

    _, historical_groups, historical_totals = build_historical_fusion_scores(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        horizon_months=3,
        groups=groups_with_governance,
        source_to_group={
            "governance_input": "governance",
            "un_comtrade": "structural",
        },
        source_weights={
            "governance": {"governance_input": 1.0},
            "structural": {"un_comtrade": 1.0},
        },
        group_weights={
            "event": 0.16,
            "narrative": 0.14,
            "governance": 0.15,
            "market_food": 0.18,
            "shock": 0.14,
            "displacement": 0.13,
            "structural": 0.1,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
        max_age_days=400,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        low_max=34.0,
        elevated_max=60.0,
        high_max=82.0,
        delta_epsilon=2.0,
        freshness_model=copy_default_freshness_model(),
        event_fresh_boost_factor=1.08,
    )
    assert historical_groups
    assert historical_totals
    assert any(item.group == "governance" and item.status in {"ok", "limited"} for item in historical_groups)


def test_layer_diagnostics_flag_governance_instability_and_stale_governance_support():
    """
    Traceability:
    - PSwR-094
    - PSwR-085
    - PSwR-089
    - ALG-035
    - TV-PSwR-094-001
    """
    run_date = date(2026, 4, 6)
    groups_with_governance = [
        "event",
        "narrative",
        "governance",
        "market_food",
        "shock",
        "displacement",
        "structural",
    ]
    observations = [
        _observation(
            source_id="governance_input",
            layer="Governance",
            signal_family="governance_instability_pressure",
            country="Iran",
            period_start=date(2025, 7, 1),
            period_end=date(2025, 7, 31),
            raw_value=0.78,
            normalized_value=0.92,
            unit="governance_instability_index",
        ),
        _observation(
            source_id="gdelt_event",
            layer="Event",
            signal_family="observed_conflict_disruption_pressure",
            country="Iran",
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            raw_value=0.58,
            normalized_value=0.67,
            unit="event_pressure_index",
        ),
    ]
    signals = build_fusion_source_signals(
        observations=observations,
        countries=["Iran"],
        run_date=run_date,
        target_period_days=365,
        source_to_group={
            "governance_input": "governance",
            "gdelt_event": "event",
        },
    )
    group_scores = build_fusion_group_scores(
        signals=signals,
        countries=["Iran"],
        groups=groups_with_governance,
        source_weights={
            "governance": {"governance_input": 1.0},
            "event": {"gdelt_event": 1.0},
        },
        max_age_days=400,
        coverage_weight=0.35,
        recency_weight=0.25,
        completeness_weight=0.25,
        consistency_weight=0.15,
        freshness_model=copy_default_freshness_model(),
        event_fresh_boost_factor=1.08,
    )
    totals = build_fusion_total_scores(
        group_records=group_scores,
        countries=["Iran"],
        groups=groups_with_governance,
        group_weights={
            "event": 0.16,
            "narrative": 0.14,
            "governance": 0.15,
            "market_food": 0.18,
            "shock": 0.14,
            "displacement": 0.13,
            "structural": 0.1,
        },
        bonus_enabled=False,
        bonus_threshold=70.0,
        bonus_points=5.0,
        bonus_min_groups=2,
    )
    diagnostics = compute_layer_diagnostics(
        group_records=group_scores,
        total_records=totals,
        source_signals=signals,
        group_weights={
            "event": 0.16,
            "narrative": 0.14,
            "governance": 0.15,
            "market_food": 0.18,
            "shock": 0.14,
            "displacement": 0.13,
            "structural": 0.1,
        },
        group_activation_threshold=55.0,
        dominance_share_threshold=0.34,
        market_food_dominance_threshold=0.34,
        structural_outlier_gap=30.0,
        event_stale_days=45,
        freshness_model=copy_default_freshness_model(),
        event_fresh_boost_factor=1.08,
        dynamic_groups=["event", "narrative", "governance", "shock", "displacement"],
    )
    iran = diagnostics[0]
    assert iran.governance_score is not None
    assert iran.governance_instability_flag is True
    assert iran.governance_low_freshness_flag is True
    assert iran.governance_contribution_share > 0.0


def _alignment_peak(
    *,
    country: str,
    peak_rank: int,
    period_label: str,
    target_period_end: date,
    attribution_label: str = "country_specific_peak",
    event_support_status: str = "event_supported",
    dominant_group: str | None = "event",
) -> ValidationPeakAttributionRecord:
    # Traceability:
    # - PSwR-043
    # - PSyR-022
    # - PSwR-041
    # - PSwR-042
    # - PSwR-045
    # - ALG-014
    return ValidationPeakAttributionRecord(
        country=country,
        peak_rank=peak_rank,
        period_label=period_label,
        target_period_end=target_period_end,
        fusion_score=72.0,
        prominence_score=3.2,
        peak_width_periods=2,
        rise_slope=4.2,
        fall_slope=2.8,
        separation_periods=1,
        peak_quality_score=3.0,
        dominant_group=dominant_group,
        second_group="governance",
        support_profile="broad",
        support_breadth_ratio=0.75,
        dominant_group_share=0.46,
        fresh_contribution_share=0.74,
        stale_contribution_share=0.12,
        global_component_score=28.0,
        country_specific_component_score=44.0,
        global_share=0.39,
        country_specific_share=0.61,
        market_food_global_pressure=0.22,
        market_food_local_pressure=0.18,
        attribution_label=attribution_label,
        peak_confidence_score=0.81,
        peak_confidence_level="high",
        event_support_status=event_support_status,
        event_marker_count=1,
        event_marker_ids="evt_marker_test",
    )


def _alignment_trajectory(*, country: str) -> ValidationTrajectoryProfileRecord:
    # Traceability:
    # - PSwR-043
    # - PSyR-022
    # - PSwR-041
    # - PSwR-042
    # - PSwR-045
    # - ALG-014
    return ValidationTrajectoryProfileRecord(
        country=country,
        trajectory_profile="event-spiking",
        peak_count=3,
        event_supported_peak_ratio=0.67,
        weakly_supported_peak_ratio=0.0,
        globally_co_moving_peak_ratio=0.22,
        model_driven_peak_ratio=0.11,
        country_specific_peak_ratio=0.67,
        mean_global_share=0.34,
        mean_country_specific_share=0.66,
        dominant_peak_group="event",
        mean_peak_confidence_score=0.74,
        differentiation_flag=True,
    )


def test_peak_event_alignment_assigns_direct_match():
    """
    Traceability:
    - PSwR-115
    - PSwR-116
    - PM-065
    - ALG-049
    - TV-PSwR-115-001
    """
    peak = _alignment_peak(
        country="Iran",
        peak_rank=1,
        period_label="2026-03",
        target_period_end=date(2026, 3, 31),
    )
    trajectory = _alignment_trajectory(country="Iran")
    registry = [
        ValidationEventRegistryRecord(
            event_id="evtreg_irn_001",
            country="Iran",
            title="Regional confrontation pulse",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 4, 15),
            event_type="security_escalation",
            summary="Analyst fixture",
            source_category="analyst_fixture",
            source_reference="test_case",
            confidence=0.84,
            relevance_groups="event|governance",
            expected_effect_direction="country_specific",
            expected_peak_window_start=date(2026, 3, 1),
            expected_peak_window_end=date(2026, 4, 15),
            notes="",
        )
    ]
    matches, coverage, country_alignment, summary = compute_peak_event_alignment(
        peak_attribution_records=[peak],
        trajectory_profile_records=[trajectory],
        event_registry_records=registry,
    )

    assert len(matches) == 1
    assert matches[0].match_class == "direct_match"
    assert matches[0].credible_match is True
    assert matches[0].matched_event_count == 1
    assert matches[0].best_event_id == "evtreg_irn_001"
    assert coverage[0].scope == "global"
    assert coverage[0].credible_match_ratio == 1.0
    assert country_alignment[0].country == "Iran"
    assert summary["credible_match_ratio"] == 1.0


def test_peak_event_alignment_detects_multi_event_overlap():
    """
    Traceability:
    - PSwR-116
    - PSwR-118
    - PM-066
    - ALG-051
    - TV-PSwR-116-001
    """
    peak = _alignment_peak(
        country="Israel",
        peak_rank=1,
        period_label="2026-03",
        target_period_end=date(2026, 3, 20),
        attribution_label="globally_co_moving_peak",
        event_support_status="weakly_supported",
    )
    trajectory = _alignment_trajectory(country="Israel")
    registry = [
        ValidationEventRegistryRecord(
            event_id="evtreg_isr_001",
            country="Israel",
            title="Security escalation phase A",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 31),
            event_type="security_escalation",
            summary="Analyst fixture A",
            source_category="analyst_fixture",
            source_reference="test_case",
            confidence=0.82,
            relevance_groups="event|narrative",
            expected_effect_direction="mixed",
            expected_peak_window_start=date(2026, 3, 1),
            expected_peak_window_end=date(2026, 4, 5),
            notes="",
        ),
        ValidationEventRegistryRecord(
            event_id="evtreg_isr_002",
            country="Israel",
            title="Security escalation phase B",
            start_date=date(2026, 3, 10),
            end_date=date(2026, 4, 10),
            event_type="security_escalation",
            summary="Analyst fixture B",
            source_category="analyst_fixture",
            source_reference="test_case",
            confidence=0.79,
            relevance_groups="event|governance",
            expected_effect_direction="mixed",
            expected_peak_window_start=date(2026, 3, 10),
            expected_peak_window_end=date(2026, 4, 10),
            notes="",
        ),
    ]
    matches, coverage, _, summary = compute_peak_event_alignment(
        peak_attribution_records=[peak],
        trajectory_profile_records=[trajectory],
        event_registry_records=registry,
        multi_overlap_min_events=2,
    )

    assert len(matches) == 1
    assert matches[0].match_class == "multi_event_overlap"
    assert matches[0].matched_event_count >= 2
    assert coverage[0].multi_event_overlap_count == 1
    assert summary["multi_event_overlap_count"] == 1


def test_peak_event_alignment_handles_missing_country_events_without_crash():
    """
    Traceability:
    - PSwR-116
    - PSwR-118
    - PM-067
    - ALG-053
    - TV-PSwR-118-001
    """
    peak = _alignment_peak(
        country="Germany",
        peak_rank=1,
        period_label="2026-02",
        target_period_end=date(2026, 2, 28),
        event_support_status="not_event_validated",
        dominant_group="market_food",
    )
    trajectory = _alignment_trajectory(country="Germany")
    matches, coverage, country_alignment, summary = compute_peak_event_alignment(
        peak_attribution_records=[peak],
        trajectory_profile_records=[trajectory],
        event_registry_records=[],
    )

    assert len(matches) == 1
    assert matches[0].match_class == "no_credible_match"
    assert matches[0].matched_event_count == 0
    assert matches[0].uncertainty_note == "no_country_events_in_registry"
    assert coverage[0].scope == "global"
    assert coverage[0].no_credible_match_ratio == 1.0
    assert country_alignment[0].country == "Germany"
    assert summary["no_credible_match_ratio"] == 1.0
