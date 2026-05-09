# Frontend Design Handoff

## 1. Ziel des Frontends
Dieses Frontend ist ein separates Web-Frontend für ein Python-basiertes Analyse- und Monitoringsystem im Bereich internationale Sicherheit / Destabilisierungssignale.

Ziel des Frontends:
- Analyse-Runs definieren und starten
- asynchrone Runs überwachen
- Länderprofile analysieren
- Tagesberichte und Langzeitdatenverläufe untersuchen
- Artefakte, Reports und Bundles abrufen
- Datenabdeckung und Frische sichtbar machen

Das Frontend enthält **keine Fachlogik**.  
Es dient ausschließlich als:
- Präsentationsschicht
- Navigationsschicht
- Interaktionsschicht
- API-Client gegenüber dem Python-Backend

---

## 2. Designquelle

### Stitch-Quelle
- Stitch-Projektname: `TODO`
- Stitch-Link: `TODO`
- Version / Stand: `TODO`
- Datum: `TODO`

### Exporte
- Figma-Link: `TODO`
- HTML/CSS-Export-Pfad: `frontend/design/stitch_exports/html_css_export/`
- Screenshot-Ordner: `frontend/design/stitch_exports/screenshots/`
- Stitch-Designsystem: `frontend/design/stitch_exports/DESIGN.md`
- Stitch-Inventar: `frontend/design/stitch_exports/stitch_inventory.md`

---

## 3. UX-/Designziel

Gewünschte Wirkung:
- cool
- clean
- dark
- premium
- serious
- analyst-focused
- fullscreen desktop-first
- modern intelligence / strategy / operations dashboard
- hohe Glaubwürdigkeit für professionelle Nutzer

Nicht gewünscht:
- verspielte Consumer-App-Optik
- generisches Business-Dashboard-Template
- überdekorierte UI
- Desktop-only GUI
- enge Kopplung an Python-Interna

---

## 4. Globale Navigationsstruktur

Primäre Navigation:
- Overview
- Runs
- Countries
- Compare
- Artifacts
- Coverage
- Settings

Globale Layoutidee:
- linke Sidebar-Navigation
- obere Utility Bar
- zentraler Hauptarbeitsbereich
- optional rechter Insight-Bereich auf passenden Seiten

---

## 5. Seiteninventar

## 5.1 Overview / Home
### Zweck
Globale Übersicht über Länder, Datenverfügbarkeit, herausstechende Werte und operative Lage.

### Wichtige Elemente
- große Weltkarte als Hauptanker
- Länder mit Datenverfügbarkeit grün umrandet
- Hover über Land zeigt kompakte Kennzahlen
- rechter Insight-Rail für auffällige Werte
- obere Utility Bar
- Filter nach Region / Verfügbarkeit / Layer / Run-Kontext

### Erwartete Interaktionen
- Hover Land → Tooltip
- Klick Land → Country Detail
- Klick auffälliger Wert → passende Detailseite
- Suchfeld für Länder

### Erwartete API-Kopplung
- Länderliste / Datenverfügbarkeit
- globale Kennzahlen / Rankings
- aktive Runs
- ggf. letzte Aktualisierung

---

## 5.2 Run Builder
### Zweck
Neue Analyse-Runs definieren und starten.

### Wichtige Elemente
- Länderwahl
- Analysehorizont
- Gruppen-/Layer-Wahl
- optionale Advanced Settings
- Live-Zusammenfassung des geplanten Runs
- klarer Start-Run-Button

### Erwartete Interaktionen
- Formular validieren
- Submit → Run anlegen
- nach Start Navigation zu Run Monitor oder Run Detail

### Erwartete API-Kopplung
- Config template
- Country options
- Layer/group options
- POST Run

---

## 5.3 Run Monitor
### Zweck
Asynchrone Runs überwachen.

### Wichtige Elemente
- Liste / Tabelle der Runs
- Status
- Progress
- Zeitstempel
- Laufzeit
- Länderanzahl
- Filter / Sortierung

### Erwartete Interaktionen
- Klick Run → Run Detail
- periodischer Statusabruf

### Erwartete API-Kopplung
- Run list
- Run status

---

## 5.4 Run Detail
### Zweck
Details eines konkreten Runs anzeigen.

### Wichtige Elemente
- Status und Progress
- Konfigurationszusammenfassung
- Summary
- Warnungen
- Artefakte
- Bundle-Download
- Ausführungsnachrichten / Logs

### Erwartete Interaktionen
- Artefakte öffnen / herunterladen
- in Länder-Details springen

### Erwartete API-Kopplung
- Run detail
- Run status
- Run summary
- Run artifacts
- Run bundle

---

## 5.5 Country Detail
### Zweck
Analytische Hauptseite für ein Land.

### Wichtige Elemente
- Länderheader
- aktueller Status
- letzte Aktualisierung
- Confidence / Freshness
- KPI-Bereich
- Umschalter:
  - Daily Briefing
  - Long-Term Trends
- Zeitreihen
- Layer-/Gruppenbeiträge
- Artefakte / Coverage / Notes

### Erwartete Interaktionen
- Umschalten zwischen Daily Briefing und Long-Term Trends
- Artefakte öffnen
- ggf. zu Compare hinzufügen

### Erwartete API-Kopplung
- Country summary
- Country trend / plot metadata
- Country artifacts
- Coverage/Freshness-Daten

---

## 5.6 Compare
### Zweck
Mehrere Länder direkt vergleichen.

### Wichtige Elemente
- Mehrfachauswahl
- KPI-Vergleich
- Trendvergleich
- Peak-Vergleich
- Gruppenvergleich

### Erwartete API-Kopplung
- mehrere Country-/Run-Summary-Endpunkte
- Vergleichsdaten / Serien

---

## 5.7 Artifacts
### Zweck
Bundles, Reports, Charts und Exporte durchsuchen und herunterladen.

### Wichtige Elemente
- gruppiert nach Runs
- Typ, Erstellungszeit, Status
- Download
- ggf. Preview

### Erwartete API-Kopplung
- Artifact list
- Artifact download / bundle

---

## 5.8 Coverage / Data Status
### Zweck
Datenverfügbarkeit und Frische transparent machen.

### Wichtige Elemente
- Länder
- Layer-/Gruppen-Abdeckung
- letzte Aktualisierung
- fehlende / stale Daten
- Warnhinweise

### Erwartete API-Kopplung
- country coverage
- layer availability
- freshness / data status

---

## 6. Designsystem-Regeln

### Stil
- dark
- clean
- premium
- serious
- fullscreen desktop-first
- hohe Informationsdichte, aber klar strukturiert

### Farb- und Statuslogik
- dunkle Grundflächen
- grün = verfügbar / aktiv / gesund / Daten vorhanden
- amber = Warnung
- rot = kritisch
- zurückhaltende Akzentnutzung

### Layout
- ruhiges Grid
- klare Hierarchie
- großzügige Hauptfläche
- kein verspieltes UI
- Sidebar + Topbar + Main Workspace

### Komponentenstil
- saubere Panels / Cards
- lesbare Tabellen
- feine Outlines
- technisch-moderne Anmutung
- keine überladenen Widgets

### Map-Stil
- elegante Weltkarte
- Länderumrisse
- Länder mit Daten grün umrandet
- Hover-Zustände klar lesbar
- keine cartoonhafte Karte

---

## 7. API-Kopplung

### Grundregel
Frontend spricht ausschließlich mit dem API-Backend.

Nicht erlaubt:
- direkte Python-Imports
- direkte Zugriffe auf interne Backend-Dateien
- enge Kopplung an Output-Ordner des Python-Kerns

### Relevante API-Endpunkte
- GET /api/v1/health
- GET /api/v1/info
- GET /api/v1/config/template
- GET /api/v1/options/countries
- GET /api/v1/options/layers
- POST /api/v1/runs
- GET /api/v1/runs
- GET /api/v1/runs/{run_id}
- GET /api/v1/runs/{run_id}/status
- GET /api/v1/runs/{run_id}/summary
- GET /api/v1/runs/{run_id}/artifacts
- GET /api/v1/runs/{run_id}/bundle

### API-Zuordnung pro Seite
- Overview:
  - primär: `GET /api/v1/health`, `GET /api/v1/overview`
  - sekundär/derive: `GET /api/v1/options/countries` (nur bei Bedarf)
- Run Builder:
  - `GET /api/v1/options/countries`
  - `GET /api/v1/options/layers`
  - `POST /api/v1/runs`
- Run Monitor:
  - `GET /api/v1/runs`
- Run Detail:
  - `GET /api/v1/runs/{run_id}`
  - `GET /api/v1/runs/{run_id}/status`
  - `GET /api/v1/runs/{run_id}/summary`
  - `GET /api/v1/runs/{run_id}/artifacts`
- Country Detail:
  - bevorzugt: `GET /api/v1/countries/{country}/detail|summary`
  - Fallback/derive: `GET /api/v1/overview` + bekannte Kernendpunkte
- Compare:
  - bevorzugt: `GET /api/v1/compare?countries=...`
  - Fallback/derive: `GET /api/v1/overview`
- Coverage:
  - bevorzugt: `GET /api/v1/coverage` oder `GET /api/v1/data-status`
  - Fallback/derive: `GET /api/v1/overview` + `GET /api/v1/options/*`
- Artifacts:
  - bevorzugt: `GET /api/v1/artifacts`
  - Fallback/derive: `GET /api/v1/runs` + `GET /api/v1/runs/{run_id}/artifacts`

Status Phase 3:
- API-first bleibt umgesetzt, inklusive zentraler Degradation im API-Client.
- UX-Hardening fuer End-to-End-Workflow ist umgesetzt (PageHeader/Breadcrumbs/Deep-Links/konsequentere States).
- Compare/Coverage/Artifacts sind als Arbeitsseiten deutlich staerker steuerbar und scannbar.
- Spezialendpunkte sind weiterhin nicht in jeder Umgebung garantiert; derive-Pfade bleiben aktiv.

---

## 8. Zustände

Für alle wichtigen Seiten müssen sauber gestaltet sein:
- loading state
- empty state
- error state
- partial data state
- stale data state, wo relevant

Wichtig:
- keine leeren weißen Flächen ohne Erklärung
- keine kaputten Screens bei fehlenden API-Daten
- klare Nutzerführung bei nicht verfügbaren Daten

---

## 9. Frontend-Komponenten-Kandidaten

Beispielhafte Komponenten:
- AppShell
- SidebarNav
- TopBar
- WorldMap
- CountryHoverTooltip
- InsightRail
- RunTable
- RunStatusBadge
- RunSummaryCard
- CountryHeader
- KPIGrid
- DailyBriefingPanel
- LongTermTrendPanel
- ArtifactList
- CoverageMatrix
- ComparePanel

---

## 10. Nicht-Ziele

- keine Fachlogik im Frontend
- keine direkte Python-Kopplung
- kein Desktop-only Ansatz
- keine Benutzerverwaltung im MVP
- keine WebSocket-Pflicht im MVP
- keine unnötige State-Management-Komplexität
- keine blinde 1:1-Übernahme von Stitch-HTML als finaler Code

---

## 11. Offene Designentscheidungen

Hier sammeln:
- welche Stitch-Screens final sind
- welche Screens nur Zwischenstand sind
- welche Bereiche noch von Codex konkretisiert werden dürfen
- welche API-Endpunkte noch fehlen
- welche Daten auf Country Detail im MVP wirklich gezeigt werden
- wie tief Compare im MVP gehen soll

Beispiele:
- `TODO: Soll Compare initial nur 2 Länder oder bis zu 4 Länder unterstützen?`
- `TODO: Soll die Weltkarte im MVP bereits voll interaktiv sein oder zunächst API-gebundener Strukturplatzhalter bleiben?`
- `TODO: Welche Country-Detail-Daten sind im MVP garantiert über die API verfügbar?`

Aktueller Stand:
- Compare unterstuetzt bis zu 6 Laender inkl. Deep-Link (`?countries=...`), Trend- und Peak-Vergleich.
- Weltkarte ist als reduzierter Laenderumriss-MVP fuer den relevanten Laenderraum umgesetzt (Hover/Klick/Legende/Filterkontext) und mit Country-Drilldown verbunden.
- Country Detail ist als Analysten-Workspace gehaertet (Status/KPI/Trend/Freshness/Coverage/Artifacts/Notes).
- Coverage und Artifacts sind filterbar und fuer operatives Scannen strukturiert.
- Offene Restfrage bleibt die verbindliche API-Verfuegbarkeit der spezialisierten Endpunkte (siehe OI-042/OI-043).

Stabilization-Update:
- TopBar zeigt expliziten Backend-Konnektivitaetsstatus (`connected`, `unavailable`, `mock mode active`) inkl. Mock-Fallback-Flag.
- Mock-/Fallback-Modus ist explizit env-gesteuert (`NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true|false`).
- Run Builder erzeugt keine stillen Fake-Runs mehr, wenn Backend fehlt und Mock-Modus deaktiviert ist.
- Dynamische App-Router-Seiten (`/runs/[runId]`, `/countries/[countryCode]`) sind auf Promise-`params` gehaertet.

Test-Automation-Update:
- Frontend-Testebenen sind explizit getrennt:
  - Unit (`tests/unit`)
  - Integration (`tests/integration`)
  - Browser E2E (`tests/e2e/mock`, `tests/e2e/api`)
- Mock-vs-API-Testmodus ist ueber getrennte Playwright-Konfigurationen abgesichert:
  - `playwright.mock.config.ts` (Mock-Fallback an)
  - `playwright.api.config.ts` (Mock-Fallback aus)
- Kritische UI-Anker fuer robuste Automatisierung sind gezielt ueber `data-testid` gesetzt (Backend-Status, Run Builder, Map, Run Monitor, Compare, Coverage, Artifacts).
