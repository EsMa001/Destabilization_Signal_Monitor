# WP-13 Function-level traceability hardening

Date: 2026-05-10
Branch: hermes/vmodel-assessment

## Scope

Hardens the Python implementation traceability baseline after the function-level audit.

## Outcome

- Python functions audited: 480
- Python functions with traceability annotation: 480
- Function-level links written to `vmodel/traceability/trace_links.yaml`: 2462
- Covered source areas: `proto/`, `api/`, `tests/`, `tools/`, `scripts/`, root `main.py`

## Link target classes

- ALG: 218
- AP: 171
- OI: 14
- PM: 229
- PSR: 472
- PSwR: 864
- PSyR: 285
- SUP: 54
- TV: 155

## Governance note

`AP-*` and `SUP-*` identifiers are retained for API/frontend-handoff and operational-support scope because they already exist in `docs/traceability/TraceabilityMatrix.md`. Product and verification IDs remain linked directly where the function annotations carry `PSR-*`, `PSyR-*`, `PSwR-*`, `PM-*`, `ALG-*`, or `TV-*` evidence.

## Validation notes

- YAML parsing and trace-link coverage check passed: 480 Python functions, 0 missing annotations, 0 unlinked unique function IDs.
- Python compile check passed for all git-tracked Python files.
- Full pytest suite passed: 120 passed.
- During verification, two pre-existing test/compatibility drifts were fixed:
  - `ApiServiceError.__post_init__` now initializes `Exception` explicitly, avoiding the `super()`/slotted dataclass runtime failure on API error paths.
  - Historical snapshot tests now verify the `snapshot_source_date` selected by the implementation and accept the governed lagged-valid mode `historical_latest_valid_before_run_date`.
