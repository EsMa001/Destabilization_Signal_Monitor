# ProtoScope

## Zielstatement
Der Prototyp identifiziert kurzfristige Auffälligkeiten in Medien- und Kontextdaten und macht damit mögliche Hinweise auf politische oder gesellschaftliche Destabilisierung sichtbar.

## Länder
- Iran
- Israel
- Deutschland

## Zeitfenster
- 7 Tage
- 30 Tage
- 12 Monate

## Cluster
1. Gesellschaftlich-politische Spannung
2. Gewaltsame Eskalation
   - interne Eskalation
   - externe / kriegerische Eskalation
3. Strukturelle / systemische Verwundbarkeit

## Version-1-Quellen
- GDELT
- UCDP
- Bridge-Datei
- Kontexttabelle

## Nicht-Ziele
- operatives Vollsystem
- vollständige Echtzeit-Erfassung aller Ereignisse
- globale Vollabdeckung
- viele Betriebsprofile
- Black-box Fusion

## V3-Zielarchitektur
Ab V3 wird der Prototyp zu einem Multi-Source-Monitor mit zusaetzlicher Layer-/Gruppensicht erweitert:
- `Event`
- `Narrative`
- `Governance`
- `Market/Food`
- `Shock`
- `Displacement`
- `Structural`

## V3.1 erster MVP-Ausbau
Der erste grosse V3.1-Ausbau fokussiert auf:
- kanonisches Observation-Schema
- Adapter-Contract
- parallelen Fusion-Pfad
- `Market/Food` als ersten sichtbaren neuen Layer
- `Structural`-Beitrag ueber `UN Comtrade`
- erste neue Quellen:
  - `FAO FFPI`
  - `FAO FPMA`
  - `UN Comtrade`

## V3.1 Grundsatz
Die bestehende Cluster-Sicht (`Spannung`, `Eskalation`, `Verwundbarkeit`) bleibt erhalten.
Die neue Layer-/Fusion-Sicht kommt zusaetzlich hinzu.

## V3.2 Ausbau
Der naechste Ausbau erweitert V3.1 um:
- historischen Fusion-Verlauf (monatliche Zielperioden)
- reale Layer-Befuellung fuer:
  - `Shock` (mit `GDACS`)
  - `Displacement` (mit `UNHCR`)
  - `Narrative` (mit strukturiertem Narrative-/Expert-Input)
- zusaetzliche historische Fusion-Exporte, Handout-Bloecke und Plots

V3.2 bleibt additiv:
- Snapshot + Historical Rolling Trend der Cluster-Sicht bleiben erhalten
- V3.1-Fusion-Snapshot bleibt erhalten
- der historische Fusion-Raum kommt als eigener zusaetzlicher Ergebnisraum hinzu

## V3.2.1 Hardening
Der nachgelagerte Hardening-Block V3.2.1 schaerft den bestehenden V3.2-Stand ohne neue Grossarchitektur:
- Narrative-/Displacement-Kalibrierung zur besseren Laenderdifferenzierung
- explizite historische Layer-Abdeckungskennzeichnung
- erweiterte Driver-Explainability (Top-Beitraege + staerkste Aenderung)
- nicht-blockierende Plausibilitaetswarnungen im Fusion-Status/Handout

## V3.3 Event Layer Integration
Der naechste grosse Ausbau operationalisiert den bisher offenen Layer `Event`:
- mindestens eine echte Event-Quelle ist tief integriert
- Event-Signale werden periodisiert und normalisiert in kanonische Observationen ueberfuehrt
- Event wirkt in Snapshot- und Historical-Fusion real mit
- Event erscheint in Exporten, Handout, Plots und Explainability
- bestehende V2.x-/V3.1-/V3.2-Pfade bleiben unveraendert additiv erhalten

## V4.0 External Validation & Calibration
Der naechste grosse Ausbau fokussiert nicht auf neue Grossquellen, sondern auf:
- expliziten Validierungsrahmen mit Referenzepisoden
- reviewbare Validierungsmetriken (Peak/Timing/Ranking/Dominanz/Stabilitaet)
- transparente Kalibrierung von Gewichten, Schwellen und Event-Recency-Logik
- analystenfreundliche Diagnose- und Review-Artefakte im bestehenden Fusion-/Bundle-Pfad

## V4.1 Operational Freshness & Responsiveness
Der naechste grosse Ausbau fokussiert auf operative Aktualitaet und zeitliche Reaktionsfaehigkeit:
- explizites Freshness-/Staleness-Modell fuer dynamische Layer
- nachgeschaerfte Event-Recency-/Decay-Logik
- sichtbare Freshness-Diagnostik im Snapshot-/Fusion-Raum
- historische Responsiveness-Metriken fuer juengere Zeitraeume
- kompakte operative Hinweise in Handout, Validation Summary und Review-Bundle

V4.1 bleibt additiv:
- keine neue Grossarchitektur
- keine beliebige Quellenvermehrung
- bestehende V2.x-/V3.x-/V4.0-Pfade bleiben erhalten

## V4.2 Governance & Political Stability Expansion
Der naechste grosse Ausbau erweitert den Multi-Layer-Monitor um eine explizite Governance-/Political-Stability-Dimension:
- neue eigenstaendige analytische Dimension `Governance`
- klare methodische Abgrenzung zu `structural`, `narrative` und `event`
- sichtbare Integration in Snapshot- und Historical-Fusion
- governance-spezifische Diagnose-/Warning-/Validation-Hinweise in Handout, Status, Acceptance-Snapshot und Review-Bundle
- weiterhin additive Architektur ohne neue Grossplattform

## V4.3 Comparative Expansion: 10 Countries, Full 356-Day Profiles
Der naechste grosse Ausbau erweitert den Vergleichsraum verbindlich auf 10 Laender:
- Germany
- Israel
- Iran
- Ukraine
- Russia
- Japan
- China
- Taiwan
- Poland
- Nigeria

V4.3-Kern:
- vollstaendige 356-Tage-Laenderprofile je Land
- profilgetriebene Vergleichsmetriken (nicht primaer episodengetrieben)
- kompakte Hauptvergleichstabelle + vertiefende Diagnostik
- Pro-Land- und Multi-Land-Vergleichsplots
- Handout mit globalem Vergleichsteil vor gleich tiefen Laenderkapiteln

V4.3 bleibt additiv:
- bestehende V2.x-/V3.x-/V4.0-/V4.1-/V4.2-Funktionalitaet bleibt erhalten
- keine neue Grossarchitektur

## V4.3.1 Peak Attribution & Event Alignment Hardening
Der naechste Haertungsblock nach V4.3 schaerft die Lesbarkeit und Trennschaerfe von Hochpunkten:
- explizite Peak-Attribution je Land/Peak
- Trennung globaler Hintergrundwellen vs. laenderspezifischer Peaks
- Kennzeichnung `event_supported` vs. `weakly_supported` vs. `globally_co_moving` vs. `model_driven`
- gehaertete Peak-Erkennung (Prominenz/Breite/Separation statt nur rohes Maximum)
- Trajectory-Profile fuer kompakte Jahresverlaufseinordnung
- neue kompakte Review-Artefakte (Peak-Attribution, Event-Support, Synchronisation)

V4.3.1 bleibt additiv:
- keine neuen Laender
- keine neuen grossen Layer
- keine neue Grossarchitektur

## V4.3.2 Analyst Event Registry & Real-World Alignment
Der naechste grosse Ausbau nach V4.3.1 ist ein expliziter Alignment-/Review-Block:
- strukturierter analystischer Event-Registry-Pfad fuer den bestehenden 10-Laender-Raum
- nachvollziehbare Peak-zu-Ereignis-Verknuepfung mit gestuften Match-Klassen statt binaerem Ja/Nein
- explizite Evidenz-/Confidence-Felder zwischen Modellverlauf und realem Kontext
- Event-Coverage-/Alignment-Diagnostik fuer starke vs. schwache Realwelt-Abdeckung
- handout-/bundle-faehige Review-Artefakte fuer manuelle und halbmanuelle Abnahme

V4.3.2 bleibt additiv:
- keine neuen Laender
- keine neue Grossarchitektur
- keine verpflichtende Live-Web-Abhaengigkeit in der Kernpipeline
