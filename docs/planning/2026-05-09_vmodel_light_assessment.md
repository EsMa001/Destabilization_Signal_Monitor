# V-Model-Light Assessment and Migration Start

Status: initial assessment
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`
Scope of this work package: repository assessment only; no production-code changes

## Purpose
This document establishes the first migration baseline for bringing `Destabilization_Signal_Monitor` closer to the stricter V-Model-light / requirements-as-code form used in the HermesCollabProject test repository.

This first step intentionally does not restructure the implementation. It documents:
- current repository state
- existing strengths
- risks and contradictions
- recommended migration target
- ordered next work packages

## Executive assessment
The repository is already strongly requirements-driven, but its governance is currently document-centric rather than machine-validated.

Assessment:
- good candidate for migration to stricter V-Model-light form
- not a greenfield conversion; this is a consolidation and hardening task
- strongest immediate leverage is not code refactoring, but governance normalization

Recommendation:
1. stabilize reproducibility and dependency declaration
2. normalize requirements and traceability into machine-readable artifacts
3. only then refactor oversized implementation hotspots

## Current repository baseline

### Repository shape
Observed top-level areas:
- `docs/`
- `config/`
- `data/`
- `proto/`
- `api/`
- `frontend/`
- `tests/`
- `tools/`
- `scripts/`

### Existing requirement and traceability assets
Already present:
- `docs/requirements/ProtoScope.md`
- `docs/requirements/ProtoSR.md`
- `docs/requirements/ProtoSyR.md`
- `docs/requirements/ProtoSwR.md`
- `docs/requirements/OpenIssues.md`
- `docs/method/ProtoMethod.md`
- `docs/method/ProtoScoring.md`
- `docs/method/ProtoRunbook.md`
- `docs/testing/TestStrategy.md`
- `docs/testing/ValidationPlan.md`
- `docs/traceability/TraceabilityMatrix.md`
- `docs/architecture/Architecture.md`
- `docs/architecture/RepositoryLayout.md`
- `AGENTS.md`
- `IMPLEMENT.md`

### Existing ID system
The repository already uses a structured ID scheme:
- stakeholder: `PSR-*`
- system: `PSyR-*`
- software: `PSwR-*`
- method: `PM-*`
- algorithm: `ALG-*`
- verification / tests: `TV-*`

This is a strong starting point for migration.

## Strengths relevant to migration

### 1. Clear domain layering already exists
The architecture is already described and partially reflected in code:
- source adapters
- canonical observations
- features
- scoring
- fusion
- reporting
- run management
- historical processing

This aligns well with a V-Model decomposition.

### 2. Traceability culture already exists
Traceability is already present in three places:
- markdown requirement documents
- traceability matrix
- traceability comments in code and tests

That means migration can focus on normalization rather than inventing traceability from scratch.

### 3. Tests already exist across multiple levels
Observed backend/core tests:
- `tests/test_config.py`
- `tests/test_sources.py`
- `tests/test_features.py`
- `tests/test_scoring.py`
- `tests/test_observations.py`
- `tests/test_fusion.py`
- `tests/test_runs.py`
- `tests/test_pipeline.py`
- `tests/test_api_mvp.py`
- `tests/test_integration_processing.py`

Frontend tests are also present under `frontend/`.

### 4. Scope evolution is explicitly documented
The repository does not hide that the prototype expanded from V1/V2 into V4.3.2. This makes later baseline clarification possible.

## Risks, inconsistencies, and content-level concerns

### 1. Governance is markdown-heavy and therefore drift-prone
Current requirement truth is spread across multiple markdown files. This creates a risk of divergence between:
- requirements documents
- implementation
- tests
- traceability matrix
- implementation notes in `IMPLEMENT.md`

Consequence:
A machine-checkable V-Model-light layer is currently missing.

### 2. Scope drift between early scope and current operational baseline
Observed content-level mismatch:
- `README.md` and `ProtoScope.md` start from a 3-country framing
- `config/default.yaml` currently configures 10 countries
- `README.md` describes a broad V4.3.2 state, while early scope text still reads like a V1/V2 prototype boundary

Interpretation:
This is not necessarily wrong, but the active baseline is not yet cleanly separated from the historical evolution path.

Required clarification for later work:
- what is the authoritative current baseline?
- what is legacy/historical context only?
- what is still provisional?

### 3. Repository layout documentation is partially outdated
`docs/architecture/RepositoryLayout.md` currently documents:
- `docs/`
- `scripts/`
- `config/`
- `data/`
- `proto/`
- `tests/`
- `outputs/`

But the actual repository also includes at least:
- `api/`
- `frontend/`
- `tools/`

Interpretation:
The documented architecture/repository view has not fully kept pace with the codebase.

### 4. Dependency declaration is under-specified
Observed in `pyproject.toml`:
- package metadata exists
- package discovery exists
- visible runtime/test dependencies are not declared comprehensively

But code visibly imports, among others:
- `matplotlib`
- `fastapi`
- `pydantic`
- `uvicorn`

Observed execution issue:
- local test collection failed due to missing `matplotlib`

Interpretation:
The repository is currently not reproducible from its package definition alone.

### 5. Central implementation hotspots are too large
Large files identified during inspection:
- `proto/fusion/validation.py` ~4373 lines
- `proto/pipeline/run_proto.py` ~2368 lines
- `tests/test_fusion.py` ~2266 lines
- `proto/reporting/handout.py` ~1667 lines
- `proto/pipeline/config.py` ~1356 lines
- `tests/test_pipeline.py` ~1175 lines
- `proto/reporting/plots.py` ~897 lines
- `proto/fusion/scoring.py` ~828 lines

Interpretation:
The system is functionally decomposed at package level, but several modules are carrying too much orchestration and policy at once.

This is a maintainability risk, but should not be the first migration step.

### 6. Quick-start expectations are stronger than the declared environment contract
`README.md` suggests simple commands such as:
- `python -m pytest`
- `python -m proto.pipeline.run_proto`

Current repository state indicates these commands may require dependencies that are not declared in the package metadata.

Interpretation:
There is a gap between the documented onboarding path and the actual reproducibility contract.

## Migration target relative to HermesCollabProject style
The goal should not be to delete the existing `docs/` structure immediately.

The recommended target is a parallel, stricter governance layer:

```text
vmodel/
  requirements/
    stakeholder_requirements.yaml
    system_requirements.yaml
    software_requirements.yaml
  verification/
    test_specifications.yaml
  traceability/
    trace_links.yaml
    impact_analysis.md
  architecture/
    design_decisions.yaml
  change/
    change_requests.yaml
tools/
  validate_requirements.py
  validate_traceability.py
  validate_code_links.py
  generate_trace_matrix.py
  generate_verification_report.py
```

Important migration rule:
- existing markdown sources remain temporarily authoritative input documents
- new YAML artifacts become the normalized machine-readable layer
- only after successful parity should markdown governance be reduced or re-scoped

## Proposed migration principles

### Principle 1: no big-bang rewrite
Migrate in parallel, not destructively.

### Principle 2: normalize before refactoring
First make requirements and traceability machine-checkable, then refactor code hotspots.

### Principle 3: separate active baseline from history
Current valid baseline, historical evolution, provisional scope, and open issues must be distinguishable.

### Principle 4: keep explicit provenance of inferred requirements
When converting markdown requirements into YAML, each migrated item should preserve source provenance, for example:
- source document
- source section
- migrated status
- explicit vs inferred
- open questions
- provisional scope marker

## Recommended next work packages

### WP-02: Reproducibility and environment contract hardening
Objective:
- make repository setup and test execution reproducible

Expected focus:
- complete dependency declaration in `pyproject.toml`
- define runtime vs dev/test dependencies
- confirm canonical test command(s)
- align documented quick-start with actual environment requirements

Status update:
- completed in commit `396e5ae`

### WP-03: Requirement inventory extraction
Objective:
- extract all existing requirement IDs into a structured inventory

Expected outputs:
- full inventory of `PSR-*`, `PSyR-*`, `PSwR-*`, `PM-*`, `ALG-*`, `TV-*`
- source mapping to current markdown documents
- first status normalization proposal (`accepted`, `implemented`, `provisional`, `open`, etc.)

Status update:
- completed in commit `f5db326`
- outputs:
  - `docs/planning/2026-05-09_requirement_inventory.json`
  - `docs/planning/2026-05-09_requirement_inventory_review.md`

### WP-04: Baseline decision package
Objective:
- resolve the highest-impact migration ambiguities before YAML migration

Resolved decisions:
- active default country baseline = 10 countries
- country count remains parameterizable
- active default historical horizon = 365 days
- historical horizon remains parameterizable
- `TV-*` will be modeled as first-class governed verification artifacts
- `OI-*` will be modeled as first-class governed issue artifacts
- open issues should be resolved autonomously where safe; escalate only high-impact semantic ambiguity

Status update:
- completed in current work package
- output:
  - `docs/planning/2026-05-09_baseline_decisions.md`

### WP-05: First YAML-oriented migration preparation
Objective:
- prepare first machine-readable migration of baseline requirements and governed support artifacts

Expected focus:
- classify current requirement statements into active baseline / historical origin / parameterized capability / legacy variant
- define first-class target representation for `TV-*` and `OI-*`
- identify and clean low-risk open issues that are documentary or consistency-related
- prepare first `vmodel/` artifact skeleton with minimum ambiguity

## Initial content-level review findings for discussion
These points are not blockers for this work package, but they should be explicitly reviewed in later steps:

1. Is the current authoritative operational baseline really the 10-country V4.3.2 state?
2. Should the 3-country framing remain as historical origin only, or still constrain parts of the active requirements set?
3. Should `IMPLEMENT.md` be treated as project-history log, active execution baseline, or both?
4. Should frontend requirements stay integrated into the same requirement tree, or be separated into a subsystem-specific requirement branch?

## Decision for this first work package
Recommendation accepted for now:
- do not restructure code yet
- do not delete existing `docs/*`
- use this document as the migration baseline for the next work package

## Summary
The repository is already requirements-oriented and therefore highly suitable for V-Model-light hardening.

The primary problem is not lack of requirements, but lack of normalized, machine-checkable governance.

Therefore the correct next step is:
- harden reproducibility and dependency declaration
- then migrate requirement and traceability content into a stricter YAML-based governance layer
- refactor large code hotspots only after governance parity exists
