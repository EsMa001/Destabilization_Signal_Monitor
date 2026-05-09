# Country Destabilization Prototype V1/V2.3 Baseline + V4.3.2 Event-Alignment Expansion

Greenfield prototype for identifying short-term destabilization signals in media and context data for Iran, Israel, and Germany.

## Purpose
The prototype identifies short-term anomalies in media and context data and makes possible indications of political or societal destabilization visible.

## Scope
- Countries: Iran, Israel, Germany (display alias: Deutschland)
- Sources: GDELT, UCDP, bridge file, context table
- Clusters:
  1. Socio-political tension
  2. Violent escalation (internal + external/warlike)
  3. Structural/systemic vulnerability

## Additional V3.1 MVP output (parallel, additive)
The existing cluster-based result space remains fully active.
A second additive V3.1 path now runs in parallel with:
- canonical observations
- source adapters for `FAO FFPI`, `FAO FPMA`, `UN Comtrade`
- layer/group scores (`market_food`, `structural` in MVP depth)
- fusion total score + separate fusion confidence

V3.1 artifacts:
- `outputs/runs/current_run/exports/fusion/observations.csv`
- `outputs/runs/current_run/exports/fusion/source_signals.csv`
- `outputs/runs/current_run/exports/fusion/group_scores.csv`
- `outputs/runs/current_run/exports/fusion/fusion_total_scores.json`
- `outputs/runs/current_run/exports/fusion/fusion_status.json`
- `outputs/runs/current_run/plots/fusion/*`

## Additional V3.2 output (parallel, additive)
V3.2 extends the fusion path with:
- source integrations: `GDACS` (`shock`), `UNHCR` (`displacement`), `narrative_input` (`narrative`)
- monthly historical fusion path (separate from cluster historical rolling trend)
- historical fusion exports + historical fusion plots + handout sections

V3.2 artifacts:
- `outputs/runs/current_run/exports/fusion/historical_source_signals.csv`
- `outputs/runs/current_run/exports/fusion/historical_group_scores.csv`
- `outputs/runs/current_run/exports/fusion/historical_total_scores.csv`
- `outputs/runs/current_run/plots/fusion/fusion_historical_groups_<country>.png`
- `outputs/runs/current_run/plots/fusion/fusion_historical_total_<country>.png`

## Additional V3.3 output (parallel, additive)
V3.3 operationalizes the previously open `event` group with a first real event source:
- source integration: `gdelt_event` (derived from GDELT event rows)
- transparent event periodization + normalization in canonical observations
- event is now active in snapshot and historical fusion (no longer default `not_available`)
- event-specific non-blocking plausibility warnings in `fusion_status.json`

## Additional V4.0 output (parallel, additive)
V4.0 hardens the existing V3.3 monitor with explicit validation and calibration artifacts:
- versioned reference episodes (`data/validation/reference_episodes.csv`)
- validation framework export (`validation_framework.json`)
- episode-level validation review (`validation_episode_review.csv`)
- country ranking plausibility (`validation_country_ranking.csv`)
- layer diagnostics (`validation_layer_diagnostics.csv`)
- aggregated validation summary (`validation_summary.json`)
- validation summary propagated into `fusion_status.json`, handout, and review bundle acceptance snapshot

## Additional V4.3.2 output (parallel, additive)
V4.3.2 hardens analyst-facing real-world alignment on top of V4.3.1:
- versioned analyst event registry fixture for the fixed 10-country space
- staged peak-event matching classes + match confidence
- event coverage and country alignment maturity diagnostics
- explicit event-alignment review artifact + per-country event-alignment plots
- acceptance snapshot / review bundle extended with V4.3.2 alignment artifacts

V4.3.2 artifacts:
- `outputs/runs/current_run/exports/fusion/event_registry.csv`
- `outputs/runs/current_run/exports/fusion/peak_event_matches.csv`
- `outputs/runs/current_run/exports/fusion/event_coverage_summary.csv`
- `outputs/runs/current_run/exports/fusion/country_event_alignment.csv`
- `outputs/runs/current_run/exports/fusion/event_alignment_summary.json`
- `outputs/runs/current_run/exports/fusion/event_alignment_review.md`
- `outputs/runs/current_run/plots/fusion/v432_event_alignment_<country>.png`

## Official standard run output (V2.3)
The standard run always produces two official result areas:
- `Current Snapshot`
- `Historical Rolling Trend`

Official artifact split:
- Snapshot exports: `outputs/runs/current_run/exports/snapshot/*`
- Historical exports: `outputs/runs/current_run/exports/historical/*`
- Snapshot plots: `outputs/runs/current_run/plots/snapshot/*`
- Historical cluster plots: `outputs/runs/current_run/plots/historical/clusters/*`
- Historical subscore plots: `outputs/runs/current_run/plots/historical/subscores/*`

Compatibility fallback artifacts are still written under `outputs/runs/current_run/exports/*` for V2.1 consumers.

Snapshot transparency artifacts (V2.2.1 rule set, still active in V2.3):
- `outputs/runs/current_run/exports/snapshot/snapshot_status.json`
- `outputs/runs/current_run/exports/snapshot/summary_export.json` contains explicit snapshot source fields per country/cluster.

Historical baseline-method markers (V2.2.1+, still active in V2.3):
- `outputs/runs/current_run/exports/historical/historical_status.json` includes `constant_clusters` and method notes for the current `vulnerability` baseline handling.

Historical validation-support artifacts (V2.3):
- `outputs/runs/current_run/exports/historical/review_candidates.csv`
- `outputs/runs/current_run/exports/historical/review_candidates.json`
- Handout section `Top historical review candidates`

Notes for review candidates:
- Candidate scope is cluster-based and transparent (`cluster_score`, primarily `tension` + `escalation`).
- Low-coverage numeric points are visible and explicitly marked; they are not treated as fully validated peaks.
- `vulnerability` is baseline-oriented in the current model and excluded from default event-style candidate ranking.

## Historical rolling defaults
`config/default.yaml` defines:
- `historical.horizon_days = 365`
- `historical.window_days = 7`
- `historical.min_valid_days = 5`
- `historical.aggregation = rolling_mean`
- `historical.compact_daily_report = false`

## V2.1 calibration and configuration
`config/default.yaml` contains calibrated and configurable scoring parameters:
- `scoring.stage.low_max = 30`
- `scoring.stage.elevated_max = 56`
- `scoring.stage.high_max = 80`
- `scoring.trend.delta_epsilon = 1.25`

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,api]"
python -m pytest
python -m proto.pipeline.run_proto
```

## Python environment and reproducibility
The backend/core repository currently assumes a Python environment with declared package dependencies installed from `pyproject.toml`.

Recommended backend/core setup:
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev,api]"
```

If `python -m venv .venv` fails because `ensurepip` is unavailable, install the OS package that provides venv support first (for example `python3.12-venv` / `python3.13-venv` on Debian/Ubuntu-derived systems).

What this installs:
- core runtime dependencies for config loading, plotting, and API schemas
- test dependencies for `pytest`
- API server dependency for `uvicorn`

Canonical backend/core commands:
```bash
python -m pytest
python -m proto.pipeline.run_proto
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Notes:
- `python -m pytest` is the canonical test entrypoint for the Python repository root.
- Frontend setup is separate and lives under `frontend/` with its own `package.json` / `package-lock.json`.
- If only backend/core work is needed, frontend Node dependencies do not need to be installed.

## Backend API MVP quick start
The project now includes a FastAPI backend layer under `api/` for frontend coupling.

Start API server:
```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Core MVP endpoints:
- `GET /api/v1/health`
- `GET /api/v1/info`
- `GET /api/v1/options/countries`
- `GET /api/v1/options/layers`
- `GET /api/v1/config/template`
- `POST /api/v1/runs`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}`
- `GET /api/v1/runs/{run_id}/status`
- `GET /api/v1/runs/{run_id}/summary`
- `GET /api/v1/runs/{run_id}/artifacts`
- `GET /api/v1/runs/{run_id}/bundle`

## Backend API MVP notes
- Run execution is asynchronous from HTTP perspective (`POST /runs` returns quickly, execution continues in background).
- MVP currently allows one active run at a time; concurrent run creation returns `409 run_execution_failed`.
- Completed runs are archived to `outputs/runs/api_archive/<run_id>` for stable per-run artifact access.
- The existing pipeline core still writes to `outputs/runs/current_run`; API archival is additive and does not duplicate domain logic.

Optional manual run-status override:
```bash
$env:PROTO_RUN_STATUS_OVERRIDE="erfolgreich"
python -m proto.pipeline.run_proto
```

Optional forced reference refresh (promote current successful run to `current_reference`):
```bash
$env:PROTO_FORCE_REFERENCE_REFRESH="1"
python -m proto.pipeline.run_proto
```

## Frontend test quick start
The separate web frontend lives in `frontend/`.

```bash
cd frontend
npm run typecheck
npm run lint
npm run test
npm run test:e2e:mock:smoke
npm run test:e2e:api:smoke
```

Full browser suites:
- `npm run test:e2e:mock`
- `npm run test:e2e:api`

## Development process
This repository is developed requirements-driven. Use:
- `AGENTS.md`
- `IMPLEMENT.md`
- `docs/requirements/*`
- `docs/method/*`
- `docs/traceability/TraceabilityMatrix.md`

## Output review note (2026-04-06, updated in V2.3)
The first factual review of the V2.2 historical outputs confirmed:
- structural dual output generation (`Current Snapshot` + `Historical Rolling Trend`)
- visible coverage/validity handling in historical exports
- dynamic behavior mainly in `tension` and `escalation`
- near-constant historical behavior of `vulnerability` in the current model

V2.2.1 closed the first follow-up items:
- explicit snapshot fallback provenance + additional confidence penalty for below-threshold numeric fallback points
- explicit method marking of `vulnerability` as current structural/baseline cluster
- documented `Germany / tension / protest_subscore` jump as data-/rule-driven (not implementation artifact)
- improved 365-day plot readability and UTF-8 handout/text encoding stability

V2.3 adds analyst-oriented historical validation support:
- explicit historical review-candidate export with validity/coverage/confidence context
- transparent candidate ranking (value/change/stage context, no black-box formula)
- compact handout shortlist with driver hints for fast external plausibility review
