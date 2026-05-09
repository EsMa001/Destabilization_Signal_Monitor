from __future__ import annotations

import csv
import json
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReviewBundleConfig:
    project_root: Path
    output_dir: Path
    bundle_name: str = "chatgpt_review_bundle"
    include_reference: bool = False
    include_plots: bool = True
    run_pytest: bool = True
    run_pipeline: bool = False
    fail_on_missing_required_docs: bool = True


# Zielname im Bundle -> mögliche Quellpfade relativ zum Projektroot
REQUIRED_DOC_CANDIDATES: dict[str, list[str]] = {
    "AGENTS.md": [
        "AGENTS.md",
    ],
    "Architecture.md": [
        "Architecture.md",
        "docs/Architecture.md",
        "docs/architecture/Architecture.md",
    ],
    "IMPLEMENT.md": [
        "IMPLEMENT.md",
        "docs/IMPLEMENT.md",
    ],
    "OpenIssues.md": [
        "OpenIssues.md",
        "docs/OpenIssues.md",
        "docs/requirements/OpenIssues.md",
    ],
    "ProtoMethod.md": [
        "ProtoMethod.md",
        "docs/ProtoMethod.md",
        "docs/method/ProtoMethod.md",
    ],
    "ProtoRunbook.md": [
        "ProtoRunbook.md",
        "docs/ProtoRunbook.md",
        "docs/method/ProtoRunbook.md",
    ],
    "ProtoScope.md": [
        "ProtoScope.md",
        "docs/ProtoScope.md",
        "docs/requirements/ProtoScope.md",
    ],
    "ProtoScoring.md": [
        "ProtoScoring.md",
        "docs/ProtoScoring.md",
        "docs/method/ProtoScoring.md",
    ],
    "ProtoSR.md": [
        "ProtoSR.md",
        "docs/ProtoSR.md",
        "docs/requirements/ProtoSR.md",
    ],
    "ProtoSyR.md": [
        "ProtoSyR.md",
        "docs/ProtoSyR.md",
        "docs/requirements/ProtoSyR.md",
    ],
    "ProtoSwR.md": [
        "ProtoSwR.md",
        "docs/ProtoSwR.md",
        "docs/requirements/ProtoSwR.md",
    ],
    "TraceabilityMatrix.md": [
        "TraceabilityMatrix.md",
        "docs/TraceabilityMatrix.md",
        "docs/traceability/TraceabilityMatrix.md",
    ],
    "README.md": [
        "README.md",
    ],
    "pyproject.toml": [
        "pyproject.toml",
    ],
    "default.yaml": [
        "config/default.yaml",
    ],
}


def _run_command(cmd: list[str], cwd: Path) -> dict[str, Any]:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        combined = stdout + ("\n" + stderr if stderr else "")
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "combined": combined.strip(),
            "cmd": cmd,
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "combined": str(exc),
            "cmd": cmd,
        }


def _copy_file(src: Path, dst: Path) -> None:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> bool:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    if not src.exists() or not src.is_dir():
        return False
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return True


def _list_files(root: Path) -> list[str]:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    if not root.exists():
        return []
    return sorted(
        str(p.relative_to(root)).replace("\\", "/")
        for p in root.rglob("*")
        if p.is_file()
    )


def _resolve_doc(project_root: Path, candidates: list[str]) -> Path | None:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    for rel in candidates:
        p = project_root / rel
        if p.exists() and p.is_file():
            return p
    return None


def _read_text_if_exists(path: Path) -> str | None:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    if not path.exists() or not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _read_json_if_exists(path: Path) -> Any | None:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    text = _read_text_if_exists(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _read_json_object_if_exists(path: Path) -> dict[str, Any] | None:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    payload = _read_json_if_exists(path)
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return payload[0]
    return None


def _read_csv_rows(path: Path, limit: int | None = None) -> list[dict[str, str]]:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    if not path.exists() or not path.is_file():
        return []
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            rows.append(dict(row))
            if limit is not None and i + 1 >= limit:
                break
    return rows


def _find_handout_sections(handout_text: str, headings: list[str]) -> dict[str, str]:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    lines = handout_text.splitlines()
    results: dict[str, str] = {}

    for heading in headings:
        start_idx = None
        for i, line in enumerate(lines):
            if heading in line:
                start_idx = i
                break

        if start_idx is None:
            results[heading] = ""
            continue

        end_idx = len(lines)
        for j in range(start_idx + 1, len(lines)):
            if lines[j].startswith("## ") and j > start_idx:
                end_idx = j
                break

        results[heading] = "\n".join(lines[start_idx:end_idx]).strip()

    return results


def _summarize_group_scores(group_rows: list[dict[str, str]]) -> dict[str, Any]:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    by_country: dict[str, list[dict[str, str]]] = {}
    for row in group_rows:
        by_country.setdefault(row.get("country", "UNKNOWN"), []).append(row)

    summary: dict[str, Any] = {"countries": {}}

    for country, rows in by_country.items():
        available = [r for r in rows if r.get("status") == "ok" and r.get("group_score") not in ("", None)]

        unavailable = []
        for r in rows:
            if r.get("status") != "ok":
                unavailable.append(
                    {
                        "group": r.get("group"),
                        "status": r.get("status"),
                    }
                )

        def parse_score(r: dict[str, str]) -> float:
            # Traceability:
            # - SUP-001
            # - PSyR-031
            # - PSwR-080
            # - PSwR-096
            try:
                return float(r.get("group_score", "nan"))
            except Exception:
                return float("-inf")

        available_sorted = sorted(available, key=parse_score, reverse=True)

        summary["countries"][country] = {
            "available_group_count": len(available),
            "unavailable_groups": unavailable,
            "top_group": available_sorted[0] if available_sorted else None,
            "bottom_group": available_sorted[-1] if available_sorted else None,
            "groups": rows,
        }

    return summary


def _summarize_fusion_totals(total_scores: list[dict[str, Any]]) -> dict[str, Any]:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    def parse_score(item: dict[str, Any]) -> float:
        # Traceability:
        # - SUP-001
        # - PSyR-031
        # - PSwR-080
        # - PSwR-096
        try:
            return float(item.get("fusion_score", "nan"))
        except Exception:
            return float("-inf")

    ranking = sorted(total_scores, key=parse_score, reverse=True)
    return {
        "country_ranking_by_fusion_score": ranking,
        "top_country": ranking[0] if ranking else None,
        "bottom_country": ranking[-1] if ranking else None,
    }


def _write_json(path: Path, data: dict | list) -> None:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def create_acceptance_snapshot(bundle_dir: Path) -> None:
    """
    Erzeugt review_meta/acceptance_snapshot.json und acceptance_snapshot.md
    auf Basis der bereits kopierten Bundle-Inhalte.
    """
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    review_meta = bundle_dir / "review_meta"
    review_meta.mkdir(parents=True, exist_ok=True)

    current_run = bundle_dir / "outputs" / "runs" / "current_run"
    exports_fusion = current_run / "exports" / "fusion"
    exports_snapshot = current_run / "exports" / "snapshot"
    exports_historical = current_run / "exports" / "historical"
    handout_path = current_run / "handout.md"

    fusion_status = _read_json_if_exists(exports_fusion / "fusion_status.json")
    fusion_totals = _read_json_if_exists(exports_fusion / "fusion_total_scores.json") or []
    validation_summary = _read_json_object_if_exists(exports_fusion / "validation_summary.json")
    validation_framework = _read_json_object_if_exists(exports_fusion / "validation_framework.json")
    validation_episode_review_preview = _read_csv_rows(
        exports_fusion / "validation_episode_review.csv",
        limit=30,
    )
    validation_country_ranking = _read_csv_rows(
        exports_fusion / "validation_country_ranking.csv",
        limit=20,
    )
    validation_layer_diagnostics = _read_csv_rows(
        exports_fusion / "validation_layer_diagnostics.csv",
        limit=20,
    )
    validation_freshness_groups = _read_csv_rows(
        exports_fusion / "validation_freshness_groups.csv",
        limit=30,
    )
    validation_historical_responsiveness = _read_csv_rows(
        exports_fusion / "validation_historical_responsiveness.csv",
        limit=20,
    )
    validation_country_profiles = _read_csv_rows(
        exports_fusion / "validation_country_profiles.csv",
        limit=20,
    )
    validation_peak_phases = _read_csv_rows(
        exports_fusion / "validation_peak_phases.csv",
        limit=30,
    )
    validation_group_profiles = _read_csv_rows(
        exports_fusion / "validation_group_profiles.csv",
        limit=40,
    )
    validation_ranking_trajectory = _read_csv_rows(
        exports_fusion / "validation_ranking_trajectory.csv",
        limit=40,
    )
    peak_attribution = _read_csv_rows(
        exports_fusion / "peak_attribution.csv",
        limit=40,
    )
    peak_event_support = _read_csv_rows(
        exports_fusion / "peak_event_support.csv",
        limit=40,
    )
    trajectory_profiles = _read_csv_rows(
        exports_fusion / "trajectory_profiles.csv",
        limit=20,
    )
    global_peak_synchronization = _read_csv_rows(
        exports_fusion / "global_peak_synchronization.csv",
        limit=30,
    )
    event_marker_registry = _read_csv_rows(
        exports_fusion / "event_marker_registry.csv",
        limit=40,
    )
    event_registry = _read_csv_rows(
        exports_fusion / "event_registry.csv",
        limit=60,
    )
    peak_event_matches = _read_csv_rows(
        exports_fusion / "peak_event_matches.csv",
        limit=60,
    )
    event_coverage_summary = _read_csv_rows(
        exports_fusion / "event_coverage_summary.csv",
        limit=40,
    )
    country_event_alignment = _read_csv_rows(
        exports_fusion / "country_event_alignment.csv",
        limit=40,
    )
    event_alignment_summary = _read_json_object_if_exists(
        exports_fusion / "event_alignment_summary.json"
    )
    event_alignment_review_text = _read_text_if_exists(
        exports_fusion / "event_alignment_review.md"
    )
    group_scores = _read_csv_rows(exports_fusion / "group_scores.csv")
    observations_preview = _read_csv_rows(exports_fusion / "observations.csv", limit=20)
    source_signals_preview = _read_csv_rows(exports_fusion / "source_signals.csv", limit=20)
    hist_group_preview = _read_csv_rows(exports_fusion / "historical_group_scores.csv", limit=30)
    hist_total_preview = _read_csv_rows(exports_fusion / "historical_total_scores.csv", limit=30)
    snapshot_status = _read_json_if_exists(exports_snapshot / "snapshot_status.json")
    historical_status = _read_json_if_exists(exports_historical / "historical_status.json")
    handout_text = _read_text_if_exists(handout_path) or ""

    handout_sections = _find_handout_sections(
        handout_text,
        headings=[
            "## V4.3 Comparative Expansion: 10 Countries, Full 356-Day Profiles",
            "## V4.3 Vertiefende Diagnostik",
            "## V4.3.1 Peak Attribution & Event Alignment Hardening",
            "## V4.3.2 Analyst Event Registry & Real-World Alignment",
            "## V3.1 Layer/Fusion Snapshot",
            "## V3.2 Historical Fusion",
            "## Top historical review candidates",
            "## V4.2 Governance, Validation & Operational Freshness",
            "## V4.1 Operational Freshness & Responsiveness",
            "## V4.0 Validation & Calibration",
        ],
    )

    payload = {
        "fusion_status": fusion_status,
        "validation_summary": validation_summary,
        "validation_framework": validation_framework,
        "validation_episode_review_preview": validation_episode_review_preview,
        "validation_country_ranking": validation_country_ranking,
        "validation_layer_diagnostics": validation_layer_diagnostics,
        "validation_freshness_groups": validation_freshness_groups,
        "validation_historical_responsiveness": validation_historical_responsiveness,
        "validation_country_profiles": validation_country_profiles,
        "validation_peak_phases": validation_peak_phases,
        "validation_group_profiles": validation_group_profiles,
        "validation_ranking_trajectory": validation_ranking_trajectory,
        "peak_attribution": peak_attribution,
        "peak_event_support": peak_event_support,
        "trajectory_profiles": trajectory_profiles,
        "global_peak_synchronization": global_peak_synchronization,
        "event_marker_registry": event_marker_registry,
        "event_registry": event_registry,
        "peak_event_matches": peak_event_matches,
        "event_coverage_summary": event_coverage_summary,
        "country_event_alignment": country_event_alignment,
        "event_alignment_summary": event_alignment_summary,
        "event_alignment_review": event_alignment_review_text,
        "fusion_total_scores": fusion_totals,
        "group_scores_summary": _summarize_group_scores(group_scores),
        "fusion_total_summary": _summarize_fusion_totals(fusion_totals),
        "observations_preview": observations_preview,
        "source_signals_preview": source_signals_preview,
        "historical_group_scores_preview": hist_group_preview,
        "historical_total_scores_preview": hist_total_preview,
        "snapshot_status": snapshot_status,
        "historical_status": historical_status,
        "handout_sections": handout_sections,
    }

    _write_json(review_meta / "acceptance_snapshot.json", payload)

    md_lines: list[str] = []
    md_lines.append("# Acceptance Snapshot")
    md_lines.append("")

    if validation_summary:
        md_lines.append("## Validation Summary")
        md_lines.append("```json")
        md_lines.append(json.dumps(validation_summary, indent=2, ensure_ascii=False))
        md_lines.append("```")
        md_lines.append("")

    if validation_framework:
        md_lines.append("## Validation Framework")
        md_lines.append("```json")
        md_lines.append(json.dumps(validation_framework, indent=2, ensure_ascii=False))
        md_lines.append("```")
        md_lines.append("")

    if fusion_status:
        md_lines.append("## Fusion Status")
        md_lines.append("```json")
        md_lines.append(json.dumps(fusion_status, indent=2, ensure_ascii=False))
        md_lines.append("```")
        md_lines.append("")

    if fusion_totals:
        md_lines.append("## Fusion Total Scores")
        md_lines.append("```json")
        md_lines.append(json.dumps(fusion_totals, indent=2, ensure_ascii=False))
        md_lines.append("```")
        md_lines.append("")

    group_summary = payload["group_scores_summary"]["countries"]
    md_lines.append("## Group Score Summary by Country")
    for country, info in group_summary.items():
        md_lines.append(f"### {country}")
        md_lines.append(f"- available_group_count: {info['available_group_count']}")
        if info["unavailable_groups"]:
            unavailable_str = ", ".join(
                f"{x['group']}({x['status']})" for x in info["unavailable_groups"]
            )
        else:
            unavailable_str = "-"
        md_lines.append(f"- unavailable_groups: {unavailable_str}")
        if info["top_group"]:
            md_lines.append(
                f"- top_group: {info['top_group'].get('group')} = {info['top_group'].get('group_score')}"
            )
        if info["bottom_group"]:
            md_lines.append(
                f"- bottom_group: {info['bottom_group'].get('group')} = {info['bottom_group'].get('group_score')}"
            )
        md_lines.append("")

    for title, content in handout_sections.items():
        md_lines.append(f"## Extract: {title}")
        if content:
            md_lines.append("```md")
            md_lines.append(content)
            md_lines.append("```")
        else:
            md_lines.append("_not found_")
        md_lines.append("")

    md_lines.append("## Observations Preview")
    md_lines.append("```json")
    md_lines.append(json.dumps(observations_preview, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Source Signals Preview")
    md_lines.append("```json")
    md_lines.append(json.dumps(source_signals_preview, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Historical Group Scores Preview")
    md_lines.append("```json")
    md_lines.append(json.dumps(hist_group_preview, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Historical Total Scores Preview")
    md_lines.append("```json")
    md_lines.append(json.dumps(hist_total_preview, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Episode Review Preview")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_episode_review_preview, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Country Ranking")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_country_ranking, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Layer Diagnostics")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_layer_diagnostics, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Freshness Groups")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_freshness_groups, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Historical Responsiveness")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_historical_responsiveness, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Country Profiles")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_country_profiles, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Peak Phases")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_peak_phases, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Group Profiles")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_group_profiles, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Validation Ranking Trajectory")
    md_lines.append("```json")
    md_lines.append(json.dumps(validation_ranking_trajectory, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Peak Attribution")
    md_lines.append("```json")
    md_lines.append(json.dumps(peak_attribution, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Peak Event Support")
    md_lines.append("```json")
    md_lines.append(json.dumps(peak_event_support, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Trajectory Profiles")
    md_lines.append("```json")
    md_lines.append(json.dumps(trajectory_profiles, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Global Peak Synchronization")
    md_lines.append("```json")
    md_lines.append(json.dumps(global_peak_synchronization, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Event Marker Registry")
    md_lines.append("```json")
    md_lines.append(json.dumps(event_marker_registry, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Event Registry")
    md_lines.append("```json")
    md_lines.append(json.dumps(event_registry, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Peak Event Matches")
    md_lines.append("```json")
    md_lines.append(json.dumps(peak_event_matches, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Event Coverage Summary")
    md_lines.append("```json")
    md_lines.append(json.dumps(event_coverage_summary, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Country Event Alignment")
    md_lines.append("```json")
    md_lines.append(json.dumps(country_event_alignment, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Event Alignment Summary")
    md_lines.append("```json")
    md_lines.append(json.dumps(event_alignment_summary or {}, indent=2, ensure_ascii=False))
    md_lines.append("```")
    md_lines.append("")

    md_lines.append("## Event Alignment Review")
    if event_alignment_review_text:
        md_lines.append("```md")
        md_lines.append(event_alignment_review_text)
        md_lines.append("```")
    else:
        md_lines.append("_not found_")
    md_lines.append("")

    (review_meta / "acceptance_snapshot.md").write_text(
        "\n".join(md_lines),
        encoding="utf-8",
    )


def create_review_bundle(config: ReviewBundleConfig) -> Path:
    # Traceability:
    # - SUP-001
    # - PSyR-031
    # - PSwR-080
    # - PSwR-096
    project_root = config.project_root.resolve()
    output_dir = config.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_dir = output_dir / f"{config.bundle_name}_{timestamp}"
    bundle_zip = output_dir / f"{config.bundle_name}_{timestamp}.zip"

    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    review_meta = bundle_dir / "review_meta"
    review_meta.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "created_at_utc": timestamp,
        "project_root": str(project_root),
        "bundle_name": config.bundle_name,
        "sections": {},
        "missing_required_docs": [],
    }

    # 0) optional pipeline run
    if config.run_pipeline:
        pipeline_result = _run_command(["python", "-m", "proto.pipeline.run_proto"], cwd=project_root)
        (review_meta / "pipeline_run.txt").write_text(
            pipeline_result["combined"] or "",
            encoding="utf-8",
        )
        manifest["sections"]["pipeline_run"] = {
            "ok": pipeline_result["ok"],
            "returncode": pipeline_result["returncode"],
            "file": "review_meta/pipeline_run.txt",
        }

    # 1) Pflichtdokumente auflösen und kopieren
    docs_dst = bundle_dir / "docs_snapshot"
    docs_dst.mkdir(parents=True, exist_ok=True)

    resolved_docs: dict[str, str] = {}
    missing_docs: dict[str, list[str]] = {}

    for target_name, candidates in REQUIRED_DOC_CANDIDATES.items():
        resolved = _resolve_doc(project_root, candidates)
        if resolved is None:
            missing_docs[target_name] = candidates
            continue
        _copy_file(resolved, docs_dst / target_name)
        resolved_docs[target_name] = str(resolved.relative_to(project_root)).replace("\\", "/")

    manifest["sections"]["docs_snapshot"] = {
        "resolved": resolved_docs,
        "missing": missing_docs,
    }
    manifest["missing_required_docs"] = sorted(missing_docs.keys())

    (review_meta / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if missing_docs and config.fail_on_missing_required_docs:
        raise FileNotFoundError(
            "Missing required bundle docs: "
            + ", ".join(sorted(missing_docs.keys()))
            + ". See review_meta/manifest.json for searched candidate paths."
        )

    # 2) current_run kopieren
    current_run_src = project_root / "outputs" / "runs" / "current_run"
    current_run_dst = bundle_dir / "outputs" / "runs" / "current_run"
    current_run_copied = _copy_tree(current_run_src, current_run_dst)

    manifest["sections"]["current_run"] = {
        "copied": current_run_copied,
        "source": str(current_run_src),
    }

    # 3) optional reference
    if config.include_reference:
        ref_src = project_root / "outputs" / "reference" / "current_reference"
        ref_dst = bundle_dir / "outputs" / "reference" / "current_reference"
        ref_copied = _copy_tree(ref_src, ref_dst)
        manifest["sections"]["reference_run"] = {
            "copied": ref_copied,
            "source": str(ref_src),
        }

    # 4) optional plots entfernen
    if not config.include_plots:
        plots_dir = current_run_dst / "plots"
        if plots_dir.exists():
            shutil.rmtree(plots_dir)
        manifest["sections"]["plots_removed"] = True
    else:
        manifest["sections"]["plots_removed"] = False

    # 5) pytest summary
    if config.run_pytest:
        pytest_result = _run_command(["python", "-m", "pytest", "-q"], cwd=project_root)
        (review_meta / "pytest_summary.txt").write_text(
            pytest_result["combined"] or "",
            encoding="utf-8",
        )
        manifest["sections"]["pytest_summary"] = {
            "ok": pytest_result["ok"],
            "returncode": pytest_result["returncode"],
            "file": "review_meta/pytest_summary.txt",
        }

    # 6) git info
    git_info = {
        "branch": _run_command(["git", "branch", "--show-current"], cwd=project_root)["combined"],
        "commit": _run_command(["git", "rev-parse", "HEAD"], cwd=project_root)["combined"],
        "status_short": _run_command(["git", "status", "--short"], cwd=project_root)["combined"],
    }
    _write_json(review_meta / "git_info.json", git_info)
    manifest["sections"]["git_info"] = "review_meta/git_info.json"

    # 7) bundle summary
    exports_root = current_run_dst / "exports"
    plots_root = current_run_dst / "plots"

    bundle_summary = {
        "handout_present": (current_run_dst / "handout.md").exists(),
        "docs_snapshot_files": _list_files(docs_dst),
        "export_dirs": sorted([p.name for p in exports_root.iterdir() if p.is_dir()]) if exports_root.exists() else [],
        "plot_dirs": sorted([p.name for p in plots_root.iterdir() if p.is_dir()]) if plots_root.exists() else [],
        "fusion_export_files": _list_files(exports_root / "fusion"),
        "historical_export_files": _list_files(exports_root / "historical"),
        "snapshot_export_files": _list_files(exports_root / "snapshot"),
        "fusion_plot_files": _list_files(plots_root / "fusion"),
        "historical_plot_files": _list_files(plots_root / "historical"),
        "snapshot_plot_files": _list_files(plots_root / "snapshot"),
    }
    _write_json(review_meta / "bundle_summary.json", bundle_summary)
    manifest["sections"]["bundle_summary"] = "review_meta/bundle_summary.json"

    # 8) acceptance snapshot
    create_acceptance_snapshot(bundle_dir)
    manifest["sections"]["acceptance_snapshot_json"] = "review_meta/acceptance_snapshot.json"
    manifest["sections"]["acceptance_snapshot_md"] = "review_meta/acceptance_snapshot.md"

    # 9) manifest neu schreiben
    _write_json(review_meta / "manifest.json", manifest)

    # 10) ZIP erzeugen
    if bundle_zip.exists():
        bundle_zip.unlink()

    with zipfile.ZipFile(bundle_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in bundle_dir.rglob("*"):
            zf.write(path, arcname=path.relative_to(bundle_dir))

    return bundle_zip


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    zip_path = create_review_bundle(
        ReviewBundleConfig(
            project_root=project_root,
            output_dir=project_root / "review_bundles",
            bundle_name="chatgpt_review_bundle",
            include_reference=False,
            include_plots=True,
            run_pytest=True,
            run_pipeline=False,  # bei Bedarf auf True setzen
            fail_on_missing_required_docs=True,
        )
    )
    print(f"Review bundle created: {zip_path}")
