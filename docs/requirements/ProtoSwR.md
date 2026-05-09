# ProtoSwR

## PSwR-001 Strukturtrennung
Die Software muss Rohdaten, Features, Scores und Darstellung klar trennen.

## PSwR-002 Konfiguration
Die Software muss eine Standardkonfiguration für V1 besitzen.

## PSwR-003 GDELT-Loader
Die Software muss GDELT-Daten laden und in ein internes Modell überführen.

## PSwR-004 UCDP-Loader
Die Software muss UCDP-Daten laden und in ein internes Modell überführen.

## PSwR-005 Bridge-Loader
Die Software muss eine kleine Ereignis-Bridge-Datei laden.

## PSwR-006 Kontext-Loader
Die Software muss eine kuratierte Kontexttabelle laden.

## PSwR-007 Features Spannung
Die Software muss Features für gesellschaftlich-politische Spannung erzeugen.

## PSwR-008 Features Eskalation
Die Software muss Features für interne und externe / kriegerische Eskalation erzeugen.

## PSwR-009 Features Verwundbarkeit
Die Software muss Features für strukturelle / systemische Verwundbarkeit erzeugen.

## PSwR-010 Teil-Scores
Die Software muss 3–5 Teil-Scores je Cluster verarbeiten können.

## PSwR-011 Cluster-Scores
Die Software muss pro Cluster einen numerischen Cluster-Score erzeugen.

## PSwR-012 Stufen
Die Software muss Cluster-Scores in niedrig / erhöht / hoch / sehr hoch verdichten.

## PSwR-013 Trend
Die Software muss Trends als rückläufig / stabil / zunehmend ausgeben.

## PSwR-014 Confidence
Die Software muss Confidence numerisch und als niedrig / mittel / hoch ausgeben.

## PSwR-015 Kurztexte
Die Software muss pro Land und Cluster kurze Textinterpretationen erzeugen.

## PSwR-016 Plots
Die Software muss zentrale Zeitverläufe plotten.

## PSwR-017 Run-Status
Die Software muss einen vorgeschlagenen Run-Status erzeugen.

## PSwR-018 Tests
Für alle zentralen Verarbeitungsstufen müssen automatisierte Tests vorhanden sein.

## PSwR-019 Traceability
Code und Tests müssen Traceability-Verweise auf Anforderungen enthalten.

## PSwR-036 Kanonisches Observation-Schema
Die Software muss neue Quellen zunaechst in ein kanonisches Observation-Schema ueberfuehren koennen.

## PSwR-037 Observation-Pflichtfelder
Die Software muss im kanonischen Observation-Schema mindestens `source_id`, `layer`, `signal_family`, `country`, `period_start`, `period_end`, `raw_value`, `normalized_value`, `unit`, `provenance` und `quality/completeness` fuehren koennen.

## PSwR-038 Unterschiedliche native Perioden
Die Software muss im kanonischen Observation-Schema unterschiedliche native Perioden der Quellen fuehren koennen.

## PSwR-039 Adapter-Contract
Die Software muss fuer neue Quellen einen klaren, pragmatischen Adapter-Contract mit Pflichtfeldern, Validierung, Provenance und definiertem Normalisierungsausgang bereitstellen.

## PSwR-040 Quellspezifische Normalisierung
Die Software muss pro Quelle explizit konfigurierbare einfache Normalisierungsregeln auf ein Teilsignal `s_i` in `[0,1]` anwenden koennen.
Fuer ausgewaehlte Quellen muss zusaetzlich ein transparenter Normalisierungs-Scope (`per_country` oder `global`) konfigurierbar sein.

## PSwR-041 Gruppenfusion
Die Software muss Quellen innerhalb ihrer Gruppe ueber eine einfache transparente gewichtete Mittelung fusionieren koennen.

## PSwR-042 Fusion-Gesamtscore
Die Software muss aus den Gruppensignalen einen parallelen Fusion-Gesamtscore ueber transparente konfigurierbare Gruppengewichte berechnen koennen.
Ein gruppenuebergreifender Bonusmechanismus darf optional vorhanden sein, muss im ersten V3.1-MVP aber standardmaessig deaktiviert bleiben.

## PSwR-043 Zeitliche Zielperioden
Die Software muss fuer die Fusion definierte Zielperioden verarbeiten koennen, ohne die nativen Quellperioden in der Provenance zu verlieren.

## PSwR-044 Observation-Provenance
Die Software muss Provenance fuer neue Quellen mindestens bis auf Observation-/Signal-Ebene fuehren.

## PSwR-045 Fusion-Confidence
Die Software muss im Fusion-Pfad Confidence getrennt vom Score fuehren und sichtbar ausgeben.
Die Confidence-Berechnung soll explizit Coverage-, Aktualitaets-, Vollstaendigkeits- und Konsistenzkomponenten ausweisen und darf moderate Penalties fuer Einzel-Layer-Dominanz bzw. `limited`-Gruppenabdeckung enthalten.

## PSwR-046 Gruppenscores
Die Software muss fuer die Layer/Gruppen numerische Gruppenscores erzeugen koennen.
Nicht tief integrierte Gruppen duerfen im V3.1-MVP als `not_available` markiert werden, sofern `Market/Food` und `Structural` als echte Scores vorliegen.
Ab V4.2 muss `Governance` als eigenstaendige Gruppe numerisch ausweisbar sein.

## PSwR-047 Parallelitaet zum bestehenden Score
Die Software muss den neuen Fusion-Pfad parallel zum bestehenden Cluster-/Score-Pfad betreiben koennen.

## PSwR-048 FAO-FFPI-Loader
Die Software muss `FAO FFPI` laden und in das kanonische Observation-Schema ueberfuehren koennen.

## PSwR-049 FAO-FPMA-Loader
Die Software muss `FAO FPMA` laden und in das kanonische Observation-Schema ueberfuehren koennen.

## PSwR-050 UN-Comtrade-Loader
Die Software muss `UN Comtrade` laden und in das kanonische Observation-Schema ueberfuehren koennen.

## PSwR-051 Fusion-Artefakte
Die Software muss fuer den V3.1-Fusion-Pfad strukturierte Exporte, Handout-Bloecke und Plots erzeugen koennen.

## PSwR-052 Beibehaltung der Cluster-Sicht
Die Software darf die bestehende Cluster-Sicht (`Spannung`, `Eskalation`, `Verwundbarkeit`) im V3.1-MVP nicht durch die neue Layer-/Gruppensicht ersetzen.

## PSwR-053 Konsistente Fusion-Plot-Zuordnung
Die Software muss Fusion-Plotdateien fuer den Handout-Laenderkontext robust den Laendern zuordnen koennen.

## PSwR-054 Erweiterter V3.x-Source-Block
Die Software muss im V3.x-Config-Block zusaetzliche Quellen `GDACS`, `UNHCR` und `narrative_input` inklusive Normalisierung validieren koennen.

## PSwR-055 Narrative-Inputformat
Die Software muss fuer den Narrative-Adapter mindestens `source_id`, `country`, `period_start`, `period_end`, `topic`, `narrative_direction`, `relevance`, `confidence`, `provenance` verarbeiten koennen.

## PSwR-056 Historische Fusion-Zielperioden
Die Software muss fuer den historischen Fusion-Pfad explizite monatliche Zielperioden erzeugen und nachvollziehbar fuehren.

## PSwR-057 Historische Source-Signale
Die Software muss historische Source-Signale pro Zielperiode als strukturierten Export bereitstellen.

## PSwR-058 Gruppenstatus-Semantik
Die Software muss fuer Fusion-Gruppen mindestens `ok`, `limited` und `not_available` unterscheiden koennen.

## PSwR-059 GDACS-Loader
Die Software muss `GDACS` laden, in kanonische Beobachtungen ueberfuehren und dem Layer `Shock` zuordnen koennen.

## PSwR-060 UNHCR-Loader
Die Software muss `UNHCR` laden, in kanonische Beobachtungen ueberfuehren und dem Layer `Displacement` zuordnen koennen.

## PSwR-061 Narrative-Input-Loader
Die Software muss strukturierte Narrative-/Expert-Inputs laden, in kanonische Beobachtungen ueberfuehren und dem Layer `Narrative` zuordnen koennen.

## PSwR-062 Historische Gruppenscores
Die Software muss historische Fusion-Gruppenscores je Land/Periode erzeugen und exportieren.

## PSwR-063 Historischer Fusion-Gesamtscore
Die Software muss historische Fusion-Gesamtscores je Land/Periode erzeugen und exportieren.
Der historische Total-Export muss die Gruppenabdeckung je Periode explizit enthalten (`available_group_count`, `expected_group_count`, `available_group_ratio`).

## PSwR-064 Historische Driver-Hinweise
Die Software muss im historischen Fusion-Pfad dominante Gruppenbeitraege fuer juengste Aenderungen ausweisen koennen.
Mindestens sichtbar sein sollen: staerkster positiver Beitrags-Layer, zweitstaerkster positiver Beitrags-Layer und staerkste Gruppenveraenderung zum Vorzeitpunkt.

## PSwR-065 Historische Fusion-Plots
Die Software muss historische Fusion-Plots (Gruppen + Gesamt) global und landbezogen erzeugen.

## PSwR-066 Historische Fusion-Handout-Sicht
Die Software muss im Handout einen klar getrennten V3.2-Historical-Fusion-Block ausgeben.

## PSwR-067 Additive Parallelitaet zum Bestand
Die Software muss V3.2 additiv integrieren, ohne Snapshot/Historical-Cluster/Review-Candidates oder V3.1-Snapshot-Fusion zu regressieren.

## PSwR-068 Event-Gruppe als explizite Luecke
Die Software darf die Gruppe `event` in V3.2 weiterhin als `not_available` ausgeben, sofern dies explizit markiert bleibt.
Ab V3.3 wird diese Uebergangsregel durch die operative Event-Integration (`PSwR-073`) abgeloest.

## PSwR-069 Fusion-Status mit Historical-Metadaten
Die Software muss den Fusion-Status-Export um historische Record-Zaehlungen erweitern.
Nicht-blockierende Plausibilitaets-Warnings sollen im Fusion-Status sichtbar werden koennen.

## PSwR-070 Bonus-Default im historischen Pfad
Die Software muss den gruppenuebergreifenden Bonusmechanismus auch im historischen Fusion-Pfad standardmaessig deaktiviert halten, solange er in der Konfiguration deaktiviert ist.

## PSwR-071 GDELT-Event-Adapter (V3.3)
Die Software muss mindestens einen echten Event-Adapter bereitstellen, der beobachtbare Event-Rohdaten laedt, validiert und als kanonische Observationen fuer den Layer `Event` ausgibt.

## PSwR-072 Event-Periodisierung und Normalisierung (V3.3)
Die Software muss Event-Rohdaten transparent in periodische Event-Signale ueberfuehren und normalisieren koennen.
Die Ableitung soll mindestens Event-Haeufigkeit, Event-Schwere, Recency und Quellqualitaet beruecksichtigen.

## PSwR-073 Event-Wirksamkeit in Snapshot/Historical-Fusion (V3.3)
Die Software muss den Event-Layer in `group_scores`, `historical_group_scores`, `fusion_total_scores` und `historical_total_scores` wirksam integrieren.
Event muss in Explainability-Feldern (z. B. `top_positive_group_*`, `strongest_change_group`) als moeglicher Treiber sichtbar sein.

## PSwR-074 Event-spezifische Plausibilitaetshinweise (V3.3)
Die Software muss nicht-blockierende Event-spezifische Plausibilitaetschecks/Warnungen bereitstellen (z. B. geringe Event-Abdeckung, stale Event-Signale, geringe Differenzierung).

## PSwR-075 Exportierbarer Validierungsrahmen (V4.0)
Die Software muss einen strukturierten, exportierbaren Validierungsrahmen (`validation_framework`) mit Kriterien, Kalibrierprofil und erwarteter Laenderrangfolge erzeugen.

## PSwR-076 Versionierbarer Referenzepisoden-Pfad (V4.0)
Die Software muss Referenzepisoden als klar versionierbaren Artefaktpfad laden und parallel in den Laufexporten bereitstellen.

## PSwR-077 Validierungsmetriken fuer Episoden und Ranking (V4.0)
Die Software muss pragmatische Validierungsmetriken fuer Peak-Hit/Miss, Timing-Fit/Reaktionsverzug, Ranking-Plausibilitaet und Gruppenreaktion berechnen und exportieren.

## PSwR-078 Kalibrierprofil fuer Fusion-Gewichte und Schwellen (V4.0)
Die Software muss ein explizites Kalibrierprofil fuer Fusion-Stage-/Trend-Schwellen, Dominanzgrenzen und Ranking-Erwartungen konfigurierbar fuehren.

## PSwR-079 Event-Recency-/Stale-Behandlung im Scorepfad (V4.0)
Die Software muss stale Event-Signale im Fusion-Scorepfad ueber transparente Recency-/Decay-Regeln behandeln und stale-bezogene Warnschwellen explizit konfigurierbar machen.

## PSwR-080 Validation Summary in Status/Review-Bundle (V4.0)
Die Software muss eine strukturierte Validation Summary in `fusion_status.json`, Handout, Acceptance-Snapshot und Review-Bundle ausgeben.

## PSwR-081 Analystenfreundliche Layer-Diagnostik (V4.0)
Die Software muss diagnostische Felder fuer Dominanz, stale Signale, strukturelle Ausreisser sowie breite vs. schmale Layer-Unterstuetzung bereitstellen.

## PSwR-082 Historical-Validation-Hilfsartefakte (V4.0)
Die Software muss zusaetzliche reviewbare Historical-Validation-Artefakte (z. B. Episodenvergleich, Timing-Hinweise, Layer-Diagnostik) im Fusion-Exportraum bereitstellen.

## PSwR-083 Explizites Freshness-/Staleness-Modell (V4.1)
Die Software muss ein konfigurierbares Freshness-/Staleness-Modell je Gruppe bereitstellen (fresh/aging/stale, Decay-Parameter), das transparent dokumentiert, testbar und exportierbar ist.

## PSwR-084 Recency-/Decay-Wirkung fuer dynamische Layer (V4.1)
Die Software muss die Recency-/Decay-Wirkung fuer dynamische Layer (insbesondere `event`) so anwenden, dass neue Signale zeitnah sichtbar werden und alte Signale nachvollziehbar an Einfluss verlieren.

## PSwR-085 Snapshot-Freshness-Diagnostik (V4.1)
Die Software muss pro Land/Gruppenbeitrag operative Freshness-Diagnosen exportieren (z. B. letzte frische Beobachtung, Freshness-Klasse, Fresh/aging/stale-Beitragsanteile).

## PSwR-086 Historische Responsiveness-Metriken (V4.1)
Die Software muss pragmatische historische Responsiveness-Metriken exportieren (z. B. Delta-Intensitaet, signifikante Aenderungsquote, Reaktivitaetsprofil, juengste Aenderungsdetektion).

## PSwR-087 Freshness-sensible Confidence-Haertung (V4.1)
Die Software muss stale-/aging-Anteile in der Fusion-Confidence explizit beruecksichtigen, ohne Score und Confidence konzeptionell zu vermischen.

## PSwR-088 V4.1-Kalibrierparameter im Config-Pfad (V4.1)
Die Software muss V4.1-spezifische Freshness-/Responsiveness-Kalibrierparameter validieren und versionierbar im Konfigurationsprofil fuehren.

## PSwR-089 Operative Warn- und Review-Hinweise (V4.1)
Die Software muss wenige, hochrelevante operative Warnhinweise bereitstellen (z. B. low fresh coverage, stale burden, dynamische Readiness-Luecken, Response-lag-Reviewhinweis).

## PSwR-090 V4.1-Sicht in Handout und Bundle (V4.1)
Die Software muss die operative Frische-/Responsiveness-Sicht in Handout, `validation_summary`, Acceptance-Snapshot und Review-Bundle transportieren.

## PSwR-091 Governance-Source-/Adapter-Contract (V4.2)
Die Software muss einen expliziten Governance-Adapterpfad bereitstellen (`governance_input`), der periodische Governance-/politische Stabilitaetssignale mit Pflichtfeldern, Provenance und Qualitaet in kanonische Observationen ueberfuehrt.

## PSwR-092 Governance-Normalisierung (V4.2)
Die Software muss Governance-Rohsignale ueber eine transparente, dokumentierte Heuristik in ein normiertes Teilsignal `[0,1]` ueberfuehren und quellspezifisch konfigurierbar normalisieren.

## PSwR-093 Governance-Wirksamkeit in Snapshot/Historical-Fusion (V4.2)
Die Software muss Governance in `group_scores`, `historical_group_scores`, `fusion_total_scores` und `historical_total_scores` als wirksamen, nachvollziehbaren Beitrag integrieren.

## PSwR-094 Governance-Diagnostik, Warnings und Confidence-Hinweise (V4.2)
Die Software muss governance-spezifische Diagnose-/Warning-Felder bereitstellen (z. B. elevated governance instability, stale governance support), ohne Warning-Flut und ohne Score-/Confidence-Vermischung.

## PSwR-095 Governance-Validation-/Referenzepisoden-Erweiterung (V4.2)
Die Software muss den Validierungsrahmen und Referenzepisoden so erweitern, dass Governance als eigener Review-Anker in Peak/Timing/Layer-Reaktionsmetriken pruefbar ist.

## PSwR-096 Governance-Sicht in Handout/Acceptance/Review-Bundle (V4.2)
Die Software muss Governance als klar benannten Analysebaustein in Handout, Validation Summary, Acceptance Snapshot und Review-Bundle sichtbar ausgeben.

## PSwR-097 Verbindliche 10-Laender-Enforcement-Logik (V4.3)
Die Software muss den V4.3-Vergleichsraum der 10 Laender in Config-/Pipeline-Validierung explizit erzwingen und konsistente Laendernamen/-codes in allen Exporten sicherstellen.

## PSwR-098 356-Tage-Laenderprofilmetriken (V4.3)
Die Software muss pro Land verlaufsbasierte 356-Tage-Metriken berechnen und exportieren (aktueller Score, Jahresmax/-min, Spannweite, Volatilitaet, mittlere Belastung, Peak-Kennzahlen, Freshness-/Confidence-Kontext).

## PSwR-099 Kompakte Hauptvergleichstabelle (V4.3)
Die Software muss eine analystisch kompakte Hauptvergleichstabelle fuer alle 10 Laender exportieren, inklusive aktueller Lage, Freshness-Status, Jahresprofil-Kennzahlen und dominantem Beitragsraum.

## PSwR-100 Vertiefende Diagnostiktabellen (V4.3)
Die Software muss mindestens zwei vertiefende Diagnostiktabellen exportieren (z. B. Top-Peaks je Land, mittlere Gruppenbeitraege/Supportprofile), die nicht redundant zur Hauptvergleichstabelle sind.

## PSwR-101 Pro-Land-Jahresprofilplots (V4.3)
Die Software muss pro Land einen V4.3-Jahresprofilplot erzeugen, der den Fusion-Gesamtverlauf ueber 356 Tage und zentrale Treibergruppen in konsistenter Darstellung zeigt.

## PSwR-102 Laenderuebergreifende Vergleichsplots (V4.3)
Die Software muss laenderuebergreifende V4.3-Vergleichsplots erzeugen (mindestens Multi-Land-Gesamtverlauf und Ranking-Trajektorie ueber die Zeit).

## PSwR-103 Handout-Struktur fuer V4.3-Vergleich (V4.3)
Die Software muss das Handout so strukturieren, dass ein globaler 10-Laender-Vergleichsteil vor den Laenderkapiteln steht und jedes Land danach gleich tief dargestellt wird.

## PSwR-104 V4.3-Vergleichssicht im Acceptance-/Review-Bundle (V4.3)
Die Software muss V4.3-Vergleichsartefakte (Hauptvergleich, Peaks, Gruppenprofile, Ranking-Trajektorie) in Acceptance Snapshot und Review-Bundle transportieren.

## PSwR-105 Gehaertete Peak-Erkennung im 356-Tage-Raum (V4.3.1)
Die Software muss Peaks je Land nicht nur ueber rohe Maxima, sondern ueber lokale Maxima mit Prominenz-, Rise-/Fall-, Breiten- und Mindestabstandsregeln erkennen und als konfigurierbare Heuristik exportierbar halten.

## PSwR-106 Kalibrierbarer Peak-Attributions-/Support-Parameterraum (V4.3.1)
Die Software muss V4.3.1-spezifische Peak-Attributionsparameter (z. B. Prominenz, Separation, Single-Group-Dominanz, Global-/Country-Share-Schwellen, Event-Support-Schwellen) im Config-Pfad validieren und versionierbar fuehren.

## PSwR-107 Globale-vs.-laenderspezifische Peak-Dekomposition (V4.3.1)
Die Software muss fuer erkannte Peaks explizite globale und laenderspezifische Beitragsanteile berechnen und als strukturierte Diagnostik exportieren, damit globale Synchronisationswellen nicht als rein laenderspezifische Hochpunkte fehlgelesen werden.

## PSwR-108 Peak-Attributionsartefakte je Land/Peak (V4.3.1)
Die Software muss je Peak einen expliziten Attributionsdatensatz exportieren (`peak_attribution.csv`) mit mindestens Zeitpunkt, Rang, Peak-Staerke, dominanter/sekundaerer Gruppe, Support-Breite, Freshness-Anteil und Attributionslabel.

## PSwR-109 Event-Support-Registry und Peak-Event-Abgleich (V4.3.1)
Die Software muss einen versionierbaren Analystenpfad fuer Event-Marker (MVP: fixture-/registry-basiert) unterstuetzen und je Peak als Artefakt (`peak_event_support.csv`) ausweisen, ob Event-Support stark, schwach oder nicht vorhanden ist.

## PSwR-110 Peak-Confidence- und Trajectory-Profil-Diagnostik (V4.3.1)
Die Software muss Peak-Confidence und Trajectory-Profile je Land berechnen und exportieren (`trajectory_profiles.csv`), inklusive Warnindikatoren fuer schmale, stale oder global getriebene Peak-Lagen.

## PSwR-111 Peak-Attributions-/Synchronisationssicht im Handout und Plotraum (V4.3.1)
Die Software muss pro Land Peak-Attributionsplots sowie einen globalen Peak-Synchronisationsplot erzeugen und im Handout explizit einbinden, inklusive kompakter Peak-Label (`event_supported`, `weakly_supported`, `globally_co_moving`, `model_driven`).

## PSwR-112 V4.3.1-Artefakte im Acceptance-/Review-Bundle (V4.3.1)
Die Software muss `peak_attribution`, `peak_event_support`, `trajectory_profiles`, `global_peak_synchronization` und `event_marker_registry` im Acceptance Snapshot und Review Bundle als eigenstaendige Review-Artefakte transportieren.

## PSwR-113 Event-Registry-Datenmodell (V4.3.2)
Die Software muss ein kompaktes, robustes Event-Registry-Schema mit analystenpflegbaren Pflichtfeldern bereitstellen (mindestens `event_id`, `country`, `title`, `start_date`, `end_date`, `event_type`, `summary`, `source_category`, `source_reference`, `confidence`, `relevance_groups`, `expected_effect_direction`, `expected_peak_window_start`, `expected_peak_window_end`, `notes`).

## PSwR-114 Initialer 10-Laender-Registry-Bestand (V4.3.2)
Die Software muss einen initialen Event-Registry-/Fixture-Bestand fuer den verbindlichen 10-Laender-Raum liefern.

## PSwR-115 Peak-Event-Matching-Export (V4.3.2)
Die Software muss je Peak einen expliziten Peak-Event-Match-Datensatz exportieren (`peak_event_matches.csv`) mit Match-Klasse, Match-Confidence, Evidenzkette und Unsicherheitsmarkern.

## PSwR-116 Match-Klassen im Event-Alignment (V4.3.2)
Die Software muss mindestens folgende Match-Klassen unterscheiden und exportieren:
`direct_match`, `plausible_context_match`, `weak_match`, `no_credible_match`, `multi_event_overlap`.

## PSwR-117 Country-Level Event-Alignment-Maturity (V4.3.2)
Die Software muss country-level Alignment-Maturity als eigenes Artefakt (`country_event_alignment.csv`) ausweisen, inklusive Trajectory-Kontext, Coverage-Qualitaet, Top-Events und offener Unsicherheiten.

## PSwR-118 Event-Coverage-Diagnostik (V4.3.2)
Die Software muss global und pro Land Event-Coverage-Metriken exportieren (`event_coverage_summary.csv`), inkl. credible/no-match/multi-overlap-Anteilen.

## PSwR-119 Event-Alignment-Reviewdatei (V4.3.2)
Die Software muss eine kompakte analystische Review-Datei fuer Event-Alignment bereitstellen (`event_alignment_review.md`) mit Summary, Coverage und manueller Review-Queue.

## PSwR-120 V4.3.2-Artefakte im Acceptance-/Review-Bundle (V4.3.2)
Die Software muss `event_registry`, `peak_event_matches`, `event_coverage_summary`, `country_event_alignment` und Event-Alignment-Summary/-Review im Acceptance Snapshot und Review Bundle transportieren.

## PSwR-121 Event-Alignment-Plot-Unterstuetzung (V4.3.2)
Die Software muss pro Land einen Event-Alignment-Plot bereitstellen, der Fusion-Verlauf, Peak-Marker und registrierte Event-Fenster in analystisch lesbarer Form kombiniert.

## PSwR-122 V4.3.2-Kalibrierparameter im Config-Pfad (V4.3.2)
Die Software muss Event-Alignment-Kalibrierparameter im Config-Pfad validieren und versionierbar fuehren (zeitliche Distanz, direct/context/weak-Schwellen, multi-overlap-Minimum, Registry-Pfad).

## PSwR-123 Event-Alignment-Sicht im Handout (V4.3.2)
Die Software muss die Event-Alignment-Sicht im Handout global und pro Land explizit darstellen (Match-Klassen, Match-Confidence, global-vs-country-Kontext, offene Unsicherheiten).

## PSwR-124 Additive V4.3.2-Integration ohne Regression (V4.3.2)
Die Software muss V4.3.2 additiv integrieren, ohne bestehende V2.x-/V3.x-/V4.0-/V4.1-/V4.2-/V4.3-/V4.3.1-Pfade zu regressieren.
