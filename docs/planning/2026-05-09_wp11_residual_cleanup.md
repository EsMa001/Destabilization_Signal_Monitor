# WP-11 Residual Provisional Cleanup and Verification Finalization

Status: residual cleanup and verification finalization
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`

## Purpose
This work package closes the remaining low-risk governance gaps after WP-10 by:
- deciding the remaining borderline software-requirement cases more explicitly
- removing the last `GV-*` placeholders
- promoting the verification baseline to a fully governed `TV-*` representation

## Target artifacts updated
- `vmodel/requirements/software_requirements.yaml`
- `vmodel/verification/test_specifications.yaml`
- `vmodel/change/open_issues.yaml`

## Main results

### 1. Remaining provisional software set reduced again
Status before WP-11:
- provisional requirements: 3
  - `PSwR-034`
  - `PSwR-046`
  - `PSwR-061`

Status after WP-11:
- provisional requirements: 2
  - `PSwR-034`
  - `PSwR-061`

- `PSwR-046` normalized to `implemented_requirement`

### 2. Why `PSwR-046` was promoted
`PSwR-046` had strong implementation evidence already, but WP-10 left it provisional because the verification story was still implicit.

WP-11 resolves that by adding an explicit governed verification artifact:
- `TV-PSwR-046-001`

Evidence basis used:
- `tests/test_fusion.py`
- `tests/test_pipeline.py`

Engineering reasoning:
- the requirement no longer suffers from a merely indirect verification-governance gap
- implementation, traceability, and requirement-level verification now line up strongly enough to justify `implemented_requirement`

### 3. Why `PSwR-034` and `PSwR-061` remain provisional
These two were intentionally not over-promoted.

#### `PSwR-034`
Still provisional because:
- historical helper-source handling remains intentionally time-constant
- full historical source versioning is still absent
- this is a real methodological limitation, not just stale documentation

#### `PSwR-061`
Still provisional because:
- the loader and canonical transformation path are implemented
- but semantic governance for narrative taxonomy, direction labels, and editorial review remains open
- therefore the implementation is operational, but not yet semantically fully governed

### 4. Last `GV-*` placeholders removed
Before WP-11, the only remaining placeholders were:
- `GV-PSwR-019-001`
- `GV-PSwR-097-001`

WP-11 promotes both into governed first-class `TV-*` artifacts:
- `TV-PSwR-019-001`
- `TV-PSwR-097-001`

#### `TV-PSwR-019-001`
Nature:
- governed mixed verification artifact

Rationale:
- requirement traceability in code/tests is not purely a functional runtime property
- it legitimately combines:
  - regression execution (`python -m pytest`)
  - manual review of requirement-reference annotations

This is therefore modeled honestly as a governed mixed-review artifact, not forced into a fake pure automation claim.

#### `TV-PSwR-097-001`
Nature:
- governed automated verification artifact

Rationale:
- the comparison-baseline enforcement behavior is sufficiently specific to be governed through the traced config-validation test path
- the branch baseline can therefore promote this from placeholder to explicit `TV-*`

### 5. Verification baseline is now fully `TV-*` governed
Status after WP-11:
- total verification entries: 156
- explicit `TV-*` entries: 156
- remaining `GV-*` placeholders: 0

This is an important governance milestone.

It means:
- the migrated verification baseline no longer contains temporary placeholder identities
- all currently retained verification artifacts are now governed as explicit first-class entries

### 6. OI-046 tightened further
`OI-046` was already resolved in WP-10.

WP-11 strengthens the resolution note:
- the remaining placeholder cleanup is now complete
- the migrated verification baseline has no residual `GV-*` debt anymore

## Current baseline state after WP-11
Software requirement status split:
- `implemented_requirement`: 121
- `provisional_requirement`: 2
- `retired_requirement`: 1

Remaining genuinely provisional software requirements:
- `PSwR-034`
- `PSwR-061`

Interpretation:
- what remains open is now mostly methodological/semantic, not structural governance debt

## Recommended next step
The migration/governance baseline is now clean enough that the next useful work package should probably stop focusing on meta-governance and instead address one of the two genuinely open substance areas:

Option A:
- resolve historical helper-source treatment / versioning posture around `PSwR-034`

Option B:
- define semantic governance for narrative input around `PSwR-061`

## Summary
WP-11 closes the residual low-risk governance backlog from WP-10.

Most important practical result:
- the migrated branch baseline now has only two genuinely provisional software requirements left, and the verification baseline is fully governed with explicit `TV-*` artifact identities.