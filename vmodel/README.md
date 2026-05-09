# V-Model-Light Target Structure

This directory is the machine-readable governance target for migrating the current markdown-driven requirement system into a stricter requirements-as-code structure.

Migration principles:
- existing `docs/*` files remain source material during migration
- `vmodel/*` becomes the normalized target layer
- requirement artifacts must support bidirectional traceability
  - parent links are mandatory when a parent exists
  - child links are mandatory when a child exists
- no requirement is considered fully migrated until its baseline role is classified explicitly as one of:
  - `active_baseline`
  - `historical_origin`
  - `parameterized_capability`
  - `legacy_variant`

Authoritative baseline decisions currently in force:
- default country scope: 10 countries
- country scope must remain parameterizable
- default historical horizon: 365 days
- historical horizon must remain parameterizable
- `TV-*` are first-class verification artifacts
- `OI-*` are first-class governed issue artifacts


Authoritative source-of-truth rule on this migration branch:
- for artifacts already migrated into `vmodel/*`, the `vmodel/*` representation is authoritative on `hermes/vmodel-assessment`
- legacy `docs/*` requirement and traceability markdown remains source material and historical evidence, but no longer overrides migrated YAML artifacts
- if migrated YAML and legacy markdown disagree, the discrepancy must be resolved in favor of the normalized `vmodel/*` baseline and tracked as governance debt only if backward-document compatibility is still needed
