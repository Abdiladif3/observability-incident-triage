"""Async client + normalized error handling for the downstream pricing/risk service."""

import os
import time

import httpx
import structlog

from src.metrics import (
    downstream_request_duration_seconds,
    downstream_requests_total,
)
from src.middleware.request_context import REQUEST_ID_HEADER

log = structlog.get_logger("api.downstream")


class DownstreamError(Exception):
    """Raised when a downstream call cannot produce a usable response.

    The ``status_code`` is what the API should return to its own caller. The
    original downstream status (if any) is preserved separately for debugging.
    """

    def __init__(
        self,
        *,
        status_code: int,
        error: str,
        message: str,
        recommended_action: str | None = None,
        downstream_status: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error = error
        self.message = message
        self.recommended_action = recommended_action
        self.downstream_status = downstream_status


_client: httpx.AsyncClient | None = None


def _build_client() -> httpx.AsyncClient:
    base_url = os.getenv("DOWNSTREAM_BASE_URL", "http://localhost:8001")
    timeout_seconds = float(os.getenv("DOWNSTREAM_TIMEOUT_SECONDS", "2"))
    return httpx.AsyncClient(base_url=base_url, timeout=timeout_seconds)


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = _build_client()
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _propagated_headers() -> dict[str, str]:
    request_id = structlog.contextvars.get_contextvars().get("request_id")
    if request_id:
        return {REQUEST_ID_HEADER: request_id}
    return {}


def _classify(response_status: int) -> str:
    if response_status >= 500:
        return "server_error"
    if response_status >= 400:
        return "client_error"
    return "success"


async def _call(target: str, method: str, path: str) -> httpx.Response:
    """Issue a downstream call, record metrics + logs, raise on transport errors."""
    client = get_client()
    start = time.perf_counter()

    try:
        response = await client.request(method, path, headers=_propagated_headers())
    except httpx.TimeoutException:
        duration = time.perf_counter() - start
        downstream_requests_total.labels(target=target, status="timeout").inc()
        downstream_request_duration_seconds.labels(target=target).observe(duration)
        log.warning("downstream.timeout", target=target, path=path, duration_ms=round(duration * 1000, 2))
        raise
    except httpx.ConnectError:
        duration = time.perf_counter() - start
        downstream_requests_total.labels(target=target, status="connect_error").inc()
        downstream_request_duration_seconds.labels(target=target).observe(duration)
        log.warning("downstream.connect_error", target=target, path=path, duration_ms=round(duration * 1000, 2))
        raise

    duration = time.perf_counter() - start
    status_label = _classify(response.status_code)
    downstream_requests_total.labels(target=target, status=status_label).inc()
    downstream_request_duration_seconds.labels(target=target).observe(duration)
    log.info(
        "downstream.call",
        target=target,
        path=path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )
    return response


def _normalize(target: str, response: httpx.Response, *, not_found_message: str) -> dict:
    if response.status_code == 200:
        return response.json()

    if response.status_code == 404:
        raise DownstreamError(
            status_code=404,
            error="not_found",
            message=not_found_message,
        )

    if response.status_code == 503:
        raise DownstreamError(
            status_code=502,
            error="downstream_unavailable",
            message=f"The {target} service returned a 503 response.",
            recommended_action="Retry with backoff. If persistent, check downstream provider status.",
            downstream_status=response.status_code,
        )

    raise DownstreamError(
        status_code=502,
        error="downstream_error",
        message=f"The {target} service returned HTTP {response.status_code}.",
        recommended_action="Check downstream service logs.",
        downstream_status=response.status_code,
    )


async def fetch_quote(symbol: str) -> dict:
    target = "pricing"
    try:
        response = await _call(target, "GET", f"/pricing/quote/{symbol}")
    except httpx.TimeoutException:
        raise DownstreamError(
            status_code=504,
            error="downstream_timeout",
            message=f"The {target} service did not respond within the timeout window.",
            recommended_action="Retry shortly. If persistent, verify the pricing service health.",
        )
    except httpx.ConnectError:
        raise DownstreamError(
            status_code=503,
            error="downstream_unavailable",
            message=f"Could not reach the {target} service.",
            recommended_action="Verify the pricing service is running and reachable from this API.",
        )

    return _normalize(target, response, not_found_message=f"No quote available for symbol '{symbol}'.")


async def fetch_account_margin(account_id: str) -> dict:
    target = "risk"
    try:
        response = await _call(target, "GET", f"/risk/account/{account_id}/margin")
    except httpx.TimeoutException:
        raise DownstreamError(
            status_code=504,
            error="downstream_timeout",
            message=f"The {target} service did not respond within the timeout window.",
            recommended_action="Retry shortly. If persistent, verify the risk service health.",
        )
    except httpx.ConnectError:
        raise DownstreamError(
            status_code=503,
            error="downstream_unavailable",
            message=f"Could not reach the {target} service.",
            recommended_action="Verify the risk service is running and reachable from this API.",
        )

    return _normalize(target, response, not_found_message=f"No margin record for account '{account_id}'.")
