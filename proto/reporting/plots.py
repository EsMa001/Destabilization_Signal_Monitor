from __future__ import annotations

"""
Traceability:
- PSwR-016
- PM-005
- PSwR-029
- PSwR-032
- PSwR-051
- PSwR-065
- PSwR-066
- PSwR-101
- PSwR-102
- PSR-015
- PSR-016
- PSR-024
- PM-014
- PM-023
- PM-030
- PM-054
"""

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from proto.models import ScoreRecord

if TYPE_CHECKING:
    from proto.fusion.models import (
        FusionGroupScoreRecord,
        FusionHistoricalGroupScoreRecord,
        FusionHistoricalTotalScoreRecord,
    )
    from proto.fusion.validation import (
        ValidationEventRegistryRecord,
        ValidationGlobalPeakSynchronizationRecord,
        ValidationPeakEventMatchRecord,
        ValidationPeakAttributionRecord,
    )
    from proto.scoring.trend_history import HistoricalRollingRecord

SNAPSHOT_FIGSIZE = (11, 5.5)
HISTORICAL_CLUSTER_FIGSIZE = (14, 7)
HISTORICAL_SUBSCORE_FIGSIZE = (16, 8)
FUSION_GROUP_FIGSIZE = (12, 6)
FUSION_HISTORICAL_GROUP_FIGSIZE = (14, 7)
FUSION_HISTORICAL_TOTAL_FIGSIZE = (14, 6)
V43_COUNTRY_PROFILE_FIGSIZE = (14, 8)
V43_MULTI_COUNTRY_FIGSIZE = (14, 7)
V43_RANKING_TRAJECTORY_FIGSIZE = (14, 7)
V431_COUNTRY_ATTRIBUTION_FIGSIZE = (14, 8)
V431_SYNCHRONIZATION_FIGSIZE = (14, 6)
V432_COUNTRY_EVENT_ALIGNMENT_FIGSIZE = (14, 8)
PLOT_DPI = 140


def _configure_date_axis(ax, x_values: list) -> None:
    # Traceability:
    # - PSwR-016
    # - PM-005
    # - PSwR-029
    # - PSwR-032
    # - PSwR-051
    # - PSwR-065
    if not x_values:
        return
    first = x_values[0]
    if not hasattr(first, "year"):
        return
    locator = mdates.AutoDateLocator(minticks=6, maxticks=12)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)


def _period_order_index(period_label: str) -> int:
    """
    Sort helper for monthly labels (YYYY-MM).

    Traceability:
    - PM-024
    """
    year_text, month_text = period_label.split("-", maxsplit=1)
    return int(year_text) * 12 + int(month_text)


def save_line_plot(
    x_values: list,
    y_values: list[float],
    title: str,
    out_path: Path,
    *,
    figsize: tuple[float, float],
) -> None:
    """
    Save a single line plot.

    Traceability:
    - PSwR-016
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    use_markers = len(x_values) <= 60
    if use_markers:
        ax.plot(x_values, y_values, marker="o", markersize=3.5, linewidth=1.8)
    else:
        ax.plot(x_values, y_values, linewidth=1.9)
    ax.set_ylim(0, 100)
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Score")
    ax.grid(alpha=0.3)
    _configure_date_axis(ax, x_values)
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    fig.autofmt_xdate(rotation=30, ha="right")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=PLOT_DPI)
    plt.close(fig)


def save_cluster_score_plots(
    *,
    cluster_scores: list[ScoreRecord],
    out_dir: Path,
) -> list[Path]:
    """
    Save time-series plots per country/cluster.

    Traceability:
    - PSwR-016
    - PSR-005
    - PM-005
    """
    grouped: dict[tuple[str, str], list[ScoreRecord]] = defaultdict(list)
    for score in cluster_scores:
        grouped[(score.country, score.cluster)].append(score)

    output_paths: list[Path] = []
    for (country, cluster), values in sorted(grouped.items()):
        sorted_values = sorted(values, key=lambda item: item.date)
        x_values = [record.date for record in sorted_values]
        y_values = [record.score_value for record in sorted_values]
        out_path = out_dir / f"{country.lower()}_{cluster}_timeseries.png"
        save_line_plot(
            x_values=x_values,
            y_values=y_values,
            title=f"{country} - {cluster} cluster score",
            out_path=out_path,
            figsize=SNAPSHOT_FIGSIZE,
        )
        output_paths.append(out_path)
    return output_paths


def save_historical_cluster_plots(
    *,
    historical_records: list["HistoricalRollingRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save historical rolling cluster plots per country/cluster.

    Traceability:
    - PSwR-029
    - PSwR-032
    - PM-014
    """
    grouped: dict[tuple[str, str], list["HistoricalRollingRecord"]] = defaultdict(list)
    for record in historical_records:
        if record.score_name != "cluster_score":
            continue
        grouped[(record.country, record.cluster)].append(record)

    output_paths: list[Path] = []
    for (country, cluster), values in sorted(grouped.items()):
        sorted_values = sorted(values, key=lambda item: item.date)
        x_values = [record.date for record in sorted_values]
        y_values = [
            record.rolling_value if record.rolling_value is not None else float("nan")
            for record in sorted_values
        ]
        out_path = out_dir / f"historical_cluster_{country.lower()}_{cluster}_timeseries.png"
        save_line_plot(
            x_values=x_values,
            y_values=y_values,
            title=f"{country} - {cluster} historical rolling score",
            out_path=out_path,
            figsize=HISTORICAL_CLUSTER_FIGSIZE,
        )
        output_paths.append(out_path)
    return output_paths


def save_historical_subscore_plots(
    *,
    historical_records: list["HistoricalRollingRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save historical rolling subscore plots per country/cluster.

    Traceability:
    - PSwR-029
    - PSwR-032
    - PM-014
    """
    grouped: dict[tuple[str, str], list["HistoricalRollingRecord"]] = defaultdict(list)
    for record in historical_records:
        if record.score_name == "cluster_score":
            continue
        grouped[(record.country, record.cluster)].append(record)

    output_paths: list[Path] = []
    for (country, cluster), values in sorted(grouped.items()):
        by_subscore: dict[str, list["HistoricalRollingRecord"]] = defaultdict(list)
        for record in values:
            by_subscore[record.score_name].append(record)

        fig = plt.figure(figsize=HISTORICAL_SUBSCORE_FIGSIZE)
        ax = fig.add_subplot(111)
        for score_name, score_values in sorted(by_subscore.items()):
            sorted_values = sorted(score_values, key=lambda item: item.date)
            x_values = [record.date for record in sorted_values]
            y_values = [
                record.rolling_value if record.rolling_value is not None else float("nan")
                for record in sorted_values
            ]
            ax.plot(x_values, y_values, linewidth=1.8, label=score_name)
        ax.set_ylim(0, 100)
        ax.set_title(f"{country} - {cluster} historical rolling subscores", fontsize=12)
        ax.set_xlabel("Date")
        ax.set_ylabel("Score")
        ax.grid(alpha=0.3)
        _configure_date_axis(ax, [record.date for record in values])
        ax.tick_params(axis="x", labelrotation=30, labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        ax.legend(loc="best", fontsize=9)
        fig.autofmt_xdate(rotation=30, ha="right")
        fig.tight_layout()
        out_path = out_dir / f"historical_subscores_{country.lower()}_{cluster}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=PLOT_DPI)
        plt.close(fig)
        output_paths.append(out_path)
    return output_paths


def save_fusion_group_plots(
    *,
    group_scores: list["FusionGroupScoreRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save per-country V3.1 fusion group bar plots.

    Traceability:
    - PSwR-051
    - PSR-015
    """
    grouped: dict[str, list["FusionGroupScoreRecord"]] = defaultdict(list)
    for record in group_scores:
        grouped[record.country].append(record)

    output_paths: list[Path] = []
    for country, records in sorted(grouped.items()):
        sorted_records = sorted(records, key=lambda item: item.group)
        labels = [item.group for item in sorted_records]
        values = [item.group_score if item.group_score is not None else 0.0 for item in sorted_records]
        colors = [
            "#1f77b4" if item.status == "ok" else "#c7c7c7"
            for item in sorted_records
        ]
        fig = plt.figure(figsize=FUSION_GROUP_FIGSIZE)
        ax = fig.add_subplot(111)
        ax.bar(labels, values, color=colors)
        ax.set_ylim(0, 100)
        ax.set_title(f"{country} - V3.1 fusion group scores", fontsize=12)
        ax.set_xlabel("Group")
        ax.set_ylabel("Score")
        ax.grid(axis="y", alpha=0.3)
        ax.tick_params(axis="x", labelrotation=25, labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        fig.tight_layout()
        out_path = out_dir / f"fusion_groups_{country.lower()}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=PLOT_DPI)
        plt.close(fig)
        output_paths.append(out_path)
    return output_paths


def save_fusion_historical_group_plots(
    *,
    historical_group_scores: list["FusionHistoricalGroupScoreRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save per-country historical fusion group line plots.

    Traceability:
    - PSwR-065
    - PM-030
    """
    grouped: dict[str, list["FusionHistoricalGroupScoreRecord"]] = defaultdict(list)
    for record in historical_group_scores:
        grouped[record.country].append(record)

    output_paths: list[Path] = []
    for country, records in sorted(grouped.items()):
        by_group: dict[str, list["FusionHistoricalGroupScoreRecord"]] = defaultdict(list)
        for record in records:
            by_group[record.group].append(record)
        fig = plt.figure(figsize=FUSION_HISTORICAL_GROUP_FIGSIZE)
        ax = fig.add_subplot(111)
        for group, group_values in sorted(by_group.items()):
            sorted_values = sorted(group_values, key=lambda item: item.target_period_end)
            x_values = [item.target_period_end for item in sorted_values]
            y_values = [
                float(item.group_score) if item.group_score is not None else float("nan")
                for item in sorted_values
            ]
            linestyle = "--" if any(item.status == "limited" for item in sorted_values) else "-"
            ax.plot(x_values, y_values, linewidth=1.8, linestyle=linestyle, marker="o", label=group)
        ax.set_ylim(0, 100)
        ax.set_title(f"{country} - V3.2 historical fusion group scores", fontsize=12)
        ax.set_xlabel("Date")
        ax.set_ylabel("Score")
        ax.grid(alpha=0.3)
        _configure_date_axis(ax, [item.target_period_end for item in records])
        ax.tick_params(axis="x", labelrotation=30, labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        ax.legend(loc="best", fontsize=9)
        fig.autofmt_xdate(rotation=30, ha="right")
        fig.tight_layout()
        out_path = out_dir / f"fusion_historical_groups_{country.lower()}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=PLOT_DPI)
        plt.close(fig)
        output_paths.append(out_path)
    return output_paths


def save_fusion_historical_total_plots(
    *,
    historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save per-country historical fusion total line plots.

    Traceability:
    - PSwR-065
    - PM-030
    """
    grouped: dict[str, list["FusionHistoricalTotalScoreRecord"]] = defaultdict(list)
    for record in historical_total_scores:
        grouped[record.country].append(record)

    output_paths: list[Path] = []
    for country, records in sorted(grouped.items()):
        sorted_values = sorted(records, key=lambda item: item.target_period_end)
        x_values = [item.target_period_end for item in sorted_values]
        y_values = [item.fusion_score for item in sorted_values]
        out_path = out_dir / f"fusion_historical_total_{country.lower()}.png"
        save_line_plot(
            x_values=x_values,
            y_values=y_values,
            title=f"{country} - V3.2 historical fusion total score",
            out_path=out_path,
            figsize=FUSION_HISTORICAL_TOTAL_FIGSIZE,
        )
        output_paths.append(out_path)
    return output_paths


def save_v43_country_profile_plots(
    *,
    historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
    historical_group_scores: list["FusionHistoricalGroupScoreRecord"],
    out_dir: Path,
    top_peak_count: int = 3,
) -> list[Path]:
    """
    Save per-country V4.3 356-day profile plots (total curve + group means).

    Traceability:
    - PSwR-101
    - PSwR-065
    - PSR-024
    - PM-054
    """
    if top_peak_count <= 0:
        raise ValueError("top_peak_count must be > 0")

    totals_by_country: dict[str, list["FusionHistoricalTotalScoreRecord"]] = defaultdict(list)
    for record in historical_total_scores:
        totals_by_country[record.country].append(record)

    groups_by_country: dict[str, list["FusionHistoricalGroupScoreRecord"]] = defaultdict(list)
    for record in historical_group_scores:
        groups_by_country[record.country].append(record)

    output_paths: list[Path] = []
    for country, country_totals in sorted(totals_by_country.items()):
        totals_sorted = sorted(country_totals, key=lambda item: item.target_period_end)
        x_values = [item.target_period_end for item in totals_sorted]
        y_values = [float(item.fusion_score) for item in totals_sorted]
        peak_points = sorted(
            totals_sorted,
            key=lambda item: (float(item.fusion_score), item.target_period_end),
            reverse=True,
        )[:top_peak_count]

        mean_group_scores: dict[str, float] = {}
        scored_groups = [
            item
            for item in groups_by_country.get(country, [])
            if item.group_score is not None
        ]
        by_group: dict[str, list[float]] = defaultdict(list)
        for group_item in scored_groups:
            by_group[group_item.group].append(float(group_item.group_score))
        for group, values in by_group.items():
            mean_group_scores[group] = sum(values) / float(len(values))
        top_groups = sorted(mean_group_scores.items(), key=lambda item: item[1], reverse=True)[:5]

        fig, (ax_curve, ax_groups) = plt.subplots(
            2,
            1,
            figsize=V43_COUNTRY_PROFILE_FIGSIZE,
            gridspec_kw={"height_ratios": [2.2, 1.1]},
        )
        ax_curve.plot(x_values, y_values, linewidth=2.0, marker="o", markersize=4, color="#1f77b4")
        if peak_points:
            peak_x = [item.target_period_end for item in peak_points]
            peak_y = [float(item.fusion_score) for item in peak_points]
            ax_curve.scatter(peak_x, peak_y, color="#d62728", s=28, zorder=4, label="Top peaks")
            for index, item in enumerate(peak_points, start=1):
                ax_curve.annotate(
                    f"#{index} {item.period_label}",
                    (item.target_period_end, float(item.fusion_score)),
                    textcoords="offset points",
                    xytext=(0, 8),
                    ha="center",
                    fontsize=8,
                )
            ax_curve.legend(loc="upper left", fontsize=8)
        ax_curve.set_ylim(0, 100)
        ax_curve.set_title(f"{country} - V4.3 fusion total profile (356-day horizon)", fontsize=12)
        ax_curve.set_xlabel("Date")
        ax_curve.set_ylabel("Fusion score")
        ax_curve.grid(alpha=0.3)
        _configure_date_axis(ax_curve, x_values)
        ax_curve.tick_params(axis="x", labelrotation=30, labelsize=9)
        ax_curve.tick_params(axis="y", labelsize=9)

        if top_groups:
            labels = [item[0] for item in top_groups]
            values = [item[1] for item in top_groups]
            ax_groups.bar(labels, values, color="#2ca02c")
            ax_groups.set_ylim(0, 100)
            ax_groups.set_ylabel("Mean group score")
            ax_groups.set_title("Top mean driver groups (historical)", fontsize=10)
            ax_groups.tick_params(axis="x", labelrotation=25, labelsize=8)
            ax_groups.tick_params(axis="y", labelsize=8)
            ax_groups.grid(axis="y", alpha=0.25)
        else:
            ax_groups.text(0.5, 0.5, "no group history available", ha="center", va="center")
            ax_groups.set_axis_off()

        fig.autofmt_xdate(rotation=30, ha="right")
        fig.tight_layout()
        out_path = out_dir / f"v43_country_profile_{country.lower()}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=PLOT_DPI)
        plt.close(fig)
        output_paths.append(out_path)
    return output_paths


def save_v43_multicountry_total_plot(
    *,
    historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save cross-country V4.3 total-score comparison plot.

    Traceability:
    - PSwR-102
    - PSR-024
    - PM-054
    """
    if not historical_total_scores:
        return []

    grouped: dict[str, list["FusionHistoricalTotalScoreRecord"]] = defaultdict(list)
    for record in historical_total_scores:
        grouped[record.country].append(record)

    fig = plt.figure(figsize=V43_MULTI_COUNTRY_FIGSIZE)
    ax = fig.add_subplot(111)
    all_dates: list = []
    for country, records in sorted(grouped.items()):
        sorted_values = sorted(records, key=lambda item: item.target_period_end)
        x_values = [item.target_period_end for item in sorted_values]
        y_values = [float(item.fusion_score) for item in sorted_values]
        all_dates.extend(x_values)
        ax.plot(x_values, y_values, linewidth=1.8, marker="o", markersize=3.0, label=country)
    ax.set_ylim(0, 100)
    ax.set_title("V4.3 multi-country fusion total comparison", fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Fusion score")
    ax.grid(alpha=0.3)
    _configure_date_axis(ax, all_dates)
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.legend(loc="best", fontsize=8, ncol=2)
    fig.autofmt_xdate(rotation=30, ha="right")
    fig.tight_layout()
    out_path = out_dir / "v43_multicountry_fusion_total.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=PLOT_DPI)
    plt.close(fig)
    return [out_path]


def save_v43_ranking_trajectory_plot(
    *,
    historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save V4.3 period-level country ranking trajectory plot.

    Traceability:
    - PSwR-102
    - PSR-024
    - ALG-039
    """
    if not historical_total_scores:
        return []

    by_period: dict[str, list["FusionHistoricalTotalScoreRecord"]] = defaultdict(list)
    for record in historical_total_scores:
        by_period[record.period_label].append(record)

    period_labels = sorted(by_period.keys(), key=_period_order_index)
    rank_series: dict[str, list[tuple[date, int]]] = defaultdict(list)
    for period_label in period_labels:
        period_records = sorted(
            by_period[period_label],
            key=lambda item: (float(item.fusion_score), item.country),
            reverse=True,
        )
        for rank, record in enumerate(period_records, start=1):
            rank_series[record.country].append((record.target_period_end, rank))

    fig = plt.figure(figsize=V43_RANKING_TRAJECTORY_FIGSIZE)
    ax = fig.add_subplot(111)
    all_dates: list = []
    max_rank = 1
    for country, values in sorted(rank_series.items()):
        x_values = [item[0] for item in values]
        y_values = [item[1] for item in values]
        all_dates.extend(x_values)
        max_rank = max(max_rank, max(y_values, default=1))
        ax.plot(x_values, y_values, linewidth=1.8, marker="o", markersize=3.0, label=country)
    ax.set_ylim(max_rank + 0.5, 0.5)
    ax.set_title("V4.3 multi-country ranking trajectory", fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Rank (1=highest fusion score)")
    ax.grid(alpha=0.3)
    _configure_date_axis(ax, all_dates)
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.legend(loc="best", fontsize=8, ncol=2)
    fig.autofmt_xdate(rotation=30, ha="right")
    fig.tight_layout()
    out_path = out_dir / "v43_multicountry_ranking_trajectory.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=PLOT_DPI)
    plt.close(fig)
    return [out_path]


def save_v431_country_peak_attribution_plots(
    *,
    historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
    peak_attribution_records: list["ValidationPeakAttributionRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save V4.3.1 per-country plots with explicit peak-attribution annotations.

    Traceability:
    - PSwR-111
    - PM-059
    - ALG-044
    """
    totals_by_country: dict[str, list["FusionHistoricalTotalScoreRecord"]] = defaultdict(list)
    for record in historical_total_scores:
        totals_by_country[record.country].append(record)

    peaks_by_country: dict[str, list["ValidationPeakAttributionRecord"]] = defaultdict(list)
    for record in peak_attribution_records:
        peaks_by_country[record.country].append(record)

    label_color = {
        "event_supported_peak": "#2ca02c",
        "country_specific_peak": "#1f77b4",
        "globally_co_moving_peak": "#ff7f0e",
        "global_background_stress_peak": "#9467bd",
        "model_driven_peak": "#d62728",
        "weakly_supported_peak": "#8c564b",
    }

    output_paths: list[Path] = []
    for country, totals in sorted(totals_by_country.items()):
        totals_sorted = sorted(totals, key=lambda item: item.target_period_end)
        x_values = [item.target_period_end for item in totals_sorted]
        y_values = [float(item.fusion_score) for item in totals_sorted]
        peaks = sorted(
            peaks_by_country.get(country, []),
            key=lambda item: item.peak_rank,
        )

        fig = plt.figure(figsize=V431_COUNTRY_ATTRIBUTION_FIGSIZE)
        ax = fig.add_subplot(111)
        ax.plot(
            x_values,
            y_values,
            linewidth=1.9,
            marker="o",
            markersize=3.6,
            color="#1f77b4",
            label="fusion_total",
        )
        rendered_labels: set[str] = set()
        for peak in peaks:
            color = label_color.get(peak.attribution_label, "#7f7f7f")
            plot_label = peak.attribution_label if peak.attribution_label not in rendered_labels else None
            rendered_labels.add(peak.attribution_label)
            ax.scatter(
                [peak.target_period_end],
                [peak.fusion_score],
                color=color,
                edgecolor="black",
                linewidth=0.4,
                s=40,
                zorder=4,
                label=plot_label,
            )
            annotation = (
                f"#{peak.peak_rank} {peak.dominant_group or 'n/a'} "
                f"{peak.event_support_status}"
            )
            ax.annotate(
                annotation,
                (peak.target_period_end, peak.fusion_score),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=7,
            )

        ax.set_ylim(0, 100)
        ax.set_title(f"{country} - V4.3.1 peak attribution view", fontsize=12)
        ax.set_xlabel("Date")
        ax.set_ylabel("Fusion score")
        ax.grid(alpha=0.28)
        _configure_date_axis(ax, x_values)
        ax.tick_params(axis="x", labelrotation=30, labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        ax.legend(loc="best", fontsize=8, ncol=2)
        fig.autofmt_xdate(rotation=30, ha="right")
        fig.tight_layout()
        out_path = out_dir / f"v431_peak_attribution_{country.lower()}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=PLOT_DPI)
        plt.close(fig)
        output_paths.append(out_path)
    return output_paths


def save_v431_peak_synchronization_plot(
    *,
    synchronization_records: list["ValidationGlobalPeakSynchronizationRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save V4.3.1 cross-country peak synchronization diagnostics plot.

    Traceability:
    - PSwR-110
    - PSwR-111
    - PM-062
    - ALG-047
    """
    if not synchronization_records:
        return []

    ordered = sorted(synchronization_records, key=lambda item: item.target_period_end)
    x_values = [item.target_period_end for item in ordered]
    ratio_values = [float(item.peak_country_ratio) * 100.0 for item in ordered]
    global_values = [float(item.mean_global_share) * 100.0 for item in ordered]
    country_values = [float(item.mean_country_specific_share) * 100.0 for item in ordered]

    fig = plt.figure(figsize=V431_SYNCHRONIZATION_FIGSIZE)
    ax = fig.add_subplot(111)
    ax.plot(
        x_values,
        ratio_values,
        linewidth=2.0,
        marker="o",
        markersize=4.0,
        color="#d62728",
        label="peak_country_ratio",
    )
    ax.plot(
        x_values,
        global_values,
        linewidth=1.8,
        marker="s",
        markersize=3.5,
        color="#ff7f0e",
        label="mean_global_share",
    )
    ax.plot(
        x_values,
        country_values,
        linewidth=1.8,
        marker="^",
        markersize=3.5,
        color="#2ca02c",
        label="mean_country_specific_share",
    )
    ax.axhline(55.0, color="#777777", linestyle="--", linewidth=1.1, alpha=0.8)
    ax.set_ylim(0, 100)
    ax.set_title("V4.3.1 global peak synchronization diagnostics", fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Ratio/share (%)")
    ax.grid(alpha=0.28)
    _configure_date_axis(ax, x_values)
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.legend(loc="best", fontsize=8)
    fig.autofmt_xdate(rotation=30, ha="right")
    fig.tight_layout()
    out_path = out_dir / "v431_global_peak_synchronization.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=PLOT_DPI)
    plt.close(fig)
    return [out_path]


def save_v432_country_event_alignment_plots(
    *,
    historical_total_scores: list["FusionHistoricalTotalScoreRecord"],
    peak_event_match_records: list["ValidationPeakEventMatchRecord"],
    event_registry_records: list["ValidationEventRegistryRecord"],
    out_dir: Path,
) -> list[Path]:
    """
    Save V4.3.2 per-country plots for peak-event alignment review.

    Traceability:
    - PSwR-121
    - PM-071
    - ALG-056
    """
    totals_by_country: dict[str, list["FusionHistoricalTotalScoreRecord"]] = defaultdict(list)
    for record in historical_total_scores:
        totals_by_country[record.country].append(record)

    peaks_by_country: dict[str, list["ValidationPeakEventMatchRecord"]] = defaultdict(list)
    for record in peak_event_match_records:
        peaks_by_country[record.country].append(record)

    events_by_country: dict[str, list["ValidationEventRegistryRecord"]] = defaultdict(list)
    for record in event_registry_records:
        events_by_country[record.country].append(record)

    class_style = {
        "direct_match": ("#2ca02c", "o", "direct_match"),
        "plausible_context_match": ("#1f77b4", "s", "plausible_context_match"),
        "weak_match": ("#ff7f0e", "^", "weak_match"),
        "no_credible_match": ("#d62728", "x", "no_credible_match"),
        "multi_event_overlap": ("#9467bd", "D", "multi_event_overlap"),
    }
    event_palette = [
        "#d9d9d9",
        "#c7d4e8",
        "#d7e9d0",
        "#f0dfca",
    ]

    output_paths: list[Path] = []
    for country, totals in sorted(totals_by_country.items()):
        totals_sorted = sorted(totals, key=lambda item: item.target_period_end)
        x_values = [item.target_period_end for item in totals_sorted]
        y_values = [float(item.fusion_score) for item in totals_sorted]
        peaks = sorted(
            peaks_by_country.get(country, []),
            key=lambda item: (item.target_period_end, item.peak_rank),
        )
        events = sorted(
            events_by_country.get(country, []),
            key=lambda item: (item.start_date, item.event_id),
        )

        fig = plt.figure(figsize=V432_COUNTRY_EVENT_ALIGNMENT_FIGSIZE)
        ax = fig.add_subplot(111)
        ax.plot(
            x_values,
            y_values,
            linewidth=1.9,
            marker="o",
            markersize=3.4,
            color="#111111",
            label="fusion_total",
        )

        for index, event in enumerate(events):
            color = event_palette[index % len(event_palette)]
            label = "event_window" if index == 0 else None
            ax.axvspan(
                event.start_date,
                event.end_date,
                color=color,
                alpha=0.23,
                linewidth=0.0,
                label=label,
            )
            if index < 6:
                midpoint = event.start_date + (event.end_date - event.start_date) / 2
                ax.annotate(
                    event.event_id,
                    (midpoint, 3.5 + (index % 3) * 3.8),
                    fontsize=7,
                    color="#444444",
                    ha="center",
                )

        rendered_labels: set[str] = set()
        for peak in peaks:
            color, marker, label = class_style.get(
                peak.match_class,
                ("#7f7f7f", "o", peak.match_class),
            )
            plot_label = label if label not in rendered_labels else None
            rendered_labels.add(label)
            ax.scatter(
                [peak.target_period_end],
                [peak.fusion_score],
                color=color,
                marker=marker,
                edgecolor="black" if marker != "x" else color,
                linewidth=0.5,
                s=46,
                zorder=5,
                label=plot_label,
            )
            class_short = {
                "direct_match": "D",
                "plausible_context_match": "C",
                "weak_match": "W",
                "no_credible_match": "N",
                "multi_event_overlap": "M",
            }.get(peak.match_class, "?")
            ax.annotate(
                f"#{peak.peak_rank}-{class_short}",
                (peak.target_period_end, peak.fusion_score),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=7,
            )

        ax.set_ylim(0, 100)
        ax.set_title(f"{country} - V4.3.2 peak-event alignment", fontsize=12)
        ax.set_xlabel("Date")
        ax.set_ylabel("Fusion score")
        ax.grid(alpha=0.25)
        _configure_date_axis(ax, x_values)
        ax.tick_params(axis="x", labelrotation=30, labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        ax.legend(loc="best", fontsize=7, ncol=2)
        fig.autofmt_xdate(rotation=30, ha="right")
        fig.tight_layout()
        out_path = out_dir / f"v432_event_alignment_{country.lower()}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=PLOT_DPI)
        plt.close(fig)
        output_paths.append(out_path)
    return output_paths
