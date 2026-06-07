def test_get_margin_returns_seeded(client):
    response = client.get("/risk/account/acct-001/margin")
    assert response.status_code == 200
    body = response.json()
    assert body["account_id"] == "acct-001"
    assert "margin_used" in body
    assert "margin_available" in body


def test_get_margin_unknown_account(client):
    response = client.get("/risk/account/nope/margin")
    assert response.status_code == 404
