from __future__ import annotations

"""
Structured governance/political-stability adapter for V4.2 `Governance` layer.

Traceability:
- PSR-023
- PSyR-034
- PSwR-091
- PSwR-092
- PSwR-039
- PSwR-040
- PM-049
- PM-050
- ALG-033
- ALG-034
"""

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from proto.common import canonical_country
from proto.observations.adapter_contract import enforce_adapter_contract
from proto.observations.models import ObservationRecord
from proto.observations.normalization import normalize_series
from proto.sources.common import parse_float, parse_iso_date

SOURCE_ID = "governance_input"
LAYER = "Governance"
SIGNAL_FAMILY = "governance_instability_pressure"


def _clamp_01(value: float) -> float:
    # Traceability:
    # - PSR-023
    # - PSyR-034
    # - PSwR-091
    # - PSwR-092
    # - PSwR-039
    # - PSwR-040
    return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class GovernanceInputRecord:
    period_start: date
    period_end: date
    country: str
    government_effectiveness: float
    institutional_trust: float
    political_polarization: float
    protest_pressure: float
    policy_blockage: float
    resilience_buffer: float
    provenance: str
    quality_completeness: float


def _derive_raw_signal(record: GovernanceInputRecord) -> float:
    """
    Transparent governance-instability mapping.

    Components:
    - institutional_erosion: low governmental effectiveness and low institutional trust
    - contention_pressure: polarization, protest pressure, policy blockage
    - resilience_dampener: high resilience can absorb part of fragility pressure
    """
    # Traceability:
    # - PSR-023
    # - PSyR-034
    # - PSwR-091
    # - PSwR-092
    # - PSwR-039
    # - PSwR-040
    institutional_erosion = (
        0.55 * (1.0 - _clamp_01(record.government_effectiveness))
        + 0.45 * (1.0 - _clamp_01(record.institutional_trust))
    )
    contention_pressure = (
        0.40 * _clamp_01(record.political_polarization)
        + 0.35 * _clamp_01(record.protest_pressure)
        + 0.25 * _clamp_01(record.policy_blockage)
    )
    fragility_pressure = 0.60 * institutional_erosion + 0.40 * contention_pressure
    resilience_dampener = 1.0 - 0.25 * _clamp_01(record.resilience_buffer)
    return round(_clamp_01(fragility_pressure * resilience_dampener), 4)


def load_governance_input_records(path: Path) -> list[GovernanceInputRecord]:
    """
    Load structured governance rows.

    Traceability:
    - PSwR-091
    - PSwR-039
    """
    rows: list[GovernanceInputRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                GovernanceInputRecord(
                    period_start=parse_iso_date(row["period_start"]),
                    period_end=parse_iso_date(row["period_end"]),
                    country=canonical_country(row["country"]),
                    government_effectiveness=parse_float(
                        row["government_effectiveness"],
                        field_name="government_effectiveness",
                    ),
                    institutional_trust=parse_float(
                        row["institutional_trust"],
                        field_name="institutional_trust",
                    ),
                    political_polarization=parse_float(
                        row["political_polarization"],
                        field_name="political_polarization",
                    ),
                    protest_pressure=parse_float(
                        row["protest_pressure"],
                        field_name="protest_pressure",
                    ),
                    policy_blockage=parse_float(
                        row["policy_blockage"],
                        field_name="policy_blockage",
                    ),
                    resilience_buffer=parse_float(
                        row["resilience_buffer"],
                        field_name="resilience_buffer",
                    ),
                    provenance=row["provenance"].strip() or "GOVERNANCE_snapshot",
                    quality_completeness=parse_float(
                        row["quality_completeness"],
                        field_name="quality_completeness",
                    ),
                )
            )
    return rows


def load_governance_input_observations(
    path: Path,
    *,
    normalization_method: str,
    normalization_scope: str = "per_country",
    baseline_value: float | None = None,
    baseline_scale: float | None = None,
) -> list[ObservationRecord]:
    """
    Load governance input as canonical `Governance` observations.

    Traceability:
    - PSwR-091
    - PSwR-092
    - PSwR-039
    - PSwR-040
    """
    rows = load_governance_input_records(path)
    normalized_scope = normalization_scope.strip().lower()
    if normalized_scope not in {"per_country", "global"}:
        raise ValueError("normalization_scope must be 'per_country' or 'global'")

    observations: list[ObservationRecord] = []
    by_country: dict[str, list[GovernanceInputRecord]] = defaultdict(list)
    for row in rows:
        by_country[row.country].append(row)

    if normalized_scope == "global":
        ordered_rows: list[GovernanceInputRecord] = []
        for country, values in sorted(by_country.items()):
            ordered_rows.extend(sorted(values, key=lambda item: item.period_end))
        raw_signals = [_derive_raw_signal(item) for item in ordered_rows]
        normalized_values = normalize_series(
            raw_signals,
            method=normalization_method,
            baseline_value=baseline_value,
            baseline_scale=baseline_scale,
        )
        for row, raw_signal, normalized_value in zip(ordered_rows, raw_signals, normalized_values):
            observations.append(
                ObservationRecord(
                    source_id=SOURCE_ID,
                    layer=LAYER,
                    signal_family=SIGNAL_FAMILY,
                    country=row.country,
                    period_start=row.period_start,
                    period_end=row.period_end,
                    raw_value=raw_signal,
                    normalized_value=normalized_value,
                    unit="governance_instability_index",
                    provenance=row.provenance,
                    quality_completeness=_clamp_01(row.quality_completeness),
                    native_periodicity="monthly",
                    metadata={
                        "government_effectiveness": row.government_effectiveness,
                        "institutional_trust": row.institutional_trust,
                        "political_polarization": row.political_polarization,
                        "protest_pressure": row.protest_pressure,
                        "policy_blockage": row.policy_blockage,
                        "resilience_buffer": row.resilience_buffer,
                        "normalization_scope": normalized_scope,
                        "mapping": (
                            "instability=(0.60*institutional_erosion+0.40*contention_pressure)"
                            "*resilience_dampener"
                        ),
                    },
                )
            )
        return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)

    for country, values in sorted(by_country.items()):
        sorted_values = sorted(values, key=lambda item: item.period_end)
        raw_signals = [_derive_raw_signal(item) for item in sorted_values]
        normalized_values = normalize_series(
            raw_signals,
            method=normalization_method,
            baseline_value=baseline_value,
            baseline_scale=baseline_scale,
        )
        for row, raw_signal, normalized_value in zip(sorted_values, raw_signals, normalized_values):
            observations.append(
                ObservationRecord(
                    source_id=SOURCE_ID,
                    layer=LAYER,
                    signal_family=SIGNAL_FAMILY,
                    country=country,
                    period_start=row.period_start,
                    period_end=row.period_end,
                    raw_value=raw_signal,
                    normalized_value=normalized_value,
                    unit="governance_instability_index",
                    provenance=row.provenance,
                    quality_completeness=_clamp_01(row.quality_completeness),
                    native_periodicity="monthly",
                    metadata={
                        "government_effectiveness": row.government_effectiveness,
                        "institutional_trust": row.institutional_trust,
                        "political_polarization": row.political_polarization,
                        "protest_pressure": row.protest_pressure,
                        "policy_blockage": row.policy_blockage,
                        "resilience_buffer": row.resilience_buffer,
                        "normalization_scope": normalized_scope,
                        "mapping": (
                            "instability=(0.60*institutional_erosion+0.40*contention_pressure)"
                            "*resilience_dampener"
                        ),
                    },
                )
            )
    return enforce_adapter_contract(source_id=SOURCE_ID, observations=observations)
