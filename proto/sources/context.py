from __future__ import annotations

"""
Traceability:
- PSwR-006
- PSwR-001
- PM-003
"""

from dataclasses import dataclass
from pathlib import Path
import csv

from proto.sources.common import parse_float


@dataclass
class ContextRecord:
    country: str
    economic_vulnerability_score: float
    economic_vulnerability_note: str
    hybrid_vulnerability_score: float
    hybrid_vulnerability_note: str
    governance_stress_score: float
    governance_stress_note: str


def load_context_records(path: Path) -> list[ContextRecord]:
    """
    Load curated context records.

    Traceability:
    - PSwR-006
    - PSwR-001
    """
    rows: list[ContextRecord] = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                ContextRecord(
                    country=row["country"],
                    economic_vulnerability_score=parse_float(
                        row["economic_vulnerability_score"],
                        field_name="economic_vulnerability_score",
                    ),
                    economic_vulnerability_note=row["economic_vulnerability_note"],
                    hybrid_vulnerability_score=parse_float(
                        row["hybrid_vulnerability_score"],
                        field_name="hybrid_vulnerability_score",
                    ),
                    hybrid_vulnerability_note=row["hybrid_vulnerability_note"],
                    governance_stress_score=parse_float(
                        row["governance_stress_score"],
                        field_name="governance_stress_score",
                    ),
                    governance_stress_note=row["governance_stress_note"],
                )
            )
    return rows
