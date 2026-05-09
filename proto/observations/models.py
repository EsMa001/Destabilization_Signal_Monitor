from __future__ import annotations

"""
Canonical observation models for V3.1 multi-source path.

Traceability:
- PSyR-018
- PSwR-036
- PSwR-037
- PSwR-038
- PSwR-044
- PM-016
- PM-022
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class ObservationRecord:
    """
    Canonical source observation.

    Traceability:
    - PSyR-018
    - PSwR-036
    - PSwR-037
    """

    source_id: str
    layer: str
    signal_family: str
    country: str
    period_start: date
    period_end: date
    raw_value: float
    normalized_value: float
    unit: str
    provenance: str
    quality_completeness: float
    native_periodicity: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
