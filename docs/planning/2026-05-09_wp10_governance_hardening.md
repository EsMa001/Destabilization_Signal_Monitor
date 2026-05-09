# WP-10 Governance Hardening and Provisional-Set Cleanup

Status: governance hardening and baseline normalization
Date: 2026-05-09
Working branch: `hermes/vmodel-assessment`

## Purpose
This work package reduces ambiguity in the migrated baseline by:
- cleaning up the explicitly provisional software-requirement subset
- declaring a clear source-of-truth rule for migrated artifacts
- hardening verification governance with direct test-trace evidence

## Target artifacts updated
- `vmodel/README.md`
- `vmodel/requirements/software_requirements.yaml`
- `vmodel/verification/test_specifications.yaml`
- `vmodel/change/open_issues.yaml`

## Main decisions and results

### 1. Source-of-truth decision on the migration branch
A governance decision is now explicit in `vmodel/README.md`:
- for artifacts already migrated into `vmodel/*`, the YAML representation is authoritative on `hermes/vmodel-assessment`
- legacy `docs/*` requirement and traceability markdown remains source material and historical evidence
- legacy markdown no longer overrides migrated YAML artifacts on this branch

Reason:
- WP-08 and WP-09 showed that the legacy markdown source set had already drifted from the actual recovered and traceable requirement baseline
- continuing dual authority would have kept the migration structurally unsafe

Practical consequence:
- migrated YAML artifacts now define the normative branch baseline
- legacy markdown drift is governance debt, not normative ambiguity

### 2. OI-045 resolved by governance decision
`OI-045` is now resolved.

Resolution logic:
- once `vmodel/*` is authoritative for migrated artifacts, the incompleteness of legacy markdown source files no longer corrupts the normative branch baseline

This does not mean the markdown files are perfect.
It means:
- they are no longer the deciding authority for migrated artifacts on this branch

### 3. Provisional software-requirement subset reduced
Status before WP-10:
- provisional `PSwR`: 8

Status after WP-10:
- provisional `PSwR`: 3
- retired `PSwR`: 1

Current remaining provisional set:
- `PSwR-034`
- `PSwR-046`
- `PSwR-061`

Retired from active baseline:
- `PSwR-068`

#### 3.1 Requirements normalized from provisional to implemented
The following requirements were normalized from `provisional_requirement` to `implemented_requirement`:
- `PSwR-040`
- `PSwR-041`
- `PSwR-042`
- `PSwR-045`

Rationale:
- explicit code traces exist
- direct explicit test-trace evidence exists
- the old traceability-matrix status was stale relative to the currently implemented baseline
- resolved issue context supports the stronger implemented reading

#### 3.2 Requirements intentionally left provisional
`PSwR-034` remains provisional because:
- helper-source treatment in historical mode still relies on time-constant simplification without full historical source versioning
- this is still explicitly open in `OI-017`

`PSwR-046` remains provisional because:
- implementation evidence is strong
- but explicit verification trace for group-score behavior is still indirect through shared fusion/pipeline tests rather than a refreshed dedicated legacy verification row

`PSwR-061` remains provisional because:
- narrative-input semantic validation, taxonomy control, and review workflow remain open
- this is still explicitly captured by `OI-031`

#### 3.3 Requirement retired from active baseline
`PSwR-068` was retired from the active baseline.

Reason:
- it is explicitly a transitional V3.2 rule that allowed `event` to remain `not_available`
- the current baseline already contains operational event integration
- therefore the transitional rule is no longer part of the active software baseline
- it is now treated as a legacy variant superseded by `PSwR-073`

### 4. Verification governance hardened from test-source evidence
WP-09 only used:
- explicit `TV-*` identifiers from the legacy traceability matrix
- `GV-*` placeholders for generic references

WP-10 adds a stronger evidence source:
- explicit `TV-*` identifiers discovered directly in test traceability annotations under `tests/*.py`

Result:
- total machine-readable verification entries: 155
- explicit `TV-*` entries: 153
- remaining `GV-*` placeholders: 2

Remaining `GV-*` placeholders:
- `GV-PSwR-019-001`
- `GV-PSwR-097-001`

Interpretation:
- almost all generic legacy verification references have now been converted into explicit verification artifacts by reading the tests directly rather than relying only on the legacy matrix
- only two cases remain as governance placeholders because a stronger explicit named artifact is still not available with sufficient certainty

### 5. OI-046 resolved by verification-governance hardening
`OI-046` is now resolved.

Resolution logic:
- software requirements now have machine-readable verification links in the YAML baseline
- additional explicit `TV-*` artifacts were derived directly from test traceability annotations
- `GV-*` remains only where no stronger explicit artifact can yet be justified

This means the previous governance gap is closed at the baseline-management level.

## Important engineering judgment
WP-10 intentionally did not try to “fix everything” by force.

Conservative choices made:
- requirements with still-real semantic or governance uncertainty remained provisional
- only one transitional requirement (`PSwR-068`) was retired because its supersession is explicit and low-risk
- not every remaining weak verification case was promoted aggressively; two `GV-*` placeholders remain on purpose

This keeps the baseline more credible than a blanket promotion of all formerly provisional or generic cases.

## Current software-baseline status after WP-10
- `implemented_requirement`: 120
- `provisional_requirement`: 3
- `retired_requirement`: 1

This is a substantially cleaner implementation-governance picture than after WP-09.

## Recommended next work package
WP-11:
- targeted treatment of the remaining genuinely provisional set:
  - `PSwR-034`
  - `PSwR-046`
  - `PSwR-061`
- explicit decision whether `GV-PSwR-019-001` and `GV-PSwR-097-001` should become named governed verification artifacts or remain governance placeholders
- optional refresh of legacy traceability markdown for backward-document compatibility only, not as primary authority

## Summary
WP-10 converted the migration branch from “YAML target under construction” into “YAML authoritative migrated baseline”.

Most important practical result:
- the migrated branch baseline now has a clear authority rule, a much smaller genuinely provisional software subset, and a significantly hardened verification-governance layer.