from __future__ import annotations

"""
Shared API schemas.

Traceability:
- AP-06
- AP-07
"""

from typing import Any

from pydantic import BaseModel, Field


class ApiErrorPayload(BaseModel):
    code: str = Field(description="Stable machine-readable error code.")
    message: str = Field(description="Human-readable error message.")
    details: Any | None = Field(
        default=None,
        description="Optional structured error details.",
    )
    trace_id: str = Field(description="Per-error trace identifier.")


class ErrorEnvelope(BaseModel):
    error: ApiErrorPayload

