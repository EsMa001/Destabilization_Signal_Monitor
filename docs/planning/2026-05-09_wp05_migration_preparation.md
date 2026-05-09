# WP-05 Migration Preparation and Derivation Workflow

Status: initial migration-preparation package
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`

## Purpose
This document defines the first practical migration-preparation step after the baseline decisions.

It also evaluates the proposed top-down approach:
1. revise and normalize stakeholder requirements
2. derive system requirements from them
3. derive software requirements from the system layer
4. resolve contradictions discovered during derivation
5. only then compare the revised requirement chain against the current implementation

## Assessment of the proposed approach
Short answer: yes, this makes sense.

It is the correct approach for this repository, with one important constraint:
- we must treat the current implementation as evidence, not as the primary authority, during the first derivation pass

Why this is the right sequence:
1. the repository already contains a broad but historically layered requirement space
2. current implementation behavior reflects both intended capability and accumulated historical drift
3. if we align requirements directly to current implementation too early, we risk legitimizing drift as intended baseline behavior
4. a top-down derivation pass gives us a cleaner normative chain before implementation comparison

Recommended interpretation:
- stakeholder layer answers: what the system shall achieve and expose externally
- system layer answers: what the system must provide structurally and behaviorally
- software layer answers: what software functions, data handling, interfaces, and controls are required
- implementation comparison answers: where code matches, exceeds, misses, or contradicts the revised chain

## Constraint on the later implementation comparison
The later implementation comparison should not be framed as:
- “make requirements match the code”

It should be framed as:
- “make mismatches explicit, then decide whether code or requirement baseline must change”

This distinction is essential for preserving engineering rigor.

## Main risks in the derivation process

### Risk 1: historical statements leak into the active baseline
Mitigation:
- classify every migrated statement as:
  - `active_baseline`
  - `historical_origin`
  - `parameterized_capability`
  - `legacy_variant`

### Risk 2: implementation convenience distorts the software layer
Mitigation:
- derive `PSwR` from normalized `PSyR`, not directly from current code
- only use code as plausibility evidence and gap evidence during derivation

### Risk 3: contradictions get hidden instead of resolved
Mitigation:
- contradictions must be logged explicitly in migration/impact artifacts
- every contradiction needs one of:
  - resolved by baseline decision
  - resolved by requirement rewrite
  - resolved by implementation change request
  - escalated to user because intent is unclear

## WP-05 result in this work package
This work package initializes the future `vmodel/` target structure and the migration rule set, but intentionally does not yet migrate the full requirement content.

Initialized target artifacts:
- `vmodel/README.md`
- `vmodel/requirements/stakeholder_requirements.yaml`
- `vmodel/requirements/system_requirements.yaml`
- `vmodel/requirements/software_requirements.yaml`
- `vmodel/verification/test_specifications.yaml`
- `vmodel/traceability/trace_links.yaml`
- `vmodel/traceability/impact_analysis.md`
- `vmodel/architecture/design_decisions.yaml`
- `vmodel/change/open_issues.yaml`
- `vmodel/change/change_requests.yaml`
- `vmodel/migration/baseline_classification_rules.yaml`

## Proposed next execution order

### Step 1: Stakeholder requirement normalization
Goal:
- produce a cleaned stakeholder baseline with explicit classification and no unresolved default-scope ambiguity

Recommended output:
- first populated `vmodel/requirements/stakeholder_requirements.yaml`

### Step 2: System requirement derivation
Goal:
- derive normalized `PSyR` from the revised stakeholder layer
- document contradictions and missing derivation links explicitly

Recommended output:
- first populated `vmodel/requirements/system_requirements.yaml`
- first non-empty `vmodel/traceability/trace_links.yaml`

### Step 3: Software requirement derivation
Goal:
- derive normalized `PSwR` from the revised system layer
- separate implementation-facing software obligations from historical implementation detail

Recommended output:
- first populated `vmodel/requirements/software_requirements.yaml`
- first governed `TV-*` entries in `vmodel/verification/test_specifications.yaml`

### Step 4: Governed open issue integration
Goal:
- migrate and triage `OI-*`
- resolve low-risk documentation/consistency issues autonomously where possible

Recommended output:
- first populated `vmodel/change/open_issues.yaml`
- updates to migrated requirements and traceability as needed

### Step 5: Implementation comparison
Goal:
- compare the revised requirement chain against current code and tests
- identify:
  - satisfied requirements
  - missing implementation
  - undocumented implementation behavior
  - contradictions
  - required change requests

Recommended output:
- populated `vmodel/traceability/impact_analysis.md`
- implementation-gap review document or change package

## Engineering recommendation
The strongest version of your proposed workflow is:
1. normalize stakeholder layer
2. derive system layer
3. derive software layer
4. govern verification and open issues
5. compare against implementation
6. then decide correction direction requirement-by-requirement

That preserves causality and prevents code-led requirement drift.

## Summary
Your proposed overall process is sound and should be used.

The key discipline is:
- derive top-down first
- compare bottom-up afterward
- resolve contradictions explicitly instead of silently absorbing them into the new baseline
