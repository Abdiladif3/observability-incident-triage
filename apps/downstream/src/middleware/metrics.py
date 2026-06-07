"""Records Prometheus HTTP metrics for every request."""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.metrics import (
    http_request_duration_seconds,
    http_requests_in_flight,
    http_requests_total,
)

NOT_FOUND_PATH_LABEL = "__not_found__"
METRICS_ENDPOINT_PATH = "/metrics"


def _path_template(request: Request, response: Response | None) -> str:
    route = request.scope.get("route")
    if route is not None and hasattr(route, "path"):
        return route.path
    if response is not None and response.status_code == 404:
        return NOT_FOUND_PATH_LABEL
    return request.url.path


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == METRICS_ENDPOINT_PATH:
            return await call_next(request)

        http_requests_in_flight.inc()
        start = time.perf_counter()
        response: Response | None = None

        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.perf_counter() - start
            http_requests_in_flight.dec()

            path = _path_template(request, response)
            status = str(response.status_code) if response is not None else "500"

            http_requests_total.labels(
                method=request.method,
                path=path,
                status=status,
            ).inc()
            http_request_duration_seconds.labels(
                method=request.method,
                path=path,
            ).observe(duration)
