# IMPLEMENT.md

## Objective
Build and harden the Country Destabilization Prototype into a stable, traceable, and presentable V1/V2 baseline and evolve it toward a structured V3 multi-source fusion architecture.

## Active Iteration Status (2026-04-17)

### F1-05 Frontend Test Automation MVP (Vitest/RTL + Playwright + Mock/API Mode Separation)
- Status: completed_mvp_scope
- Ziel: etablieren einer reproduzierbaren, zweistufigen Frontend-Testbasis mit klarer Trennung von schnellen Komponententests und echten Browser-Flows, inklusive expliziter Mock-vs-API-Moduspruefung.
- Betroffene Requirement-IDs: test-automation AP-01 bis AP-12 (current block), `PSwR-001` separation principle (frontend bleibt praesentation/API-only), `PSwR-018` required test-level expectation (unit/integration/e2e).
- Betroffene Open-Issues: keine neuen fachlichen Open-Issues; bisherige API-Gaps (`OI-042`, `OI-043`) bleiben als fachliche Randbedingungen bestehen.
- Betroffene Codebereiche:
  - `frontend/package.json`
  - `frontend/vitest.config.ts`
  - `frontend/playwright.mock.config.ts` (neu)
  - `frontend/playwright.api.config.ts` (neu)
  - `frontend/.gitignore`
  - `frontend/tests/setup.ts`
  - `frontend/src/components/ui/Panel.tsx`
  - `frontend/src/components/ui/StateCard.tsx`
  - `frontend/src/components/layout/TopBar.tsx`
  - `frontend/src/components/layout/SidebarNav.tsx`
  - `frontend/src/components/map/InteractiveWorldMap.tsx`
  - `frontend/src/components/coverage/CoverageTable.tsx`
  - `frontend/src/components/artifacts/ArtifactList.tsx`
  - `frontend/src/features/overview/OverviewPage.tsx`
  - `frontend/src/features/runs/RunBuilderForm.tsx`
  - `frontend/src/features/runs/RunMonitorTable.tsx`
  - `frontend/src/features/countries/CountryDetailView.tsx`
  - `frontend/src/features/compare/CompareView.tsx`
  - `frontend/src/features/coverage/CoverageView.tsx`
  - `frontend/src/features/artifacts/ArtifactsView.tsx`
  - `frontend/tests/unit/*` (strukturierte Unit-Tests)
  - `frontend/tests/integration/*` (strukturierte Integration-Tests)
  - `frontend/tests/e2e/mock/*` (neu)
  - `frontend/tests/e2e/api/*` (neu)
  - `frontend/README.md`
  - `frontend/design/frontend_design_handoff.md`
- Tests:
  - Unit: 8 Dateien / 14 Tests (`tests/unit/*`)
  - Integration: 11 Dateien / 21 Tests (`tests/integration/*`)
  - E2E Mock: 12 Tests (`tests/e2e/mock/*`)
  - E2E API: 3 Tests (`tests/e2e/api/*`)
- Ergebnisstand:
  - Frontend-Teststack ist konsolidiert und klar getrennt (`unit`, `integration`, `e2e`).
  - Playwright ist mit lokalem `webServer`, `baseURL`, Reporter und getrennten Mock/API-Konfigurationen produktiv nutzbar.
  - Mock-Fallback-Verhalten ist testseitig explizit pruefbar, inklusive sichtbarer UI-Kennzeichnung.
  - API-Modus ohne Mock-Fallback prueft, dass keine stillen Fake-Run-Erfolge auftreten.
  - Kritische UI-Punkte haben stabile, sparsame `data-testid`-Anker fuer robuste Automatisierung.
  - API-Client-Regressionsschutz deckt `createRun`-Trennung explizit ab (`mock on` vs `mock off`).
  - Loading-/Empty-/Error-Zustaende zentraler Workspaces sind als eigene Integrationstests abgesichert.

### F1-04 Frontend Stabilization & Error Hardening (Hydration, Routing, Backend/Fallback Separation, Map MVP)
- Status: completed_with_stabilization_scope
- Ziel: remove concrete runtime/integration failures and enforce honest backend-vs-mock behavior without moving domain logic into frontend.
- Betroffene Requirement-IDs: stabilization AP-01 bis AP-10 (current block), `PSwR-001` separation principle (boundary respected), `PSwR-018` frontend test-level expectation mirrored.
- Betroffene Open-Issues: `OI-043` remains open (specialized API endpoint coverage), compare-view test harness marked unstable and skipped pending hardening.
- Betroffene Codebereiche:
  - `frontend/src/components/layout/TopBar.tsx`
  - `frontend/src/app/runs/[runId]/page.tsx`
  - `frontend/src/app/countries/[countryCode]/page.tsx`
  - `frontend/src/lib/api/client.ts`
  - `frontend/src/lib/api/fallback.ts`
  - `frontend/src/features/runs/RunBuilderForm.tsx`
  - `frontend/src/features/overview/OverviewPage.tsx`
  - `frontend/src/features/runs/RunMonitorTable.tsx`
  - `frontend/src/features/runs/RunDetailView.tsx`
  - `frontend/src/features/countries/CountryDetailView.tsx`
  - `frontend/src/components/map/InteractiveWorldMap.tsx`
  - `frontend/src/styles/globals.css`
  - `frontend/src/types/api.ts`
  - `frontend/src/app/compare/page.tsx`
  - `frontend/tests/*` (erweitert/angepasst)
  - `frontend/.env.example`
  - `frontend/README.md`
  - `frontend/design/frontend_design_handoff.md`
- Tests:
  - neu: `frontend/tests/topbar-hydration.test.tsx`
  - neu: `frontend/tests/dynamic-route-params.test.tsx`
  - erweitert: `frontend/tests/run-builder-submit.test.tsx`
  - erweitert: `frontend/tests/interactive-world-map.test.tsx`
  - erweitert: `frontend/tests/page-header.test.tsx`
  - erweitert: `frontend/tests/country-detail-toggle.test.tsx`
  - Hinweis: `frontend/tests/compare-view.test.tsx` aktuell `skip` wegen instabilem Hanging-Harness
- Ergebnisstand:
  - Hydration mismatch in TopBar beseitigt (stabiler Initialwert + clientseitiger Tick).
  - Dynamische App-Router-Params in Run/Country Detail auf Promise-`params` gehaertet.
  - API/Fallback-Verhalten explizit env-gesteuert; kein stiller Fake-Run im Normalbetrieb.
  - Backend-Konnektivitaet sichtbar (TopBar + Run Builder) mit klaren Zustandslabels.
  - Run Builder blockiert irrefuehrende Erfolgsfaelle bei Backend-Ausfall (wenn Mock aus).
  - Weltkarten-MVP auf reduzierte, glaubwuerdigere Laenderumrisse fuer relevante Laender umgestellt.
  - Build/Typecheck/Lint/Test in dieser Umgebung ausfuehrbar; Vergleichstest derzeit bewusst ausgesetzt.

### F1-01 Frontend MVP Phase 1 (App Shell + Core Pages + API Client)
- Status: implemented_with_mvp_fallback_scope
- Ziel: establish a separate web frontend baseline that is stitch-aligned, API-only coupled, and ready for iterative expansion without moving domain logic out of the Python core.
- Betroffene Requirement-IDs: frontend handoff AP-01 bis AP-11 (work-package scope), `PSwR-001` separation principle (boundary respected), `PSwR-018` test-level expectation mirrored for frontend checks.
- Betroffene Open-Issues: none newly opened in this block; fallback constraints documented in `frontend/README.md`.
- Betroffene Codebereiche:
  - `frontend/src/app/*`
  - `frontend/src/components/layout/*`
  - `frontend/src/components/ui/*`
  - `frontend/src/features/overview/*`
  - `frontend/src/features/runs/*`
  - `frontend/src/features/countries/*`
  - `frontend/src/lib/api/*`
  - `frontend/src/hooks/usePolling.ts`
  - `frontend/src/styles/globals.css`
  - `frontend/tests/*`
  - `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vitest.config.ts`, `frontend/eslint.config.mjs`
- Ergebnisstand:
  - App shell with sidebar + topbar + workspace is implemented and reused across pages.
  - Core pages implemented for Overview, Run Builder, Run Monitor, Run Detail, and Country Detail.
  - API client layer is centralized and typed (`health`, `runs`, `options`, `artifacts`) with controlled fallback adapter.
  - Loading/empty/error states are implemented on core screens.
  - Frontend tests added for app shell, run builder submit, run monitor rendering, and country detail mode toggle.
  - Environment note: frontend toolchain checks (`build`, `lint`, `typecheck`, `tests`) are prepared in scripts but could not be executed in this environment because Node/npm is not available.

### F1-02 Frontend MVP Phase 2 (Real Data Binding + Map + Country Hardening + Compare/Coverage/Artifacts Expansion)
- Status: implemented_with_api_gap_constraints
- Ziel: evolve the frontend from structural MVP pages to usable analyst workspaces with stronger API binding, interactive map usage, and robust handling of partial/unavailable backend contracts.
- Betroffene Requirement-IDs: frontend handoff AP-01 bis AP-12 (phase-2 scope), `PSwR-001` separation principle (boundary respected), `PSwR-018` frontend test-level expectation mirrored.
- Betroffene Open-Issues: `OI-042` (weiter offen), `OI-043` (neu, API-coverage gap for specialized frontend endpoints).
- Betroffene Codebereiche:
  - `frontend/src/lib/api/client.ts`
  - `frontend/src/lib/api/fallback.ts`
  - `frontend/src/types/api.ts`
  - `frontend/src/features/overview/OverviewPage.tsx`
  - `frontend/src/features/countries/CountryDetailView.tsx`
  - `frontend/src/features/compare/CompareView.tsx` (neu)
  - `frontend/src/features/coverage/CoverageView.tsx` (neu)
  - `frontend/src/features/artifacts/ArtifactsView.tsx` (neu)
  - `frontend/src/components/map/InteractiveWorldMap.tsx` (neu)
  - `frontend/src/components/charts/TrendLineChart.tsx` (neu)
  - `frontend/src/components/ui/KpiCard.tsx` (neu)
  - `frontend/src/components/ui/SectionHeader.tsx` (neu)
  - `frontend/src/components/coverage/CoverageTable.tsx` (neu)
  - `frontend/src/components/artifacts/ArtifactList.tsx` (neu)
  - `frontend/src/app/compare/page.tsx`
  - `frontend/src/app/coverage/page.tsx`
  - `frontend/src/app/artifacts/page.tsx`
  - `frontend/src/app/countries/page.tsx`
  - `frontend/src/components/layout/navigation.ts`
  - `frontend/src/styles/globals.css`
  - `frontend/tests/*` (erweitert)
  - `frontend/README.md`
  - `frontend/design/frontend_design_handoff.md`
- Tests:
  - neu: `frontend/tests/interactive-world-map.test.tsx`
  - neu: `frontend/tests/compare-view.test.tsx`
  - neu: `frontend/tests/coverage-view.test.tsx`
  - neu: `frontend/tests/artifacts-view.test.tsx`
  - neu: `frontend/tests/overview-states.test.tsx`
  - bestehende Phase-1-Tests weiterhin relevant (`app-shell`, `run-builder-submit`, `run-monitor`, `country-detail-toggle`)
- Ergebnisstand:
  - Overview ist API-gebunden ausgebaut und enthält eine interaktive SVG-Weltkarte mit Hover-Tooltip/Klicknavigation.
  - Country Detail ist API-gebunden gehärtet (KPI, Status/Confidence/Freshness, Trend, Layer, Coverage, Artifacts, Notes, Daily/Long-Term-Modus).
  - Compare/Coverage/Artifacts sind von Placeholder-Seiten zu operativ nutzbaren Arbeitsseiten ausgebaut.
  - API-Client und Typen wurden für Phase-2-Datenflüsse erweitert; spezialisierte Endpunkte nutzen klar definierte derive/fallback-pfade.
  - Lade-/Leer-/Fehler-/Teilzustände sind seitenübergreifend sichtbar abgesichert.
  - Environment note: frontend toolchain checks (`build`, `lint`, `typecheck`, `tests`) konnten in dieser Umgebung weiterhin nicht ausgeführt werden, da Node/npm nicht verfügbar ist.

### F1-03 Frontend MVP Phase 3 (UX Hardening + Navigation Polish + Charting Depth + End-to-End Workflow)
- Status: implemented_with_environment_limit
- Ziel: harden the frontend UX into a usable analyst workspace with clearer routing context, stronger chart readability, and a smoother end-to-end workflow across Overview -> Runs -> Country -> Compare/Coverage/Artifacts.
- Betroffene Requirement-IDs: frontend handoff AP-01 bis AP-11 (phase-3 scope), `PSwR-001` separation principle (boundary respected), `PSwR-018` frontend test-level expectation mirrored.
- Betroffene Open-Issues: `OI-042` (weiter offen), `OI-043` (weiter offen).
- Betroffene Codebereiche:
  - `frontend/src/components/ui/PageHeader.tsx` (neu)
  - `frontend/src/components/ui/StateCard.tsx`
  - `frontend/src/components/ui/StatusBadge.tsx`
  - `frontend/src/components/charts/TrendLineChart.tsx`
  - `frontend/src/components/map/InteractiveWorldMap.tsx`
  - `frontend/src/components/coverage/CoverageTable.tsx`
  - `frontend/src/components/artifacts/ArtifactList.tsx`
  - `frontend/src/components/layout/TopBar.tsx`
  - `frontend/src/components/layout/SidebarNav.tsx`
  - `frontend/src/features/overview/OverviewPage.tsx`
  - `frontend/src/features/runs/RunBuilderForm.tsx`
  - `frontend/src/features/runs/RunMonitorTable.tsx`
  - `frontend/src/features/runs/RunDetailView.tsx`
  - `frontend/src/features/countries/CountryDetailView.tsx`
  - `frontend/src/features/compare/CompareView.tsx`
  - `frontend/src/features/coverage/CoverageView.tsx`
  - `frontend/src/features/artifacts/ArtifactsView.tsx`
  - `frontend/src/app/countries/page.tsx`
  - `frontend/src/styles/globals.css`
  - `frontend/tests/*` (erweitert)
  - `frontend/README.md`
  - `frontend/design/frontend_design_handoff.md`
  - `docs/traceability/TraceabilityMatrix.md`
- Tests:
  - neu: `frontend/tests/page-header.test.tsx`
  - neu: `frontend/tests/trend-line-chart.test.tsx`
  - erweitert: `frontend/tests/compare-view.test.tsx`
  - erweitert: `frontend/tests/coverage-view.test.tsx`
  - erweitert: `frontend/tests/artifacts-view.test.tsx`
  - erweitert: `frontend/tests/country-detail-toggle.test.tsx`
- Ergebnisstand:
  - End-to-End-Workflow wurde UX-seitig gehaertet (PageHeader/Breadcrumbs/Quick-Jumps auf Hauptseiten).
  - Navigation/Routing sind klarer (aktive Kontextanzeige in TopBar, konsistente Header/Backpaths).
  - Overview/Country/Compare/Coverage/Artifacts wurden operativ lesbarer und steuerbarer ausgebaut.
  - Charting wurde vertieft (Hover-Tooltip, Crosshair, bessere Legenden-/Achsenlesbarkeit, Mehrfachserien).
  - Teil-, Warn- und Fehlerzustaende wurden uebergreifend staerker vereinheitlicht.
  - Environment note: frontend toolchain checks (`build`, `lint`, `typecheck`, `tests`) konnten weiterhin nicht ausgefuehrt werden, da Node/npm in dieser Umgebung nicht verfuegbar ist.

### B1-01 Backend API MVP (FastAPI layer for proto core)
- Status: completed_mvp_scope
- Ziel: provide a real Python API surface for the existing `proto/` core so frontend integration can move from fallback-heavy mode to real backend calls.
- Betroffene Requirement-IDs: API MVP AP-01 bis AP-10; separation principle from `PSwR-001` remains respected (no domain logic moved to frontend).
- Betroffene Open-Issues: `OI-044` (neu, dedicated overview/country/compare/coverage/artifacts endpoints still missing on backend side; frontend derive paths remain relevant).
- Betroffene Codebereiche:
  - `api/main.py`
  - `api/routes/system.py`
  - `api/routes/options.py`
  - `api/routes/runs.py`
  - `api/schemas/common.py`
  - `api/schemas/system.py`
  - `api/schemas/options.py`
  - `api/schemas/runs.py`
  - `api/services/errors.py`
  - `api/services/config_service.py`
  - `api/services/run_service.py`
  - `tests/test_api_mvp.py`
  - `pyproject.toml`
- Tests:
  - `tests/test_api_mvp.py` (health, info, options/template, run creation, run status/summary, unknown run id, unknown artifact)
- Ergebnisstand:
  - New root package `api/` exists with a runnable FastAPI entrypoint (`api.main:app`).
  - MVP endpoints for health/info/options/config and run lifecycle are implemented and typed with Pydantic models.
  - Run execution is prepared asynchronously (background-thread + subprocess pipeline launch) so long runs do not block HTTP requests.
  - Error responses are standardized (`validation_error`, `run_not_found`, `artifact_not_found`, `run_execution_failed`, `internal_error`).
  - Run outputs are archived per API run under `outputs/runs/api_archive/<run_id>` after pipeline completion for stable artifact access.
  - Uvicorn startup path was verified with health check (`python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000`).

### V4-32 Analyst event registry & real-world alignment
- Status: completed
- Ziel: build a structured analyst path that links major country peaks and trajectory phases to real-world events via a stable registry-based alignment flow, without introducing mandatory live-web dependency.
- Betroffene Requirement-IDs: `PSR-026`, `PSyR-041` bis `PSyR-043`, `PSwR-113` bis `PSwR-124` (plus bestehende V4.3.1-/V4.3-/V4.2-/V4.1-/V4.0-/V3.x-Baseline-IDs)
- Betroffene Methodik-/Algorithmus-IDs: `PM-063` bis `PM-071`, `ALG-048` bis `ALG-056`
- Betroffene Open-Issues: `OI-041` (neu)
- Betroffene Codebereiche:
  - `config/default.yaml`
  - `data/validation/event_registry.csv` (neu)
  - `proto/fusion/validation.py`
  - `proto/pipeline/config.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `proto/reporting/plots.py`
  - `tools/create_review_bundle.py`
  - `tests/test_fusion.py`
  - `tests/test_pipeline.py`
  - `tests/test_config.py`
- Tests:
  - `tests/test_fusion.py` (`TV-PSwR-115-001`, `TV-PSwR-116-001`, `TV-PSwR-118-001`)
  - `tests/test_config.py` (`TV-PSwR-122-001`, `TV-PSwR-122-002`)
  - `tests/test_pipeline.py` (`TV-PSwR-113-001` bis `TV-PSwR-121-001`, `TV-PSwR-123-001`, `TV-PSwR-124-001`)
- Ergebnisstand:
  - Event-Registry-Schema und initialer 10-Laender-Bestand sind als analystische Fixture-Basis integriert.
  - Peak-Event-Matching liefert gestufte Klassen (`direct_match`, `plausible_context_match`, `weak_match`, `no_credible_match`, `multi_event_overlap`) inkl. Match-Confidence und Review-Hinweisen.
  - Event-Coverage-/Alignment-Maturity-Diagnostik ist als eigener Exportpfad aktiv.
  - V4.3.2-Artefakte sind im Handout, in V4.3.2-Landplots, im Acceptance Snapshot und im Review-Bundle sichtbar.
  - Neue Event-Alignment-Warnings bleiben dosiert und additiv; bestehende V2.x-/V3.x-/V4.0-/V4.1-/V4.2-/V4.3-/V4.3.1-Pfade bleiben erhalten.

### V4-31 Peak attribution & event alignment hardening
- Status: completed
- Ziel: harden 356-day peak interpretation by separating global co-movement from country-specific peak behavior, exposing peak attribution and event support explicitly across exports, handout, validation, and review bundle.
- Betroffene Requirement-IDs: `PSR-025`, `PSyR-039`, `PSyR-040`, `PSwR-105` bis `PSwR-112` (plus bestehende V4.3-/V4.2-/V4.1-/V4.0-/V3.x-Baseline-IDs)
- Betroffene Methodik-/Algorithmus-IDs: `PM-057` bis `PM-062`, `ALG-041` bis `ALG-047`
- Betroffene Open-Issues: `OI-040` (neu)
- Betroffene Codebereiche:
  - `config/default.yaml`
  - `data/validation/event_marker_registry.csv` (neu)
  - `proto/fusion/validation.py`
  - `proto/pipeline/config.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `proto/reporting/plots.py`
  - `tools/create_review_bundle.py`
  - `tests/test_fusion.py`
  - `tests/test_pipeline.py`
  - `tests/test_config.py`
- Tests:
  - `tests/test_fusion.py` (`TV-PSwR-105-001`)
  - `tests/test_config.py` (`TV-PSwR-106-001`)
  - `tests/test_pipeline.py` (`TV-PSwR-107-001`, `TV-PSwR-108-001`, `TV-PSwR-109-001`, `TV-PSwR-111-001`, `TV-PSwR-112-001`)
- Ergebnisstand:
  - Peak-Erkennung im 356-Tage-Raum wurde von rohen Maxima auf gehaertete Peak-Kandidaten (Prominenz/Rise/Fall/Breite/Separation) umgestellt.
  - Peak-Attribution ist als eigener Exportpfad vorhanden (`peak_attribution.csv`), inklusive global-vs-country-Share, Dominanz- und Support-Feldern.
  - Event-Support wird ueber eine versionierte Marker-Registry gespiegelt (`event_marker_registry.csv`, `peak_event_support.csv`).
  - Trajectory-Profile und globale Peak-Synchronisationsdiagnostik sind exportiert (`trajectory_profiles.csv`, `global_peak_synchronization.csv`).
  - V4.3.1-Plot- und Handout-Sicht ist aktiv (`v431_peak_attribution_<country>.png`, `v431_global_peak_synchronization.png`, V4.3.1-Block im Handout).
  - Acceptance Snapshot / Review Bundle transportieren die neuen V4.3.1-Artefakte additiv.
  - Bestehende V2.x-/V3.x-/V4.0-/V4.1-/V4.2-/V4.3-Pfade bleiben intakt (gezielte und Regressionstests gruen).

### V4-30 Comparative expansion: 10 countries, full 356-day profiles
- Status: completed
- Ziel: expand the monitor to a fixed 10-country comparison space with full 356-day profile-driven diagnostics, artifacts, plots, and equal-depth reporting.
- Betroffene Requirement-IDs: `PSR-024`, `PSyR-036` bis `PSyR-038`, `PSwR-097` bis `PSwR-104` (plus bestehende V4.2-/V4.1-/V4.0-/V3.x-Baseline-IDs)
- Betroffene Methodik-/Algorithmus-IDs: `PM-052` bis `PM-056`, `ALG-036` bis `ALG-040`
- Betroffene Open-Issues: `OI-039` (neu)
- Betroffene Codebereiche:
  - `config/default.yaml`
  - `proto/fusion/validation.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/plots.py`
  - `proto/reporting/handout.py`
  - `tools/create_review_bundle.py`
  - `tests/test_fusion.py`
  - `tests/test_pipeline.py`
- Tests:
  - `tests/test_fusion.py` (`TV-PSwR-098-001`)
  - `tests/test_pipeline.py` (`TV-PSwR-098-002`, bestehende Pipeline-TV-IDs erweitert)
- Ergebnisstand:
  - Verbindlicher 10-Laender-Raum ist technisch erzwungen und in allen Kernartefakten konsistent.
  - Neue V4.3-Vergleichsartefakte vorhanden:
    - `validation_country_profiles.csv`
    - `validation_peak_phases.csv`
    - `validation_group_profiles.csv`
    - `validation_ranking_trajectory.csv`
  - Neue V4.3-Plots vorhanden:
    - `v43_country_profile_<country>.png`
    - `v43_multicountry_fusion_total.png`
    - `v43_multicountry_ranking_trajectory.png`
  - Handout fuehrt globalen V4.3-Vergleichsteil vor gleich tiefen Laenderkapiteln.
  - Acceptance Snapshot / Review-Bundle transportieren die V4.3-Vergleichssicht additiv.
  - Bestehende V2.x-/V3.x-/V4.0-/V4.1-/V4.2-Pfade bleiben intakt (Tests gruen).

### V4-20 Governance & political stability expansion
- Status: completed
- Ziel: extend the existing V4.1 monitor with an explicit governance/political-stability analytical dimension, integrated end-to-end in canonical observations, snapshot/historical fusion, diagnostics, validation and review artifacts.
- Betroffene Requirement-IDs: `PSR-023`, `PSyR-034`, `PSyR-035`, `PSwR-091` bis `PSwR-096` (plus bestehende V4.1-/V4.0-/V3.x-Baseline-IDs)
- Betroffene Methodik-/Algorithmus-IDs: `PM-049` bis `PM-051`, `ALG-033` bis `ALG-035`
- Betroffene Open-Issues: `OI-038` (neu)
- Betroffene Codebereiche:
  - `data/governance_input/governance_input.csv` (neu)
  - `proto/sources/governance_input.py` (neu)
  - `proto/observations/schema.py`
  - `proto/fusion/freshness.py`
  - `proto/fusion/validation.py`
  - `proto/pipeline/config.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `tools/create_review_bundle.py`
  - `config/default.yaml`
  - `data/validation/reference_episodes.csv`
- Tests:
  - `tests/test_sources.py` (`TV-PSwR-091-001`)
  - `tests/test_observations.py` (`TV-PSwR-091-002`)
  - `tests/test_fusion.py` (`TV-PSwR-093-001`, `TV-PSwR-094-001`)
  - `tests/test_pipeline.py` (`TV-PSwR-095-001`, `TV-PSwR-096-001`)
- Ergebnisstand:
  - Governance ist als eigenstaendige Gruppe (`governance`) und als kanonischer Adapterpfad (`governance_input`) integriert.
  - Governance wirkt in Snapshot- und Historical-Fusion operativ mit (Gruppenscores, Total-Scores, Historical-Verlaeufe).
  - Validation/Diagnostics fuehren governance-spezifische Felder/Flags (Instability, Contribution-Share, Low-Freshness) und governancebezogene Warnings.
  - Referenzepisoden und Validation Summary enthalten Governance-Reviewanker.
  - Handout, `fusion_status`, Acceptance-Snapshot und Review-Bundle transportieren die Governance-Sicht additiv.
  - Bestehende V2.x-/V3.x-/V4.0-/V4.1-Pfade bleiben intakt (Tests weiterhin gruen).

### V4-10 Operational freshness & responsiveness
- Status: completed
- Ziel: improve operational freshness, temporal responsiveness and near-term analytical usability of the existing V4.0 monitor without introducing a new source megablock.
- Betroffene Requirement-IDs: `PSR-022`, `PSyR-032`, `PSyR-033`, `PSwR-083` bis `PSwR-090` (plus bestehende V4.0-/V3.x-Baseline-IDs)
- Betroffene Methodik-/Algorithmus-IDs: `PM-042` bis `PM-048`, `ALG-029` bis `ALG-032`
- Betroffene Open-Issues: `OI-036` (weiter offen, partiell mitigiert), `OI-037` (neu)
- Betroffene Codebereiche:
  - `proto/fusion/freshness.py` (neu)
  - `proto/fusion/scoring.py`
  - `proto/fusion/validation.py`
  - `proto/pipeline/config.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `tools/create_review_bundle.py`
  - `config/default.yaml`
- Tests:
  - `tests/test_fusion.py` (`TV-PSwR-083-001`, `TV-PSwR-085-001`, `TV-PSwR-086-001`)
  - `tests/test_config.py` (`TV-PSwR-083-002`)
  - `tests/test_pipeline.py` (`TV-PSwR-085-002`, erweiterte V4.1-Assertions in bestehendem V4.0-Pfad)
- Ergebnisstand:
  - Freshness-/Staleness-Modell ist explizit eingefuehrt und konfigurierbar.
  - Event-Recency/Decay wurde operativ nachgeschaerft (inkl. Fresh-Boost und stale Abschwaechung).
  - Snapshot-Freshness-Diagnostik und Historical-Responsiveness-Metriken werden als eigene Artefakte exportiert.
  - Validation Summary/Handout/Warnings enthalten operative Freshness- und Responsiveness-Kennzahlen.
  - Acceptance-Snapshot und Review-Bundle transportieren die V4.1-Operativsicht.
  - Bestehende V2.x-/V3.x-/V4.0-Pfade bleiben intakt (Tests weiterhin gruen).

### V4-00 External validation & calibration
- Status: completed
- Ziel: mirror the existing multi-layer monitor against structured real-world reference episodes, calibrate fusion response logic, and harden analyst-facing validation artifacts without introducing new source megablocks.
- Betroffene Requirement-IDs: `PSR-004`, `PSR-016`, `PSR-018`, `PSR-020`, `PSR-021`, `PSyR-023`, `PSyR-028`, `PSyR-029`, `PSyR-030`, `PSyR-031`, `PSwR-041`, `PSwR-042`, `PSwR-045`, `PSwR-056`, `PSwR-062`, `PSwR-063`, `PSwR-064`, `PSwR-069`, `PSwR-075` bis `PSwR-082`
- Betroffene Methodik-/Algorithmus-IDs: `PM-028`, `PM-029`, `PM-032`, `PM-033`, `PM-034`, `PM-035` bis `PM-041`, `ALG-021`, `ALG-022`, `ALG-023`, `ALG-024`, `ALG-025` bis `ALG-028`
- Betroffene Open-Issues: `OI-026`, `OI-034`, `OI-035` (neu), `OI-036` (neu)
- Betroffene Codebereiche:
  - `data/validation/reference_episodes.csv`
  - `config/default.yaml`
  - `proto/fusion/scoring.py`
  - `proto/fusion/validation.py` (neu)
  - `proto/pipeline/config.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `tools/create_review_bundle.py`
- Tests:
  - `tests/test_fusion.py` (`TV-PSwR-077-001`, `TV-PSwR-079-002`, `TV-PSwR-081-001`)
  - `tests/test_config.py` (`TV-PSwR-078-001`, `TV-PSwR-079-001`)
  - `tests/test_pipeline.py` (`TV-PSwR-080-001`, `TV-PSwR-080-002`)
- Ergebnisstand:
  - Expliziter Validierungsrahmen wird als Artefakt exportiert (`validation_framework.json`).
  - Versionierbare Referenzepisoden sind als Review-Anker integriert (`validation_reference_episodes.csv`).
  - Episoden-, Timing-, Ranking- und Diagnostikmetriken sind operationalisiert (`validation_episode_review.csv`, `validation_country_ranking.csv`, `validation_layer_diagnostics.csv`, `validation_summary.json`).
  - Fusion-Kalibrierprofil ist explizit konfigurierbar (Gewichte, Fusion-Stage/Trend-Schwellen, Dominanz-/Coverage-/Event-Recency-Regeln).
  - Event-Recency/Decay wirkt nun direkt im Fusion-Scorepfad; stale Event-Lagen bleiben sichtbar markiert.
  - Handout, `fusion_status.json`, Acceptance-Snapshot und Review-Bundle transportieren den Validierungsstand.
  - Bestehende V2.x-/V3.x-Pfade bleiben intakt (Tests weiterhin gruen).

### V3-03 Event layer integration
- Status: completed
- Ziel: operationalize `event` as a real layer in the existing V3 fusion architecture (snapshot + historical), without breaking V2.x/V3.1/V3.2 paths.
- Betroffene Requirement-IDs: `PSR-020`, `PSyR-029`, `PSwR-071`, `PSwR-072`, `PSwR-073`, `PSwR-074`, `PSwR-041`, `PSwR-042`, `PSwR-045`, `PSwR-056`, `PSwR-057`, `PSwR-062`, `PSwR-063`, `PSwR-064`, `PSwR-066`, `PSwR-069`
- Betroffene Methodik-/Algorithmus-IDs: `PM-032`, `PM-033`, `PM-034`, `ALG-023`, `ALG-024`, `ALG-014`, `ALG-015`, `ALG-017`, `ALG-021`, `ALG-022`
- Betroffene Open-Issues: `OI-033` (geschlossen), `OI-034` (neu, non-blocking)
- Betroffene Codebereiche:
  - `proto/sources/gdelt_event.py`
  - `proto/pipeline/config.py`
  - `proto/pipeline/run_proto.py`
  - `config/default.yaml`
  - `proto/fusion/*` (bestehender Pfad, additiv genutzt)
  - `proto/reporting/*` (bestehender Pfad, additiv genutzt)
- Tests:
  - `tests/test_sources.py` (`TV-PSwR-071-001`, `TV-PSwR-072-001`)
  - `tests/test_observations.py` (`TV-PSwR-071-002`)
  - `tests/test_fusion.py` (`TV-PSwR-073-001`)
  - `tests/test_pipeline.py` (Event-Artefakt-/Warning-Absicherung)
- Ergebnisstand:
  - `event` ist nicht mehr pauschal `not_available`.
  - Erste echte Event-Quelle ist integriert (`gdelt_event`, aus GDELT-Rohereignissen periodisiert).
  - Event-Signale sind in Snapshot- und Historical-Fusion wirksam.
  - Event erscheint in Explainability, Handout, Exporten, Plots und Acceptance-Snapshot.
  - Event-spezifische nicht-blockierende Plausibilitaetswarnungen sind sichtbar (`event_signal_stale`, ggf. weitere Kontextwarnungen).

### V3-02.2 Semantic polish
- Status: completed
- Ziel: close remaining semantic/reporting polish points after V3.2.1 without changing architecture or source scope.
- Betroffene Requirement-IDs: `PSR-003`, `PSR-016`, `PSR-018`, `PSyR-023`, `PSyR-028`, `PSwR-063`, `PSwR-064`, `PSwR-066`, `PSwR-069`
- Betroffene Methodik-/Algorithmus-IDs: `PM-028`, `PM-029`, `PM-030`, `ALG-022`
- Betroffene Open-Issues: `OI-032` (weiter offen fuer alternative Zielperioden)
- Betroffene Codebereiche:
  - `proto/fusion/models.py`
  - `proto/fusion/scoring.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
- Tests:
  - `tests/test_fusion.py` (`TV-PSwR-064-002`)
  - `tests/test_pipeline.py` (`TV-PSwR-066-002`, `TV-PSwR-069-002`)
- Ergebnisstand:
  - `strongest_change_group` wird bei nicht-materieller Delta-Lage nicht mehr kuenstlich gesetzt; stattdessen `no_material_change=true`.
  - Historische Total-Scores fuehren `interpretation_status` explizit (`standard`/`reduced_historical_coverage`/`limited_historical_coverage`).
  - Handout markiert eingeschraenkte fruehe historische Perioden klarer und fuehrt die Interpretationskennzeichnung sichtbar.
  - Plausibilitaetswarnungen fuer historische Niedrigabdeckung sind konsolidiert (`historical_low_group_coverage_summary`) statt warn-flutartiger Einzelmeldungen.

### V3-02.1 Calibration & explainability hardening
- Status: completed
- Ziel: harden the existing V3.2 historical fusion path for better plausibility, differentiation, and analyst explainability without replacing the existing architecture.
- Betroffene Requirement-IDs: `PSR-004`, `PSR-016`, `PSR-018`, `PSyR-023`, `PSyR-025`, `PSyR-026`, `PSyR-028`, `PSwR-040`, `PSwR-045`, `PSwR-058`, `PSwR-060`, `PSwR-061`, `PSwR-062`, `PSwR-063`, `PSwR-064`, `PSwR-066`, `PSwR-069`
- Betroffene Methodik-/Algorithmus-IDs: `PM-018`, `PM-021`, `PM-026`, `PM-027`, `PM-028`, `PM-029`, `PM-030`, `ALG-017`, `ALG-019`, `ALG-020`, `ALG-021`, `ALG-022`
- Betroffene Open-Issues: `OI-031`, `OI-032`, `OI-033`
- Betroffene Codebereiche:
  - `config/default.yaml`
  - `proto/pipeline/config.py`
  - `proto/sources/narrative_input.py`
  - `proto/sources/unhcr.py`
  - `proto/fusion/models.py`
  - `proto/fusion/confidence.py`
  - `proto/fusion/scoring.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
- Tests:
  - `tests/test_config.py`
  - `tests/test_sources.py`
  - `tests/test_fusion.py`
  - `tests/test_pipeline.py`
- Ergebnisstand:
  - Narrative/Displacement sind kalibriert (`global`-Scope + `z_score` in Standardkonfiguration) und differenzieren Laender wieder plausibel.
  - Historische Fusion-Total-Exporte fuehren explizite Layer-Abdeckung (`available_group_count`, `expected_group_count`, `available_group_ratio`).
  - Driver-Erklaerung erweitert: Top-1/Top-2 Beitragslayer und staerkste Gruppenveraenderung zum Vorzeitpunkt.
  - Fusion-Confidence bleibt getrennt vom Score und fuehrt zusaetzliche Dominanz-/Limited-Penalties transparent mit.
  - Nicht-blockierende Plausibilitaetswarnungen sind in `fusion_status.json` und Handout sichtbar.
  - V2.x-/V3.1-/V3.2-Bestandspfade bleiben intakt.

### V3-01.1 MVP completion / handout- and plot-consistency fix
- Status: completed
- Ziel: close remaining V3.1 MVP follow-up on handout/plot consistency (`RP-01`) and tighten V3.1 handout wording without changing output structure.
- Betroffene Requirement-IDs: `PSR-013`, `PSR-015`, `PSyR-019`, `PSyR-020`, `PSwR-051`, `PSwR-053`, `PSwR-067`
- Betroffene Methodik-/Algorithmus-IDs: `PM-017`, `PM-020`, `PM-023`, `PM-030`, `ALG-014`, `ALG-015`, `ALG-017`
- Betroffene Open-Issues: `OI-030`
- Betroffene Codebereiche:
  - `proto/pipeline/run_proto.py` (robustes Plot-Landmapping, bereits aktiv)
  - `proto/reporting/handout.py` (V3.1-Block sprachlich geschaerft)
- Tests:
  - `tests/test_pipeline.py` (`TV-PSwR-053-002`)
- Ergebnisstand:
  - Landbezogene Fusion-Plots werden im Handout konsistent referenziert, wenn Dateien vorhanden sind.
  - Keine falsche `manual review required`-Meldung mehr im V3.1-Land-Fusionsplot-Abschnitt bei vorhandenen Plotdateien.
  - V3.1-/V2.x-Stand bleibt intakt.

### V3-02 Historical multi-layer expansion + time-aware fusion
- Status: implemented_with_provisional_scope
- Ziel: extend V3.1 to a historical, time-aware fusion path with first operational `Shock`, `Displacement`, and `Narrative` layers.
- Betroffene Requirement-IDs: `PSR-016`, `PSR-017`, `PSR-018`, `PSR-019`, `PSyR-023` bis `PSyR-028`, `PSwR-053` bis `PSwR-070`
- Betroffene Methodik-/Algorithmus-IDs: `PM-024` bis `PM-031`, `ALG-018` bis `ALG-022`
- Betroffene Open-Issues: `OI-030`, `OI-031`, `OI-032`, `OI-033`
- Betroffene Codebereiche:
  - `config/default.yaml`
  - `proto/sources/gdacs.py`
  - `proto/sources/unhcr.py`
  - `proto/sources/narrative_input.py`
  - `proto/fusion/*`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `proto/reporting/plots.py`
  - `data/gdacs/gdacs_events.csv`
  - `data/unhcr/unhcr_displacement.csv`
  - `data/narrative_input/narrative_input.csv`
- Tests:
  - `tests/test_sources.py`
  - `tests/test_observations.py`
  - `tests/test_fusion.py`
  - `tests/test_pipeline.py`
- Ergebnisstand:
  - RP-01 geschlossen: landbezogene Fusion-Plot-Einbindung im Handout ist konsistent.
  - `GDACS` (`shock`), `UNHCR` (`displacement`) und `narrative_input` (`narrative`) sind als kanonische Adapter integriert.
  - Historischer Fusion-Pfad (monatliche Zielperioden) ist implementiert:
    - historische source signals
    - historische group scores
    - historische fusion total scores
  - Historische Fusion-Plots (Gruppen + Gesamt) global und landbezogen sind vorhanden.
  - Historische Driver-Hinweise (dominanter Gruppenimpuls) sind im Fusion-Historical-Output sichtbar.
  - V2.x- und V3.1-Bestandspfade bleiben intakt.
- Provisorische Restpunkte:
  - Narrative-Validierungs-/Taxonomie-Regeln bleiben offen (`OI-031`).
  - Zielperioden jenseits `monthly` bleiben offen (`OI-032`).
  - `event`-Gruppe bleibt im MVP `not_available` (`OI-033`).

### V3-01 Multi-source layer integration + first fusion MVP
- Status: implemented_with_provisional_scope
- Ziel: establish the V3.1 architecture with canonical observations, layer logic, adapter contract and a first parallel fusion MVP with Food/Structural focus.
- Betroffene Requirement-IDs: `PSR-012`, `PSR-013`, `PSR-014`, `PSR-015`, `PSyR-018`, `PSyR-019`, `PSyR-020`, `PSyR-021`, `PSyR-022`, `PSwR-036` bis `PSwR-052`
- Betroffene Methodik-/Algorithmus-IDs: `PM-016` bis `PM-023`, `ALG-013` bis `ALG-017`
- Betroffene Open-Issues: `OI-025`, `OI-026`, `OI-027`, `OI-028`, `OI-029`
- Betroffene Codebereiche:
  - `proto/observations/*`
  - `proto/sources/fao_ffpi.py`
  - `proto/sources/fao_fpma.py`
  - `proto/sources/un_comtrade.py`
  - `proto/fusion/*`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `proto/reporting/plots.py`
  - `proto/reporting/exports.py`
  - `config/default.yaml`
- Tests:
  - `tests/test_observations.py`
  - `tests/test_sources.py`
  - `tests/test_fusion.py`
  - `tests/test_pipeline.py`
- Ergebnisstand:
  - Kanonisches Observation-Schema + Validierung + Adapter-Contract sind implementiert.
  - V3.1-MVP-Quellen `FAO FFPI`, `FAO FPMA`, `UN Comtrade` sind als Adapter integriert.
  - Quellspezifische Normalisierung (`z_score`, `percentile`, `baseline_deviation`) ist konfigurierbar in `config/default.yaml`.
  - Gruppenfusion ist operativ fuer `market_food` und `structural`; weitere Gruppen sind als explizite `not_available`-Struktur vorhanden.
  - Paralleler Fusion-Gesamtscore inkl. optionalem (standardmaessig deaktiviertem) Bonusmechanismus ist implementiert.
  - Fusion-Confidence wird getrennt vom Score berechnet und separat exportiert.
  - Additive V3.1-Artefakte (Export/Handout/Plot) laufen parallel zur bestehenden Cluster-Sicht ohne Bruch des V2.x-Standards.
- Provisorische Restpunkte:
  - Source-/Group-Defaultgewichte bleiben heuristisch (`OI-026`).
  - Volltiefe Operationalisierung von `Event`, `Narrative`, `Shock`, `Displacement` bleibt Follow-up (`OI-029`).


### V2-23 Output-Review Follow-up (`OI-021` bis `OI-024`)
- Status: completed
- Ziel: methodisch und darstellerisch den V2.2-Stand nach erstem fachlichen Output-Review nachschärfen.
- Betroffene Requirement-IDs: `PSR-003`, `PSR-005`, `PSR-009`, `PSwR-007`, `PSwR-009`, `PSwR-010`, `PSwR-011`, `PSwR-016`, `PSwR-022`, `PSwR-026`, `PSwR-032`, `PSwR-033`, `PSwR-034`
- Betroffene Methodik-/Algorithmus-IDs: `PM-001`, `PM-005`, `PM-010`, `PM-012`, `PM-013`, `PM-014`, `ALG-001`, `ALG-003`, `ALG-004`, `ALG-012`
- Betroffene Open-Issues: `OI-021`, `OI-022`, `OI-023`, `OI-024`
- Betroffene Codebereiche:
  - `proto/scoring/confidence.py`
  - `proto/scoring/trend_history.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `proto/reporting/plots.py`
- Tests:
  - `tests/test_scoring.py` (`TV-PSwR-022-003`, `TV-PSwR-022-004`)
  - `tests/test_pipeline.py` (`TV-PSwR-022-005`, `TV-PSwR-032-002`, `TV-PSwR-034-002`)
  - `tests/test_integration_processing.py` (`TV-PSwR-007-002`)

### V2-22 Dual official result areas (`Current Snapshot` + `Historical Rolling Trend`)
- Status: completed
- Ziel: implement official dual-output standard run with strict artifact separation and shared rolling logic for snapshot + historical trend.
- Betroffene Requirement-IDs: `PSR-008`, `PSR-009`, `PSR-010`, `PSR-011`, `PSyR-011`, `PSyR-012`, `PSyR-013`, `PSyR-014`, `PSyR-015`, `PSyR-016`, `PSyR-017`, `PSwR-020` bis `PSwR-035`
- Betroffene Methodik-/Algorithmus-IDs: `PM-008` bis `PM-015`, `ALG-009` bis `ALG-012`
- Betroffene Open-Issues: `OI-014`, `OI-015`, `OI-016`, `OI-017`, `OI-018`
- Betroffene Codebereiche:
  - `config/default.yaml`
  - `proto/pipeline/config.py`
  - `proto/scoring/trend_history.py`
  - `proto/scoring/confidence.py`
  - `proto/pipeline/run_proto.py`
  - `proto/reporting/handout.py`
  - `proto/reporting/plots.py`
  - `proto/runs/reference.py`
- Tests:
  - `tests/test_config.py` (`TV-PSwR-021-001`, `TV-PSwR-026-001`, `TV-PSwR-031-001`, `TV-PSwR-035-001`)
  - `tests/test_scoring.py` (`TV-PSwR-021-002`, `TV-PSwR-022-001`, `TV-PSwR-024-001`, `TV-PSwR-027-001`, `TV-PSwR-033-001`, `TV-PSwR-034-001`)
  - `tests/test_pipeline.py` (`TV-PSyR-012-001`, `TV-PSwR-022-002`, `TV-PSyR-017-001`, `TV-PSwR-031-002`)

### V2-07 Fresh reference run and reference migration
- Status: completed
- Ziel: create a fresh reference run with full metadata and documented `current_reference` schema; keep legacy references compatible as fallback only.
- Betroffene Requirement-IDs: `PSyR-008`, `PSyR-010`, `PSwR-017`
- Betroffene Methodik-/Algorithmus-IDs: `PM-001`, `ALG-008`
- Betroffene Codebereiche: `proto/runs/reference.py`, `proto/runs/models.py`, `proto/pipeline/run_proto.py`
- Tests: `tests/test_runs.py` (`TV-PSyR-010-002`, `TV-PSyR-010-008`, `TV-PSyR-010-010`, `TV-PSyR-010-005`), `tests/test_pipeline.py` (`TV-PSyR-010-009`, `TV-PSyR-010-011`, `TV-PSyR-010-007`)

### V2-08 Controlled change case and delta proof
- Status: completed
- Ziel: prove that `run_comparison.json` and `reference_comparison.json` show real deltas on controlled snapshot changes.
- Betroffene Requirement-IDs: `PSyR-009`, `PSyR-010`, `PSwR-017`, `PSwR-018`
- Betroffene Methodik-/Algorithmus-IDs: `PM-001`, `ALG-008`
- Betroffene Codebereiche: `proto/runs/compare_runs.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py`
- Tests: `tests/test_runs.py` (`TV-PSyR-009-004`, `TV-PSyR-009-007`), `tests/test_integration_processing.py` (`TV-PSyR-009-008`), `tests/test_pipeline.py` (`TV-PSyR-009-005`, `TV-PSyR-010-004`, `TV-PSyR-006-002`, `TV-PSwR-016-002`)
- Fixtures: `tests/fixtures/change_case/gdelt_events_baseline.csv`, `tests/fixtures/change_case/gdelt_events_changed.csv`

### V2-01 Calibrated and configurable stage/trend rules
- Status: completed
- Ziel: calibrate thresholds/trend limits further and remove hard V1 defaults in scoring paths where sensible.
- Betroffene Requirement-IDs: `PSwR-002`, `PSwR-012`, `PSwR-013`
- Betroffene Methodik-/Algorithmus-IDs: `PM-006`, `ALG-005`, `ALG-006`
- Betroffene Codebereiche: `config/default.yaml`, `proto/scoring/thresholds.py`, `proto/scoring/trend.py`, `proto/pipeline/run_proto.py`, `proto/pipeline/config.py`
- Tests: `tests/test_config.py`, `tests/test_scoring.py`, `tests/test_integration_processing.py`
- V2.1 Profil: `stage(30/56/80)` und `trend.delta_epsilon=1.25`

## Standard Mode
- Countries: Germany, Israel, Iran, Ukraine, Russia, Japan, China, Taiwan, Poland, Nigeria
- Windows: 7d, 30d, 356d baseline
- Historical horizon: 356d
- Single standard mode only

## Review-Befund V2.2: First functional output check (2026-04-06)

### Status
- Status: documented review
- Ziel: record the first technical/factual review findings after successful implementation of the dual official result areas `Current Snapshot` + `Historical Rolling Trend`.
- Bezug: first real output inspection after successful `python -m pytest` and `python -m proto.pipeline.run_proto`.

### Positiver Befund
- The standard run now produces the two official result areas:
  - `Current Snapshot`
  - `Historical Rolling Trend`
- Snapshot and historical artifacts are structurally separated.
- Historical exports, historical cluster plots, and historical subscore plots are present.
- Historical validity/coverage logic is visible in the exported time-series.
- The handout presents per-country sections for snapshot and historical trend.

### Review-Feststellungen
- `tension` and `escalation` currently behave as the dynamic/event-near clusters.
- `vulnerability` currently behaves across all three countries as a near-constant structural/baseline cluster.
- Cluster curves are in principle consistent with the visible subscore curves.
- For valid endpoints, the snapshot can be matched to the last valid historical rolling point.
- The most important open methodological point remains the snapshot fallback behavior when the historical end-point does not satisfy minimum coverage.

### Review-Folgepunkte
- Normatively sharpen snapshot fallback behavior for under-covered historical endpoints.
- Decide whether `vulnerability` is intentionally a largely static structural cluster or should later gain historical time dynamics.
- Review the strong `Germany / tension / protest_subscore` jump for factual plausibility.
- Improve plot readability and handout text/encoding quality.

### Einschätzung
V2.2 is functionally successful. V2.2.1 closes the first review follow-ups (`OI-021` bis `OI-024`) with explicit snapshot fallback provenance/penalty, baseline-marking for `vulnerability`, documented Germany protest-path plausibility, and improved plot/encoding readability.
