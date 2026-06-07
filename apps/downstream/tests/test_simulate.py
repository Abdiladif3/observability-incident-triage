def test_status_starts_in_normal_mode(client):
    response = client.get("/simulate/status")
    assert response.status_code == 200
    assert response.json()["mode"] == "normal"


def test_simulate_latency_sets_mode_and_latency(client):
    response = client.post("/simulate/latency", json={"latency_ms": 150})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "latency"
    assert body["latency_ms"] == 150


def test_simulate_errors_sets_mode_and_rate(client):
    response = client.post("/simulate/errors", json={"error_rate": 0.25})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "errors"
    assert body["error_rate"] == 0.25


def test_simulate_outage_sets_mode(client):
    response = client.post("/simulate/outage", json={})
    assert response.status_code == 200
    assert response.json()["mode"] == "outage"


def test_simulate_recovery_resets_mode(client):
    client.post("/simulate/outage", json={})
    response = client.post("/simulate/recovery", json={})
    assert response.status_code == 200
    assert response.json()["mode"] == "normal"
