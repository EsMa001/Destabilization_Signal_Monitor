# ProtoSyR

## PSyR-001 Laenderumfang
Das System muss die Laender Iran, Israel und Deutschland unterstuetzen.

## PSyR-002 Zeitfenster
Das System muss 7d, 30d und 12m als Analysefenster verwenden.

## PSyR-003 Cluster
Das System muss die Cluster Spannung, Eskalation und Verwundbarkeit erzeugen.

## PSyR-004 Eskalationsunterteilung
Das System muss interne und externe / kriegerische Eskalation getrennt darstellen.

## PSyR-005 Quellenkern
Das System muss GDELT, UCDP, Bridge-Datei und Kontexttabelle verarbeiten koennen.

## PSyR-006 Reporting
Das System muss einen Report / ein Handout mit Plots erzeugen.

## PSyR-007 Exporte
Das System muss strukturierte Exporte erzeugen.

## PSyR-008 Run-Metadaten
Das System muss Run-Metadaten speichern.

## PSyR-009 Run-Vergleich
Das System muss Runs mit dem letzten gespeicherten Run vergleichen koennen.

## PSyR-010 Referenz-Run
Das System muss einen Referenz-Run speichern und wiederverwenden koennen.

## PSyR-018 Kanonische Beobachtungen
Das System muss neue Quellen vor weiterer Verarbeitung in ein gemeinsames kanonisches Observation-Schema ueberfuehren koennen.

## PSyR-019 Layer-/Gruppensicht
Das System muss parallel zur bestehenden Cluster-Sicht die Layer/Gruppen `Event`, `Narrative`, `Governance`, `Market/Food`, `Shock`, `Displacement` und `Structural` fuehren koennen.
Im ersten V3.1-MVP muessen mindestens `Market/Food` und `Structural` mit echten Gruppensignalen befuellt werden; die anderen Gruppen duerfen als explizit nicht verfuegbar markierte Struktur vorliegen.
Ab V3.3 ist `Event` ebenfalls real zu befuellen (nicht mehr nur als Lueckenmarker).

## PSyR-020 Paralleler Fusion-Pfad
Das System muss zusaetzlich zum bestehenden Score-Pfad Gruppenscores und einen Fusion-Gesamtscore erzeugen koennen.

## PSyR-021 V3.1 MVP-Quellen
Das System muss im ersten V3.1-MVP mindestens `FAO FFPI`, `FAO FPMA` und `UN Comtrade` verarbeiten koennen.

## PSyR-022 Unterschiedliche native Perioden
Das System muss Quellen mit unterschiedlichen nativen zeitlichen Aufloesungen verarbeiten koennen, ohne sie vorzeitig auf ein einziges Rohdatenraster zu zwingen.

## PSyR-023 Historischer Fusion-Pfad (V3.2)
Das System muss fuer den Fusion-Ergebnisraum zusaetzlich zu Snapshot-Werten einen historischen Verlauf bereitstellen.

## PSyR-024 Shock-Layer mit GDACS (V3.2)
Das System muss `GDACS` als `Shock`-Layer-Quelle in den kanonischen Observation- und Fusion-Pfad integrieren.

## PSyR-025 Displacement-Layer mit UNHCR (V3.2)
Das System muss `UNHCR` als `Displacement`-Layer-Quelle in den kanonischen Observation- und Fusion-Pfad integrieren.

## PSyR-026 Operationaler Narrative-Layer (V3.2)
Das System muss einen klar getrennten, strukturierten Narrative-/Expert-Input-Adapterpfad bereitstellen.

## PSyR-027 Monatliche Zielperioden fuer historische Fusion (V3.2)
Das System muss den historischen Fusion-Pfad ueber explizite monatliche Zielperioden berechnen.

## PSyR-028 V3.2 Fusion-Reporting (V3.2)
Das System muss historische Fusion-Artefakte (Export/Handout/Plots) als zusaetzlichen Ergebnisraum ausgeben.
Im V3.2.1-Hardening sollen in den historischen Artefakten zusaetzlich Gruppenabdeckung, erweiterte Driver-Hinweise und nicht-blockierende Plausibilitaetswarnungen sichtbar werden koennen.

## PSyR-029 Event-Layer-Integration (V3.3)
Das System muss den Layer `Event` mit mindestens einer echten Event-Quelle im kanonischen Observation- und Fusion-Pfad betreiben koennen.
Der Event-Layer muss im Snapshot- und im historischen Fusion-Raum erscheinen und darf im Regelbetrieb nicht mehr pauschal `not_available` bleiben.

## PSyR-030 Validierungsrahmen mit Referenzepisoden (V4.0)
Das System muss einen expliziten Validierungsrahmen mit versionierbaren Referenzepisoden fuer mindestens Iran, Israel und Germany bereitstellen und im Lauf auswerten koennen.

## PSyR-031 Validierungsstand in Review-Artefakten (V4.0)
Das System muss den Validierungsstand (Summary, Episodenvergleich, Ranking, Diagnostik) in den regulaeren Fusion-Artefakten und im Review-Bundle/Acceptance-Snapshot sichtbar transportieren koennen.

## PSyR-032 Freshness-/Staleness-Steuerung fuer dynamische Layer (V4.1)
Das System muss fuer zeitdynamische Layer (insbesondere `event`) ein explizites Freshness-/Staleness-Modell mit konfigurierbaren Regeln betreiben, das Score-, Confidence- und Diagnosepfade konsistent beeinflusst.

## PSyR-033 Operative Responsiveness-Sicht im Reviewpfad (V4.1)
Das System muss neben der V4.0-Validierung eine operative Responsiveness-Sicht bereitstellen (Freshness-Coverage, stale burden, historische Reaktionsmetriken) und diese in Exporten, Handout und Acceptance-Snapshot transportieren.

## PSyR-034 Governance-Layer im kanonischen Fusion-Pfad (V4.2)
Das System muss einen eigenstaendigen Governance-Layer (`governance`) mit klar benannter Quelle im kanonischen Observation-/Fusion-Pfad fuehren koennen und diesen in Snapshot- sowie Historical-Fusion wirksam berechnen.

## PSyR-035 Governance-Sicht in Validation und Review-Artefakten (V4.2)
Das System muss governance-spezifische Diagnose-, Warning- und Validation-Hinweise (inkl. Freshness-/Contribution-Sicht) in `validation_summary`, Handout, Acceptance-Snapshot und Review-Bundle transportieren.

## PSyR-036 Verbindlicher 10-Laender-Vergleichsraum (V4.3)
Das System muss in V4.3 den Vergleichsraum verbindlich auf folgende 10 Laender setzen:
`Germany`, `Israel`, `Iran`, `Ukraine`, `Russia`, `Japan`, `China`, `Taiwan`, `Poland`, `Nigeria`.
Die Selektion darf nicht implizit/zufaellig sein und muss in Config, Pipeline und Artefakten konsistent sein.

## PSyR-037 Vollstaendige 356-Tage-Laenderprofile (V4.3)
Das System muss fuer alle 10 Laender den vollstaendigen 356-Tage-Verlauf im Snapshot-/Historical-Fusion-Raum verarbeiten und exportieren; Datenluecken sind explizit zu markieren, ohne Laender aus dem Vergleich auszuschliessen.

## PSyR-038 Vergleichsdiagnostik und gleich tiefe Berichtsstruktur (V4.3)
Das System muss globale Vergleichsdiagnostik und pro-Land-Jahresprofile bereitstellen; das Handout muss zuerst einen globalen Vergleichsteil und danach gleich tiefe Laenderkapitel enthalten.

## PSyR-039 Peak-Attribution im 10-Laender-Verlauf (V4.3.1)
Das System muss fuer die 356-Tage-Verlaeufe je Land eine explizite Peak-Attribution bereitstellen, die dominante Gruppen, globale versus laenderspezifische Anteile, Freshness-Kontext und Support-Breite nachvollziehbar ausweist.

## PSyR-040 Event-Alignment- und Synchronisationssicht im Reviewpfad (V4.3.1)
Das System muss im Validation-/Reviewpfad klar zwischen `event_supported_peak`, `weakly_supported_peak`, `globally_co_moving_peak` und `model_driven_peak` unterscheiden koennen und diese Unterscheidung in Exporten, Handout, Acceptance Snapshot und Review Bundle transportieren.

## PSyR-041 Strukturierter Event-Registry-Reviewpfad (V4.3.2)
Das System muss einen stabilen, versionierbaren Event-Registry-Pfad bereitstellen, in dem analystische Ereignisphasen pro Land gepflegt und ohne Live-Web-Abhaengigkeit im Lauf verwendet werden koennen.

## PSyR-042 Gestuftes Peak-Event-Matching (V4.3.2)
Das System muss erkannte Peaks gegen den Event-Registry-Raum ueber eine gestufte Matching-Logik spiegeln (kein binaeres Ja/Nein), inklusive Match-Klassen, Match-Confidence und Evidenzfeldern.

## PSyR-043 Event-Alignment-Diagnostik und Review-Artefakte (V4.3.2)
Das System muss Event-Alignment-Coverage, country-level Alignment-Maturity und offene Unsicherheiten als kompakte Export-, Handout- und Bundle-Artefakte bereitstellen.
