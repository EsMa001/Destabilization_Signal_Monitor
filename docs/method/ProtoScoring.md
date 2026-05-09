# ProtoScoring

## ALG-001 Spannungs-Subscores
Spannung wird aus mehreren Teil-Scores fuer Protest-, Krisen- und Negativitaetssignale gebildet.

## ALG-002 Eskalations-Subscores
Eskalation wird getrennt fuer interne und externe / kriegerische Dynamik aus Teil-Scores gebildet.

## ALG-003 Verwundbarkeits-Subscores
Verwundbarkeit wird aus wirtschaftlicher, hybrider und Governance-bezogener Hintergrundlage gebildet.

## ALG-004 Cluster-Score
Cluster-Scores werden in V1/V2 durch eine einfache, transparente Aggregation aus validierten Teil-Scores gebildet.

## ALG-005 Stufen
Cluster-Scores werden je Cluster in niedrig / erhoeht / hoch / sehr hoch eingeteilt.

## ALG-006 Trend
Trend wird aus robusten 7d- und 30d-Vergleichen als ruecklaeufig / stabil / zunehmend abgeleitet.

## ALG-007 Confidence
Confidence wird aus Datendichte, Signalkonsistenz, Staerke der Abweichung und Quellplausibilitaet abgeleitet.

## ALG-008 Run-Status
Der Run-Status wird aus Pflichtquellenverfuegbarkeit, Datenqualitaet, Konsistenz und Output-Vollstaendigkeit vorgeschlagen.

## V2 Kalibrierprofil (konfigurierbar)
V2 fuehrt ein explizites Kalibrierprofil in `config/default.yaml` ein:
- `scoring.stage.low_max`
- `scoring.stage.elevated_max`
- `scoring.stage.high_max`
- `scoring.trend.delta_epsilon`

Damit werden harte V1-Defaults fuer Stufen und Trendgrenzen durch klar dokumentierte, konfigurierbare Regeln ersetzt.

## V2.1 kalibrierter Standardwertsatz
Der aktuelle V2.1-Standardwertsatz ist:
- `scoring.stage.low_max = 30`
- `scoring.stage.elevated_max = 56`
- `scoring.stage.high_max = 80`
- `scoring.trend.delta_epsilon = 1.25`

Die Scoring-Funktionen verwenden diese Grenzen im Pipeline-Pfad ausschliesslich explizit aus der Konfiguration (keine impliziten V1-Harddefaults).

## ALG-013 Kanonisches Quellsignal (V3.1)
Jede neue Quelle liefert nach der Adapter-Normalisierung ein einfach normiertes Teilsignal `s_i` in `[0,1]`.

## ALG-014 Gruppenfusion (V3.1)
Quellen werden innerhalb ihrer Gruppe ueber eine einfache gewichtete Mittelung fusioniert. Die Quellgewichte sind transparent, manuell gesetzt und konfigurierbar.

## ALG-015 Fusion-Gesamtscore (V3.1)
Aus den Gruppensignalen wird ein zusaetzlicher Fusion-Gesamtscore ueber transparente, manuell gesetzte Gruppengewichte berechnet.

## ALG-016 Optionale gruppenuebergreifende Verstaerkung (V3.1)
Ein kleiner Bonus bei gleichzeitig erhoehten Gruppen kann als optionaler Mechanismus vorgesehen werden, ist im V3.1-MVP aber standardmaessig deaktiviert.

## ALG-017 Fusion-Confidence (V3.1)
Confidence wird im Fusion-Pfad getrennt vom Score gefuehrt und aus Quellenabdeckung, Aktualitaet, Datenvollstaendigkeit und Quellkonsistenz abgeleitet.
Im V3.2.1-Hardening kann eine moderate Confidence-Reduktion bei starker Einzel-Layer-Dominanz und hohem `limited`-Anteil erfolgen (weiterhin getrennt vom Score).

## ALG-018 GDACS-Schocksignal (V3.2)
Das `Shock`-Teilsignal wird transparent aus `severity`, Alarmstufe und Relevanz abgeleitet und danach quellspezifisch normalisiert.

## ALG-019 UNHCR-Displacementsignal (V3.2)
Das `Displacement`-Teilsignal wird transparent aus Belastungsniveau, positiver Veraenderung und Exposition abgeleitet und danach normalisiert.
Im V3.2.1-Hardening ist fuer diesen Pfad eine globale Laendernormalisierung zulaessig, um relative Plausibilitaet im Landervergleich zu staerken.

## ALG-020 Narrative-Inputsignal (V3.2)
Das `Narrative`-Teilsignal wird transparent aus Richtung, Relevanz und Confidence strukturierter Expert-Inputs abgeleitet und danach normalisiert.
Im V3.2.1-Hardening ist fuer diesen Pfad eine globale Laendernormalisierung zulaessig, um triviale länderweite Maximalsaettigung zu vermeiden.

## ALG-021 Historische Monatsfusion (V3.2)
Historische Gruppenscores und Fusion-Gesamtscores werden je monatlicher Zielperiode ueber die bestehende Gewichtungslogik berechnet.

## ALG-022 Dominanter Gruppenimpuls (V3.2)
Der dominante historische Treiber wird als Gruppe mit maximalem absoluten Delta gegenueber der Vorperiode bestimmt.
Zusaetzlich koennen Top-1/Top-2 Beitragsgruppen ueber gewichtete Beitragsanteile ausgewiesen werden.

## ALG-023 Event-Rohsignalsynthese (V3.3)
Das Event-Rohsignal wird transparent aus Event-Schwere, Event-Typ-Gewichtung, Tonalitaetsstaerke, Berichtsvolumen und innerhalb-Periode-Recency gebildet.

## ALG-024 Event-Periodenaggregation (V3.3)
Periodische Event-Signale werden aus Event-Intensitaet, Event-Haeufigkeit und Event-Typ-Abdeckung aggregiert und anschliessend wie andere Quellen auf `[0,1]` normalisiert.

## ALG-025 Episodenbasierter Peak-/Timing-Abgleich (V4.0)
Je Referenzepisode wird der beobachtete Peak im definierten Zeitraum ermittelt und gegen erwartete Stage-/Timing-Regeln geprueft (Peak-Hit/Miss, Reaktionsverzug).

## ALG-026 Ranking-Plausibilitaet (V4.0)
Die Snapshot-Laenderrangfolge wird gegen eine explizite Erwartungsrangfolge gespiegelt; Rank-Deltas und ein kompakter Ranking-Fit-Score werden ausgewiesen.

## ALG-027 Layer-Dominanz- und Support-Diagnostik (V4.0)
Dominanter Gruppenanteil, strukturelle Ausreisser sowie breite vs. schmale Layer-Unterstuetzung werden als analystenfreundliche Diagnostikfelder berechnet.

## ALG-028 Kalibrierte Event-Recency-/Validation-Heuristik (V4.0)
Event-Signale werden ab definiertem Stale-Alter ueber einen transparenten Decay-Faktor abgeschwaecht; Validation Summary aggregiert Episoden-, Ranking- und Diagnostikmetriken.

## ALG-029 Freshness-Klassifikation und Decay-Faktor (V4.1)
Je Gruppe wird ein expliziter Freshness-Rule-Satz (`fresh_max_days`, `stale_max_days`, `aging_floor_factor`, `stale_half_life_days`, `minimum_decay_factor`) angewendet, der Signalalter in `fresh/aging/stale` klassifiziert und einen transparenten Decay-Faktor liefert.

## ALG-030 Snapshot-Freshness-Gruppendiagnostik (V4.1)
Aus Signalalter, Freshness-Klasse und gewichteten Gruppenbeitraegen werden pro Land/Gruppenpaar operative Freshness-Diagnosen berechnet (inkl. letzter frischer Beobachtung, Freshness-Klasse, Beitragsanteile).

## ALG-031 Historische Responsiveness-Profile (V4.1)
Historische Fusion-Total-Zeitreihen werden ueber periodische Deltas zu einem pragmatischen Responsiveness-Profil verdichtet (`reactive`, `balanced`, `inertia_risk`, `insufficient_history`).

## ALG-032 Operative Validation Summary (V4.1)
Die Validation Summary aggregiert zusaetzlich operative Kennzahlen (freshness coverage, stale burden, dynamic readiness, response-lag fit, historical responsiveness), um den aktuellen Betriebszustand reviewbar zu machen.

## ALG-033 Governance-Rohsignalsynthese (V4.2)
Das Governance-Rohsignal wird transparent aus institutioneller Erosion (geringe Regierungs-/Institutionenwirksamkeit), politischer Kontention (Polarisierung, Protestdruck, Blockade) und Resilienzdaempfung abgeleitet.
Die Heuristik ist explizit parametriert und bleibt als reviewbarer MVP-Ansatz dokumentiert.

## ALG-034 Governance-Integration in Snapshot/Historical-Fusion (V4.2)
Der Governance-Beitrag wird als eigenstaendige Gruppe `governance` in Snapshot- und Historical-Fusion ueber den bestehenden gewichteten Fusionspfad integriert.
Gewichts- und Dominanzregeln bleiben transparent kalibrierbar, um unkontrollierte Layer-Dominanz zu vermeiden.

## ALG-035 Governance-Diagnostik und Instabilitaetsflags (V4.2)
Validation-/Diagnostikfelder fuehren governance-spezifische Hinweise explizit:
- Governance-Beitragsanteil
- Governance-Instabilitaetsflag (aktivierungsbasiert)
- Governance-Low-Freshness-Flag (freshness-basiert)
Diese Felder dienen der analystischen Trennung zwischen akutem Event-Stress und governance-getriebener Fragilitaet.

## ALG-036 356-Tage-Laenderprofilmetriken (V4.3)
Pro Land werden ueber den historischen Fusion-Verlauf kompakte Profilmetriken berechnet: aktueller Score, Jahresmaximum/-minimum, Spannweite, Mittelwert, Volatilitaet und mittlere Delta-Intensitaet.

## ALG-037 Peak-Phasen-Extraktion je Land (V4.3)
Pro Land werden die Top-Peak-Phasen ueber den 356-Tage-Verlauf ermittelt und mit Stage/Trend/Driver/Freshness-Kontext als reviewbare Diagnostik exportiert.

## ALG-038 Mittlere Gruppenbeitragsprofile (V4.3)
Historische Gruppenscores werden je Land/Gruppendimension ueber Verfuegbarkeit, Aktivierungsquote, dominante Perioden und mittlere gewichtete Beitragsanteile verdichtet.

## ALG-039 Ranking-Trajektorie ueber Perioden (V4.3)
Aus historischen Total-Scores wird pro Zielperiode ein länderübergreifendes Ranking berechnet; die zeitliche Rangentwicklung je Land wird als Vergleichspfad exportiert.

## ALG-040 Operativer Profilstatus fresh/mixed/stale (V4.3)
Ein kompakter operativer Profilstatus wird aus Freshness-Anteilen und dynamischer Readiness abgeleitet (`fresh_operational`, `mixed_watch`, `aging_watch`, `stale_attention`) und in der Hauptvergleichssicht ausgewiesen.

## ALG-041 Gehaertete Peak-Erkennung im Jahresverlauf (V4.3.1)
Peaks werden je Land ueber eine transparente Heuristik erkannt: lokales Maximum + Mindestprominenz + Mindestanstieg/-abfall + Mindestabstand + Peak-Breite.
Zur Robustheit darf ein begrenzter Fallback auf verbleibende Top-Maxima genutzt werden, damit die konfigurierte Anzahl Peak-Kandidaten fuer den Vergleichspfad stabil bleibt.

## ALG-042 Globale-vs.-laenderspezifische Peak-Anteilszerlegung (V4.3.1)
Fuer jeden Peak werden gewichtete Gruppenbeitraege in globale, laenderuebergreifend zeitnahe Komponenten und laenderspezifische Restanteile zerlegt.
Die resultierenden Anteile (`global_share`, `country_specific_share`) werden auf `[0,1]` geklemmt und als Diagnostik exportiert.

## ALG-043 Peak-Attributionslabel (V4.3.1)
Aus Event-Support, Global-/Country-Share und Support-Breite wird je Peak ein kompaktes Label abgeleitet:
`event_supported_peak`, `globally_co_moving_peak`, `country_specific_peak`, `model_driven_peak`, `weakly_supported_peak`.

## ALG-044 Event-Support-Scoring gegen Marker-Registry (V4.3.1)
Event-Support je Peak wird als zeitliches Naehe-/Overlap-Mass gegen eine versionierte Event-Marker-Registry berechnet und in diskrete Klassen (`strong`, `weak`, `none`) ueberfuehrt.

## ALG-045 Peak-Confidence-Level (V4.3.1)
Peak-Confidence wird aus Support-Breite, Freshness-Anteil, Single-Group-Dominanz, Event-Support und globaler Synchronisationslast zu einem kompakten Score und Level (`high`, `medium`, `low`) verdichtet.

## ALG-046 Trajectory-Profilableitung je Land (V4.3.1)
Je Land wird aus Peak-Struktur, Dominanzmustern und Synchronisationsanteilen ein Trajectory-Profil abgeleitet (z. B. `event_spiking`, `baseline_high`, `governance_heavy`, `globally_co_moving`).

## ALG-047 Globale Peak-Synchronisationsmetriken (V4.3.1)
Perioden mit Mehrlaender-Peak-Konzentration werden als Synchronisationscluster ausgewiesen; exportiert werden mindestens Landanzahl, beteiligte dominante Gruppen, mittlerer globaler Anteil und Event-Support-Anteil.

## ALG-048 Event-Registry-Schema-Validierung (V4.3.2)
Registry-Zeilen werden gegen ein kompaktes Pflichtfeldschema validiert (IDs, Land, Zeitfenster, Evidenz-/Confidence-/Relevanzfelder), damit Event-Alignment robust und reproduzierbar bleibt.

## ALG-049 Candidate-Event-Selektion je Peak (V4.3.2)
Fuer jeden Peak werden Event-Kandidaten ueber Landfilter + zeitliches Suchfenster + erwartetes Peak-Wirkfenster vorselektiert.

## ALG-050 Mehrfaktor-Matchscore fuer Peak-Event-Alignment (V4.3.2)
Matchscore kombiniert zeitliche Distanz, Fensterueberlappung, thematische Relevanzgruppenpassung, Peak-Support/Confidence und Verlaufskontext zu einem kontinuierlichen Wert auf `[0,1]`.

## ALG-051 Match-Klassifikation aus Schwellenprofil (V4.3.2)
Kontinuierliche Matchscores werden ueber kalibrierbare Schwellen in Klassen ueberfuehrt:
`direct_match`, `plausible_context_match`, `weak_match`, `no_credible_match`; bei Mehrfachtreffern gilt `multi_event_overlap`.

## ALG-052 Event-Coverage-Kennzahlen (V4.3.2)
Global und pro Land werden Coverage-Metriken berechnet: credible-match-Anteil, no-credible-match-Anteil, multi-overlap-Anteil, mittlere Match-Confidence und Registry-Abdeckung.

## ALG-053 Country Alignment Maturity (V4.3.2)
Je Land wird aus Matchqualitaet, Coverage und Unsicherheitslast ein kompakter Alignment-Maturity-Score inkl. Maturity-Klasse abgeleitet.

## ALG-054 Event-Alignment-Reviewqueue (V4.3.2)
Peaks mit `no_credible_match`, niedriger Match-Confidence oder `multi_event_overlap` werden als manuelle Reviewqueue priorisiert.

## ALG-055 Event-Alignment-Warning-Heuristik (V4.3.2)
Der Lauf erzeugt wenige, fokussierte Hinweise bei schlechter Event-Erdung (`peak_no_credible_event_match`, `event_coverage_sparse`, `multi_event_overlap_review`, `trajectory_weak_event_grounding`).

## ALG-056 Event-Alignment-Plotkodierung (V4.3.2)
Pro Land werden 356-Tage-Verlauf, Peak-Marker und Event-Fenster kombiniert; Match-Klassen werden ueber Farbe/Symbol eindeutig codiert, ohne Plotueberladung.
