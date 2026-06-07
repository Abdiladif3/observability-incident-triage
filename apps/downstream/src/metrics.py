"""Prometheus metric definitions for the downstream service."""

from prometheus_client import Counter, Gauge, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests received, labeled by method, route template, and status.",
    labelnames=["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request handling duration in seconds, labeled by method and route template.",
    labelnames=["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

http_requests_in_flight = Gauge(
    "http_requests_in_flight",
    "Number of HTTP requests currently being handled.",
)
