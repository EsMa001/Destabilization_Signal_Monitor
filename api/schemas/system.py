from __future__ import annotations

"""
System-level API schemas.

Traceability:
- AP-02
- AP-06
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Service health indicator.")
    api_version: str = Field(description="Semantic API version.")
    timestamp: str = Field(description="UTC timestamp in ISO-8601 format.")


class InfoResponse(BaseModel):
    project_name: str
    api_name: str
    api_version: str
    timestamp: str
    python_version: str
    environment: str

