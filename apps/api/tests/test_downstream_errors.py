"""Verify the api normalizes downstream failures into actionable error responses."""

import httpx


def test_downstream_503_returns_502_with_recommended_action(client, mock_downstream):
    mock_downstream.expect("GET", "/pricing/quote/AAPL", httpx.Response(503))

    response = client.get("/market/quote/AAPL")

    assert response.status_code == 502
    body = response.json()
    assert body["error"] == "downstream_unavailable"
    assert body["downstream_status"] == 503
    assert "recommended_action" in body
    assert "retry" in body["recommended_action"].lower()


def test_downstream_500_returns_502(client, mock_downstream):
    mock_downstream.expect("GET", "/pricing/quote/AAPL", httpx.Response(500, json={"err": "boom"}))

    response = client.get("/market/quote/AAPL")

    assert response.status_code == 502
    body = response.json()
    assert body["error"] == "downstream_error"
    assert body["downstream_status"] == 500


def test_downstream_404_passes_through(client, mock_downstream):
    mock_downstream.expect("GET", "/pricing/quote/AAPL", httpx.Response(404, json={"detail": "nope"}))

    response = client.get("/market/quote/AAPL")

    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "not_found"
