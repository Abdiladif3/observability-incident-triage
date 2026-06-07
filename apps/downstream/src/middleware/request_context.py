"""Per-request context: generate or propagate request ID, bind to structlog, emit access log."""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = structlog.get_logger("downstream.access")

REQUEST_ID_HEADER = "x-request-id"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            log.exception("request.failed", duration_ms=duration_ms)
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        log.info(
            "request.completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
