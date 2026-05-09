# OpenIssues

Use this document for missing, unclear, or contradictory requirements.

## OI-001
- Issue ID: OI-001
- Betroffene Requirement IDs: PSR-002, PSyR-001, PSwR-002
- Problem: Inconsistent country naming (`Deutschland` vs `Germany`) is not explicitly normalized.
- Vorschlag: V1 defines canonical country names (`Iran`, `Israel`, `Germany`) and maps `Deutschland -> Germany` during loading.
- Blocker / Non-blocker: Non-blocker
- Status: open (V1 assumption accepted)

## OI-002
- Issue ID: OI-002
- Betroffene Requirement IDs: PSwR-003, PSwR-004, PSyR-005
- Problem: GDELT/UCDP input schema and ingestion mode are not specified (API vs snapshot files).
- Vorschlag: V1 uses CSV snapshots with mandatory fields `date`, `country`, `category|event_type`, `raw_value`; adapters validate fields.
- Blocker / Non-blocker: Non-blocker
- Status: open (V1 assumption accepted)

## OI-003
- Issue ID: OI-003
- Betroffene Requirement IDs: PSwR-007, PSwR-008, PSwR-009, PSwR-010, PSwR-011, ALG-001, ALG-002, ALG-003, ALG-004
- Problem: Feature/subscore formulas and weights are not defined quantitatively.
- Vorschlag: V1 uses transparent equal-weight aggregation within each cluster (arithmetic mean of validated subscores), documented as provisional.
- Blocker / Non-blocker: Non-blocker
- Status: open (V1 assumption accepted)

## OI-004
- Issue ID: OI-004
- Betroffene Requirement IDs: PSwR-012, PSwR-013, ALG-005, ALG-006
- Problem: Stage thresholds and trend boundaries are described qualitatively without numeric defaults.
- Vorschlag: V1 uses fixed defaults (`25/50/75` for stage, robust delta logic for 7d vs 30d trend) and marks them calibratable.
- Blocker / Non-blocker: Non-blocker
- Status: open (V1 assumption accepted)

## OI-005
- Issue ID: OI-005
- Betroffene Requirement IDs: PSwR-014, ALG-007
- Problem: Confidence components are listed but not quantified or weighted.
- Vorschlag: V1 computes confidence from data density, signal consistency, deviation strength, and source plausibility (all 0-100, weighted).
- Blocker / Non-blocker: Non-blocker
- Status: open (V1 assumption accepted)

## OI-006
- Issue ID: OI-006
- Betroffene Requirement IDs: PSyR-009, PSyR-010, ProtoRunbook
- Problem: Exact selection rule for "last run" and reference run artifacts is not specified.
- Vorschlag: V1 defines `outputs/runs/current_run` as the last run and stores the frozen reference in `outputs/reference/current_reference`.
- Blocker / Non-blocker: Non-blocker
- Status: open (V1 assumption accepted)

## OI-007
- Issue ID: OI-007
- Betroffene Requirement IDs: PSR-003, PSR-005, PSyR-006, PSyR-007, PSwR-016
- Problem: Handout/report format and required sections are not formally defined.
- Vorschlag: V1 produces a Markdown handout with trend plots, cluster tables, and short interpretations; exports are CSV/JSON.
- Blocker / Non-blocker: Non-blocker
- Status: open (V1 assumption accepted)

## OI-008
- Issue ID: OI-008
- Betroffene Requirement IDs: PSR-007, PSwR-017, PSyR-008
- Problem: Manual run-status override is required conceptually, but trigger mechanism and persistence schema are unspecified.
- Vorschlag: V1 uses optional environment variable `PROTO_RUN_STATUS_OVERRIDE` with strict value validation and stores both proposed and effective status in run metadata.
- Blocker / Non-blocker: Non-blocker
- Status: open (provisional V1 mechanism)

## OI-009
- Issue ID: OI-009
- Betroffene Requirement IDs: PSwR-002, PSyR-001, PSyR-002
- Problem: Required config-validation constraints (allowed country aliases, mandatory keys, boundary checks) are not defined in the requirements documents.
- Vorschlag: V1 will enforce minimal validation set (mandatory sections, integer windows > 0, required version keys, known country aliases) and mark stricter schema rules as future refinement.
- Blocker / Non-blocker: Non-blocker
- Status: open (provisional validation baseline)

## OI-010
- Issue ID: OI-010
- Betroffene Requirement IDs: PSwR-007, PSwR-008, ALG-001, ALG-002
- Problem: Bridge-uplift transfer function from `severity` to feature score is not specified (linear, capped, weighted by confidence, cluster-specific).
- Vorschlag: V1 keeps a simple provisional linear mapping `severity * 100`, clamped to 0-100, independent of country/cluster; calibration is deferred.
- Blocker / Non-blocker: Non-blocker
- Status: open (provisional feature-uplift rule)

## OI-011
- Issue ID: OI-011
- Betroffene Requirement IDs: PSwR-010, PSwR-011, PSwR-014, ALG-004, ALG-007
- Problem: Requirements do not define whether missing subscores should reduce cluster score or only confidence.
- Vorschlag: V1 computes cluster scores from available validated subscores and models missingness via confidence components (data density + source plausibility).
- Blocker / Non-blocker: Non-blocker
- Status: open (provisional missing-data handling)


## OI-014
- Issue ID: OI-014
- Betroffene Requirement IDs: PSR-008, PSR-010, PSyR-011, PSyR-012, PSyR-013, PSwR-020, PSwR-021, PSwR-022, PSwR-029, PSwR-030
- Problem: Historical Rolling Trend is not yet formalized as an official mandatory second result area of the standard run.
- Vorschlag: V2.2 defines `Current Snapshot` and `Historical Rolling Trend` as co-equal official result areas of the standard run with strictly separated artifacts.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v2_2 (implemented with separated snapshot/historical artifacts)

## OI-015
- Issue ID: OI-015
- Betroffene Requirement IDs: PSwR-024, PM-011
- Problem: The as-of-date rule for historical replay is now required conceptually, but exact source-specific availability semantics are not yet formally defined in code/config.
- Vorschlag: V2.2 introduces an explicit as-of-date evaluation path and documents per-source availability assumptions.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v2_2 (as-of-date enforced in historical rolling calculation)

## OI-016
- Issue ID: OI-016
- Betroffene Requirement IDs: PSwR-025, PSwR-026, PSwR-027, ALG-012
- Problem: Missing-day handling and rolling-window minimum coverage are now specified conceptually, but exact confidence penalty mapping is not yet quantified.
- Vorschlag: V2.2 introduces configurable `min_valid_days` and an explicit confidence penalty function for insufficient window coverage.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v2_2 (min_valid_days + explicit coverage-based confidence implemented)

## OI-017
- Issue ID: OI-017
- Betroffene Requirement IDs: PSwR-034, PM-013
- Problem: Bridge-file and context-table contributions are to be treated as time-constant in the Historical Rolling Trend, but this is a provisional simplification without historical source versioning.
- Vorschlag: V2.2 documents constant historical handling as provisional and defers full historical versioning to a later iteration.
- Blocker / Non-blocker: Non-blocker
- Status: open_v2_2

## OI-018
- Issue ID: OI-018
- Betroffene Requirement IDs: PSR-009, PSwR-029, PM-015
- Problem: Historical validation is desired, but no explicit curated event-layer is yet available for automatic event-to-peak interpretation.
- Vorschlag: V2.2 limits the handout to compact text plus fixed annual context metrics and records a future event-layer as dedicated follow-up work.
- Blocker / Non-blocker: Non-blocker
- Status: open_v2_2

## OI-019
- Issue ID: OI-019
- Betroffene Requirement IDs: PSyR-002, PSyR-014
- Problem: `PSyR-002` keeps 7d/30d/12m analysis windows while `PSyR-014` requires exactly one active historical rolling window per run. The relationship between these window concepts is not yet explicitly normalized in the requirement texts.
- Vorschlag: Keep 7d/30d/12m as legacy/base processing windows and treat `historical.window_days` as the single official rolling window for V2.2 output derivation. Document this as normative in upcoming requirement cleanup.
- Blocker / Non-blocker: Non-blocker
- Status: open_v2_2

## OI-020
- Issue ID: OI-020
- Betroffene Requirement IDs: PSwR-022, PSwR-026, PSwR-033
- Problem: If no historical point reaches `min_valid_days`, snapshot derivation from the last valid historical point becomes undefined.
- Vorschlag: Use the latest historical point with numeric rolling value (even below minimum coverage) and mark reduced confidence via coverage penalty; keep `kein_vergleich` trend for below-threshold points.
- Blocker / Non-blocker: Non-blocker
- Status: open_v2_2 (implemented as explicit fallback rule)

## OI-021
- Issue ID: OI-021
- Betroffene Requirement IDs: PSwR-022, PSwR-026, PSwR-033
- Problem: The first V2.2 output review shows that snapshot values can remain populated although the historical rolling end-point is not valid at run date. The exact normative status of this fallback is still not fully clarified in the requirements text.
- Vorschlag: Explicitly document whether snapshot output is allowed to use the latest numeric rolling point below full validity threshold and how this must be marked in handout and metadata.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v2_2_1
- Umsetzung V2.2.1:
  - Snapshot-Herkunft wird pro Land/Cluster explizit ausgewiesen (`historical_valid_endpoint`, `historical_latest_valid_before_run_date`, `historical_numeric_fallback_below_min_valid_days`, `raw_latest_fallback_no_historical_value`).
  - Bei `historical_numeric_fallback_below_min_valid_days` wird eine explizite zusätzliche Snapshot-Confidence-Reduktion angewendet.
  - Kennzeichnung erfolgt in:
    - `exports/snapshot/summary_export.json`
    - `exports/snapshot/snapshot_status.json`
    - Handout (`Snapshot-Herkunft`-Zeile je Cluster)

## OI-022
- Issue ID: OI-022
- Betroffene Requirement IDs: PSwR-009, PSwR-034, PM-013
- Problem: The first V2.2 output review shows that `vulnerability` currently behaves across all three countries as a near-constant structural/baseline cluster over the historical horizon.
- Vorschlag: Decide explicitly whether this is the intended model behavior for V2.2 or whether future iterations shall introduce time-varying historical inputs for vulnerability.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v2_2_1
- Umsetzung V2.2.1:
  - V2.2.1 ordnet `vulnerability` explizit als derzeit strukturellen Baseline-Cluster ein.
  - Technische Grundlage: `constant_clusters={"vulnerability"}` im Historical-Rolling-Pfad.
  - Sichtbare Kennzeichnung in:
    - `exports/historical/historical_status.json` (`constant_clusters`, `method_notes.vulnerability_cluster_role`)
    - Handout-Historical-Block (methodischer Baseline-Hinweis am Cluster)

## OI-023
- Issue ID: OI-023
- Betroffene Requirement IDs: PSwR-007, PSwR-010, PSwR-011
- Problem: The first V2.2 output review shows a strong `Germany / tension / protest_subscore` jump that dominates the cluster increase and should be checked for factual/data plausibility.
- Vorschlag: Review source data, feature scaling, and cluster contribution for the Germany tension protest path and document whether the magnitude is intended.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v2_2_1
- Umsetzung V2.2.1:
  - Befund: kein Implementierungsartefakt.
  - Der Sprung ist daten-/regelgetrieben:
    - GDELT `Germany/protest`: `28 -> 31`
    - Bridge-Marker `protest_marker` mit `severity=0.4` erzeugt per V1-Regel (`severity * 100`) einen Uplift von `+40`.
    - Ergebnis `protest_subscore`: `28 -> 71`.
  - Der Clusteranstieg ist durch transparente Mittelung erklärbar; der Protest-Teilpfad dominiert den Delta-Beitrag erwartungskonform.
  - Abgesichert durch Integrations-Test (`TV-PSwR-007-002`).

## OI-024
- Issue ID: OI-024
- Betroffene Requirement IDs: PSR-003, PSR-005, PSwR-016, PSwR-032
- Problem: The first V2.2 output review shows that yearly historical plots are functionally present but still partly hard to read; additionally, the handout still shows encoding/umlaut rendering problems.
- Vorschlag: Increase plot readability (size/layout/date-axis formatting) and normalize UTF-8/encoding handling in generated Markdown outputs.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v2_2_1
- Umsetzung V2.2.1:
  - Plots:
    - Snapshot `figsize=(11, 5.5)`, Historical Cluster `figsize=(14, 7)`, Historical Subscores `figsize=(16, 8)`.
    - Datumsachsen im Historical-Kontext mit AutoDateLocator/ConciseDateFormatter und verbesserter Tick-Dichte.
    - `tight_layout()` + `autofmt_xdate()` für bessere Beschriftungslesbarkeit.
  - Encoding:
    - Handout und kompakter Historical-Textreport werden mit UTF-8-BOM (`utf-8-sig`) geschrieben.
    - Umlaute in Handout-Texten sind normiert (z. B. `gültig`, `eingeschränkt`).

## OI-025
- Issue ID: OI-025
- Betroffene Requirement IDs: PSyR-018, PSwR-036, PSwR-037, PSwR-044
- Problem: V3.1 introduces a canonical observation schema, but the exact mandatory/optional field set and the minimal adapter contract still need normative text beyond the current design intention.
- Vorschlag: V3.1 defines a pragmatic canonical observation schema with explicit Pflichtfelder (`source_id`, `layer`, `signal_family`, `country`, `period_start`, `period_end`, `raw_value`, `normalized_value`, `unit`, `provenance`, `quality/completeness`) and keeps source-specific extension fields optional.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v3_1
- Umsetzung V3.1:
  - Kanonisches Observation-Schema implementiert (`proto/observations/models.py`, `proto/observations/schema.py`).
  - Adapter-Contract implementiert (`proto/observations/adapter_contract.py`).
  - Pflichtfelder und Validierungsregeln sind in Code und Tests explizit abgesichert.

## OI-026
- Issue ID: OI-026
- Betroffene Requirement IDs: PSwR-040, PSwR-041, PSwR-042, ALG-014, ALG-015
- Problem: The first V3.1 fusion MVP shall use transparent manual group/source weights, but exact default values remain provisional and should be documented as heuristic rather than validated.
- Vorschlag: V3.1 introduces explicit configurable default weights for source-level and group-level fusion and marks them as provisional heuristic defaults.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v4_0 (calibrated_with_explicit_validation_profile)
- Umsetzung V3.1:
  - Manuelle konfigurierbare Source-/Group-Weights sind aktiv im Fusion-Pfad.
  - Die Defaultwerte bleiben explizit heuristisch/provisorisch und sind nicht als kalibrierte Endwerte zu lesen.
- Umsetzung V4.0:
  - Fusion-Gewichte wurden anhand eines expliziten Validierungsrahmens nachgeschaerft und als Kalibrierprofil versioniert.
  - Ranking-/Dominanz-/Timing-Metriken sind als laufbegleitende Review-Kriterien operationalisiert.

## OI-027
- Issue ID: OI-027
- Betroffene Requirement IDs: PSyR-022, PSwR-038, PSwR-043, PM-022
- Problem: V3.1 allows multiple native temporal resolutions, but the exact target-period alignment rules for monthly, warning-style and trade/exposure sources still need a final normative wording.
- Vorschlag: V3.1 keeps native source periods in the canonical observation schema and defines explicit target-period aggregation rules in the fusion path.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v3_1
- Umsetzung V3.1:
  - Native Perioden bleiben pro Observation erhalten (`period_start`, `period_end`, `native_periodicity`).
  - Fusion arbeitet auf definierter Zielperiode (`target_period_days`) und waehlt je Quelle/Land den letzten gueltigen Punkt bis Run-Datum.

## OI-028
- Issue ID: OI-028
- Betroffene Requirement IDs: PSwR-042, ALG-016
- Problem: A cross-group reinforcement bonus is desired as an optional mechanism, but it should not be active by default before basic layer behavior is understood and reviewed.
- Vorschlag: V3.1 introduces the mechanism as configurable but disabled by default.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v3_1
- Umsetzung V3.1:
  - Bonusmechanismus im Fusion-Score implementiert, aber in der Standardkonfiguration deaktiviert.

## OI-029
- Issue ID: OI-029
- Betroffene Requirement IDs: PSR-012, PSyR-019, PSyR-020, PM-017, PM-023
- Problem: The overall V3 scope includes `Narrative`, `Shock`, `Displacement`, and future event-source expansion, but the first implementation block is intentionally focused on Food/Structural MVP and parallel architecture enablement.
- Vorschlag: V3.1 documents these layers as in-scope in the target architecture, while only `Market/Food` and `Structural` are required as first implemented MVP layers; `Narrative`, `Shock`, `Displacement`, and later `UCDP` extension remain staged follow-up integrations.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v3_3
- Umsetzung V3.2/V3.3:
  - V3.2: `Market/Food`, `Structural`, `Shock`, `Displacement` und `Narrative` liefern echte Gruppenscores.
  - V3.3: `Event` ist als realer Layer integriert und nicht mehr pauschal `not_available`.

## OI-030
- Issue ID: OI-030
- Betroffene Requirement IDs: PSR-019, PSwR-053
- Problem: Landbezogene Fusion-Plot-Einbindung im Handout war inkonsistent, obwohl Plotdateien physisch vorhanden waren.
- Vorschlag: Plot-Landzuordnung token-basiert robust machen und fuer Gesamt-/Laenderbloecke denselben Pfadbestand verwenden.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v3_1_1_and_v3_2
- Umsetzung V3.1.1/V3.2:
  - Landmapping fuer Plotdateien robust erweitert (`_plots_by_country`).
  - Handout referenziert vorhandene Fusion-Plotdateien konsistent in Gesamt- und Laenderbloeken.

## OI-031
- Issue ID: OI-031
- Betroffene Requirement IDs: PSyR-026, PSwR-061, PM-026
- Problem: Narrative-Input ist im V3.2-MVP strukturiert integriert, aber semantische Validierung (Topic-Taxonomie, Richtungslabel-Harmonisierung, Redaktionsprozess) bleibt methodisch offen.
- Vorschlag: V3.3 fuehrt ein kuratiertes Narrative-Validierungsprofil mit kontrollierten Labelsets und Review-Workflow ein.
- Blocker / Non-blocker: Non-blocker
- Status: open_v3_2_1 (calibration_hardened_semantic_validation_open)
- Umsetzung V3.2.1:
  - Narrative-Kalibrierung wurde technisch nachgeschaerft (globaler Normalisierungs-Scope + nicht-triviale Differenzierung zwischen Laendern).
  - Offener Restpunkt bleibt die semantische Label-/Taxonomie-Validierung des Narrative-Inputs.

## OI-032
- Issue ID: OI-032
- Betroffene Requirement IDs: PSyR-027, PSwR-056, PSwR-057, PM-024, PM-025
- Problem: Monatliche Zielperioden sind implementiert, aber langfristige Regeln fuer alternative Zielperioden (z. B. quartalsweise oder event-getriebene Fenster) sind noch nicht normativ festgelegt.
- Vorschlag: Zielperioden-Regeln in einem dedizierten Erweiterungsprofil (`monthly`/`quarterly`) normieren; V3.2 bleibt bewusst auf `monthly`.
- Blocker / Non-blocker: Non-blocker
- Status: open_v3_2_2 (implemented_with_provisional_scope)
- Umsetzung V3.2.1/V3.2.2:
  - Historische Layer-Abdeckung wird explizit ausgewiesen (`available_group_count`, `expected_group_count`, `available_group_ratio`).
  - Historische Niedrigabdeckung wird ueber nicht-blockierende Plausibilitaetswarnungen sichtbar gemacht (ab V3.2.2 konsolidiert als Summary-Warning).
  - Historische Total-Scores fuehren zusaetzlich `interpretation_status` sowie `no_material_change` fuer semantisch saubere Driver-Einordnung.
  - Alternative Zielperioden jenseits `monthly` bleiben methodisch offen.

## OI-033
- Issue ID: OI-033
- Betroffene Requirement IDs: PSyR-019, PSwR-068
- Problem: Die Gruppe `Event` ist im Zielmodell vorhanden, aber im V3.2-MVP weiterhin nicht tief befuellt.
- Vorschlag: Event-Layer als naechsten stufenweisen Ausbau mit klarer Quellenpriorisierung und eigenen Adaptern aufnehmen.
- Blocker / Non-blocker: Non-blocker
- Status: closed_v3_3
- Umsetzung V3.3:
  - Erste echte Event-Quelle integriert (`gdelt_event`).
  - Event-Observationen werden periodisiert und normalisiert in den Fusion-Pfad eingespeist.
  - Event wirkt in Snapshot- und Historical-Fusion (`group_scores`, `historical_group_scores`, `fusion_total_scores`, `historical_total_scores`).
  - Event erscheint in Explainability, Handout, Exporten und Plots.
  - Event-spezifische nicht-blockierende Plausibilitaetswarnungen sind aktiv.

## OI-034
- Issue ID: OI-034
- Betroffene Requirement IDs: PSyR-029, PSwR-071, PSwR-072, PM-032, PM-033
- Problem: V3.3 integriert den Event-Layer mit einer ersten echten Quelle, aber die Robustheit gegen source-spezifische Biases bleibt bei Ein-Quellen-Eventbetrieb begrenzt.
- Vorschlag: In einem Folgeblock mindestens eine zweite komplementaere Event-Quelle (z. B. UCDP-Event-Adapter im Fusion-Raum) integrieren und gegen `gdelt_event` cross-checken.
- Blocker / Non-blocker: Non-blocker
- Status: open_v3_3

## OI-035
- Issue ID: OI-035
- Betroffene Requirement IDs: PSR-021, PSyR-030, PSwR-076, PSwR-077, PM-036, PM-037
- Problem: Referenzepisoden sind in V4.0 bewusst analystennahe Review-Anker und kein formal gelabelter Ground Truth; inter-analystische Konsistenzregeln sind noch nicht normiert.
- Vorschlag: Fuer einen Folgeblock ein kuratiertes Review-Protokoll (Doppelreview, Konfliktauflösung, Episoden-Freeze-Regeln) als Validierungsgovernance ergänzen.
- Blocker / Non-blocker: Non-blocker
- Status: open_v4_0

## OI-036
- Issue ID: OI-036
- Betroffene Requirement IDs: PSwR-079, PSwR-082, PM-039, PM-040
- Problem: V4.0 markiert stale Event-Signale und geringe fruehe Layer-Abdeckung transparent, kann diese Datenluecken methodisch aber nicht vollständig kompensieren.
- Vorschlag: Event-Quelle erweitern (zweite Quelle) und historisierte Layer-Abdeckung in einem Folgeblock vertiefen; bis dahin Warn-/Interpretationshinweise verpflichtend beibehalten.
- Blocker / Non-blocker: Non-blocker
- Status: open_v4_1 (partially_mitigated_by_operational_freshness_logic)

## OI-037
- Issue ID: OI-037
- Betroffene Requirement IDs: PSR-022, PSyR-032, PSyR-033, PSwR-083, PSwR-086, PSwR-089
- Problem: V4.1 verbessert die Freshness-/Responsiveness-Logik methodisch, aber operative Frische bleibt durch reale Update-Latenz einzelner Quellen begrenzt (insbesondere Event bei laenger ausbleibenden neuen Datenpunkten).
- Vorschlag: In einem Folgeblock ein schlankes operatives Refresh-Protokoll (staleness SLA je Quelle, ingestion health checks, optional second event source) einfuehren, ohne den Scope in Richtung unkontrollierter Quellenausweitung zu verschieben.
- Blocker / Non-blocker: Non-blocker
- Status: open_v4_1

## OI-038
- Issue ID: OI-038
- Betroffene Requirement IDs: PSR-023, PSyR-034, PSyR-035, PSwR-091, PSwR-095
- Problem: V4.2 fuehrt Governance als eigenstaendigen Layer ein, nutzt im MVP aber einen einzelnen strukturierten Governance-Inputpfad. Damit bleibt die externe Triangulation gegen alternative Governance-Quellen/Methoden begrenzt.
- Vorschlag: In einem Folgeblock ein schlankes Governance-Reviewprotokoll mit Cross-Checks (mindestens zweite Referenzperspektive oder kuratierte Experten-Doppelreview-Regeln) einfuehren, ohne den Scope in unkontrollierte Quellenausweitung zu treiben.
- Blocker / Non-blocker: Non-blocker
- Status: open_v4_2

## OI-039
- Issue ID: OI-039
- Betroffene Requirement IDs: PSR-024, PSyR-037, PSwR-098, PSwR-100, PM-053, PM-054
- Problem: V4.3 erweitert den Vergleich auf 10 Laender mit vollstaendigen 356-Tage-Profilen, aber die länderübergreifende Vergleichbarkeit bleibt methodisch durch heterogene Datenfrische und unterschiedliche Quellabdeckung partiell eingeschraenkt.
- Vorschlag: In einem Folgeblock ein schlankes Vergleichbarkeits-Protokoll einfuehren (coverage-/freshness-adjusted comparison labels, optionale robuste Normalisierungschecks), ohne den Scope in eine neue Grossmethodik auszuweiten.
- Blocker / Non-blocker: Non-blocker
- Status: open_v4_3

## OI-040
- Issue ID: OI-040
- Betroffene Requirement IDs: PSR-025, PSyR-040, PSwR-109, PSwR-110, PM-059, PM-060
- Problem: V4.3.1 fuehrt Peak-Attribution und Event-Alignment robust ein, aber Event-Support basiert im MVP auf einer analystischen Marker-Registry und nicht auf einer formal kuratierten, extern validierten Event-Ground-Truth-Pipeline.
- Vorschlag: In einem Folgeblock ein leichtgewichtiges Event-Alignment-Governance-Protokoll definieren (Marker-Pflegeprozess, Doppelreview-Regeln, Freeze-Versionierung, Konfliktaufloesung), ohne den Produktcode um verpflichtende Live-Web-Recherche zu erweitern.
- Blocker / Non-blocker: Non-blocker
- Status: open_v4_3_1

## OI-041
- Issue ID: OI-041
- Betroffene Requirement IDs: PSR-026, PSyR-041, PSyR-043, PSwR-113, PSwR-118, PSwR-120, PM-064, PM-068, PM-070
- Problem: V4.3.2 etabliert einen belastbaren Registry-/Alignment-Pfad, aber inter-analystische Konsistenzregeln fuer Registry-Pflege, Evidence-Confidence-Kalibrierung und Review-Freeze-Zyklen sind noch nicht voll formalisiert.
- Vorschlag: In einem Folgeblock ein schlankes Registry-Governance-Protokoll definieren (Pflege-Rollen, minimale Evidenzstandards je `source_category`, Delta-Review bei Registry-Aenderungen, periodischer Freeze), ohne den Scope in verpflichtende Live-Recherche oder neue Grossarchitektur auszuweiten.
- Blocker / Non-blocker: Non-blocker
- Status: open_v4_3_2

## OI-042
- Issue ID: OI-042
- Betroffene Requirement IDs: Frontend handoff AP-04, AP-05, AP-08, AP-10
- Problem: Das neue Frontend-MVP benoetigt stabile API-Endpunkte fuer Overview-/Run-Detail-/Artifact-Daten. Diese sind im aktuellen Integrationsstand nicht in jeder Umgebung garantiert verfuegbar.
- Vorschlag: Frontend nutzt bis zur API-Vollabdeckung eine zentrale API-Fallback-Schicht im Client (keine verteilten Seiten-Mocks), markiert als MVP-Zwischenzustand.
- Blocker / Non-blocker: Non-blocker
- Status: open_frontend_phase_1

## OI-043
- Issue ID: OI-043
- Betroffene Requirement IDs: Frontend handoff AP-01, AP-04, AP-06, AP-07, AP-08, AP-10, AP-11
- Problem: Phase-2-Seiten (Country Detail, Compare, Coverage, Artifacts) benoetigen spezialisierte Aggregatendpunkte. Diese sind im aktuellen Integrationsstand nicht durchgaengig als stabile Verträge verfuegbar.
- Vorschlag: API-Client bleibt API-first, nutzt aber klar dokumentierte derive-pfade aus stabilen Kernendpunkten (`overview`, `runs`, `options`) mit zentralen Fallback-Records, bis dedizierte Endpunkte verbindlich bereitstehen.
- Blocker / Non-blocker: Non-blocker
- Status: open_frontend_phase_2

## OI-044
- Issue ID: OI-044
- Betroffene Requirement IDs: Backend API MVP AP-04, AP-08
- Problem: Die neue FastAPI-MVP-Schicht deckt den Run-Lifecycle stabil ab, aber dedizierte Analysten-Endpunkte (`/overview`, `/countries/*`, `/compare`, `/coverage`, `/artifacts`) sind im Backend noch nicht als verbindliche API-Vertraege umgesetzt.
- Vorschlag: In einem Folgeblock die spezialisierten Read-Model-Endpunkte backendseitig ergaenzen, damit Frontend-Derive-Pfade schrittweise entfallen koennen.
- Blocker / Non-blocker: Non-blocker
- Status: open_backend_api_mvp
