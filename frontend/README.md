# Frontend

Separates Web-Frontend fuer das Python-Analyseprojekt.

## Architekturprinzipien
- keine Fachlogik im Frontend
- API-only Kommunikation (`/api/v1/*`)
- Stitch als Designreferenz, keine 1:1 HTML-Uebernahme
- dark / clean / fullscreen analyst UI
- robust gegen partielle API-Verfuegbarkeit (zentraler API-Adapter, keine verteilten Seiten-Mocks)

## Stand: Stabilization + Test Automation MVP

### End-to-End-Workflow
- Overview (`/`)
  - KPI + Insight Rail + interaktive Weltkarte mit Statusfilter
  - direkte Navigation in Country Detail / Run Detail / Coverage
  - TopBar zeigt Backend-Zustand (`connected` / `unavailable` / `mock mode active`)
- Run Builder (`/runs/new`)
  - API-gebundener Run-Start mit hartem Backend/Mock-Verhalten:
    - backend unavailable + mock disabled -> kein Run-Start, klare Fehlermeldung
    - mock mode active -> Run wird explizit als Mock-Run markiert
- Run Monitor (`/runs`)
  - Polling + Statusfilter + direkter Sprung in Run Detail
- Run Detail (`/runs/[runId]`)
  - partial-robuste Ladepfade (allSettled), Runtime-Status, Summary, Artifacts, Countries
  - Quick-Jumps zu Compare/Coverage/Artifacts
- Country Detail (`/countries/[countryCode]`)
  - Daily vs Long-Term, KPI/Status/Freshness, Trend + Freshness-Chart, Layer/Coverage/Artifacts/Notes
  - Compare-Deep-Link und Source-Run-Link
- Compare (`/compare`)
  - Deep-Link-Selection (`?countries=...`), Mehrfachauswahl, KPI/Trend/Peak-Vergleich
- Coverage (`/coverage`)
  - Statusfilter + Suche + Country-Drilldown
- Artifacts (`/artifacts`)
  - Run-gruppiert, Statusfilter, available-only Modus, Run-Detail-Links

### Reusable UX-Komponenten (Phase 3 erweitert)
- `PageHeader` (Breadcrumbs + Actions)
- `InteractiveWorldMap`
- `TrendLineChart` (Hover-Tooltip/Crosshair)
- `KpiCard`
- `SectionHeader`
- `CoverageTable`
- `ArtifactList`
- `StateCard` / `StatusBadge`

## API-Mapping

### Direkt genutzte Endpunkte
- `GET /health`
- `GET /options/countries`
- `GET /options/layers`
- `GET /runs`
- `POST /runs`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/status`
- `GET /runs/{run_id}/summary`
- `GET /runs/{run_id}/artifacts`
- `GET /overview`

### Optional genutzte Endpunkte (wenn verfuegbar)
- `GET /countries/{country}/detail`
- `GET /countries/{country}/summary`
- `GET /countries/{country}`
- `GET /coverage`
- `GET /data-status`
- `GET /countries/coverage`
- `GET /compare?countries=...`
- `GET /countries/compare?countries=...`
- `GET /artifacts`
- `GET /runs/artifacts`

### Fallback-/Degradation-Strategie
- zentrale Steuerung ueber `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK` (`true|false`)
- default: `false` (kein stiller Mock-Betrieb)
- keine seiten-spezifischen Hardcoded-Mocks
- derive-pfade bei fehlenden Spezialendpunkten:
  - Coverage aus `overview` + `options/*`
  - Compare aus `overview`
  - Artifacts-Uebersicht aus `runs` + `runs/{id}/artifacts`
  - Country Detail aus `overview` + fallback-country-record
- zentraler Mock-Fallback aus `src/lib/api/fallback.ts` nur bei explizit aktivem Mock-Modus
- `POST /runs` erzeugt niemals still Fake-Runs:
  - nur bei aktivem Mock-Modus wird `mock_run_*` bewusst erzeugt und im UI markiert
  - sonst wird ein `Backend unavailable`-Fehler propagiert

## Bekannte API-Luecken / Restpunkte
- stabile Country-Detail-Endpunkte sind nicht in jeder Umgebung garantiert (`OI-042`)
- dedizierte Compare-/Coverage-/Artifacts-Aggregatendpunkte sind nicht durchgaengig verfuegbar (`OI-043`)
- Run-Logs/Timeline fuer noch bessere Run-Detail-UX sind aktuell nicht verbindlich spezifiziert

## Test Automation MVP

### Test-Stack
- `Vitest`
- `@testing-library/react`
- `@testing-library/jest-dom`
- `@testing-library/user-event`
- `jsdom`
- `@playwright/test` (Chromium)

### Teststruktur
- `tests/unit/*` - schnelle Komponenten-/Seitenlogiktests
- `tests/integration/*` - integrationsnahe Frontend-Flows (ohne echten Browser)
- `tests/e2e/mock/*` - Browser-Smoke + Core-Flows im expliziten Mock-Modus
- `tests/e2e/api/*` - Browser-Checks mit Mock-Fallback aus (API-Modus/Backend unavailable path)

### Mock/API-Mode-Trennung in Tests
- Unit/Integration:
  - API-Responses werden bewusst pro Test gemockt (kein stiller Fallback).
  - `tests/unit/api-client-fallback-separation.test.ts` prueft explizit:
    - `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=false` -> kein stiller Fake-Run bei `POST /runs`
    - `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true` -> expliziter Mock-Run mit sichtbarer Kennzeichnung
- Playwright Mock-Mode:
  - Config: `playwright.mock.config.ts`
  - erzwingt `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true`
  - nutzt standardmaessig ein nicht erreichbares Backend (`http://127.0.0.1:8999/api/v1`), damit Mock-Verhalten deterministisch pruefbar ist.
- Playwright API-Mode:
  - Config: `playwright.api.config.ts`
  - erzwingt `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=false`
  - prueft, dass bei fehlendem Backend keine stillen Fake-Erfolge entstehen.
  - optional kann ein echtes Backend via `PLAYWRIGHT_BACKEND_BASE_URL` gesetzt werden.
- Stabile Selektoren fuer kritische UI-Punkte sind gesetzt (u. a. Backend-Status, Run Builder Submit/Toggle, Country-Mode-Toggle, Overview-Map, Run Monitor, Compare Controls).

## Struktur
- `src/app/*`: Routing und Seiten
- `src/components/layout/*`: App Shell
- `src/components/ui/*`: UI-Primitives
- `src/components/map/*`: Kartenkomponenten
- `src/components/charts/*`: Diagrammkomponenten
- `src/components/coverage/*`: Coverage-Komponenten
- `src/components/artifacts/*`: Artifact-Komponenten
- `src/features/*`: seitennahe Feature-Module
- `src/lib/api/*`: API-Client + Fallback-Daten
- `src/types/*`: Typdefinitionen
- `tests/unit/*`: Vitest Unit
- `tests/integration/*`: Vitest Integration
- `tests/e2e/*`: Playwright E2E

## Runtime-Konfiguration
- `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8000/api/v1`)
- `NEXT_PUBLIC_API_KEY` (optional)
- `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK`:
  - `false` (default): kein Mock/Fallback, Backend muss erreichbar sein
  - `true`: expliziter Mock-/Fallback-Modus erlaubt
- `NEXT_PUBLIC_API_FALLBACK_MODE`:
  - Legacy-Kompatibilitaet (`on|off`), nur fallback fuer alte Konfigurationen

## Befehle
- `npm run dev`
- `npm run typecheck`
- `npm run lint`
- `npm run test`
- `npm run test:unit`
- `npm run test:integration`
- `npm run test:e2e:mock`
- `npm run test:e2e:api`
- `npm run test:e2e:mock:smoke`
- `npm run test:e2e:api:smoke`
- `npm run build`

## Verifikation in dieser Umgebung
- erfolgreich ausgefuehrt:
  - `npm.cmd run typecheck`
  - `npm.cmd run lint`
  - `npm.cmd run test` (`tests/unit`: 14 passed, `tests/integration`: 21 passed)
  - `npm.cmd run test:e2e:mock` (12 passed)
  - `npm.cmd run test:e2e:api` (3 passed)
  - `npm.cmd run test:e2e:mock:smoke` (8 passed)
  - `npm.cmd run test:e2e:api:smoke` (2 passed)
