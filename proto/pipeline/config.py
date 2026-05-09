from __future__ import annotations

"""
Pipeline configuration loader.

Traceability:
- PSwR-002
- PSyR-001
- PSyR-002
- PSyR-032
- PSyR-033
- PSyR-013
- PSyR-014
- PSyR-015
- PSyR-018
- PSyR-019
- PSyR-020
- PSyR-021
- PSyR-022
- PSyR-034
- PSwR-021
- PSwR-026
- PSwR-031
- PSwR-035
- PSwR-036
- PSwR-039
- PSwR-040
- PSwR-041
- PSwR-042
- PSwR-043
- PSwR-045
- PSwR-048
- PSwR-049
- PSwR-050
- PSwR-054
- PSwR-056
- PSwR-057
- PSwR-059
- PSwR-060
- PSwR-061
- PSwR-091
- PSwR-092
- PSwR-071
- PSwR-072
- PSwR-073
- PSwR-078
- PSwR-079
- PSwR-083
- PSwR-084
- PSwR-087
- PSwR-088
- PSwR-089
- PM-006
- PM-009
- PM-014
- PM-016
- PM-018
- PM-019
- PM-020
- PM-021
- PM-022
- PM-024
- PM-026
- PM-049
- PM-050
- PM-032
- PM-033
- PM-038
- PM-039
- PM-042
- PM-043
- PM-044
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

from proto.common import canonical_country
from proto.fusion.freshness import copy_default_freshness_model
from proto.observations.normalization import SUPPORTED_NORMALIZATION_METHODS

REQUIRED_COUNTRIES = (
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
)
REQUIRED_WINDOWS = {
    "short_days": 7,
    "recent_days": 30,
    "baseline_days": 356,
}
V31_REQUIRED_GROUPS = (
    "event",
    "narrative",
    "governance",
    "market_food",
    "shock",
    "displacement",
    "structural",
)
V31_REQUIRED_SOURCES = (
    "fao_ffpi",
    "fao_fpma",
    "un_comtrade",
    "gdacs",
    "unhcr",
    "narrative_input",
    "governance_input",
    "gdelt_event",
)


class ConfigValidationError(ValueError):
    """
    Raised for invalid V1/V2 configuration.

    Traceability:
    - PSwR-002
    - PM-006
    """


@dataclass(frozen=True)
class ScoringConfig:
    """
    Calibrated scoring parameters.

    Traceability:
    - PSwR-012
    - PSwR-013
    - ALG-005
    - ALG-006
    """

    stage_low_max: float
    stage_elevated_max: float
    stage_high_max: float
    trend_delta_epsilon: float


@dataclass(frozen=True)
class HistoricalConfig:
    """
    Historical Rolling Trend configuration.

    Traceability:
    - PSyR-013
    - PSyR-014
    - PSyR-015
    - PSwR-021
    - PSwR-026
    - PSwR-031
    - PSwR-035
    - PM-009
    - PM-014
    """

    horizon_days: int
    window_days: int
    min_valid_days: int
    aggregation: str
    countries: list[str]
    compact_daily_report: bool


@dataclass(frozen=True)
class V31SourceConfig:
    """
    V3.1 source adapter configuration.

    Traceability:
    - PSyR-021
    - PSwR-039
    - PSwR-040
    - PSwR-048
    - PSwR-049
    - PSwR-050
    - PM-016
    - PM-018
    """

    path: Path
    normalization_method: str
    normalization_scope: str
    normalization_baseline_value: float | None
    normalization_baseline_scale: float | None


@dataclass(frozen=True)
class V31FusionConfidenceConfig:
    """
    Fusion-confidence configuration.

    Traceability:
    - PSwR-045
    - PM-021
    """

    max_age_days: int
    coverage_weight: float
    recency_weight: float
    completeness_weight: float
    consistency_weight: float


@dataclass(frozen=True)
class V31FusionHistoricalConfig:
    """
    Historical fusion configuration (V3.2 expansion on V3.1 block).

    Traceability:
    - PSyR-023
    - PSwR-056
    - PSwR-057
    - PM-024
    """

    enabled: bool
    target_periodicity: str
    horizon_months: int


@dataclass(frozen=True)
class V31FusionCalibrationConfig:
    """
    V4.x calibration profile for fusion validation and diagnostics.

    Traceability:
    - PSwR-078
    - PSwR-079
    - PM-038
    - PM-039
    """

    stage_low_max: float
    stage_elevated_max: float
    stage_high_max: float
    trend_delta_epsilon: float
    group_activation_threshold: float
    dominance_share_threshold: float
    market_food_dominance_threshold: float
    structural_outlier_gap: float
    event_stale_after_days: int
    event_decay_half_life_days: int
    event_min_decay_factor: float
    event_fresh_boost_factor: float
    event_stale_warning_days: int
    limited_coverage_threshold: float
    reduced_coverage_threshold: float
    freshness_model: dict[str, dict[str, float]]
    freshness_min_fresh_contribution_share: float
    freshness_max_stale_contribution_share: float
    dynamic_layer_readiness_min_share: float
    responsiveness_delta_threshold: float
    responsiveness_lag_tolerance_months: int
    peak_prominence_min: float
    peak_min_rise: float
    peak_min_fall: float
    peak_min_separation_periods: int
    peak_quality_floor: float
    peak_support_group_min_share: float
    peak_country_specific_share_threshold: float
    peak_global_share_warning_threshold: float
    peak_model_driven_global_share_threshold: float
    peak_single_group_dominance_threshold: float
    peak_event_support_weak_threshold: float
    peak_event_support_strong_threshold: float
    event_alignment_temporal_distance_days: int
    event_alignment_direct_match_threshold: float
    event_alignment_context_match_threshold: float
    event_alignment_weak_match_threshold: float
    event_alignment_multi_overlap_min_events: int
    event_registry_path: Path
    event_marker_registry_path: Path
    expected_ranking: list[str]
    reference_episodes_path: Path


@dataclass(frozen=True)
class V31FusionConfig:
    """
    V3.1 fusion-scoring configuration.

    Traceability:
    - PSyR-019
    - PSyR-020
    - PSwR-041
    - PSwR-042
    - PSwR-043
    - PSwR-045
    - PM-019
    - PM-020
    - PM-021
    - PM-022
    """

    target_period_days: int
    groups: list[str]
    source_to_group: dict[str, str]
    source_weights: dict[str, dict[str, float]]
    group_weights: dict[str, float]
    bonus_enabled: bool
    bonus_threshold: float
    bonus_points: float
    bonus_min_groups: int
    confidence: V31FusionConfidenceConfig
    historical: V31FusionHistoricalConfig
    calibration: V31FusionCalibrationConfig


@dataclass(frozen=True)
class V31Config:
    """
    Canonical V3.1 extension block.

    Traceability:
    - PSR-012
    - PSR-013
    - PSyR-018
    - PSyR-019
    - PSyR-020
    """

    enabled: bool
    fao_ffpi: V31SourceConfig
    fao_fpma: V31SourceConfig
    un_comtrade: V31SourceConfig
    gdacs: V31SourceConfig
    unhcr: V31SourceConfig
    narrative_input: V31SourceConfig
    governance_input: V31SourceConfig
    gdelt_event: V31SourceConfig
    fusion: V31FusionConfig

    def source_config_by_id(self) -> dict[str, V31SourceConfig]:
        """
        Convenience map for source adapters.

        Traceability:
        - PSwR-039
        """
        return {
            "fao_ffpi": self.fao_ffpi,
            "fao_fpma": self.fao_fpma,
            "un_comtrade": self.un_comtrade,
            "gdacs": self.gdacs,
            "unhcr": self.unhcr,
            "narrative_input": self.narrative_input,
            "governance_input": self.governance_input,
            "gdelt_event": self.gdelt_event,
        }


@dataclass(frozen=True)
class PipelineConfig:
    """
    Canonical configuration object for the V1/V2 standard mode.

    Traceability:
    - PSwR-002
    - PSyR-001
    - PSyR-002
    """

    countries: list[str]
    short_days: int
    recent_days: int
    baseline_days: int
    query_version: str
    scoring_version: str
    bridge_file_version: str
    context_table_version: str
    report_dir: Path
    reference_dir: Path
    gdelt_path: Path
    ucdp_path: Path
    bridge_path: Path
    context_path: Path
    scoring: ScoringConfig
    historical: HistoricalConfig
    v3_1: V31Config


def _require_mapping(raw: object, *, section: str) -> dict:
    # Traceability:
    # - PSwR-002
    # - PSyR-001
    # - PSyR-002
    # - PSyR-032
    # - PSyR-033
    # - PSyR-013
    if not isinstance(raw, dict):
        raise ConfigValidationError(f"configuration section {section!r} must be a mapping")
    return raw


def _require_keys(raw: dict, *, section: str, keys: list[str]) -> None:
    # Traceability:
    # - PSwR-002
    # - PSyR-001
    # - PSyR-002
    # - PSyR-032
    # - PSyR-033
    # - PSyR-013
    missing = [key for key in keys if key not in raw]
    if missing:
        raise ConfigValidationError(
            f"configuration section {section!r} is missing keys: {', '.join(missing)}"
        )


def _validate_countries(raw_countries: object) -> list[str]:
    """
    Validate and canonicalize configured countries.

    Traceability:
    - PSyR-001
    - OI-001
    """
    if not isinstance(raw_countries, list):
        raise ConfigValidationError("configuration key 'countries' must be a list")
    canonicalized = [canonical_country(str(item)) for item in raw_countries]
    if len(set(canonicalized)) != len(canonicalized):
        raise ConfigValidationError("configuration key 'countries' contains duplicates after normalization")
    if tuple(canonicalized) != REQUIRED_COUNTRIES:
        raise ConfigValidationError(
            "configuration key 'countries' must equal "
            + ", ".join(REQUIRED_COUNTRIES)
        )
    return canonicalized


def _validate_windows(raw_windows: object) -> dict[str, int]:
    """
    Validate exact analysis windows.

    Traceability:
    - PSyR-002
    - PM-006
    """
    windows = _require_mapping(raw_windows, section="windows")
    _require_keys(windows, section="windows", keys=list(REQUIRED_WINDOWS.keys()))
    parsed: dict[str, int] = {}
    for key, expected_value in REQUIRED_WINDOWS.items():
        try:
            parsed[key] = int(windows[key])
        except (TypeError, ValueError) as exc:
            raise ConfigValidationError(f"configuration key 'windows.{key}' must be an integer") from exc
        if parsed[key] <= 0:
            raise ConfigValidationError(f"configuration key 'windows.{key}' must be > 0")
        if parsed[key] != expected_value:
            raise ConfigValidationError(
                f"configuration key 'windows.{key}' must be {expected_value} in V1/V2 standard mode"
            )
    return parsed


def _validate_versions(raw_versions: object) -> dict[str, str]:
    # Traceability:
    # - PSwR-002
    # - PSyR-001
    # - PSyR-002
    # - PSyR-032
    # - PSyR-033
    # - PSyR-013
    versions = _require_mapping(raw_versions, section="versions")
    required = [
        "query_version",
        "scoring_version",
        "bridge_file_version",
        "context_table_version",
    ]
    _require_keys(versions, section="versions", keys=required)
    parsed: dict[str, str] = {}
    for key in required:
        value = str(versions[key]).strip()
        if not value:
            raise ConfigValidationError(f"configuration key 'versions.{key}' must be non-empty")
        parsed[key] = value
    return parsed


def _validate_output(raw_output: object) -> dict[str, Path]:
    # Traceability:
    # - PSwR-002
    # - PSyR-001
    # - PSyR-002
    # - PSyR-032
    # - PSyR-033
    # - PSyR-013
    output = _require_mapping(raw_output, section="output")
    required = ["report_dir", "reference_dir"]
    _require_keys(output, section="output", keys=required)
    parsed: dict[str, Path] = {}
    for key in required:
        value = str(output[key]).strip()
        if not value:
            raise ConfigValidationError(f"configuration key 'output.{key}' must be non-empty")
        parsed[key] = Path(value)
    return parsed


def _validate_scoring(raw_scoring: object) -> ScoringConfig:
    """
    Validate calibrated scoring configuration.

    Traceability:
    - PSwR-012
    - PSwR-013
    - ALG-005
    - ALG-006
    """
    scoring = _require_mapping(raw_scoring, section="scoring")
    stage = _require_mapping(scoring.get("stage"), section="scoring.stage")
    trend = _require_mapping(scoring.get("trend"), section="scoring.trend")

    _require_keys(
        stage,
        section="scoring.stage",
        keys=["low_max", "elevated_max", "high_max"],
    )
    _require_keys(
        trend,
        section="scoring.trend",
        keys=["delta_epsilon"],
    )

    try:
        low_max = float(stage["low_max"])
        elevated_max = float(stage["elevated_max"])
        high_max = float(stage["high_max"])
        delta_epsilon = float(trend["delta_epsilon"])
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError("scoring calibration values must be numeric") from exc

    if not (0.0 < low_max < elevated_max < high_max < 100.0):
        raise ConfigValidationError(
            "scoring.stage thresholds must satisfy 0 < low_max < elevated_max < high_max < 100"
        )
    if not (0.1 <= delta_epsilon <= 20.0):
        raise ConfigValidationError("scoring.trend.delta_epsilon must be in range [0.1, 20.0]")

    return ScoringConfig(
        stage_low_max=low_max,
        stage_elevated_max=elevated_max,
        stage_high_max=high_max,
        trend_delta_epsilon=delta_epsilon,
    )


def _validate_historical(
    raw_historical: object,
    *,
    configured_countries: list[str],
) -> HistoricalConfig:
    """
    Validate historical rolling-trend configuration.

    Traceability:
    - PSyR-013
    - PSyR-014
    - PSyR-015
    - PSwR-021
    - PSwR-026
    - PSwR-031
    - PSwR-035
    - PM-009
    - PM-014
    """
    historical = _require_mapping(raw_historical, section="historical")
    _require_keys(
        historical,
        section="historical",
        keys=[
            "horizon_days",
            "window_days",
            "min_valid_days",
            "aggregation",
            "countries",
            "compact_daily_report",
        ],
    )
    try:
        horizon_days = int(historical["horizon_days"])
        window_days = int(historical["window_days"])
        min_valid_days = int(historical["min_valid_days"])
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError(
            "historical.horizon_days, historical.window_days and historical.min_valid_days must be integers"
        ) from exc
    if horizon_days <= 0:
        raise ConfigValidationError("historical.horizon_days must be > 0")
    if window_days <= 0:
        raise ConfigValidationError("historical.window_days must be > 0")
    if min_valid_days <= 0:
        raise ConfigValidationError("historical.min_valid_days must be > 0")
    if min_valid_days > window_days:
        raise ConfigValidationError("historical.min_valid_days must be <= historical.window_days")

    aggregation = str(historical["aggregation"]).strip()
    if aggregation != "rolling_mean":
        raise ConfigValidationError("historical.aggregation must be 'rolling_mean' in standard mode")

    if not isinstance(historical["countries"], list) or not historical["countries"]:
        raise ConfigValidationError("historical.countries must be a non-empty list")
    historical_countries = [canonical_country(str(item)) for item in historical["countries"]]
    if len(set(historical_countries)) != len(historical_countries):
        raise ConfigValidationError("historical.countries contains duplicates after normalization")
    configured_set = set(configured_countries)
    for country in historical_countries:
        if country not in configured_set:
            raise ConfigValidationError(
                "historical.countries must be a subset of configured countries"
            )

    compact_daily_report = bool(historical["compact_daily_report"])
    return HistoricalConfig(
        horizon_days=horizon_days,
        window_days=window_days,
        min_valid_days=min_valid_days,
        aggregation=aggregation,
        countries=historical_countries,
        compact_daily_report=compact_daily_report,
    )


def _validate_v31_source_config(
    raw: object,
    *,
    source_id: str,
) -> V31SourceConfig:
    # Traceability:
    # - PSwR-002
    # - PSyR-001
    # - PSyR-002
    # - PSyR-032
    # - PSyR-033
    # - PSyR-013
    source = _require_mapping(raw, section=f"v3_1.sources.{source_id}")
    _require_keys(source, section=f"v3_1.sources.{source_id}", keys=["path", "normalization"])
    path_value = str(source["path"]).strip()
    if not path_value:
        raise ConfigValidationError(f"v3_1.sources.{source_id}.path must be non-empty")

    normalization = _require_mapping(
        source["normalization"],
        section=f"v3_1.sources.{source_id}.normalization",
    )
    _require_keys(
        normalization,
        section=f"v3_1.sources.{source_id}.normalization",
        keys=["method"],
    )
    method = str(normalization["method"]).strip().lower()
    if method not in SUPPORTED_NORMALIZATION_METHODS:
        raise ConfigValidationError(
            f"v3_1.sources.{source_id}.normalization.method must be one of "
            f"{sorted(SUPPORTED_NORMALIZATION_METHODS)}"
        )

    baseline_value = normalization.get("baseline_value")
    baseline_scale = normalization.get("baseline_scale")
    normalization_scope = str(normalization.get("scope", "per_country")).strip().lower()
    if normalization_scope not in {"per_country", "global"}:
        raise ConfigValidationError(
            f"v3_1.sources.{source_id}.normalization.scope must be 'per_country' or 'global'"
        )
    parsed_baseline_value: float | None = None
    parsed_baseline_scale: float | None = None
    if baseline_value is not None:
        try:
            parsed_baseline_value = float(baseline_value)
        except (TypeError, ValueError) as exc:
            raise ConfigValidationError(
                f"v3_1.sources.{source_id}.normalization.baseline_value must be numeric"
            ) from exc
    if baseline_scale is not None:
        try:
            parsed_baseline_scale = float(baseline_scale)
        except (TypeError, ValueError) as exc:
            raise ConfigValidationError(
                f"v3_1.sources.{source_id}.normalization.baseline_scale must be numeric"
            ) from exc

    return V31SourceConfig(
        path=Path(path_value),
        normalization_method=method,
        normalization_scope=normalization_scope,
        normalization_baseline_value=parsed_baseline_value,
        normalization_baseline_scale=parsed_baseline_scale,
    )


def _validate_freshness_rule(
    raw_rule: object,
    *,
    section: str,
) -> dict[str, float]:
    # Traceability:
    # - PSwR-002
    # - PSyR-001
    # - PSyR-002
    # - PSyR-032
    # - PSyR-033
    # - PSyR-013
    rule = _require_mapping(raw_rule, section=section)
    _require_keys(
        rule,
        section=section,
        keys=[
            "fresh_max_days",
            "stale_max_days",
            "aging_floor_factor",
            "stale_half_life_days",
            "minimum_decay_factor",
        ],
    )
    try:
        fresh_max_days = int(rule["fresh_max_days"])
        stale_max_days = int(rule["stale_max_days"])
        aging_floor_factor = float(rule["aging_floor_factor"])
        stale_half_life_days = int(rule["stale_half_life_days"])
        minimum_decay_factor = float(rule["minimum_decay_factor"])
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError(f"{section} contains invalid numeric fields") from exc

    if fresh_max_days < 0:
        raise ConfigValidationError(f"{section}.fresh_max_days must be >= 0")
    if stale_max_days <= fresh_max_days:
        raise ConfigValidationError(
            f"{section}.stale_max_days must be > {section}.fresh_max_days"
        )
    if stale_half_life_days <= 0:
        raise ConfigValidationError(f"{section}.stale_half_life_days must be > 0")
    if not (0.0 < minimum_decay_factor <= 1.0):
        raise ConfigValidationError(f"{section}.minimum_decay_factor must be in range (0, 1]")
    if not (minimum_decay_factor <= aging_floor_factor <= 1.0):
        raise ConfigValidationError(
            f"{section}.aging_floor_factor must be in range [minimum_decay_factor, 1]"
        )

    return {
        "fresh_max_days": float(fresh_max_days),
        "stale_max_days": float(stale_max_days),
        "aging_floor_factor": round(aging_floor_factor, 6),
        "stale_half_life_days": float(stale_half_life_days),
        "minimum_decay_factor": round(minimum_decay_factor, 6),
    }


def _validate_freshness_model(
    raw_model: object,
    *,
    groups: list[str],
) -> dict[str, dict[str, float]]:
    # Traceability:
    # - PSwR-002
    # - PSyR-001
    # - PSyR-002
    # - PSyR-032
    # - PSyR-033
    # - PSyR-013
    model = _require_mapping(raw_model, section="v3_1.fusion.calibration.freshness_model")
    if "default" not in model:
        raise ConfigValidationError("v3_1.fusion.calibration.freshness_model must include 'default'")

    allowed_keys = {"default", *groups}
    unknown_keys = sorted(set(model.keys()) - allowed_keys)
    if unknown_keys:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.freshness_model contains unknown groups: "
            + ", ".join(unknown_keys)
        )

    default_rule = _validate_freshness_rule(
        model["default"],
        section="v3_1.fusion.calibration.freshness_model.default",
    )
    normalized: dict[str, dict[str, float]] = {"default": default_rule}
    for group in groups:
        if group in model:
            normalized[group] = _validate_freshness_rule(
                model[group],
                section=f"v3_1.fusion.calibration.freshness_model.{group}",
            )
        else:
            normalized[group] = dict(default_rule)
    return normalized


def _validate_v31(
    raw_v31: object,
    *,
    configured_countries: list[str],
    scoring: ScoringConfig,
) -> V31Config:
    """
    Validate V3.1 multi-source extension configuration.

    Traceability:
    - PSyR-018
    - PSyR-019
    - PSyR-020
    - PSyR-021
    - PSyR-022
    - PSyR-032
    - PSyR-033
    - PSwR-039
    - PSwR-040
    - PSwR-041
    - PSwR-042
    - PSwR-043
    - PSwR-045
    - PSwR-083
    - PSwR-084
    - PSwR-087
    - PSwR-088
    - PSwR-089
    - PM-016
    - PM-018
    - PM-019
    - PM-020
    - PM-021
    - PM-022
    - PM-042
    - PM-043
    - PM-044
    """
    v31 = _require_mapping(raw_v31, section="v3_1")
    _require_keys(v31, section="v3_1", keys=["enabled", "sources", "fusion"])

    enabled = bool(v31["enabled"])

    sources = _require_mapping(v31["sources"], section="v3_1.sources")
    _require_keys(
        sources,
        section="v3_1.sources",
        keys=list(V31_REQUIRED_SOURCES),
    )
    ffpi = _validate_v31_source_config(sources["fao_ffpi"], source_id="fao_ffpi")
    fpma = _validate_v31_source_config(sources["fao_fpma"], source_id="fao_fpma")
    comtrade = _validate_v31_source_config(sources["un_comtrade"], source_id="un_comtrade")
    gdacs = _validate_v31_source_config(sources["gdacs"], source_id="gdacs")
    unhcr = _validate_v31_source_config(sources["unhcr"], source_id="unhcr")
    narrative_input = _validate_v31_source_config(
        sources["narrative_input"],
        source_id="narrative_input",
    )
    governance_input = _validate_v31_source_config(
        sources["governance_input"],
        source_id="governance_input",
    )
    gdelt_event = _validate_v31_source_config(
        sources["gdelt_event"],
        source_id="gdelt_event",
    )

    fusion = _require_mapping(v31["fusion"], section="v3_1.fusion")
    _require_keys(
        fusion,
        section="v3_1.fusion",
        keys=[
            "target_period_days",
            "groups",
            "source_to_group",
            "source_weights",
            "group_weights",
            "bonus",
            "confidence",
            "historical",
        ],
    )
    try:
        target_period_days = int(fusion["target_period_days"])
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError("v3_1.fusion.target_period_days must be an integer") from exc
    if target_period_days <= 0:
        raise ConfigValidationError("v3_1.fusion.target_period_days must be > 0")

    groups_raw = fusion["groups"]
    if not isinstance(groups_raw, list) or not groups_raw:
        raise ConfigValidationError("v3_1.fusion.groups must be a non-empty list")
    groups = [str(item).strip().lower() for item in groups_raw]
    if tuple(groups) != V31_REQUIRED_GROUPS:
        raise ConfigValidationError(
            "v3_1.fusion.groups must equal "
            + ", ".join(V31_REQUIRED_GROUPS)
        )

    source_to_group_raw = _require_mapping(fusion["source_to_group"], section="v3_1.fusion.source_to_group")
    source_to_group: dict[str, str] = {}
    for source_id in V31_REQUIRED_SOURCES:
        if source_id not in source_to_group_raw:
            raise ConfigValidationError(f"v3_1.fusion.source_to_group missing key {source_id!r}")
        group = str(source_to_group_raw[source_id]).strip().lower()
        if group not in groups:
            raise ConfigValidationError(
                f"v3_1.fusion.source_to_group[{source_id!r}] must reference one of configured groups"
            )
        source_to_group[source_id] = group

    source_weights_raw = _require_mapping(fusion["source_weights"], section="v3_1.fusion.source_weights")
    source_weights: dict[str, dict[str, float]] = {}
    for group, group_source_map_raw in source_weights_raw.items():
        normalized_group = str(group).strip().lower()
        group_source_map = _require_mapping(
            group_source_map_raw,
            section=f"v3_1.fusion.source_weights.{normalized_group}",
        )
        source_weights[normalized_group] = {}
        for source_id, raw_weight in group_source_map.items():
            try:
                weight = float(raw_weight)
            except (TypeError, ValueError) as exc:
                raise ConfigValidationError(
                    f"v3_1.fusion.source_weights.{normalized_group}.{source_id} must be numeric"
                ) from exc
            if weight <= 0:
                raise ConfigValidationError(
                    f"v3_1.fusion.source_weights.{normalized_group}.{source_id} must be > 0"
                )
            source_weights[normalized_group][str(source_id).strip().lower()] = weight

    group_weights_raw = _require_mapping(fusion["group_weights"], section="v3_1.fusion.group_weights")
    group_weights: dict[str, float] = {}
    for group in groups:
        if group not in group_weights_raw:
            raise ConfigValidationError(f"v3_1.fusion.group_weights missing key {group!r}")
        try:
            weight = float(group_weights_raw[group])
        except (TypeError, ValueError) as exc:
            raise ConfigValidationError(f"v3_1.fusion.group_weights.{group} must be numeric") from exc
        if weight <= 0:
            raise ConfigValidationError(f"v3_1.fusion.group_weights.{group} must be > 0")
        group_weights[group] = weight

    bonus = _require_mapping(fusion["bonus"], section="v3_1.fusion.bonus")
    _require_keys(
        bonus,
        section="v3_1.fusion.bonus",
        keys=["enabled", "threshold", "points", "min_groups"],
    )
    bonus_enabled = bool(bonus["enabled"])
    try:
        bonus_threshold = float(bonus["threshold"])
        bonus_points = float(bonus["points"])
        bonus_min_groups = int(bonus["min_groups"])
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError("v3_1.fusion.bonus fields must be numeric/bool") from exc
    if not (0.0 <= bonus_threshold <= 100.0):
        raise ConfigValidationError("v3_1.fusion.bonus.threshold must be in range [0, 100]")
    if bonus_points < 0:
        raise ConfigValidationError("v3_1.fusion.bonus.points must be >= 0")
    if bonus_min_groups <= 0:
        raise ConfigValidationError("v3_1.fusion.bonus.min_groups must be > 0")

    confidence = _require_mapping(fusion["confidence"], section="v3_1.fusion.confidence")
    _require_keys(
        confidence,
        section="v3_1.fusion.confidence",
        keys=[
            "max_age_days",
            "coverage_weight",
            "recency_weight",
            "completeness_weight",
            "consistency_weight",
        ],
    )
    try:
        max_age_days = int(confidence["max_age_days"])
        coverage_weight = float(confidence["coverage_weight"])
        recency_weight = float(confidence["recency_weight"])
        completeness_weight = float(confidence["completeness_weight"])
        consistency_weight = float(confidence["consistency_weight"])
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError("v3_1.fusion.confidence fields must be numeric") from exc
    if max_age_days <= 0:
        raise ConfigValidationError("v3_1.fusion.confidence.max_age_days must be > 0")
    if (
        coverage_weight <= 0
        or recency_weight <= 0
        or completeness_weight <= 0
        or consistency_weight <= 0
    ):
        raise ConfigValidationError("v3_1.fusion.confidence weights must be > 0")

    historical = _require_mapping(fusion["historical"], section="v3_1.fusion.historical")
    _require_keys(
        historical,
        section="v3_1.fusion.historical",
        keys=["enabled", "target_periodicity", "horizon_months"],
    )
    historical_enabled = bool(historical["enabled"])
    target_periodicity = str(historical["target_periodicity"]).strip().lower()
    if target_periodicity != "monthly":
        raise ConfigValidationError("v3_1.fusion.historical.target_periodicity must be 'monthly'")
    try:
        horizon_months = int(historical["horizon_months"])
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError("v3_1.fusion.historical.horizon_months must be an integer") from exc
    if horizon_months <= 0:
        raise ConfigValidationError("v3_1.fusion.historical.horizon_months must be > 0")

    calibration_raw = fusion.get("calibration", {})
    if calibration_raw is None:
        calibration_raw = {}
    calibration = _require_mapping(calibration_raw, section="v3_1.fusion.calibration")
    raw_freshness_model = calibration.get("freshness_model", copy_default_freshness_model())
    if raw_freshness_model is None:
        raw_freshness_model = copy_default_freshness_model()
    freshness_model = _validate_freshness_model(raw_freshness_model, groups=groups)

    try:
        stage_low_max = float(calibration.get("stage_low_max", scoring.stage_low_max))
        stage_elevated_max = float(
            calibration.get("stage_elevated_max", scoring.stage_elevated_max)
        )
        stage_high_max = float(calibration.get("stage_high_max", scoring.stage_high_max))
        trend_delta_epsilon = float(
            calibration.get("trend_delta_epsilon", scoring.trend_delta_epsilon)
        )
        group_activation_threshold = float(calibration.get("group_activation_threshold", 55.0))
        dominance_share_threshold = float(calibration.get("dominance_share_threshold", 0.34))
        market_food_dominance_threshold = float(
            calibration.get("market_food_dominance_threshold", 0.34)
        )
        structural_outlier_gap = float(calibration.get("structural_outlier_gap", 30.0))
        event_stale_after_days = int(calibration.get("event_stale_after_days", 30))
        event_decay_half_life_days = int(calibration.get("event_decay_half_life_days", 45))
        event_min_decay_factor = float(calibration.get("event_min_decay_factor", 0.4))
        event_fresh_boost_factor = float(calibration.get("event_fresh_boost_factor", 1.08))
        event_stale_warning_days = int(calibration.get("event_stale_warning_days", 45))
        limited_coverage_threshold = float(calibration.get("limited_coverage_threshold", 0.5))
        reduced_coverage_threshold = float(calibration.get("reduced_coverage_threshold", 0.75))
        freshness_min_fresh_contribution_share = float(
            calibration.get("freshness_min_fresh_contribution_share", 0.35)
        )
        freshness_max_stale_contribution_share = float(
            calibration.get("freshness_max_stale_contribution_share", 0.5)
        )
        dynamic_layer_readiness_min_share = float(
            calibration.get("dynamic_layer_readiness_min_share", 0.5)
        )
        responsiveness_delta_threshold = float(
            calibration.get("responsiveness_delta_threshold", 2.0)
        )
        responsiveness_lag_tolerance_months = int(
            calibration.get("responsiveness_lag_tolerance_months", 1)
        )
        peak_prominence_min = float(calibration.get("peak_prominence_min", 1.0))
        peak_min_rise = float(calibration.get("peak_min_rise", 0.5))
        peak_min_fall = float(calibration.get("peak_min_fall", 0.5))
        peak_min_separation_periods = int(calibration.get("peak_min_separation_periods", 0))
        peak_quality_floor = float(calibration.get("peak_quality_floor", 1.0))
        peak_support_group_min_share = float(calibration.get("peak_support_group_min_share", 0.12))
        peak_country_specific_share_threshold = float(
            calibration.get("peak_country_specific_share_threshold", 0.4)
        )
        peak_global_share_warning_threshold = float(
            calibration.get("peak_global_share_warning_threshold", 0.55)
        )
        peak_model_driven_global_share_threshold = float(
            calibration.get("peak_model_driven_global_share_threshold", 0.7)
        )
        peak_single_group_dominance_threshold = float(
            calibration.get("peak_single_group_dominance_threshold", 0.58)
        )
        peak_event_support_weak_threshold = float(
            calibration.get("peak_event_support_weak_threshold", 0.45)
        )
        peak_event_support_strong_threshold = float(
            calibration.get("peak_event_support_strong_threshold", 0.7)
        )
        event_alignment_temporal_distance_days = int(
            calibration.get("event_alignment_temporal_distance_days", 75)
        )
        event_alignment_direct_match_threshold = float(
            calibration.get("event_alignment_direct_match_threshold", 0.72)
        )
        event_alignment_context_match_threshold = float(
            calibration.get("event_alignment_context_match_threshold", 0.56)
        )
        event_alignment_weak_match_threshold = float(
            calibration.get("event_alignment_weak_match_threshold", 0.4)
        )
        event_alignment_multi_overlap_min_events = int(
            calibration.get("event_alignment_multi_overlap_min_events", 2)
        )
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError("v3_1.fusion.calibration contains invalid numeric fields") from exc

    if not (0.0 <= stage_low_max < stage_elevated_max < stage_high_max <= 100.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration stage thresholds must satisfy "
            "0 <= low_max < elevated_max < high_max <= 100"
        )
    if trend_delta_epsilon <= 0:
        raise ConfigValidationError("v3_1.fusion.calibration.trend_delta_epsilon must be > 0")
    if not (0.0 < group_activation_threshold <= 100.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.group_activation_threshold must be in range (0, 100]"
        )
    if not (0.0 < dominance_share_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.dominance_share_threshold must be in range (0, 1]"
        )
    if not (0.0 < market_food_dominance_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.market_food_dominance_threshold must be in range (0, 1]"
        )
    if structural_outlier_gap < 0:
        raise ConfigValidationError("v3_1.fusion.calibration.structural_outlier_gap must be >= 0")
    if event_stale_after_days < 0:
        raise ConfigValidationError("v3_1.fusion.calibration.event_stale_after_days must be >= 0")
    if event_decay_half_life_days <= 0:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_decay_half_life_days must be > 0"
        )
    if not (0.0 < event_min_decay_factor <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_min_decay_factor must be in range (0, 1]"
        )
    if not (1.0 <= event_fresh_boost_factor <= 1.3):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_fresh_boost_factor must be in range [1.0, 1.3]"
        )
    if event_stale_warning_days <= 0:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_stale_warning_days must be > 0"
        )
    if event_stale_warning_days < event_stale_after_days:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_stale_warning_days must be >= event_stale_after_days"
        )
    if not (0.0 < limited_coverage_threshold < reduced_coverage_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration coverage thresholds must satisfy "
            "0 < limited_coverage_threshold < reduced_coverage_threshold <= 1"
        )
    if not (0.0 < freshness_min_fresh_contribution_share <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.freshness_min_fresh_contribution_share must be in range (0, 1]"
        )
    if not (0.0 < freshness_max_stale_contribution_share <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.freshness_max_stale_contribution_share must be in range (0, 1]"
        )
    if not (0.0 < dynamic_layer_readiness_min_share <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.dynamic_layer_readiness_min_share must be in range (0, 1]"
        )
    if responsiveness_delta_threshold <= 0:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.responsiveness_delta_threshold must be > 0"
        )
    if responsiveness_lag_tolerance_months < 0:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.responsiveness_lag_tolerance_months must be >= 0"
        )
    if peak_prominence_min < 0:
        raise ConfigValidationError("v3_1.fusion.calibration.peak_prominence_min must be >= 0")
    if peak_min_rise < 0:
        raise ConfigValidationError("v3_1.fusion.calibration.peak_min_rise must be >= 0")
    if peak_min_fall < 0:
        raise ConfigValidationError("v3_1.fusion.calibration.peak_min_fall must be >= 0")
    if peak_min_separation_periods < 0:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_min_separation_periods must be >= 0"
        )
    if peak_quality_floor < 0:
        raise ConfigValidationError("v3_1.fusion.calibration.peak_quality_floor must be >= 0")
    if not (0.0 <= peak_support_group_min_share <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_support_group_min_share must be in range [0, 1]"
        )
    if not (0.0 <= peak_country_specific_share_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_country_specific_share_threshold must be in range [0, 1]"
        )
    if not (0.0 <= peak_global_share_warning_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_global_share_warning_threshold must be in range [0, 1]"
        )
    if not (0.0 <= peak_model_driven_global_share_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_model_driven_global_share_threshold must be in range [0, 1]"
        )
    if peak_model_driven_global_share_threshold < peak_global_share_warning_threshold:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_model_driven_global_share_threshold must be >= peak_global_share_warning_threshold"
        )
    if not (0.0 <= peak_single_group_dominance_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_single_group_dominance_threshold must be in range [0, 1]"
        )
    if not (0.0 <= peak_event_support_weak_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_event_support_weak_threshold must be in range [0, 1]"
        )
    if not (0.0 <= peak_event_support_strong_threshold <= 1.0):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_event_support_strong_threshold must be in range [0, 1]"
        )
    if peak_event_support_strong_threshold < peak_event_support_weak_threshold:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.peak_event_support_strong_threshold must be >= peak_event_support_weak_threshold"
        )
    if event_alignment_temporal_distance_days <= 0:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_alignment_temporal_distance_days must be > 0"
        )
    if not (
        0.0 <= event_alignment_weak_match_threshold
        <= event_alignment_context_match_threshold
        <= event_alignment_direct_match_threshold
        <= 1.0
    ):
        raise ConfigValidationError(
            "v3_1.fusion.calibration event_alignment thresholds must satisfy "
            "0 <= weak <= context <= direct <= 1"
        )
    if event_alignment_multi_overlap_min_events < 2:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_alignment_multi_overlap_min_events must be >= 2"
        )

    expected_ranking_raw = calibration.get("expected_ranking", configured_countries)
    if not isinstance(expected_ranking_raw, list) or not expected_ranking_raw:
        raise ConfigValidationError("v3_1.fusion.calibration.expected_ranking must be a non-empty list")
    expected_ranking = [canonical_country(str(item)) for item in expected_ranking_raw]
    if len(set(expected_ranking)) != len(expected_ranking):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.expected_ranking contains duplicates after normalization"
        )
    if set(expected_ranking) != set(configured_countries):
        raise ConfigValidationError(
            "v3_1.fusion.calibration.expected_ranking must contain exactly configured countries"
        )

    reference_episodes_path_raw = str(
        calibration.get("reference_episodes_path", "data/validation/reference_episodes.csv")
    ).strip()
    if not reference_episodes_path_raw:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.reference_episodes_path must be non-empty"
        )
    event_registry_path_raw = str(
        calibration.get(
            "event_registry_path",
            calibration.get("event_marker_registry_path", "data/validation/event_registry.csv"),
        )
    ).strip()
    if not event_registry_path_raw:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_registry_path must be non-empty"
        )
    event_marker_registry_path_raw = str(
        calibration.get("event_marker_registry_path", event_registry_path_raw)
    ).strip()
    if not event_marker_registry_path_raw:
        raise ConfigValidationError(
            "v3_1.fusion.calibration.event_marker_registry_path must be non-empty"
        )

    return V31Config(
        enabled=enabled,
        fao_ffpi=ffpi,
        fao_fpma=fpma,
        un_comtrade=comtrade,
        gdacs=gdacs,
        unhcr=unhcr,
        narrative_input=narrative_input,
        governance_input=governance_input,
        gdelt_event=gdelt_event,
        fusion=V31FusionConfig(
            target_period_days=target_period_days,
            groups=groups,
            source_to_group=source_to_group,
            source_weights=source_weights,
            group_weights=group_weights,
            bonus_enabled=bonus_enabled,
            bonus_threshold=bonus_threshold,
            bonus_points=bonus_points,
            bonus_min_groups=bonus_min_groups,
            confidence=V31FusionConfidenceConfig(
                max_age_days=max_age_days,
                coverage_weight=coverage_weight,
                recency_weight=recency_weight,
                completeness_weight=completeness_weight,
                consistency_weight=consistency_weight,
            ),
            historical=V31FusionHistoricalConfig(
                enabled=historical_enabled,
                target_periodicity=target_periodicity,
                horizon_months=horizon_months,
            ),
            calibration=V31FusionCalibrationConfig(
                stage_low_max=stage_low_max,
                stage_elevated_max=stage_elevated_max,
                stage_high_max=stage_high_max,
                trend_delta_epsilon=trend_delta_epsilon,
                group_activation_threshold=group_activation_threshold,
                dominance_share_threshold=dominance_share_threshold,
                market_food_dominance_threshold=market_food_dominance_threshold,
                structural_outlier_gap=structural_outlier_gap,
                event_stale_after_days=event_stale_after_days,
                event_decay_half_life_days=event_decay_half_life_days,
                event_min_decay_factor=event_min_decay_factor,
                event_fresh_boost_factor=event_fresh_boost_factor,
                event_stale_warning_days=event_stale_warning_days,
                limited_coverage_threshold=limited_coverage_threshold,
                reduced_coverage_threshold=reduced_coverage_threshold,
                freshness_model=freshness_model,
                freshness_min_fresh_contribution_share=freshness_min_fresh_contribution_share,
                freshness_max_stale_contribution_share=freshness_max_stale_contribution_share,
                dynamic_layer_readiness_min_share=dynamic_layer_readiness_min_share,
                responsiveness_delta_threshold=responsiveness_delta_threshold,
                responsiveness_lag_tolerance_months=responsiveness_lag_tolerance_months,
                peak_prominence_min=peak_prominence_min,
                peak_min_rise=peak_min_rise,
                peak_min_fall=peak_min_fall,
                peak_min_separation_periods=peak_min_separation_periods,
                peak_quality_floor=peak_quality_floor,
                peak_support_group_min_share=peak_support_group_min_share,
                peak_country_specific_share_threshold=peak_country_specific_share_threshold,
                peak_global_share_warning_threshold=peak_global_share_warning_threshold,
                peak_model_driven_global_share_threshold=peak_model_driven_global_share_threshold,
                peak_single_group_dominance_threshold=peak_single_group_dominance_threshold,
                peak_event_support_weak_threshold=peak_event_support_weak_threshold,
                peak_event_support_strong_threshold=peak_event_support_strong_threshold,
                event_alignment_temporal_distance_days=event_alignment_temporal_distance_days,
                event_alignment_direct_match_threshold=event_alignment_direct_match_threshold,
                event_alignment_context_match_threshold=event_alignment_context_match_threshold,
                event_alignment_weak_match_threshold=event_alignment_weak_match_threshold,
                event_alignment_multi_overlap_min_events=event_alignment_multi_overlap_min_events,
                event_registry_path=Path(event_registry_path_raw),
                event_marker_registry_path=Path(event_marker_registry_path_raw),
                expected_ranking=expected_ranking,
                reference_episodes_path=Path(reference_episodes_path_raw),
            ),
        ),
    )


def load_pipeline_config(path: Path) -> PipelineConfig:
    """
    Load and validate standard configuration.

    Traceability:
    - PSwR-002
    - PSyR-001
    - PSyR-002
    - PM-006
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    top_level = _require_mapping(raw, section="root")
    _require_keys(
        top_level,
        section="root",
        keys=["countries", "windows", "historical", "versions", "output", "scoring", "v3_1"],
    )

    countries = _validate_countries(top_level["countries"])
    windows = _validate_windows(top_level["windows"])
    historical = _validate_historical(
        top_level["historical"],
        configured_countries=countries,
    )
    versions = _validate_versions(top_level["versions"])
    output = _validate_output(top_level["output"])
    scoring = _validate_scoring(top_level["scoring"])
    v3_1 = _validate_v31(
        top_level["v3_1"],
        configured_countries=countries,
        scoring=scoring,
    )

    return PipelineConfig(
        countries=countries,
        short_days=windows["short_days"],
        recent_days=windows["recent_days"],
        baseline_days=windows["baseline_days"],
        query_version=versions["query_version"],
        scoring_version=versions["scoring_version"],
        bridge_file_version=versions["bridge_file_version"],
        context_table_version=versions["context_table_version"],
        report_dir=output["report_dir"],
        reference_dir=output["reference_dir"],
        gdelt_path=Path("data/gdelt/gdelt_events.csv"),
        ucdp_path=Path("data/ucdp/ucdp_events.csv"),
        bridge_path=Path("data/bridge/bridge_events.csv"),
        context_path=Path("data/context/country_context.csv"),
        scoring=scoring,
        historical=historical,
        v3_1=v3_1,
    )
