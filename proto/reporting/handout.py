from __future__ import annotations

"""
Traceability:
- PSR-003
- PSR-005
- PSR-009
- PSR-010
- PSR-011
- PSR-012
- PSR-013
- PSR-014
- PSR-015
- PSR-016
- PSR-018
- PSR-019
- PSR-020
- PSR-021
- PSR-022
- PSR-023
- PSR-024
- PSR-026
- PSyR-006
- PSyR-011
- PSyR-012
- PSyR-015
- PSyR-016
- PSyR-017
- PSyR-019
- PSyR-020
- PSyR-023
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
- PSwR-015
- PSwR-016
- PSwR-029
- PSwR-033
- PSwR-045
- PSwR-046
- PSwR-051
- PSwR-052
- PSwR-053
- PSwR-064
- PSwR-065
- PSwR-066
- PSwR-073
- PSwR-074
- PSwR-080
- PSwR-081
- PSwR-083
- PSwR-085
- PSwR-089
- PSwR-090
- PSwR-093
- PSwR-094
- PSwR-095
- PSwR-096
- PSwR-098
- PSwR-099
- PSwR-100
- PSwR-101
- PSwR-102
- PSwR-103
- PSwR-104
- PSwR-113
- PSwR-114
- PSwR-115
- PSwR-116
- PSwR-117
- PSwR-118
- PSwR-119
- PSwR-120
- PSwR-121
- PSwR-123
- PSwR-124
- PM-014
- PM-015
- PM-017
- PM-020
- PM-021
- PM-023
- PM-028
- PM-030
- PM-034
- PM-041
- PM-046
- PM-047
- PM-048
- PM-051
- PM-052
- PM-053
- PM-054
- PM-055
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

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from proto.models import ClusterAssessment
from proto.reporting.presentation import (
    CLUSTER_ORDER,
    cluster_order_index,
    country_order_index,
    display_cluster,
    display_country,
)

if TYPE_CHECKING:
    from proto.fusion.models import (
        FusionGroupScoreRecord,
        FusionHistoricalGroupScoreRecord,
        FusionHistoricalTotalScoreRecord,
        FusionTotalScoreRecord,
    )
    from proto.scoring.trend_history import HistoricalReviewCandidateRecord
    from proto.scoring.trend_history import HistoricalRollingRecord

DELTA_SYMBOL = "\u0394"
TREND_DECREASING = "r\u00fcckl\u00e4ufig"
SNAPSHOT_SOURCE_VALID_ENDPOINT = "historical_valid_endpoint"
SNAPSHOT_SOURCE_VALID_LAGGED = "historical_latest_valid_before_run_date"
SNAPSHOT_SOURCE_NUMERIC_FALLBACK = "historical_numeric_fallback_below_min_valid_days"
SNAPSHOT_SOURCE_RAW_FALLBACK = "raw_latest_fallback_no_historical_value"


def _sorted_assessments(assessments: list[ClusterAssessment]) -> list[ClusterAssessment]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    return sorted(
        assessments,
        key=lambda item: (country_order_index(item.country), cluster_order_index(item.cluster)),
    )


def _format_delta(value: float | None) -> str:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    if value is None:
        return "n/a"
    if value > 0:
        return f"+{value:.2f}"
    return f"{value:.2f}"


def _format_interpretation_status(status: str) -> str:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    if status == "limited_historical_coverage":
        return "limited_historical_coverage (eingeschraenkt interpretierbar)"
    if status == "reduced_historical_coverage":
        return "reduced_historical_coverage (vorsichtig interpretieren)"
    return "standard"


def _country_cluster_map(
    assessments: list[ClusterAssessment],
) -> dict[str, dict[str, ClusterAssessment]]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    by_country: dict[str, dict[str, ClusterAssessment]] = defaultdict(dict)
    for assessment in assessments:
        by_country[assessment.country][assessment.cluster] = assessment
    return by_country


def _comparison_map(payload: dict) -> dict[tuple[str, str], dict]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    return {
        (entry["country"], entry["cluster"]): entry
        for entry in payload.get("comparisons", [])
    }


def _render_run_summary(
    *,
    run_timestamp: str,
    countries: list[str],
    run_status_effective: str,
    run_status_proposed: str,
    run_status_overridden: bool,
    run_comparison_payload: dict,
    reference_comparison_payload: dict,
    reference_action: str,
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    return [
        "## Run-Zusammenfassung",
        "",
        f"- Run timestamp: {run_timestamp}",
        f"- Countries: {', '.join(display_country(country) for country in countries)}",
        f"- Proposed run status: {run_status_proposed}",
        f"- Effective run status: {run_status_effective}",
        f"- Status override active: {'ja' if run_status_overridden else 'nein'}",
        f"- Vergleich letzter Run: {run_comparison_payload.get('status', 'n/a')}",
        f"- Vergleich Referenz-Run: {reference_comparison_payload.get('status', 'n/a')} ({reference_action})",
        "",
    ]


def _render_versions(versions: dict[str, str]) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    return [
        "## Versionsst\u00e4nde",
        "",
        f"- Query version: {versions['query_version']}",
        f"- Scoring version: {versions['scoring_version']}",
        f"- Bridge file version: {versions['bridge_file_version']}",
        f"- Context table version: {versions['context_table_version']}",
        "",
    ]


def _render_global_delta_overview(run_comparison_payload: dict) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    overview = run_comparison_payload.get("overview", {})
    return [
        "## Vergleich zum letzten Run (gesamt)",
        "",
        f"- Items: {overview.get('items', 0)}",
        f"- Zunehmend: {overview.get('zunehmend', 0)}",
        f"- {TREND_DECREASING.capitalize()}: {overview.get(TREND_DECREASING, 0)}",
        f"- Stabil: {overview.get('stabil', 0)}",
        f"- Kein Vergleich: {overview.get('kein_vergleich', 0)}",
        "",
    ]


def _historical_latest_cluster_map(
    records: list["HistoricalRollingRecord"],
) -> dict[tuple[str, str], "HistoricalRollingRecord"]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    latest: dict[tuple[str, str], "HistoricalRollingRecord"] = {}
    for record in records:
        if record.score_name != "cluster_score" or not record.is_valid:
            continue
        key = (record.country, record.cluster)
        previous = latest.get(key)
        if previous is None or record.date > previous.date:
            latest[key] = record
    return latest


def _historical_valid_count_map(
    records: list["HistoricalRollingRecord"],
) -> dict[tuple[str, str], int]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for record in records:
        if record.score_name == "cluster_score" and record.is_valid:
            counts[(record.country, record.cluster)] += 1
    return counts


def _format_snapshot_source_note(source: dict[str, object]) -> str:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    mode = str(source.get("source_mode", SNAPSHOT_SOURCE_RAW_FALLBACK))
    source_date = source.get("source_date") or "n/a"
    valid_days = source.get("valid_days")
    min_valid_days = source.get("min_valid_days")
    penalty = float(source.get("confidence_penalty_applied", 0.0) or 0.0)

    if mode == SNAPSHOT_SOURCE_VALID_ENDPOINT:
        return f"Snapshot-Herkunft: gueltiger Historical-Endpunkt am Run-Datum ({source_date})."
    if mode == SNAPSHOT_SOURCE_VALID_LAGGED:
        return (
            "Snapshot-Herkunft: letzter gueltiger Historical-Punkt vor Run-Datum "
            f"({source_date}); Endpunkt am Run-Datum war nicht gueltig."
        )
    if mode == SNAPSHOT_SOURCE_NUMERIC_FALLBACK:
        return (
            "Snapshot-Herkunft: Fallback auf letzten numerischen Historical-Rolling-Punkt "
            f"unter Mindestabdeckung ({source_date}, valid_days={valid_days}, "
            f"min_valid_days={min_valid_days}); zusaetzliche Confidence-Reduktion={penalty:.2f}."
        )
    return "Snapshot-Herkunft: Raw-Fallback ohne Historical-Rolling-Wert."


def _render_snapshot_block(
    *,
    country: str,
    clusters_for_country: dict[str, ClusterAssessment],
    run_comparison_map: dict[tuple[str, str], dict],
    snapshot_context: dict[tuple[str, str], dict[str, float | int | str | None]],
    snapshot_source_by_cluster: dict[tuple[str, str], dict[str, object]],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "### 1) Current Snapshot (offiziell)",
        "",
    ]
    for cluster in CLUSTER_ORDER:
        assessment = clusters_for_country.get(cluster)
        if assessment is None:
            lines.append(f"- {display_cluster(cluster)}: keine Snapshot-Bewertung verf\u00fcgbar.")
            continue
        comparison = run_comparison_map.get((country, cluster), {})
        delta_abs = _format_delta(comparison.get("delta_absolute"))
        delta_rel = comparison.get("delta_relative_percent")
        delta_rel_text = "n/a" if delta_rel is None else f"{delta_rel:+.2f}%"
        lines.append(
            "- "
            f"{display_cluster(cluster)}: {assessment.cluster_score:.2f} "
            f"({assessment.stage}, {assessment.trend}, {assessment.confidence_level}) "
            f"| {DELTA_SYMBOL} letzter Run: {delta_abs} ({delta_rel_text})"
        )
        annual = snapshot_context.get((country, cluster), {})
        current = annual.get("current_value")
        yearly_max = annual.get("year_max")
        yearly_min = annual.get("year_min")
        high_days = annual.get("high_or_very_high_days")
        latest_valid_date = annual.get("latest_valid_date")
        current_text = "n/a" if current is None else f"{float(current):.2f}"
        max_text = "n/a" if yearly_max is None else f"{float(yearly_max):.2f}"
        min_text = "n/a" if yearly_min is None else f"{float(yearly_min):.2f}"
        lines.append(
            "  Jahreskontext: "
            f"aktuell={current_text}, max={max_text}, min={min_text}, "
            f"Tage hoch/sehr hoch={int(high_days or 0)}, "
            f"letzter gueltiger Trendpunkt={latest_valid_date or 'n/a'}"
        )
        source = snapshot_source_by_cluster.get((country, cluster), {})
        lines.append(f"  {_format_snapshot_source_note(source)}")
        lines.append(f"  Interpretation: {assessment.summary_text}")
    lines.append("")
    return lines


def _render_historical_block(
    *,
    country: str,
    historical_records: list["HistoricalRollingRecord"],
    historical_limited_marker: bool,
    historical_constant_clusters: set[str],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    latest_map = _historical_latest_cluster_map(historical_records)
    valid_count_map = _historical_valid_count_map(historical_records)
    lines = [
        "### 2) Historical Rolling Trend (offiziell)",
        "",
    ]
    if historical_limited_marker:
        lines.append("- Hinweis: Historical Rolling Trend ist als eingeschraenkt brauchbar markiert.")
    for cluster in CLUSTER_ORDER:
        latest = latest_map.get((country, cluster))
        if latest is None:
            lines.append(f"- {display_cluster(cluster)}: keine gueltigen historischen Trendpunkte.")
            continue
        cluster_note = ""
        if cluster in historical_constant_clusters:
            cluster_note = " | methodischer Baseline-Cluster (historische Hilfsquellen aktuell zeitlich konstant)"
        lines.append(
            "- "
            f"{display_cluster(cluster)}: letzter gueltiger Punkt {latest.date.isoformat()} "
            f"= {latest.rolling_value:.2f} ({latest.stage}, {latest.trend}, {latest.confidence_level}), "
            f"gueltige Punkte im Jahr={valid_count_map.get((country, cluster), 0)}"
            f"{cluster_note}"
        )
    lines.append("")
    return lines


def _render_plot_block(
    *,
    heading: str,
    plot_paths: list[Path],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [heading, ""]
    if not plot_paths:
        lines.append("manual review required: keine Plotdateien gefunden.")
        lines.append("")
        return lines
    for path in sorted(plot_paths):
        lines.append(f"![{path.stem}]({path.as_posix()})")
    lines.append("")
    return lines


def _fusion_group_map(
    records: list["FusionGroupScoreRecord"],
) -> dict[str, list["FusionGroupScoreRecord"]]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    grouped: dict[str, list["FusionGroupScoreRecord"]] = defaultdict(list)
    for record in records:
        grouped[record.country].append(record)
    for country in grouped:
        grouped[country] = sorted(grouped[country], key=lambda item: item.group)
    return grouped


def _fusion_total_map(
    records: list["FusionTotalScoreRecord"],
) -> dict[str, "FusionTotalScoreRecord"]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    return {record.country: record for record in records}


def _fusion_historical_group_map(
    records: list["FusionHistoricalGroupScoreRecord"],
) -> dict[str, list["FusionHistoricalGroupScoreRecord"]]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    grouped: dict[str, list["FusionHistoricalGroupScoreRecord"]] = defaultdict(list)
    for record in records:
        grouped[record.country].append(record)
    for country in grouped:
        grouped[country] = sorted(
            grouped[country],
            key=lambda item: (item.target_period_end, item.group),
        )
    return grouped


def _fusion_historical_total_map(
    records: list["FusionHistoricalTotalScoreRecord"],
) -> dict[str, list["FusionHistoricalTotalScoreRecord"]]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    grouped: dict[str, list["FusionHistoricalTotalScoreRecord"]] = defaultdict(list)
    for record in records:
        grouped[record.country].append(record)
    for country in grouped:
        grouped[country] = sorted(grouped[country], key=lambda item: item.target_period_end)
    return grouped


def _render_fusion_overview_block(
    *,
    fusion_total_scores: list["FusionTotalScoreRecord"],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## V3.1 Layer/Fusion Snapshot (zusaetzlich)",
        "",
        "- Gruppenstatus: `ok`=berechnet, `limited`=teilweise Quellabdeckung, `not_available`=keine verwertbaren Quellen.",
        "- Hinweis: Der Fusion-Pfad ist ein zusaetzlicher Ergebnisraum und ersetzt die Cluster-Sicht nicht.",
        "",
    ]
    if not fusion_total_scores:
        lines.append("- keine Fusion-Scores verfuegbar.")
        lines.append("")
        return lines
    for record in sorted(fusion_total_scores, key=lambda item: country_order_index(item.country)):
        lines.append(
            "- "
            f"{display_country(record.country)}: Fusion={record.fusion_score:.2f}, "
            f"Confidence={record.confidence_score:.2f} ({record.confidence_level}), "
            f"Gruppen verfuegbar={record.available_group_count}/{record.group_count}, "
            f"Bonus={'ja' if record.bonus_applied else 'nein'} ({record.bonus_points:.2f})"
        )
    lines.append("")
    return lines


def _render_fusion_plausibility_warnings_block(
    *,
    warnings: list[dict[str, object]],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## Fusion Plausibility Warnings",
        "",
        "- Hinweise sind nicht-blockierend und dienen der analystischen Nachpruefung.",
        "",
    ]
    if not warnings:
        lines.append("- keine Auffaelligkeiten erkannt.")
        lines.append("")
        return lines
    for item in warnings:
        severity = str(item.get("severity", "info")).upper()
        message = str(item.get("message", "n/a"))
        code = str(item.get("code", "n/a"))
        lines.append(f"- [{severity}] {code}: {message}")
    lines.append("")
    return lines


def _render_fusion_validation_block(
    *,
    validation_summary: dict[str, object],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## V4.2 Governance, Validation & Operational Freshness (zusaetzlich)",
        "",
    ]
    if not validation_summary:
        lines.append("- keine Validation-Zusammenfassung verfuegbar.")
        lines.append("")
        return lines
    lines.append(f"- Status: {validation_summary.get('status', 'n/a')}")
    lines.append(
        "- "
        f"Referenzepisoden: {validation_summary.get('episode_count', 0)} "
        f"(mit Daten: {validation_summary.get('episodes_with_data', 0)})"
    )
    lines.append(
        "- "
        f"Peak-Hit-Rate: {float(validation_summary.get('peak_hit_rate', 0.0)):.2f}, "
        f"Timing-Fit-Rate: {float(validation_summary.get('timing_fit_rate', 0.0)):.2f}, "
        f"Expected-Group-Hit-Rate: {float(validation_summary.get('expected_group_hit_rate', 0.0)):.2f}"
    )
    lines.append(
        "- "
        f"Ranking-Fit: {float(validation_summary.get('ranking_fit_score', 0.0)):.2f} "
        f"(plausible={validation_summary.get('ranking_plausible', False)})"
    )
    lines.append(
        "- "
        f"Freshness-Coverage: {float(validation_summary.get('freshness_coverage_rate', 0.0)):.2f}, "
        f"Stale-Burden: {float(validation_summary.get('stale_burden_rate', 0.0)):.2f}, "
        f"Dynamic-Readiness: {float(validation_summary.get('dynamic_layer_readiness_rate', 0.0)):.2f}"
    )
    lines.append(
        "- "
        f"Response-Lag-Fit: {float(validation_summary.get('response_lag_fit_rate', 0.0)):.2f}, "
        f"Mean-|Lag|: {float(validation_summary.get('mean_absolute_timing_lag_months', 0.0)):.2f} Monate, "
        f"Historical-Mean-|Delta|: {float(validation_summary.get('historical_responsiveness_mean_abs_delta', 0.0)):.2f}"
    )
    lines.append(
        "- "
        f"Operational-Freshness-Attention: {validation_summary.get('operational_freshness_attention', False)}"
    )
    lines.append(
        "- "
        f"Dominance-Flags: {validation_summary.get('dominance_flag_count', 0)}, "
        f"Event-stale: {validation_summary.get('event_stale_country_count', 0)}, "
        f"Governance-instability: {validation_summary.get('governance_instability_country_count', 0)}, "
        f"Governance-stale: {validation_summary.get('governance_low_freshness_country_count', 0)}, "
        f"Structural-Outlier: {validation_summary.get('structural_outlier_count', 0)}, "
        f"Low-Fresh-Coverage: {validation_summary.get('low_fresh_coverage_country_count', 0)}, "
        f"Stale-Burden-Countries: {validation_summary.get('stale_burden_country_count', 0)}"
    )
    key_findings = validation_summary.get("key_findings", [])
    if isinstance(key_findings, list):
        for finding in key_findings[:5]:
            lines.append(f"- Hinweis: {finding}")
    lines.append("")
    return lines


def _render_fusion_historical_overview_block(
    *,
    fusion_historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## V3.2 Historical Fusion View (zusaetzlich)",
        "",
        "- Hinweis: Dies ist ein eigener historischer Multi-Layer-Ergebnisraum neben der Cluster-Historie.",
        "",
    ]
    if not fusion_historical_total_scores:
        lines.append("- keine historischen Fusion-Zeitreihen verfuegbar.")
        lines.append("")
        return lines
    latest_by_country: dict[str, "FusionHistoricalTotalScoreRecord"] = {}
    for record in fusion_historical_total_scores:
        previous = latest_by_country.get(record.country)
        if previous is None or record.target_period_end > previous.target_period_end:
            latest_by_country[record.country] = record
    for country, record in sorted(latest_by_country.items(), key=lambda item: country_order_index(item[0])):
        driver_text = (
            "n/a"
            if record.strongest_change_group is None
            else f"{record.strongest_change_group} ({record.strongest_change_delta:+.2f})"
        )
        if record.no_material_change:
            driver_text = "none (no material change)"
        top_1 = (
            "n/a"
            if record.top_positive_group_1 is None
            else f"{record.top_positive_group_1} ({record.top_positive_group_1_contribution:.2f})"
        )
        top_2 = (
            "n/a"
            if record.top_positive_group_2 is None
            else f"{record.top_positive_group_2} ({record.top_positive_group_2_contribution:.2f})"
        )
        lines.append(
            "- "
            f"{display_country(country)}: {record.period_label} -> Fusion={record.fusion_score:.2f} "
            f"({record.stage}, {record.trend}), Confidence={record.confidence_score:.2f} "
            f"({record.confidence_level}), Coverage={record.available_group_count}/{record.expected_group_count} "
            f"({record.available_group_ratio:.2f}), Top-Beitraege={top_1}; {top_2}, "
            f"staerkste Aenderung={driver_text}, "
            f"Interpretation={_format_interpretation_status(record.interpretation_status)}"
        )
    lines.append("")
    return lines


def _render_fusion_country_block(
    *,
    country: str,
    fusion_group_scores: list["FusionGroupScoreRecord"],
    fusion_total_score: "FusionTotalScoreRecord | None",
    validation_diagnostic: dict[str, object] | None,
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "### 2b) V3.1 Layer/Fusion (zusaetzlich)",
        "",
    ]
    if fusion_total_score is None:
        lines.append("- kein Fusion-Gesamtscore verfuegbar.")
    else:
        lines.append(
            "- "
            f"Fusion-Gesamtscore: {fusion_total_score.fusion_score:.2f} "
            f"(Confidence {fusion_total_score.confidence_score:.2f} / {fusion_total_score.confidence_level}), "
            f"Gruppen {fusion_total_score.available_group_count}/{fusion_total_score.group_count}, "
            f"Bonus={'ja' if fusion_total_score.bonus_applied else 'nein'}."
        )
    if not fusion_group_scores:
        lines.append("- keine Gruppenwerte verfuegbar.")
        lines.append("")
        return lines
    if validation_diagnostic:
        lines.append(
            "- "
            f"V4-Diagnose: dominant={validation_diagnostic.get('dominant_group') or 'n/a'} "
            f"(share={float(validation_diagnostic.get('dominant_group_share', 0.0)):.2f}), "
            f"support={validation_diagnostic.get('support_profile', 'n/a')} "
            f"({validation_diagnostic.get('active_group_count', 0)}/"
            f"{validation_diagnostic.get('available_group_count', 0)} aktiv), "
            f"event_stale={validation_diagnostic.get('event_stale_flag', False)}, "
            f"governance_instability={validation_diagnostic.get('governance_instability_flag', False)}, "
            f"governance_stale={validation_diagnostic.get('governance_low_freshness_flag', False)}, "
            f"structural_outlier={validation_diagnostic.get('structural_outlier_flag', False)}."
        )
        lines.append(
            "- "
            f"Freshness-Diagnose: fresh_support={validation_diagnostic.get('fresh_support_profile', 'n/a')}, "
            f"stale_support={validation_diagnostic.get('stale_support_profile', 'n/a')}, "
            f"fresh_share={float(validation_diagnostic.get('fresh_contribution_share', 0.0)):.2f}, "
            f"stale_share={float(validation_diagnostic.get('stale_contribution_share', 0.0)):.2f}, "
            f"dynamic_ready={validation_diagnostic.get('dynamic_layer_readiness', False)}, "
            f"dominant_fresh={validation_diagnostic.get('dominant_fresh_group') or 'n/a'}, "
            f"dominant_aging={validation_diagnostic.get('dominant_aging_group') or 'n/a'}, "
            f"latest_fresh_obs={validation_diagnostic.get('latest_fresh_observation_date') or 'n/a'}."
        )
    for record in fusion_group_scores:
        if record.status != "ok" or record.group_score is None:
            lines.append(f"- {record.group}: n/a (not_available)")
            continue
        lines.append(
            "- "
            f"{record.group}: {record.group_score:.2f} "
            f"(Confidence {record.confidence_score:.2f}/{record.confidence_level}, "
            f"Coverage {record.source_count}/{record.expected_source_count}) "
            f"| sources={record.sources_used or 'n/a'}"
        )
    lines.append("")
    return lines


def _render_fusion_historical_country_block(
    *,
    country: str,
    fusion_historical_group_scores: list["FusionHistoricalGroupScoreRecord"],
    fusion_historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "### 2c) V3.2 Historical Fusion (zusaetzlich)",
        "",
    ]
    if not fusion_historical_total_scores:
        lines.append("- keine historischen Fusion-Werte verfuegbar.")
        lines.append("")
        return lines

    latest_total = max(fusion_historical_total_scores, key=lambda item: item.target_period_end)
    has_limited_period = any(
        item.interpretation_status == "limited_historical_coverage"
        for item in fusion_historical_total_scores
    )
    has_reduced_period = any(
        item.interpretation_status == "reduced_historical_coverage"
        for item in fusion_historical_total_scores
    )
    strongest_change_text = (
        "n/a"
        if latest_total.strongest_change_group is None
        else f"{latest_total.strongest_change_group} ({latest_total.strongest_change_delta:+.2f})"
    )
    if latest_total.no_material_change:
        strongest_change_text = "none (no material change)"
    top_1 = (
        "n/a"
        if latest_total.top_positive_group_1 is None
        else f"{latest_total.top_positive_group_1} ({latest_total.top_positive_group_1_contribution:.2f})"
    )
    top_2 = (
        "n/a"
        if latest_total.top_positive_group_2 is None
        else f"{latest_total.top_positive_group_2} ({latest_total.top_positive_group_2_contribution:.2f})"
    )
    coverage_text = (
        f"{latest_total.available_group_count}/{latest_total.expected_group_count} "
        f"({latest_total.available_group_ratio:.2f})"
    )
    lines.append(
        "- "
        f"Letzter historischer Fusion-Punkt {latest_total.period_label}: {latest_total.fusion_score:.2f} "
        f"({latest_total.stage}, {latest_total.trend}), "
        f"Confidence {latest_total.confidence_score:.2f}/{latest_total.confidence_level}, "
        f"Coverage={coverage_text}, Top-Beitraege={top_1}; {top_2}, "
        f"staerkste Aenderung={strongest_change_text}, "
        f"Interpretation={_format_interpretation_status(latest_total.interpretation_status)}."
    )
    if latest_total.interpretation_status == "limited_historical_coverage":
        lines.append(
            "- Hinweis: Historische Aussagekraft eingeschraenkt (geringe Gruppenabdeckung in letzter Periode)."
        )
    elif latest_total.interpretation_status == "reduced_historical_coverage":
        lines.append(
            "- Hinweis: Historische Aussagekraft reduziert (partielle Gruppenabdeckung in letzter Periode)."
        )
    elif has_limited_period:
        lines.append(
            "- Hinweis: Fruehe historische Perioden sind eingeschraenkt interpretierbar "
            "(zeitweise geringe Gruppenabdeckung)."
        )
    elif has_reduced_period:
        lines.append(
            "- Hinweis: Fruehe historische Perioden sind reduziert interpretierbar "
            "(zeitweise partielle Gruppenabdeckung)."
        )
    if latest_total.confidence_dominance_penalty > 0:
        lines.append(
            "- Hinweis: Confidence durch Dominanz eines Einzel-Layers reduziert "
            f"(Penalty {latest_total.confidence_dominance_penalty:.2f})."
        )

    latest_group_date = latest_total.target_period_end
    latest_group_records = [
        record
        for record in fusion_historical_group_scores
        if record.target_period_end == latest_group_date
    ]
    if not latest_group_records:
        lines.append("- keine historischen Gruppenwerte zum letzten Punkt verfuegbar.")
        lines.append("")
        return lines
    for record in sorted(latest_group_records, key=lambda item: item.group):
        if record.group_score is None:
            lines.append(f"- {record.group}: n/a ({record.status})")
            continue
        lines.append(
            "- "
            f"{record.group}: {record.group_score:.2f} "
            f"(status={record.status}, confidence={record.confidence_score:.2f}/{record.confidence_level}, "
            f"coverage={record.source_count}/{record.expected_source_count})"
        )
    lines.append("")
    return lines


def _render_top_review_candidates_block(
    *,
    candidates: list["HistoricalReviewCandidateRecord"],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## Top historical review candidates",
        "",
        (
            "- Scope: `cluster_score` fuer `tension` und `escalation`; "
            "`vulnerability` ist derzeit baseline-artig und standardmaessig ausgeschlossen."
        ),
        (
            "- Hinweis: Kandidaten sind analystenorientierte Pruefpunkte; "
            "Low-Coverage-Punkte sind nicht als voll validierte historische Peaks zu lesen."
        ),
        "",
    ]
    if not candidates:
        lines.append("- keine Review-Kandidaten verfuegbar.")
        lines.append("")
        return lines

    for candidate in candidates:
        coverage_note = (
            f"valid ({candidate.valid_days}/{candidate.min_valid_days})"
            if candidate.is_valid
            else (
                f"LOW-COVERAGE ({candidate.valid_days}/{candidate.min_valid_days}, "
                f"coverage={candidate.coverage_ratio:.2f})"
            )
        )
        driver_note = candidate.dominant_driver or candidate.top_driver_1_name or "n/a"
        lines.append(
            "- "
            f"#{candidate.rank} {display_country(candidate.country)} / {display_cluster(candidate.cluster)} / "
            f"{candidate.date.isoformat()}: {candidate.rolling_value:.2f} "
            f"({candidate.stage}, {candidate.trend}), {coverage_note}, "
            f"confidence={candidate.confidence_score:.2f} ({candidate.confidence_level}), "
            f"driver={driver_note}, snapshot_relation={candidate.snapshot_relation}"
        )
    lines.append("")
    return lines


def _as_float(payload: dict[str, object], key: str, default: float = 0.0) -> float:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    value = payload.get(key, default)
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _as_int(payload: dict[str, object], key: str, default: int = 0) -> int:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    value = payload.get(key, default)
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _render_v43_main_comparison_block(
    *,
    country_profiles: list[dict[str, object]],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## V4.3 Comparative Expansion: 10 Countries, Full 356-Day Profiles",
        "",
        "- Fokus: verlaufsgetriebener 356-Tage-Laendervergleich (nicht primaer episodengetrieben).",
        "- Hauptvergleichstabelle:",
        "",
    ]
    if not country_profiles:
        lines.append("- keine V4.3-Laenderprofile verfuegbar.")
        lines.append("")
        return lines

    sorted_profiles = sorted(
        country_profiles,
        key=lambda item: _as_float(item, "current_fusion_score"),
        reverse=True,
    )
    for record in sorted_profiles:
        country = display_country(str(record.get("country", "n/a")))
        lines.append(
            "- "
            f"{country}: current={_as_float(record, 'current_fusion_score'):.2f}, "
            f"confidence={_as_float(record, 'confidence_score'):.2f} "
            f"({record.get('confidence_level', 'n/a')}), "
            f"freshness={record.get('operational_freshness_status', 'n/a')}, "
            f"year_max={_as_float(record, 'year_max_score'):.2f}, "
            f"year_min={_as_float(record, 'year_min_score'):.2f}, "
            f"volatility={_as_float(record, 'year_volatility_std'):.2f}, "
            f"range={_as_float(record, 'year_range_score'):.2f}, "
            f"dominant={record.get('dominant_group') or 'n/a'}, "
            f"support={record.get('support_profile', 'n/a')}."
        )
    lines.append("")
    return lines


def _render_v43_diagnostics_block(
    *,
    peak_phases: list[dict[str, object]],
    group_profiles: list[dict[str, object]],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## V4.3 Vertiefende Diagnostik",
        "",
    ]
    if not peak_phases and not group_profiles:
        lines.append("- keine vertiefenden V4.3-Diagnostikdaten verfuegbar.")
        lines.append("")
        return lines

    top_peaks = [
        item
        for item in peak_phases
        if _as_int(item, "peak_rank", default=99) == 1
    ]
    top_peaks_sorted = sorted(
        top_peaks,
        key=lambda item: _as_float(item, "fusion_score"),
        reverse=True,
    )
    lines.append("- Top-Peak je Land:")
    for peak in top_peaks_sorted:
        lines.append(
            "- "
            f"{display_country(str(peak.get('country', 'n/a')))} / {peak.get('period_label', 'n/a')}: "
            f"{_as_float(peak, 'fusion_score'):.2f} "
            f"({peak.get('stage', 'n/a')}), driver={peak.get('top_positive_group_1') or 'n/a'}, "
            f"fresh_share={_as_float(peak, 'fresh_contribution_share'):.2f}, "
            f"stale_share={_as_float(peak, 'stale_contribution_share'):.2f}."
        )

    dominant_group_by_country: dict[str, dict[str, object]] = {}
    for row in group_profiles:
        country = str(row.get("country", ""))
        previous = dominant_group_by_country.get(country)
        if previous is None or _as_float(row, "mean_contribution_share") > _as_float(previous, "mean_contribution_share"):
            dominant_group_by_country[country] = row
    lines.append("")
    lines.append("- Mittlerer dominanter Gruppenbeitrag (356 Tage):")
    for country in sorted(dominant_group_by_country.keys(), key=country_order_index):
        row = dominant_group_by_country[country]
        lines.append(
            "- "
            f"{display_country(country)}: {row.get('group', 'n/a')} "
            f"(mean_score={_as_float(row, 'mean_group_score'):.2f}, "
            f"mean_share={_as_float(row, 'mean_contribution_share'):.2f}, "
            f"active_ratio={_as_float(row, 'active_period_ratio'):.2f})."
        )
    lines.append("")
    return lines


def _render_v431_peak_hardening_block(
    *,
    peak_attribution: list[dict[str, object]],
    peak_synchronization: list[dict[str, object]],
    trajectory_profiles: list[dict[str, object]],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## V4.3.1 Peak Attribution & Event Alignment Hardening",
        "",
    ]
    if not peak_attribution and not peak_synchronization:
        lines.append("- keine V4.3.1-Peak-Attributionsdaten verfuegbar.")
        lines.append("")
        return lines

    total_peak_count = len(peak_attribution)
    event_supported = len(
        [item for item in peak_attribution if str(item.get("attribution_label")) == "event_supported_peak"]
    )
    weak_supported = len(
        [item for item in peak_attribution if str(item.get("attribution_label")) == "weakly_supported_peak"]
    )
    global_co_moving = len(
        [
            item
            for item in peak_attribution
            if str(item.get("attribution_label")) in {"globally_co_moving_peak", "global_background_stress_peak"}
        ]
    )
    model_driven = len(
        [item for item in peak_attribution if str(item.get("attribution_label")) == "model_driven_peak"]
    )
    if total_peak_count > 0:
        lines.append(
            "- "
            f"Peak-Klassen: event_supported={event_supported}/{total_peak_count}, "
            f"weakly_supported={weak_supported}/{total_peak_count}, "
            f"globally_co_moving_or_background={global_co_moving}/{total_peak_count}, "
            f"model_driven={model_driven}/{total_peak_count}."
        )
    lines.append("- Top-Peaks mit Attribution:")
    top_rows = sorted(
        [item for item in peak_attribution if _as_int(item, "peak_rank", default=99) == 1],
        key=lambda item: _as_float(item, "fusion_score"),
        reverse=True,
    )
    for row in top_rows:
        lines.append(
            "- "
            f"{display_country(str(row.get('country', 'n/a')))} / {row.get('period_label', 'n/a')}: "
            f"score={_as_float(row, 'fusion_score'):.2f}, "
            f"attr={row.get('attribution_label', 'n/a')}, "
            f"event={row.get('event_support_status', 'n/a')}, "
            f"global_share={_as_float(row, 'global_share'):.2f}, "
            f"country_share={_as_float(row, 'country_specific_share'):.2f}, "
            f"driver={row.get('dominant_group') or 'n/a'}."
        )

    if peak_synchronization:
        lines.append("")
        lines.append("- Synchronisierte Peak-Cluster:")
        for row in peak_synchronization:
            lines.append(
                "- "
                f"{row.get('period_label', 'n/a')}: "
                f"peak_ratio={_as_float(row, 'peak_country_ratio'):.2f}, "
                f"class={row.get('synchronization_class', 'n/a')}, "
                f"countries={row.get('peak_countries', 'n/a')}, "
                f"wave_group={row.get('dominant_wave_group') or 'n/a'}."
            )

    if trajectory_profiles:
        lines.append("")
        lines.append("- Trajectory-Profile:")
        for row in sorted(
            trajectory_profiles,
            key=lambda item: country_order_index(str(item.get("country", ""))),
        ):
            lines.append(
                "- "
                f"{display_country(str(row.get('country', 'n/a')))}: "
                f"profile={row.get('trajectory_profile', 'n/a')}, "
                f"country_specific_ratio={_as_float(row, 'country_specific_peak_ratio'):.2f}, "
                f"global_ratio={_as_float(row, 'globally_co_moving_peak_ratio'):.2f}, "
                f"mean_peak_conf={_as_float(row, 'mean_peak_confidence_score'):.2f}, "
                f"differentiation={row.get('differentiation_flag', False)}."
            )
    lines.append("")
    return lines


def _render_v432_event_alignment_block(
    *,
    event_registry: list[dict[str, object]],
    peak_event_matches: list[dict[str, object]],
    event_coverage_summary: list[dict[str, object]],
    country_event_alignment: list[dict[str, object]],
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "## V4.3.2 Analyst Event Registry & Real-World Alignment",
        "",
    ]
    if not peak_event_matches and not event_registry:
        lines.append("- keine V4.3.2-Event-Alignment-Daten verfuegbar.")
        lines.append("")
        return lines

    global_coverage = next(
        (item for item in event_coverage_summary if str(item.get("scope")) == "global"),
        None,
    )
    lines.append(
        "- "
        f"Registry-Eintraege: {len(event_registry)}, "
        f"Peak-Event-Matches: {len(peak_event_matches)}, "
        f"Global credible ratio={_as_float(global_coverage or {}, 'credible_match_ratio'):.2f}, "
        f"no_match_ratio={_as_float(global_coverage or {}, 'no_credible_match_ratio'):.2f}, "
        f"multi_overlap_ratio={_as_float(global_coverage or {}, 'multi_event_overlap_ratio'):.2f}."
    )

    class_counts: dict[str, int] = defaultdict(int)
    for item in peak_event_matches:
        class_counts[str(item.get("match_class", "unknown"))] += 1
    lines.append(
        "- "
        "Match-Klassen: "
        f"direct={class_counts.get('direct_match', 0)}, "
        f"context={class_counts.get('plausible_context_match', 0)}, "
        f"weak={class_counts.get('weak_match', 0)}, "
        f"no_credible={class_counts.get('no_credible_match', 0)}, "
        f"multi_overlap={class_counts.get('multi_event_overlap', 0)}."
    )

    if country_event_alignment:
        lines.append("- Country alignment maturity:")
        for item in sorted(
            country_event_alignment,
            key=lambda row: country_order_index(str(row.get("country", ""))),
        ):
            lines.append(
                "- "
                f"{display_country(str(item.get('country', 'n/a')))}: "
                f"maturity={item.get('alignment_maturity', 'n/a')} "
                f"({_as_float(item, 'alignment_maturity_score'):.2f}), "
                f"credible={_as_float(item, 'credible_match_ratio'):.2f}, "
                f"mean_match_conf={_as_float(item, 'mean_match_confidence'):.2f}, "
                f"uncertainties={item.get('open_uncertainties') or 'none'}."
            )

    top_rows = sorted(
        [item for item in peak_event_matches if _as_int(item, "peak_rank", default=99) == 1],
        key=lambda item: _as_float(item, "fusion_score"),
        reverse=True,
    )
    if top_rows:
        lines.append("")
        lines.append("- Top-Peaks mit Realwelt-Zuordnung:")
        for item in top_rows:
            lines.append(
                "- "
                f"{display_country(str(item.get('country', 'n/a')))} / {item.get('period_label', 'n/a')}: "
                f"score={_as_float(item, 'fusion_score'):.2f}, "
                f"match={item.get('match_class', 'n/a')}, "
                f"match_conf={_as_float(item, 'match_confidence'):.2f}, "
                f"event={item.get('best_event_title') or 'n/a'}, "
                f"trajectory={item.get('trajectory_profile', 'n/a')}."
            )

    lines.append("")
    return lines


def _render_v43_country_profile_block(
    *,
    country: str,
    country_profile: dict[str, object] | None,
    country_peaks: list[dict[str, object]],
    country_group_profiles: list[dict[str, object]],
    country_peak_attribution: list[dict[str, object]],
    country_peak_event_support: list[dict[str, object]],
    country_peak_event_matches: list[dict[str, object]],
    country_event_alignment: dict[str, object] | None,
    trajectory_profile: dict[str, object] | None,
) -> list[str]:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    lines = [
        "### 2d) V4.3 Jahresprofil (zusaetzlich)",
        "",
    ]
    if country_profile is None:
        lines.append("- kein V4.3-Laenderprofil verfuegbar.")
        lines.append("")
        return lines

    volatility = _as_float(country_profile, "year_volatility_std")
    score_range = _as_float(country_profile, "year_range_score")
    mean_score = _as_float(country_profile, "year_mean_score")
    peak_count = _as_int(country_profile, "peak_count")
    profile_shape = "peak-getrieben" if peak_count >= 3 else "kontinuierlicher"
    if volatility >= 10.0:
        stability_label = "volatil"
    elif score_range <= 20.0:
        stability_label = "relativ stabil"
    else:
        stability_label = "moderat variabel"

    lines.append(
        "- "
        f"Profil: {stability_label}, {profile_shape}; "
        f"mean={mean_score:.2f}, range={score_range:.2f}, volatility={volatility:.2f}, "
        f"freshness={country_profile.get('operational_freshness_status', 'n/a')}."
    )
    lines.append(
        "- "
        f"Treiberbild: dominant={country_profile.get('dominant_group') or 'n/a'}, "
        f"support={country_profile.get('support_profile', 'n/a')}, "
        f"fresh_support={country_profile.get('fresh_support_profile', 'n/a')}, "
        f"stale_support={country_profile.get('stale_support_profile', 'n/a')}."
    )
    lines.append(
        "- "
        f"Max/Min: {country_profile.get('year_max_period', 'n/a')}="
        f"{_as_float(country_profile, 'year_max_score'):.2f}, "
        f"{country_profile.get('year_min_period', 'n/a')}="
        f"{_as_float(country_profile, 'year_min_score'):.2f}."
    )

    peaks_sorted = sorted(
        country_peaks,
        key=lambda item: _as_int(item, "peak_rank", default=99),
    )[:3]
    peak_attribution_by_rank = {
        _as_int(item, "peak_rank", default=99): item for item in country_peak_attribution
    }
    peak_support_by_rank = {
        _as_int(item, "peak_rank", default=99): item for item in country_peak_event_support
    }
    peak_match_by_rank = {
        _as_int(item, "peak_rank", default=99): item for item in country_peak_event_matches
    }
    if peaks_sorted:
        lines.append("- Kritische Peak-Phasen:")
        for peak in peaks_sorted:
            rank = _as_int(peak, "peak_rank")
            attribution = peak_attribution_by_rank.get(rank, {})
            support = peak_support_by_rank.get(rank, {})
            match = peak_match_by_rank.get(rank, {})
            lines.append(
                "- "
                f"#{rank} {peak.get('period_label', 'n/a')}: "
                f"{_as_float(peak, 'fusion_score'):.2f} ({peak.get('stage', 'n/a')}), "
                f"driver={peak.get('top_positive_group_1') or 'n/a'}, "
                f"change={peak.get('strongest_change_group') or 'n/a'}, "
                f"attr={attribution.get('attribution_label', 'n/a')}, "
                f"event={support.get('event_support_status', 'n/a')}, "
                f"event_match={match.get('match_class', 'n/a')}, "
                f"match_conf={_as_float(match, 'match_confidence'):.2f}, "
                f"linked_event={match.get('best_event_title') or 'n/a'}, "
                f"global_share={_as_float(attribution, 'global_share'):.2f}, "
                f"country_share={_as_float(attribution, 'country_specific_share'):.2f}."
            )

    top_group_profiles = sorted(
        country_group_profiles,
        key=lambda item: _as_float(item, "mean_contribution_share"),
        reverse=True,
    )[:3]
    if top_group_profiles:
        lines.append("- Mittlere Gruppenbeitraege (Top 3):")
        for row in top_group_profiles:
            lines.append(
                "- "
                f"{row.get('group', 'n/a')}: mean={_as_float(row, 'mean_group_score'):.2f}, "
                f"share={_as_float(row, 'mean_contribution_share'):.2f}, "
                f"availability={_as_float(row, 'availability_ratio'):.2f}."
            )
    if trajectory_profile is not None:
        lines.append(
            "- "
            f"Trajectory: {trajectory_profile.get('trajectory_profile', 'n/a')}, "
            f"country_specific_peak_ratio={_as_float(trajectory_profile, 'country_specific_peak_ratio'):.2f}, "
            f"globally_co_moving_peak_ratio={_as_float(trajectory_profile, 'globally_co_moving_peak_ratio'):.2f}, "
            f"mean_peak_confidence={_as_float(trajectory_profile, 'mean_peak_confidence_score'):.2f}, "
            f"differentiation={trajectory_profile.get('differentiation_flag', False)}."
        )
    if country_event_alignment is not None:
        global_wave_ratio = _as_float(country_event_alignment, "global_wave_peak_ratio")
        country_specific_ratio = _as_float(country_event_alignment, "country_specific_peak_ratio")
        if global_wave_ratio >= 0.55 and country_specific_ratio < 0.35:
            trajectory_comment = "Phase laeuft eher global mit"
        elif country_specific_ratio >= 0.45:
            trajectory_comment = "Phase wirkt eher laenderspezifisch"
        else:
            trajectory_comment = "Phase ist gemischt (global + laenderspezifisch)"
        lines.append(
            "- "
            f"Event-Alignment: maturity={country_event_alignment.get('alignment_maturity', 'n/a')} "
            f"({_as_float(country_event_alignment, 'alignment_maturity_score'):.2f}), "
            f"credible_ratio={_as_float(country_event_alignment, 'credible_match_ratio'):.2f}, "
            f"mean_match_conf={_as_float(country_event_alignment, 'mean_match_confidence'):.2f}, "
            f"global_wave_ratio={global_wave_ratio:.2f}, "
            f"country_specific_ratio={country_specific_ratio:.2f}."
        )
        lines.append(
            "- "
            f"Event-Alignment-Kommentar: {trajectory_comment}; "
            f"Top-Events={country_event_alignment.get('top_linked_events') or 'n/a'}; "
            f"offene Unsicherheiten={country_event_alignment.get('open_uncertainties') or 'none'}."
        )
    lines.append("")
    return lines


def build_handout_markdown(
    *,
    run_timestamp: str,
    countries: list[str],
    snapshot_assessments: list[ClusterAssessment],
    snapshot_source_by_cluster: dict[tuple[str, str], dict[str, object]],
    snapshot_context: dict[tuple[str, str], dict[str, float | int | str | None]],
    historical_records: list["HistoricalRollingRecord"],
    historical_review_candidates: list["HistoricalReviewCandidateRecord"],
    fusion_group_scores: list["FusionGroupScoreRecord"],
    fusion_total_scores: list["FusionTotalScoreRecord"],
    fusion_historical_group_scores: list["FusionHistoricalGroupScoreRecord"],
    fusion_historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
    fusion_plausibility_warnings: list[dict[str, object]],
    fusion_validation_summary: dict[str, object],
    fusion_validation_diagnostics: list[dict[str, object]],
    fusion_validation_country_profiles: list[dict[str, object]],
    fusion_validation_peak_phases: list[dict[str, object]],
    fusion_validation_group_profiles: list[dict[str, object]],
    fusion_validation_ranking_trajectory: list[dict[str, object]],
    fusion_peak_attribution: list[dict[str, object]],
    fusion_peak_event_support: list[dict[str, object]],
    fusion_peak_event_matches: list[dict[str, object]],
    fusion_event_registry: list[dict[str, object]],
    fusion_event_coverage_summary: list[dict[str, object]],
    fusion_country_event_alignment: list[dict[str, object]],
    fusion_trajectory_profiles: list[dict[str, object]],
    fusion_peak_synchronization: list[dict[str, object]],
    snapshot_plot_paths: list[Path],
    snapshot_plot_paths_by_country: dict[str, list[Path]],
    historical_cluster_plot_paths: list[Path],
    historical_subscore_plot_paths: list[Path],
    fusion_plot_paths: list[Path],
    fusion_plot_paths_by_country: dict[str, list[Path]],
    fusion_historical_group_plot_paths: list[Path],
    fusion_historical_total_plot_paths: list[Path],
    fusion_historical_group_plot_paths_by_country: dict[str, list[Path]],
    fusion_historical_total_plot_paths_by_country: dict[str, list[Path]],
    v43_country_profile_plot_paths: list[Path],
    v43_country_profile_plot_paths_by_country: dict[str, list[Path]],
    v43_multicountry_plot_paths: list[Path],
    v431_country_peak_plot_paths: list[Path],
    v431_country_peak_plot_paths_by_country: dict[str, list[Path]],
    v431_synchronization_plot_paths: list[Path],
    v432_country_event_alignment_plot_paths: list[Path],
    v432_country_event_alignment_plot_paths_by_country: dict[str, list[Path]],
    historical_cluster_plot_paths_by_country: dict[str, list[Path]],
    historical_subscore_plot_paths_by_country: dict[str, list[Path]],
    historical_constant_clusters: set[str],
    historical_limited_marker: bool,
    run_status_effective: str,
    run_status_proposed: str,
    run_status_overridden: bool,
    run_comparison_payload: dict,
    reference_comparison_payload: dict,
    reference_action: str,
    versions: dict[str, str],
) -> str:
    """
    Build Markdown handout with separated official Snapshot + Historical sections.

    Traceability:
    - PSR-003
    - PSR-005
    - PSR-009
    - PSR-010
    - PSR-011
    - PSR-012
    - PSR-013
    - PSR-015
    - PSR-016
    - PSR-018
    - PSR-019
    - PSR-022
    - PSR-023
    - PSR-024
    - PSR-026
    - PSyR-006
    - PSyR-011
    - PSyR-012
    - PSyR-015
    - PSyR-016
    - PSyR-017
    - PSyR-019
    - PSyR-020
    - PSyR-023
    - PSyR-028
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
    - PSwR-015
    - PSwR-016
    - PSwR-029
    - PSwR-033
    - PSwR-045
    - PSwR-046
    - PSwR-051
    - PSwR-052
    - PSwR-053
    - PSwR-064
    - PSwR-065
    - PSwR-066
    - PSwR-080
    - PSwR-081
    - PSwR-085
    - PSwR-089
    - PSwR-090
    - PSwR-093
    - PSwR-094
    - PSwR-095
    - PSwR-096
    - PSwR-098
    - PSwR-099
    - PSwR-100
    - PSwR-101
    - PSwR-102
    - PSwR-103
    - PSwR-104
    - PSwR-113
    - PSwR-114
    - PSwR-115
    - PSwR-116
    - PSwR-117
    - PSwR-118
    - PSwR-119
    - PSwR-120
    - PSwR-121
    - PSwR-123
    - PSwR-124
    - PM-014
    - PM-015
    - PM-017
    - PM-020
    - PM-021
    - PM-023
    - PM-028
    - PM-030
    - PM-046
    - PM-047
    - PM-048
    - PM-051
    - PM-052
    - PM-053
    - PM-054
    - PM-055
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
    sorted_assessments = _sorted_assessments(snapshot_assessments)
    cluster_map = _country_cluster_map(sorted_assessments)
    run_comparison_map = _comparison_map(run_comparison_payload)
    fusion_group_by_country = _fusion_group_map(fusion_group_scores)
    fusion_total_by_country = _fusion_total_map(fusion_total_scores)
    fusion_historical_group_by_country = _fusion_historical_group_map(fusion_historical_group_scores)
    fusion_historical_total_by_country = _fusion_historical_total_map(fusion_historical_total_scores)
    fusion_validation_by_country = {
        str(item.get("country")): item for item in fusion_validation_diagnostics
    }
    fusion_validation_profile_by_country = {
        str(item.get("country")): item for item in fusion_validation_country_profiles
    }
    fusion_validation_peak_by_country: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in fusion_validation_peak_phases:
        fusion_validation_peak_by_country[str(item.get("country"))].append(item)
    fusion_validation_group_profile_by_country: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in fusion_validation_group_profiles:
        fusion_validation_group_profile_by_country[str(item.get("country"))].append(item)
    fusion_peak_attribution_by_country: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in fusion_peak_attribution:
        fusion_peak_attribution_by_country[str(item.get("country"))].append(item)
    fusion_peak_support_by_country: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in fusion_peak_event_support:
        fusion_peak_support_by_country[str(item.get("country"))].append(item)
    fusion_peak_matches_by_country: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in fusion_peak_event_matches:
        fusion_peak_matches_by_country[str(item.get("country"))].append(item)
    fusion_country_event_alignment_by_country = {
        str(item.get("country")): item for item in fusion_country_event_alignment
    }
    fusion_trajectory_profile_by_country = {
        str(item.get("country")): item for item in fusion_trajectory_profiles
    }

    lines = ["# Country Destabilization Prototype V4.3.2 - Handout", ""]
    lines.extend(
        _render_run_summary(
            run_timestamp=run_timestamp,
            countries=countries,
            run_status_effective=run_status_effective,
            run_status_proposed=run_status_proposed,
            run_status_overridden=run_status_overridden,
            run_comparison_payload=run_comparison_payload,
            reference_comparison_payload=reference_comparison_payload,
            reference_action=reference_action,
        )
    )
    lines.extend(_render_versions(versions))
    lines.extend(_render_global_delta_overview(run_comparison_payload))
    lines.extend(
        _render_v43_main_comparison_block(
            country_profiles=fusion_validation_country_profiles,
        )
    )
    lines.extend(
        _render_v43_diagnostics_block(
            peak_phases=fusion_validation_peak_phases,
            group_profiles=fusion_validation_group_profiles,
        )
    )
    lines.extend(
        _render_v431_peak_hardening_block(
            peak_attribution=fusion_peak_attribution,
            peak_synchronization=fusion_peak_synchronization,
            trajectory_profiles=fusion_trajectory_profiles,
        )
    )
    lines.extend(
        _render_v432_event_alignment_block(
            event_registry=fusion_event_registry,
            peak_event_matches=fusion_peak_event_matches,
            event_coverage_summary=fusion_event_coverage_summary,
            country_event_alignment=fusion_country_event_alignment,
        )
    )
    lines.extend(
        _render_top_review_candidates_block(
            candidates=historical_review_candidates,
        )
    )
    lines.extend(
        _render_fusion_overview_block(
            fusion_total_scores=fusion_total_scores,
        )
    )
    lines.extend(
        _render_fusion_historical_overview_block(
            fusion_historical_total_scores=fusion_historical_total_scores,
        )
    )
    lines.extend(
        _render_fusion_plausibility_warnings_block(
            warnings=fusion_plausibility_warnings,
        )
    )
    lines.extend(
        _render_fusion_validation_block(
            validation_summary=fusion_validation_summary,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## Snapshot-Plots (gesamt)",
            plot_paths=snapshot_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## Historical-Trend-Plots Cluster (gesamt)",
            plot_paths=historical_cluster_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## Historical-Trend-Plots Subscores (gesamt)",
            plot_paths=historical_subscore_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## V3.1 Fusion-Plots (gesamt)",
            plot_paths=fusion_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## V3.2 Historical Fusion Group-Plots (gesamt)",
            plot_paths=fusion_historical_group_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## V3.2 Historical Fusion Total-Plots (gesamt)",
            plot_paths=fusion_historical_total_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## V4.3 Vergleichsplots (laenderuebergreifend)",
            plot_paths=v43_multicountry_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## V4.3 Pro-Land-Jahresprofil-Plots (gesamt)",
            plot_paths=v43_country_profile_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## V4.3.1 Peak-Synchronisationsplots (gesamt)",
            plot_paths=v431_synchronization_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## V4.3.1 Peak-Attributionsplots (gesamt)",
            plot_paths=v431_country_peak_plot_paths,
        )
    )
    lines.extend(
        _render_plot_block(
            heading="## V4.3.2 Event-Alignment-Plots (gesamt)",
            plot_paths=v432_country_event_alignment_plot_paths,
        )
    )

    for country in sorted(countries, key=country_order_index):
        lines.append(f"## {display_country(country)}")
        lines.append("")
        lines.extend(
            _render_snapshot_block(
                country=country,
                clusters_for_country=cluster_map.get(country, {}),
                run_comparison_map=run_comparison_map,
                snapshot_context=snapshot_context,
                snapshot_source_by_cluster=snapshot_source_by_cluster,
            )
        )
        lines.extend(
            _render_historical_block(
                country=country,
                historical_records=[record for record in historical_records if record.country == country],
                historical_limited_marker=historical_limited_marker,
                historical_constant_clusters=historical_constant_clusters,
            )
        )
        lines.extend(
            _render_fusion_country_block(
                country=country,
                fusion_group_scores=fusion_group_by_country.get(country, []),
                fusion_total_score=fusion_total_by_country.get(country),
                validation_diagnostic=fusion_validation_by_country.get(country),
            )
        )
        lines.extend(
            _render_fusion_historical_country_block(
                country=country,
                fusion_historical_group_scores=fusion_historical_group_by_country.get(country, []),
                fusion_historical_total_scores=fusion_historical_total_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_v43_country_profile_block(
                country=country,
                country_profile=fusion_validation_profile_by_country.get(country),
                country_peaks=fusion_validation_peak_by_country.get(country, []),
                country_group_profiles=fusion_validation_group_profile_by_country.get(country, []),
                country_peak_attribution=fusion_peak_attribution_by_country.get(country, []),
                country_peak_event_support=fusion_peak_support_by_country.get(country, []),
                country_peak_event_matches=fusion_peak_matches_by_country.get(country, []),
                country_event_alignment=fusion_country_event_alignment_by_country.get(country),
                trajectory_profile=fusion_trajectory_profile_by_country.get(country),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 3) Snapshot-Plots (Land)",
                plot_paths=snapshot_plot_paths_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 4) Historical-Cluster-Plots (Land)",
                plot_paths=historical_cluster_plot_paths_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 5) Historical-Subscore-Plots (Land)",
                plot_paths=historical_subscore_plot_paths_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 6) V3.1 Fusion-Plots (Land)",
                plot_paths=fusion_plot_paths_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 7) V3.2 Historical Fusion Group-Plots (Land)",
                plot_paths=fusion_historical_group_plot_paths_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 8) V3.2 Historical Fusion Total-Plots (Land)",
                plot_paths=fusion_historical_total_plot_paths_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 9) V4.3 Jahresprofil-Plot (Land)",
                plot_paths=v43_country_profile_plot_paths_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 10) V4.3.1 Peak-Attributionsplot (Land)",
                plot_paths=v431_country_peak_plot_paths_by_country.get(country, []),
            )
        )
        lines.extend(
            _render_plot_block(
                heading="### 11) V4.3.2 Event-Alignment-Plot (Land)",
                plot_paths=v432_country_event_alignment_plot_paths_by_country.get(country, []),
            )
        )

    return "\n".join(lines)


def write_handout(text: str, out_path: Path) -> None:
    """
    Persist handout Markdown file.

    Traceability:
    - PSyR-006
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8-sig")
