from __future__ import annotations

"""
Traceability:
- PSwR-005
- PSwR-001
- PM-003
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import csv

from proto.sources.common import parse_float, parse_iso_date


@dataclass
class BridgeRecord:
    date: date
    country: str
    event_type: str
    cluster: str
    subcluster: str
    severity: float
    description: str
    source_note: str
    confidence: str
    include_in_cluster: bool


def load_bridge_records(path: Path) -> list[BridgeRecord]:
    """
    Load bridge records.

    Traceability:
    - PSwR-005
    - PSwR-001
    """
    rows: list[BridgeRecord] = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            include_flag = row["include_in_cluster"].strip().lower()
            rows.append(
                BridgeRecord(
                    date=parse_iso_date(row["date"]),
                    country=row["country"],
                    event_type=row["event_type"],
                    cluster=row["cluster"].strip().lower(),
                    subcluster=row["subcluster"].strip().lower(),
                    severity=parse_float(row["severity"], field_name="severity"),
                    description=row["description"],
                    source_note=row["source_note"],
                    confidence=row["confidence"].strip().lower(),
                    include_in_cluster=include_flag in {"true", "1", "yes"},
                )
            )
    return rows
