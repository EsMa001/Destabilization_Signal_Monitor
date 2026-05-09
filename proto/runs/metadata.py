from __future__ import annotations

"""
Traceability:
- PSyR-008
- PSwR-001
"""

from pathlib import Path
import json
from dataclasses import asdict
from .models import RunMetadata

def write_run_metadata(metadata: RunMetadata, out_path: Path) -> None:
    """
    Traceability:
    - PSyR-008
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(asdict(metadata), indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
