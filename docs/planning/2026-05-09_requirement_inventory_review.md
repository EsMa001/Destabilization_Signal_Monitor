# Requirement Inventory Review and Normalization Proposal

Status: initial inventory review
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`
Related machine-readable artifact: `docs/planning/2026-05-09_requirement_inventory.json`

## Purpose
This document records the first structured inventory review of the current governed artifacts in `Destabilization_Signal_Monitor`.

The goal of this work package is not yet to migrate the requirements into the final `vmodel/` YAML structure. The goal is to create a stable inventory baseline that tells us:
- what governed IDs currently exist
- where they are currently defined or referenced
- which artifact classes already have a strong source of truth
- where contradictions, drift, or governance gaps are already visible

## Inventory result summary
Extracted governed IDs:
- `PSR`: 22
- `PSyR`: 36
- `PSwR`: 108
- `PM`: 71
- `ALG`: 52
- `TV`: 108
- `OI`: 42

Interpretation:
- the repository already has substantial governance coverage
- the scope is much larger than a small prototype baseline
- migration must therefore be treated as normalization of an already broad requirement system, not as lightweight scaffolding

## Current source-of-truth shape by artifact class

### Strongest current definition sources
- `PSR-*`: `docs/requirements/ProtoSR.md`
- `PSyR-*`: `docs/requirements/ProtoSyR.md`
- `PSwR-*`: `docs/requirements/ProtoSwR.md`
- `PM-*`: `docs/method/ProtoMethod.md`
- `ALG-*`: `docs/method/ProtoScoring.md`

### Weaker / indirect artifact classes
- `TV-*` currently does not have a dedicated catalog document
  - it is currently inferred primarily from `docs/traceability/TraceabilityMatrix.md`
- `OI-*` currently does not have a dedicated structured issue register
  - it is currently referenced textually inside `docs/requirements/OpenIssues.md`

Interpretation:
- requirements, method rules, and algorithms already have strong textual definition anchors
- verification artifacts and open issues are still governance-weaker than the requirement hierarchy

## Proposed normalization model

### Requirement-like artifacts
For `PSR`, `PSyR`, `PSwR`:
- `candidate_baseline_requirement`
- `accepted_baseline_requirement`
- `implemented_requirement`
- `provisional_requirement`
- `retired_requirement`

### Method artifacts
For `PM`:
- `candidate_baseline_method_rule`
- `accepted_method_rule`
- `provisional_method_rule`
- `retired_method_rule`

### Algorithm artifacts
For `ALG`:
- `candidate_baseline_algorithm`
- `accepted_algorithm`
- `provisional_algorithm`
- `retired_algorithm`

### Verification artifacts
For `TV`:
- `candidate_verification_artifact`
- `accepted_verification_artifact`
- `implemented_verification_artifact`
- `retired_verification_artifact`

### Issue artifacts
For `OI`:
- `candidate_open_issue`
- `open_issue`
- `resolved_issue`
- `retired_issue`

## Content-level findings and contradictions

### Finding 1: current active baseline is broader than early prototype framing
Observed:
- `ProtoScope.md` opens with 3 countries: Iran, Israel, Deutschland
- `config/default.yaml` currently configures 10 countries
- `README.md` describes a V4.3.2 monitor state, not only an early V1/V2 prototype

Interpretation:
The repository has evolved from an original narrow prototype statement into a much broader operational comparative baseline.

Risk:
If we migrate requirements without separating historical origin from current baseline, we may encode contradictory scope statements into the future YAML layer.

Recommendation:
During migration, mark scope statements explicitly as one of:
- `historical_origin_scope`
- `current_active_baseline_scope`
- `provisional_future_scope`

### Finding 2: time-horizon statements are inconsistent
Observed:
- `ProtoScope.md` states time window `12 Monate`
- `README.md` still describes historical rolling defaults with `365` days
- `config/default.yaml` currently sets `baseline_days = 356` and `historical.horizon_days = 356`
- `PSR-024` and related V4.3 comparative artifacts explicitly reference full `356-day` profiles

Interpretation:
There is a real content-level inconsistency, not just wording noise.

Most likely explanation:
- earlier historical logic was 365-day oriented
- later V4.3 comparative baseline moved to a 356-day profile standard
- not all narrative documentation was updated consistently

Impact:
This must be treated as a migration decision point. Otherwise the future requirement baseline would encode contradictory temporal scope.

Recommendation:
Before YAML baseline conversion of the affected requirements, decide whether the authoritative active baseline is:
- `356 days`
- `365 days`
- or a version-dependent split that must be documented explicitly

### Finding 3: verification governance is less mature than requirement governance
Observed:
- `TV-*` IDs are referenced in the matrix and tests
- but no explicit `TV` catalog currently exists
- therefore test intent is partially implicit in traceability rows rather than fully governed as first-class verification specifications

Interpretation:
This is a structural governance gap.

Recommendation:
When we move to `vmodel/verification/test_specifications.yaml`, `TV-*` items should become first-class governed artifacts instead of matrix-only references.

### Finding 4: open issues are important but not yet governed like change-controlled artifacts
Observed:
- `OI-*` references are present in `OpenIssues.md`
- but they are not normalized like requirements or trace links

Interpretation:
The repository already uses open issues as meaningful scope and architecture constraints, but not yet as a machine-governed artifact class.

Recommendation:
Future migration should decide whether `OI-*` lives under:
- `vmodel/change/`
- a separate governed issue register
- or a hybrid change/clarification mechanism

### Finding 5: repository documentation still lags the actual subsystem structure
Observed:
- `docs/architecture/RepositoryLayout.md` does not reflect the full visible structure of `api/`, `frontend/`, and `tools/`

Interpretation:
The system architecture has expanded beyond the documented repository layout.

This is not only a docs issue. It indicates subsystem scope is now larger than the original repository model.

Recommendation:
During migration, treat the repository as at least a 3-subsystem landscape:
- analysis core (`proto/`)
- API layer (`api/`)
- frontend (`frontend/`)

## Sense-check on the current governance shape
Overall, the current requirement set is meaningful and not obviously random. The growth path from V1/V2 to V4.3.2 is visible and largely internally explainable.

However, there are three clear sense-making risks:
1. historical statements are mixed with active baseline statements
2. some documentation still reflects older time/scope assumptions
3. verification and issue artifacts are not yet governed as rigorously as requirements and methods

That means the repository is already governance-rich, but not yet governance-clean.

## Decision for next migration step
Status update:
- the baseline decision package has now been created in `docs/planning/2026-05-09_baseline_decisions.md`

Resolved decisions:
1. active default country baseline = 10 countries
2. country count must remain parameterizable
3. active default historical horizon = 365 days
4. historical horizon must remain parameterizable
5. `TV-*` becomes a first-class governed verification artifact
6. `OI-*` becomes a first-class governed issue artifact
7. open issues should be resolved autonomously where safe, and escalated only for high-impact semantic ambiguity

Updated interpretation of previously observed contradictions:
- 3-country scope now becomes historical-origin context unless explicitly re-scoped
- 356-day baseline behavior is now non-default legacy/variant candidate behavior unless explicitly justified later

## Recommended next work package
WP-05 should now begin the first machine-readable migration preparation with the resolved baseline in force.

Recommended WP-05 scope:
- start preparing YAML-oriented migration of `PSR/PSyR/PSwR`
- define first-class target representation for `TV-*` and `OI-*`
- identify requirements and config statements that still conflict with the accepted 10-country / 365-day defaults
- autonomously clean up low-risk open issues that are purely documentary or consistency-related

## Summary
This work package produced a usable machine-readable requirement inventory and surfaced real content-level contradictions that matter for the later V-Model-light migration.

Most important outcome:
The main migration risk is no longer “missing requirements”.
The main migration risk is “migrating historically layered requirements into YAML without first classifying baseline/default/parameterized/legacy statements correctly”.
