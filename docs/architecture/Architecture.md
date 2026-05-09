# Architecture

## Ziel
Modulare, klare und fusion-ready Architektur fuer V1/V2/V3.

## Ebenen
1. source adapters
2. canonical observations
3. feature builders
4. subscores / cluster scores
5. layer signals / fusion scores
6. thresholds / trend / confidence
7. reporting / plots / exports
8. run management
9. historical rolling trend

## Regeln
- keine direkte Kopplung von Reporting an Rohdaten
- keine Black-box Fusion in V1/V2/V3
- kleine klar benannte Module
- Testbarkeit pro Ebene
- Snapshot-Artefakte und Historical-Trend-Artefakte sind strikt getrennt
- Historical Rolling Trend wird aus taeglichen Basiswerten ueber klar parametrierbare Rolling-Window-Regeln abgeleitet
- Current Snapshot und letzter Historical-Trend-Punkt muessen auf derselben Verdichtungslogik basieren
- historische Pflichtartefakte beschraenken sich auf offizielle Subscores und Cluster-Scores
- ab V3.1 muessen neue Quellen zunaechst in ein kanonisches Observation-Schema normalisiert werden, bevor Layer-Signale oder Fusion berechnet werden
- ab V3.1 existiert parallel zur bestehenden Cluster-Sicht eine zusaetzliche Layer-/Gruppensicht (`Event`, `Narrative`, `Market/Food`, `Shock`, `Displacement`, `Structural`)
- der erste V3.1-MVP fuehrt den neuen Fusion-Pfad parallel zum bestehenden Score; der bestehende Cluster-Raum bleibt erhalten
- der erste operative V3.1-Ausbau fokussiert auf `Market/Food` und `Structural` mit `FAO FFPI`, `FAO FPMA` und `UN Comtrade`
- ab V3.2 wird der Fusion-Pfad historisierbar (monatliche Zielperioden als eigener zusaetzlicher Ergebnisraum)
- ab V3.2 werden `Shock`, `Displacement` und ein erster operationaler `Narrative`-Layer real befuellt (`GDACS`, `UNHCR`, strukturierter Narrative-Input)
- historische Fusion-Artefakte bleiben strikt getrennt von der bestehenden Cluster-Historical-Sicht
- Handout-Plot-Referenzen muessen globale und landbezogene Fusion-Plots konsistent auf vorhandene Dateien mappen
- ab V3.3 wird der bisher offene `Event`-Layer real befuellt (erste echte Event-Quelle) und wirkt additiv in Snapshot-/Historical-Fusion, Explainability und Plausibility-Warnings
- ab V4.0 bleibt die Architektur additiv: ein expliziter Validation-/Calibration-Layer wird als Artefakt- und Diagnostikschicht ueber den bestehenden Fusion-Pfad gelegt (ohne neue Grossarchitektur)
- ab V4.1 wird derselbe Validation-/Diagnostics-Layer operativ erweitert um Freshness-/Staleness-Modell, Responsiveness-Metriken und kompakte Aktualitaetswarnungen (weiterhin ohne neue Grossarchitektur)
- ab V4.2 wird der Fusion-Pfad additiv um einen eigenstaendigen Governance-Layer erweitert; Governance ist in Snapshot/Historical, Validation, Warnings und Review-Bundle explizit sichtbar, ohne den bestehenden Architekturrahmen zu brechen
- ab V4.3 bleibt die Architektur additiv und erweitert den bestehenden Validation-/Reporting-Raum um verbindliche 10-Laender-Comparative-Artefakte (356-Tage-Profile, Vergleichstabellen und Vergleichsplots), ohne neue Grossarchitektur
- ab V4.3.1 bleibt Peak-Attribution/Event-Alignment ein expliziter Diagnose- und Review-Layer ueber dem bestehenden Scorepfad (keine Ersetzung der Kernfusion)
- ab V4.3.2 wird ein analystischer Event-Registry-Alignment-Pfad additiv eingefuehrt: registry-basierte Realweltverknuepfung, gestufte Match-Klassen, Coverage-/Maturity-Diagnostik und reviewbare Artefakte ohne verpflichtende Live-Web-Abhaengigkeit
- Frontend wird als separates Web-Frontend gefuehrt und kommuniziert ausschliesslich ueber versionierte API-Vertraege; keine direkte Kopplung an Python-Module oder interne Output-Pfade.
- UI-/UX-Designquellen (z. B. Stitch-Exporte) werden als Referenz genutzt; produktiver Frontend-Code entsteht als eigenstaendige Komponenten-/Seitenarchitektur mit API-Client-Schicht.
