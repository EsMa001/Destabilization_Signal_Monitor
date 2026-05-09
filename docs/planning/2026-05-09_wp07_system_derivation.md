# WP-07 System Requirement Derivation Baseline

Status: initial system derivation
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`

## Purpose
This work package derives the first normalized system-requirement layer from the migrated stakeholder baseline and establishes the first populated bidirectional traceability links between stakeholder and system requirements.

## What was migrated
Target artifacts:
- `vmodel/requirements/system_requirements.yaml`
- updated `vmodel/requirements/stakeholder_requirements.yaml`

Result:
- `PSyR-*` layer is now initialized in machine-readable form
- stakeholder requirements now contain populated `child_system_ids`
- system requirements contain populated `parent_stakeholder_ids`

## Bidirectional traceability implementation
The bidirectional traceability requirement is now implemented at the first real derivation boundary:
- stakeholder -> system via `child_system_ids`
- system -> stakeholder via `parent_stakeholder_ids`

Current state:
- top layer (`PSR`) has empty `parent_stakeholder_ids`, which is correct
- mid layer (`PSyR`) has populated parent stakeholder links
- `PSyR.child_software_ids` remains empty pending software derivation

Engineering judgment:
- this is the first point in the migration where bidirectional traceability becomes content-bearing rather than only structural

## Key normalization decisions applied in the system layer

### 1. Country scope normalization
Original issue:
- early `PSyR-001` wording still reflected a 3-country support boundary
- later `PSyR-036` enforced a fixed 10-country comparative baseline
- accepted baseline says default = 10 countries, but parameterizable

Handled as:
- `PSyR-001` normalized to default 10-country baseline plus configurable country selection
- `PSyR-036` normalized to explicit default baseline plus consistent configurable selection

Interpretation:
- we avoid a false contradiction between default baseline and parameterization capability
- fixed-only country wording is no longer treated as authoritative

### 2. Horizon normalization
Original issue:
- older `PSyR-002` used generic `12m`
- later `PSyR-037` used fixed `356-day` wording
- accepted baseline says default = 365 days, parameterizable

Handled as:
- `PSyR-002` normalized to explicit default 365-day annual horizon plus configurable horizon capability
- `PSyR-037` normalized to full default 365-day profiles plus configurable horizon

Interpretation:
- generic annual semantics and explicit profile length semantics are now aligned to the same accepted default baseline

### 3. Comparative baseline wording
Original issue:
- later comparative requirements were written in a way that could be misread as “exactly fixed forever”

Handled as:
- comparative baseline is still explicit and mandatory by default
- configurability is modeled as a separate required capability rather than a contradiction

## Parent mapping approach used
Derivation rule used in this work package:
- system requirements were linked to stakeholder parents based on normative intent, not only by textual similarity
- where several stakeholder requirements jointly justify one system behavior, multiple parent links were assigned

Examples:
- `PSyR-001` derives from both:
  - `PSR-002` default country baseline and parameterization
  - `PSR-006` comparable presentation structure
- `PSyR-028` derives from:
  - `PSR-016` historical fusion result space
  - `PSR-018` time-aware and analyst-friendly driver visibility
  - `PSR-019` consistent fusion plot embedding
- `PSyR-040` derives from:
  - `PSR-025` peak attribution and event-alignment hardening
  - `PSR-026` analyst event registry and real-world alignment

## Low-risk contradictions handled in this package

### Country baseline contradiction
Resolved in normalized system wording.

### 356-day versus 365-day contradiction
Resolved in normalized system wording.

### Fixed-baseline versus configurable-capability ambiguity
Resolved by expressing both explicitly:
- one statement for the default baseline
- one statement for parameterization capability within the same normalized requirement where appropriate

## What was intentionally not done yet
Not yet done in this work package:
- software requirement derivation
- child software links
- verification artifact population
- implementation comparison

Reason:
- these require the next derivation layer and should not be guessed prematurely

## Assessment of the top-down chain after this step
The chain now has a meaningful first normative structure:
- migrated stakeholder baseline
- derived system baseline
- first populated bidirectional traceability between the two layers

This means the project is now ready for the next strictly top-down step:
- derive software requirements from the normalized system layer

## Recommended next work package
WP-08:
- derive normalized `PSwR` layer from `vmodel/requirements/system_requirements.yaml`
- populate:
  - `PSyR.child_software_ids`
  - `PSwR.parent_system_ids`
- define the first concrete target representation for `TV-*`
- continue autonomous cleanup of low-risk issue/documentation contradictions where safe

## Summary
This work package established the first real bidirectional traceability boundary in the migrated V-Model structure.

Most important practical result:
- the requirement chain is no longer only prepared structurally; it now exists in normalized stakeholder and system form with explicit parent/child links.
