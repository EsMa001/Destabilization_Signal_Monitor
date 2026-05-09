from __future__ import annotations

"""
FastAPI application entrypoint.

Traceability:
- AP-01
- AP-07
"""

from datetime import UTC, datetime
import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.routes.options import router as options_router
from api.routes.runs import router as runs_router
from api.routes.system import router as system_router
from api.schemas.common import ErrorEnvelope
from api.services.errors import ApiServiceError, error_payload

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Country Destabilization API",
    version="0.1.0",
    description="FastAPI bridge for frontend access to the existing proto analysis core.",
)

app.include_router(system_router, prefix="/api/v1", tags=["system"])
app.include_router(options_router, prefix="/api/v1", tags=["options"])
app.include_router(runs_router, prefix="/api/v1", tags=["runs"])


@app.exception_handler(ApiServiceError)
async def handle_api_service_error(_: Request, exc: ApiServiceError) -> JSONResponse:
    # Traceability:
    # - AP-01
    # - AP-07
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc),
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Traceability:
    # - AP-01
    # - AP-07
    trace_id = uuid4().hex
    payload = ErrorEnvelope(
        error={
            "code": "validation_error",
            "message": "Request validation failed.",
            "details": exc.errors(),
            "trace_id": trace_id,
        }
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # Traceability:
    # - AP-01
    # - AP-07
    if isinstance(exc, StarletteHTTPException):
        return await http_exception_handler(request, exc)

    trace_id = uuid4().hex
    logger.exception("Unhandled API exception trace_id=%s", trace_id)
    payload = ErrorEnvelope(
        error={
            "code": "internal_error",
            "message": "Unhandled internal API error.",
            "details": {
                "timestamp": datetime.now(UTC).isoformat(),
            },
            "trace_id": trace_id,
        }
    )
    return JSONResponse(status_code=500, content=payload.model_dump())

