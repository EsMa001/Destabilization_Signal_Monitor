from __future__ import annotations

"""
Standard-mode prototype pipeline.

Traceability:
- PSR-001
- PSR-003
- PSR-005
- PSR-006
- PSR-007
- PSR-008
- PSR-009
- PSR-010
- PSR-011
- PSR-012
- PSR-013
- PSR-014
- PSR-015
- PSR-016
- PSR-017
- PSR-018
- PSR-019
- PSR-020
- PSR-021
- PSR-022
- PSR-023
- PSR-024
- PSR-026
- PSyR-006
- PSyR-007
- PSyR-008
- PSyR-009
- PSyR-010
- PSyR-011
- PSyR-012
- PSyR-015
- PSyR-016
- PSyR-017
- PSyR-018
- PSyR-019
- PSyR-020
- PSyR-021
- PSyR-022
- PSyR-023
- PSyR-024
- PSyR-025
- PSyR-026
- PSyR-027
- PSyR-028
- PSyR-029
- PSyR-030
- PSyR-031
- PSyR-032
- PSyR-033
- PSyR-034
- PSyR-035
- PSyR-036
- PSyR-037
- PSyR-038
- PSyR-041
- PSyR-042
- PSyR-043
- PSwR-029
- PSwR-034
- PSwR-039
- PSwR-041
- PSwR-042
- PSwR-043
- PSwR-045
- PSwR-046
- PSwR-047
- PSwR-048
- PSwR-049
- PSwR-050
- PSwR-051
- PSwR-052
- PSwR-053
- PSwR-054
- PSwR-056
- PSwR-057
- PSwR-058
- PSwR-059
- PSwR-060
- PSwR-061
- PSwR-091
- PSwR-092
- PSwR-093
- PSwR-094
- PSwR-095
- PSwR-096
- PSwR-097
- PSwR-098
- PSwR-099
- PSwR-100
- PSwR-101
- PSwR-102
- PSwR-103
- PSwR-104
- PSwR-071
- PSwR-072
- PSwR-073
- PSwR-074
- PSwR-075
- PSwR-076
- PSwR-077
- PSwR-078
- PSwR-079
- PSwR-080
- PSwR-081
- PSwR-082
- PSwR-083
- PSwR-084
- PSwR-085
- PSwR-086
- PSwR-087
- PSwR-088
- PSwR-089
- PSwR-090
- PSwR-062
- PSwR-063
- PSwR-064
- PSwR-065
- PSwR-066
- PSwR-067
- PSwR-068
- PSwR-069
- PSwR-070
- PSwR-113
- PSwR-114
- PSwR-115
- PSwR-116
- PSwR-117
- PSwR-118
- PSwR-119
- PSwR-120
- PSwR-121
- PSwR-122
- PSwR-123
- PSwR-124
- PM-001
- PM-008
- PM-009
- PM-010
- PM-014
- PM-016
- PM-017
- PM-018
- PM-019
- PM-020
- PM-021
- PM-022
- PM-023
- PM-024
- PM-025
- PM-026
- PM-027
- PM-028
- PM-029
- PM-030
- PM-031
- PM-032
- PM-033
- PM-034
- PM-035
- PM-036
- PM-037
- PM-038
- PM-039
- PM-040
- PM-041
- PM-042
- PM-043
- PM-044
- PM-045
- PM-046
- PM-047
- PM-048
- PM-049
- PM-050
- PM-051
- PM-052
- PM-053
- PM-054
- PM-055
- PM-056
- PM-063
- PM-064
- PM-065
- PM-066
- PM-067
- PM-068
- PM-069
- PM-070
- PM-071
"""

from dataclasses import asdict
from datetime import UTC, date, datetime
import json
import os
from pathlib import Path
from statistics import mean
import shutil

from proto.common import canonical_country
from proto.fusion.models import (
    FusionGroupScoreRecord,
    FusionHistoricalGroupScoreRecord,
    FusionHistoricalSourceSignalRecord,
    FusionHistoricalTotalScoreRecord,
    FusionSourceSignalRecord,
    FusionTotalScoreRecord,
)
from proto.fusion.scoring import (
    build_historical_fusion_scores,
    build_fusion_group_scores,
    build_fusion_source_signals,
    build_fusion_total_scores,
    summarize_group_availability,
)
from proto.fusion.validation import (
    ValidationCountryGroupProfileRecord,
    ValidationCountryEventAlignmentRecord,
    ValidationEventMarkerRecord,
    ValidationEventCoverageSummaryRecord,
    ValidationEventRegistryRecord,
    ValidationCountryPeakPhaseRecord,
    ValidationCountryProfileRecord,
    ValidationEpisodeResultRecord,
    ValidationFreshnessGroupRecord,
    ValidationGlobalPeakSynchronizationRecord,
    ValidationHistoricalResponsivenessRecord,
    ValidationLayerDiagnosticRecord,
    ValidationPeakAttributionRecord,
    ValidationPeakEventMatchRecord,
    ValidationPeakEventSupportRecord,
    ValidationRankingTrajectoryRecord,
    ValidationRankingRecord,
    ValidationReferenceEpisodeRecord,
    ValidationTrajectoryProfileRecord,
    build_validation_framework,
    build_validation_summary,
    compute_peak_attribution,
    compute_peak_event_alignment,
    compute_country_profile_comparison,
    compute_historical_responsiveness,
    compute_layer_diagnostics,
    compute_snapshot_freshness_groups,
    compute_validation_episode_results,
    compute_validation_ranking,
    load_event_registry,
    load_event_marker_registry,
    load_validation_reference_episodes,
)
from proto.features.escalation_features import build_escalation_features
from proto.features.gdelt_features import build_tension_features
from proto.features.vulnerability_features import build_vulnerability_features
from proto.models import ClusterAssessment, ScoreRecord
from proto.observations.models import ObservationRecord
from proto.pipeline.config import load_pipeline_config
from proto.reporting.exports import write_csv_records, write_json_records
from proto.reporting.handout import build_handout_markdown, write_handout
from proto.reporting.plots import (
    save_cluster_score_plots,
    save_fusion_group_plots,
    save_fusion_historical_group_plots,
    save_fusion_historical_total_plots,
    save_historical_cluster_plots,
    save_historical_subscore_plots,
    save_v431_country_peak_attribution_plots,
    save_v431_peak_synchronization_plot,
    save_v432_country_event_alignment_plots,
    save_v43_country_profile_plots,
    save_v43_multicountry_total_plot,
    save_v43_ranking_trajectory_plot,
)
from proto.reporting.presentation import (
    CLUSTER_ORDER,
    cluster_order_index,
    country_order_index,
    display_cluster,
)
from proto.reporting.summary_text import build_short_summary
from proto.runs.compare_runs import write_run_comparison
from proto.runs.metadata import write_run_metadata
from proto.runs.models import RunMetadata
from proto.runs.reference import ensure_reference_metadata_schema, freeze_reference_run_if_absent
from proto.runs.status import propose_run_status, validate_status_override
from proto.scoring.cluster_scores import compute_cluster_scores
from proto.scoring.confidence import apply_snapshot_fallback_penalty, derive_confidence_by_cluster
from proto.scoring.subscores import compute_subscores
from proto.scoring.thresholds import StageThresholds, derive_stage_by_cluster
from proto.scoring.trend import derive_trend_by_cluster
from proto.scoring.trend_history import (
    HistoricalReviewCandidateRecord,
    HistoricalRollingRecord,
    build_historical_review_candidates,
    build_historical_rolling_records,
    build_snapshot_context_by_cluster,
    latest_valid_points_by_series,
    latest_points_with_value_by_series,
    points_on_date_by_series,
)
from proto.sources.bridge import BridgeRecord, load_bridge_records
from proto.sources.context import ContextRecord, load_context_records
from proto.sources.fao_ffpi import load_fao_ffpi_observations
from proto.sources.fao_fpma import load_fao_fpma_observations
from proto.sources.gdacs import load_gdacs_observations
from proto.sources.gdelt import load_gdelt_records
from proto.sources.gdelt_event import load_gdelt_event_observations
from proto.sources.governance_input import load_governance_input_observations
from proto.sources.narrative_input import load_narrative_input_observations
from proto.sources.unhcr import load_unhcr_observations
from proto.sources.un_comtrade import load_un_comtrade_observations
from proto.sources.ucdp import load_ucdp_records

STATUS_SUCCESS = "erfolgreich"
STATUS_LIMITED = "eingeschränkt brauchbar"
SNAPSHOT_SOURCE_VALID_ENDPOINT = "historical_valid_endpoint"
SNAPSHOT_SOURCE_VALID_LAGGED = "historical_latest_valid_before_run_date"
SNAPSHOT_SOURCE_NUMERIC_FALLBACK = "historical_numeric_fallback_below_min_valid_days"
SNAPSHOT_SOURCE_RAW_FALLBACK = "raw_latest_fallback_no_historical_value"


def _latest_score_by_cluster(
    cluster_scores: list[ScoreRecord],
) -> dict[tuple[str, str], ScoreRecord]:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    latest: dict[tuple[str, str], ScoreRecord] = {}
    for score in cluster_scores:
        key = (score.country, score.cluster)
        previous = latest.get(key)
        if previous is None or score.date > previous.date:
            latest[key] = score
    return latest


def _derive_source_count_by_cluster(
    *,
    countries: list[str],
    gdelt_records,
    ucdp_records,
    bridge_records: list[BridgeRecord],
    context_records: list[ContextRecord],
) -> dict[tuple[str, str], int]:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    source_count: dict[tuple[str, str], int] = {}
    for country in countries:
        canonical = canonical_country(country)
        has_gdelt = any(canonical_country(record.country) == canonical for record in gdelt_records)
        has_ucdp = any(canonical_country(record.country) == canonical for record in ucdp_records)
        has_bridge_tension = any(
            canonical_country(record.country) == canonical and record.cluster == "tension"
            for record in bridge_records
        )
        has_bridge_escalation = any(
            canonical_country(record.country) == canonical and record.cluster == "escalation"
            for record in bridge_records
        )
        has_context = any(canonical_country(record.country) == canonical for record in context_records)
        source_count[(canonical, "tension")] = int(has_gdelt) + int(has_bridge_tension)
        source_count[(canonical, "escalation")] = int(has_ucdp) + int(has_bridge_escalation)
        source_count[(canonical, "vulnerability")] = int(has_context)
    return source_count


def _build_assessments(
    *,
    latest_cluster_scores: dict[tuple[str, str], ScoreRecord],
    stage_by_cluster: dict[tuple[str, str], str],
    trend_by_cluster: dict[tuple[str, str], str],
    confidence_by_cluster: dict[tuple[str, str], tuple[float, str]],
) -> list[ClusterAssessment]:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    assessments: list[ClusterAssessment] = []
    sorted_items = sorted(
        latest_cluster_scores.items(),
        key=lambda item: (
            country_order_index(item[0][0]),
            cluster_order_index(item[0][1]),
        ),
    )
    for key, score in sorted_items:
        stage = stage_by_cluster.get(key, "niedrig")
        trend = trend_by_cluster.get(key, "stabil")
        confidence_score, confidence_level = confidence_by_cluster.get(key, (0.0, "niedrig"))
        summary = build_short_summary(
            display_cluster(score.cluster),
            stage,
            trend,
            confidence_level,
        )
        assessments.append(
            ClusterAssessment(
                country=score.country,
                cluster=score.cluster,
                cluster_score=round(score.score_value, 4),
                stage=stage,
                trend=trend,
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                summary_text=summary,
            )
        )
    return assessments


def _assessment_records(
    assessments: list[ClusterAssessment],
    *,
    snapshot_source_by_cluster: dict[tuple[str, str], dict[str, object]],
) -> list[dict]:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    rows: list[dict] = []
    for assessment in assessments:
        source = snapshot_source_by_cluster.get((assessment.country, assessment.cluster), {})
        rows.append(
            {
                "country": assessment.country,
                "cluster": assessment.cluster,
                "cluster_score": assessment.cluster_score,
                "stage": assessment.stage,
                "trend": assessment.trend,
                "confidence_score": assessment.confidence_score,
                "confidence_level": assessment.confidence_level,
                "summary_text": assessment.summary_text,
                "snapshot_source_mode": source.get("source_mode", SNAPSHOT_SOURCE_RAW_FALLBACK),
                "snapshot_source_date": source.get("source_date"),
                "snapshot_endpoint_is_valid": source.get("endpoint_is_valid", False),
                "snapshot_source_is_valid": source.get("source_is_valid"),
                "snapshot_source_valid_days": source.get("valid_days"),
                "snapshot_source_min_valid_days": source.get("min_valid_days"),
                "snapshot_source_coverage_ratio": source.get("coverage_ratio"),
                "snapshot_confidence_penalty_applied": source.get("confidence_penalty_applied", 0.0),
                "snapshot_constant_cluster_assumption": source.get("constant_cluster_assumption", False),
            }
        )
    return rows


def _required_outputs_present(
    *,
    features_path: Path,
    scores_path: Path,
    summary_path: Path,
    plot_paths: list[Path],
) -> bool:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    return (
        features_path.exists()
        and scores_path.exists()
        and summary_path.exists()
        and bool(plot_paths)
    )


def _cache_previous_run(
    *,
    run_dir: Path,
    cache_dir: Path,
) -> tuple[Path | None, Path | None]:
    """
    Cache previous run summary/metadata before current run folder is replaced.

    Traceability:
    - PSyR-009
    - OI-006
    """
    summary_candidates = [
        run_dir / "exports" / "snapshot" / "summary_export.json",
        run_dir / "exports" / "summary_export.json",
    ]
    previous_summary = next((path for path in summary_candidates if path.exists()), None)
    previous_metadata = run_dir / "run_metadata.json"
    if previous_summary is None or not previous_metadata.exists():
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
        return None, None

    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached_summary = cache_dir / "summary_export.json"
    cached_metadata = cache_dir / "run_metadata.json"
    shutil.copy2(previous_summary, cached_summary)
    shutil.copy2(previous_metadata, cached_metadata)
    return cached_summary, cached_metadata


def _derive_escalation_breakdown(
    *,
    countries: list[str],
    latest_historical_points: dict[tuple[str, str, str], HistoricalRollingRecord],
) -> dict[str, dict[str, float | None]]:
    """
    Build internal vs external escalation visibility per country from rolling points.

    Traceability:
    - PSyR-004
    - PSwR-008
    - PSwR-015
    - PSwR-022
    """
    output: dict[str, dict[str, float | None]] = {}
    for country in countries:
        internal = latest_historical_points.get(
            (country, "escalation", "internal_dynamics_subscore")
        )
        external = latest_historical_points.get(
            (country, "escalation", "external_dynamics_subscore")
        )
        output[country] = {
            "internal": internal.rolling_value if internal and internal.rolling_value is not None else None,
            "external": external.rolling_value if external and external.rolling_value is not None else None,
        }
    return output


def _plots_by_country(
    *,
    plot_paths: list[Path],
    countries: list[str],
) -> dict[str, list[Path]]:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    grouped: dict[str, list[Path]] = {country: [] for country in countries}
    for path in plot_paths:
        name = path.name.lower()
        stem_tokens = set(path.stem.lower().split("_"))
        for country in countries:
            country_key = country.lower()
            if (
                name.startswith(f"{country_key}_")
                or f"_{country_key}_" in name
                or country_key in stem_tokens
            ):
                grouped[country].append(path)
                break
    return grouped


def _validate_snapshot_plot_coverage(
    *,
    plot_paths: list[Path],
    countries: list[str],
) -> None:
    """
    Ensure mandatory central snapshot plots are available in handout.

    Traceability:
    - PSR-005
    - PSwR-016
    """
    grouped = _plots_by_country(plot_paths=plot_paths, countries=countries)
    for country in countries:
        available_clusters = {
            next(
                (
                    cluster
                    for cluster in CLUSTER_ORDER
                    if f"_{cluster}_timeseries" in path.stem
                ),
                None,
            )
            for path in grouped[country]
        }
        if set(CLUSTER_ORDER) - {value for value in available_clusters if value is not None}:
            raise RuntimeError(f"missing mandatory snapshot plot coverage for country {country}")


def _write_historical_status_file(
    *,
    out_dir: Path,
    status: str,
    historical_limited_marker: bool,
    enabled: bool,
    constant_clusters: set[str],
) -> None:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    payload = {
        "status": status,
        "historical_enabled": enabled,
        "historical_limited_marker": historical_limited_marker,
        "constant_clusters": sorted(constant_clusters),
        "method_notes": {
            "vulnerability_cluster_role": (
                "structural_baseline_cluster"
                if "vulnerability" in constant_clusters
                else "not_constant"
            )
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "historical_status.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_snapshot_status_file(
    *,
    out_dir: Path,
    run_date: date,
    snapshot_source_by_cluster: dict[tuple[str, str], dict[str, object]],
) -> None:
    """
    Persist explicit snapshot derivation status per country/cluster.

    Traceability:
    - PSwR-022
    - PSwR-026
    - PSwR-033
    - PM-010
    - PM-012
    - OI-021
    """
    mode_counts: dict[str, int] = {}
    items: list[dict[str, object]] = []
    for (country, cluster), source in sorted(snapshot_source_by_cluster.items()):
        mode = str(source.get("source_mode", SNAPSHOT_SOURCE_RAW_FALLBACK))
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        items.append(
            {
                "country": country,
                "cluster": cluster,
                "source_mode": mode,
                "source_date": source.get("source_date"),
                "endpoint_is_valid": bool(source.get("endpoint_is_valid", False)),
                "source_is_valid": source.get("source_is_valid"),
                "valid_days": source.get("valid_days"),
                "min_valid_days": source.get("min_valid_days"),
                "coverage_ratio": source.get("coverage_ratio"),
                "confidence_penalty_applied": source.get("confidence_penalty_applied", 0.0),
                "constant_cluster_assumption": bool(
                    source.get("constant_cluster_assumption", False)
                ),
            }
        )

    payload = {
        "snapshot_rule_version": "v2.2.1",
        "run_date": run_date.isoformat(),
        "overview": {
            "items": len(items),
            "modes": mode_counts,
        },
        "series": items,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "snapshot_status.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_v31_observations(
    *,
    config,
) -> list[ObservationRecord]:
    """
    Load V3.1 source observations through canonical adapter contract.

    Traceability:
    - PSyR-018
    - PSyR-021
    - PSwR-039
    - PSwR-048
    - PSwR-049
    - PSwR-050
    - PSwR-059
    - PSwR-060
    - PSwR-061
    - PSwR-091
    - PSwR-071
    """
    source_config = config.v3_1.source_config_by_id()
    ffpi_cfg = source_config["fao_ffpi"]
    fpma_cfg = source_config["fao_fpma"]
    comtrade_cfg = source_config["un_comtrade"]
    gdacs_cfg = source_config["gdacs"]
    unhcr_cfg = source_config["unhcr"]
    narrative_cfg = source_config["narrative_input"]
    governance_cfg = source_config["governance_input"]
    gdelt_event_cfg = source_config["gdelt_event"]

    ffpi_observations = load_fao_ffpi_observations(
        ffpi_cfg.path,
        normalization_method=ffpi_cfg.normalization_method,
        baseline_value=ffpi_cfg.normalization_baseline_value,
        baseline_scale=ffpi_cfg.normalization_baseline_scale,
    )
    fpma_observations = load_fao_fpma_observations(
        fpma_cfg.path,
        normalization_method=fpma_cfg.normalization_method,
        baseline_value=fpma_cfg.normalization_baseline_value,
        baseline_scale=fpma_cfg.normalization_baseline_scale,
    )
    comtrade_observations = load_un_comtrade_observations(
        comtrade_cfg.path,
        normalization_method=comtrade_cfg.normalization_method,
        baseline_value=comtrade_cfg.normalization_baseline_value,
        baseline_scale=comtrade_cfg.normalization_baseline_scale,
    )
    gdacs_observations = load_gdacs_observations(
        gdacs_cfg.path,
        normalization_method=gdacs_cfg.normalization_method,
        baseline_value=gdacs_cfg.normalization_baseline_value,
        baseline_scale=gdacs_cfg.normalization_baseline_scale,
    )
    unhcr_observations = load_unhcr_observations(
        unhcr_cfg.path,
        normalization_method=unhcr_cfg.normalization_method,
        normalization_scope=unhcr_cfg.normalization_scope,
        baseline_value=unhcr_cfg.normalization_baseline_value,
        baseline_scale=unhcr_cfg.normalization_baseline_scale,
    )
    narrative_observations = load_narrative_input_observations(
        narrative_cfg.path,
        normalization_method=narrative_cfg.normalization_method,
        normalization_scope=narrative_cfg.normalization_scope,
        baseline_value=narrative_cfg.normalization_baseline_value,
        baseline_scale=narrative_cfg.normalization_baseline_scale,
    )
    governance_observations = load_governance_input_observations(
        governance_cfg.path,
        normalization_method=governance_cfg.normalization_method,
        normalization_scope=governance_cfg.normalization_scope,
        baseline_value=governance_cfg.normalization_baseline_value,
        baseline_scale=governance_cfg.normalization_baseline_scale,
    )
    gdelt_event_observations = load_gdelt_event_observations(
        gdelt_event_cfg.path,
        normalization_method=gdelt_event_cfg.normalization_method,
        normalization_scope=gdelt_event_cfg.normalization_scope,
        baseline_value=gdelt_event_cfg.normalization_baseline_value,
        baseline_scale=gdelt_event_cfg.normalization_baseline_scale,
    )
    return (
        ffpi_observations
        + fpma_observations
        + comtrade_observations
        + gdacs_observations
        + unhcr_observations
        + narrative_observations
        + governance_observations
        + gdelt_event_observations
    )


def _write_fusion_status_file(
    *,
    out_dir: Path,
    enabled: bool,
    group_records: list[FusionGroupScoreRecord],
    total_records: list[FusionTotalScoreRecord],
    historical_group_records: list[FusionHistoricalGroupScoreRecord],
    historical_total_records: list[FusionHistoricalTotalScoreRecord],
    plausibility_warnings: list[dict[str, object]],
    validation_summary: dict[str, object],
) -> None:
    """
    Persist compact V3.1 fusion status summary.

    Traceability:
    - PSwR-051
    - PSwR-069
    - PSyR-007
    """
    payload = {
        "enabled": enabled,
        "group_records": len(group_records),
        "total_records": len(total_records),
        "historical_group_records": len(historical_group_records),
        "historical_total_records": len(historical_total_records),
        "group_availability": summarize_group_availability(group_records),
        "plausibility_warnings": plausibility_warnings,
        "plausibility_warning_count": len(plausibility_warnings),
        "validation_summary": validation_summary,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "fusion_status.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_event_alignment_review_file(
    *,
    out_path: Path,
    summary: dict[str, object],
    coverage_records: list[ValidationEventCoverageSummaryRecord],
    country_alignment_records: list[ValidationCountryEventAlignmentRecord],
    peak_event_matches: list[ValidationPeakEventMatchRecord],
) -> None:
    """
    Persist compact analyst-facing review notes for V4.3.2 event alignment.

    Traceability:
    - PSwR-119
    - PSwR-120
    - PSwR-123
    - PM-070
    """
    global_coverage = next(
        (item for item in coverage_records if item.scope == "global"),
        None,
    )
    lines = [
        "# Event Alignment Review",
        "",
        "## Summary",
        "",
        f"- peak_event_match_record_count: {summary.get('peak_event_match_record_count', len(peak_event_matches))}",
        f"- credible_match_ratio: {float(summary.get('credible_match_ratio', global_coverage.credible_match_ratio if global_coverage else 0.0) or 0.0):.2f}",
        f"- no_credible_match_ratio: {float(summary.get('no_credible_match_ratio', global_coverage.no_credible_match_ratio if global_coverage else 0.0) or 0.0):.2f}",
        f"- multi_event_overlap_ratio: {float(summary.get('multi_event_overlap_ratio', global_coverage.multi_event_overlap_ratio if global_coverage else 0.0) or 0.0):.2f}",
        f"- mean_match_confidence: {float(summary.get('mean_match_confidence', global_coverage.mean_match_confidence if global_coverage else 0.0) or 0.0):.2f}",
        "",
        "## Country Coverage",
        "",
    ]
    country_coverage = sorted(
        [item for item in coverage_records if item.scope == "country"],
        key=lambda item: item.country,
    )
    if not country_coverage:
        lines.append("- no country coverage records")
    else:
        for item in country_coverage:
            lines.append(
                "- "
                f"{item.country}: credible={item.credible_match_ratio:.2f}, "
                f"no_match={item.no_credible_match_ratio:.2f}, "
                f"multi_overlap={item.multi_event_overlap_ratio:.2f}, "
                f"band={item.coverage_band}"
            )

    lines.extend(
        [
            "",
            "## Alignment Maturity",
            "",
        ]
    )
    if not country_alignment_records:
        lines.append("- no country alignment records")
    else:
        for item in sorted(country_alignment_records, key=lambda row: row.country):
            lines.append(
                "- "
                f"{item.country}: maturity={item.alignment_maturity} ({item.alignment_maturity_score:.2f}), "
                f"trajectory={item.trajectory_profile}, "
                f"uncertainties={item.open_uncertainties or 'none'}"
            )

    no_match_peaks = [
        item
        for item in peak_event_matches
        if item.match_class == "no_credible_match"
    ]
    if no_match_peaks:
        lines.extend(
            [
                "",
                "## Manual Review Queue",
                "",
            ]
        )
        for item in sorted(
            no_match_peaks,
            key=lambda row: (row.country, row.peak_rank),
        )[:20]:
            lines.append(
                "- "
                f"{item.country} peak#{item.peak_rank} {item.period_label}: "
                f"match_class={item.match_class}, "
                f"confidence={item.match_confidence:.2f}, "
                f"note={item.uncertainty_note or 'none'}"
            )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _build_fusion_plausibility_warnings(
    *,
    source_signals: list[FusionSourceSignalRecord],
    group_records: list[FusionGroupScoreRecord],
    total_records: list[FusionTotalScoreRecord],
    historical_total_records: list[FusionHistoricalTotalScoreRecord],
    event_stale_warning_days: int,
    dominance_share_threshold: float,
    validation_summary: dict[str, object] | None = None,
    validation_layer_diagnostics: list[ValidationLayerDiagnosticRecord] | None = None,
    validation_peak_attribution: list[ValidationPeakAttributionRecord] | None = None,
    validation_trajectory_profiles: list[ValidationTrajectoryProfileRecord] | None = None,
    validation_peak_event_matches: list[ValidationPeakEventMatchRecord] | None = None,
    validation_event_coverage: list[ValidationEventCoverageSummaryRecord] | None = None,
    validation_country_event_alignment: list[ValidationCountryEventAlignmentRecord] | None = None,
) -> list[dict[str, object]]:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    warnings: list[dict[str, object]] = []
    if not group_records:
        return warnings

    countries = sorted({record.country for record in group_records})
    by_group: dict[str, list[FusionGroupScoreRecord]] = {}
    for record in group_records:
        by_group.setdefault(record.group, []).append(record)

    event_records = by_group.get("event", [])
    event_available = [
        record
        for record in event_records
        if record.status in {"ok", "limited"} and record.group_score is not None
    ]
    if event_records and len(event_available) < len(countries):
        missing = sorted(
            {
                record.country
                for record in event_records
                if record.status not in {"ok", "limited"} or record.group_score is None
            }
        )
        warnings.append(
            {
                "code": "event_group_partial_coverage",
                "severity": "warn",
                "missing_countries": missing,
                "message": (
                    "Event group is not fully available in snapshot for all countries: "
                    + ", ".join(missing)
                ),
            }
        )
    if event_records and event_available:
        event_scores = [float(record.group_score) for record in event_available]
        if max(event_scores) - min(event_scores) < 2.0:
            warnings.append(
                {
                    "code": "event_group_low_cross_country_contrast",
                    "severity": "info",
                    "message": "Event group shows low cross-country contrast in current snapshot.",
                }
            )
    event_signals = [signal for signal in source_signals if signal.group == "event"]
    if event_signals and all(signal.age_days > event_stale_warning_days for signal in event_signals):
        warnings.append(
            {
                "code": "event_signal_stale",
                "severity": "warn",
                "max_age_days": max(signal.age_days for signal in event_signals),
                "message": (
                    "Event source signals are stale "
                    f"(>{event_stale_warning_days} days) for all countries in current snapshot."
                ),
            }
        )

    for group, records in sorted(by_group.items()):
        available = [
            record
            for record in records
            if record.status in {"ok", "limited"} and record.group_score is not None
        ]
        if len(available) != len(countries):
            continue
        if all(float(record.group_score) >= 95.0 for record in available):
            warnings.append(
                {
                    "code": "group_saturation_all_countries",
                    "severity": "warn",
                    "group": group,
                    "message": (
                        f"Group {group} is saturated >=95 in all countries "
                        "for the current snapshot."
                    ),
                }
            )
        ranked = sorted(available, key=lambda item: float(item.group_score), reverse=True)
        if len(ranked) >= 3 and float(ranked[0].group_score) >= 85.0 and float(ranked[1].group_score) <= 55.0:
            warnings.append(
                {
                    "code": "group_country_outlier_high",
                    "severity": "info",
                    "group": group,
                    "country": ranked[0].country,
                    "value": round(float(ranked[0].group_score), 2),
                    "next_value": round(float(ranked[1].group_score), 2),
                    "message": (
                        f"Group {group} shows a high country outlier "
                        f"({ranked[0].country}: {float(ranked[0].group_score):.2f})."
                    ),
                }
            )

    low_coverage_by_country: dict[str, int] = {}
    for record in historical_total_records:
        if record.available_group_ratio < 0.5:
            low_coverage_by_country[record.country] = low_coverage_by_country.get(record.country, 0) + 1
    if low_coverage_by_country:
        affected = [
            f"{country} ({count})"
            for country, count in sorted(low_coverage_by_country.items())
        ]
        warnings.append(
            {
                "code": "historical_low_group_coverage_summary",
                "severity": "warn",
                "countries": sorted(low_coverage_by_country.keys()),
                "period_counts": low_coverage_by_country,
                "message": (
                    "Historical fusion contains early period(s) with <50% group coverage: "
                    + ", ".join(affected)
                ),
            }
        )

    for record in total_records:
        if record.dominant_group_contribution_share > dominance_share_threshold:
            warnings.append(
                {
                    "code": "single_layer_dominance",
                    "severity": "info",
                    "country": record.country,
                    "share": round(record.dominant_group_contribution_share, 4),
                    "message": (
                        f"{record.country} fusion snapshot is dominated by one layer "
                        f"(share={record.dominant_group_contribution_share:.2f}, "
                        f"threshold={dominance_share_threshold:.2f})."
                    ),
                }
            )

    summary = validation_summary or {}
    diagnostics = validation_layer_diagnostics or []
    peak_attribution = validation_peak_attribution or []
    trajectory_profiles = validation_trajectory_profiles or []
    peak_event_matches = validation_peak_event_matches or []
    event_coverage = validation_event_coverage or []
    country_event_alignment = validation_country_event_alignment or []
    low_fresh_coverage_count = int(summary.get("low_fresh_coverage_country_count", 0) or 0)
    stale_burden_count = int(summary.get("stale_burden_country_count", 0) or 0)
    governance_instability_count = int(summary.get("governance_instability_country_count", 0) or 0)
    governance_low_freshness_count = int(summary.get("governance_low_freshness_country_count", 0) or 0)
    dynamic_ready_count = int(summary.get("dynamic_layer_ready_country_count", 0) or 0)
    dynamic_total = len(total_records)
    if low_fresh_coverage_count > 0:
        warnings.append(
            {
                "code": "low_fresh_coverage",
                "severity": "warn",
                "country_count": low_fresh_coverage_count,
                "message": (
                    f"{low_fresh_coverage_count} country snapshot(s) have low fresh contribution share."
                ),
            }
        )
    if stale_burden_count > 0:
        warnings.append(
            {
                "code": "aging_data_burden",
                "severity": "warn",
                "country_count": stale_burden_count,
                "message": (
                    f"{stale_burden_count} country snapshot(s) are strongly driven by stale/aging layer contributions."
                ),
            }
        )
    if governance_instability_count > 0:
        warnings.append(
            {
                "code": "governance_instability_elevated",
                "severity": "info",
                "country_count": governance_instability_count,
                "message": (
                    f"{governance_instability_count} country snapshot(s) show elevated governance-instability contribution."
                ),
            }
        )
    if governance_low_freshness_count > 0:
        warnings.append(
            {
                "code": "governance_signal_stale",
                "severity": "warn",
                "country_count": governance_low_freshness_count,
                "message": (
                    f"{governance_low_freshness_count} country snapshot(s) rely on stale governance signals."
                ),
            }
        )
    if dynamic_total > 0 and dynamic_ready_count < dynamic_total:
        warnings.append(
            {
                "code": "dynamic_layer_readiness_gap",
                "severity": "info",
                "ready_country_count": dynamic_ready_count,
                "country_count": dynamic_total,
                "message": (
                    "Dynamic-layer freshness readiness is incomplete across countries."
                ),
            }
        )
    response_lag_fit_rate = float(summary.get("response_lag_fit_rate", 0.0) or 0.0)
    if response_lag_fit_rate < 0.66:
        warnings.append(
            {
                "code": "response_lag_review",
                "severity": "info",
                "response_lag_fit_rate": round(response_lag_fit_rate, 4),
                "message": (
                    "Historical response-lag fit is below target review range and should be monitored."
                ),
            }
        )
    stale_dominant_countries = sorted(
        [
            item.country
            for item in diagnostics
            if item.dominant_stale_group is not None
            and item.stale_contribution_share >= 0.5
        ]
    )
    if stale_dominant_countries:
        warnings.append(
            {
                "code": "stale_dominant_country",
                "severity": "warn",
                "countries": stale_dominant_countries,
                "message": (
                    "At least one country has stale-dominated fusion contribution in current snapshot."
                ),
            }
        )
    if peak_attribution:
        synchronized_peak_count = len(
            [
                item
                for item in peak_attribution
                if item.attribution_label in {"globally_co_moving_peak", "global_background_stress_peak"}
            ]
        )
        weak_peak_count = len(
            [item for item in peak_attribution if item.attribution_label == "weakly_supported_peak"]
        )
        single_group_peak_count = len(
            [
                item
                for item in peak_attribution
                if item.dominant_group_share >= 0.58
            ]
        )
        peak_count = len(peak_attribution)
        if peak_count > 0 and (synchronized_peak_count / float(peak_count)) >= 0.5:
            warnings.append(
                {
                    "code": "peak_globally_synchronized",
                    "severity": "warn",
                    "peak_count": peak_count,
                    "synchronized_peak_count": synchronized_peak_count,
                    "message": (
                        "Many detected peaks are globally synchronized; check country-specific differentiation."
                    ),
                }
            )
        if peak_count > 0 and (weak_peak_count / float(peak_count)) >= 0.4:
            warnings.append(
                {
                    "code": "peak_weak_event_support",
                    "severity": "warn",
                    "peak_count": peak_count,
                    "weak_peak_count": weak_peak_count,
                    "message": (
                        "A large share of peaks is weakly event-supported or not externally validated."
                    ),
                }
            )
        if single_group_peak_count > 0:
            warnings.append(
                {
                    "code": "peak_single_group_dominance",
                    "severity": "info",
                    "peak_count": peak_count,
                    "single_group_peak_count": single_group_peak_count,
                    "message": (
                        "Some peaks are dominated by one group; review support breadth and attribution confidence."
                    ),
                }
            )
    low_differentiation_countries = sorted(
        [
            item.country
            for item in trajectory_profiles
            if not item.differentiation_flag
        ]
    )
    if low_differentiation_countries:
        warnings.append(
            {
                "code": "trajectory_low_country_specificity",
                "severity": "info",
                "countries": low_differentiation_countries,
                "message": (
                    "At least one country trajectory lacks clear country-specific peak differentiation."
                ),
            }
        )

    no_match_count = len(
        [item for item in peak_event_matches if item.match_class == "no_credible_match"]
    )
    if no_match_count == 0 and not peak_event_matches:
        no_match_count = int(
            round(
                float(summary.get("event_registry_no_credible_match_ratio", 0.0) or 0.0)
                * float(summary.get("peak_event_match_record_count", 0) or 0)
            )
        )
    no_match_ratio = float(
        summary.get(
            "event_registry_no_credible_match_ratio",
            (
                len([item for item in peak_event_matches if item.match_class == "no_credible_match"])
                / float(len(peak_event_matches))
                if peak_event_matches
                else 0.0
            ),
        )
        or 0.0
    )
    if no_match_count > 0:
        warnings.append(
            {
                "code": "peak_no_credible_event_match",
                "severity": "warn" if no_match_ratio >= 0.35 else "info",
                "no_match_count": no_match_count,
                "no_match_ratio": round(no_match_ratio, 4),
                "message": (
                    "At least one detected peak has no credible event-registry match and requires analyst review."
                ),
            }
        )

    sparse_coverage_countries = sorted(
        {
            item.country
            for item in event_coverage
            if item.scope == "country" and item.coverage_band == "low"
        }
    )
    if sparse_coverage_countries:
        warnings.append(
            {
                "code": "event_coverage_sparse",
                "severity": "info",
                "countries": sparse_coverage_countries,
                "message": (
                    "Event-registry coverage is sparse for at least one country trajectory."
                ),
            }
        )

    multi_overlap_count = len(
        [item for item in peak_event_matches if item.match_class == "multi_event_overlap"]
    )
    if multi_overlap_count == 0 and not peak_event_matches:
        multi_overlap_count = int(
            round(
                float(summary.get("event_registry_multi_event_overlap_ratio", 0.0) or 0.0)
                * float(summary.get("peak_event_match_record_count", 0) or 0)
            )
        )
    if multi_overlap_count > 0:
        warnings.append(
            {
                "code": "multi_event_overlap_review",
                "severity": "info",
                "multi_event_overlap_count": multi_overlap_count,
                "message": (
                    "At least one peak overlaps multiple plausible events and needs manual analyst review."
                ),
            }
        )

    weak_grounding_countries = sorted(
        {
            item.country
            for item in country_event_alignment
            if item.alignment_maturity == "low" or item.credible_match_ratio < 0.4
        }
    )
    if weak_grounding_countries:
        warnings.append(
            {
                "code": "trajectory_weak_event_grounding",
                "severity": "warn",
                "countries": weak_grounding_countries,
                "message": (
                    "At least one country trajectory is weakly grounded in the current event registry."
                ),
            }
        )

    return warnings


def _write_compact_historical_daily_report(
    *,
    historical_records: list[HistoricalRollingRecord],
    out_path: Path,
) -> None:
    """
    Optional compact, human-readable daily report for historical trend.

    Traceability:
    - PSwR-031
    - PSyR-015
    """
    cluster_records = [
        record
        for record in historical_records
        if record.score_name == "cluster_score" and record.is_valid
    ]
    grouped: dict[tuple[str, date], list[HistoricalRollingRecord]] = {}
    for record in cluster_records:
        grouped.setdefault((record.country, record.date), []).append(record)

    lines = ["# Compact Historical Daily Report (UTF-8)", ""]
    for (country, point_date), values in sorted(grouped.items()):
        rendered = ", ".join(
            f"{record.cluster}={record.rolling_value:.2f} ({record.stage}/{record.trend})"
            for record in sorted(values, key=lambda item: cluster_order_index(item.cluster))
        )
        lines.append(f"- {country} {point_date.isoformat()}: {rendered}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8-sig")


def _write_reference_comparison_payload(
    *,
    run_dir: Path,
    status: str,
    current_run_info: dict,
) -> dict:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    payload = {
        "status": status,
        "baseline_label": "reference_run",
        "current_run": current_run_info,
        "baseline_run": {},
        "overview": {
            "items": 0,
            "zunehmend": 0,
            "rückläufig": 0,
            "stabil": 0,
            "kein_vergleich": 0,
        },
        "comparisons": [],
    }
    out_path = run_dir / "reference_comparison.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def _env_flag_enabled(value: str | None) -> bool:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def main() -> None:
    # Traceability:
    # - PSR-001
    # - PSR-003
    # - PSR-005
    # - PSR-006
    # - PSR-007
    # - PSR-008
    config = load_pipeline_config(Path("config/default.yaml"))
    ordered_countries = sorted(config.countries, key=country_order_index)
    historical_countries = sorted(config.historical.countries, key=country_order_index)
    run_timestamp = datetime.now(UTC).isoformat()
    run_date = datetime.now(UTC).date()

    run_dir = config.report_dir / "current_run"
    reference_run_dir = config.reference_dir / "current_reference"
    previous_cache_dir = config.report_dir / "_previous_run_cache"
    previous_summary_cache, previous_metadata_cache = _cache_previous_run(
        run_dir=run_dir,
        cache_dir=previous_cache_dir,
    )

    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    gdelt_records = load_gdelt_records(config.gdelt_path)
    ucdp_records = load_ucdp_records(config.ucdp_path)
    bridge_records = load_bridge_records(config.bridge_path)
    context_records = load_context_records(config.context_path)
    v31_observations: list[ObservationRecord] = []
    if config.v3_1.enabled:
        v31_observations = _load_v31_observations(config=config)

    source_availability = {
        "gdelt": bool(gdelt_records),
        "ucdp": bool(ucdp_records),
        "bridge": bool(bridge_records),
        "context": bool(context_records),
    }

    all_source_dates = [record.date for record in gdelt_records] + [record.date for record in ucdp_records]
    feature_date = max(all_source_dates) if all_source_dates else run_date

    tension_features = build_tension_features(
        gdelt_records,
        bridge_records,
        countries=ordered_countries,
    )
    escalation_features = build_escalation_features(
        ucdp_records,
        bridge_records,
        countries=ordered_countries,
    )
    vulnerability_features = build_vulnerability_features(
        context_records,
        countries=ordered_countries,
        feature_date=feature_date,
    )
    features = tension_features + escalation_features + vulnerability_features

    subscores = compute_subscores(features)
    cluster_scores = compute_cluster_scores(subscores)
    stage_thresholds = StageThresholds(
        low_max=config.scoring.stage_low_max,
        elevated_max=config.scoring.stage_elevated_max,
        high_max=config.scoring.stage_high_max,
    )

    raw_stage_by_cluster = derive_stage_by_cluster(
        cluster_scores,
        thresholds=stage_thresholds,
    )
    raw_trend_by_cluster = derive_trend_by_cluster(
        cluster_scores,
        short_days=config.short_days,
        recent_days=config.recent_days,
        delta_epsilon=config.scoring.trend_delta_epsilon,
    )
    raw_confidence_by_cluster = derive_confidence_by_cluster(
        subscores=subscores,
        cluster_scores=cluster_scores,
        expected_subscores_by_cluster={
            "tension": 3,
            "escalation": 4,
            "vulnerability": 3,
        },
        source_count_by_cluster=_derive_source_count_by_cluster(
            countries=ordered_countries,
            gdelt_records=gdelt_records,
            ucdp_records=ucdp_records,
            bridge_records=bridge_records,
            context_records=context_records,
        ),
    )

    historical_constant_clusters = {"vulnerability"}
    historical_records = build_historical_rolling_records(
        base_scores=subscores + cluster_scores,
        run_date=run_date,
        countries=historical_countries,
        horizon_days=config.historical.horizon_days,
        window_days=config.historical.window_days,
        min_valid_days=config.historical.min_valid_days,
        aggregation=config.historical.aggregation,
        delta_epsilon=config.scoring.trend_delta_epsilon,
        thresholds=stage_thresholds,
        constant_clusters=historical_constant_clusters,
    )
    latest_historical_points = latest_valid_points_by_series(historical_records)
    latest_historical_points_with_value = latest_points_with_value_by_series(historical_records)
    historical_points_on_run_date = points_on_date_by_series(
        historical_records,
        point_date=run_date,
    )

    latest_raw_cluster_scores = _latest_score_by_cluster(cluster_scores)
    snapshot_latest_cluster_scores: dict[tuple[str, str], ScoreRecord] = {}
    snapshot_stage_by_cluster: dict[tuple[str, str], str] = {}
    snapshot_trend_by_cluster: dict[tuple[str, str], str] = {}
    snapshot_confidence_by_cluster: dict[tuple[str, str], tuple[float, str]] = {}
    snapshot_source_by_cluster: dict[tuple[str, str], dict[str, object]] = {}

    for country in ordered_countries:
        for cluster in CLUSTER_ORDER:
            key = (country, cluster)
            historical_key = (country, cluster, "cluster_score")
            run_date_point = historical_points_on_run_date.get(historical_key)
            latest_valid_point = latest_historical_points.get(historical_key)
            latest_numeric_point = latest_historical_points_with_value.get(historical_key)

            source_mode = SNAPSHOT_SOURCE_RAW_FALLBACK
            historical_point: HistoricalRollingRecord | None = None
            if run_date_point is not None and run_date_point.is_valid and run_date_point.rolling_value is not None:
                source_mode = SNAPSHOT_SOURCE_VALID_ENDPOINT
                historical_point = run_date_point
            elif latest_valid_point is not None and latest_valid_point.rolling_value is not None:
                source_mode = SNAPSHOT_SOURCE_VALID_LAGGED
                historical_point = latest_valid_point
            elif latest_numeric_point is not None and latest_numeric_point.rolling_value is not None:
                source_mode = SNAPSHOT_SOURCE_NUMERIC_FALLBACK
                historical_point = latest_numeric_point

            if historical_point and historical_point.rolling_value is not None:
                confidence_score = historical_point.confidence_score
                confidence_level = historical_point.confidence_level
                confidence_penalty_applied = 0.0
                if source_mode == SNAPSHOT_SOURCE_NUMERIC_FALLBACK:
                    confidence_score, confidence_level, confidence_penalty_applied = (
                        apply_snapshot_fallback_penalty(
                            confidence_score=historical_point.confidence_score,
                            valid_days=historical_point.valid_days,
                            min_valid_days=historical_point.min_valid_days,
                        )
                    )

                snapshot_latest_cluster_scores[key] = ScoreRecord(
                    score_id=f"{country}-{historical_point.date.isoformat()}-{cluster}-snapshot-cluster-score",
                    country=country,
                    date=historical_point.date,
                    cluster=cluster,
                    subcluster="all",
                    score_name="cluster_score",
                    score_value=historical_point.rolling_value,
                )
                snapshot_stage_by_cluster[key] = historical_point.stage
                snapshot_trend_by_cluster[key] = historical_point.trend
                snapshot_confidence_by_cluster[key] = (
                    confidence_score,
                    confidence_level,
                )
                snapshot_source_by_cluster[key] = {
                    "source_mode": source_mode,
                    "source_date": historical_point.date.isoformat(),
                    "endpoint_is_valid": bool(run_date_point and run_date_point.is_valid),
                    "source_is_valid": historical_point.is_valid,
                    "valid_days": historical_point.valid_days,
                    "min_valid_days": historical_point.min_valid_days,
                    "coverage_ratio": historical_point.coverage_ratio,
                    "confidence_penalty_applied": confidence_penalty_applied,
                    "constant_cluster_assumption": cluster in historical_constant_clusters,
                }
                continue

            raw_score = latest_raw_cluster_scores.get(key)
            if raw_score is not None:
                snapshot_latest_cluster_scores[key] = raw_score
            snapshot_stage_by_cluster[key] = raw_stage_by_cluster.get(key, "niedrig")
            snapshot_trend_by_cluster[key] = raw_trend_by_cluster.get(key, "stabil")
            snapshot_confidence_by_cluster[key] = raw_confidence_by_cluster.get(key, (0.0, "niedrig"))
            snapshot_source_by_cluster[key] = {
                "source_mode": SNAPSHOT_SOURCE_RAW_FALLBACK,
                "source_date": None,
                "endpoint_is_valid": bool(run_date_point and run_date_point.is_valid),
                "source_is_valid": None,
                "valid_days": None,
                "min_valid_days": None,
                "coverage_ratio": None,
                "confidence_penalty_applied": 0.0,
                "constant_cluster_assumption": cluster in historical_constant_clusters,
            }

    assessments = _build_assessments(
        latest_cluster_scores=snapshot_latest_cluster_scores,
        stage_by_cluster=snapshot_stage_by_cluster,
        trend_by_cluster=snapshot_trend_by_cluster,
        confidence_by_cluster=snapshot_confidence_by_cluster,
    )

    snapshot_export_dir = run_dir / "exports" / "snapshot"
    historical_export_dir = run_dir / "exports" / "historical"
    fusion_export_dir = run_dir / "exports" / "fusion"
    legacy_export_dir = run_dir / "exports"
    write_csv_records(features, snapshot_export_dir / "features_export.csv")
    write_csv_records(subscores + cluster_scores, snapshot_export_dir / "scores_export.csv")
    summary_records = _assessment_records(
        assessments,
        snapshot_source_by_cluster=snapshot_source_by_cluster,
    )
    snapshot_summary_export_path = snapshot_export_dir / "summary_export.json"
    write_json_records(summary_records, snapshot_summary_export_path)
    _write_snapshot_status_file(
        out_dir=snapshot_export_dir,
        run_date=run_date,
        snapshot_source_by_cluster=snapshot_source_by_cluster,
    )

    # Legacy flat export paths remain as compatibility fallback for V2.1 artifacts.
    write_csv_records(features, legacy_export_dir / "features_export.csv")
    write_csv_records(subscores + cluster_scores, legacy_export_dir / "scores_export.csv")
    write_json_records(summary_records, legacy_export_dir / "summary_export.json")

    fusion_source_signals: list[FusionSourceSignalRecord] = []
    fusion_group_scores: list[FusionGroupScoreRecord] = []
    fusion_total_scores: list[FusionTotalScoreRecord] = []
    fusion_historical_source_signals: list[FusionHistoricalSourceSignalRecord] = []
    fusion_historical_group_scores: list[FusionHistoricalGroupScoreRecord] = []
    fusion_historical_total_scores: list[FusionHistoricalTotalScoreRecord] = []
    fusion_plausibility_warnings: list[dict[str, object]] = []
    validation_framework: dict[str, object] = {}
    validation_reference_episodes: list[ValidationReferenceEpisodeRecord] = []
    validation_episode_results: list[ValidationEpisodeResultRecord] = []
    validation_ranking_results: list[ValidationRankingRecord] = []
    validation_freshness_groups: list[ValidationFreshnessGroupRecord] = []
    validation_historical_responsiveness: list[ValidationHistoricalResponsivenessRecord] = []
    validation_layer_diagnostics: list[ValidationLayerDiagnosticRecord] = []
    validation_country_profiles: list[ValidationCountryProfileRecord] = []
    validation_peak_phases: list[ValidationCountryPeakPhaseRecord] = []
    validation_group_profiles: list[ValidationCountryGroupProfileRecord] = []
    validation_ranking_trajectory: list[ValidationRankingTrajectoryRecord] = []
    validation_event_registry: list[ValidationEventRegistryRecord] = []
    validation_event_markers: list[ValidationEventMarkerRecord] = []
    validation_peak_attribution: list[ValidationPeakAttributionRecord] = []
    validation_peak_event_support: list[ValidationPeakEventSupportRecord] = []
    validation_peak_event_matches: list[ValidationPeakEventMatchRecord] = []
    validation_event_coverage_summary: list[ValidationEventCoverageSummaryRecord] = []
    validation_country_event_alignment: list[ValidationCountryEventAlignmentRecord] = []
    validation_trajectory_profiles: list[ValidationTrajectoryProfileRecord] = []
    validation_peak_synchronization: list[ValidationGlobalPeakSynchronizationRecord] = []
    validation_peak_attribution_summary: dict[str, object] = {}
    validation_event_alignment_summary: dict[str, object] = {}
    validation_summary: dict[str, object] = {"status": "not_enabled"}
    if config.v3_1.enabled:
        dynamic_groups = ["event", "narrative", "governance", "shock", "displacement"]
        fusion_source_signals = build_fusion_source_signals(
            observations=v31_observations,
            countries=ordered_countries,
            run_date=run_date,
            target_period_days=config.v3_1.fusion.target_period_days,
            source_to_group=config.v3_1.fusion.source_to_group,
        )
        fusion_group_scores = build_fusion_group_scores(
            signals=fusion_source_signals,
            countries=ordered_countries,
            groups=config.v3_1.fusion.groups,
            source_weights=config.v3_1.fusion.source_weights,
            max_age_days=config.v3_1.fusion.confidence.max_age_days,
            coverage_weight=config.v3_1.fusion.confidence.coverage_weight,
            recency_weight=config.v3_1.fusion.confidence.recency_weight,
            completeness_weight=config.v3_1.fusion.confidence.completeness_weight,
            consistency_weight=config.v3_1.fusion.confidence.consistency_weight,
            event_stale_after_days=config.v3_1.fusion.calibration.event_stale_after_days,
            event_decay_half_life_days=config.v3_1.fusion.calibration.event_decay_half_life_days,
            event_min_decay_factor=config.v3_1.fusion.calibration.event_min_decay_factor,
            freshness_model=config.v3_1.fusion.calibration.freshness_model,
            event_fresh_boost_factor=config.v3_1.fusion.calibration.event_fresh_boost_factor,
        )
        fusion_total_scores = build_fusion_total_scores(
            group_records=fusion_group_scores,
            countries=ordered_countries,
            groups=config.v3_1.fusion.groups,
            group_weights=config.v3_1.fusion.group_weights,
            bonus_enabled=config.v3_1.fusion.bonus_enabled,
            bonus_threshold=config.v3_1.fusion.bonus_threshold,
            bonus_points=config.v3_1.fusion.bonus_points,
            bonus_min_groups=config.v3_1.fusion.bonus_min_groups,
        )
        if config.v3_1.fusion.historical.enabled:
            (
                fusion_historical_source_signals,
                fusion_historical_group_scores,
                fusion_historical_total_scores,
            ) = build_historical_fusion_scores(
                observations=v31_observations,
                countries=ordered_countries,
                run_date=run_date,
                horizon_months=config.v3_1.fusion.historical.horizon_months,
                groups=config.v3_1.fusion.groups,
                source_to_group=config.v3_1.fusion.source_to_group,
                source_weights=config.v3_1.fusion.source_weights,
                group_weights=config.v3_1.fusion.group_weights,
                bonus_enabled=config.v3_1.fusion.bonus_enabled,
                bonus_threshold=config.v3_1.fusion.bonus_threshold,
                bonus_points=config.v3_1.fusion.bonus_points,
                bonus_min_groups=config.v3_1.fusion.bonus_min_groups,
                max_age_days=config.v3_1.fusion.confidence.max_age_days,
                coverage_weight=config.v3_1.fusion.confidence.coverage_weight,
                recency_weight=config.v3_1.fusion.confidence.recency_weight,
                completeness_weight=config.v3_1.fusion.confidence.completeness_weight,
                consistency_weight=config.v3_1.fusion.confidence.consistency_weight,
                low_max=config.v3_1.fusion.calibration.stage_low_max,
                elevated_max=config.v3_1.fusion.calibration.stage_elevated_max,
                high_max=config.v3_1.fusion.calibration.stage_high_max,
                delta_epsilon=config.v3_1.fusion.calibration.trend_delta_epsilon,
                event_stale_after_days=config.v3_1.fusion.calibration.event_stale_after_days,
                event_decay_half_life_days=config.v3_1.fusion.calibration.event_decay_half_life_days,
                event_min_decay_factor=config.v3_1.fusion.calibration.event_min_decay_factor,
                limited_coverage_threshold=config.v3_1.fusion.calibration.limited_coverage_threshold,
                reduced_coverage_threshold=config.v3_1.fusion.calibration.reduced_coverage_threshold,
                freshness_model=config.v3_1.fusion.calibration.freshness_model,
                event_fresh_boost_factor=config.v3_1.fusion.calibration.event_fresh_boost_factor,
            )

        reference_episodes_path = config.v3_1.fusion.calibration.reference_episodes_path
        if not reference_episodes_path.exists():
            raise FileNotFoundError(
                "validation reference episodes file missing: "
                f"{reference_episodes_path.as_posix()}"
            )
        validation_reference_episodes = load_validation_reference_episodes(reference_episodes_path)
        validation_episode_results = compute_validation_episode_results(
            reference_episodes=validation_reference_episodes,
            historical_total_records=fusion_historical_total_scores,
            historical_group_records=fusion_historical_group_scores,
            group_activation_threshold=config.v3_1.fusion.calibration.group_activation_threshold,
        )
        (
            validation_ranking_results,
            ranking_fit_score,
            ranking_plausible,
        ) = compute_validation_ranking(
            total_records=fusion_total_scores,
            expected_ranking=config.v3_1.fusion.calibration.expected_ranking,
        )
        validation_freshness_groups = compute_snapshot_freshness_groups(
            source_signals=fusion_source_signals,
            group_records=fusion_group_scores,
            group_weights=config.v3_1.fusion.group_weights,
            freshness_model=config.v3_1.fusion.calibration.freshness_model,
            event_fresh_boost_factor=config.v3_1.fusion.calibration.event_fresh_boost_factor,
        )
        validation_historical_responsiveness = compute_historical_responsiveness(
            historical_total_records=fusion_historical_total_scores,
            delta_threshold=config.v3_1.fusion.calibration.responsiveness_delta_threshold,
        )
        validation_layer_diagnostics = compute_layer_diagnostics(
            group_records=fusion_group_scores,
            total_records=fusion_total_scores,
            source_signals=fusion_source_signals,
            group_weights=config.v3_1.fusion.group_weights,
            group_activation_threshold=config.v3_1.fusion.calibration.group_activation_threshold,
            dominance_share_threshold=config.v3_1.fusion.calibration.dominance_share_threshold,
            market_food_dominance_threshold=config.v3_1.fusion.calibration.market_food_dominance_threshold,
            structural_outlier_gap=config.v3_1.fusion.calibration.structural_outlier_gap,
            event_stale_days=config.v3_1.fusion.calibration.event_stale_warning_days,
            freshness_model=config.v3_1.fusion.calibration.freshness_model,
            event_fresh_boost_factor=config.v3_1.fusion.calibration.event_fresh_boost_factor,
            dynamic_layer_readiness_min_share=config.v3_1.fusion.calibration.dynamic_layer_readiness_min_share,
            dynamic_groups=dynamic_groups,
        )
        (
            validation_country_profiles,
            validation_peak_phases,
            validation_group_profiles,
            validation_ranking_trajectory,
        ) = compute_country_profile_comparison(
            total_records=fusion_total_scores,
            historical_total_records=fusion_historical_total_scores,
            historical_group_records=fusion_historical_group_scores,
            layer_diagnostics=validation_layer_diagnostics,
            group_weights=config.v3_1.fusion.group_weights,
            group_activation_threshold=config.v3_1.fusion.calibration.group_activation_threshold,
            high_stage_threshold=config.v3_1.fusion.calibration.stage_high_max,
            top_peak_count=3,
            peak_prominence_min=config.v3_1.fusion.calibration.peak_prominence_min,
            peak_min_rise=config.v3_1.fusion.calibration.peak_min_rise,
            peak_min_fall=config.v3_1.fusion.calibration.peak_min_fall,
            peak_min_separation_periods=config.v3_1.fusion.calibration.peak_min_separation_periods,
            peak_quality_floor=config.v3_1.fusion.calibration.peak_quality_floor,
        )
        validation_event_markers = load_event_marker_registry(
            config.v3_1.fusion.calibration.event_marker_registry_path
        )
        (
            validation_peak_attribution,
            validation_peak_event_support,
            validation_trajectory_profiles,
            validation_peak_synchronization,
            validation_peak_attribution_summary,
        ) = compute_peak_attribution(
            country_profile_records=validation_country_profiles,
            peak_phase_records=validation_peak_phases,
            historical_total_records=fusion_historical_total_scores,
            historical_group_records=fusion_historical_group_scores,
            layer_diagnostics=validation_layer_diagnostics,
            group_weights=config.v3_1.fusion.group_weights,
            event_markers=validation_event_markers,
            support_group_min_share=config.v3_1.fusion.calibration.peak_support_group_min_share,
            country_specific_share_threshold=config.v3_1.fusion.calibration.peak_country_specific_share_threshold,
            global_share_warning_threshold=config.v3_1.fusion.calibration.peak_global_share_warning_threshold,
            model_driven_global_share_threshold=config.v3_1.fusion.calibration.peak_model_driven_global_share_threshold,
            single_group_dominance_threshold=config.v3_1.fusion.calibration.peak_single_group_dominance_threshold,
            event_support_weak_threshold=config.v3_1.fusion.calibration.peak_event_support_weak_threshold,
            event_support_strong_threshold=config.v3_1.fusion.calibration.peak_event_support_strong_threshold,
            peak_prominence_min=config.v3_1.fusion.calibration.peak_prominence_min,
            peak_min_rise=config.v3_1.fusion.calibration.peak_min_rise,
            peak_min_fall=config.v3_1.fusion.calibration.peak_min_fall,
            peak_min_separation_periods=config.v3_1.fusion.calibration.peak_min_separation_periods,
            peak_quality_floor=config.v3_1.fusion.calibration.peak_quality_floor,
        )
        validation_event_registry = load_event_registry(
            config.v3_1.fusion.calibration.event_registry_path
        )
        (
            validation_peak_event_matches,
            validation_event_coverage_summary,
            validation_country_event_alignment,
            validation_event_alignment_summary,
        ) = compute_peak_event_alignment(
            peak_attribution_records=validation_peak_attribution,
            trajectory_profile_records=validation_trajectory_profiles,
            event_registry_records=validation_event_registry,
            temporal_distance_days=config.v3_1.fusion.calibration.event_alignment_temporal_distance_days,
            direct_match_threshold=config.v3_1.fusion.calibration.event_alignment_direct_match_threshold,
            context_match_threshold=config.v3_1.fusion.calibration.event_alignment_context_match_threshold,
            weak_match_threshold=config.v3_1.fusion.calibration.event_alignment_weak_match_threshold,
            multi_overlap_min_events=config.v3_1.fusion.calibration.event_alignment_multi_overlap_min_events,
        )
        validation_framework = build_validation_framework(
            countries=ordered_countries,
            reference_episodes_path=reference_episodes_path,
            reference_episode_count=len(validation_reference_episodes),
            expected_ranking=config.v3_1.fusion.calibration.expected_ranking,
            group_weights=config.v3_1.fusion.group_weights,
            source_weights=config.v3_1.fusion.source_weights,
            fusion_stage_low_max=config.v3_1.fusion.calibration.stage_low_max,
            fusion_stage_elevated_max=config.v3_1.fusion.calibration.stage_elevated_max,
            fusion_stage_high_max=config.v3_1.fusion.calibration.stage_high_max,
            fusion_trend_delta_epsilon=config.v3_1.fusion.calibration.trend_delta_epsilon,
            event_stale_after_days=config.v3_1.fusion.calibration.event_stale_after_days,
            event_decay_half_life_days=config.v3_1.fusion.calibration.event_decay_half_life_days,
            event_min_decay_factor=config.v3_1.fusion.calibration.event_min_decay_factor,
            event_fresh_boost_factor=config.v3_1.fusion.calibration.event_fresh_boost_factor,
            freshness_model=config.v3_1.fusion.calibration.freshness_model,
            freshness_min_fresh_contribution_share=config.v3_1.fusion.calibration.freshness_min_fresh_contribution_share,
            freshness_max_stale_contribution_share=config.v3_1.fusion.calibration.freshness_max_stale_contribution_share,
            dynamic_layer_readiness_min_share=config.v3_1.fusion.calibration.dynamic_layer_readiness_min_share,
            responsiveness_delta_threshold=config.v3_1.fusion.calibration.responsiveness_delta_threshold,
            responsiveness_lag_tolerance_months=config.v3_1.fusion.calibration.responsiveness_lag_tolerance_months,
            dynamic_groups=dynamic_groups,
            group_activation_threshold=config.v3_1.fusion.calibration.group_activation_threshold,
            dominance_share_threshold=config.v3_1.fusion.calibration.dominance_share_threshold,
            structural_outlier_gap=config.v3_1.fusion.calibration.structural_outlier_gap,
            peak_prominence_min=config.v3_1.fusion.calibration.peak_prominence_min,
            peak_min_rise=config.v3_1.fusion.calibration.peak_min_rise,
            peak_min_fall=config.v3_1.fusion.calibration.peak_min_fall,
            peak_min_separation_periods=config.v3_1.fusion.calibration.peak_min_separation_periods,
            peak_quality_floor=config.v3_1.fusion.calibration.peak_quality_floor,
            peak_support_group_min_share=config.v3_1.fusion.calibration.peak_support_group_min_share,
            peak_country_specific_share_threshold=config.v3_1.fusion.calibration.peak_country_specific_share_threshold,
            peak_global_share_warning_threshold=config.v3_1.fusion.calibration.peak_global_share_warning_threshold,
            peak_model_driven_global_share_threshold=config.v3_1.fusion.calibration.peak_model_driven_global_share_threshold,
            peak_single_group_dominance_threshold=config.v3_1.fusion.calibration.peak_single_group_dominance_threshold,
            peak_event_support_weak_threshold=config.v3_1.fusion.calibration.peak_event_support_weak_threshold,
            peak_event_support_strong_threshold=config.v3_1.fusion.calibration.peak_event_support_strong_threshold,
            event_alignment_temporal_distance_days=config.v3_1.fusion.calibration.event_alignment_temporal_distance_days,
            event_alignment_direct_match_threshold=config.v3_1.fusion.calibration.event_alignment_direct_match_threshold,
            event_alignment_context_match_threshold=config.v3_1.fusion.calibration.event_alignment_context_match_threshold,
            event_alignment_weak_match_threshold=config.v3_1.fusion.calibration.event_alignment_weak_match_threshold,
            event_alignment_multi_overlap_min_events=config.v3_1.fusion.calibration.event_alignment_multi_overlap_min_events,
            event_registry_path=config.v3_1.fusion.calibration.event_registry_path,
            event_marker_registry_path=config.v3_1.fusion.calibration.event_marker_registry_path,
        )
        validation_summary = build_validation_summary(
            episode_results=validation_episode_results,
            ranking_results=validation_ranking_results,
            ranking_fit_score=ranking_fit_score,
            ranking_plausible=ranking_plausible,
            layer_diagnostics=validation_layer_diagnostics,
            freshness_group_records=validation_freshness_groups,
            historical_responsiveness_records=validation_historical_responsiveness,
            country_profile_records=validation_country_profiles,
            peak_phase_records=validation_peak_phases,
            group_profile_records=validation_group_profiles,
            ranking_trajectory_records=validation_ranking_trajectory,
            peak_attribution_records=validation_peak_attribution,
            peak_event_support_records=validation_peak_event_support,
            peak_event_match_records=validation_peak_event_matches,
            event_coverage_summary_records=validation_event_coverage_summary,
            country_event_alignment_records=validation_country_event_alignment,
            trajectory_profile_records=validation_trajectory_profiles,
            peak_synchronization_records=validation_peak_synchronization,
            peak_attribution_summary=validation_peak_attribution_summary,
            event_alignment_summary=validation_event_alignment_summary,
            freshness_min_fresh_contribution_share=config.v3_1.fusion.calibration.freshness_min_fresh_contribution_share,
            freshness_max_stale_contribution_share=config.v3_1.fusion.calibration.freshness_max_stale_contribution_share,
            dynamic_layer_readiness_min_share=config.v3_1.fusion.calibration.dynamic_layer_readiness_min_share,
            responsiveness_lag_tolerance_months=config.v3_1.fusion.calibration.responsiveness_lag_tolerance_months,
        )
    write_csv_records(v31_observations, fusion_export_dir / "observations.csv")
    write_csv_records(fusion_source_signals, fusion_export_dir / "source_signals.csv")
    write_csv_records(fusion_group_scores, fusion_export_dir / "group_scores.csv")
    write_json_records(fusion_total_scores, fusion_export_dir / "fusion_total_scores.json")
    write_csv_records(
        fusion_historical_source_signals,
        fusion_export_dir / "historical_source_signals.csv",
    )
    write_csv_records(
        fusion_historical_group_scores,
        fusion_export_dir / "historical_group_scores.csv",
    )
    write_csv_records(
        fusion_historical_total_scores,
        fusion_export_dir / "historical_total_scores.csv",
    )
    write_json_records([validation_framework], fusion_export_dir / "validation_framework.json")
    write_csv_records(
        validation_reference_episodes,
        fusion_export_dir / "validation_reference_episodes.csv",
    )
    write_csv_records(
        validation_episode_results,
        fusion_export_dir / "validation_episode_review.csv",
    )
    write_csv_records(
        validation_ranking_results,
        fusion_export_dir / "validation_country_ranking.csv",
    )
    write_csv_records(
        validation_layer_diagnostics,
        fusion_export_dir / "validation_layer_diagnostics.csv",
    )
    write_csv_records(
        validation_freshness_groups,
        fusion_export_dir / "validation_freshness_groups.csv",
    )
    write_csv_records(
        validation_historical_responsiveness,
        fusion_export_dir / "validation_historical_responsiveness.csv",
    )
    write_csv_records(
        validation_country_profiles,
        fusion_export_dir / "validation_country_profiles.csv",
    )
    write_csv_records(
        validation_peak_phases,
        fusion_export_dir / "validation_peak_phases.csv",
    )
    write_csv_records(
        validation_group_profiles,
        fusion_export_dir / "validation_group_profiles.csv",
    )
    write_csv_records(
        validation_ranking_trajectory,
        fusion_export_dir / "validation_ranking_trajectory.csv",
    )
    write_csv_records(
        validation_event_registry,
        fusion_export_dir / "event_registry.csv",
    )
    write_csv_records(
        validation_event_markers,
        fusion_export_dir / "event_marker_registry.csv",
    )
    write_csv_records(
        validation_peak_attribution,
        fusion_export_dir / "peak_attribution.csv",
    )
    write_csv_records(
        validation_peak_event_support,
        fusion_export_dir / "peak_event_support.csv",
    )
    write_csv_records(
        validation_peak_event_matches,
        fusion_export_dir / "peak_event_matches.csv",
    )
    write_csv_records(
        validation_event_coverage_summary,
        fusion_export_dir / "event_coverage_summary.csv",
    )
    write_csv_records(
        validation_country_event_alignment,
        fusion_export_dir / "country_event_alignment.csv",
    )
    write_csv_records(
        validation_trajectory_profiles,
        fusion_export_dir / "trajectory_profiles.csv",
    )
    write_csv_records(
        validation_peak_synchronization,
        fusion_export_dir / "global_peak_synchronization.csv",
    )
    write_json_records(
        [validation_event_alignment_summary],
        fusion_export_dir / "event_alignment_summary.json",
    )
    _write_event_alignment_review_file(
        out_path=fusion_export_dir / "event_alignment_review.md",
        summary=validation_event_alignment_summary,
        coverage_records=validation_event_coverage_summary,
        country_alignment_records=validation_country_event_alignment,
        peak_event_matches=validation_peak_event_matches,
    )
    write_json_records([validation_summary], fusion_export_dir / "validation_summary.json")
    fusion_plausibility_warnings = _build_fusion_plausibility_warnings(
        source_signals=fusion_source_signals,
        group_records=fusion_group_scores,
        total_records=fusion_total_scores,
        historical_total_records=fusion_historical_total_scores,
        event_stale_warning_days=config.v3_1.fusion.calibration.event_stale_warning_days,
        dominance_share_threshold=config.v3_1.fusion.calibration.dominance_share_threshold,
        validation_summary=validation_summary,
        validation_layer_diagnostics=validation_layer_diagnostics,
        validation_peak_attribution=validation_peak_attribution,
        validation_trajectory_profiles=validation_trajectory_profiles,
        validation_peak_event_matches=validation_peak_event_matches,
        validation_event_coverage=validation_event_coverage_summary,
        validation_country_event_alignment=validation_country_event_alignment,
    )
    _write_fusion_status_file(
        out_dir=fusion_export_dir,
        enabled=config.v3_1.enabled,
        group_records=fusion_group_scores,
        total_records=fusion_total_scores,
        historical_group_records=fusion_historical_group_scores,
        historical_total_records=fusion_historical_total_scores,
        plausibility_warnings=fusion_plausibility_warnings,
        validation_summary=validation_summary,
    )

    snapshot_plots_dir = run_dir / "plots" / "snapshot"
    snapshot_plot_paths = save_cluster_score_plots(
        cluster_scores=cluster_scores,
        out_dir=snapshot_plots_dir,
    )
    fusion_plot_paths = save_fusion_group_plots(
        group_scores=fusion_group_scores,
        out_dir=run_dir / "plots" / "fusion",
    )
    fusion_historical_group_plot_paths = save_fusion_historical_group_plots(
        historical_group_scores=fusion_historical_group_scores,
        out_dir=run_dir / "plots" / "fusion",
    )
    fusion_historical_total_plot_paths = save_fusion_historical_total_plots(
        historical_total_scores=fusion_historical_total_scores,
        out_dir=run_dir / "plots" / "fusion",
    )
    v43_country_profile_plot_paths = save_v43_country_profile_plots(
        historical_total_scores=fusion_historical_total_scores,
        historical_group_scores=fusion_historical_group_scores,
        out_dir=run_dir / "plots" / "fusion",
        top_peak_count=3,
    )
    v43_multicountry_plot_paths: list[Path] = []
    v43_multicountry_plot_paths.extend(
        save_v43_multicountry_total_plot(
            historical_total_scores=fusion_historical_total_scores,
            out_dir=run_dir / "plots" / "fusion",
        )
    )
    v43_multicountry_plot_paths.extend(
        save_v43_ranking_trajectory_plot(
            historical_total_scores=fusion_historical_total_scores,
            out_dir=run_dir / "plots" / "fusion",
        )
    )
    v431_country_peak_plot_paths = save_v431_country_peak_attribution_plots(
        historical_total_scores=fusion_historical_total_scores,
        peak_attribution_records=validation_peak_attribution,
        out_dir=run_dir / "plots" / "fusion",
    )
    v431_synchronization_plot_paths = save_v431_peak_synchronization_plot(
        synchronization_records=validation_peak_synchronization,
        out_dir=run_dir / "plots" / "fusion",
    )
    v432_country_event_alignment_plot_paths = save_v432_country_event_alignment_plots(
        historical_total_scores=fusion_historical_total_scores,
        peak_event_match_records=validation_peak_event_matches,
        event_registry_records=validation_event_registry,
        out_dir=run_dir / "plots" / "fusion",
    )
    _validate_snapshot_plot_coverage(plot_paths=snapshot_plot_paths, countries=ordered_countries)

    expected_subscores_total = len(ordered_countries) * (3 + 4 + 3)
    latest_subscore_date = max(score.date for score in subscores) if subscores else feature_date
    actual_subscores_latest = len([score for score in subscores if score.date == latest_subscore_date])
    data_quality_score = round(
        min(100.0, 100.0 * (actual_subscores_latest / max(1, expected_subscores_total))),
        2,
    )
    consistency_score = round(
        mean(score for score, _ in raw_confidence_by_cluster.values()) if raw_confidence_by_cluster else 0.0,
        2,
    )

    outputs_complete = _required_outputs_present(
        features_path=snapshot_export_dir / "features_export.csv",
        scores_path=snapshot_export_dir / "scores_export.csv",
        summary_path=snapshot_summary_export_path,
        plot_paths=snapshot_plot_paths,
    )
    proposed_run_status = propose_run_status(
        required_source_availability=source_availability,
        data_quality_score=data_quality_score,
        consistency_score=consistency_score,
        outputs_complete=outputs_complete,
    )
    status_override = validate_status_override(os.environ.get("PROTO_RUN_STATUS_OVERRIDE"))
    effective_run_status = status_override or proposed_run_status
    run_status_overridden = status_override is not None
    force_reference_refresh = _env_flag_enabled(os.environ.get("PROTO_FORCE_REFERENCE_REFRESH"))

    historical_enabled = effective_run_status in {STATUS_SUCCESS, STATUS_LIMITED}
    historical_limited_marker = effective_run_status == STATUS_LIMITED
    historical_cluster_plot_paths: list[Path] = []
    historical_subscore_plot_paths: list[Path] = []
    historical_review_candidates: list[HistoricalReviewCandidateRecord] = []
    if historical_enabled:
        write_csv_records(historical_records, historical_export_dir / "historical_timeseries.csv")
        historical_review_candidates = build_historical_review_candidates(
            records=historical_records,
            snapshot_source_by_cluster=snapshot_source_by_cluster,
            baseline_clusters=historical_constant_clusters,
            include_baseline_clusters=False,
        )
        write_csv_records(historical_review_candidates, historical_export_dir / "review_candidates.csv")
        write_json_records(
            [asdict(item) for item in historical_review_candidates],
            historical_export_dir / "review_candidates.json",
        )
        if config.historical.compact_daily_report:
            _write_compact_historical_daily_report(
                historical_records=historical_records,
                out_path=historical_export_dir / "compact_daily_report.md",
            )
        historical_cluster_plot_paths = save_historical_cluster_plots(
            historical_records=historical_records,
            out_dir=run_dir / "plots" / "historical" / "clusters",
        )
        historical_subscore_plot_paths = save_historical_subscore_plots(
            historical_records=historical_records,
            out_dir=run_dir / "plots" / "historical" / "subscores",
        )
        _write_historical_status_file(
            out_dir=historical_export_dir,
            status="ok",
            historical_limited_marker=historical_limited_marker,
            enabled=True,
            constant_clusters=historical_constant_clusters,
        )
    else:
        _write_historical_status_file(
            out_dir=historical_export_dir,
            status="skipped_unbrauchbar",
            historical_limited_marker=False,
            enabled=False,
            constant_clusters=historical_constant_clusters,
        )

    metadata = RunMetadata(
        run_timestamp=run_timestamp,
        countries=ordered_countries,
        short_days=config.short_days,
        recent_days=config.recent_days,
        baseline_days=config.baseline_days,
        query_version=config.query_version,
        scoring_version=config.scoring_version,
        bridge_file_version=config.bridge_file_version,
        context_table_version=config.context_table_version,
        proposed_run_status=proposed_run_status,
        run_status=effective_run_status,
        run_status_overridden=run_status_overridden,
    )
    metadata_path = run_dir / "run_metadata.json"
    write_run_metadata(metadata, metadata_path)
    (run_dir / "run_status.txt").write_text(effective_run_status, encoding="utf-8")

    current_run_info = {
        "run_timestamp": run_timestamp,
        "countries": ordered_countries,
        "short_days": config.short_days,
        "recent_days": config.recent_days,
        "baseline_days": config.baseline_days,
        "query_version": config.query_version,
        "scoring_version": config.scoring_version,
        "bridge_file_version": config.bridge_file_version,
        "context_table_version": config.context_table_version,
        "metadata_schema_version": metadata.metadata_schema_version,
        "proposed_run_status": proposed_run_status,
        "effective_run_status": effective_run_status,
        "run_status_overridden": run_status_overridden,
        "historical_horizon_days": config.historical.horizon_days,
        "historical_window_days": config.historical.window_days,
        "historical_min_valid_days": config.historical.min_valid_days,
        "historical_aggregation": config.historical.aggregation,
    }

    run_comparison_payload = write_run_comparison(
        current_summary_path=snapshot_summary_export_path,
        baseline_summary_path=previous_summary_cache,
        out_path=run_dir / "run_comparison.json",
        baseline_label="previous_run",
        current_run_info=current_run_info,
        baseline_metadata_path=previous_metadata_cache,
    )

    reference_summary_candidates = [
        reference_run_dir / "exports" / "snapshot" / "summary_export.json",
        reference_run_dir / "exports" / "summary_export.json",
    ]
    reference_summary_path = next((path for path in reference_summary_candidates if path.exists()), None)
    reference_metadata_path = ensure_reference_metadata_schema(reference_run_dir)
    had_reference_before = reference_summary_path is not None

    reference_action = freeze_reference_run_if_absent(
        current_run_dir=run_dir,
        reference_dir=reference_run_dir,
        proposed_run_status=proposed_run_status,
        effective_run_status=effective_run_status,
        run_status_overridden=run_status_overridden,
        force_refresh=force_reference_refresh,
    )

    if reference_action == "created":
        reference_comparison_payload = _write_reference_comparison_payload(
            run_dir=run_dir,
            status="reference_created_from_current_run",
            current_run_info=current_run_info,
        )
    elif reference_action == "refreshed_forced":
        reference_comparison_payload = _write_reference_comparison_payload(
            run_dir=run_dir,
            status="reference_refreshed_from_current_run",
            current_run_info=current_run_info,
        )
    elif reference_action == "migrated_legacy_to_current":
        reference_comparison_payload = _write_reference_comparison_payload(
            run_dir=run_dir,
            status="reference_migrated_to_current_run",
            current_run_info=current_run_info,
        )
    elif had_reference_before and reference_summary_path is not None:
        reference_comparison_payload = write_run_comparison(
            current_summary_path=snapshot_summary_export_path,
            baseline_summary_path=reference_summary_path,
            out_path=run_dir / "reference_comparison.json",
            baseline_label="reference_run",
            current_run_info=current_run_info,
            baseline_metadata_path=reference_metadata_path,
        )
    else:
        reference_comparison_payload = _write_reference_comparison_payload(
            run_dir=run_dir,
            status="no_reference_run",
            current_run_info=current_run_info,
        )

    snapshot_context = build_snapshot_context_by_cluster(historical_records)
    relative_snapshot_plot_paths = [Path("plots/snapshot") / path.name for path in snapshot_plot_paths]
    relative_historical_cluster_plot_paths = [
        Path("plots/historical/clusters") / path.name for path in historical_cluster_plot_paths
    ]
    relative_historical_subscore_plot_paths = [
        Path("plots/historical/subscores") / path.name for path in historical_subscore_plot_paths
    ]
    relative_fusion_plot_paths = [Path("plots/fusion") / path.name for path in fusion_plot_paths]
    relative_fusion_historical_group_plot_paths = [
        Path("plots/fusion") / path.name for path in fusion_historical_group_plot_paths
    ]
    relative_fusion_historical_total_plot_paths = [
        Path("plots/fusion") / path.name for path in fusion_historical_total_plot_paths
    ]
    relative_v43_country_profile_plot_paths = [
        Path("plots/fusion") / path.name for path in v43_country_profile_plot_paths
    ]
    relative_v43_multicountry_plot_paths = [
        Path("plots/fusion") / path.name for path in v43_multicountry_plot_paths
    ]
    relative_v431_country_peak_plot_paths = [
        Path("plots/fusion") / path.name for path in v431_country_peak_plot_paths
    ]
    relative_v431_synchronization_plot_paths = [
        Path("plots/fusion") / path.name for path in v431_synchronization_plot_paths
    ]
    relative_v432_country_event_alignment_plot_paths = [
        Path("plots/fusion") / path.name for path in v432_country_event_alignment_plot_paths
    ]

    grouped_snapshot_plot_paths = _plots_by_country(
        plot_paths=relative_snapshot_plot_paths,
        countries=ordered_countries,
    )
    grouped_historical_cluster_plot_paths = _plots_by_country(
        plot_paths=relative_historical_cluster_plot_paths,
        countries=ordered_countries,
    )
    grouped_historical_subscore_plot_paths = _plots_by_country(
        plot_paths=relative_historical_subscore_plot_paths,
        countries=ordered_countries,
    )
    grouped_fusion_plot_paths = _plots_by_country(
        plot_paths=relative_fusion_plot_paths,
        countries=ordered_countries,
    )
    grouped_fusion_historical_group_plot_paths = _plots_by_country(
        plot_paths=relative_fusion_historical_group_plot_paths,
        countries=ordered_countries,
    )
    grouped_fusion_historical_total_plot_paths = _plots_by_country(
        plot_paths=relative_fusion_historical_total_plot_paths,
        countries=ordered_countries,
    )
    grouped_v43_country_profile_plot_paths = _plots_by_country(
        plot_paths=relative_v43_country_profile_plot_paths,
        countries=ordered_countries,
    )
    grouped_v431_country_peak_plot_paths = _plots_by_country(
        plot_paths=relative_v431_country_peak_plot_paths,
        countries=ordered_countries,
    )
    grouped_v432_country_event_alignment_plot_paths = _plots_by_country(
        plot_paths=relative_v432_country_event_alignment_plot_paths,
        countries=ordered_countries,
    )

    handout_text = build_handout_markdown(
        run_timestamp=run_timestamp,
        countries=ordered_countries,
        snapshot_assessments=assessments,
        snapshot_source_by_cluster=snapshot_source_by_cluster,
        snapshot_context=snapshot_context,
        historical_records=historical_records if historical_enabled else [],
        historical_review_candidates=historical_review_candidates[:5],
        fusion_group_scores=fusion_group_scores,
        fusion_total_scores=fusion_total_scores,
        fusion_historical_group_scores=fusion_historical_group_scores,
        fusion_historical_total_scores=fusion_historical_total_scores,
        fusion_plausibility_warnings=fusion_plausibility_warnings,
        fusion_validation_summary=validation_summary,
        fusion_validation_diagnostics=[asdict(item) for item in validation_layer_diagnostics],
        fusion_validation_country_profiles=[asdict(item) for item in validation_country_profiles],
        fusion_validation_peak_phases=[asdict(item) for item in validation_peak_phases],
        fusion_validation_group_profiles=[asdict(item) for item in validation_group_profiles],
        fusion_validation_ranking_trajectory=[asdict(item) for item in validation_ranking_trajectory],
        fusion_peak_attribution=[asdict(item) for item in validation_peak_attribution],
        fusion_peak_event_support=[asdict(item) for item in validation_peak_event_support],
        fusion_peak_event_matches=[asdict(item) for item in validation_peak_event_matches],
        fusion_event_registry=[asdict(item) for item in validation_event_registry],
        fusion_event_coverage_summary=[asdict(item) for item in validation_event_coverage_summary],
        fusion_country_event_alignment=[asdict(item) for item in validation_country_event_alignment],
        fusion_trajectory_profiles=[asdict(item) for item in validation_trajectory_profiles],
        fusion_peak_synchronization=[asdict(item) for item in validation_peak_synchronization],
        snapshot_plot_paths=relative_snapshot_plot_paths,
        snapshot_plot_paths_by_country=grouped_snapshot_plot_paths,
        historical_cluster_plot_paths=relative_historical_cluster_plot_paths,
        historical_subscore_plot_paths=relative_historical_subscore_plot_paths,
        fusion_plot_paths=relative_fusion_plot_paths,
        fusion_plot_paths_by_country=grouped_fusion_plot_paths,
        fusion_historical_group_plot_paths=relative_fusion_historical_group_plot_paths,
        fusion_historical_total_plot_paths=relative_fusion_historical_total_plot_paths,
        fusion_historical_group_plot_paths_by_country=grouped_fusion_historical_group_plot_paths,
        fusion_historical_total_plot_paths_by_country=grouped_fusion_historical_total_plot_paths,
        v43_country_profile_plot_paths=relative_v43_country_profile_plot_paths,
        v43_country_profile_plot_paths_by_country=grouped_v43_country_profile_plot_paths,
        v43_multicountry_plot_paths=relative_v43_multicountry_plot_paths,
        v431_country_peak_plot_paths=relative_v431_country_peak_plot_paths,
        v431_country_peak_plot_paths_by_country=grouped_v431_country_peak_plot_paths,
        v431_synchronization_plot_paths=relative_v431_synchronization_plot_paths,
        v432_country_event_alignment_plot_paths=relative_v432_country_event_alignment_plot_paths,
        v432_country_event_alignment_plot_paths_by_country=grouped_v432_country_event_alignment_plot_paths,
        historical_cluster_plot_paths_by_country=grouped_historical_cluster_plot_paths,
        historical_subscore_plot_paths_by_country=grouped_historical_subscore_plot_paths,
        historical_constant_clusters=historical_constant_clusters,
        historical_limited_marker=historical_limited_marker,
        run_status_effective=effective_run_status,
        run_status_proposed=proposed_run_status,
        run_status_overridden=run_status_overridden,
        run_comparison_payload=run_comparison_payload,
        reference_comparison_payload=reference_comparison_payload,
        reference_action=reference_action,
        versions={
            "query_version": config.query_version,
            "scoring_version": config.scoring_version,
            "bridge_file_version": config.bridge_file_version,
            "context_table_version": config.context_table_version,
        },
    )
    write_handout(handout_text, run_dir / "handout.md")

    print(f"Run finished with status: {effective_run_status}")


if __name__ == "__main__":
    main()
