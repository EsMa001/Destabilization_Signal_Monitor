from __future__ import annotations

"""
Adapter contract helpers for V3.1 source integrations.

Traceability:
- PSwR-039
- PSwR-044
- PM-016
- PM-018
"""

from proto.observations.models import ObservationRecord
from proto.observations.schema import validate_observation_records


class AdapterContractError(ValueError):
    """
    Raised when a source adapter violates the canonical adapter contract.

    Traceability:
    - PSwR-039
    """


def enforce_adapter_contract(
    *,
    source_id: str,
    observations: list[ObservationRecord],
) -> list[ObservationRecord]:
    """
    Enforce minimal adapter contract for canonical observations.

    Traceability:
    - PSwR-039
    - PSwR-044
    """
    if not observations:
        raise AdapterContractError(f"adapter {source_id!r} returned no observations")
    validate_observation_records(observations)
    for observation in observations:
        if observation.source_id != source_id:
            raise AdapterContractError(
                f"adapter {source_id!r} returned mismatching source_id {observation.source_id!r}"
            )
    return observations
