# WP-08 Software Requirement Derivation Baseline

Status: initial software derivation
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`

## Purpose
This work package derives the first populated software-requirement layer from the normalized system baseline, populates bidirectional system-to-software traceability, and creates the first machine-readable verification-artifact baseline for explicit `TV-*` identifiers.

## Target artifacts updated
- `vmodel/requirements/software_requirements.yaml`
- `vmodel/requirements/system_requirements.yaml`
- `vmodel/requirements/stakeholder_requirements.yaml`
- `vmodel/verification/test_specifications.yaml`

## Main results

### 1. Software requirements populated
`vmodel/requirements/software_requirements.yaml` now contains the migrated `PSwR-*` layer with:
- `id`
- `title`
- `statement`
- `status`
- `baseline_classification`
- `migration_tags`
- `parent_system_ids`
- `child_verification_ids`
- `source_refs`

### 2. Bidirectional traceability System <-> Software populated
The first complete system/software trace boundary is now explicit:
- system -> software via `PSyR.child_software_ids`
- software -> system via `PSwR.parent_system_ids`

This means the migrated requirement chain now exists across three levels:
- stakeholder
- system
- software

### 3. First concrete `TV-*` target representation created
`vmodel/verification/test_specifications.yaml` now contains the first machine-readable verification baseline for explicit `TV-*` identifiers already present in the legacy traceability matrix.

Current scope:
- explicit `TV-*` identifiers were migrated
- generic test-file references without an explicit `TV-*` ID remain a later verification work package

## Required prerequisite fix discovered during WP-08
While deriving software requirements, a structural inconsistency became visible:
- `PSwR-020..PSwR-035` existed in the legacy traceability and issue set
- but their parent lineage `PSR-008..PSR-011` and `PSyR-011..PSyR-017` had not yet been migrated into the new YAML baseline

Without that repair, software requirements in the historical rolling-trend branch would have required invented parent links.

### Fix applied
I recovered the missing lineage as a low-risk prerequisite migration step:
- Stakeholder layer recovered:
  - `PSR-008..PSR-011`
- System layer recovered:
  - `PSyR-011..PSyR-017`

Recovery sources:
- `docs/traceability/TraceabilityMatrix.md`
- `docs/requirements/OpenIssues.md`

Engineering rationale:
- top-down continuity is more important than preserving an accidental omission in intermediate migration steps
- recovered entries are explicitly marked as recovered, not silently treated as first-class canonical source text from `ProtoSR.md` / `ProtoSyR.md`

## Low-risk normalization decisions applied in WP-08

### 1. Comparative 10-country software wording
Legacy issue:
- several V4.3 software requirements were worded as if the 10-country set were fixed forever

Handled as:
- default 10-country baseline remains explicit and binding
- configurability is preserved where supported
- normalized examples:
  - `PSwR-097`
  - related configuration semantics in `PSwR-002`, `PSwR-035`, `PSwR-114`

### 2. 356-day software wording
Legacy issue:
- several V4.3/V4.3.1 software requirements used fixed `356-day` wording
- accepted baseline is `365 days default`, configurable horizon

Handled as:
- normalized to default 365-day baseline where the requirement intent is clearly annual-profile based
- normalized examples:
  - `PSwR-098`
  - `PSwR-101`
  - `PSwR-105`

Interpretation:
- annual-comparison intent is preserved
- legacy 356-day wording is kept visible only through migration tags / notes, not as active normative baseline text

## Source-gap finding from the legacy software layer
A new migration finding appeared:
- `ProtoSwR.md` currently contains `PSwR-001..019` and `PSwR-036..124`
- `PSwR-020..035` are missing there as explicit standalone entries
- however, they are implemented, referenced in the traceability matrix, and discussed in open issues

Current handling:
- `PSwR-020..035` were migrated as recovered requirements
- each recovered entry is marked accordingly in `migration_tags` and `notes`

Recommended follow-up:
- later re-establish these requirements in the authoritative legacy source set or fully retire the legacy markdown source in favor of the new YAML baseline

## Traceability mapping approach used
Parent mapping rule used in this package:
- software requirements were linked to system parents by normative function, not only by numeric proximity or file adjacency
- where one software behavior materially supports more than one system behavior, multiple parents were assigned

Examples:
- `PSwR-002` -> `PSyR-001`, `PSyR-002`, `PSyR-013`, `PSyR-036`, `PSyR-037`
- `PSwR-040` -> `PSyR-018`, `PSyR-021`, `PSyR-022`
- `PSwR-098` -> `PSyR-037`
- `PSwR-122` -> `PSyR-042`, `PSyR-043`

## Verification-artifact migration scope in WP-08
What is included now:
- explicit `TV-*` IDs from the legacy traceability matrix
- links from software requirements to explicit verification IDs via `child_verification_ids`
- machine-readable specification entries in `test_specifications.yaml`

What is intentionally not finalized yet:
- normalization of all non-`TV-*` test references into a fully governed verification hierarchy
- explicit requirement coverage decisions for rows that only cite generic test files
- full `TV` governance integration with open issues and acceptance criteria

## What was intentionally not done yet
Not yet done in this work package:
- code/implementation gap analysis against the newly migrated software baseline
- migration of `OI-*` into `vmodel/change/open_issues.yaml`
- machine-readable change-request harmonization for historical baseline conflicts
- full normalization of all verification artifacts beyond explicit `TV-*` identifiers

## Assessment after WP-08
After this step, the migrated V-model chain is now materially present across the requirement hierarchy:
- stakeholder baseline populated
- system baseline populated
- software baseline populated
- bidirectional traceability populated at both:
  - stakeholder <-> system
  - system <-> software
- first machine-readable verification baseline initialized

This is the first point where the migrated requirements-as-code structure is operationally useful for a later implementation comparison.

## Recommended next work package
WP-09:
- compare normalized `PSwR` baseline against implementation reality
- identify missing / provisional / contradictory implementation coverage
- migrate `OI-*` into `vmodel/change/open_issues.yaml`
- tighten verification governance for non-explicit test references

## Summary
WP-08 completed the first end-to-end requirement derivation path down to software level.

Most important practical result:
- the project now has a machine-readable stakeholder/system/software chain with explicit bidirectional traceability and an initial verification-artifact baseline.