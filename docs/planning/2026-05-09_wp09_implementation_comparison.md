# WP-09 Implementation Comparison and Open-Issue Migration

Status: initial implementation comparison
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`

## Purpose
This work package compares the normalized software-requirement baseline against the currently traceable implementation state, migrates the open-issue set into machine-readable form, and hardens verification governance for legacy generic test references.

## Target artifacts updated
- `vmodel/change/open_issues.yaml`
- `vmodel/verification/test_specifications.yaml`

Reference artifacts assessed:
- `vmodel/requirements/software_requirements.yaml`
- `docs/traceability/TraceabilityMatrix.md`
- `docs/requirements/OpenIssues.md`
- `docs/testing/TestStrategy.md`
- `docs/testing/ValidationPlan.md`

## Scope of the implementation comparison
This was not a code-first re-derivation step.

Comparison basis used:
- migrated `PSwR` baseline as normative target
- legacy traceability matrix as current implementation evidence
- current executable test situation on the host as validation evidence

Interpretation rule:
- code and traceability are evidence for implementation state
- migrated requirements remain the normative baseline

## Main findings

### 1. Requirement-to-implementation trace coverage
Result:
- `PSwR` total in migrated baseline: 124
- `PSwR` with legacy implementation trace row: 124
- `PSwR` without implementation trace row: 0

Interpretation:
- every migrated software requirement currently has at least one implementation-trace anchor in the legacy traceability matrix
- the main risk is therefore not absence of any implementation evidence, but varying evidence quality and governance maturity

### 2. Implementation status split from current evidence
Current comparison result:
- `implemented_requirement`: 116
- `provisional_requirement`: 8

Provisional software requirements currently visible in the implementation evidence:
- `PSwR-034`
- `PSwR-040`
- `PSwR-041`
- `PSwR-042`
- `PSwR-045`
- `PSwR-046`
- `PSwR-061`
- `PSwR-068`

Interpretation:
- the dominant implementation state is already positive
- the remaining gaps are concentrated in explicitly provisional scopes rather than in fully missing implementation blocks

### 3. Verification evidence quality is mixed
Current comparison result:
- explicit implemented `TV-*` artifacts: 108
- software requirements with only generic legacy test references and no explicit `TV-*` ID: 25
- raw manual-review marker detected: 1 (`PSwR-019`)

This means:
- technical verification evidence exists broadly
- but not all evidence is yet governed as explicit named verification artifacts

### 4. Current host-side executable validation blocker
Observed during WP-09:
- `PYTHONPATH=. /opt/hermes/.venv/bin/pytest -q` fails during collection
- root cause observed on this host: `ModuleNotFoundError: No module named 'matplotlib'`
- additional environment finding: `/opt/hermes/.venv/bin/python -m pip` is not available on this host environment

Interpretation:
- this does not invalidate the migrated requirement baseline
- but it means full live re-verification of the legacy test suite is currently blocked in this execution environment
- therefore the implementation comparison in WP-09 is source-grounded and trace-grounded, with partial live validation only

## Open-issue migration result
`vmodel/change/open_issues.yaml` is now populated.

Migrated counts:
- total issues in YAML baseline: 44
- normalized open issues: 30
- normalized resolved issues: 14

Normalization rule used:
- legacy `closed_*` variants -> `resolved_issue`
- legacy `open*` variants -> `open_issue`

This preserves issue intent while removing inconsistent free-text status variants.

## New low-risk governance issues added in WP-09

### OI-045 — Legacy markdown source-set drift
Problem:
- recovered requirement lineage from WP-08 shows that the legacy markdown source set is no longer complete as an authoritative baseline
- specifically affected are:
  - `PSR-008..011`
  - `PSyR-011..017`
  - `PSwR-020..035`

Meaning:
- these requirements are implemented and traceable
- but they are not all present as explicit standalone entries in the legacy requirement markdown files

Why this matters:
- dual maintenance between legacy markdown and YAML baseline becomes unsafe
- future engineers could mistake omissions in the markdown files for true scope absence

### OI-046 — Generic verification references not yet formally governed
Problem:
- 25 implemented software requirements are currently only backed by generic test references or manual review markers in the legacy traceability matrix
- they lack explicit governed verification artifact IDs

Meaning:
- implementation evidence exists
- governance quality of verification evidence is weaker than for explicit `TV-*` items

## Verification-governance hardening applied in WP-09
`vmodel/verification/test_specifications.yaml` was hardened in two layers:

### 1. Explicit `TV-*` artifacts preserved as authoritative
No legacy `TV-*` IDs were overwritten or renamed.

### 2. Candidate governance placeholders added for generic references
For legacy rows without explicit `TV-*` IDs, machine-readable candidate artifacts were added using the prefix:
- `GV-*`

Purpose:
- make generic verification evidence machine-trackable
- avoid inventing fake legacy `TV-*` IDs
- create an explicit governance backlog that can later be promoted into stable verification artifacts

Current counts after hardening:
- explicit implemented verification artifacts: 108
- candidate governance placeholders: 25
- total machine-readable verification entries: 133

Important engineering point:
- `GV-*` means governance placeholder, not legacy accepted verification ID
- this keeps traceability honest while still improving control of incomplete legacy verification references

## Assessment of implementation maturity after WP-09
The migrated software baseline now supports a clearer maturity picture:

Strong points:
- no software requirement is completely untraced
- most software requirements are already represented as implemented in the legacy evidence
- provisional scope is concentrated and explicit
- open issues are now machine-readable
- verification governance now distinguishes between explicit artifacts and weaker legacy generic references

Remaining risks:
- legacy source-set drift between markdown and YAML baseline
- verification evidence quality is uneven across requirements
- full test-suite execution on the current host is blocked by missing runtime dependency availability

## Recommended next work package
WP-10:
- implementation-gap cleanup on the explicitly provisional `PSwR` set
- start migrating or reconciling legacy markdown source-of-truth drift
- decide whether legacy markdown remains authoritative or YAML becomes the primary requirement baseline
- continue verification formalization by promoting selected `GV-*` placeholders into stable governed verification artifacts

## Summary
WP-09 established the first explicit implementation-comparison view on top of the migrated requirement stack.

Most important practical result:
- the project now has a machine-readable open-issue baseline and an implementation/verification maturity view that distinguishes clearly between:
  - implemented vs provisional software requirements
  - explicit verification artifacts vs generic legacy verification references
  - resolved vs still-open engineering issues