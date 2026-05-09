# Baseline Decisions for V-Model-Light Migration

Status: accepted baseline decisions
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`
Decision source: user clarification in migration thread

## Purpose
This document resolves the highest-impact baseline ambiguities identified during the requirement inventory review.

These decisions are authoritative for the migration path from the current markdown-driven governance into a stricter V-Model-light / requirements-as-code structure.

## Decision 1: Country scope baseline
Decision:
- default operational baseline: 10 countries
- country scope must remain parameterizable

Interpretation:
- the active baseline is no longer the historical 3-country origin
- the 3-country framing remains relevant only as historical origin context unless a later artifact explicitly reintroduces it for a bounded mode
- requirement migration should therefore model two concepts separately:
  1. default baseline country set
  2. parameterizable country-selection capability

Migration consequence:
- requirements that still read like a fixed 3-country operational baseline must be reviewed and either:
  - reclassified as historical origin statements
  - or rewritten into parameterized active-baseline statements

Recommended requirement interpretation pattern:
- stakeholder/system/software baseline may define a default 10-country set
- software/config requirements should additionally express that the selected country subset is configurable

## Decision 2: Time-horizon baseline
Decision:
- default historical horizon baseline: 365 days
- historical horizon must remain parameterizable

Interpretation:
- the currently observed 356-day implementation/config baseline is no longer authoritative as default
- future migration should treat 365 days as the canonical default baseline
- any current 356-day wording or configuration must be treated as implementation drift, version-specific legacy behavior, or a deliberate variant that now needs explicit justification

Migration consequence:
- requirements and config-related artifacts touching historical horizon, baseline window, annual profile, and comparative profile length must be checked against this decision
- if 356 remains useful, it should survive only as an explicitly parameterized non-default mode

## Decision 3: Governance model for TV and OI artifacts
Decision:
- govern `TV-*` and `OI-*` as first-class artifacts in the future target model
- target placement:
  - `TV-*` under verification/test-specification governance
  - `OI-*` under governed issue/change tracking

Target interpretation:
- `TV-*` becomes a first-class verification artifact, not just an inferred traceability reference
- `OI-*` becomes a governed issue class, not just free-text documentation

Recommended target structure:
```text
vmodel/
  verification/
    test_specifications.yaml        # contains TV-* artifacts
  change/
    open_issues.yaml                # contains OI-* artifacts
    change_requests.yaml            # future CR-* artifacts if needed
```

Recommended artifact semantics:
- `TV-*`
  - verification intent
  - linked requirement IDs
  - linked test file(s)
  - test level
  - automation status
  - pass/fail/blocked or review status
- `OI-*`
  - title
  - statement/problem
  - affected artifacts
  - severity/priority
  - disposition
  - resolution status
  - resolution note or follow-up action

## Decision 4: Open issue handling policy during migration
Decision:
- open issues should be reviewed and resolved autonomously where possible
- only scope-critical ambiguities or high-impact semantic conflicts should be escalated back to the user

Interpretation:
- the migration should not treat every `OI-*` as a stop condition
- if an issue can be resolved safely through inspection, traceability cleanup, documentation correction, or a bounded consistency fix, it should be handled proactively
- if an issue changes system intent, operational semantics, or accepted baseline meaning, it must be escalated

Escalation rule:
Escalate to the user when an open issue affects at least one of the following:
- authoritative baseline scope
- external-facing semantics
- safety/security interpretation
- non-obvious trade-off between alternative valid behaviors
- change of accepted requirement meaning

## Resolved interpretation of previous contradictions

### 3-country vs 10-country contradiction
Resolved as:
- 10 countries = active default baseline
- variable country count = required parameterization capability
- 3-country framing = historical origin context unless explicitly re-scoped

### 356-day vs 365-day contradiction
Resolved as:
- 365 days = active default baseline
- variable horizon = required parameterization capability
- 356-day behavior = non-default legacy/variant candidate requiring later cleanup or explicit retention rationale

### TV and OI governance weakness
Resolved as:
- both artifact classes become first-class governed objects in the target V-Model-light structure

## Migration rule derived from these decisions
All future requirement migration and cleanup work should distinguish explicitly between:
1. historical-origin statements
2. active default baseline statements
3. parameterization capabilities
4. provisional or legacy variants

This rule is necessary to avoid freezing historical project evolution noise into the new machine-readable baseline.

## Immediate next-step implication
The next migration step should now be able to proceed with substantially lower ambiguity.

Recommended next work package after this decision package:
- begin first YAML-oriented migration prep for:
  - `PSR-*`
  - `PSyR-*`
  - `PSwR-*`
- while simultaneously defining first-class representations for:
  - `TV-*`
  - `OI-*`

## Summary
Authoritative migration baseline is now:
- default country scope: 10 countries
- country count: parameterizable
- default historical horizon: 365 days
- historical horizon: parameterizable
- `TV-*`: first-class verification artifacts
- `OI-*`: first-class governed issue artifacts
- open issues: resolve autonomously where safe; escalate only high-impact semantic ambiguities
