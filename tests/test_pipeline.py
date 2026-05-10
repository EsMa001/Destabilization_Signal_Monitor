from __future__ import annotations

import csv
from pathlib import Path
import json
import shutil

from proto.pipeline.run_proto import main
from proto.reporting.plots import (
    FUSION_GROUP_FIGSIZE,
    FUSION_HISTORICAL_GROUP_FIGSIZE,
    FUSION_HISTORICAL_TOTAL_FIGSIZE,
    HISTORICAL_CLUSTER_FIGSIZE,
    HISTORICAL_SUBSCORE_FIGSIZE,
    SNAPSHOT_FIGSIZE,
)
from tools.create_review_bundle import ReviewBundleConfig, create_review_bundle

STATUS_LIMITED = "eingeschr\u00e4nkt brauchbar"
EXPECTED_COUNTRIES = [
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


def _load_json(path: Path) -> dict:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    return json.loads(path.read_text(encoding="utf-8"))


def _prepare_workspace(project_root: Path, tmp_path: Path) -> None:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    shutil.copytree(project_root / "config", tmp_path / "config")
    shutil.copytree(project_root / "data", tmp_path / "data")


def _country_block(handout: str, country_label: str) -> str:
    # Traceability:
    # - PSR-003
    # - PSR-005
    # - PSR-009
    # - PSR-010
    # - PSR-011
    # - PSR-012
    marker = f"## {country_label}"
    start = handout.index(marker)
    next_index = handout.find("\n## ", start + len(marker))
    if next_index == -1:
        return handout[start:]
    return handout[start:next_index]


def test_pipeline_creates_required_outputs_and_v31_handout(tmp_path, monkeypatch):
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
    - PSR-017
    - PSR-018
    - PSR-019
    - PSR-021
    - PSR-023
    - PSR-024
    - PSR-025
    - PSR-026
    - PSyR-006
    - PSyR-007
    - PSyR-008
    - PSyR-011
    - PSyR-012
    - PSyR-015
    - PSyR-016
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
    - PSyR-030
    - PSyR-031
    - PSyR-034
    - PSyR-035
    - PSyR-036
    - PSyR-037
    - PSyR-038
    - PSyR-039
    - PSyR-040
    - PSyR-041
    - PSyR-042
    - PSyR-043
    - PSwR-015
    - PSwR-016
    - PSwR-029
    - PSwR-030
    - PSwR-032
    - PSwR-033
    - PSwR-034
    - PSwR-036
    - PSwR-039
    - PSwR-040
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
    - PSwR-057
    - PSwR-058
    - PSwR-059
    - PSwR-060
    - PSwR-061
    - PSwR-062
    - PSwR-063
    - PSwR-064
    - PSwR-065
    - PSwR-066
    - PSwR-067
    - PSwR-068
    - PSwR-069
    - PSwR-070
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
    - PSwR-091
    - PSwR-092
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
    - PSwR-105
    - PSwR-106
    - PSwR-107
    - PSwR-108
    - PSwR-109
    - PSwR-110
    - PSwR-111
    - PSwR-112
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
    - TV-PSwR-051-001
    - TV-PSwR-047-001
    - TV-PSwR-053-001
    - TV-PSwR-057-001
    - TV-PSwR-058-002
    - TV-PSwR-064-001
    - TV-PSwR-065-001
    - TV-PSwR-066-001
    - TV-PSwR-066-002
    - TV-PSwR-069-001
    - TV-PSwR-069-002
    - TV-PSwR-029-004
    - TV-PSR-010-002
    - TV-PSyR-012-001
    - TV-PSwR-034-002
    - TV-PSwR-080-001
    - TV-PSwR-095-001
    - TV-PSwR-096-001
    - TV-PSwR-098-002
    - TV-PSwR-107-001
    - TV-PSwR-108-001
    - TV-PSwR-109-001
    - TV-PSwR-111-001
    - TV-PSwR-113-001
    - TV-PSwR-114-001
    - TV-PSwR-115-001
    - TV-PSwR-116-001
    - TV-PSwR-117-001
    - TV-PSwR-118-001
    - TV-PSwR-119-001
    - TV-PSwR-120-001
    - TV-PSwR-121-001
    - TV-PSwR-123-001
    - TV-PSwR-124-001
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)
    main()

    run_dir = Path("outputs/runs/current_run")
    reference_dir = Path("outputs/reference/current_reference")
    assert (run_dir / "handout.md").exists()
    assert (run_dir / "run_metadata.json").exists()
    assert (run_dir / "run_status.txt").exists()
    assert (run_dir / "run_comparison.json").exists()
    assert (run_dir / "reference_comparison.json").exists()

    # Snapshot + historical official artifact split.
    assert (run_dir / "exports/snapshot/features_export.csv").exists()
    assert (run_dir / "exports/snapshot/scores_export.csv").exists()
    assert (run_dir / "exports/snapshot/summary_export.json").exists()
    assert (run_dir / "exports/snapshot/snapshot_status.json").exists()
    assert (run_dir / "exports/historical/historical_timeseries.csv").exists()
    assert (run_dir / "exports/historical/historical_status.json").exists()
    assert (run_dir / "exports/historical/review_candidates.csv").exists()
    assert (run_dir / "exports/historical/review_candidates.json").exists()
    assert (run_dir / "exports/fusion/observations.csv").exists()
    assert (run_dir / "exports/fusion/source_signals.csv").exists()
    assert (run_dir / "exports/fusion/group_scores.csv").exists()
    assert (run_dir / "exports/fusion/fusion_total_scores.json").exists()
    assert (run_dir / "exports/fusion/historical_source_signals.csv").exists()
    assert (run_dir / "exports/fusion/historical_group_scores.csv").exists()
    assert (run_dir / "exports/fusion/historical_total_scores.csv").exists()
    assert (run_dir / "exports/fusion/fusion_status.json").exists()
    assert (run_dir / "exports/fusion/validation_framework.json").exists()
    assert (run_dir / "exports/fusion/validation_reference_episodes.csv").exists()
    assert (run_dir / "exports/fusion/validation_episode_review.csv").exists()
    assert (run_dir / "exports/fusion/validation_country_ranking.csv").exists()
    assert (run_dir / "exports/fusion/validation_layer_diagnostics.csv").exists()
    assert (run_dir / "exports/fusion/validation_freshness_groups.csv").exists()
    assert (run_dir / "exports/fusion/validation_historical_responsiveness.csv").exists()
    assert (run_dir / "exports/fusion/validation_country_profiles.csv").exists()
    assert (run_dir / "exports/fusion/validation_peak_phases.csv").exists()
    assert (run_dir / "exports/fusion/validation_group_profiles.csv").exists()
    assert (run_dir / "exports/fusion/validation_ranking_trajectory.csv").exists()
    assert (run_dir / "exports/fusion/event_registry.csv").exists()
    assert (run_dir / "exports/fusion/event_marker_registry.csv").exists()
    assert (run_dir / "exports/fusion/peak_attribution.csv").exists()
    assert (run_dir / "exports/fusion/peak_event_support.csv").exists()
    assert (run_dir / "exports/fusion/peak_event_matches.csv").exists()
    assert (run_dir / "exports/fusion/event_coverage_summary.csv").exists()
    assert (run_dir / "exports/fusion/country_event_alignment.csv").exists()
    assert (run_dir / "exports/fusion/event_alignment_summary.json").exists()
    assert (run_dir / "exports/fusion/event_alignment_review.md").exists()
    assert (run_dir / "exports/fusion/trajectory_profiles.csv").exists()
    assert (run_dir / "exports/fusion/global_peak_synchronization.csv").exists()
    assert (run_dir / "exports/fusion/validation_summary.json").exists()
    with (run_dir / "exports/historical/historical_timeseries.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert any(row["score_name"] == "cluster_score" for row in rows)
    assert any(row["score_name"] != "cluster_score" for row in rows)
    with (run_dir / "exports/historical/review_candidates.csv").open(encoding="utf-8") as handle:
        review_rows = list(csv.DictReader(handle))
    assert review_rows
    required_review_fields = {
        "rank",
        "country",
        "cluster",
        "date",
        "rolling_value",
        "is_valid",
        "valid_days",
        "coverage_ratio",
        "stage",
        "trend",
        "confidence_score",
        "confidence_level",
        "snapshot_relation",
        "top_driver_1_name",
    }
    assert required_review_fields.issubset(set(review_rows[0].keys()))
    assert all(row["cluster"] in {"tension", "escalation"} for row in review_rows)
    assert all(row["baseline_marker"] == "False" for row in review_rows)
    ranks = [int(row["rank"]) for row in review_rows]
    assert ranks == list(range(1, len(review_rows) + 1))
    assert any(
        row["cluster"] == "tension" and row["top_driver_1_name"]
        for row in review_rows
    )

    # V2.1 fallback compatibility still present.
    assert (run_dir / "exports/features_export.csv").exists()
    assert (run_dir / "exports/scores_export.csv").exists()
    assert (run_dir / "exports/summary_export.json").exists()

    # Plot structure.
    assert any((run_dir / "plots/snapshot").glob("*.png"))
    assert any((run_dir / "plots/historical/clusters").glob("*.png"))
    assert any((run_dir / "plots/historical/subscores").glob("*.png"))
    assert any((run_dir / "plots/fusion").glob("*.png"))
    assert any((run_dir / "plots/fusion").glob("fusion_historical_groups_*.png"))
    assert any((run_dir / "plots/fusion").glob("fusion_historical_total_*.png"))
    assert any((run_dir / "plots/fusion").glob("v43_country_profile_*.png"))
    assert (run_dir / "plots/fusion/v43_multicountry_fusion_total.png").exists()
    assert (run_dir / "plots/fusion/v43_multicountry_ranking_trajectory.png").exists()
    assert any((run_dir / "plots/fusion").glob("v431_peak_attribution_*.png"))
    assert (run_dir / "plots/fusion/v431_global_peak_synchronization.png").exists()
    assert any((run_dir / "plots/fusion").glob("v432_event_alignment_*.png"))
    assert (reference_dir / "reference_info.json").exists()

    handout_bytes = (run_dir / "handout.md").read_bytes()
    assert handout_bytes.startswith(b"\xef\xbb\xbf")
    handout = handout_bytes.decode("utf-8")
    assert "# Country Destabilization Prototype V4.3.2 - Handout" in handout
    assert "## Run-Zusammenfassung" in handout
    assert "## Versionsst\u00e4nde" in handout
    assert "## Vergleich zum letzten Run (gesamt)" in handout
    assert "## Top historical review candidates" in handout
    assert "## V3.1 Layer/Fusion Snapshot (zusaetzlich)" in handout
    assert "## V3.2 Historical Fusion View (zusaetzlich)" in handout
    assert "## V4.3 Comparative Expansion: 10 Countries, Full 356-Day Profiles" in handout
    assert "## V4.3 Vertiefende Diagnostik" in handout
    assert "## V4.3.1 Peak Attribution & Event Alignment Hardening" in handout
    assert "## V4.3.2 Analyst Event Registry & Real-World Alignment" in handout
    assert "## Fusion Plausibility Warnings" in handout
    assert "## V4.2 Governance, Validation & Operational Freshness (zusaetzlich)" in handout
    assert "### 2b) V3.1 Layer/Fusion (zusaetzlich)" in handout
    assert "### 2c) V3.2 Historical Fusion (zusaetzlich)" in handout
    assert "### 2d) V4.3 Jahresprofil (zusaetzlich)" in handout
    assert "## V3.1 Fusion-Plots (gesamt)" in handout
    assert "## V3.2 Historical Fusion Group-Plots (gesamt)" in handout
    assert "## V3.2 Historical Fusion Total-Plots (gesamt)" in handout
    assert "## V4.3 Vergleichsplots (laenderuebergreifend)" in handout
    assert "## V4.3 Pro-Land-Jahresprofil-Plots (gesamt)" in handout
    assert "## V4.3.1 Peak-Synchronisationsplots (gesamt)" in handout
    assert "## V4.3.1 Peak-Attributionsplots (gesamt)" in handout
    assert "## V4.3.2 Event-Alignment-Plots (gesamt)" in handout
    assert "Top historical review candidates" in handout
    has_low_coverage_marker = (
        "Fruehe historische Perioden sind eingeschraenkt interpretierbar" in handout
        or "Fruehe historische Perioden sind reduziert interpretierbar" in handout
        or "Historische Aussagekraft eingeschraenkt" in handout
        or "Historische Aussagekraft reduziert" in handout
    )
    has_low_coverage_state = (
        "Interpretation=limited_historical_coverage" in handout
        or "Interpretation=reduced_historical_coverage" in handout
    )
    if has_low_coverage_state:
        assert has_low_coverage_marker
    for country in EXPECTED_COUNTRIES:
        assert f"## {country}" in handout
    assert handout.index("## V4.3 Comparative Expansion: 10 Countries, Full 356-Day Profiles") < handout.index("## Germany")
    assert "### 1) Current Snapshot (offiziell)" in handout
    assert "### 2) Historical Rolling Trend (offiziell)" in handout
    assert "Jahreskontext: aktuell=" in handout
    assert "letzter gueltiger Trendpunkt=" in handout
    assert "Snapshot-Herkunft:" in handout
    assert "Baseline-Cluster" in handout
    assert "Freshness-Coverage:" in handout
    assert "Freshness-Diagnose:" in handout
    assert "Peak-Klassen:" in handout
    assert "## Historical-Trend-Plots Cluster (gesamt)" in handout
    assert "## Historical-Trend-Plots Subscores (gesamt)" in handout
    assert "manual review required: keine Plotdateien gefunden." not in handout

    historical_status = _load_json(run_dir / "exports/historical/historical_status.json")
    assert "vulnerability" in historical_status["constant_clusters"]
    assert historical_status["method_notes"]["vulnerability_cluster_role"] == "structural_baseline_cluster"

    snapshot_status = _load_json(run_dir / "exports/snapshot/snapshot_status.json")
    assert snapshot_status["snapshot_rule_version"] == "v2.2.1"
    assert snapshot_status["overview"]["items"] == len(EXPECTED_COUNTRIES) * 3
    assert (
        snapshot_status["overview"]["modes"].get("historical_valid_endpoint", 0)
        >= len(EXPECTED_COUNTRIES)
    )

    fusion_totals = _load_json(run_dir / "exports/fusion/fusion_total_scores.json")
    assert len(fusion_totals) == len(EXPECTED_COUNTRIES)
    assert all(item["fusion_score"] >= 0.0 for item in fusion_totals)
    assert all("confidence_score" in item for item in fusion_totals)
    assert all(item["available_group_count"] >= 7 for item in fusion_totals)

    fusion_groups = list(csv.DictReader((run_dir / "exports/fusion/group_scores.csv").open(encoding="utf-8")))
    assert fusion_groups
    assert any(row["group"] == "market_food" and row["status"] == "ok" for row in fusion_groups)
    assert any(row["group"] == "structural" and row["status"] == "ok" for row in fusion_groups)
    assert any(row["group"] == "narrative" and row["status"] in {"ok", "limited"} for row in fusion_groups)
    assert any(row["group"] == "shock" and row["status"] in {"ok", "limited"} for row in fusion_groups)
    assert any(row["group"] == "displacement" and row["status"] in {"ok", "limited"} for row in fusion_groups)
    assert any(row["group"] == "event" and row["status"] in {"ok", "limited"} for row in fusion_groups)
    assert any(row["group"] == "governance" and row["status"] in {"ok", "limited"} for row in fusion_groups)

    fusion_signals = list(csv.DictReader((run_dir / "exports/fusion/source_signals.csv").open(encoding="utf-8")))
    assert fusion_signals
    assert any(row["source_id"] == "fao_ffpi" for row in fusion_signals)
    assert any(row["source_id"] == "fao_fpma" for row in fusion_signals)
    assert any(row["source_id"] == "un_comtrade" for row in fusion_signals)
    assert any(row["source_id"] == "gdacs" for row in fusion_signals)
    assert any(row["source_id"] == "unhcr" for row in fusion_signals)
    assert any(row["source_id"] == "narrative_input" for row in fusion_signals)
    assert any(row["source_id"] == "governance_input" for row in fusion_signals)
    assert any(row["source_id"] == "gdelt_event" for row in fusion_signals)

    fusion_observations = list(csv.DictReader((run_dir / "exports/fusion/observations.csv").open(encoding="utf-8")))
    assert fusion_observations
    assert any(row["native_periodicity"] == "monthly" for row in fusion_observations)
    assert any(row["native_periodicity"] == "annual" for row in fusion_observations)
    assert any(row["layer"] == "Event" for row in fusion_observations)
    assert any(row["layer"] == "Governance" for row in fusion_observations)
    assert any(row["layer"] == "Shock" for row in fusion_observations)
    assert any(row["layer"] == "Displacement" for row in fusion_observations)
    assert any(row["layer"] == "Narrative" for row in fusion_observations)

    fusion_historical_groups = list(
        csv.DictReader((run_dir / "exports/fusion/historical_group_scores.csv").open(encoding="utf-8"))
    )
    fusion_historical_totals = list(
        csv.DictReader((run_dir / "exports/fusion/historical_total_scores.csv").open(encoding="utf-8"))
    )
    assert fusion_historical_groups
    assert fusion_historical_totals
    assert any(row["group"] == "shock" for row in fusion_historical_groups)
    assert any(row["group"] == "displacement" for row in fusion_historical_groups)
    assert any(row["group"] == "narrative" for row in fusion_historical_groups)
    assert any(row["group"] == "event" for row in fusion_historical_groups)
    assert any(row["group"] == "governance" for row in fusion_historical_groups)
    assert all(row["period_label"] for row in fusion_historical_totals)
    assert any(row["dominant_group"] for row in fusion_historical_totals)
    assert all("expected_group_count" in row for row in fusion_historical_totals)
    assert all("available_group_ratio" in row for row in fusion_historical_totals)
    assert all("top_positive_group_1" in row for row in fusion_historical_totals)
    assert all("top_positive_group_2" in row for row in fusion_historical_totals)
    assert all("strongest_change_group" in row for row in fusion_historical_totals)
    assert all("no_material_change" in row for row in fusion_historical_totals)
    assert all("interpretation_status" in row for row in fusion_historical_totals)
    assert all(
        row["interpretation_status"] in {
            "standard",
            "limited_historical_coverage",
            "reduced_historical_coverage",
        }
        for row in fusion_historical_totals
    )
    if any(float(row["available_group_ratio"]) < 0.75 for row in fusion_historical_totals):
        assert any(
            row["interpretation_status"] in {"limited_historical_coverage", "reduced_historical_coverage"}
            for row in fusion_historical_totals
        )
    assert "Interpretation=" in handout

    event_registry_rows = list(
        csv.DictReader((run_dir / "exports/fusion/event_registry.csv").open(encoding="utf-8"))
    )
    assert event_registry_rows
    assert set(row["country"] for row in event_registry_rows) == set(EXPECTED_COUNTRIES)
    assert all(row.get("event_id") for row in event_registry_rows)
    assert all(row.get("event_type") for row in event_registry_rows)

    peak_event_match_rows = list(
        csv.DictReader((run_dir / "exports/fusion/peak_event_matches.csv").open(encoding="utf-8"))
    )
    assert peak_event_match_rows
    assert all(row["country"] in set(EXPECTED_COUNTRIES) for row in peak_event_match_rows)
    assert all(row["match_class"] in {"direct_match", "plausible_context_match", "weak_match", "no_credible_match", "multi_event_overlap"} for row in peak_event_match_rows)
    assert all("match_confidence" in row for row in peak_event_match_rows)

    event_coverage_rows = list(
        csv.DictReader((run_dir / "exports/fusion/event_coverage_summary.csv").open(encoding="utf-8"))
    )
    assert event_coverage_rows
    assert any(row["scope"] == "global" for row in event_coverage_rows)
    assert any(row["scope"] == "country" for row in event_coverage_rows)

    country_event_alignment_rows = list(
        csv.DictReader((run_dir / "exports/fusion/country_event_alignment.csv").open(encoding="utf-8"))
    )
    assert len(country_event_alignment_rows) == len(EXPECTED_COUNTRIES)
    assert all(row["country"] in set(EXPECTED_COUNTRIES) for row in country_event_alignment_rows)
    assert all("alignment_maturity" in row for row in country_event_alignment_rows)
    assert all("open_uncertainties" in row for row in country_event_alignment_rows)

    fusion_status = _load_json(run_dir / "exports/fusion/fusion_status.json")
    assert "plausibility_warnings" in fusion_status
    assert "plausibility_warning_count" in fusion_status
    assert "validation_summary" in fusion_status
    assert fusion_status["validation_summary"]["episode_count"] >= 9
    assert "ranking_fit_score" in fusion_status["validation_summary"]
    assert "freshness_coverage_rate" in fusion_status["validation_summary"]
    assert "response_lag_fit_rate" in fusion_status["validation_summary"]
    warning_codes = {item.get("code") for item in fusion_status["plausibility_warnings"]}
    has_low_coverage_period = any(float(row["available_group_ratio"]) < 0.5 for row in fusion_historical_totals)
    if has_low_coverage_period:
        assert "historical_low_group_coverage_summary" in warning_codes
    assert "historical_low_group_coverage" not in warning_codes
    if fusion_status["validation_summary"].get("event_stale_country_count", 0) > 0:
        assert "event_signal_stale" in warning_codes
    if fusion_status["validation_summary"].get("event_registry_no_credible_match_ratio", 0.0) > 0.0:
        assert "peak_no_credible_event_match" in warning_codes
    if fusion_status["validation_summary"].get("event_registry_multi_event_overlap_ratio", 0.0) > 0.0:
        assert "multi_event_overlap_review" in warning_codes
    if fusion_status["validation_summary"].get("event_coverage_sparse_country_count", 0) > 0:
        assert "event_coverage_sparse" in warning_codes

    validation_summary = _load_json(run_dir / "exports/fusion/validation_summary.json")[0]
    assert validation_summary["episode_count"] >= 12
    assert validation_summary["episodes_with_data"] >= 12
    assert validation_summary["peak_hit_rate"] >= 0.5
    assert "freshness_coverage_rate" in validation_summary
    assert "stale_burden_rate" in validation_summary
    assert "response_lag_fit_rate" in validation_summary
    assert "governance_instability_country_count" in validation_summary
    assert "governance_low_freshness_country_count" in validation_summary
    assert "event_registry_credible_match_ratio" in validation_summary
    assert "event_registry_no_credible_match_ratio" in validation_summary
    assert "event_registry_multi_event_overlap_ratio" in validation_summary
    assert "event_coverage_sparse_country_count" in validation_summary
    assert "peak_alignment_quality_score" in validation_summary
    assert "country_alignment_maturity_mean" in validation_summary
    assert "key_findings" in validation_summary

    validation_episode_rows = list(
        csv.DictReader((run_dir / "exports/fusion/validation_episode_review.csv").open(encoding="utf-8"))
    )
    assert validation_episode_rows
    assert all(row["country"] in set(EXPECTED_COUNTRIES) for row in validation_episode_rows)
    assert all(row["expected_total_reaction"] in {"low", "elevated", "high", "very_high"} for row in validation_episode_rows)
    validation_reference_rows = list(
        csv.DictReader((run_dir / "exports/fusion/validation_reference_episodes.csv").open(encoding="utf-8"))
    )
    assert validation_reference_rows
    assert any("governance" in (row.get("expected_groups", "")) for row in validation_reference_rows)
    assert all(row.get("episode_id") for row in validation_reference_rows)

    validation_diag_rows = list(
        csv.DictReader((run_dir / "exports/fusion/validation_layer_diagnostics.csv").open(encoding="utf-8"))
    )
    assert validation_diag_rows
    assert any(row["structural_outlier_flag"] == "True" for row in validation_diag_rows)
    assert any(row["event_stale_flag"] in {"True", "False"} for row in validation_diag_rows)
    assert all("governance_instability_flag" in row for row in validation_diag_rows)
    assert all("governance_low_freshness_flag" in row for row in validation_diag_rows)
    assert all("fresh_contribution_share" in row for row in validation_diag_rows)
    assert all("stale_contribution_share" in row for row in validation_diag_rows)
    assert all("dynamic_layer_readiness" in row for row in validation_diag_rows)

    validation_freshness_rows = list(
        csv.DictReader((run_dir / "exports/fusion/validation_freshness_groups.csv").open(encoding="utf-8"))
    )
    assert validation_freshness_rows
    assert any(row["freshness_class"] in {"fresh", "aging", "stale"} for row in validation_freshness_rows)
    assert all("last_fresh_observation_date" in row for row in validation_freshness_rows)

    validation_responsiveness_rows = list(
        csv.DictReader(
            (run_dir / "exports/fusion/validation_historical_responsiveness.csv").open(encoding="utf-8")
        )
    )
    assert validation_responsiveness_rows
    assert all(row["responsiveness_profile"] for row in validation_responsiveness_rows)
    assert all("mean_abs_delta" in row for row in validation_responsiveness_rows)

    validation_country_profiles = list(
        csv.DictReader((run_dir / "exports/fusion/validation_country_profiles.csv").open(encoding="utf-8"))
    )
    assert len(validation_country_profiles) == len(EXPECTED_COUNTRIES)
    assert all(row["country"] in set(EXPECTED_COUNTRIES) for row in validation_country_profiles)
    assert all("year_max_score" in row for row in validation_country_profiles)
    assert all("year_volatility_std" in row for row in validation_country_profiles)
    assert all("operational_freshness_status" in row for row in validation_country_profiles)

    validation_peak_phases = list(
        csv.DictReader((run_dir / "exports/fusion/validation_peak_phases.csv").open(encoding="utf-8"))
    )
    assert validation_peak_phases
    assert all(row["country"] in set(EXPECTED_COUNTRIES) for row in validation_peak_phases)
    assert all(row["peak_rank"] in {"1", "2", "3"} for row in validation_peak_phases)
    assert all("top_positive_group_1" in row for row in validation_peak_phases)

    validation_group_profiles = list(
        csv.DictReader((run_dir / "exports/fusion/validation_group_profiles.csv").open(encoding="utf-8"))
    )
    assert validation_group_profiles
    assert all(row["country"] in set(EXPECTED_COUNTRIES) for row in validation_group_profiles)
    assert all("mean_group_score" in row for row in validation_group_profiles)
    assert all("mean_contribution_share" in row for row in validation_group_profiles)

    validation_ranking_trajectory = list(
        csv.DictReader((run_dir / "exports/fusion/validation_ranking_trajectory.csv").open(encoding="utf-8"))
    )
    assert validation_ranking_trajectory
    assert all(row["country"] in set(EXPECTED_COUNTRIES) for row in validation_ranking_trajectory)
    assert all("period_label" in row for row in validation_ranking_trajectory)
    assert all("rank" in row for row in validation_ranking_trajectory)


def test_pipeline_writes_fully_documented_current_reference(tmp_path, monkeypatch):
    """
    Traceability:
    - PSyR-008
    - PSyR-010
    - PSwR-017
    - TV-PSyR-010-009
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)
    main()

    reference_info = _load_json(Path("outputs/reference/current_reference/reference_info.json"))
    assert reference_info["reference_schema_version"] == "v2"
    assert reference_info["run_metadata_complete"] is True
    assert reference_info["missing_run_metadata_keys"] == []
    assert reference_info["legacy_fallback_mode"] is False


def test_pipeline_emits_v41_freshness_and_responsiveness_artifacts(tmp_path, monkeypatch):
    """
    Traceability:
    - PSR-022
    - PSyR-032
    - PSyR-033
    - PSwR-085
    - PSwR-086
    - PSwR-089
    - PSwR-090
    - PM-046
    - PM-048
    - TV-PSwR-085-002
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)
    main()

    run_dir = Path("outputs/runs/current_run")
    freshness_csv = run_dir / "exports/fusion/validation_freshness_groups.csv"
    responsiveness_csv = run_dir / "exports/fusion/validation_historical_responsiveness.csv"
    summary_json = run_dir / "exports/fusion/validation_summary.json"
    handout_path = run_dir / "handout.md"

    assert freshness_csv.exists()
    assert responsiveness_csv.exists()
    assert summary_json.exists()
    assert handout_path.exists()

    summary = _load_json(summary_json)[0]
    assert "freshness_coverage_rate" in summary
    assert "stale_burden_rate" in summary
    assert "response_lag_fit_rate" in summary
    assert "historical_responsiveness_mean_abs_delta" in summary
    assert "operational_freshness_attention" in summary

    freshness_rows = list(csv.DictReader(freshness_csv.open(encoding="utf-8")))
    assert freshness_rows
    assert any(row["freshness_class"] in {"fresh", "aging", "stale"} for row in freshness_rows)

    responsiveness_rows = list(csv.DictReader(responsiveness_csv.open(encoding="utf-8")))
    assert responsiveness_rows
    assert any(row["responsiveness_profile"] for row in responsiveness_rows)

    handout = handout_path.read_text(encoding="utf-8")
    assert "## V4.2 Governance, Validation & Operational Freshness (zusaetzlich)" in handout
    assert "Governance-instability:" in handout
    assert "Freshness-Diagnose:" in handout


def test_pipeline_reference_comparison_uses_full_reference_metadata(tmp_path, monkeypatch):
    """
    Traceability:
    - PSyR-009
    - PSyR-010
    - PSwR-017
    - TV-PSyR-009-006
    - TV-PSyR-010-011
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)

    # Create and then refresh reference as new official baseline.
    main()
    monkeypatch.setenv("PROTO_FORCE_REFERENCE_REFRESH", "1")
    main()
    monkeypatch.delenv("PROTO_FORCE_REFERENCE_REFRESH", raising=False)

    # Next normal run must compare against the full reference metadata.
    main()

    payload = _load_json(Path("outputs/runs/current_run/reference_comparison.json"))
    assert payload["status"] == "ok"
    baseline = payload["baseline_run"]
    required_keys = {
        "run_timestamp",
        "countries",
        "short_days",
        "recent_days",
        "baseline_days",
        "query_version",
        "scoring_version",
        "bridge_file_version",
        "context_table_version",
        "proposed_run_status",
        "run_status",
        "run_status_overridden",
        "metadata_schema_version",
    }
    assert required_keys.issubset(set(baseline.keys()))
    assert baseline["metadata_schema_version"] == "v2"


def test_pipeline_supports_manual_run_status_override(tmp_path, monkeypatch):
    """
    Traceability:
    - PSwR-017
    - PSyR-008
    - ALG-008
    - TV-PSwR-017-003
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PROTO_RUN_STATUS_OVERRIDE", STATUS_LIMITED)
    Path("outputs").mkdir(exist_ok=True)
    main()

    run_dir = Path("outputs/runs/current_run")
    status = (run_dir / "run_status.txt").read_text(encoding="utf-8").strip()
    assert status == STATUS_LIMITED
    metadata = _load_json(run_dir / "run_metadata.json")
    assert metadata["run_status"] == STATUS_LIMITED
    assert metadata["run_status_overridden"] is True


def test_pipeline_change_case_updates_previous_and_reference_deltas_with_fixtures(tmp_path, monkeypatch):
    """
    Traceability:
    - PSyR-009
    - PSyR-010
    - PSyR-006
    - PSwR-017
    - PSwR-016
    - PSwR-018
    - TV-PSyR-009-003
    - TV-PSyR-009-005
    - TV-PSyR-010-004
    - TV-PSyR-006-002
    - TV-PSwR-016-002
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)

    # First run with baseline snapshot.
    main()
    baseline_iran_plot = Path(
        "outputs/runs/current_run/plots/snapshot/iran_tension_timeseries.png"
    ).read_bytes()

    # Second run with controlled changed snapshot (single Iran protest uplift).
    gdelt_path = Path("data/gdelt/gdelt_events.csv")
    rows = []
    with gdelt_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    changed = False
    for row in rows:
        if (
            row["country"] == "Iran"
            and row["category"] == "protest"
            and row["date"] == "2026-04-12"
        ):
            row["raw_value"] = str(round(float(row["raw_value"]) + 60.0, 1))
            changed = True
            break
    assert changed
    with gdelt_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    main()

    run_dir = Path("outputs/runs/current_run")
    run_comparison = _load_json(run_dir / "run_comparison.json")
    reference_comparison = _load_json(run_dir / "reference_comparison.json")

    assert run_comparison["status"] == "ok"
    assert reference_comparison["status"] == "ok"
    assert run_comparison["overview"]["zunehmend"] >= 1
    assert reference_comparison["overview"]["zunehmend"] >= 1

    iran_prev = next(
        item
        for item in run_comparison["comparisons"]
        if item["country"] == "Iran" and item["cluster"] == "tension"
    )
    iran_ref = next(
        item
        for item in reference_comparison["comparisons"]
        if item["country"] == "Iran" and item["cluster"] == "tension"
    )
    assert iran_prev["delta_absolute"] > 0.0
    assert iran_ref["delta_absolute"] > 0.0
    assert iran_prev["delta_relative_percent"] is not None and iran_prev["delta_relative_percent"] > 0.0
    assert iran_ref["delta_relative_percent"] is not None and iran_ref["delta_relative_percent"] > 0.0
    assert iran_prev["delta_direction"] == "zunehmend"
    assert iran_ref["delta_direction"] == "zunehmend"

    handout = (run_dir / "handout.md").read_text(encoding="utf-8")
    assert "## Vergleich zum letzten Run (gesamt)" in handout
    assert "Δ letzter Run: +" in handout
    assert "- Zunehmend: " in handout

    changed_iran_plot = (run_dir / "plots/snapshot/iran_tension_timeseries.png").read_bytes()
    assert baseline_iran_plot != changed_iran_plot


def test_pipeline_snapshot_matches_latest_historical_point(tmp_path, monkeypatch):
    """
    Traceability:
    - PSwR-022
    - PM-010
    - TV-PSwR-022-002
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)
    main()

    summary = _load_json(Path("outputs/runs/current_run/exports/snapshot/summary_export.json"))
    summary_by_key = {
        (row["country"], row["cluster"]): (
            float(row["cluster_score"]),
            row["snapshot_source_date"],
        )
        for row in summary
    }

    historical_by_key_and_date: dict[tuple[str, str, str], float] = {}
    with Path("outputs/runs/current_run/exports/historical/historical_timeseries.csv").open(
        encoding="utf-8"
    ) as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["score_name"] != "cluster_score":
                continue
            if row["rolling_value"] in {"", "None"}:
                continue
            key = (row["country"], row["cluster"], row["date"])
            historical_by_key_and_date[key] = float(row["rolling_value"])

    for (country, cluster), (summary_value, source_date) in summary_by_key.items():
        assert source_date is not None
        historical_key = (country, cluster, source_date)
        assert historical_key in historical_by_key_and_date
        assert round(summary_value, 4) == round(historical_by_key_and_date[historical_key], 4)


def test_pipeline_marks_historical_trend_for_limited_status(tmp_path, monkeypatch):
    """
    Traceability:
    - PSyR-017
    - PSwR-029
    - TV-PSyR-017-001
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PROTO_RUN_STATUS_OVERRIDE", STATUS_LIMITED)
    Path("outputs").mkdir(exist_ok=True)
    main()

    status_payload = _load_json(Path("outputs/runs/current_run/exports/historical/historical_status.json"))
    assert status_payload["historical_enabled"] is True
    assert status_payload["historical_limited_marker"] is True

    handout = Path("outputs/runs/current_run/handout.md").read_text(encoding="utf-8")
    assert "Historical Rolling Trend ist als eingeschraenkt brauchbar markiert" in handout


def test_pipeline_snapshot_marks_under_coverage_fallback_and_penalty(tmp_path, monkeypatch):
    """
    Traceability:
    - PSwR-022
    - PSwR-026
    - PSwR-033
    - PM-010
    - PM-012
    - OI-021
    - TV-PSwR-022-005
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)
    main()

    summary = _load_json(Path("outputs/runs/current_run/exports/snapshot/summary_export.json"))
    germany_tension = next(
        row for row in summary if row["country"] == "Germany" and row["cluster"] == "tension"
    )
    assert germany_tension["snapshot_source_mode"] in {
        "historical_valid_endpoint",
        "historical_latest_valid_before_run_date",
        "historical_numeric_fallback_below_min_valid_days",
    }
    if germany_tension["snapshot_source_mode"] == "historical_numeric_fallback_below_min_valid_days":
        assert germany_tension["snapshot_endpoint_is_valid"] is False
        assert germany_tension["snapshot_source_is_valid"] is False
        assert germany_tension["snapshot_source_valid_days"] < germany_tension["snapshot_source_min_valid_days"]
        assert germany_tension["snapshot_confidence_penalty_applied"] > 0.0
    elif germany_tension["snapshot_source_mode"] == "historical_latest_valid_before_run_date":
        assert germany_tension["snapshot_endpoint_is_valid"] is False
        assert germany_tension["snapshot_source_is_valid"] is True
        assert germany_tension["snapshot_confidence_penalty_applied"] == 0.0
    else:
        assert germany_tension["snapshot_endpoint_is_valid"] is True
        assert germany_tension["snapshot_confidence_penalty_applied"] == 0.0


def test_plot_default_sizes_match_readability_targets():
    """
    Traceability:
    - PSwR-016
    - PSwR-032
    - PSR-005
    - OI-024
    - TV-PSwR-032-002
    """
    assert SNAPSHOT_FIGSIZE == (11, 5.5)
    assert HISTORICAL_CLUSTER_FIGSIZE == (14, 7)
    assert HISTORICAL_SUBSCORE_FIGSIZE == (16, 8)
    assert FUSION_GROUP_FIGSIZE == (12, 6)
    assert FUSION_HISTORICAL_GROUP_FIGSIZE == (14, 7)
    assert FUSION_HISTORICAL_TOTAL_FIGSIZE == (14, 6)


def test_pipeline_can_emit_optional_compact_historical_daily_report(tmp_path, monkeypatch):
    """
    Traceability:
    - PSwR-031
    - PSyR-015
    - TV-PSwR-031-002
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    config_path = tmp_path / "config" / "default.yaml"
    config_text = config_path.read_text(encoding="utf-8").replace(
        "  compact_daily_report: false",
        "  compact_daily_report: true",
    )
    config_path.write_text(config_text, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)
    main()

    assert Path("outputs/runs/current_run/exports/historical/compact_daily_report.md").exists()


def test_pipeline_can_force_refresh_reference_run(tmp_path, monkeypatch):
    """
    Traceability:
    - PSyR-010
    - PSwR-017
    - ALG-008
    - TV-PSyR-010-007
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)

    main()
    monkeypatch.setenv("PROTO_FORCE_REFERENCE_REFRESH", "1")
    main()

    run_dir = Path("outputs/runs/current_run")
    reference_dir = Path("outputs/reference/current_reference")
    run_metadata = _load_json(run_dir / "run_metadata.json")
    reference_metadata = _load_json(reference_dir / "run_metadata.json")
    reference_info = _load_json(reference_dir / "reference_info.json")
    reference_comparison = _load_json(run_dir / "reference_comparison.json")

    assert reference_info["reference_action"] == "refreshed_forced"
    assert reference_metadata["run_timestamp"] == run_metadata["run_timestamp"]
    assert reference_comparison["status"] == "reference_refreshed_from_current_run"


def test_review_bundle_acceptance_snapshot_contains_validation_hints(tmp_path, monkeypatch):
    """
    Traceability:
    - PSyR-007
    - PSyR-031
    - PSwR-080
    - PSwR-081
    - PSwR-096
    - PSwR-104
    - PSyR-040
    - PSwR-112
    - PM-041
    - TV-PSwR-080-002
    - TV-PSwR-096-002
    - TV-PSwR-112-001
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)
    shutil.copytree(project_root / "docs", tmp_path / "docs")
    shutil.copy2(project_root / "AGENTS.md", tmp_path / "AGENTS.md")
    shutil.copy2(project_root / "IMPLEMENT.md", tmp_path / "IMPLEMENT.md")
    shutil.copy2(project_root / "README.md", tmp_path / "README.md")
    shutil.copy2(project_root / "pyproject.toml", tmp_path / "pyproject.toml")

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)
    main()

    bundle_zip = create_review_bundle(
        ReviewBundleConfig(
            project_root=tmp_path,
            output_dir=tmp_path / "review_bundles",
            include_reference=False,
            include_plots=False,
            run_pytest=False,
            run_pipeline=False,
            fail_on_missing_required_docs=True,
        )
    )
    bundle_dir = bundle_zip.with_suffix("")
    assert bundle_dir.exists()

    acceptance_snapshot = _load_json(bundle_dir / "review_meta/acceptance_snapshot.json")
    assert "validation_summary" in acceptance_snapshot
    assert "validation_episode_review_preview" in acceptance_snapshot
    assert "validation_layer_diagnostics" in acceptance_snapshot
    assert "validation_freshness_groups" in acceptance_snapshot
    assert "validation_historical_responsiveness" in acceptance_snapshot
    assert "validation_country_profiles" in acceptance_snapshot
    assert "validation_peak_phases" in acceptance_snapshot
    assert "validation_group_profiles" in acceptance_snapshot
    assert "validation_ranking_trajectory" in acceptance_snapshot
    assert "peak_attribution" in acceptance_snapshot
    assert "peak_event_support" in acceptance_snapshot
    assert "peak_event_matches" in acceptance_snapshot
    assert "event_registry" in acceptance_snapshot
    assert "event_coverage_summary" in acceptance_snapshot
    assert "country_event_alignment" in acceptance_snapshot
    assert "event_alignment_summary" in acceptance_snapshot
    assert "trajectory_profiles" in acceptance_snapshot
    assert "global_peak_synchronization" in acceptance_snapshot
    assert "event_marker_registry" in acceptance_snapshot
    assert acceptance_snapshot["validation_summary"]["episode_count"] >= 9
    assert acceptance_snapshot["validation_episode_review_preview"]
    assert acceptance_snapshot["validation_layer_diagnostics"]
    assert acceptance_snapshot["validation_freshness_groups"]
    assert acceptance_snapshot["validation_historical_responsiveness"]
    assert acceptance_snapshot["validation_country_profiles"]
    assert acceptance_snapshot["validation_peak_phases"]
    assert acceptance_snapshot["validation_group_profiles"]
    assert acceptance_snapshot["validation_ranking_trajectory"]
    assert acceptance_snapshot["peak_attribution"]
    assert acceptance_snapshot["peak_event_support"]
    assert acceptance_snapshot["peak_event_matches"]
    assert acceptance_snapshot["event_registry"]
    assert acceptance_snapshot["event_coverage_summary"]
    assert acceptance_snapshot["country_event_alignment"]
    assert acceptance_snapshot["trajectory_profiles"]
    assert acceptance_snapshot["global_peak_synchronization"]
    assert acceptance_snapshot["event_marker_registry"]

    acceptance_md = (bundle_dir / "review_meta/acceptance_snapshot.md").read_text(encoding="utf-8")
    assert "## Validation Summary" in acceptance_md
    assert "## Validation Episode Review Preview" in acceptance_md
    assert "## Validation Freshness Groups" in acceptance_md
    assert "## Validation Historical Responsiveness" in acceptance_md
    assert "## Validation Country Profiles" in acceptance_md
    assert "## Validation Peak Phases" in acceptance_md
    assert "## Validation Group Profiles" in acceptance_md
    assert "## Validation Ranking Trajectory" in acceptance_md
    assert "## Peak Attribution" in acceptance_md
    assert "## Peak Event Support" in acceptance_md
    assert "## Peak Event Matches" in acceptance_md
    assert "## Event Registry" in acceptance_md
    assert "## Event Coverage Summary" in acceptance_md
    assert "## Country Event Alignment" in acceptance_md
    assert "## Event Alignment Summary" in acceptance_md
    assert "## Event Alignment Review" in acceptance_md
    assert "## Trajectory Profiles" in acceptance_md
    assert "## Global Peak Synchronization" in acceptance_md
    assert "## Event Marker Registry" in acceptance_md


def test_pipeline_country_fusion_plot_links_are_consistent_when_files_exist(tmp_path, monkeypatch):
    """
    Traceability:
    - PSR-013
    - PSR-015
    - PSwR-051
    - PSwR-053
    - PSwR-111
    - PM-020
    - PM-023
    - TV-PSwR-053-002
    - TV-PSwR-111-001
    """
    project_root = Path(__file__).resolve().parents[1]
    _prepare_workspace(project_root, tmp_path)

    monkeypatch.chdir(tmp_path)
    Path("outputs").mkdir(exist_ok=True)
    main()

    run_dir = Path("outputs/runs/current_run")
    handout = (run_dir / "handout.md").read_text(encoding="utf-8")

    for country, label in [
        ("germany", "Germany"),
        ("israel", "Israel"),
        ("iran", "Iran"),
        ("ukraine", "Ukraine"),
        ("russia", "Russia"),
        ("japan", "Japan"),
        ("china", "China"),
        ("taiwan", "Taiwan"),
        ("poland", "Poland"),
        ("nigeria", "Nigeria"),
    ]:
        plot_path = f"plots/fusion/fusion_groups_{country}.png"
        v43_profile_plot_path = f"plots/fusion/v43_country_profile_{country}.png"
        v431_peak_plot_path = f"plots/fusion/v431_peak_attribution_{country}.png"
        v432_alignment_plot_path = f"plots/fusion/v432_event_alignment_{country}.png"
        assert (run_dir / plot_path).exists()
        assert (run_dir / v43_profile_plot_path).exists()
        assert (run_dir / v431_peak_plot_path).exists()
        assert (run_dir / v432_alignment_plot_path).exists()

        block = _country_block(handout, label)
        assert plot_path in block
        assert v43_profile_plot_path in block
        assert v431_peak_plot_path in block
        assert v432_alignment_plot_path in block

        section_heading = "### 6) V3.1 Fusion-Plots (Land)"
        assert section_heading in block
        section = block.split(section_heading, 1)[1]
        next_heading = section.find("\n### ")
        section_text = section if next_heading == -1 else section[:next_heading]
        assert "manual review required: keine Plotdateien gefunden." not in section_text
        assert "### 9) V4.3 Jahresprofil-Plot (Land)" in block
        assert "### 10) V4.3.1 Peak-Attributionsplot (Land)" in block
        assert "### 11) V4.3.2 Event-Alignment-Plot (Land)" in block
