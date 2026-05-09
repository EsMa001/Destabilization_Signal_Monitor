# AGENTS.md

## Mission
Develop the complete software for **Country Destabilization Prototype V1** requirements-driven from the markdown documents in this repository.

## Source of truth
Use these files as authoritative project context:
- `docs/requirements/ProtoScope.md`
- `docs/requirements/ProtoSR.md`
- `docs/requirements/ProtoSyR.md`
- `docs/requirements/ProtoSwR.md`
- `docs/method/ProtoMethod.md`
- `docs/method/ProtoScoring.md`
- `docs/method/ProtoRunbook.md`
- `docs/testing/TestStrategy.md`
- `docs/traceability/TraceabilityMatrix.md`
- `IMPLEMENT.md`
- `README.md`

## Non-negotiable rules
1. Work requirements-driven.
2. Keep traceability between requirements, algorithms, code, and tests.
3. Develop tests with the implementation.
4. Work in small, reviewable steps.
5. Prefer simple, explainable logic in V1.
6. Preserve strict separation of:
   - raw data
   - features
   - scores
   - presentation / outputs
7. If requirements are missing, unclear, or contradictory:
   - document the issue
   - propose a solution
   - proceed only with minimal, explicit assumptions

## Traceability conventions
- `PSR-*` stakeholder requirements
- `PSyR-*` system requirements
- `PSwR-*` software requirements
- `PM-*` method rules
- `ALG-*` algorithms
- `TV-*` test case IDs

All important modules, public functions, and tests must reference relevant IDs.

## Required test levels
- unit tests
- integration tests
- end-to-end tests
- manual-review markers for non-automatable checks

## Required run metadata
- run timestamp
- countries
- time windows
- query version
- scoring version
- bridge file version
- context table version

## Required outputs
- report / handout
- plots
- scores export
- features export
- summary export
- run status
- run comparison
- reference run support

## Definition of done
A work item is done only if:
- implementation exists
- traceability exists
- tests exist / were updated
- relevant checks passed
- documentation was updated
- open requirement gaps are recorded when applicable
