from __future__ import annotations

"""
Traceability:
- PSyR-009
- PSwR-017
"""

from pathlib import Path
import json

from proto.reporting.presentation import cluster_order_index, country_order_index

TREND_INCREASING = "zunehmend"
TREND_DECREASING = "r\u00fcckl\u00e4ufig"
TREND_STABLE = "stabil"
TREND_NO_COMPARISON = "kein_vergleich"


def load_summary_records(path: Path) -> list[dict]:
    """
    Load summary records from JSON export.

    Traceability:
    - PSyR-009
    """
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    return raw.get("records", [])


def load_run_metadata(path: Path | None) -> dict:
    """
    Load run metadata with safe defaults.

    Traceability:
    - PSyR-008
    - PSyR-009
    """
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _delta_direction(value: float | None) -> str:
    if value is None:
        return TREND_NO_COMPARISON
    if value > 0.5:
        return TREND_INCREASING
    if value < -0.5:
        return TREND_DECREASING
    return TREND_STABLE


def compare_summary_records(
    current: list[dict],
    baseline: list[dict],
) -> list[dict]:
    """
    Compare summary records by country+cluster with explicit delta semantics.

    Traceability:
    - PSyR-009
    """
    baseline_map = {(entry["country"], entry["cluster"]): entry for entry in baseline}
    comparisons: list[dict] = []
    sorted_current = sorted(
        current,
        key=lambda entry: (
            country_order_index(entry["country"]),
            cluster_order_index(entry["cluster"]),
        ),
    )
    for entry in sorted_current:
        key = (entry["country"], entry["cluster"])
        baseline_entry = baseline_map.get(key)
        current_score = float(entry["cluster_score"])
        if baseline_entry is None:
            comparisons.append(
                {
                    "country": entry["country"],
                    "cluster": entry["cluster"],
                    "current_score": current_score,
                    "baseline_score": None,
                    "delta_absolute": None,
                    "delta_relative_percent": None,
                    "delta_direction": TREND_NO_COMPARISON,
                }
            )
            continue

        baseline_score = float(baseline_entry["cluster_score"])
        delta = round(current_score - baseline_score, 4)
        if abs(baseline_score) < 1e-9:
            delta_relative = None
        else:
            delta_relative = round((delta / baseline_score) * 100.0, 2)

        comparisons.append(
            {
                "country": entry["country"],
                "cluster": entry["cluster"],
                "current_score": current_score,
                "baseline_score": baseline_score,
                "delta_absolute": delta,
                "delta_relative_percent": delta_relative,
                "delta_direction": _delta_direction(delta),
            }
        )
    return comparisons


def _comparison_overview(comparisons: list[dict]) -> dict[str, int]:
    totals = {
        "items": len(comparisons),
        TREND_INCREASING: 0,
        TREND_DECREASING: 0,
        TREND_STABLE: 0,
        TREND_NO_COMPARISON: 0,
    }
    for entry in comparisons:
        direction = entry["delta_direction"]
        totals[direction] = totals.get(direction, 0) + 1
    return totals


def write_run_comparison(
    *,
    current_summary_path: Path,
    baseline_summary_path: Path | None,
    out_path: Path,
    baseline_label: str,
    current_run_info: dict,
    baseline_metadata_path: Path | None,
) -> dict:
    """
    Write robust comparison payload for previous or reference baseline.

    Traceability:
    - PSyR-009
    - PSyR-010
    """
    current = load_summary_records(current_summary_path)
    baseline = load_summary_records(baseline_summary_path) if baseline_summary_path else []
    baseline_info = load_run_metadata(baseline_metadata_path)

    if not baseline:
        payload = {
            "status": f"no_{baseline_label}",
            "baseline_label": baseline_label,
            "current_run": current_run_info,
            "baseline_run": baseline_info,
            "overview": _comparison_overview([]),
            "comparisons": [],
        }
    else:
        comparisons = compare_summary_records(current, baseline)
        payload = {
            "status": "ok",
            "baseline_label": baseline_label,
            "current_run": current_run_info,
            "baseline_run": baseline_info,
            "overview": _comparison_overview(comparisons),
            "comparisons": comparisons,
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload
