# ProtoRunbook

## Standardmodus
V1/V2 besitzt genau einen Standardmodus.

## Laufreihenfolge
1. Konfiguration laden
2. Quellen laden
3. Features erzeugen
4. Teil-Scores berechnen
5. Cluster-Scores berechnen
6. Stufen / Trend / Confidence ableiten
7. Report und Exporte erzeugen
8. Run-Metadaten speichern
9. Run-Status vorschlagen
10. Vergleich mit letztem Run durchfuehren
11. Vergleich mit Referenz-Run durchfuehren

## Referenz-Run
Der erste saubere aktuelle Standardlauf wird eingefroren und als Referenz-Run abgelegt.
Ein bereits vorhandener Referenz-Run kann kontrolliert ueber `PROTO_FORCE_REFERENCE_REFRESH=1` mit dem aktuellen erfolgreichen Lauf aktualisiert werden.

## Referenzschema (`outputs/reference/current_reference`)
`current_reference` enthaelt:
- `run_metadata.json` (vollstaendige Run-Metadaten inkl. Versionsblock, Zeitfenster, Status)
- `reference_info.json` (Schema- und Dokumentationsstatus der Referenz)
- `exports/*` und `plots/*` aus dem eingefrorenen Referenzlauf

Legacy-Referenzen ohne vollstaendige Metadaten bleiben nur als Fallback lesbar; bei erfolgreichem aktuellem Lauf werden sie auf `current_reference` migriert.

## Kontrollierter Aenderungsfall (V2-08)
Fuer den reproduzierbaren Delta-Nachweis werden Snapshot-Fixtures unter `tests/fixtures/change_case` verwendet.
Der kontrollierte Eingriff betrifft ausschliesslich den GDELT-Wert `Iran/protest` am 2026-01-20; dadurch wird ein klarer Ursache-Wirkung-Nachweis fuer nicht-null Deltas in `run_comparison.json` und `reference_comparison.json` gefuehrt.

## Standardlauf ab V3.1
Der Standardlauf bleibt ein einzelner offizieller Standardmodus, erzeugt aber zusaetzlich parallel:
- den bestehenden Cluster-basierten Ergebnisraum
- einen V3.1-Fusion-Pfad mit Layer-/Gruppenscores und Fusion-Gesamtscore

## V3.1 Beobachtungs- und Fusionsreihenfolge
Erweiterte Reihenfolge ab V3.1:
1. Konfiguration laden
2. Rohquellen laden
3. Rohdaten in kanonische Beobachtungen normalisieren
4. Quellennahe normierte Teilsignale erzeugen
5. bestehende Feature-/Cluster-Kette erzeugen
6. Layer-/Gruppensignale fusionieren
7. parallelen Fusion-Gesamtscore berechnen
8. Historical Rolling Trend fuer bestehende offizielle Cluster-Scores erzeugen
9. Snapshot aus derselben Rolling-Window-Logik ableiten
10. Export-, Plot- und Handout-Artefakte fuer beide Sichten erzeugen

## V3.1 MVP-Quellen
Erster implementierter V3.1-Ausbau:
- `FAO FFPI`
- `FAO FPMA`
- `UN Comtrade`

Dabei gilt:
- `Market/Food` ist der erste sichtbare neue Layer
- `UN Comtrade` dient primaer als struktureller Exposure-/Abhaengigkeitsbeitrag
- weitere Ziel-Layer (`Narrative`, `Shock`, `Displacement`, spaetere Event-Erweiterungen) bleiben Teil der Zielarchitektur, aber nicht zwingend Teil des ersten technisch tiefen MVP-Ausbaus

## Zusaetzliche V3.1-Artefakte
Der V3.1-MVP soll zusaetzlich erzeugen:
- strukturierte Observation-Exporte
- strukturierte Source-Signal-Exporte fuer die Zielperiode
- Layer-/Gruppenscore-Exporte
- Fusion-Gesamtscore-Export
- Handout-/Plot-Bloecke fuer den neuen Fusion-Pfad

Konkrete Pfade im Standardlauf:
- `outputs/runs/current_run/exports/fusion/observations.csv`
- `outputs/runs/current_run/exports/fusion/source_signals.csv`
- `outputs/runs/current_run/exports/fusion/group_scores.csv`
- `outputs/runs/current_run/exports/fusion/fusion_total_scores.json`
- `outputs/runs/current_run/exports/fusion/fusion_status.json`
- `outputs/runs/current_run/plots/fusion/*`

## Standardlauf ab V3.2
V3.2 erweitert den bestehenden V3.1-Fusion-Pfad um einen historischen Multi-Layer-Verlauf.

Ergaenzte Reihenfolge ab V3.2:
1. Konfiguration laden
2. Rohquellen laden (inkl. `GDACS`, `UNHCR`, `narrative_input`)
3. Rohdaten in kanonische Beobachtungen normalisieren
4. Snapshot-Fusion (Gruppen + Gesamt) berechnen
5. historische Fusion auf monatlichen Zielperioden berechnen
6. bestehende Cluster-Historical-/Snapshot-Pfade unveraendert berechnen
7. additive Export-/Plot-/Handout-Artefakte fuer V3.2 erzeugen

## Zusaetzliche V3.2-Artefakte
- `outputs/runs/current_run/exports/fusion/historical_source_signals.csv`
- `outputs/runs/current_run/exports/fusion/historical_group_scores.csv`
- `outputs/runs/current_run/exports/fusion/historical_total_scores.csv`
- `outputs/runs/current_run/exports/fusion/fusion_status.json` (inkl. Historical-Record-Counts; ab V3.2.1 zusaetzlich mit nicht-blockierenden Plausibilitaetswarnungen, ab V3.2.2 mit konsolidierter Low-Coverage-Summary-Warnung)
- `outputs/runs/current_run/plots/fusion/fusion_historical_groups_<country>.png`
- `outputs/runs/current_run/plots/fusion/fusion_historical_total_<country>.png`

Hinweis:
- Der V3.2-Historical-Fusion-Raum ist ein zusaetzlicher Ergebnisraum und ersetzt nicht den `Historical Rolling Trend` der Cluster-Sicht.
- Ab V3.2.1 enthalten historische Total-Exporte explizite Gruppenabdeckungsfelder sowie erweiterte Driver-Hinweise (Top-1/Top-2 Beitraege, staerkste Aenderung).
- Ab V3.2.2 enthalten historische Total-Exporte zusaetzlich `interpretation_status` und `no_material_change`; das Handout markiert frueh eingeschraenkte historische Perioden explizit.

## Standardlauf ab V3.3
V3.3 erweitert den bestehenden V3.2-Fusion-Pfad um einen realen Event-Layer.

Ergaenzte Reihenfolge ab V3.3:
1. Konfiguration laden
2. Rohquellen laden (inkl. `gdelt_event` als Event-Adapterpfad)
3. Rohdaten in kanonische Beobachtungen normalisieren
4. Snapshot-Fusion (inkl. `event`) berechnen
5. historische Fusion (inkl. `event`) auf monatlichen Zielperioden berechnen
6. bestehende Cluster-Historical-/Snapshot-Pfade unveraendert berechnen
7. additive Export-/Plot-/Handout-Artefakte fuer V3.3 erzeugen

Hinweis:
- Event-spezifische Plausibilitaetswarnungen sind nicht blockierend und werden im `fusion_status.json` sowie im Handout ausgegeben.

## Standardlauf ab V4.0
V4.0 erweitert den bestehenden V3.3-Fusion-Pfad um externe Validierung und Kalibrierungsdiagnostik.

Ergaenzte Reihenfolge ab V4.0:
1. Konfiguration laden (inkl. V4-Kalibrierprofil)
2. Fusion-Snapshot und historische Fusion wie bisher berechnen
3. Referenzepisoden laden und episodenbezogene Validierungsmetriken berechnen
4. Snapshot-Ranking gegen erwartete Rangfolge spiegeln
5. Layer-Dominanz-/stale-/Support-Diagnostik erzeugen
6. Validation Summary in Fusion-Status, Handout und Review-Artefakte schreiben

## Zusaetzliche V4.0-Artefakte
- `outputs/runs/current_run/exports/fusion/validation_framework.json`
- `outputs/runs/current_run/exports/fusion/validation_reference_episodes.csv`
- `outputs/runs/current_run/exports/fusion/validation_episode_review.csv`
- `outputs/runs/current_run/exports/fusion/validation_country_ranking.csv`
- `outputs/runs/current_run/exports/fusion/validation_layer_diagnostics.csv`
- `outputs/runs/current_run/exports/fusion/validation_summary.json`

Hinweis:
- Validation-Artefakte sind revieworientiert und ersetzen keinen formalen Ground-Truth-Labelprozess.
- Fruehe historische Perioden mit niedriger Layer-Abdeckung bleiben als eingeschraenkt interpretierbar markiert.

## Standardlauf ab V4.1
V4.1 schaerft den bestehenden V4.0-Pfad operativ auf Frische und Reaktionsfaehigkeit nach.

Ergaenzte Reihenfolge ab V4.1:
1. Konfiguration laden (inkl. Freshness-/Responsiveness-Kalibrierprofil)
2. Snapshot-/Historical-Fusion mit gruppenspezifischen Freshness-Regeln berechnen
3. Operative Freshness-Gruppendiagnostik berechnen
4. Historische Responsiveness-Metriken berechnen
5. Layer-Diagnostik und Validation Summary um Freshness-/Responsiveness-Felder erweitern
6. Operative Hinweise in `fusion_status`, Handout und Review-Bundle ausgeben

## Zusaetzliche V4.1-Artefakte
- `outputs/runs/current_run/exports/fusion/validation_freshness_groups.csv`
- `outputs/runs/current_run/exports/fusion/validation_historical_responsiveness.csv`
- `outputs/runs/current_run/exports/fusion/validation_summary.json` (erweitert um Freshness-/Responsiveness-Kennzahlen)
- `outputs/runs/current_run/handout.md` (V4.1-Abschnitt zur operativen Frische/Responsiveness)
- `review_meta/acceptance_snapshot.json` und `review_meta/acceptance_snapshot.md` (erweitert um Freshness-/Responsiveness-Previews)

Hinweis:
- V4.1 bleibt additiv auf dem V4.0-Validierungsrahmen; keine neue Grossarchitektur und kein neuer Quellenblock.
- Stale Event-Lagen werden operativ klar markiert und in Score/Confidence/Warnings nachvollziehbar behandelt.

## Standardlauf ab V4.2
V4.2 erweitert den bestehenden V4.1-Pfad um eine explizite Governance-/Political-Stability-Dimension.

Ergaenzte Reihenfolge ab V4.2:
1. Konfiguration laden (inkl. Governance-Source- und Group-Weight-Profil)
2. Governance-Input laden und in kanonische Observationen normalisieren
3. Snapshot-/Historical-Fusion inkl. `governance` berechnen
4. Validation-/Layer-Diagnostik um governance-spezifische Felder und Flags erweitern
5. Governance-Reviewanker in Referenzepisoden und Validation Summary ausgeben
6. Governance-Sicht in Handout, Acceptance-Snapshot und Review-Bundle transportieren

## Zusaetzliche V4.2-Artefakte
- `outputs/runs/current_run/exports/fusion/observations.csv` (enthaelt Layer `Governance`)
- `outputs/runs/current_run/exports/fusion/group_scores.csv` (enthaelt Gruppe `governance`)
- `outputs/runs/current_run/exports/fusion/historical_group_scores.csv` (enthaelt historische `governance`-Verlaeufe)
- `outputs/runs/current_run/exports/fusion/validation_reference_episodes.csv` (um Governance-Reviewepisoden erweitert)
- `outputs/runs/current_run/exports/fusion/validation_layer_diagnostics.csv` (inkl. Governance-Instability/Freshness-Felder)
- `outputs/runs/current_run/exports/fusion/validation_summary.json` (inkl. Governance-bezogener Kennzahlen)
- `outputs/runs/current_run/exports/fusion/fusion_status.json` (inkl. governancebezogener Plausibility-Warnings)
- `outputs/runs/current_run/handout.md` (V4.2-Validation/Governance-Abschnitt)
- `review_meta/acceptance_snapshot.json` und `review_meta/acceptance_snapshot.md` (Governance-Previews enthalten)

Hinweis:
- V4.2 bleibt additiv und ersetzt weder den bestehenden Cluster-Raum noch den bisherigen V3.x/V4.0/V4.1-Fusionspfad.

## Standardlauf ab V4.3
V4.3 erweitert den bestehenden V4.2-Pfad um einen verbindlichen 10-Laender-Vergleichsraum und profilgetriebene 356-Tage-Vergleichsartefakte.

Ergaenzte Reihenfolge ab V4.3:
1. Konfiguration laden (verbindliche 10-Laender-Liste)
2. Snapshot-/Historical-Fusion wie bisher berechnen
3. V4.0-V4.2 Validation/Freshness/Governance wie bisher berechnen
4. 356-Tage-Laenderprofilmetriken und Peak-/Gruppen-/Ranking-Diagnostik ableiten
5. V4.3-Hauptvergleichstabelle + vertiefende Diagnostiktabellen exportieren
6. Pro-Land-Jahresprofilplots und laenderuebergreifende Vergleichsplots erzeugen
7. Handout/Acceptance/Review-Bundle um die V4.3-Vergleichssicht erweitern

## Zusaetzliche V4.3-Artefakte
- `outputs/runs/current_run/exports/fusion/validation_country_profiles.csv`
- `outputs/runs/current_run/exports/fusion/validation_peak_phases.csv`
- `outputs/runs/current_run/exports/fusion/validation_group_profiles.csv`
- `outputs/runs/current_run/exports/fusion/validation_ranking_trajectory.csv`
- `outputs/runs/current_run/plots/fusion/v43_country_profile_<country>.png`
- `outputs/runs/current_run/plots/fusion/v43_multicountry_fusion_total.png`
- `outputs/runs/current_run/plots/fusion/v43_multicountry_ranking_trajectory.png`
- `outputs/runs/current_run/handout.md` (globaler V4.3-Vergleichsteil + gleich tiefe Laenderkapitel)
- `review_meta/acceptance_snapshot.json` und `review_meta/acceptance_snapshot.md` (V4.3-Vergleichspreview enthalten)

Hinweis:
- V4.3 bleibt additiv und ersetzt keine bestehenden V2.x-/V3.x-/V4.0-V4.2-Pfade.

## Standardlauf ab V4.3.1
V4.3.1 haertet den bestehenden V4.3-Pfad um Peak-Attribution und Event-Alignment.

Ergaenzte Reihenfolge ab V4.3.1:
1. Konfiguration laden (inkl. V4.3.1 Peak-/Attributions-Kalibrierprofil)
2. Snapshot-/Historical-Fusion wie bisher berechnen
3. V4.0-V4.3 Validation/Freshness/Governance/Comparison wie bisher berechnen
4. Gehaertete Peak-Kandidaten je Land im 356-Tage-Raum extrahieren
5. Peak-Attribution inkl. global-vs-country-Anteilen und Peak-Confidence ableiten
6. Event-Support gegen Marker-Registry ausweisen
7. Trajectory-Profile und globale Peak-Synchronisationsdiagnostik exportieren
8. Handout/Acceptance/Review-Bundle um V4.3.1-Attributionssicht erweitern

## Zusaetzliche V4.3.1-Artefakte
- `outputs/runs/current_run/exports/fusion/event_marker_registry.csv`
- `outputs/runs/current_run/exports/fusion/peak_attribution.csv`
- `outputs/runs/current_run/exports/fusion/peak_event_support.csv`
- `outputs/runs/current_run/exports/fusion/trajectory_profiles.csv`
- `outputs/runs/current_run/exports/fusion/global_peak_synchronization.csv`
- `outputs/runs/current_run/plots/fusion/v431_peak_attribution_<country>.png`
- `outputs/runs/current_run/plots/fusion/v431_global_peak_synchronization.png`
- `outputs/runs/current_run/handout.md` (V4.3.1 Peak-Attribution-&-Event-Alignment-Block)
- `review_meta/acceptance_snapshot.json` und `review_meta/acceptance_snapshot.md` (V4.3.1-Artefakte als Preview)

Hinweis:
- V4.3.1 bleibt ein Haertungsblock ohne neue Laender oder neue Grosslayer.
- Event-Marker sind ein analystischer Reviewpfad und ersetzen keine formale Ground-Truth-Pipeline.

## Standardlauf ab V4.3.2
V4.3.2 erweitert den bestehenden V4.3.1-Pfad um einen strukturierten analystischen Event-Registry-Alignment-Block.

Ergaenzte Reihenfolge ab V4.3.2:
1. Konfiguration laden (inkl. Event-Alignment-Schwellen und Registry-Pfad)
2. Snapshot-/Historical-Fusion und bestehende V4.0-V4.3.1-Validierungslogik wie bisher berechnen
3. Event-Registry laden und schema-validieren
4. Peak-Event-Matching je Land/Peak mit gestuften Match-Klassen berechnen
5. Event-Coverage-Summary und Country-Alignment-Maturity ableiten
6. Event-Alignment-Warnings dosiert in `fusion_status` spiegeln
7. Event-Alignment-Artefakte exportieren und Event-Alignment-Reviewdatei erzeugen
8. Handout/Plots/Acceptance-Snapshot/Review-Bundle um V4.3.2-Sicht erweitern

## Zusaetzliche V4.3.2-Artefakte
- `outputs/runs/current_run/exports/fusion/event_registry.csv`
- `outputs/runs/current_run/exports/fusion/peak_event_matches.csv`
- `outputs/runs/current_run/exports/fusion/event_coverage_summary.csv`
- `outputs/runs/current_run/exports/fusion/country_event_alignment.csv`
- `outputs/runs/current_run/exports/fusion/event_alignment_summary.json`
- `outputs/runs/current_run/exports/fusion/event_alignment_review.md`
- `outputs/runs/current_run/plots/fusion/v432_event_alignment_<country>.png`
- `outputs/runs/current_run/handout.md` (V4.3.2 Analyst Event Registry & Real-World Alignment)
- `review_meta/acceptance_snapshot.json` und `review_meta/acceptance_snapshot.md` (V4.3.2-Artefakte als Preview)

## Analystenworkflow V4.3.2
1. Registry pflegen:
- `data/validation/event_registry.csv` pro Land um relevante Ereignisse/Phasen erweitern oder korrigieren.
- Pflichtfelder fuellen (`event_id`, `country`, Zeitfenster, `source_category`, `source_reference`, `confidence`, `relevance_groups`, erwartetes Peak-Fenster).
2. Lauf ausfuehren:
- `python -m proto.pipeline.run_proto`
3. Match-Ergebnisse pruefen:
- `peak_event_matches.csv` nach `match_class`, `match_confidence`, `linked_event_ids` und `manual_review_required` sichten.
- `event_alignment_review.md` fuer priorisierte Reviewqueue nutzen.
4. Coverage/Maturity bewerten:
- `event_coverage_summary.csv` und `country_event_alignment.csv` auf Laender mit schwacher Event-Erdung pruefen.
5. Unsicherheiten dokumentieren:
- Offene Unsicherheiten in Registry-`notes` und in Open Issues nachfuehren.
6. Bundle fuer Review einfrieren:
- `python tools/create_review_bundle.py`

Hinweis:
- V4.3.2 bleibt additiv und macht den Produktlauf nicht von Live-Web-Recherche abhaengig.
- Event-Registry ist ein analystischer Evidenzpfad, kein automatischer Ground-Truth-Beweis.
