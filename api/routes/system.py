from __future__ import annotations

"""
System routes.

Traceability:
- AP-02
"""

from datetime import UTC, datetime
import os
import platform

from fastapi import APIRouter

from api.schemas.system import HealthResponse, InfoResponse
from api.services.config_service import get_raw_config

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        api_version="v1",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get("/info", response_model=InfoResponse)
def get_info() -> InfoResponse:
    raw_config = get_raw_config()
    return InfoResponse(
        project_name=str(raw_config.get("project_name", "country-destabilization-proto")),
        api_name="destabilization-signal-monitor-api",
        api_version="v1",
        timestamp=datetime.now(UTC).isoformat(),
        python_version=platform.python_version(),
        environment=os.environ.get("APP_ENV", "dev"),
    )

