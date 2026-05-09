# WP-12 Scope Clarification for Remaining Software Baseline Debt

Status: scope clarification and residual baseline closure
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`

## Purpose
This work package closes the last remaining provisional software requirements by clarifying baseline scope boundaries instead of letting future enhancement wishes continue to block already implemented requirements.

## Target artifacts updated
- `vmodel/requirements/software_requirements.yaml`
- `vmodel/change/open_issues.yaml`

## Main result
The migrated active software baseline now has:
- `implemented_requirement`: 123
- `provisional_requirement`: 0
- `retired_requirement`: 1 (`PSwR-068`)

That means:
- no active software requirement remains in a provisional state
- remaining uncertainty is now tracked as explicit future enhancement / governance debt, not as ambiguity in the current baseline

## Key engineering decision in WP-12
The remaining provisional cases were not unresolved because the implementation was absent.
They were unresolved because future enhancement space had been mixed into current-baseline requirement status.

WP-12 fixes that by separating:
- what the current branch baseline actually requires and implements
from
- what a future, richer method/governance layer could still add

## Requirement decisions

### 1. PSwR-034 -> implemented_requirement
Previous concern:
- helper-source treatment in historical mode is time-constant
- full historical source versioning is not implemented

WP-12 decision:
- the current baseline requirement is explicitly the constant-helper-source behavior
- the implementation and tests satisfy that requirement as written
- therefore the requirement itself is implemented

Important distinction:
- “future historized helper-source versioning would be useful”
  is not the same as
- “PSwR-034 is not yet implemented”

Result:
- `PSwR-034` is now `implemented_requirement`

### 2. PSwR-061 -> implemented_requirement
Previous concern:
- narrative loading exists
- but semantic governance for taxonomy, direction labels, and editorial review is still open

WP-12 decision:
- the current requirement is about structured narrative/expert input loading, canonical transformation, and assignment to the Narrative layer
- that behavior is implemented and verified
- semantic taxonomy/review policy is a higher-level governance extension, not a blocker for the loader requirement itself

Result:
- `PSwR-061` is now `implemented_requirement`

## Open-issue decisions

### 1. OI-017 resolved
Reason:
- the issue no longer blocks the current baseline once PSwR-034 is interpreted correctly as the constant-baseline behavior

Meaning after WP-12:
- historical helper-source versioning is not forgotten
- but it is now treated as future enhancement debt rather than unresolved current-baseline ambiguity

### 2. OI-031 resolved
Reason:
- the issue no longer blocks the current baseline once PSwR-061 is interpreted correctly as the implemented loader/transformation behavior

Meaning after WP-12:
- semantic governance for narrative inputs remains a future enhancement topic
- but it no longer keeps the current loader requirement provisional

## New forward-looking issues created
To preserve the remaining debt explicitly, WP-12 adds two new issues instead of leaving current requirements artificially provisional.

### OI-047
Topic:
- future historized helper-source versioning beyond the current constant-helper-source baseline

Purpose:
- keeps the potential future requirement visible
- avoids silently broadening PSwR-034

### OI-048
Topic:
- future semantic governance for narrative taxonomy, direction-label harmonization, and editorial review

Purpose:
- keeps the semantic-governance topic visible
- avoids silently broadening PSwR-061 beyond its current implemented scope

## Why this is the right engineering move
A requirement should stay provisional only when the current required behavior is genuinely not yet satisfied.

That was no longer true here.

By WP-11, the real situation was:
- current required software behavior existed
- verification existed
- remaining concerns were about future richer semantics and governance

Therefore the honest move is:
- mark the current requirement implemented
- track future expansion as separate issue debt

This makes the baseline cleaner and more truthful.

## Recommended next step
The software-baseline migration is now effectively complete.

Useful next directions are no longer baseline-cleanup steps but true follow-on engineering decisions, for example:
- define whether OI-047 should become a new historized-helper-source requirement package
- define whether OI-048 should become a narrative semantic-governance package
- begin similar closure work for system/stakeholder and issue-governance refinement if desired

## Summary
WP-12 closes the remaining active software provisional backlog by clarifying scope boundaries.

Most important practical result:
- the active migrated software baseline is now fully implemented, and the remaining uncertainty has been moved into explicit future enhancement issues instead of being left as requirement-status ambiguity.