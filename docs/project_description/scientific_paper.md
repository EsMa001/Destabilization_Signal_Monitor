# Country Destabilization Prototype: ein requirements-getriebener Multi-Source-Monitor fuer kurzfristige Destabilisierungssignale

**Autor:** Projektstand auf Branch `hermes/vmodel-assessment`, automatisiert aus Repository-Artefakten abgeleitet  
**Projekt:** `Country Destabilization Prototype V1/V2.3 Baseline + V4.3.2 Event-Alignment Expansion`

## Abstract

Dieses Paper beschreibt den aktuellen Stand eines requirements-getrieben entwickelten Prototyps zur Identifikation kurzfristiger politischer und gesellschaftlicher Destabilisierungssignale. Das System verarbeitet Medien-, Ereignis-, Kontext-, Markt-, Displacement-, Governance- und Narrative-Daten fuer einen konfigurierbaren Laenderraum und erzeugt daraus erklaerbare Risikoindikatoren. Methodisch kombiniert der Prototyp einen klassischen Clusterpfad fuer Spannung, Eskalation und strukturelle Verwundbarkeit mit einem additiven V3+-Multi-Source-Fusionpfad. Der Clusterpfad verdichtet Features ueber Subscores zu Cluster-Scores, leitet Stufen, Trends und Confidence ab und erzeugt Snapshot- sowie Historical-Rolling-Trend-Artefakte. Der Fusionpfad normalisiert heterogene Quellen in ein kanonisches Observation-Schema, bildet Gruppenwerte fuer `event`, `narrative`, `governance`, `market_food`, `shock`, `displacement` und `structural` und berechnet daraus einen separaten Fusion-Gesamtscore mit eigenstaendiger Confidence. Die Entwicklung wird durch eine V-Model-Light-/Requirements-as-Code-Governance abgesichert: 26 Stakeholder-, 43 System- und 124 Softwareanforderungen sind in YAML migriert; 156 Verifikationsartefakte und 2462 Function-Level-Trace-Links dokumentieren den Zusammenhang zwischen Anforderungen, Algorithmen, Code und Tests. Der aktuelle Stand ist ein fortgeschrittener, aber bewusst heuristischer Analyseprototyp; offene Punkte liegen insbesondere in methodischer Kalibrierung, Daten-/Event-Governance, semantischer Narrative-Governance und Ausbau spezialisierter API-/Frontend-Endpunkte.

## 1. Einleitung und Motivation

Politische und gesellschaftliche Destabilisierung entsteht selten aus einem einzelnen isolierten Signal. Medienaufmerksamkeit, Protestdynamik, Gewaltintensitaet, wirtschaftliche Verwundbarkeit, Governance-Fragilitaet, Displacement, Schockereignisse und Expertennarrative wirken in unterschiedlicher zeitlicher Aufloesung zusammen. Fuer Analysten entsteht daraus ein klassisches System-Engineering-Problem: heterogene, teilweise unsichere Quellen muessen reproduzierbar in nachvollziehbare Indikatoren ueberfuehrt werden, ohne die Bewertungslogik in eine Black Box zu verschieben.

Der Country Destabilization Prototype adressiert dieses Problem als erklaerbares, requirements-getriebenes Softwaresystem. Das Ziel ist nicht ein operatives Vollsystem und auch keine probabilistische Vorhersage im engeren Sinne, sondern ein reviewbarer Monitor, der kurzfristige Auffaelligkeiten sichtbar macht, Quellen- und Confidence-Kontext ausweist und manuelle Analyseentscheidungen vorbereitet. Der Prototyp arbeitet aktuell mit einer konfigurierten Standardbasis von zehn Laendern: Germany, Israel, Iran, Ukraine, Russia, Japan, China, Taiwan, Poland und Nigeria. Historische Sichtweisen nutzen 7-Tage-Rolling-Window-Logik, 30-Tage-Vergleiche, monatliche Fusionshistorie und 356-Tage-Jahresprofile.

## 2. Systemuebersicht

Abbildung 1 zeigt die Hauptarchitektur. Die Software trennt Rohdaten, Features/Observations, Scores, Reporting und Governance. Die zentrale Laufsteuerung liegt in `proto/pipeline/run_proto.py`; Datenmodelle, Quellenadapter, Feature-Builders, Scoring, Fusion, Validation, Reporting und Run-Management sind in separaten Python-Packages gekapselt. Ein FastAPI-MVP stellt Health-, Options-, Run-, Status- und Artifact-Endpunkte bereit.

![Projektarchitektur](diagrams/architecture_overview.svg)

Der klassische Ergebnisraum berechnet drei Cluster: gesellschaftlich-politische Spannung, gewaltsame Eskalation und strukturelle/systemische Verwundbarkeit. Parallel dazu erzeugt der V3+-Pfad eine Multi-Source-Fusion mit sieben Gruppen. Beide Ergebnisraeume bleiben bewusst nebeneinander bestehen: Der Clusterpfad bietet Kontinuitaet und einfache Interpretierbarkeit, der Fusionpfad erweitert die Quellbreite und fuehrt Validierungs- und Event-Alignment-Diagnostik ein.

Abbildung 2 zeigt die Abbildung der Quellen auf den Fusionsraum. Besonders wichtig ist, dass die neuen Quellen nicht direkt auf den Gesamtscore wirken, sondern immer zuerst in ein kanonisches Observation-Schema ueberfuehrt werden. Dadurch bleiben Herkunft, Zeitbezug und Qualitaetsinformation entlang der Verarbeitung sichtbar.

![Quellen-zu-Layer-Mapping](diagrams/source_to_layer_mapping.svg)

## 3. Methodischer Ansatz

Die mathematische Grundhaltung ist bewusst einfach und reviewbar. Im Clusterpfad werden Featurewerte auf eine Skala von 0 bis 100 geklemmt. Subscores entstehen aus Mittelwerten thematisch zusammengehoeriger Features. Ein Cluster-Score ist der einfache Mittelwert der zugeordneten Subscores:

\[
C_{c,k,t} = \frac{1}{n_k}\sum_{j=1}^{n_k} S_{c,k,j,t}, \quad C \in [0,100]
\]

Dabei bezeichnet `c` ein Land, `k` einen Cluster und `t` den Bewertungszeitpunkt. Stufen werden ueber konfigurierbare Schwellen abgeleitet. Der aktuelle Standardwertsatz nutzt `low_max=30`, `elevated_max=56` und `high_max=80`. Trends entstehen aus einem robusten Vergleich zwischen aktuellem 7-Tage-Mittel und einem 30-Tage-Baseline-Segment:

\[
\Delta_{c,k,t} = \overline{C}_{7d} - \overline{C}_{baseline},
\]

wobei `delta_epsilon=1.25` eine neutrale Zone definiert. Positive Deltas groesser als Epsilon werden als zunehmend, negative Deltas kleiner als minus Epsilon als ruecklaeufig, sonst als stabil klassifiziert.

Im Fusionpfad werden heterogene Quellen zunaechst in kanonische Beobachtungen ueberfuehrt. Jede Beobachtung besitzt Land, Quelle, Layer, Zeitraum, Rohwert, normalisierten Wert, Einheit, Provenance und Quality-Completeness. Gruppenwerte entstehen als gewichtete Mittel normalisierter Quellsignale, optional angepasst durch Freshness-/Decay-Faktoren:

\[
G_{c,g,t} = 100 \cdot \frac{\sum_i w_i s_{i,c,g,t} d_{i,c,g,t}}{\sum_i w_i}
\]

Der Fusion-Gesamtscore ist wiederum eine gewichtete Aggregation verfuegbarer Gruppen:

\[
F_{c,t} = \frac{\sum_g W_g G_{c,g,t}}{\sum_g W_g}.
\]

Score und Confidence werden getrennt gefuehrt. Die Gruppen-Confidence kombiniert Quellenabdeckung, Aktualitaet, Vollstaendigkeit und Konsistenz. Die Total-Confidence aggregiert diese Komponenten und reduziert Confidence bei starker Dominanz einzelner Gruppen oder hohem `limited`-Anteil. Dadurch bleibt ein hoher Score ohne gute Datengrundlage sichtbar als methodisch unsicher markiert.

![Mathematische Modellstruktur](diagrams/mathematical_model.svg)

## 4. Programmablauf und Artefakte

Ein Standardlauf laedt zunaechst Konfiguration und Quellen, erzeugt Features und kanonische Observations, berechnet Scores und schreibt anschliessend Exporte, Plots, Run-Metadaten, Status, Vergleichsartefakte und Handout. Die Pipeline erzeugt mehrere Ergebnisraeume: Snapshot, Historical Rolling Trend, Fusion Snapshot, historische Monatsfusion, V4.3-Laenderprofile, Peak-Hardening, Event-Alignment und Review-Queues.

![Programmablauf](diagrams/program_flow.svg)

Die wichtigsten Ausgaben liegen unter `outputs/runs/current_run/`: strukturierte CSV-/JSON-Exporte, Plots, `handout.md`, Run-Metadaten, Run-Vergleich und Referenzvergleich. Review-Bundles und Acceptance-Snapshots unterstuetzen manuelle Abnahme und Engineering-Governance.

## 5. Requirements- und Verifikationsstand

Das Projekt ist nicht nur ein Analyseprototyp, sondern auch ein Beispiel fuer Requirements-as-Code. Die migrierte V-Model-Light-Struktur unter `vmodel/` bildet Anforderungen, Testspezifikationen, Open Issues und Traceability maschinenlesbar ab. Aktuell existieren 26 Stakeholder Requirements, 43 System Requirements, 124 Software Requirements, 156 implementierte Verifikationsartefakte und 2462 funktionsbasierte Trace-Links. Von den Softwareanforderungen sind 123 als implementiert und eine als retired klassifiziert. Die letzte verifizierte Testsuite bestand mit 120 bestandenen Tests.

![V-Model Traceability](diagrams/vmodel_traceability.svg)

Diese Governance ist fuer den Projektcharakter wesentlich: Der Prototyp entwickelt sich schnell, aber jede zentrale Funktion, jeder Test und jedes methodische Element soll auf Requirements, Algorithmen, Method Rules oder Open Issues zurueckfuehrbar bleiben.

## 6. Diskussion und aktueller Reifegrad

Der aktuelle Stand ist ein technisch weit ausgebauter, lokal lauffaehiger und stark tracebarer Prototyp. Seine Staerken liegen in modularer Architektur, erklaerbarer Heuristik, getrennten Confidence-Pfaden, reichhaltigen Exporten, Event-Alignment-Diagnostik und formalisierter Governance. Gleichzeitig bleibt das System methodisch ein MVP: Gewichte, Schwellen, Event-Registry, Narrative-Semantik und Validierungsmetriken sind transparent, aber noch nicht empirisch abschliessend kalibriert. Die Ergebnisse sind daher als strukturierte analytische Hinweise zu verstehen, nicht als autonome Entscheidung oder belastbare Prognose.

## 7. Schlussfolgerung

Der Country Destabilization Prototype demonstriert, wie ein politisch-gesellschaftlicher Risikoindikator als requirements-getriebenes, erklaerbares Analysesystem aufgebaut werden kann. Die Verbindung aus klassischem Clusterpfad, Multi-Source-Fusion, historischer Diagnostik, Event-Alignment und V-Model-Light-Governance schafft eine belastbare Grundlage fuer weitere Forschung und Engineering-Arbeit. Die naechsten Entwicklungsschritte sollten auf methodische Kalibrierung, Datenqualitaet, semantische Governance, API-/Frontend-Produktisierung und reproduzierbare Evaluationsdaten fokussieren.
