from __future__ import annotations

"""
Source adapter utilities.

Traceability:
- PSwR-001
"""

from datetime import date


def parse_iso_date(raw: str) -> date:
    """
    Parse YYYY-MM-DD into a date.

    Traceability:
    - PSwR-003
    - PSwR-004
    - PM-005
    """
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"invalid date value: {raw!r}") from exc


def parse_float(raw: str, *, field_name: str) -> float:
    """
    Parse numeric value with clear error context.

    Traceability:
    - PSwR-003
    - PSwR-004
    """
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"invalid float in {field_name}: {raw!r}") from exc
