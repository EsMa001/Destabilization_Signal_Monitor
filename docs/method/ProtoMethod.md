# ProtoMethod

## PM-001 Grundkette
Rohdaten -> Features -> Subscores -> Cluster-Scores -> Baseline-Einordnung -> Stufen / Trend / Confidence -> Report.

## PM-002 Laendervergleich
Laender werden in gemeinsamer Struktur, aber mit landesspezifischer Baseline-Einordnung betrachtet.

## PM-003 V1-Quellenkern
Version 1 verwendet ausschliesslich GDELT, UCDP, Bridge-Datei und Kontexttabelle.

## PM-004 Clusterlogik
Spannung und Eskalation stehen in der Leselogik vor Verwundbarkeit; Verwundbarkeit bleibt methodisch gleichwertig.

## PM-005 Zeitaufloesung
Intern taeglich, sichtbar geglaettet / robust verdichtet.

## PM-006 Einfach und erklaerbar
Die erste Ableitungslogik bleibt einfach, robust und erklaerbar.

## PM-007 Kalibrierbare Regeln (V2)
Ab V2 werden Schwellen- und Trendgrenzen explizit konfigurierbar gehalten und ueber die Projektkonfiguration versioniert.
Im Pipeline-Pfad werden Stufen- und Trendgrenzen explizit aus der geladenen Konfiguration uebergeben; implizite V1-Harddefaults sind nur noch Legacy-Fallback fuer Altartefakte.

## PM-008 Duale Standardsicht
Der offizielle Standardlauf erzeugt zwei gleichwertige Ergebnisbereiche: `Current Snapshot` und `Historical Rolling Trend`.

## PM-009 Rolling-Window-Prinzip
Der Historical Rolling Trend wird aus taeglichen Basiswerten durch eine parametrierbare Rolling-Window-Verdichtung erzeugt. Standard ist ein gleitender Mittelwert ueber `window_days=7`.

## PM-010 Gemeinsame Ableitungslogik
Der `Current Snapshot` basiert auf derselben Rolling-Window-Logik wie der letzte Punkt des `Historical Rolling Trend`.
Ableitungsreihenfolge im Standardmodus:
- gueltiger Historical-Endpunkt am Run-Datum
- sonst letzter gueltiger Historical-Punkt vor Run-Datum
- sonst letzter numerischer Historical-Punkt unterhalb `min_valid_days` (explizit markiert, mit zusaetzlicher Snapshot-Confidence-Reduktion)

## PM-011 As-of-Date-Pflicht
Jeder historische Trendpunkt darf nur Daten verwenden, die bis zu seinem Bewertungszeitpunkt verfuegbar gewesen waeren. Diese Regel ist im offiziellen Standardmodus verpflichtend; weitere historische Sondermodi koennen spaeter ergaenzt werden.

## PM-012 Historische Datenabdeckung
Der Historical Rolling Trend liegt auf einem taeglichen Raster. Fehlende Tage bleiben explizit fehlend; es erfolgt keine Interpolation und keine automatische Fortschreibung. Pro Verdichtungsfenster gilt eine Mindestabdeckung `min_valid_days`, deren Unterschreitung zu einer expliziten Einschraenkung und reduzierter Confidence fuehrt.
Falls der Snapshot mangels gueltiger Punkte auf einen numerischen Punkt unterhalb `min_valid_days` zurueckfaellt, wird dieser Zustand verpflichtend in Handout/Metadaten markiert und die Snapshot-Confidence zusaetzlich abgesenkt.

## PM-013 Historische Hilfsquellen
Bridge-Datei und Kontexttabelle werden im Historical Rolling Trend vorerst als zeitlich konstant behandelt, bis historisierte Versionen vorliegen. Diese Einschraenkung ist methodisch explizit zu dokumentieren.
Im aktuellen Modellstand wird dadurch insbesondere `vulnerability` als ueberwiegend struktureller Baseline-Cluster eingeordnet.

## PM-014 Berichtslogik
Das Handout bleibt primaer pro Land gegliedert. Innerhalb jedes Landes werden `Current Snapshot` und `Historical Rolling Trend` strikt getrennt dargestellt. Der Snapshot enthaelt zusaetzlich einen Jahreskontext aus dem Historical Rolling Trend.

## PM-015 Historische Validierung
Der Historical Rolling Trend dient der laengerfristigen Trendbeobachtung und der rueckwirkenden Validierung gegen bekannte historische Entwicklungen. Ein expliziter Event-Layer ist als spaeterer Ausbaupfad vorgesehen, aber nicht Teil des aktuellen Pflichtumfangs.
Bis zur Einfuehrung eines Event-Layers wird ein analystenorientierter Review-Candidate-Output verwendet: priorisierte historische Clusterpunkte mit expliziter Kennzeichnung von Low-Coverage-Signalen und kompakten Driver-Hinweisen.

## PM-016 Kanonische Beobachtungsnormalisierung (V3.1)
Neue V3.1-Quellen werden vor jeder Layer-/Fusion-Berechnung in ein kanonisches Observation-Schema ueberfuehrt und auf Pflichtfelder validiert.

## PM-017 Parallele Ergebnisraeume (V3.1)
Die bestehende Cluster-Sicht bleibt unveraendert erhalten; die Layer-/Gruppensicht und der Fusion-Pfad werden additiv parallel gefuehrt.

## PM-018 Quellennahe Normalisierung (V3.1)
Jede neue Quelle liefert ein explizit konfiguriertes normiertes Teilsignal `s_i` in `[0,1]` (z-score, percentile oder baseline deviation).
Fuer ausgewaehlte Quellen darf der Normalisierungs-Scope explizit zwischen `per_country` und `global` differenziert werden, um triviale Laender-Saettigung zu vermeiden.

## PM-019 Transparente Gruppenfusion (V3.1)
Innerhalb jeder Gruppe werden Quellen ueber einfache manuelle Gewichte gemittelt; keine automatische Optimierung im MVP.

## PM-020 Paralleler Fusion-Gesamtscore (V3.1)
Aus Gruppenscores wird ein separater Fusion-Gesamtscore ueber manuelle Gruppengewichte berechnet; der bestehende Score wird nicht ersetzt.

## PM-021 Separate Fusion-Confidence (V3.1)
Confidence im Fusion-Pfad wird getrennt vom Score berechnet und sichtbar ausgegeben.
Im V3.2.1-Hardening werden Coverage-/Qualitaetskomponenten explizit ausweisbar gehalten; moderate Penalties fuer dominante Einzel-Layer bzw. hohe `limited`-Anteile sind zulaessig.

## PM-022 Zielperioden statt erzwungenem Rohdatenraster (V3.1)
Native Quellperioden bleiben im Observation-Schema erhalten; die Fusion arbeitet auf definierter Zielperiode und behaelt Provenance.

## PM-023 Additives V3.1-Reporting (V3.1)
V3.1 erzeugt zusaetzliche Exporte, Handout-Bloecke und Plots fuer Layer/Fusion, ohne Snapshot/Historical-Artefakte des Bestands zu brechen.

## PM-024 Monatliche Fusion-Zielperioden (V3.2)
Der historische Fusion-Pfad arbeitet im MVP auf expliziten monatlichen Zielperioden statt auf kuenstlicher Tagesaufloesung.

## PM-025 As-of-Selektion je Zielperiode (V3.2)
Pro Quelle/Land/Periode wird der letzte bis Periodenende verfuegbare Beobachtungspunkt verwendet.

## PM-026 Transparente Layer-Mappings fuer neue Quellen (V3.2)
`GDACS`, `UNHCR` und `narrative_input` werden ueber explizite, nachvollziehbare Mapping-Regeln in `Shock`, `Displacement` und `Narrative` ueberfuehrt.

## PM-027 Gruppenstatus-Semantik (V3.2)
Fusion-Gruppen unterscheiden `ok`, `limited` und `not_available` transparent nach Quellabdeckung.

## PM-028 Historische Driver-Hinweise (V3.2)
Der historische Fusion-Pfad fuehrt kompakte Hinweise auf dominante Gruppen-Deltas fuer analystenfreundliche Interpretation.
Im V3.2.1-Hardening werden zusaetzlich Top-Beitrags-Layer (Top-1/Top-2) und die staerkste Aenderung zum Vorzeitpunkt ausgewiesen.
Ab V3.2.2 gilt: wenn keine materielle Aenderung vorliegt, bleibt der Aenderungs-Driver neutral (`strongest_change_group = none`, `no_material_change = true`).

## PM-029 Historische Fusion-Einordnung (V3.2)
Historische Fusion-Gesamtscores erhalten pro Periode eine einfache Stage-/Trend-Einordnung mit konfigurierten Schwellen.
Die Einordnung fuehrt explizite Gruppenabdeckungsfelder (`available/expected/ratio`) je historischer Periode mit.
Ab V3.2.2 wird zusaetzlich ein `interpretation_status` (`standard` / `reduced_historical_coverage` / `limited_historical_coverage`) je Periode ausgewiesen.

## PM-030 Additives V3.2-Reporting (V3.2)
V3.2 erzeugt zusaetzliche historische Fusion-Exporte, Handout-Bloecke und Plots als eigenen Ergebnisraum neben Snapshot und Cluster-History.
V3.2.1 ergaenzt kompakte, nicht-blockierende Plausibilitaetswarnungen in Status-/Handout-Sicht.
V3.2.2 verdichtet die Warnings auf aussagekraeftige Summary-Hinweise und markiert fruehe historisch eingeschraenkte Perioden im Handout expliziter.

## PM-031 Bestandswahrung (V3.2)
V2.x- und V3.1-Pfade bleiben unveraendert lauffaehig; V3.2 wirkt ausschliesslich additiv.

## PM-032 Event-Signaldefinition (V3.3)
Der Event-Layer verarbeitet beobachtbare, explizit ereignisbezogene Konflikt-/Stoerungsindikatoren (keine Narrative-/Struktur-Ersatzlogik).
Die Ableitung bleibt transparent und fuehrt Event-Typ, Schwere, Frequenz, Recency und Qualitaetsaspekte nachvollziehbar zusammen.

## PM-033 Event-Periodisierung fuer Fusion (V3.3)
Event-Rohdaten werden in periodische Event-Observationen ueberfuehrt (MVP: monatlich) und danach in den bestehenden Snapshot-/Historical-Fusionpfad eingespeist.
Native Ereigniszeitpunkte bleiben ueber Metadaten/Provenance nachvollziehbar.

## PM-034 Event-Explainability und Plausibility-Hinweise (V3.3)
Event wird als gleichwertiger Gruppenbeitrag in der Fusion-Explainability gefuehrt.
Nicht-blockierende Event-spezifische Warnungen (z. B. stale Signale, partielle Verfuegbarkeit) sind explizit sichtbar auszuweisen.

## PM-035 Expliziter Validierungsrahmen (V4.0)
V4.0 fuehrt einen expliziten Validierungsrahmen mit Referenzepisoden, Bewertungsregeln und exportierbarer Framework-Beschreibung ein.

## PM-036 Referenzepisoden als Analysten-Review-Anker (V4.0)
Referenzepisoden sind strukturierte analystennahe Review-Anker (kein perfekter Ground Truth), die Land, Zeitraum, erwartete Layer-Reaktion und erwartete Gesamtreaktion transparent dokumentieren.

## PM-037 Pragmatistische Validierungsmetriken (V4.0)
Validierung wird ueber einfache, reviewbare Kennzahlen operationalisiert (Peak-Hit/Miss, Timing-Fit, Gruppenreaktion, Ranking-Plausibilitaet), ohne methodische Scheingenauigkeit.

## PM-038 Transparente Kalibrierungsheuristik (V4.0)
Gewichte, Stages und Warnschwellen werden ueber ein explizites Kalibrierprofil nachgeschaerft; Entscheidungen bleiben nachvollziehbar und versioniert.

## PM-039 Event-Recency als Dynamik-Regel (V4.0)
Event-Signale behalten ihre Dynamikrolle ueber transparente Recency-/Decay-Regeln; stale Event-Lagen werden explizit diagnostiziert.

## PM-040 Historische Interpretationsgrenzen (V4.0)
Historische Validierung muss eingeschraenkte fruehe Perioden mit geringer Layer-Abdeckung explizit markieren; diese Perioden sind nur vorsichtig interpretierbar.

## PM-041 Validierungsstand als Pflicht-Reviewkontext (V4.0)
Der Lauf transportiert den Validierungsstand verpflichtend in Fusion-Status, Handout, Acceptance-Snapshot und Review-Bundle.

## PM-042 Freshness-Klassifikation als Betriebsregel (V4.1)
Zeitdynamische Signale werden je Gruppe explizit als `fresh`, `aging` oder `stale` klassifiziert; die Klassengrenzen sind konfigurierbar und nachvollziehbar zu dokumentieren.

## PM-043 Transparenter Freshness-Decay mit Event-Fresh-Boost (V4.1)
Freshness-Wirkung erfolgt ueber eine einfache, transparente Piecewise-Decay-Heuristik (fresh/aging/stale); fuer `event` ist ein begrenzter Fresh-Boost zulaessig.

## PM-044 Freshness-kalibrierte Snapshot-/Historical-Fusion (V4.1)
Snapshot- und Historical-Fusion verwenden dieselben Freshness-Regeln, damit operative Aktualitaetslogik ueber beide Zeitraeume konsistent wirkt.

## PM-045 Pragmatistische Responsiveness-Metrik (V4.1)
Historische Reaktionsfaehigkeit wird ueber einfache Delta-Metriken bewertet (mean/max absolute delta, signifikante Aenderungsquote, juengste Delta-Detektion) statt ueber komplexe Statistik.

## PM-046 Operative Freshness-Sicht fuer Analysten (V4.1)
Review-Artefakte sollen frische vs. stale Beitragslage explizit zeigen (Freshness-Coverage, stale burden, dynamic readiness, letzte frische Beobachtung).

## PM-047 Operative Diagnosefelder je Land (V4.1)
Diagnosefelder je Land muessen zwischen frischer Unterstuetzung und nachwirkender Altlast unterscheiden (fresh/stale support profile, dominante frische/aging/stale Gruppen).

## PM-048 V4.1-Review-Bundle-Kompaktheit (V4.1)
Die operative Frische-/Responsiveness-Sicht wird als knapper, reviewbarer Zusatz in Handout/Status/Acceptance-Snapshot transportiert; keine Textueberladung und keine neue Grossarchitektur.

## PM-049 Governance-Abgrenzung und Scope-Regel (V4.2)
Der Governance-Beitragsraum modelliert politische Handlungsfaehigkeit, institutionelle Stabilitaet, Legitimitaet und politische Kohaesion explizit zwischen struktureller Baseline und akutem Event-Stress.
Abgrenzung:
- `structural`: eher langfristige Verwundbarkeit/Exposure
- `event`: beobachtbare akute Ereignisintensitaet
- `narrative`: diskursive/kommunikative Dynamik
Governance soll keine Duplikat-Ersatzlogik fuer diese Layer sein, sondern eine eigenstaendige politische Zwischenebene.

## PM-050 Governance-Signalableitung und Periodik (V4.2)
Governance wird ueber einen expliziten, transparenten Adapterpfad (`governance_input`) periodisch (MVP: monatlich) in kanonische Observationen ueberfuehrt.
Die Rohableitung bleibt heuristisch, nachvollziehbar und testbar (institutionelle Erosion, politische Blockade/Polarisierung, Resilienzdaempfung) und wird quellspezifisch normalisiert.

## PM-051 Governance-Reviewfaehigkeit in Validation/Bundle (V4.2)
Governance muss nicht nur score-wirksam sein, sondern als eigener Reviewanker in Validation Summary, Layer-Diagnostik, Warnings, Handout, Acceptance-Snapshot und Review-Bundle sichtbar bleiben.
Die Darstellung bleibt kompakt, aber mit klaren Signalen fuer Governance-Instabilitaet, Governance-Freshness und Governance-Beitragsanteil.

## PM-052 Verbindlicher V4.3-Vergleichsraum (V4.3)
V4.3 arbeitet mit einem festen 10-Laender-Vergleichsraum. Alle Laender werden in derselben Analyse-/Exportlogik verarbeitet; es gibt keine impliziten Prioritaetslaender.

## PM-053 356-Tage-Profil-First-Methodik (V4.3)
Die V4.3-Kernsicht ist profilgetrieben ueber den vollstaendigen 356-Tage-Verlauf je Land. Vergleich und Validierung werden primär ueber Verlaufsmetriken (Level, Range, Volatilitaet, Peaks, Ranking-Trajektorie) gefuehrt.

## PM-054 Kompakte + vertiefende Vergleichsartefakte (V4.3)
V4.3 exportiert eine kompakte Hauptvergleichstabelle plus vertiefende Diagnostiktabellen und Vergleichsplots. Die Artefakte bleiben pragmatisch, reviewbar und ohne methodische Scheingenauigkeit.

## PM-055 Gleich tiefe Reporting-Struktur (V4.3)
Das Handout beginnt mit globalen Vergleichsteilen fuer alle 10 Laender und fuehrt danach gleich tief strukturierte Laenderkapitel aus. Unterschiede sollen aus Datenprofilen folgen, nicht aus Berichtstiefe.

## PM-056 Additive V4.3-Integration (V4.3)
V4.3 erweitert den bestehenden V4.2-Stand additiv; Snapshot, Historical Fusion, Validation, Governance-/Freshness-Logik und bestehende Bundlepfade bleiben funktional erhalten.

## PM-057 Peak-Qualitaet vor Rohmaximum (V4.3.1)
Peak-Erkennung folgt in V4.3.1 einer qualitaetsorientierten Heuristik (lokales Maximum, Prominenz, Rise/Fall, Breite, Mindestabstand), damit analytisch markante Phasen priorisiert werden statt isolierter numerischer Spitzen.

## PM-058 Globale-vs.-laenderspezifische Dekomposition (V4.3.1)
Jeder Peak wird in einen global synchronisierten und einen laenderspezifischen Anteil zerlegt. Diese Zerlegung bleibt transparent, heuristisch und reviewbar; keine Black-box-Entkopplung.

## PM-059 Event-Support als Analysten-Reviewanker (V4.3.1)
Event-Support wird in V4.3.1 ueber einen versionierbaren Marker-/Annotation-Pfad bestimmt (MVP: Registry/Fixture), klar getrennt von der Scorelogik. Ziel ist interpretierbare Peak-Einordnung statt Scheinvalidierung.

## PM-060 Peak-Confidence aus Support-Breite, Freshness und Dominanz (V4.3.1)
Peak-Confidence wird aus nachvollziehbaren Faktoren gebildet: Anzahl tragender Gruppen, Freshness-Anteil, Single-Group-Dominanz, globaler Synchronisationsanteil und Event-Support-Status.

## PM-061 Trajectory-Profile fuer Verlaufseinordnung (V4.3.1)
Der Jahresverlauf je Land wird zusaetzlich ueber ein kompaktes Trajectory-Profil klassifiziert (z. B. `event_spiking`, `globally_co_moving`, `structurally_elevated`), um numerische Verlaeufe analystisch lesbarer zu machen.

## PM-062 Peak-Synchronisationsdiagnostik im Mehrlaenderraum (V4.3.1)
Der Mehrlaendervergleich fuehrt explizite Synchronisationsdiagnostik fuer Peak-Cluster, damit globale Wellen, mitlaufende Laender und laenderspezifische Eigenstaendigkeit systematisch unterschieden werden koennen.

## PM-063 Event-Registry als stabiler Analystenpfad (V4.3.2)
Der Event-Alignment-Raum wird als versionierbare Analysten-Registry gefuehrt (fixture-/dateibasiert), getrennt von Live-Web-Recherche und getrennt von der Kernscore-Berechnung.

## PM-064 Evidenzkette pro Event-Eintrag (V4.3.2)
Jeder Registry-Eintrag fuehrt eine kompakte Evidenzkette (Quelle, Referenz, Confidence, erwartetes Wirkfenster), damit Peak-Zuordnungen reviewbar und dauerhaft reproduzierbar bleiben.

## PM-065 Gestuftes Peak-Event-Matching statt Binaerlogik (V4.3.2)
Peak-Event-Zuordnung erfolgt ueber eine nachvollziehbare Mehrfaktor-Heuristik (zeitliche Naehe, Fensterueberlappung, thematische Passung, Verlaufstyp, Peak-Support) und liefert gestufte Match-Klassen.

## PM-066 Match-Klassen mit expliziter Unsicherheit (V4.3.2)
Event-Alignment unterscheidet `direct_match`, `plausible_context_match`, `weak_match`, `no_credible_match`, `multi_event_overlap`; Unsicherheit bleibt sichtbar und wird nicht als Scheinvalidierung verborgen.

## PM-067 Ereignisgestuetzte Verlaufskommentierung (V4.3.2)
Jahresverlaeufe werden pro Land narrativ-kompakt kommentiert: welche Peaks eventnah gestuetzt sind, welche Phasen global mitlaufen und welche Phasen laenderspezifisch eigenstaendig erscheinen.

## PM-068 Event-Coverage- und Maturity-Diagnostik (V4.3.2)
Der Reviewpfad fuehrt globale und laenderspezifische Alignment-Qualitaetskennzahlen (credible/no-match/multi-overlap, country maturity), um starke vs. schwache Realweltabdeckung transparent zu machen.

## PM-069 Review-/Handout-/Bundle-Sichtbarkeit (V4.3.2)
Event-Registry, Peak-Event-Matches, Coverage-Summary, Country-Alignment und kompakte Review-Hinweise werden verpflichtend in Exporte, Handout und Acceptance-/Review-Bundle transportiert.

## PM-070 Analystenworkflow fuer Registry-Pflege (V4.3.2)
Registry-Pflege folgt einem expliziten Ablauf: Ereignisse erfassen, Evidenz dokumentieren, erwartete Peak-Fenster setzen, Match-Ergebnisse pruefen, Unsicherheiten markieren und versioniert einfrieren.

## PM-071 Additive Integration ohne Live-Web-Pflicht (V4.3.2)
V4.3.2 bleibt ein additiver Alignment-Block: bestehende V2.x-/V3.x-/V4.0-/V4.1-/V4.2-/V4.3-/V4.3.1-Pfade bleiben erhalten; keine verpflichtende externe Live-Recherche im Produktlauf.

### V4.3.1 Begriffsklaerung
- `global background stress`: laenderuebergreifend zeitnah auftretender, synchronisierter Belastungsanteil im Peak.
- `country-specific peak`: Peak mit ueberwiegend laenderspezifischem Anteil und eigenstaendiger Treiberlage.
- `event-supported peak`: Peak mit starker oder nachvollziehbarer eventnaher Marker-Unterstuetzung.
- `model-driven peak`: Peak mit hoher modellseitiger Intensitaet, aber schwacher externer Supportlage und hohem globalen Mitlaufanteil.
- `weakly supported peak`: Peak mit eingeschraenkter Supportbreite (wenige Gruppen, geringe Freshness oder schwacher Event-Support).
- `peak attribution`: explizite Zerlegung und Labelung eines Peaks nach Treibern, Supportprofil und global-vs-country-Anteil.
- `peak confidence`: kompakte Belastbarkeitsbewertung eines Peaks aus Supportbreite, Freshness, Dominanz, Event-Support und Synchronisationslast.

### V4.3.2 Begriffsklaerung
- `event registry`: versionierte, analystisch gepflegte Ereignisdatenbasis fuer Realwelt-Alignment.
- `event marker`: einzelner Registry-Eintrag mit Zeitfenster, Thema, Evidenz und erwarteter Wirkung.
- `candidate event`: Event-Marker, der fuer einen Peak im Matchingraum grundsaetzlich in Frage kommt.
- `linked event`: Event-Marker, der im Match-Ergebnis explizit einem Peak zugeordnet wurde.
- `peak-event match`: strukturierter Abgleich zwischen Peak und einem oder mehreren Event-Markern.
- `match confidence`: zusammengefasste Belastbarkeit der Peak-Event-Zuordnung auf `[0,1]`.
- `direct match`: hohe zeitliche/thematische Passung mit starker Evidenzlage.
- `contextual match`: plausible Kontextpassung ohne vollstaendige Direktpassung.
- `no credible match`: keine hinreichend belastbare Event-Zuordnung fuer den Peak.
- `multi-event phase`: Peak-Phase mit mehreren gleichzeitig plausiblen Event-Markern, die manuelle Review erfordert.
