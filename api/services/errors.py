from __future__ import annotations

"""
API error helpers.

Traceability:
- AP-07
"""

from dataclasses import dataclass
from uuid import uuid4


@dataclass(slots=True)
class ApiServiceError(Exception):
    code: str
    message: str
    status_code: int
    details: object | None = None
    trace_id: str | None = None

    def __post_init__(self) -> None:
        # Traceability:
        # - AP-07
        self.trace_id = self.trace_id or uuid4().hex
        super().__init__(self.message)


def error_payload(error: ApiServiceError) -> dict[str, object]:
    # Traceability:
    # - AP-07
    return {
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
            "trace_id": error.trace_id,
        }
    }

