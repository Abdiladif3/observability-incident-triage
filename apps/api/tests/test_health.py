def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "api"


def test_health_attaches_request_id_header(client):
    response = client.get("/health")
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) > 0


def test_health_propagates_client_request_id(client):
    response = client.get("/health", headers={"X-Request-Id": "trace-abc-123"})
    assert response.headers["x-request-id"] == "trace-abc-123"
