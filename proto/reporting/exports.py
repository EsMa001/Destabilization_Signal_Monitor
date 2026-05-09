from __future__ import annotations

"""
Structured export writers.

Traceability:
- PSyR-007
- PSwR-001
"""

from dataclasses import asdict, is_dataclass
from pathlib import Path
import csv
import json


def _serialize_value(value):
    # Traceability:
    # - PSyR-007
    # - PSwR-001
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _records_to_rows(records: list[object]) -> list[dict]:
    # Traceability:
    # - PSyR-007
    # - PSwR-001
    rows: list[dict] = []
    for record in records:
        if is_dataclass(record):
            payload = asdict(record)
        else:
            payload = dict(record)
        rows.append({key: _serialize_value(value) for key, value in payload.items()})
    return rows


def write_csv_records(records: list[object], out_path: Path) -> None:
    """
    Write dataclass or dict records to CSV.

    Traceability:
    - PSyR-007
    """
    rows = _records_to_rows(records)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        out_path.write_text("", encoding="utf-8")
        return
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json_records(records: list[object], out_path: Path) -> None:
    """
    Write dataclass or dict records to JSON.

    Traceability:
    - PSyR-007
    """
    rows = _records_to_rows(records)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
