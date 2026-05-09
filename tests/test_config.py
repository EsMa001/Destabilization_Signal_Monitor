from __future__ import annotations

from pathlib import Path

import pytest

from proto.pipeline.config import ConfigValidationError, load_pipeline_config

DEFAULT_COUNTRIES = [
    "Germany",
    "Israel",
    "Iran",
    "Ukraine",
    "Russia",
    "Japan",
    "China",
    "Taiwan",
    "Poland",
    "Nigeria",
]
DEFAULT_EXPECTED_RANKING = [
    "Iran",
    "Ukraine",
    "Nigeria",
    "Russia",
    "Israel",
    "Taiwan",
    "China",
    "Poland",
    "Germany",
    "Japan",
]


def _base_config_text(*, countries: list[str]) -> str:
    # Traceability:
    # - PSwR-002
    # - PSyR-001
    # - PSyR-002
    # - PM-006
    # - PSwR-012
    # - ALG-005
    return "\n".join(
        [
            "countries:",
            *(f"  - {country}" for country in countries),
            "windows:",
            "  short_days: 7",
            "  recent_days: 30",
            "  baseline_days: 356",
            "historical:",
            "  horizon_days: 356",
            "  window_days: 7",
            "  min_valid_days: 5",
            "  aggregation: rolling_mean",
            "  countries:",
            *(f"    - {country}" for country in countries),
            "  compact_daily_report: false",
            "versions:",
            "  query_version: v1",
            "  scoring_version: v4.3",
            "  bridge_file_version: v1",
            "  context_table_version: v1",
            "output:",
            "  report_dir: outputs/runs",
            "  reference_dir: outputs/reference",
            "scoring:",
            "  stage:",
            "    low_max: 30",
            "    elevated_max: 56",
            "    high_max: 80",
            "  trend:",
            "    delta_epsilon: 1.25",
            "v3_1:",
            "  enabled: true",
            "  sources:",
            "    fao_ffpi:",
            "      path: data/fao_ffpi/fao_ffpi.csv",
            "      normalization:",
            "        method: z_score",
            "    fao_fpma:",
            "      path: data/fao_fpma/fao_fpma.csv",
            "      normalization:",
            "        method: percentile",
            "    un_comtrade:",
            "      path: data/un_comtrade/un_comtrade.csv",
            "      normalization:",
            "        method: baseline_deviation",
            "        baseline_value: 0.35",
            "        baseline_scale: 0.35",
            "    gdacs:",
            "      path: data/gdacs/gdacs_events.csv",
            "      normalization:",
            "        method: z_score",
            "    unhcr:",
            "      path: data/unhcr/unhcr_displacement.csv",
            "      normalization:",
            "        method: z_score",
            "        scope: global",
            "    narrative_input:",
            "      path: data/narrative_input/narrative_input.csv",
            "      normalization:",
            "        method: z_score",
            "        scope: global",
            "    governance_input:",
            "      path: data/governance_input/governance_input.csv",
            "      normalization:",
            "        method: z_score",
            "        scope: global",
            "    gdelt_event:",
            "      path: data/gdelt/gdelt_events.csv",
            "      normalization:",
            "        method: z_score",
            "        scope: global",
            "  fusion:",
            "    target_period_days: 365",
            "    groups:",
            "      - event",
            "      - narrative",
            "      - governance",
            "      - market_food",
            "      - shock",
            "      - displacement",
            "      - structural",
            "    source_to_group:",
            "      fao_ffpi: market_food",
            "      fao_fpma: market_food",
            "      un_comtrade: structural",
            "      gdacs: shock",
            "      unhcr: displacement",
            "      narrative_input: narrative",
            "      governance_input: governance",
            "      gdelt_event: event",
            "    source_weights:",
            "      market_food:",
            "        fao_ffpi: 0.6",
            "        fao_fpma: 0.4",
            "      structural:",
            "        un_comtrade: 1.0",
            "      shock:",
            "        gdacs: 1.0",
            "      displacement:",
            "        unhcr: 1.0",
            "      narrative:",
            "        narrative_input: 1.0",
            "      governance:",
            "        governance_input: 1.0",
            "      event:",
            "        gdelt_event: 1.0",
            "    group_weights:",
            "      event: 0.16",
            "      narrative: 0.14",
            "      governance: 0.15",
            "      market_food: 0.18",
            "      shock: 0.14",
            "      displacement: 0.13",
            "      structural: 0.1",
            "    bonus:",
            "      enabled: false",
            "      threshold: 70.0",
            "      points: 5.0",
            "      min_groups: 2",
            "    confidence:",
            "      max_age_days: 400",
            "      coverage_weight: 0.35",
            "      recency_weight: 0.25",
            "      completeness_weight: 0.25",
            "      consistency_weight: 0.15",
            "    historical:",
            "      enabled: true",
            "      target_periodicity: monthly",
            "      horizon_months: 12",
        ]
    )


def test_load_pipeline_config_default_success():
    """
    Traceability:
    - PSwR-002
    - PSyR-001
    - PSyR-002
    - PM-006
    - TV-PSwR-002-001
    """
    config = load_pipeline_config(Path("config/default.yaml"))
    assert config.countries == DEFAULT_COUNTRIES
    assert config.short_days == 7
    assert config.recent_days == 30
    assert config.baseline_days == 356
    assert config.scoring.stage_low_max == 30.0
    assert config.scoring.stage_elevated_max == 56.0
    assert config.scoring.stage_high_max == 80.0
    assert config.scoring.trend_delta_epsilon == 1.25
    assert config.historical.horizon_days == 356
    assert config.historical.window_days == 7
    assert config.historical.min_valid_days == 5
    assert config.historical.aggregation == "rolling_mean"
    assert config.historical.countries == DEFAULT_COUNTRIES
    assert config.historical.compact_daily_report is False
    assert config.v3_1.enabled is True
    assert config.v3_1.fao_ffpi.normalization_method == "z_score"
    assert config.v3_1.fao_fpma.normalization_method == "percentile"
    assert config.v3_1.un_comtrade.normalization_method == "baseline_deviation"
    assert config.v3_1.gdacs.normalization_method == "z_score"
    assert config.v3_1.unhcr.normalization_method == "z_score"
    assert config.v3_1.narrative_input.normalization_method == "z_score"
    assert config.v3_1.governance_input.normalization_method == "z_score"
    assert config.v3_1.gdelt_event.normalization_method == "z_score"
    assert config.v3_1.unhcr.normalization_scope == "global"
    assert config.v3_1.narrative_input.normalization_scope == "global"
    assert config.v3_1.governance_input.normalization_scope == "global"
    assert config.v3_1.gdelt_event.normalization_scope == "global"
    assert config.v3_1.fusion.target_period_days == 356
    assert config.v3_1.fusion.historical.target_periodicity == "monthly"
    assert config.v3_1.fusion.historical.horizon_months == 12
    assert config.v3_1.fusion.source_to_group["fao_ffpi"] == "market_food"
    assert config.v3_1.fusion.source_to_group["gdacs"] == "shock"
    assert config.v3_1.fusion.source_to_group["governance_input"] == "governance"
    assert config.v3_1.fusion.source_to_group["gdelt_event"] == "event"
    assert config.v3_1.fusion.group_weights["governance"] == 0.15
    assert config.v3_1.fusion.group_weights["structural"] == 0.1
    assert config.v3_1.fusion.bonus_enabled is False
    assert config.v3_1.fusion.calibration.stage_low_max == 34.0
    assert config.v3_1.fusion.calibration.stage_elevated_max == 60.0
    assert config.v3_1.fusion.calibration.stage_high_max == 82.0
    assert config.v3_1.fusion.calibration.trend_delta_epsilon == 2.0
    assert config.v3_1.fusion.calibration.event_fresh_boost_factor >= 1.0
    assert "default" in config.v3_1.fusion.calibration.freshness_model
    assert (
        config.v3_1.fusion.calibration.freshness_min_fresh_contribution_share > 0.0
    )
    assert (
        config.v3_1.fusion.calibration.freshness_max_stale_contribution_share > 0.0
    )
    assert config.v3_1.fusion.calibration.responsiveness_delta_threshold > 0.0
    assert config.v3_1.fusion.calibration.peak_prominence_min >= 0.0
    assert config.v3_1.fusion.calibration.peak_min_rise >= 0.0
    assert config.v3_1.fusion.calibration.peak_min_fall >= 0.0
    assert config.v3_1.fusion.calibration.peak_min_separation_periods >= 0
    assert config.v3_1.fusion.calibration.peak_quality_floor >= 0.0
    assert 0.0 <= config.v3_1.fusion.calibration.peak_support_group_min_share <= 1.0
    assert 0.0 <= config.v3_1.fusion.calibration.peak_country_specific_share_threshold <= 1.0
    assert 0.0 <= config.v3_1.fusion.calibration.peak_global_share_warning_threshold <= 1.0
    assert 0.0 <= config.v3_1.fusion.calibration.peak_model_driven_global_share_threshold <= 1.0
    assert (
        config.v3_1.fusion.calibration.peak_model_driven_global_share_threshold
        >= config.v3_1.fusion.calibration.peak_global_share_warning_threshold
    )
    assert 0.0 <= config.v3_1.fusion.calibration.peak_single_group_dominance_threshold <= 1.0
    assert 0.0 <= config.v3_1.fusion.calibration.peak_event_support_weak_threshold <= 1.0
    assert 0.0 <= config.v3_1.fusion.calibration.peak_event_support_strong_threshold <= 1.0
    assert (
        config.v3_1.fusion.calibration.peak_event_support_strong_threshold
        >= config.v3_1.fusion.calibration.peak_event_support_weak_threshold
    )
    assert config.v3_1.fusion.calibration.event_alignment_temporal_distance_days > 0
    assert (
        0.0
        <= config.v3_1.fusion.calibration.event_alignment_weak_match_threshold
        <= config.v3_1.fusion.calibration.event_alignment_context_match_threshold
        <= config.v3_1.fusion.calibration.event_alignment_direct_match_threshold
        <= 1.0
    )
    assert config.v3_1.fusion.calibration.event_alignment_multi_overlap_min_events >= 2
    assert (
        config.v3_1.fusion.calibration.event_registry_path.as_posix()
        == "data/validation/event_registry.csv"
    )
    assert (
        config.v3_1.fusion.calibration.event_marker_registry_path.as_posix()
        == "data/validation/event_marker_registry.csv"
    )
    assert config.v3_1.fusion.calibration.expected_ranking == DEFAULT_EXPECTED_RANKING
    assert (
        config.v3_1.fusion.calibration.reference_episodes_path.as_posix()
        == "data/validation/reference_episodes.csv"
    )


def test_load_pipeline_config_normalizes_deutschland(tmp_path: Path):
    """
    Traceability:
    - PSwR-002
    - PSyR-001
    - PM-006
    - TV-PSwR-002-002
    """
    config_path = tmp_path / "config.yaml"
    countries_with_alias = [value if value != "Germany" else "Deutschland" for value in DEFAULT_COUNTRIES]
    config_path.write_text(
        _base_config_text(countries=countries_with_alias),
        encoding="utf-8",
    )

    config = load_pipeline_config(config_path)
    assert config.countries == DEFAULT_COUNTRIES


def test_load_pipeline_config_rejects_missing_sections(tmp_path: Path):
    """
    Traceability:
    - PSwR-002
    - PM-006
    - TV-PSwR-002-003
    """
    config_path = tmp_path / "invalid_missing.yaml"
    config_path.write_text("countries:\n  - Iran\n", encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_windows(tmp_path: Path):
    """
    Traceability:
    - PSwR-002
    - PSyR-002
    - PM-006
    - TV-PSwR-002-004
    """
    config_path = tmp_path / "invalid_windows.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "  short_days: 7",
        "  short_days: 6",
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_unknown_country(tmp_path: Path):
    """
    Traceability:
    - PSwR-002
    - PSyR-001
    - PM-006
    - TV-PSwR-002-005
    """
    invalid_countries = DEFAULT_COUNTRIES[:-1] + ["France"]
    config_path = tmp_path / "invalid_country.yaml"
    config_path.write_text(
        _base_config_text(countries=invalid_countries),
        encoding="utf-8",
    )

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_scoring_threshold_order(tmp_path: Path):
    """
    Traceability:
    - PSwR-012
    - ALG-005
    - TV-PSwR-012-002
    """
    config_path = tmp_path / "invalid_scoring_stage.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "    elevated_max: 56",
        "    elevated_max: 20",
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_trend_epsilon(tmp_path: Path):
    """
    Traceability:
    - PSwR-013
    - ALG-006
    - TV-PSwR-013-002
    """
    config_path = tmp_path / "invalid_scoring_trend.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "    delta_epsilon: 1.25",
        "    delta_epsilon: 0.0",
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_historical_min_coverage(tmp_path: Path):
    """
    Traceability:
    - PSwR-026
    - PM-012
    - TV-PSwR-026-001
    """
    config_path = tmp_path / "invalid_historical_min_coverage.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "  min_valid_days: 5",
        "  min_valid_days: 8",
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_historical_aggregation(tmp_path: Path):
    """
    Traceability:
    - PSwR-021
    - ALG-009
    - TV-PSwR-021-001
    """
    config_path = tmp_path / "invalid_historical_aggregation.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "  aggregation: rolling_mean",
        "  aggregation: rolling_median",
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_historical_country_outside_scope(tmp_path: Path):
    """
    Traceability:
    - PSwR-035
    - PSyR-001
    - TV-PSwR-035-001
    """
    config_path = tmp_path / "invalid_historical_country.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "    - Nigeria",
        "    - France",
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_accepts_compact_daily_report_flag(tmp_path: Path):
    """
    Traceability:
    - PSwR-031
    - PSyR-015
    - TV-PSwR-031-001
    """
    config_path = tmp_path / "historical_compact_daily_report.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "  compact_daily_report: false",
        "  compact_daily_report: true",
    )
    config_path.write_text(text, encoding="utf-8")

    config = load_pipeline_config(config_path)
    assert config.historical.compact_daily_report is True


def test_load_pipeline_config_rejects_invalid_v31_normalization_method(tmp_path: Path):
    """
    Traceability:
    - PSwR-040
    - PM-018
    - TV-PSwR-040-001
    """
    config_path = tmp_path / "invalid_v31_normalization_method.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "        method: z_score",
        "        method: unknown_method",
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_v31_historical_periodicity(tmp_path: Path):
    """
    Traceability:
    - PSwR-054
    - PSwR-056
    - PM-024
    - TV-PSwR-054-001
    """
    config_path = tmp_path / "invalid_v31_historical_periodicity.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "      target_periodicity: monthly",
        "      target_periodicity: daily",
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_v31_normalization_scope(tmp_path: Path):
    """
    Traceability:
    - PSwR-040
    - PM-018
    - TV-PSwR-040-003
    """
    config_path = tmp_path / "invalid_v31_normalization_scope.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES).replace(
        "        scope: global",
        "        scope: invalid",
        1,
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_v31_calibration_expected_ranking(tmp_path: Path):
    """
    Traceability:
    - PSwR-078
    - PM-038
    - TV-PSwR-078-001
    """
    config_path = tmp_path / "invalid_v31_calibration_expected_ranking.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES) + "\n".join(
        [
            "",
            "    calibration:",
            "      expected_ranking:",
            "        - Germany",
            "        - Iran",
            "        - Nigeria",
        ]
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_v31_event_decay_factor(tmp_path: Path):
    """
    Traceability:
    - PSwR-079
    - PM-039
    - TV-PSwR-079-001
    """
    config_path = tmp_path / "invalid_v31_event_decay_factor.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES) + "\n".join(
        [
            "",
            "    calibration:",
            "      event_min_decay_factor: 1.5",
        ]
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_v31_peak_event_support_threshold_order(tmp_path: Path):
    """
    Traceability:
    - PSwR-106
    - PM-060
    - TV-PSwR-106-001
    """
    config_path = tmp_path / "invalid_v31_peak_event_support_threshold_order.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES) + "\n".join(
        [
            "",
            "    calibration:",
            "      peak_event_support_weak_threshold: 0.7",
            "      peak_event_support_strong_threshold: 0.5",
        ]
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_v31_freshness_model(tmp_path: Path):
    """
    Traceability:
    - PSwR-083
    - PSwR-088
    - PM-042
    - TV-PSwR-083-002
    """
    config_path = tmp_path / "invalid_v31_freshness_model.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES) + "\n".join(
        [
            "",
            "    calibration:",
            "      freshness_model:",
            "        default:",
            "          fresh_max_days: 30",
            "          stale_max_days: 30",
            "          aging_floor_factor: 0.8",
            "          stale_half_life_days: 60",
            "          minimum_decay_factor: 0.4",
        ]
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_v432_event_alignment_threshold_order(tmp_path: Path):
    """
    Traceability:
    - PSwR-122
    - PM-066
    - TV-PSwR-122-001
    """
    config_path = tmp_path / "invalid_v432_event_alignment_threshold_order.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES) + "\n".join(
        [
            "",
            "    calibration:",
            "      event_alignment_direct_match_threshold: 0.5",
            "      event_alignment_context_match_threshold: 0.6",
            "      event_alignment_weak_match_threshold: 0.4",
        ]
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)


def test_load_pipeline_config_rejects_invalid_v432_event_alignment_multi_overlap_min_events(tmp_path: Path):
    """
    Traceability:
    - PSwR-122
    - PM-066
    - TV-PSwR-122-002
    """
    config_path = tmp_path / "invalid_v432_event_alignment_multi_overlap_min_events.yaml"
    text = _base_config_text(countries=DEFAULT_COUNTRIES) + "\n".join(
        [
            "",
            "    calibration:",
            "      event_alignment_multi_overlap_min_events: 1",
        ]
    )
    config_path.write_text(text, encoding="utf-8")

    with pytest.raises(ConfigValidationError):
        load_pipeline_config(config_path)
