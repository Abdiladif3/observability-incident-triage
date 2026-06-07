def test_get_quote_returns_seeded_symbol(client):
    response = client.get("/pricing/quote/AAPL")
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert "bid" in body
    assert "ask" in body
    assert "last" in body
    assert "as_of" in body


def test_get_quote_normalizes_symbol_case(client):
    response = client.get("/pricing/quote/aapl")
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"


def test_get_quote_unknown_symbol(client):
    response = client.get("/pricing/quote/XYZ")
    assert response.status_code == 404


def test_get_quote_during_outage(client):
    client.post("/simulate/outage", json={})
    response = client.get("/pricing/quote/AAPL")
    assert response.status_code == 503
