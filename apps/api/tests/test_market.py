import httpx


def test_get_quote_returns_downstream_data(client, mock_downstream):
    mock_downstream.expect(
        "GET",
        "/pricing/quote/NVDA",
        httpx.Response(
            200,
            json={
                "symbol": "NVDA",
                "bid": "875.40",
                "ask": "875.80",
                "last": "875.60",
                "volume": 1,
                "as_of": "2026-06-07T12:00:00+00:00",
            },
        ),
    )

    response = client.get("/market/quote/NVDA")
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "NVDA"
    assert body["bid"] == "875.40"
    assert body["last"] == "875.60"


def test_get_quote_downstream_404_returns_404(client, mock_downstream):
    mock_downstream.expect(
        "GET",
        "/pricing/quote/XYZ",
        httpx.Response(404, json={"detail": "no pricing data"}),
    )

    response = client.get("/market/quote/XYZ")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "not_found"


def test_get_market_status(client):
    response = client.get("/market/status")
    assert response.status_code == 200
    body = response.json()
    assert body["session"] == "open"
    assert "as_of" in body
