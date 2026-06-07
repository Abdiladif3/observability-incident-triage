import httpx

QUOTE_AAPL = {
    "symbol": "AAPL",
    "bid": "184.25",
    "ask": "184.32",
    "last": "184.30",
    "volume": 1,
    "as_of": "2026-06-07T12:00:00+00:00",
}


def test_risk_check_approved(client, mock_downstream):
    mock_downstream.expect("GET", "/pricing/quote/AAPL", httpx.Response(200, json=QUOTE_AAPL))

    response = client.post(
        "/admin/risk-check",
        json={"account_id": "acct-001", "symbol": "AAPL", "side": "buy", "quantity": 10},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is True
    assert "account.active" in body["checks_passed"]
    assert "buying_power.sufficient" in body["checks_passed"]
    assert body["checks_failed"] == []


def test_risk_check_position_size_limit_fails(client, mock_downstream):
    mock_downstream.expect("GET", "/pricing/quote/AAPL", httpx.Response(200, json=QUOTE_AAPL))

    response = client.post(
        "/admin/risk-check",
        json={"account_id": "acct-001", "symbol": "AAPL", "side": "buy", "quantity": 100_000},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is False
    assert "position_size.within_limit" in body["checks_failed"]


def test_risk_check_unknown_account(client):
    response = client.post(
        "/admin/risk-check",
        json={"account_id": "nope", "symbol": "AAPL", "side": "buy", "quantity": 10},
    )
    assert response.status_code == 404
