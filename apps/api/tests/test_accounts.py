import httpx

QUOTE_AAPL = {
    "symbol": "AAPL",
    "bid": "184.25",
    "ask": "184.32",
    "last": "190.00",
    "volume": 1,
    "as_of": "2026-06-07T12:00:00+00:00",
}

QUOTE_MSFT = {
    "symbol": "MSFT",
    "bid": "338.05",
    "ask": "338.18",
    "last": "350.00",
    "volume": 1,
    "as_of": "2026-06-07T12:00:00+00:00",
}


def test_get_account_returns_seeded(client):
    response = client.get("/accounts/acct-001")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "acct-001"
    assert body["holder_name"] == "Acme Capital LLC"
    assert body["account_type"] == "margin"


def test_get_account_not_found(client):
    response = client.get("/accounts/nope")
    assert response.status_code == 404


def test_get_positions_enriches_with_downstream_prices(client, mock_downstream):
    mock_downstream.expect("GET", "/pricing/quote/AAPL", httpx.Response(200, json=QUOTE_AAPL))
    mock_downstream.expect("GET", "/pricing/quote/MSFT", httpx.Response(200, json=QUOTE_MSFT))

    response = client.get("/accounts/acct-001/positions")
    assert response.status_code == 200
    positions = response.json()
    assert len(positions) == 2

    by_symbol = {p["symbol"]: p for p in positions}
    # current_price was replaced by downstream `last`, not the seeded local value
    assert by_symbol["AAPL"]["current_price"] == "190.00"
    assert by_symbol["MSFT"]["current_price"] == "350.00"


def test_get_positions_unknown_account_skips_downstream(client, mock_downstream):
    response = client.get("/accounts/nope/positions")
    assert response.status_code == 404


def test_get_account_orders(client):
    response = client.get("/accounts/acct-001/orders")
    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)
    # acct-001 has the seeded ord-001
    assert any(o["id"] == "ord-001" for o in orders)
