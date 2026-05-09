# TestStrategy

## Test levels
- Unit tests
- Integration tests
- End-to-end tests
- Manual review markers for non-automatable checks

## Unit coverage
- config
- source loaders
- feature builders
- score logic
- thresholds
- trend
- confidence
- metadata
- run status

## Integration coverage
- GDELT -> tension
- UCDP + bridge -> escalation
- context -> vulnerability
- scoring -> stage/trend/confidence
- pipeline -> report/exports/plots

## End-to-end coverage
- standard mode full run
- all required outputs created
- run metadata created
- run comparison works
- reference run read/write works
- controlled snapshot change proves real deltas in `run_comparison.json` and `reference_comparison.json`

## Codex responsibility
Codex must implement and maintain tests together with the code.
