def test_submit_market_order_returns_pending(client):
    payload = {
        "account_id": "acct-001",
        "symbol": "AAPL",
        "side": "buy",
        "order_type": "market",
        "quantity": 10,
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["symbol"] == "AAPL"
    assert body["account_id"] == "acct-001"
    assert body["id"].startswith("ord-")


def test_submit_order_normalizes_symbol_to_upper(client):
    payload = {
        "account_id": "acct-001",
        "symbol": "aapl",
        "side": "buy",
        "order_type": "market",
        "quantity": 1,
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    assert response.json()["symbol"] == "AAPL"


def test_submit_order_missing_required_field(client):
    payload = {"account_id": "acct-001", "symbol": "AAPL"}
    response = client.post("/orders", json=payload)
    assert response.status_code == 422


def test_submit_order_unknown_account(client):
    payload = {
        "account_id": "nope",
        "symbol": "AAPL",
        "side": "buy",
        "order_type": "market",
        "quantity": 1,
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 404


def test_submit_limit_order_requires_limit_price(client):
    payload = {
        "account_id": "acct-001",
        "symbol": "AAPL",
        "side": "buy",
        "order_type": "limit",
        "quantity": 1,
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 400


def test_get_order(client):
    response = client.get("/orders/ord-001")
    assert response.status_code == 200
    assert response.json()["id"] == "ord-001"


def test_get_order_not_found(client):
    response = client.get("/orders/nope")
    assert response.status_code == 404
