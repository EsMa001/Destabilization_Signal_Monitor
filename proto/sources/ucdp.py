from __future__ import annotations

"""
Traceability:
- PSwR-004
- PSwR-001
- PM-003
"""

import csv
from pathlib import Path

from proto.models import SourceRecord
from proto.sources.common import parse_float, parse_iso_date


def load_ucdp_records(path: Path) -> list[SourceRecord]:
    """
    Load UCDP records.

    Traceability:
    - PSwR-004
    - PSwR-001
    """
    records: list[SourceRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            date_value = parse_iso_date(row["date"])
            raw_value = parse_float(
                row.get("raw_value", row.get("value", "")),
                field_name="raw_value",
            )
            category = row["event_type"].strip().lower()
            metadata = {
                key: value
                for key, value in row.items()
                if key not in {"date", "country", "event_type", "raw_value", "value"}
            }
            records.append(
                SourceRecord(
                    source_id="ucdp",
                    country=row["country"],
                    date=date_value,
                    category=category,
                    raw_value=raw_value,
                    metadata=metadata,
                )
            )
    return records
