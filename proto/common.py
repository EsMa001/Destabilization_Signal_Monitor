from __future__ import annotations

"""
Cross-layer shared helpers.

Traceability:
- PSwR-001
- PSyR-001
"""

from datetime import date
from typing import Iterable

COUNTRY_ALIASES = {
    "iran": "Iran",
    "israel": "Israel",
    "ukraine": "Ukraine",
    "russia": "Russia",
    "japan": "Japan",
    "china": "China",
    "taiwan": "Taiwan",
    "poland": "Poland",
    "nigeria": "Nigeria",
    "germany": "Germany",
    "deutschland": "Germany",
}


def canonical_country(raw_country: str) -> str:
    """
    Normalize country names into V1 canonical form.

    Traceability:
    - PSyR-001
    - OI-001
    """
    normalized = raw_country.strip().lower()
    return COUNTRY_ALIASES.get(normalized, raw_country.strip())


def sorted_unique_dates(values: Iterable[date]) -> list[date]:
    """
    Deterministic sorted unique-date helper.

    Traceability:
    - PM-005
    """
    return sorted(set(values))
