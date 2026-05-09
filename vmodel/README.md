# V-Model-Light Target Structure

This directory is the machine-readable governance target for migrating the current markdown-driven requirement system into a stricter requirements-as-code structure.

Migration principles:
- existing `docs/*` files remain source material during migration
- `vmodel/*` becomes the normalized target layer
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
