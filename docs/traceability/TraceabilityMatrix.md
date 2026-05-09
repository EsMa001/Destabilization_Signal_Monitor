# TraceabilityMatrix

| Requirement ID | Description | Method / Algorithm | Code Module | Test File / TV-ID | Status |
|---|---|---|---|---|---|
| PSR-001 | Prototype goal | PM-001 | `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSR-002 | Target countries | PM-002 | `proto/common.py`, `proto/reporting/presentation.py`, `proto/pipeline/config.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSR-003 | Readability/presentability | PM-001 | `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSR-004 | Explainability | PM-006 | `proto/scoring/subscores.py`, `proto/scoring/cluster_scores.py`, `proto/reporting/summary_text.py` | `tests/test_scoring.py` (`TV-PSwR-010-001`, `TV-PSwR-011-002`) | implemented |
| PSR-005 | Time-series plots in handout | PM-005 | `proto/reporting/plots.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSR-006 | Comparable country structure | PM-002 | `proto/reporting/handout.py`, `proto/reporting/presentation.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSR-007 | Run rating | ALG-008 | `proto/runs/status.py`, `proto/pipeline/run_proto.py` | `tests/test_runs.py` (`TV-PSwR-017-001`, `TV-PSwR-017-002`), `tests/test_pipeline.py` (`TV-PSwR-017-003`) | implemented |
| PSyR-001 | Country scope | PM-002 | `proto/common.py`, `proto/reporting/presentation.py`, `proto/pipeline/config.py` | `tests/test_config.py` (`TV-PSwR-002-001`, `TV-PSwR-002-002`, `TV-PSwR-002-005`) | implemented |
| PSyR-002 | Windows 7d/30d/12m | PM-005 | `config/default.yaml`, `proto/pipeline/config.py`, `proto/scoring/trend.py` | `tests/test_config.py` (`TV-PSwR-002-001`, `TV-PSwR-002-004`), `tests/test_scoring.py` (`TV-PSwR-013-001`) | implemented |
| PSyR-003 | Cluster generation | PM-001 | `proto/features/*.py`, `proto/scoring/*.py` | `tests/test_features.py` (`TV-PSwR-007-001`, `TV-PSwR-008-001`, `TV-PSwR-009-001`), `tests/test_integration_processing.py` (`TV-PSwR-001-INT-001`) | implemented |
| PSyR-004 | Internal/external escalation split | ALG-002 | `proto/features/escalation_features.py` | `tests/test_features.py` (`TV-PSwR-008-001`) | implemented |
| PSyR-005 | Core source set | PM-003 | `proto/sources/*.py` | `tests/test_sources.py` (`TV-PSwR-003-001`, `TV-PSwR-004-001`, `TV-PSwR-005-001`, `TV-PSwR-006-001`) | implemented |
| PSyR-006 | Report/handout generation | PM-001 | `proto/reporting/handout.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSyR-007 | Structured exports | PM-001 | `proto/reporting/exports.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSyR-008 | Run metadata | PM-001 | `proto/runs/models.py`, `proto/runs/metadata.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSyR-009 | Run comparison | ProtoRunbook | `proto/runs/compare_runs.py` | `tests/test_runs.py` (`TV-PSyR-009-001`) | implemented |
| PSyR-010 | Reference run | ProtoRunbook | `proto/runs/reference.py` | `tests/test_runs.py` (`TV-PSyR-010-001`) | implemented |
| PSwR-001 | Separation raw/features/scores/presentation | PM-001 | `proto/sources/*`, `proto/features/*`, `proto/scoring/*`, `proto/reporting/*`, `proto/pipeline/*` | `tests/test_sources.py`, `tests/test_features.py`, `tests/test_scoring.py`, `tests/test_integration_processing.py` (`TV-PSwR-001-INT-001`) | implemented |
| PSwR-002 | Standard V1 config | PM-006 | `config/default.yaml`, `proto/pipeline/config.py` | `tests/test_config.py` (`TV-PSwR-002-001`, `TV-PSwR-002-002`, `TV-PSwR-002-003`, `TV-PSwR-002-004`, `TV-PSwR-002-005`) | implemented |
| PSwR-003 | GDELT loader | PM-003 | `proto/sources/gdelt.py` | `tests/test_sources.py` (`TV-PSwR-003-001`) | implemented |
| PSwR-004 | UCDP loader | PM-003 | `proto/sources/ucdp.py` | `tests/test_sources.py` (`TV-PSwR-004-001`) | implemented |
| PSwR-005 | Bridge loader | PM-003 | `proto/sources/bridge.py` | `tests/test_sources.py` (`TV-PSwR-005-001`) | implemented |
| PSwR-006 | Context loader | PM-003 | `proto/sources/context.py` | `tests/test_sources.py` (`TV-PSwR-006-001`) | implemented |
| PSwR-007 | Tension features | ALG-001 | `proto/features/gdelt_features.py` | `tests/test_features.py` (`TV-PSwR-007-001`) | implemented |
| PSwR-008 | Escalation features | ALG-002 | `proto/features/escalation_features.py` | `tests/test_features.py` (`TV-PSwR-008-001`) | implemented |
| PSwR-009 | Vulnerability features | ALG-003 | `proto/features/vulnerability_features.py` | `tests/test_features.py` (`TV-PSwR-009-001`) | implemented |
| PSwR-010 | 3-5 subscores per cluster | ALG-001, ALG-002, ALG-003 | `proto/scoring/subscores.py` | `tests/test_scoring.py` (`TV-PSwR-010-001`), `tests/test_integration_processing.py` (`TV-PSwR-010-INT-001`) | implemented |
| PSwR-011 | Cluster scores | ALG-004 | `proto/scoring/cluster_scores.py` | `tests/test_scoring.py` (`TV-PSwR-011-001`, `TV-PSwR-011-002`) | implemented |
| PSwR-012 | Stage mapping | ALG-005 | `proto/scoring/thresholds.py` | `tests/test_scoring.py` (`TV-PSwR-012-001`) | implemented |
| PSwR-013 | Trend mapping | ALG-006 | `proto/scoring/trend.py` | `tests/test_scoring.py` (`TV-PSwR-013-001`) | implemented |
| PSwR-014 | Confidence score + level | ALG-007 | `proto/scoring/confidence.py` | `tests/test_scoring.py` (`TV-PSwR-014-001`, `TV-PSwR-014-002`) | implemented |
| PSwR-015 | Short interpretation texts | PM-006 | `proto/reporting/summary_text.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSwR-016 | Plots | PM-005 | `proto/reporting/plots.py` | `tests/test_pipeline.py` (`TV-PSyR-006-001`) | implemented |
| PSwR-017 | Run status | ALG-008 | `proto/runs/status.py`, `proto/pipeline/run_proto.py` | `tests/test_runs.py` (`TV-PSwR-017-001`, `TV-PSwR-017-002`), `tests/test_pipeline.py` (`TV-PSwR-017-003`) | implemented |
| PSwR-018 | Automated tests for core processing stages | TestStrategy | `tests/*.py` | `python -m pytest` (unit + integration + e2e) | implemented |
| PSwR-019 | Traceability links in code/tests | AGENTS.md conventions | `proto/**/*.py`, `tests/**/*.py` | manual review required + `python -m pytest` | implemented |

| PSR-008 | Dual standard view | PM-008 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSR-009 | Annual context in snapshot | PM-014, PM-015 | `proto/scoring/trend_history.py`, `proto/reporting/handout.py` | `tests/test_scoring.py` (`TV-PSwR-033-001`), `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSR-010 | Historical validation capability | PM-015 | `proto/pipeline/run_proto.py`, `proto/reporting/plots.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSR-011 | Strict result separation | PM-008, PM-014 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSyR-011 | Current Snapshot result area | PM-008, PM-010 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSyR-012 | Historical Rolling Trend result area | PM-008, PM-009 | `proto/scoring/trend_history.py`, `proto/pipeline/run_proto.py`, `proto/reporting/plots.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSyR-013 | Historical horizon 365d | PM-009 | `proto/pipeline/config.py`, `config/default.yaml` | `tests/test_config.py` (`TV-PSwR-002-001`) | implemented |
| PSyR-014 | One active rolling window per run | PM-009 | `proto/pipeline/config.py`, `config/default.yaml` | `tests/test_config.py` (`TV-PSwR-021-001`) | implemented |
| PSyR-015 | Historical annual block + daily data | PM-014 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`, `TV-PSwR-031-002`) | implemented |
| PSyR-016 | Separate snapshot/trend artifacts | PM-014 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSyR-017 | Explicit limited-usable trend marking | PM-014 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-017-001`) | implemented |
| PSwR-020 | Daily rolling base values | PM-009 | `proto/scoring/subscores.py`, `proto/scoring/cluster_scores.py`, `proto/scoring/trend_history.py` | `tests/test_scoring.py` (`TV-PSwR-021-002`) | implemented |
| PSwR-021 | Rolling aggregation | ALG-009 | `proto/scoring/trend_history.py`, `proto/pipeline/run_proto.py` | `tests/test_config.py` (`TV-PSwR-021-001`), `tests/test_scoring.py` (`TV-PSwR-021-002`) | implemented |
| PSwR-022 | Shared snapshot logic | PM-010 | `proto/pipeline/run_proto.py`, `proto/scoring/trend_history.py` | `tests/test_scoring.py` (`TV-PSwR-022-001`), `tests/test_pipeline.py` (`TV-PSwR-022-002`) | implemented |
| PSwR-023 | Historical derived stage/trend/confidence | ALG-010, ALG-011, ALG-012 | `proto/scoring/trend_history.py`, `proto/scoring/confidence.py` | `tests/test_scoring.py` (`TV-PSwR-021-002`, `TV-PSwR-027-001`) | implemented |
| PSwR-024 | As-of-date rule | PM-011 | `proto/scoring/trend_history.py` | `tests/test_scoring.py` (`TV-PSwR-024-001`) | implemented |
| PSwR-025 | Missing-day handling | PM-012 | `proto/scoring/trend_history.py` | `tests/test_scoring.py` (`TV-PSwR-021-002`) | implemented |
| PSwR-026 | Minimum coverage | PM-012 | `config/default.yaml`, `proto/pipeline/config.py`, `proto/scoring/trend_history.py` | `tests/test_config.py` (`TV-PSwR-026-001`), `tests/test_scoring.py` (`TV-PSwR-021-002`) | implemented |
| PSwR-027 | Coverage impact on confidence | ALG-012 | `proto/scoring/confidence.py`, `proto/scoring/trend_history.py` | `tests/test_scoring.py` (`TV-PSwR-027-001`) | implemented |
| PSwR-028 | Historical trend comparison | ALG-011 | `proto/scoring/trend_history.py` | `tests/test_scoring.py` (`TV-PSwR-021-002`) | implemented |
| PSwR-029 | Historical mandatory artifacts | PM-014, PM-015 | `proto/pipeline/run_proto.py`, `proto/reporting/plots.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`, `TV-PSyR-017-001`) | implemented |
| PSwR-030 | Historical shared time-series file | PM-014 | `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSwR-031 | Optional compact daily reports | PM-014 | `proto/pipeline/config.py`, `proto/pipeline/run_proto.py` | `tests/test_config.py` (`TV-PSwR-031-001`), `tests/test_pipeline.py` (`TV-PSwR-031-002`) | implemented |
| PSwR-032 | Historical plot structure | PM-014 | `proto/reporting/plots.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSwR-033 | Snapshot annual context metrics | PM-014, PM-015 | `proto/scoring/trend_history.py`, `proto/reporting/handout.py` | `tests/test_scoring.py` (`TV-PSwR-033-001`), `tests/test_pipeline.py` (`TV-PSyR-012-001`) | implemented |
| PSwR-034 | Constant historical helper sources | PM-013 | `proto/scoring/trend_history.py`, `proto/pipeline/run_proto.py` | `tests/test_scoring.py` (`TV-PSwR-034-001`) | implemented_with_provisional_scope |
| PSwR-035 | Parametric historical target countries | PM-002, PM-009 | `config/default.yaml`, `proto/pipeline/config.py` | `tests/test_config.py` (`TV-PSwR-035-001`) | implemented |

| PSR-012 | Multi-source architecture | PM-016, PM-017 | `proto/observations/*`, `proto/fusion/*`, `proto/pipeline/run_proto.py` | `tests/test_observations.py`, `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSR-013 | Parallel fusion path | PM-020, PM-021 | `proto/fusion/*`, `proto/pipeline/run_proto.py`, `proto/reporting/*` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented_with_provisional_scope |
| PSR-014 | Provenance of new sources | PM-016, PM-022 | `proto/observations/*`, `proto/sources/*`, `proto/reporting/*` | `tests/test_observations.py`, `tests/test_pipeline.py` | implemented |
| PSR-015 | First visible Market/Food value | PM-017, PM-020 | `proto/sources/fao_ffpi.py`, `proto/sources/fao_fpma.py`, `proto/fusion/*`, `proto/reporting/*` | `tests/test_sources.py`, `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSyR-018 | Canonical observations | PM-016 | `proto/observations/*`, `proto/sources/*` | `tests/test_observations.py`, `tests/test_sources.py` | implemented |
| PSyR-019 | Layer/group view | PM-017 | `proto/fusion/*`, `proto/reporting/*` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSyR-020 | Parallel fusion path | PM-020, PM-021 | `proto/fusion/*`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSyR-021 | V3.1 MVP sources | PM-016, PM-018 | `proto/sources/fao_ffpi.py`, `proto/sources/fao_fpma.py`, `proto/sources/un_comtrade.py` | `tests/test_sources.py` | implemented |
| PSyR-022 | Mixed native periods | PM-022 | `proto/observations/*`, `proto/fusion/*` | `tests/test_observations.py`, `tests/test_fusion.py` | implemented |
| PSwR-036 | Canonical observation schema | PM-016 | `proto/observations/*` | `tests/test_observations.py` | implemented |
| PSwR-037 | Observation mandatory fields | PM-016 | `proto/observations/*`, `proto/sources/*` | `tests/test_observations.py`, `tests/test_sources.py` | implemented |
| PSwR-038 | Mixed native periods in observations | PM-022 | `proto/observations/*` | `tests/test_observations.py` | implemented |
| PSwR-039 | Adapter contract | PM-016, PM-018 | `proto/sources/*`, `proto/observations/*` | `tests/test_sources.py`, `tests/test_observations.py` | implemented |
| PSwR-040 | Source-specific normalization | PM-018, ALG-013 | `proto/observations/*`, `proto/sources/unhcr.py`, `proto/sources/narrative_input.py`, `proto/pipeline/config.py`, `config/default.yaml` | `tests/test_config.py` (`TV-PSwR-040-001`, `TV-PSwR-040-003`), `tests/test_observations.py` (`TV-PSwR-040-002`), `tests/test_sources.py` | implemented_with_provisional_scope |
| PSwR-041 | Group fusion | PM-019, ALG-014 | `proto/fusion/*` | `tests/test_fusion.py` | implemented_with_provisional_scope |
| PSwR-042 | Fusion total score | PM-020, ALG-015, ALG-016 | `proto/fusion/*`, `config/default.yaml` | `tests/test_fusion.py`, `tests/test_config.py` | implemented_with_provisional_scope |
| PSwR-043 | Target periods for fusion | PM-022 | `proto/fusion/*`, `proto/observations/*` | `tests/test_fusion.py`, `tests/test_observations.py` | implemented |
| PSwR-044 | Observation provenance | PM-016, PM-022 | `proto/observations/*`, `proto/sources/*`, `proto/reporting/*` | `tests/test_observations.py`, `tests/test_pipeline.py` | implemented |
| PSwR-045 | Fusion confidence | PM-021, ALG-017 | `proto/fusion/confidence.py`, `proto/fusion/scoring.py` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented_with_provisional_scope |
| PSwR-046 | Group scores | PM-019, ALG-014 | `proto/fusion/*` | `tests/test_fusion.py` | implemented_with_provisional_scope |
| PSwR-047 | Parallel run path | PM-020 | `proto/pipeline/run_proto.py`, `proto/reporting/*` | `tests/test_pipeline.py` | implemented |
| PSwR-048 | FAO FFPI loader | PM-016, PM-018 | `proto/sources/fao_ffpi.py` | `tests/test_sources.py` | implemented |
| PSwR-049 | FAO FPMA loader | PM-016, PM-018 | `proto/sources/fao_fpma.py` | `tests/test_sources.py` | implemented |
| PSwR-050 | UN Comtrade loader | PM-016, PM-018 | `proto/sources/un_comtrade.py` | `tests/test_sources.py` | implemented |
| PSwR-051 | Fusion artifacts | PM-020, PM-021 | `proto/reporting/exports.py`, `proto/reporting/handout.py`, `proto/reporting/plots.py` | `tests/test_pipeline.py` | implemented |
| PSwR-052 | Keep cluster view | PM-017, PM-020 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` | implemented |
| PSR-016 | Historical fusion result area | PM-024, PM-030 | `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSR-017 | Expanded layer coverage in V3.2 | PM-026, PM-027 | `proto/sources/gdacs.py`, `proto/sources/unhcr.py`, `proto/sources/narrative_input.py`, `proto/fusion/*` | `tests/test_sources.py`, `tests/test_pipeline.py` | implemented_with_provisional_scope |
| PSR-018 | Time-aware historical fusion with drivers | PM-028, PM-029 | `proto/fusion/scoring.py`, `proto/reporting/handout.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSR-019 | Consistent fusion plot embedding | PM-030 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` | implemented |
| PSR-020 | Operational Event layer | PM-032, PM-033, PM-034 | `proto/sources/gdelt_event.py`, `proto/fusion/*`, `proto/pipeline/run_proto.py`, `proto/reporting/*` | `tests/test_sources.py`, `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSyR-023 | Historical fusion path | PM-024, PM-029 | `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSyR-024 | GDACS shock integration | PM-026, ALG-018 | `proto/sources/gdacs.py`, `config/default.yaml` | `tests/test_sources.py`, `tests/test_pipeline.py` | implemented |
| PSyR-025 | UNHCR displacement integration | PM-026, ALG-019 | `proto/sources/unhcr.py`, `config/default.yaml` | `tests/test_sources.py`, `tests/test_pipeline.py` | implemented |
| PSyR-026 | Narrative input integration | PM-026, ALG-020 | `proto/sources/narrative_input.py`, `config/default.yaml` | `tests/test_sources.py`, `tests/test_observations.py`, `tests/test_pipeline.py` | implemented_with_provisional_scope |
| PSyR-027 | Monthly historical fusion target periods | PM-024, PM-025 | `proto/fusion/scoring.py`, `proto/pipeline/config.py` | `tests/test_fusion.py`, `tests/test_config.py` | implemented |
| PSyR-028 | V3.2 historical fusion reporting | PM-030 | `proto/reporting/handout.py`, `proto/reporting/plots.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` | implemented |
| PSyR-029 | Event-layer integration in fusion path | PM-032, PM-033 | `proto/sources/gdelt_event.py`, `proto/pipeline/run_proto.py`, `proto/fusion/scoring.py` | `tests/test_sources.py`, `tests/test_pipeline.py` | implemented |
| PSwR-053 | Consistent fusion country-plot mapping | PM-030 | `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-053-001`, `TV-PSwR-053-002`) | implemented |
| PSwR-054 | Extended V3.x source config validation | PM-024, PM-026 | `proto/pipeline/config.py`, `config/default.yaml` | `tests/test_config.py` (`TV-PSwR-054-001`) | implemented |
| PSwR-055 | Narrative input schema support | PM-026 | `proto/sources/narrative_input.py` | `tests/test_sources.py` (`TV-PSwR-061-001`) | implemented |
| PSwR-056 | Historical monthly period generation | PM-024 | `proto/fusion/scoring.py` | `tests/test_fusion.py` (`TV-PSwR-056-002`) | implemented |
| PSwR-057 | Historical source signal export | PM-025 | `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-057-001`) | implemented |
| PSwR-058 | Group status semantics (`ok/limited/not_available`) | PM-027 | `proto/fusion/scoring.py` | `tests/test_fusion.py` (`TV-PSwR-058-001`), `tests/test_pipeline.py` (`TV-PSwR-058-002`) | implemented |
| PSwR-059 | GDACS loader | PM-026, ALG-018 | `proto/sources/gdacs.py` | `tests/test_sources.py` (`TV-PSwR-059-001`) | implemented |
| PSwR-060 | UNHCR loader | PM-026, ALG-019 | `proto/sources/unhcr.py` | `tests/test_sources.py` (`TV-PSwR-060-001`, `TV-PSwR-060-002`) | implemented |
| PSwR-061 | Narrative input loader | PM-026, ALG-020 | `proto/sources/narrative_input.py` | `tests/test_sources.py` (`TV-PSwR-061-001`, `TV-PSwR-061-002`) | implemented_with_provisional_scope |
| PSwR-062 | Historical fusion group scores | PM-029, ALG-021 | `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSwR-063 | Historical fusion total scores | PM-029, ALG-021 | `proto/fusion/models.py`, `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSwR-064 | Historical dominant-driver hints | PM-028, ALG-022 | `proto/fusion/scoring.py`, `proto/reporting/handout.py` | `tests/test_fusion.py` (`TV-PSwR-064-001`, `TV-PSwR-064-002`), `tests/test_pipeline.py` | implemented |
| PSwR-065 | Historical fusion plots (global + country) | PM-030 | `proto/reporting/plots.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-065-001`) | implemented |
| PSwR-066 | Historical fusion handout section | PM-030 | `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-066-001`, `TV-PSwR-066-002`) | implemented |
| PSwR-067 | Additive compatibility to V2.x/V3.1 | PM-031 | `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` | implemented |
| PSwR-068 | Event group explicit not_available marker | PM-027 | `config/default.yaml`, `proto/fusion/scoring.py` | `tests/test_pipeline.py` | implemented_with_provisional_scope |
| PSwR-069 | Fusion status includes historical counts | PM-030 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-069-001`, `TV-PSwR-069-002`) | implemented |
| PSwR-070 | Bonus default remains disabled in historical path | PM-029, ALG-016 | `config/default.yaml`, `proto/fusion/scoring.py` | `tests/test_fusion.py` | implemented |
| PSwR-071 | GDELT event adapter | PM-032, ALG-023 | `proto/sources/gdelt_event.py`, `config/default.yaml`, `proto/pipeline/config.py` | `tests/test_sources.py` (`TV-PSwR-071-001`), `tests/test_observations.py` (`TV-PSwR-071-002`) | implemented |
| PSwR-072 | Event periodization + normalization | PM-033, ALG-024 | `proto/sources/gdelt_event.py`, `proto/observations/*` | `tests/test_sources.py` (`TV-PSwR-072-001`) | implemented |
| PSwR-073 | Event effectiveness in snapshot/historical fusion | PM-034, ALG-022 | `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py`, `config/default.yaml` | `tests/test_fusion.py` (`TV-PSwR-073-001`), `tests/test_pipeline.py` | implemented |
| PSwR-074 | Event-specific plausibility warnings | PM-034 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` | implemented |
| PSR-021 | External validation and calibration | PM-035, PM-038 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_fusion.py`, `tests/test_pipeline.py` | implemented |
| PSyR-030 | Validation framework with reference episodes | PM-035, PM-036 | `data/validation/reference_episodes.csv`, `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-077-001`), `tests/test_pipeline.py` (`TV-PSwR-080-001`) | implemented |
| PSyR-031 | Validation status in review artifacts | PM-041 | `proto/pipeline/run_proto.py`, `tools/create_review_bundle.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-080-001`, `TV-PSwR-080-002`) | implemented |
| PSwR-075 | Exportable validation framework | PM-035 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-080-001`) | implemented |
| PSwR-076 | Versioned reference episode path | PM-036 | `data/validation/reference_episodes.csv`, `proto/fusion/validation.py` | `tests/test_pipeline.py` (`TV-PSwR-080-001`) | implemented |
| PSwR-077 | Episode/ranking validation metrics | PM-037, ALG-025, ALG-026 | `proto/fusion/validation.py` | `tests/test_fusion.py` (`TV-PSwR-077-001`) | implemented |
| PSwR-078 | Fusion calibration profile | PM-038, ALG-028 | `config/default.yaml`, `proto/pipeline/config.py`, `proto/pipeline/run_proto.py` | `tests/test_config.py` (`TV-PSwR-078-001`) | implemented |
| PSwR-079 | Event recency/stale handling in score path | PM-039, ALG-028 | `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py`, `config/default.yaml` | `tests/test_fusion.py` (`TV-PSwR-079-002`), `tests/test_config.py` (`TV-PSwR-079-001`) | implemented |
| PSwR-080 | Validation summary in status/review bundle | PM-041 | `proto/pipeline/run_proto.py`, `tools/create_review_bundle.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-080-001`, `TV-PSwR-080-002`) | implemented |
| PSwR-081 | Analyst-friendly layer diagnostics | PM-041, ALG-027 | `proto/fusion/validation.py`, `proto/reporting/handout.py` | `tests/test_fusion.py` (`TV-PSwR-081-001`), `tests/test_pipeline.py` (`TV-PSwR-080-001`) | implemented |
| PSwR-082 | Historical validation helper artifacts | PM-040 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-080-001`) | implemented |
| PSR-022 | Operational freshness and responsiveness | PM-046, PM-048 | `proto/fusion/freshness.py`, `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-085-002`) | implemented |
| PSyR-032 | Freshness/staleness control for dynamic layers | PM-042, PM-043 | `proto/fusion/freshness.py`, `proto/fusion/scoring.py`, `proto/pipeline/config.py` | `tests/test_fusion.py` (`TV-PSwR-083-001`), `tests/test_config.py` (`TV-PSwR-083-002`) | implemented |
| PSyR-033 | Operational responsiveness view in review path | PM-046, PM-048 | `proto/fusion/validation.py`, `proto/reporting/handout.py`, `tools/create_review_bundle.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-085-002`) | implemented |
| PSwR-083 | Explicit freshness/staleness model | PM-042, ALG-029 | `proto/fusion/freshness.py`, `proto/pipeline/config.py`, `config/default.yaml` | `tests/test_fusion.py` (`TV-PSwR-083-001`), `tests/test_config.py` (`TV-PSwR-083-002`) | implemented |
| PSwR-084 | Recency/decay effect for dynamic layers | PM-043, ALG-029 | `proto/fusion/scoring.py`, `config/default.yaml` | `tests/test_fusion.py` (`TV-PSwR-083-001`) | implemented |
| PSwR-085 | Snapshot freshness diagnostics | PM-046, ALG-030 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-085-001`), `tests/test_pipeline.py` (`TV-PSwR-085-002`) | implemented |
| PSwR-086 | Historical responsiveness metrics | PM-045, ALG-031 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-086-001`) | implemented |
| PSwR-087 | Freshness-sensitive confidence hardening | PM-044, ALG-029 | `proto/fusion/scoring.py` | `tests/test_fusion.py` (`TV-PSwR-083-001`) | implemented |
| PSwR-088 | V4.1 calibration parameters in config | PM-044 | `proto/pipeline/config.py`, `config/default.yaml` | `tests/test_config.py` (`TV-PSwR-083-002`) | implemented |
| PSwR-089 | Operational warnings and review hints | PM-047, ALG-032 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-085-002`) | implemented |
| PSwR-090 | V4.1 view in handout and bundle | PM-048, ALG-032 | `proto/reporting/handout.py`, `tools/create_review_bundle.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-085-002`, `TV-PSwR-080-002`) | implemented |
| PSR-023 | Governance and political stability dimension | PM-049, PM-051, ALG-034 | `proto/sources/governance_input.py`, `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_fusion.py` (`TV-PSwR-093-001`), `tests/test_pipeline.py` (`TV-PSwR-096-001`) | implemented |
| PSyR-034 | Governance layer in canonical fusion path | PM-049, PM-050 | `proto/sources/governance_input.py`, `proto/observations/schema.py`, `proto/pipeline/config.py`, `proto/pipeline/run_proto.py` | `tests/test_sources.py` (`TV-PSwR-091-001`), `tests/test_observations.py` (`TV-PSwR-091-002`), `tests/test_fusion.py` (`TV-PSwR-093-001`) | implemented |
| PSyR-035 | Governance view in validation/review artifacts | PM-051, ALG-035 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py`, `tools/create_review_bundle.py` | `tests/test_fusion.py` (`TV-PSwR-094-001`), `tests/test_pipeline.py` (`TV-PSwR-096-001`) | implemented |
| PSwR-091 | Governance source/adapter contract | PM-050, ALG-033 | `proto/sources/governance_input.py`, `config/default.yaml`, `proto/pipeline/config.py` | `tests/test_sources.py` (`TV-PSwR-091-001`), `tests/test_observations.py` (`TV-PSwR-091-002`) | implemented |
| PSwR-092 | Governance normalization | PM-050, ALG-033 | `proto/sources/governance_input.py`, `config/default.yaml` | `tests/test_sources.py` (`TV-PSwR-091-001`) | implemented |
| PSwR-093 | Governance effectiveness in snapshot/historical fusion | PM-050, ALG-034 | `proto/fusion/scoring.py`, `proto/pipeline/run_proto.py`, `config/default.yaml` | `tests/test_fusion.py` (`TV-PSwR-093-001`), `tests/test_pipeline.py` (`TV-PSwR-095-001`) | implemented |
| PSwR-094 | Governance diagnostics/warnings/confidence hints | PM-051, ALG-035 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_fusion.py` (`TV-PSwR-094-001`), `tests/test_pipeline.py` (`TV-PSwR-095-001`) | implemented |
| PSwR-095 | Governance validation/reference-episode extension | PM-051, ALG-035 | `data/validation/reference_episodes.csv`, `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-095-001`) | implemented |
| PSwR-096 | Governance visibility in handout/acceptance/review-bundle | PM-051 | `proto/reporting/handout.py`, `proto/pipeline/run_proto.py`, `tools/create_review_bundle.py` | `tests/test_pipeline.py` (`TV-PSwR-096-001`, `TV-PSwR-096-002`, `TV-PSwR-080-002`) | implemented |
| PSR-024 | Comparative expansion to 10 countries with full 356-day profiles | PM-052, PM-053, PM-055 | `config/default.yaml`, `proto/pipeline/config.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSyR-036 | Fixed 10-country comparative scope | PM-052 | `config/default.yaml`, `proto/common.py`, `proto/pipeline/config.py`, `proto/reporting/presentation.py` | `tests/test_config.py`, `tests/test_pipeline.py` | implemented |
| PSyR-037 | Full 356-day profiles for all countries | PM-053 | `proto/fusion/scoring.py`, `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-098-001`), `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSyR-038 | Comparative diagnostics + equal-depth reporting | PM-054, PM-055 | `proto/fusion/validation.py`, `proto/reporting/handout.py`, `proto/reporting/plots.py` | `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSwR-097 | Enforced 10-country configuration | PM-052 | `config/default.yaml`, `proto/pipeline/config.py` | `tests/test_config.py` | implemented |
| PSwR-098 | 356-day country profile metrics export | PM-053, ALG-036, ALG-040 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-098-001`), `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSwR-099 | Compact main comparison table | PM-054, ALG-036 | `proto/fusion/validation.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSwR-100 | Deep diagnostic tables (peaks/group profiles) | PM-054, ALG-037, ALG-038 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_fusion.py` (`TV-PSwR-098-001`), `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSwR-101 | Per-country V4.3 profile plots | PM-054 | `proto/reporting/plots.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSwR-102 | Cross-country comparison plots + ranking trajectory | PM-054, ALG-039 | `proto/reporting/plots.py`, `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-098-001`), `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSwR-103 | Handout global-first comparative structure | PM-055 | `proto/reporting/handout.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-098-002`) | implemented |
| PSwR-104 | V4.3 comparative data in acceptance/review bundle | PM-055, PM-056 | `tools/create_review_bundle.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-096-002`, `TV-PSwR-098-002`) | implemented |
| PSR-025 | Peak attribution and event alignment hardening | PM-057, PM-058, PM-059 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_fusion.py` (`TV-PSwR-105-001`), `tests/test_pipeline.py` (`TV-PSwR-107-001`) | implemented |
| PSyR-039 | Peak attribution in 10-country trajectory space | PM-057, PM-060, PM-061 | `proto/fusion/validation.py`, `proto/reporting/exports.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-105-001`), `tests/test_pipeline.py` (`TV-PSwR-108-001`) | implemented |
| PSyR-040 | Event alignment and synchronization view in review path | PM-059, PM-062 | `proto/fusion/validation.py`, `tools/create_review_bundle.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-112-001`) | implemented |
| PSwR-105 | Hardened peak detection in annual trajectory | PM-057, ALG-041 | `proto/fusion/validation.py` | `tests/test_fusion.py` (`TV-PSwR-105-001`) | implemented |
| PSwR-106 | Calibrated peak attribution/support config space | PM-060, ALG-043 | `proto/pipeline/config.py`, `config/default.yaml` | `tests/test_config.py` (`TV-PSwR-106-001`) | implemented |
| PSwR-107 | Global-vs-country peak decomposition | PM-058, ALG-042 | `proto/fusion/validation.py` | `tests/test_fusion.py` (`TV-PSwR-105-001`), `tests/test_pipeline.py` (`TV-PSwR-107-001`) | implemented |
| PSwR-108 | Peak attribution artifacts | PM-058, PM-060, ALG-043, ALG-045 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/exports.py` | `tests/test_pipeline.py` (`TV-PSwR-108-001`) | implemented |
| PSwR-109 | Event marker registry and peak-event support matching | PM-059, ALG-044 | `data/validation/event_marker_registry.csv`, `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-105-001`), `tests/test_pipeline.py` (`TV-PSwR-109-001`) | implemented |
| PSwR-110 | Peak confidence and trajectory profile diagnostics | PM-060, PM-061, ALG-045, ALG-046 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-105-001`) | implemented |
| PSwR-111 | Handout and plot visibility for attribution/synchronization | PM-061, PM-062, ALG-047 | `proto/reporting/handout.py`, `proto/reporting/plots.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-111-001`) | implemented |
| PSwR-112 | V4.3.1 artifacts in acceptance/review bundle | PM-062 | `tools/create_review_bundle.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-112-001`) | implemented |
| PSR-026 | Analyst event registry and real-world alignment | PM-063, PM-069, PM-071 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py`, `tools/create_review_bundle.py` | `tests/test_pipeline.py` (`TV-PSwR-113-001`, `TV-PSwR-120-001`, `TV-PSwR-123-001`, `TV-PSwR-124-001`) | implemented |
| PSyR-041 | Structured event-registry review path | PM-063, PM-064, ALG-048 | `data/validation/event_registry.csv`, `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-113-001`, `TV-PSwR-114-001`) | implemented |
| PSyR-042 | Staged peak-event matching | PM-065, PM-066, ALG-049, ALG-050, ALG-051 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-115-001`, `TV-PSwR-116-001`, `TV-PSwR-118-001`), `tests/test_pipeline.py` (`TV-PSwR-115-001`, `TV-PSwR-116-001`) | implemented |
| PSyR-043 | Event-alignment diagnostics and review artifacts | PM-068, PM-069, ALG-052, ALG-053, ALG-054 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py`, `tools/create_review_bundle.py` | `tests/test_pipeline.py` (`TV-PSwR-117-001`, `TV-PSwR-119-001`, `TV-PSwR-120-001`, `TV-PSwR-121-001`) | implemented |
| PSwR-113 | Event registry data model | PM-064, ALG-048 | `data/validation/event_registry.csv`, `proto/fusion/validation.py` | `tests/test_pipeline.py` (`TV-PSwR-113-001`) | implemented |
| PSwR-114 | Initial 10-country registry fixture | PM-063, PM-070 | `data/validation/event_registry.csv`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-114-001`) | implemented |
| PSwR-115 | Peak-event matching export | PM-065, ALG-050 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-115-001`), `tests/test_pipeline.py` (`TV-PSwR-115-001`) | implemented |
| PSwR-116 | Event-alignment match classes | PM-066, ALG-051 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-116-001`), `tests/test_pipeline.py` (`TV-PSwR-116-001`) | implemented |
| PSwR-117 | Country event-alignment maturity | PM-068, ALG-053 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py`, `proto/reporting/handout.py` | `tests/test_pipeline.py` (`TV-PSwR-117-001`) | implemented |
| PSwR-118 | Event coverage diagnostics | PM-068, ALG-052 | `proto/fusion/validation.py`, `proto/pipeline/run_proto.py` | `tests/test_fusion.py` (`TV-PSwR-118-001`), `tests/test_pipeline.py` (`TV-PSwR-118-001`) | implemented |
| PSwR-119 | Event-alignment review file | PM-069, ALG-054 | `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-119-001`) | implemented |
| PSwR-120 | V4.3.2 artifacts in acceptance/review bundle | PM-069 | `tools/create_review_bundle.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-120-001`) | implemented |
| PSwR-121 | Event-alignment plot support | PM-069, ALG-056 | `proto/reporting/plots.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-121-001`) | implemented |
| PSwR-122 | V4.3.2 calibration parameters in config | PM-071, ALG-051 | `config/default.yaml`, `proto/pipeline/config.py` | `tests/test_config.py` (`TV-PSwR-122-001`, `TV-PSwR-122-002`) | implemented |
| PSwR-123 | Event-alignment view in handout | PM-067, PM-069, ALG-055 | `proto/reporting/handout.py`, `proto/pipeline/run_proto.py` | `tests/test_pipeline.py` (`TV-PSwR-123-001`) | implemented |
| PSwR-124 | Additive V4.3.2 integration without regression | PM-071 | `proto/pipeline/run_proto.py`, `proto/reporting/handout.py`, `tools/create_review_bundle.py` | `tests/test_pipeline.py` (`TV-PSwR-124-001`) | implemented |

## Frontend Phase 1 Traceability (AP Scope)

| Work Package | Description | Code Module | Test File | Status |
|---|---|---|---|---|
| AP-01 | Frontend structure completion | `frontend/src/app/*`, `frontend/src/features/*`, `frontend/src/components/*` | `frontend/tests/app-shell.test.tsx` | implemented |
| AP-02 | App shell (sidebar/topbar/workspace) | `frontend/src/components/layout/AppShell.tsx`, `SidebarNav.tsx`, `TopBar.tsx` | `frontend/tests/app-shell.test.tsx` | implemented |
| AP-03 | Design system baseline (dark/clean/panels/badges) | `frontend/src/styles/globals.css`, `frontend/src/components/ui/*` | `frontend/tests/app-shell.test.tsx` | implemented |
| AP-04 | Typed API client layer (health/runs/options/artifacts) | `frontend/src/lib/api/client.ts`, `fallback.ts`, `frontend/src/types/api.ts` | `frontend/tests/run-builder-submit.test.tsx`, `frontend/tests/run-monitor.test.tsx` | implemented_with_fallback_scope |
| AP-05 | Overview MVP structure | `frontend/src/features/overview/OverviewPage.tsx`, `frontend/src/app/page.tsx` | manual review marker | implemented |
| AP-06 | Run Builder MVP | `frontend/src/features/runs/RunBuilderForm.tsx`, `frontend/src/app/runs/new/page.tsx` | `frontend/tests/run-builder-submit.test.tsx` | implemented |
| AP-07 | Run Monitor MVP (polling) | `frontend/src/features/runs/RunMonitorTable.tsx`, `frontend/src/app/runs/page.tsx` | `frontend/tests/run-monitor.test.tsx` | implemented |
| AP-08 | Run Detail MVP | `frontend/src/features/runs/RunDetailView.tsx`, `frontend/src/app/runs/[runId]/page.tsx` | manual review marker | implemented |
| AP-09 | Country Detail MVP + toggle | `frontend/src/features/countries/CountryDetailView.tsx`, `frontend/src/app/countries/[countryCode]/page.tsx` | `frontend/tests/country-detail-toggle.test.tsx` | implemented |
| AP-10 | Robust states (loading/empty/error/partial) | `frontend/src/components/ui/StateCard.tsx`, core feature screens | manual review marker | implemented |
| AP-11 | Frontend checks and tests | `frontend/package.json`, `frontend/tests/*`, `frontend/vitest.config.ts` | `frontend/tests/*` | implemented_with_environment_limit |

## Frontend Phase 2 Traceability (AP Scope)

| Work Package | Description | Code Module | Test File | Status |
|---|---|---|---|---|
| AP-01 | API↔Frontend mapping hardening | `frontend/src/lib/api/client.ts`, `frontend/src/types/api.ts`, `frontend/src/lib/api/fallback.ts`, `frontend/README.md` | `frontend/tests/overview-states.test.tsx` | implemented_with_api_gap_constraints |
| AP-02 | Overview real-data strengthening | `frontend/src/features/overview/OverviewPage.tsx`, `frontend/src/components/ui/KpiCard.tsx` | `frontend/tests/overview-states.test.tsx`, manual review marker | implemented |
| AP-03 | Interactive world map component | `frontend/src/components/map/InteractiveWorldMap.tsx`, `frontend/src/features/overview/OverviewPage.tsx` | `frontend/tests/interactive-world-map.test.tsx` | implemented |
| AP-04 | Country Detail hardening | `frontend/src/features/countries/CountryDetailView.tsx`, `frontend/src/components/charts/TrendLineChart.tsx` | `frontend/tests/country-detail-toggle.test.tsx`, manual review marker | implemented |
| AP-05 | Trend/chart baseline expansion | `frontend/src/components/charts/TrendLineChart.tsx`, `frontend/src/features/countries/CountryDetailView.tsx`, `frontend/src/features/compare/CompareView.tsx` | `frontend/tests/compare-view.test.tsx`, manual review marker | implemented |
| AP-06 | Compare view operationalization | `frontend/src/features/compare/CompareView.tsx`, `frontend/src/app/compare/page.tsx` | `frontend/tests/compare-view.test.tsx` | implemented |
| AP-07 | Coverage/Data Status expansion | `frontend/src/features/coverage/CoverageView.tsx`, `frontend/src/components/coverage/CoverageTable.tsx`, `frontend/src/app/coverage/page.tsx` | `frontend/tests/coverage-view.test.tsx` | implemented |
| AP-08 | Artifacts/Reports expansion | `frontend/src/features/artifacts/ArtifactsView.tsx`, `frontend/src/components/artifacts/ArtifactList.tsx`, `frontend/src/app/artifacts/page.tsx` | `frontend/tests/artifacts-view.test.tsx` | implemented |
| AP-09 | Reusable component strengthening | `frontend/src/components/ui/KpiCard.tsx`, `frontend/src/components/ui/SectionHeader.tsx`, `frontend/src/components/charts/TrendLineChart.tsx`, `frontend/src/components/coverage/CoverageTable.tsx`, `frontend/src/components/artifacts/ArtifactList.tsx` | manual review marker | implemented |
| AP-10 | State/error hardening across pages | `frontend/src/features/overview/*`, `frontend/src/features/countries/*`, `frontend/src/features/compare/*`, `frontend/src/features/coverage/*`, `frontend/src/features/artifacts/*` | `frontend/tests/overview-states.test.tsx` | implemented |
| AP-11 | Frontend documentation update | `frontend/README.md`, `frontend/design/frontend_design_handoff.md`, `IMPLEMENT.md` | manual review marker | implemented |
| AP-12 | Tests and verification extension | `frontend/tests/*`, `frontend/package.json` | `frontend/tests/interactive-world-map.test.tsx`, `frontend/tests/compare-view.test.tsx`, `frontend/tests/coverage-view.test.tsx`, `frontend/tests/artifacts-view.test.tsx`, `frontend/tests/overview-states.test.tsx` | implemented_with_environment_limit |

## Frontend Phase 3 Traceability (AP Scope)

| Work Package | Description | Code Module | Test File | Status |
|---|---|---|---|---|
| AP-01 | End-to-end workflow hardening | `frontend/src/features/overview/OverviewPage.tsx`, `frontend/src/features/runs/RunBuilderForm.tsx`, `frontend/src/features/runs/RunMonitorTable.tsx`, `frontend/src/features/runs/RunDetailView.tsx`, `frontend/src/features/countries/CountryDetailView.tsx` | manual review marker | implemented |
| AP-02 | Navigation and routing polish | `frontend/src/components/ui/PageHeader.tsx`, `frontend/src/components/layout/TopBar.tsx`, `frontend/src/components/layout/SidebarNav.tsx` | `frontend/tests/page-header.test.tsx`, `frontend/tests/app-shell.test.tsx` | implemented |
| AP-03 | Overview UX refinement | `frontend/src/features/overview/OverviewPage.tsx`, `frontend/src/components/map/InteractiveWorldMap.tsx` | `frontend/tests/interactive-world-map.test.tsx`, `frontend/tests/overview-states.test.tsx` | implemented |
| AP-04 | Country Detail UX hardening | `frontend/src/features/countries/CountryDetailView.tsx` | `frontend/tests/country-detail-toggle.test.tsx`, manual review marker | implemented |
| AP-05 | Charting depth increase | `frontend/src/components/charts/TrendLineChart.tsx`, `frontend/src/features/countries/CountryDetailView.tsx`, `frontend/src/features/compare/CompareView.tsx` | `frontend/tests/trend-line-chart.test.tsx`, `frontend/tests/compare-view.test.tsx` | implemented |
| AP-06 | Compare UX expansion | `frontend/src/features/compare/CompareView.tsx` | `frontend/tests/compare-view.test.tsx` | implemented |
| AP-07 | Coverage/Artifacts UX expansion | `frontend/src/features/coverage/CoverageView.tsx`, `frontend/src/components/coverage/CoverageTable.tsx`, `frontend/src/features/artifacts/ArtifactsView.tsx`, `frontend/src/components/artifacts/ArtifactList.tsx` | `frontend/tests/coverage-view.test.tsx`, `frontend/tests/artifacts-view.test.tsx` | implemented |
| AP-08 | Professional state logic | `frontend/src/components/ui/StateCard.tsx`, `frontend/src/features/runs/RunDetailView.tsx`, `frontend/src/features/compare/CompareView.tsx`, `frontend/src/features/coverage/CoverageView.tsx` | `frontend/tests/overview-states.test.tsx`, `frontend/tests/country-detail-toggle.test.tsx` | implemented |
| AP-09 | Reusable UX components strengthening | `frontend/src/components/ui/PageHeader.tsx`, `frontend/src/components/ui/StateCard.tsx`, `frontend/src/components/charts/TrendLineChart.tsx`, `frontend/src/components/coverage/CoverageTable.tsx`, `frontend/src/components/artifacts/ArtifactList.tsx` | `frontend/tests/page-header.test.tsx`, `frontend/tests/trend-line-chart.test.tsx` | implemented |
| AP-10 | Frontend docs and rest-point update | `frontend/README.md`, `frontend/design/frontend_design_handoff.md`, `IMPLEMENT.md` | manual review marker | implemented |
| AP-11 | Tests and verification extension | `frontend/tests/*`, `frontend/package.json` | `frontend/tests/page-header.test.tsx`, `frontend/tests/trend-line-chart.test.tsx`, `frontend/tests/compare-view.test.tsx`, `frontend/tests/coverage-view.test.tsx`, `frontend/tests/artifacts-view.test.tsx` | implemented_with_environment_limit |
