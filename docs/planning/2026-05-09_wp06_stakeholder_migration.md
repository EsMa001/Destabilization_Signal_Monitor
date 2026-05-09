# WP-06 Stakeholder Requirement Migration Baseline

Status: initial stakeholder migration
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`

## Purpose
This work package performs the first populated migration into the `vmodel/` target layer by normalizing the stakeholder requirement set.

## What was migrated
Target artifact:
- `vmodel/requirements/stakeholder_requirements.yaml`

Migrated scope:
- all currently defined `PSR-*` entries from `docs/requirements/ProtoSR.md`

## Key migration decisions applied
Applied baseline decisions:
- default country scope = 10 countries
- country count remains parameterizable
- default historical horizon = 365 days
- historical horizon remains parameterizable

Applied migration rule:
- stakeholder statements were normalized toward active baseline intent, not copied mechanically when the original wording still reflected obsolete defaults or milestone wording

## Low-risk contradictions handled in this package

### 1. Three-country origin wording
Original issue:
- `PSR-002` and `PSR-006` still reflected a 3-country operational framing

Handled as:
- normalized to a 10-country default baseline
- configurability retained explicitly in the migrated stakeholder statements
- original wording retained only indirectly via source references and migration tags

### 2. 356-day wording in V4.3/V4.3.1 stakeholder layer
Original issue:
- `PSR-024` and `PSR-025` still used `356-day` wording

Handled as:
- normalized to default `365-day` horizon with explicit parameterization capability
- original variant context captured via migration tags such as `normalized_from_356_day_variant`

### 3. Milestone-style wording inside stakeholder requirements
Original issue:
- some stakeholder statements used milestone-style phrasing such as `first visible` or direct version-step wording

Handled as:
- converted into durable stakeholder-intent wording where the functionality is still part of the active product baseline
- version origin retained in migration tags instead of keeping milestone wording as the normative requirement text

## Bidirectional traceability note
Your additional requirement was incorporated:
- requirement artifacts now explicitly support parent and child trace fields

Current stakeholder state:
- `parent_stakeholder_ids` is present for all stakeholder requirements and currently empty, which is correct for the top layer
- `child_system_ids` is present for all stakeholder requirements but intentionally still empty

Reason:
- child system links cannot be populated responsibly until the formal `PSyR` derivation is done
- populating guessed child links now would create false traceability

Engineering judgment:
- it is better to have explicit empty child fields pending derivation than to create fabricated links

## Assessment of your proposed overall workflow
Your proposed workflow still makes sense and becomes stronger after this step:
1. normalize stakeholder requirements
2. derive system requirements from them
3. derive software requirements from the system layer
4. resolve contradictions during derivation
5. compare the revised chain against the current implementation afterward

This stakeholder migration step is therefore the correct starting point for the top-down chain.

## Recommended next work package
WP-07:
- derive first normalized `PSyR` layer from the migrated stakeholder layer
- populate bidirectional stakeholder <-> system links
- identify any stakeholder/system contradictions explicitly during derivation

## Summary
The stakeholder layer is now initialized in machine-readable form and aligned with the accepted default baseline decisions.

Most important practical result:
- the migration has now moved from pure preparation into the first normative requirement layer
- future derivation can now proceed top-down without re-litigating the already resolved country/horizon defaults
