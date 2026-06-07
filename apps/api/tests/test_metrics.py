def test_metrics_endpoint_returns_prometheus_format(client):
    # Generate at least one request so the metrics have data
    client.get("/health")

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_metrics_includes_http_counters(client):
    client.get("/health")
    body = client.get("/metrics").text

    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "http_requests_in_flight" in body


def test_metrics_includes_downstream_counters(client):
    body = client.get("/metrics").text

    assert "downstream_requests_total" in body
    assert "downstream_request_duration_seconds" in body
